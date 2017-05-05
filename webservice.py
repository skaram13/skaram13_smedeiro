import jsonschema
from flask import Flask, jsonify, abort, make_response, request
from flask.ext.httpauth import HTTPBasicAuth
from flask import render_template
from werkzeug.utils import secure_filename


app = Flask(__name__)
auth = HTTPBasicAuth()
students = [
]


# schema = {
#   "type": "object", 
#   "properties": {"username" : {"type": "string"}},
#   "required": ["username"]
# }

# @app.route('/client', methods=['OPTIONS'])
# def show_api():
#     return jsonify(schema)

# @app.route('/client', methods=['GET'])
# @auth.login_required
# def show_client():
#     return open('client.html','r').read()

# @app.route('/app/api/v0.1/users', methods=['GET'])
# def get_users(): # Server-side reusable name for function.
#     print("I'm responding.")
#     return jsonify({'users': users})

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
    if request.method=='Post':
        if not request.json:
            print('Request not valid JSON.')
            abort(400)
        try:

            #TODO - these two files/functions
            #findPotentialStops.execute(school="Everett ES", lon= -71.06918, lat= 42.29890)
            #studentsGraph.execute(schoolInput="Everett ES", lonInput=-71.06918,  latInput= 42.29890)


            # print ('hi')
            # jsonschema.validate(request.json, schema)
            # user = { 'id': users[-1]['id'] + 1, 'username': request.json['username'] }
            students.append(request.json)
            print(students)        
            return jsonify(request.json), 201
        except:
            print('Request does not follow schema.')
            abort(400)
    else:
        return ('i need these values')


# @auth.get_password
# def foo(username):
#     if username == 'alice':
#         return 'ecila'
#     return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access.'}), 401)

if __name__ == '__main__':
    app.run(debug=True)

