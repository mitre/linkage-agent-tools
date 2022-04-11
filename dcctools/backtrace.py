from pathlib import Path
import time
import argparse
import csv

from pymongo import MongoClient

from config import Configuration

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

result_csv_path = Path(c.matching_results_folder) / "link_ids.csv"

link_id_row = None
with open(result_csv_path) as csvfile:
    reader = csv.DictReader(csvfile)
    link_id_row = next(filter(lambda r: r['LINK_ID'] == args.linkid, reader))

print(f"Actual linkages for {args.linkid}:")

query = {}
for (key, value) in link_id_row.items():
    if key != 'LINK_ID' and len(value) > 0:
        query[key] = int(value)
        print(f"{key}: {value}")

print('---')

for result in database.match_groups.find(query):
    print(result)
