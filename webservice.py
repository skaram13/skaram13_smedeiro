import jsonschema
from flask import Flask, jsonify, abort, make_response, request
from flask.ext.httpauth import HTTPBasicAuth
from flask import render_template
from werkzeug.utils import secure_filename
from findPotentialStops import findPotentialStops
from studentsGraph import studentsGraph


app = Flask(__name__)
auth = HTTPBasicAuth()
students = [
]
app.config['MONGO_DBNAME'] = 'repo'
app.config['MONGO_USERNAME'] = 'skaram13_smedeiro'
app.config['MONGO_PASSWORD'] = 'skaram13_smedeiro'

# @app.route('/app/api/v0.1/users/', methods=['GET'])
# def get_user(user_id):
#     user = [user for user in users if user['id'] == user_id]
#     if len(user) == 0:
#         abort(404)
#     return jsonify({'user': user[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found foo.'}), 404)

@app.route('/')
def index():
    return 'Index Page'

@app.route('/home')
def home(name=None):
    return render_template('home.html')

@app.route('/app/api/v0.1/newStudent', methods=['POST','GET'])
def create_student():
    # print('here')
    # print(request.json)
    #TODO - these two files/functions
    #findPotentialStops.execute(school="Everett ES", lon= -71.06918, lat= 42.29890)
    #studentsGraph.execute(schoolInput="Everett ES", lonInput=-71.06918,  latInput= 42.29890)

    if not request.json:
        print('Request not valid JSON.')
        abort(400)
    try:
        # print ('hi')
        # jsonschema.validate(request.json, schema)
        print(request.json['lat'])
        print(request.json['lng'])
        print(request.json['school'])
        # findPotentialStops.execute(school="Everett ES", lon= -71.06918, lat= 42.29890)
        # print
        # studentsGraph.execute(schoolInput="Everett ES", lonInput=-71.06918,  latInput= 42.29890)
        # findPotentialStops.execute()
        # findPotentialStops.execute(school=request.json['school'], lon= request.json['lng'], lat= request.json['lat'])
        # print (temp)
        # print (studentsGraph.execute(schoolInput=request.json['school'], lonInput=request.json['lng'],  latInput= request.json['lng']))

        students.append(request.json)
        print(students)        
        return jsonify(request.json), 201
    except:
        print('Request does not follow schema.')
        abort(400)


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access.'}), 401)

if __name__ == '__main__':
    app.run(debug=True)

