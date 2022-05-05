from pymongo import MongoClient

from config import Configuration

c = Configuration("config.json")
client = MongoClient(c.mongo_uri)
database = client.linkage_agent


results = database.match_groups.aggregate(
    [
        {"$unwind": "$run_results"},
        {"$group": {"_id": "$run_results.project", "total": {"$sum": 1}}},
    ]
)

for result in results:
    print(result)
