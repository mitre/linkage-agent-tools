import os
from pymongo import MongoClient

from dcctools.config import Configuration

c = Configuration("config.json")
if 'MONGODB_USERNAME' in os.environ and 'MONGODB_PASSWORD' in os.environ:
    client = MongoClient(host=c.mongo_uri,
                         username=os.environ['MONGODB_USERNAME'],
                         password=os.environ['MONGODB_PASSWORD'],
                         authSource='linkage_agent')
else:
    client = MongoClient(c.mongo_uri)

database = client.linkage_agent
database.match_groups.drop()
database.household_match_groups.drop()
print("Database cleared.")
