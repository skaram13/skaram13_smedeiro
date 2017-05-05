import json
import urllib.request

# get list of schools
req = urllib.request.Request('http://datamechanics.io/data/_bps_transportation_challenge/schools-real.geojson')
response = urllib.request.urlopen(req).read().decode("UTF-8")

r = json.loads(response)

with open('listOfBostonSchools.txt','w') as f:
	for feature in r['features']:
		# write school to file
		f.write("\'" + feature['properties']['name']+"\',")
