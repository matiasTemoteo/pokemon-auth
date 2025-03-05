from flask import Blueprint, request
import jwt
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
    return data

@views.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    if "auth_key" in body:
        encodedKey = body['auth_key']
        decoded = jwt.decode(encodedKey, config['jwtSecret'], algorithms=["HS256"])
        if decoded['id'].isalnum():
            return 'Authenticated'

    client = AtlasClient(config['dbUri'], config['dbName'])
    col = client.get_collection('User')
    data = list(col.find({ "name": body['name'] }))
    print(data)
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
            return JSONEncoder().encode({ "key": enconded })
        else:
            return 'Invalid Password'
    else:
        return 'Invalid user'

@views.route('/logout', methods=['POST'])
def logout():
    return 'success'

@views.route('/sign-up', methods=['POST'])
def signup():
    data = request.get_json()
    print(f'data: {data}')
    if not len(data['name']) > 5:
        return 'Fail'
    if not len(data['email']) > 5:
        return 'Fail'
    if not data['password1'] == data['password2']:
        return 'Fail'

    newUser = user(data['name'], data['email'])
    newUser.setPassword(data['password1'])
    client = AtlasClient(config['dbUri'], config['dbName'])
    col = client.get_collection('User')
    col.insert_one({
        "name": newUser.name,
        "email": newUser.email,
        "password": newUser.password
    })
    return 'Success'