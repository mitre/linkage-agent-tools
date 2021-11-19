from pathlib import Path
import time
import argparse
import csv
from pprint import pprint as pp

from pymongo import MongoClient

from dcctools.config import Configuration

c = Configuration("config.json")
client = MongoClient(c.mongo_uri)
database = client.linkage_agent

parser = argparse.ArgumentParser(
    description="Tool for tracing a LINKID back to its matching record in MongoDB"
)
parser.add_argument(
    "linkid",
    help="The LINKID to find",
)
args = parser.parse_args()



# 2 get some overall analytics. total match pairs, total links
total = database.match_groups.count_documents({})
print(f"total number of matches: {total}")

total = database.match_groups.aggregate([{
    "$group": {
        "_id": None,
        "count": {
            "$sum": {"$size": "$run_results"}
        }
    }
}])
for doc in total:  # should only be one
    print(f"total number of matched pairs (run_results): {doc['count']}")


# 2. get analytics on how many matches are based on each project

# 3. get analytics on what matches would be different if each project were excluded - numbers, specific examples

for project in c.projects:
    print(project.upper())
    query = {"run_results.project": project}
    count = database.match_groups.count_documents(query)
    print(f"{count} results have a match on {project}")

    only_this_project = {**query, "run_results": {"$size": 1}}
    count = database.match_groups.count_documents(only_this_project)
    print(f"{count} results have a match ONLY on {project}")

    if count:
        results = database.match_groups.find(only_this_project)
        for result in results:
            pp(result)

    # Now find results that would be different if this project were excluded
    different_results = []
    results = database.match_groups.find(query)
    for result in results:
        if len(result['run_results']) == 1:
            continue  # we already addressed this above, in the "match ONLY on" section

        # sample result:
        #  {
        #   "site_c": [518],
        #   "site_d": [317],
        #   "site_e": [732],
        #   "run_results": [
        #     {
        #       "site_c": 518,
        #       "site_d": 317,
        #       "project": "name-sex-dob-phone"
        #     },
        #     {
        #       "site_c": 518,
        #       "site_d": 317,
        #       "project": "name-sex-dob-zip"
        #     },
        #     {
        #       "site_d": 317,
        #       "site_e": 732,
        #       "project": "name-sex-dob-parents"
        #     },
        #     {
        #       "site_d": 518,
        #       "site_e": 732,
        #       "project": "name-sex-dob-parents"
        #     }
        #   ]
        # }

        # basically the idea is we need to rebuild the site lists,
        # but don't include the given project
        # (it may be possible to do this by mongo aggregation but i hope this is more readable)

        new_result = {}

        for project_result in result['run_results']:
            if project_result['project'] == project:
                continue

            for key, value in project_result.items():
                if key == 'project':
                    continue

                if key not in new_result:
                    new_result[key] = set()

                new_result[key].add(value)

        # now compare the old result to the new result, see if anything changed
        for key, value in result.items():
            if key in ['run_results', '_id']:
                continue

            if key not in new_result or set(value) != new_result[key]:
                different_results.append((result, new_result))
                break


    print(f"number of changes by removing this project: {len(different_results)}")
    if different_results:
        pp(different_results)

    print()
