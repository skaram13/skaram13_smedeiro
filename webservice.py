import jsonschema
from flask import Flask, jsonify, abort, make_response, request, redirect
from flask.ext.httpauth import HTTPBasicAuth
from flask import render_template
from werkzeug.utils import secure_filename
from findPotentialStops import findPotentialStops
from studentsGraph import studentsGraph
import geocoder


app = Flask(__name__)
auth = HTTPBasicAuth()
students = [
]
stops = [
]
app.config['MONGO_DBNAME'] = 'repo'
app.config['MONGO_USERNAME'] = 'skaram13_smedeiro'
app.config['MONGO_PASSWORD'] = 'skaram13_smedeiro'

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found foo.'}), 404)

@app.route('/')
def index():
	return 'Index Page'

@app.route('/home', methods=['POST','GET'])
def newStudent():
	if request.method == 'POST':
		try:
			print ('hi')

			address = request.form['Address']
			# address = address.replace(' ','+')
			city = request.form['City']
			# city = city.replace(' ','+')
			school = request.form['school']
			print(address,city,school)

			print (address +', ' + city +', MA')
			g = geocoder.google(address +', ' + city +', MA')
			print (g.latlng)
			lat = g.latlng[0]
			lng = g.latlng[1]
			
			
			findPotentialStops.execute(schoolName=school, lon= lng, lat= lat)
			print ('done')
			# students.append(request.json)
			# print(students)

			temp = studentsGraph.execute(schoolInput=school, lonInput=lng,  latInput= lat)
			
			print (len(temp))
			if (len(temp) > 0):
				coords = temp[0]
				print(coords)
				values = lat, lng, coords['lat'], coords['lon']
				return render_template('home.html',values=values)
# 
			return redirect('/')
		except:
			print('Request does not follow schema.')
			abort(400)
	else:
		values = '42.3523891', '-71.1159753','42.3523891', '-71.1159753'
		return render_template('home.html',values=values)



@auth.error_handler
def unauthorized():
	return make_response(jsonify({'error': 'Unauthorized access.'}), 401)

if __name__ == '__main__':
	app.run(debug=True)

