import configparser
import os

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))

config = {
    "dbUri": config['PROD']['DB_URI'],
    "dbName": config['PROD']['DB_NAME'],
    "jwtSecret": config['PROD']['JWT_SECRET']
}

def getConfig():
    return config
