import certifi
from pymongo import MongoClient
# local connection for compass
# CONNECTION_STRING = "mongodb://localhost:27017/?readPreference=primary&appname=MongoDB%20Compass&directConnection=true&ssl=false"
# server connection
CONNECTION_STRING = "mongodb+srv://trufla_admin:O7O8zXIjBgTiSIIn@cluster0.spr6v.mongodb.net/test?authSource=admin&replicaSet=atlas-uc8vhh-shard-0&readPreference=primary&appname=MongoDB%20Compass&ssl=true"
client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())


def get_trufla_db():
    return client.get_database('trufla')


