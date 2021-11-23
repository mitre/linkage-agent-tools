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

link_id_csv_path = Path(c.matching_results_folder) / "link_ids.csv"


with open(link_id_csv_path) as csvfile:
    link_id_rows = csv.DictReader(csvfile)
    # drop keys with empty string values
    link_id_rows = list(map(lambda r: {k: v for k, v in r.items() if v},
                            link_id_rows))


def find_link_id(result):
    matching_fn = lambda r: all(k == 'run_results' or (k in r and int(r[k]) in result[k]) for k in result.keys())
    link_id = next(filter(matching_fn, link_id_rows))['LINK_ID']
    return link_id


def describe(changed, project, args):
    linkid = changed['link_id']
    if args.linkids:
        print(linkid)
    else:
        if 'new' not in changed or len(changed['new']) == 0:
            sites = changed['original'].keys() - set(['run_results'])
            print(f"LINKID {linkid} was created using only {project}\
 -- sites: {list(sites)}")
        else:
            delta = changed['original'].keys() - changed['new'].keys() - set(['run_results'])
            print(f"LINKID {linkid} links to {' and '.join(delta)} only by {project}\
 -- remaining links are {list(changed['new'].keys())}")

    if args.debug:
        pp(changed)


def main():
    parser = argparse.ArgumentParser(
        description="Tool for reviewing how removing one project\
                     will affect overall matching"
    )

    parser.add_argument(
        "-p", "--project",
        help="Select a project to test removing. \
              Default: iterate through all defined projects",
    )

    parser.add_argument(
        "-l", "--linkids", action="store_true",
        help="Print out ONLY the LINKIDs without additional description",
    )

    parser.add_argument(
        "-d", "--debug", action="store_true",
        help="Print out additional detail for debugging",
    )

    args = parser.parse_args()

    # get some overall analytics. total match pairs, total links
    total = database.match_groups.count_documents({})
    print(f"Total number of matches: {total}")

    total = database.match_groups.aggregate([{
        "$group": {
            "_id": None,
            "count": {
                "$sum": {"$size": "$run_results"}
            }
        }
    }])
    for doc in total:  # should only be one result in the cursor
        count = doc['count']
        print(f"Total number of matched pairs (run_results): {count}")

    for project in c.projects:
        if args.project and args.project != project:
            continue

        changed_results = []
        print(project.upper())
        query = {"run_results.project": project}
        count = database.match_groups.count_documents(query)
        print(f"{count} results have a match on {project}")

        only_this_project = {**query, "run_results": {"$size": 1}}
        count = database.match_groups.count_documents(only_this_project)
        print(f"{count} results have a match ONLY on {project}")

        if count:
            results = database.match_groups.find(only_this_project, {"_id": 0})
            for result in results:
                changed_results.append({'original': result,
                                        'link_id': find_link_id(result)})

        # find results that would be different if this project were excluded
        results = database.match_groups.find(query, {"_id": 0})
        for result in results:
            if len(result['run_results']) == 1:
                continue  # already addressed in the "match ONLY on" logic ^

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
            # (it may be possible to do this by mongo aggregation,
            #  but i hope this is more readable)

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

            # now compare the old result to the new result, see what changed
            for key, value in result.items():
                if key in ['run_results', '_id']:
                    continue

                if key not in new_result or set(value) != new_result[key]:
                    # find the link_id belonging to this result
                    link_id = find_link_id(result)
                    changed_results.append({'original': result,
                                            'new': new_result,
                                            'link_id': link_id})
                    break

        count = len(changed_results)
        print(f"Total # of changes by removing this project: {count}")
        if changed_results:
            for r in changed_results:
                describe(r, project, args)

        print()


if __name__ == '__main__':
    main()
