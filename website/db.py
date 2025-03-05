from pymongo import MongoClient


class AtlasClient ():

    def __init__ (self, altas_uri, dbname):
        self.mongodb_client = MongoClient(altas_uri)
        self.database = self.mongodb_client[dbname]

    def get_collection (self, collection_name):
       collection = self.database[collection_name]
       return collection

    ## A quick way to test if we can connect to Atlas instance
    def ping (self):
        tfrt = ''
        #    self.mongodb_client.admin.command('ping')

    def close(self):
        self.mongodb_client.close()
