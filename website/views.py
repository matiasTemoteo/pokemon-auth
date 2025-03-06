from flask import Blueprint, request
import jwt
import time
from .models import user
from .db import AtlasClient
from .utils import JSONEncoder
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
            enconded = jwt.encode(
                {
                    "id": str(userData['_id']),
                    "name": userData['name'],
                    "email": userData['email']
                },
                config['jwtSecret'],
                algorithm="HS256"
            )
            col.update_one({ "_id": userData['_id'] }, { "$set": { "logged_in": True, "logged_in_date": time.time() } })
            return JSONEncoder().encode({ "key": enconded }), 200
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
            try:
                decoded = jwt.decode(encodedKey, config['jwtSecret'], algorithms=["HS256"])
            except jwt.ExpiredSignatureError:
                return JSONEncoder().encode({ "state": "not-authenticated", "result": "Expired token"}), 401
            except jwt.InvalidTokenError:
                return JSONEncoder().encode({ "state": "not-authenticated", "result": "Invalid token"}), 401
            
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
    decoded = jwt.decode(encodedKey, config['jwtSecret'], algorithms=["HS256"])
    client = AtlasClient(config['dbUri'], config['dbName'])
    col = client.get_collection('User')
    col.update_one({ "name": decoded['name'] }, { "$set": { "logged_in": False, "logged_in_date": None } })
    return JSONEncoder().encode({"result": "logged-out"}), 200

@views.route('/sign-up', methods=['POST'])
def signup():
    data = request.get_json()
    print(f'data: {data}')
    if not len(data['name']) > 5:
        return JSONEncoder().encode({"result": "Name invalid, must be at minimum 5 chars"}), 400
    if not len(data['email']) > 5:
        return JSONEncoder().encode({"result": "Email invalid, must be at minimum 5 chars"}), 400
    if not data['password1'] == data['password2']:
        return JSONEncoder().encode({"result": "The passwords being compared must be equal"}), 400

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