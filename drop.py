from pymongo import MongoClient

from dcctools.config import Configuration

c = Configuration("config.json")
client = MongoClient(c.mongo_uri())
database = client.linkage_agent
if database.match_groups or database.household_match_groups:
    database.match_groups.drop()
    database.household_match_groups.drop()
    print("Dropped match_groups collection from previous run.")
else:
    print("No previous run data found.")
