from flask import Blueprint, request
import time
from .models import user
from .db import AtlasClient
from .utils import JSONEncoder
from .auth import encode_token, decode_token
from .config import getConfig

views = Blueprint('views', __name__)

config = getConfig()

@views.route('/', methods=['GET'])
def home():
    return 'Hello world '

@views.route('/users', methods=['GET'])
def users():
    client = AtlasClient(config['dbUri'], config['dbName'])
    col = client.get_collection('User')
    data = JSONEncoder().encode(list(col.find()))
    print(data)
    return JSONEncoder().encode({ data }), 200

@views.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    client = AtlasClient(config['dbUri'], config['dbName'])
    col = client.get_collection('User')
    data = list(col.find({ "name": body['name'] }))

    if len(data) > 0:
        userData = data[0]
        print(userData)
        if userData['password'] == body['password']:
            encoded = encode_token({
                "id": str(userData['_id']),
                "name": userData['name'],
                "email": userData['email']
            })
            col.update_one(
                { "_id": userData['_id'] },
                {"$set": {
                    "logged_in": True,
                    "logged_in_date": time.time()
                }})
            return JSONEncoder().encode({ "key": encoded }), 200
        else:
            return JSONEncoder().encode({ "result": "Invalid Password" }), 401
    else:
        return JSONEncoder().encode({ "result": "Invalid Username" }), 401

@views.route('/check-user-state', methods=['POST'])
def check_user_state():
    body = request.get_json()
    if "auth_key" in body:
            body = request.get_json()
            encodedKey = body['auth_key']
            decoded = decode_token(encodedKey)
            if decoded.get('error'):
                return JSONEncoder().encode({ "state": "not-authenticated", "result": decoded['result']}), 401
            
            if len(decoded['name']) > 5:
                client = AtlasClient(config['dbUri'], config['dbName'])
                col = client.get_collection('User')
                data = list(col.find({ "name": decoded['name'] }))
                if decoded['id'].isalnum() and data[0]['logged_in']:
                    return JSONEncoder().encode({ "state": "authenticated"}), 200
            else:
                return JSONEncoder().encode({ "state": "not-authenticated"}), 401

@views.route('/logout', methods=['POST'])
def logout():
    body = request.get_json()
    encodedKey = body['auth_key']
    decoded = decode_token(encodedKey)
    if decoded.get('error'):
        return JSONEncoder().encode({ "state": "not-authenticated", "result": decoded['result']}), 401

    client = AtlasClient(config['dbUri'], config['dbName'])
    col = client.get_collection('User')
    col.update_one(
        { "name": decoded['name'] },
        { "$set": {
            "logged_in": False,
            "logged_in_date": None
        }})
    return JSONEncoder().encode({"result": "logged-out"}), 200

@views.route('/sign-up', methods=['POST'])
def signup():
    data = request.get_json()
    error_validation = ''
    if not len(data['name']) > 5:
        error_validation = 'Name invalid, must be at minimum 5 chars'
    if not len(data['email']) > 5:
        error_validation = 'Email invalid, must be at minimum 5 chars'
    if not data['password1'] == data['password2']:
        error_validation = 'The passwords being compared must be equal'
    
    if len(error_validation) > 0:
        return JSONEncoder().encode({"result": error_validation}), 400

    newUser = user(data['name'], data['email'])
    newUser.setPassword(data['password1'])
    client = AtlasClient(config['dbUri'], config['dbName'])
    col = client.get_collection('User')
    col.insert_one({
        "name": newUser.name,
        "email": newUser.email,
        "password": newUser.password,
        "logged_in": False,
        "logged_in_date": None
    })
    return JSONEncoder().encode({"result": "Successfully signed-up"}), 200