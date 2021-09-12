from pymongo import MongoClient

from dcctools.config import Configuration

c = Configuration("config.json")
client = MongoClient(c.mongo_uri)
database = client.linkage_agent
database.match_groups.drop()
database.household_match_groups.drop()
print("Database cleared.")
