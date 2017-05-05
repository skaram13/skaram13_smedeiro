import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import requests 
import time
import csv
class getStudents(dml.Algorithm):
	contributor = 'skaram13_smedeiro'
	reads = []
	writes = ['skaram13_smedeiro.students']
	

	@staticmethod
	def execute(trial = False):
		startTime = datetime.datetime.now()
		# Set up the database connection.
		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('skaram13_smedeiro', 'skaram13_smedeiro')

		req = urllib.request.Request('http://datamechanics.io/data/_bps_transportation_challenge/students-simulated.geojson')
		response = urllib.request.urlopen(req).read().decode("UTF-8")

		r = json.loads(response)

		repo.dropCollection("students")
		repo.createCollection("students")


		repo['skaram13_smedeiro.students'].insert_many(r['features'])
		repo['skaram13_smedeiro.students'].metadata({'complete':True})
		# print(repo['skaram13_smedeiro.GradRates'].metadata())
		repo.logout()

		endTime = datetime.datetime.now()

		return {"start":startTime, "end":endTime}
	
	@staticmethod
	def provenance(doc = prov.model.ProvDocument(), startTime = None, endTime = None):
		'''
			Create the provenance document describing everything happening
			in this script. Each run of the script will generate a new
			document describing that invocation event.
			'''

		client = dml.pymongo.MongoClient()
		repo = client.repo
		doc.add_namespace('alg', 'http://datamechanics.io/algorithm/skaram13_smedeiro/') # The scripts are in <folder>#<filename> format.
		doc.add_namespace('dat', 'http://datamechanics.io/data/skaram13_smedeiro/') # The data sets are in <user>#<collection> format.
		doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
		doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
		doc.add_namespace('dmg', 'http://datamechanics.io/data/_bps_transportation_challenge/')
		#Agents
		# this script gets the student information 
		this_script = doc.agent('alg:skaram13_smedeiro#getStudents', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})

		# Entities
		# this is the data set that we take the student from 
		studentGeoJson = doc.entity('dmg:skaram13_smedeiro#Students-Simulated',{'prov:label':'Students', prov.model.PROV_TYPE:'ont:DataSet','ont:Extension':'Geojson'})		
		#this is the data set we create in this script
		students = doc.entity('dat:skaram13_smedeiro#Students',{'prov:label':'Students', prov.model.PROV_TYPE:'ont:DataSet'})

		# Activities			
		get_students = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		
		
		doc.wasAttributedTo(get_students, this_script)
		doc.wasGeneratedBy(students, get_students, endTime)
		doc.wasDerivedFrom(students, studentGeoJson)
		doc.usage(get_students, students, startTime)
		doc.wasDerivedFrom(students,get_students)
		doc.wasAssociatedWith(get_students, this_script)

		repo.logout()
				  
		return doc

getStudents.execute()
doc = getStudents.provenance()
print(doc.get_provn())

# print(json.dumps(json.loads(doc.serialize()), indent=4))