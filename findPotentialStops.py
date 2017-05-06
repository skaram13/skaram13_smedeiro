import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import requests 
import time
import csv
import numpy as np
import os
import requests
import random
import math
import json
import geojson
import geopy.distance
import xlsxwriter
from sklearn.cluster import KMeans

class findPotentialStops(dml.Algorithm):
	contributor = 'skaram13_smedeiro'
	reads = ['skaram13_smedeiro.students', 'skaram13_smedeiro.potential_stops']
	writes = ['skaram13_smedeiro.students', 'skaram13_smedeiro.potential_stops']
	
	def storePotentialStops(data, singleSchool=False, school = ""):
		startTime = datetime.datetime.now()
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('skaram13_smedeiro', 'skaram13_smedeiro')

		if singleSchool == False:
			repo.dropCollection("potential_stops")
			repo.createCollection("potential_stops")
			repo['skaram13_smedeiro.potential_stops'].insert_many(data)
			repo['skaram13_smedeiro.potential_stops'].metadata({'complete':True})

			# #PRINT DATA TO TEST IF INSERTED CORRECTLY
			results = repo['skaram13_smedeiro.potential_stops'].find()

		else:
			repo['skaram13_smedeiro.potential_stops'].remove({'properties': {'school': school}})
			repo['skaram13_smedeiro.potential_stops'].insert_many(data)



		#TODO -- drop single school's stops
		#Add in new entry

		repo.logout()
		endTime = datetime.datetime.now()
		return {"start":startTime, "end":endTime}

	def addStudent(school, lon, lat):
		startTime = datetime.datetime.now()
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('skaram13_smedeiro', 'skaram13_smedeiro')

		entry ={"type": "Feature", "properties": {
        "school_start": "08:30:00",
        "zip": "02127",
        "walk": 0.5,
        "safety": "4",
        "number": "168",
        "pickup": "corner",
        "geocode": "25025060800",
        "school": school,
        "street": "W Ninth St",
        "length": 1.337088313674985,
        "grade": "2",
        "school_address": "380 Shawmut Avenue",
        "school_end": "15:10:00"
        },
        "geometry": {
        "type": "LineString",
        "coordinates": [
          [
            lon,
            lat
          ],
          [
            "-71.07246107",
            "42.34073755"
          ]
        ]
        }}
		
		print(entry)


		
		repo['skaram13_smedeiro.students'].insert_one(entry)

		repo.logout()
		endTime = datetime.datetime.now()
		return {"start":startTime, "end":endTime}

	def getStopsForSingleSchool(school, allEntries):
			latList = []
			lonList = []
			students = []
			walkLookup = {}
			schoolLookup = {} #to find out the max distance a student can walk
			#find lat, lon, and walking distance for each student at this school
			for student in school['students']:
				school = student['properties']['school']
				walk =  student['properties']['walk']
				longitude = student['geometry']['coordinates'][0][0]
				latitude = student['geometry']['coordinates'][0][1]
				
				#do not account for kids that need a D2D stop
				if walk is not None:
					#make key to look up walking distance/school for each student after assigning them to a bus stop
					key = str(longitude) + "," + str(latitude)

					#if more than one student is at the same location,use the min walking distance of them all
					if key in walkLookup: 
						walkLookup[key] = min(walk, walkLookup[key])
					else:
						walkLookup[key] = walk

					schoolLookup[key] = school

					#for finding the bounds of the r tree we will be making for 
					#each school
					latList.append(latitude)
					lonList.append(longitude)

					latLon = [str(longitude),str(latitude)]
					students.append(latLon)

			latList.sort()
			lonList.sort()

			latLBound = latList[0]
			latUBound = latList[-1]
			lonLBound = lonList[0]
			lonUBound = lonList[-1]

			#set potential number of bus_stops
			k = len(students) // 3
			students = np.array(students)
			# if (len(students) < k):
			# 	print(len(students))
			# 	k = len(students)//2
			kmeans = KMeans(n_clusters=k).fit(students)

			labels = kmeans.labels_
			centers = kmeans.cluster_centers_
			pointsByMean = [students[np.where(labels==i)] for i in range(k)]
			

			for i in range(k):
				studentsPerSchoolAndStop = []
				for item in pointsByMean[i]:
					#lookup child attributes by long/lat
					key = str(item[0]) + "," + str(item[1])
					walk = walkLookup[key]
					school = schoolLookup[key]
					student = {
					'longitude':item[0],
					'latitude':item[1],
					'walk':walk
					}
					studentsPerSchoolAndStop.append(student)
					#make entries with bus stop, their lat/lon/, school name, and max walking distance
					#meansAndPoints.append(entry)
				entry = {
					'school': school,
					'bus_stop': (centers[i][0],centers[i][1]), 
					'rTreeUBound': (lonUBound, latUBound), #lon, lat
					'rTreeLBound': (lonLBound, latLBound), #lon, lat
					'students' : studentsPerSchoolAndStop
					}
				allEntries.append(entry)



	
	@staticmethod
	def execute(school="", lon= 0, lat=0, trial = False):

		if school != "":
			findPotentialStops.addStudent(school,lon, lat)

		startTime = datetime.datetime.now()
		# Set up the database connection.
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('skaram13_smedeiro', 'skaram13_smedeiro')

		if school == "":
		#get students grouped by school
			results = repo['skaram13_smedeiro.students'].aggregate(
				[
	     			{'$group':{'_id' : '$properties.school', 'students': { '$push': '$$ROOT' } } }
				]
			)
		else:
			results = repo['skaram13_smedeiro.students'].aggregate(
				[
					{'$match': { 'properties.school' : school } },
	     			{'$group':{'_id' : '$properties.school', 'students': { '$push': '$$ROOT' } } }
				]
			)
		
		
		#init to save 
		allEntries = []

		i = 0
		#find k means(i.e. bus stops) for each school
		for school in results:
			print (school)
			findPotentialStops.getStopsForSingleSchool(school, allEntries)
				#key = str(centers[i][0]) + "," + str(centers[i][1])
		
		if school == "":
			findPotentialStops.storePotentialStops(allEntries)
		else:		
			#findPotentialStops.getStopsForSingleSchool(school, allEntries)
			singleSchool = True
			#fix the school thing - needs to be a single entry - just get school
			findPotentialStops.storePotentialStops(allEntries, singleSchool, school)

		

			
			
	@staticmethod
	def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
		'''
			Create the provenance document describing everything happening
			in this script. Each run of the script will generate a new
			document describing that invocation event.
			'''

		# Set up the database connection.
		client = dml.pymongo.MongoClient()
		repo = client.repo
		doc.add_namespace('alg', 'http://datamechanics.io/algorithm/skaram13_smedeiro/') # The scripts are in <folder>#<filename> format.
		doc.add_namespace('dat', 'http://datamechanics.io/data/skaram13_smedeiro/') # The data sets are in <user>#<collection> format.
		doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
		doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
		# doc.add_namespace('dmg', 'http://datamechanics.io/data/_bps_transportation_challenge/')


		#Agents
		
		findPotentialStops = doc.agent('alg:skaram13_smedeiro#findPotentialStops ', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
		
		# Entities
		students = doc.entity('dat:skaram13_smedeiro#Students',{'prov:label':'Students', prov.model.PROV_TYPE:'ont:DataSet'})
		potential_stops = doc.entity('dat:skaram13_smedeiro#Potential_Stops',{'prov:label':'Potential Stops', prov.model.PROV_TYPE:'ont:DataSet'})
		
		# Activities			
		get_potentialStops = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		doc.wasAssociatedWith(get_potentialStops,findPotentialStops)
		
		doc.used(get_potentialStops,students)
		doc.wasAttributedTo(potential_stops, findPotentialStops)
		doc.wasGeneratedBy(potential_stops, get_potentialStops, endTime)

		doc.wasDerivedFrom(potential_stops, students, get_potentialStops)


		repo.logout()
				  
		return doc

#findPotentialStops.execute()

#findPotentialStops.execute(school="Everett ES", lon= -71.06918, lat= 42.29890)
#doc = findPotentialStops.provenance()
#print(doc.get_provn())
