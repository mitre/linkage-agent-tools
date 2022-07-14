from config import Configuration
from pymongo import MongoClient

c = Configuration("config.json")
client = MongoClient(c.mongo_uri)
database = client.linkage_agent

version_array = client.server_info()["versionArray"]

# $function was implemented in 4.4
if version_array[0] > 4 or (version_array[0] == 4 and version_array[1] >= 4):
    results = database.match_groups.aggregate(
        [
            {
                "$addFields": {
                    "key": {
                        "$function": {
                            "body": "function(run_results) {\
                                     const key = { \
                                       'name-sex-dob-addr': 0, \
                                       'name-sex-dob-parents': 0, \
                                       'name-sex-dob-phone': 0, \
                                       'name-sex-dob-zip': 0\
                                     };\
                                     run_results.forEach(r => key[r.project]++);\
                                     return key;\
                                    }",
                            "args": ["$run_results"],
                            "lang": "js",
                        }
                    }
                }
            },
            {"$group": {"_id": "$key", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
        ],
        allowDiskUse=True,
    )
else:
    results = database.match_groups.aggregate(
        [
            {"$unwind": {"path": "$run_results", "preserveNullAndEmptyArrays": True}},
            {"$sort": {"_id": 1, "run_results.project": 1}},
            {
                "$project": {
                    "projectName": {"$substr": ["$run_results.project", 13, -1]}
                }
            },
            {"$group": {"_id": "$_id", "projects": {"$push": "$projectName"}}},
            {
                "$addFields": {
                    "shape": {
                        "$reduce": {
                            "input": "$projects",
                            "initialValue": "",
                            "in": {"$concat": ["$$value", ",", "$$this"]},
                        }
                    }
                }
            },
            {"$group": {"_id": "$shape", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ],
        allowDiskUse=True,
    )


for result in results:
    print(result)
