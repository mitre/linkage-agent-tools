from pymongo import MongoClient

from config import Configuration

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
    ]
)

for result in results:
    print(result)
