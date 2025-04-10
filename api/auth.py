import jwt
from .config import getConfig

config = getConfig()

def encode_token(data):
    encoded = jwt.encode(
        data,
        config['jwtSecret'],
        algorithm="HS256"
    )
    return encoded

def decode_token(token):
    try:
        decoded = jwt.decode(token, config['jwtSecret'], algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return { "error": True, "result": "Expired token" }
    except jwt.InvalidTokenError:
        return { "error": True, "result": "Invalid token" }
    