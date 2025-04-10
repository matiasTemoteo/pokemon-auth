from flask import Blueprint, request
import time
import logging
from .models import user, role, user_role, user_log
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
    data = list(col.find())
    return JSONEncoder().encode(data), 200

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
                "email": userData['email'],
                "role": userData['role']
            })
            col.update_one(
                { "_id": userData['_id'] },
                {"$set": {
                    "logged_in": True,
                    "logged_in_date": time.time()
                }})
            newLog = user_log('login', userData['name'], time.time())
            newLog.setContent(f'User ({userData['name']}) performed log-in successfully.')
            colLog = client.get_collection('User_log')
            colLog.insert_one({
                "type": newLog.type,
                "user_name": newLog.user_name,
                "content": newLog.content,
                "date": newLog.date
            })
            logging.info(f'Log-in successfully performed by user: {userData['name']}')
            return JSONEncoder().encode({ "key": encoded }), 200
        else:
            logging.warning(f'Error when Log-in action by user: {userData['name']} - Invalid Password')
            return JSONEncoder().encode({ "result": "Invalid Password" }), 401
    else:
        logging.warning(f'Error when Log-in action by user: {userData['name']} - Invalid Username')
        return JSONEncoder().encode({ "result": "Invalid Username" }), 401

@views.route('/check-user-state', methods=['POST'])
def check_user_state():
    headers = request.headers
    if headers.get('auth-token'):
            encodedKey = headers.get('auth-token')
            decoded = decode_token(encodedKey)
            if decoded.get('error'):
                logging.warning(f'Error when checking state of user - {decoded['result']}')
                return JSONEncoder().encode({ "state": "not-authenticated", "result": decoded['result']}), 401
            
            if len(decoded['name']) > 5:
                client = AtlasClient(config['dbUri'], config['dbName'])
                col = client.get_collection('User')
                data = list(col.find({ "name": decoded['name'] }))
                if decoded['id'].isalnum() and data[0]['logged_in']:
                    userObj = { "name": decoded['name'], "role": decoded['role'] }
                    logging.info(f'User state Checking successfully performed for user: {decoded['name']}')
                    return JSONEncoder().encode({ "state": "authenticated", "user": userObj }), 200
            else:
                logging.warning(f'Error when checking state of user: {decoded['name']}')
                return JSONEncoder().encode({ "state": "not-authenticated"}), 401

@views.route('/logout', methods=['POST'])
def logout():
    headers = request.headers
    encodedKey = headers.get('auth-token')
    decoded = decode_token(encodedKey)
    if decoded.get('error'):
        logging.warning(f'Error when log-out action by user - {decoded['result']}')
        return JSONEncoder().encode({ "state": "not-authenticated", "result": decoded['result']}), 401

    client = AtlasClient(config['dbUri'], config['dbName'])
    col = client.get_collection('User')
    col.update_one(
        { "name": decoded['name'] },
        { "$set": {
            "logged_in": False,
            "logged_in_date": None
        }})
    newLog = user_log('logout', decoded['name'], time.time())
    newLog.setContent(f'User ({decoded['name']}) performed log-out successfully.')
    colLog = client.get_collection('User_log')
    colLog.insert_one({
        "type": newLog.type,
        "user_name": newLog.user_name,
        "content": newLog.content,
        "date": newLog.date
    })
    logging.info(f'Log-out action successfully performed by user: {decoded['name']}')
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
        logging.warning(f'Error when sign-up action by user - {data['name']} - {error_validation}')
        return JSONEncoder().encode({"result": error_validation}), 400
    
    roleLevel = 2
    if data.get('role-definition'):
        if data['role-definition'] == 'admin':
            roleLevel = 0
        elif data['role-definition'] == 'manager':
            roleLevel = 1

    client = AtlasClient(config['dbUri'], config['dbName'])

    col = client.get_collection('Role')
    roles_from_db = col.find()
    roles_list = []
    for i, obj in enumerate(roles_from_db):
        newRole = role(obj['name'], obj['level'], obj['description'])
        roles_list.append(newRole)

    userRole = user_role(roles_list, roleLevel)

    newUser = user(data['name'], data['email'])
    newUser.setPassword(data['password1'])
    newUser.setLogged_in(False, None)
    newUser.setRole(userRole)

    col = client.get_collection('User')
    col.insert_one({
        "name": newUser.name,
        "email": newUser.email,
        "password": newUser.password,
        "role": newUser.role.getName(),
        "logged_in": newUser.logged_in,
        "logged_in_date": newUser.logged_in_date
    })
    newLog = user_log('sign-up', newUser.name, time.time())
    newLog.setContent(f'New User ({newUser.name}) signed-up.')
    colLog = client.get_collection('User_log')
    colLog.insert_one({
        "type": newLog.type,
        "user_name": newLog.user_name,
        "content": newLog.content,
        "date": newLog.date
    })
    client.close()
    logging.info(f'Sign-up action successfully performed by user: {data['name']}')
    return JSONEncoder().encode({"result": "Successfully signed-up"}), 200