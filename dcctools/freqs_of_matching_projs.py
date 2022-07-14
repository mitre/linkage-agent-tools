from config import Configuration
from pymongo import MongoClient

c = Configuration("config.json")
client = MongoClient(c.mongo_uri)
database = client.linkage_agent

results = database.match_groups.aggregate(
    [
        {
            "$group": {
                "_id": {"$size": "$run_results"},
                "total": {"$sum": 1},
            }
        }
    ],
    allowDiskUse=True,
)

for result in results:
    print(result)
