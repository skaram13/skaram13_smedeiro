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
	reads = ['skaram13_smedeiro.potential_stops']
	writes = ['skaram13_smedeiro.students', 'skaram13_smedeiro.potential_stops']
	
	def storePotentialStops(data):
		startTime = datetime.datetime.now()
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('skaram13_smedeiro', 'skaram13_smedeiro')

		repo.dropCollection("potential_stops")
		repo.createCollection("potential_stops")
		repo['skaram13_smedeiro.potential_stops'].insert_many(data)
		repo['skaram13_smedeiro.potential_stops'].metadata({'complete':True})

		# #PRINT DATA TO TEST IF INSERTED CORRECTLY
		results = repo['skaram13_smedeiro.potential_stops'].find()

		repo.logout()
		endTime = datetime.datetime.now()
		return {"start":startTime, "end":endTime}
	
	@staticmethod
	def execute(trial = False):
		startTime = datetime.datetime.now()
		# Set up the database connection.
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('skaram13_smedeiro', 'skaram13_smedeiro')

		#get students grouped by school
		results = repo['skaram13_smedeiro.students'].aggregate(
			[
     			{'$group':{'_id' : '$properties.school', 'students': { '$push': '$$ROOT' } } }
			]
		)
		
		#init to save 
		allEntries = []

		i = 0
		#find k means(i.e. bus stops) for each school
		for school in results:
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
			k= len(students) // 3
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

			#key = str(centers[i][0]) + "," + str(centers[i][1])

		findPotentialStops.storePotentialStops(allEntries)

			
			
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

findPotentialStops.execute()
doc = findPotentialStops.provenance()
print(doc.get_provn())
