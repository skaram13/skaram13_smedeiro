import urllib.request
import json
import dml
import prov.model
import datetime
import uuid
import requests 
import time
import csv
class getBuses(dml.Algorithm):
	contributor = 'skaram13_smedeiro'
	reads = []
	writes = ['skaram13_smedeiro.buses']
	

	@staticmethod
	def execute(trial = False):
		startTime = datetime.datetime.now()

		client = dml.pymongo.MongoClient()
		repo = client.repo
		repo.authenticate('skaram13_smedeiro', 'skaram13_smedeiro')

		with open('buses.json', 'r') as f:
			listOfbuses = json.load(f)

		print (listOfbuses)
		repo.dropCollection("buses")
		repo.createCollection("buses")
		repo['skaram13_smedeiro.buses'].insert_many(listOfbuses)
		repo['skaram13_smedeiro.buses'].metadata({'complete':True})
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

		# Set up the database connection.
		# client = dml.pymongo.MongoClient()
		# repo = client.repo
		# doc.add_namespace('alg', 'http://datamechanics.io/algorithm/skaram13_smedeiro/') # The scripts are in <folder>#<filename> format.
		# doc.add_namespace('dat', 'http://datamechanics.io/data/skaram13_smedeiro/') # The data sets are in <user>#<collection> format.
		# doc.add_namespace('ont', 'http://datamechanics.io/ontology#') # 'Extension', 'DataResource', 'DataSet', 'Retrieval', 'Query', or 'Computation'.
		# doc.add_namespace('log', 'http://datamechanics.io/log/') # The event log.
		# doc.add_namespace('dmg', 'https://census.gov/resource/')


		# #Agents
		# # this script gets the tech rates for 2011 and the corresponding org codes
		# this_script = doc.agent('alg:skaram13_smedeiro#getGradRatesByOrgCodeFor2011', {prov.model.PROV_TYPE:prov.model.PROV['SoftwareAgent'], 'ont:Extension':'py'})

		# # Entities
		# # this is the data set that we take the Grad reports from 
		# gradReport = doc.entity('dmg:skaram13_smedeiro#Graduation-Rate-Report-by-District-by-School',{'prov:label':'Graduation Report', prov.model.PROV_TYPE:'ont:DataSet','ont:Extension':'CSV'})		
		# #this is the data set we create in this script
		# gradRates = doc.entity('dat:skaram13_smedeiro#GradRates',{'prov:label':'Percent graduated for 2011', prov.model.PROV_TYPE:'ont:DataSet'})

		# # Activities			
		# get_gradRates = doc.activity('log:uuid'+str(uuid.uuid4()), startTime, endTime)
		# doc.wasAssociatedWith(get_gradRates, this_script)
		# # usage(activity, entity=None, time=None, identifier=None, other_attributes=None)
		# doc.usage(get_gradRates,gradRates, startTime, None,
		# 		  {prov.model.PROV_TYPE:'ont:Retrieval',
		# 		  'ont:Query':'?type=reg4_r,org_code'
		# 		  }
		# 		  )
		# doc.wasAttributedTo(gradRates, this_script)
		# doc.wasGeneratedBy(gradRates, get_gradRates, endTime)
		# doc.wasDerivedFrom(gradRates, gradReport, get_gradRates, get_gradRates, get_gradRates)


		repo.logout()
				  
		return doc

getBuses.execute()

# example.execute()
# doc = example.provenance()
# print(doc.get_provn())
# print(json.dumps(json.loads(doc.serialize()), indent=4))
