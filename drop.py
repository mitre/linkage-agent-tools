from dcctools.config import Configuration
from pymongo import MongoClient

c = Configuration("config.json")
client = MongoClient(c.mongo_uri())
database = client.linkage_agent
if database.match_groups:
    database.match_groups.drop()
    print('Dropped match_groups collection from previous run.')
else:
    print('No previous run data found.')
