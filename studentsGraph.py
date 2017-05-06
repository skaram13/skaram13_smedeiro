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
import rtree
from sklearn.cluster import KMeans
from geopy.distance import vincenty
import geoql
import geoleaflet

from tqdm import tqdm

class studentsGraph(dml.Algorithm):
	contributor = 'skaram13_smedeiro'
	reads = ['skaram13_smedeiro.potential_stops']
	writes = ['skaram13_smedeiro.new_stops']

	


	def storeNewStops(data):
		startTime = datetime.datetime.now()
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('skaram13_smedeiro', 'skaram13_smedeiro')

		repo.dropCollection("new_stops")
		repo.createCollection("new_stops")
		repo['skaram13_smedeiro.new_stops'].insert_many(data)
		repo['skaram13_smedeiro.new_stops'].metadata({'complete':True})

		# #PRINT DATA TO TEST IF INSERTED CORRECTLY
		results = repo['skaram13_smedeiro.new_stops'].find()
		for each in results:
			print (each)
			


		repo.logout()
		endTime = datetime.datetime.now()
		return {"start":startTime, "end":endTime}

	def findNewStops(school,dictOfCenters,dictOfSchoolStops, studentsByBusStop, latInput=0, lonInput=0, newStudentStop=[]):
		with open('input_data/boston_massachusetts_osm_line.geojson', encoding="utf8") as data_file:
			
			print('loading')
			g = json.load(data_file)
			g = geoql.features_properties_null_remove(g)
			g = geoql.features_tags_parse_str_to_dict(g)
			g = geoql.features_keep_by_property(g, {"highway": {"$in": ["residential", "secondary", "tertiary"]}})
			lat = dictOfCenters[school]['latitude']
			longi = dictOfCenters[school]['longitude']
			radius = dictOfCenters[school]['radius']
			g = geoql.features_keep_within_radius(g, (lat, longi), radius, 'miles') # Within 0.75 of Boston Common.
			g = geoql.features_node_edge_graph(g) # Converted into a graph with nodes and edges.
			print('code time!')
			

			#for each bus_stop in school
			yay = 0 
			nay = 0
			stops = dictOfSchoolStops[school]
			for stop in stops:
				lat = stop[1]
				longi = stop[0]
				minValue = 100
				minCoord = []
				#find the closest corner to the mean
				for x in (g['features']):
					if ('geometry' not in x and 'coordinates' in x):
						latCorner = (x['coordinates'][1])
						longCorner = (x['coordinates'][0])
						tmp = (abs(lat-latCorner)+abs(longi- longCorner))
						if (tmp < minValue):
				 			minValue = tmp
				 			minCoord = [latCorner,longCorner]
				#check if every student can reach the new stop
				for student in studentsByBusStop[str(stop)]:
					sLat = (student['latitude'])
					sLong = (student['longitude'])
					walkDist = (student['walk'])

					if latInput!= 0 and lonInput != 0:
						if (str(sLat) == str(latInput)) and (str(sLong) == str(lonInput)):
							print("Student:", student)
							newStudentStop.append({"lat": minCoord[0],"lon": minCoord[1]})

					dist = ((vincenty((sLat,sLong),(minCoord[0],minCoord[1])).miles)) 
					if (dist > walkDist):
						nay += 1
					else:
						yay +=1

			print(school)
			print('yays:', yay)
			print('nays:', nay)
			return ({'withinWalk': yay, 'outsideWalk': nay, 'school':school, 'coordinates': minCoord})
	
	
	@staticmethod
	def execute(schoolInput = "", latInput=0, lonInput =0 ,trial = False):
		
		#results = studentsGraph.getPotentialStops()
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('skaram13_smedeiro', 'skaram13_smedeiro')
		results = repo['skaram13_smedeiro.potential_stops'].aggregate(
			[
     			{'$group':{'_id' : '$school', 'stop': { '$push': '$$ROOT' } } }
			]
		)

		dictOfSchoolStops = {}
		dictOfCenters = {}
		studentsByBusStop = {}
		newStudentStop = []

		newStops = []

		for school in results:
			stopsForSingleSchool = []

			schoolName = school['_id']

			for stop in school['stop']:
				stopCoord = stop['bus_stop'] 
				studentsByBusStop[str(stopCoord)] = stop['students']
				stopsForSingleSchool.append(stopCoord)

			left, bottom = stop['rTreeLBound'] #left - more negative / bottom - more negative
			right, top =  stop['rTreeUBound'] #right - more positive / top - more positive

			midLong = (left+right)/2
			midLat =  (top+bottom)/2
			radius = ((vincenty((midLat,midLong),(top,right)).miles)) 

			dictOfSchoolStops[schoolName] = stopsForSingleSchool
			dictOfCenters[schoolName] = {'latitude': midLat,'longitude': midLong, 'radius': radius}


		i = len(dictOfSchoolStops)

		if (schoolInput == ""):
			for school in dictOfSchoolStops:
				if (trial == True):
					if i < len(dictOfSchoolStops):
						print(newStops)
						break

				print(i, ' left to go!')
				i -= 1

				print ("here 2")
				newStop = studentsGraph.findNewStops(school, dictOfCenters, dictOfSchoolStops, studentsByBusStop)
				newStops.append(newStop)
		else:
			newStop = studentsGraph.findNewStops(schoolInput, dictOfCenters, dictOfSchoolStops, studentsByBusStop, latInput, lonInput, newStudentStop)
			newStops.append(newStop)
		
		studentsGraph.storeNewStops(newStops)	

		return newStudentStop


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
		studentsGraph = doc.agent('alg:skaram13_smedeiro#findNewStops ', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})
		
		# Entities
		potential_stops = doc.entity('dat:skaram13_smedeiro#Potential_Stops',{'prov:label':'Potential Stops', prov.model.PROV_TYPE:'ont:DataSet'})
		new_stops = doc.entity('dat:skaram13_smedeiro#New_Stops',{'prov:label':'New Stops', prov.model.PROV_TYPE:'ont:DataSet'})
		
		# Activities			
		get_studentsGraphs = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		doc.wasAssociatedWith(get_studentsGraphs,studentsGraph)
		
		doc.used(get_studentsGraphs,potential_stops)
		doc.wasAttributedTo(new_stops, studentsGraph)
		doc.wasGeneratedBy(new_stops, get_studentsGraphs, endTime)

		doc.wasDerivedFrom(new_stops, potential_stops, get_studentsGraphs)


		repo.logout()
				  
		return doc

#studentsGraph.execute()
#test!


#newStop = studentsGraph.execute(schoolInput="Everett ES", lonInput=-71.06911,  latInput= 42.29891)
#print("NEW STOP:", newStop)   

#doc = studentsGraph.provenance()
#print(doc.get_provn())
			

#McKinley Middle
