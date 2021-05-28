from dcctools.config import Configuration
from pymongo import MongoClient
from dcctools.deconflict import deconflict
from functools import reduce
from pathlib import Path
import uuid
import csv
import json
import argparse
import os

parser = argparse.ArgumentParser(description='Tool for generating LINK_IDs in the CODI PPRL process')
parser.add_argument('--remove', action="store_true", help='Drop match_groups collection from database when finished')
args = parser.parse_args()

c = Configuration("config.json")
client = MongoClient(c.mongo_uri())
database = client.linkage_agent

systems = c.systems()
header = ['LINK_ID']
header.extend(systems)

all_ids_for_systems = {}
all_ids_for_households = {}
first_project = c.projects()[0]
for system in systems:
  clk_json = c.get_clks_raw(system, first_project)
  clks = json.loads(clk_json)
  system_size = len(clks['clks'])
  all_ids_for_systems[system] = list(range(system_size))
  household_clk_json = c.get_household_clks_raw(system, 'fn-phone-addr-zip')
  h_clks = json.loads(household_clk_json)
  h_system_size = len(h_clks['clks'])
  all_ids_for_households[system] = list(range(h_system_size))

result_csv_path = Path(c.matching_results_folder()) / "link_ids.csv"

with open(result_csv_path, 'w', newline='') as csvfile:
  writer = csv.DictWriter(csvfile, fieldnames=header)
  writer.writeheader()

  for row in database.match_groups.find():
    conflict = reduce(lambda acc, s: acc | len(row.get(s, [])) > 1, systems, False)
    final_record = {}
    if conflict:
      final_record = deconflict(row, systems)
    else:
      for s in systems:
        id = row.get(s, None)
        if id != None:
          final_record[s] = id[0]
          all_ids_for_systems[s].remove(id[0])
    final_record['LINK_ID'] = uuid.uuid1()
    writer.writerow(final_record)

  for system, unmatched_ids in all_ids_for_systems.items():
    for unmatched_id in unmatched_ids:
      final_record = {system: unmatched_id}
      final_record['LINK_ID'] = uuid.uuid1()
      writer.writerow(final_record)

print('results/link_ids.csv created')

if c.household_match():
  with open('household_pprl_links.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=header)
    writer.writeheader()
    for row in database.household_match_groups.find():
      conflict = reduce(lambda acc, s: acc | len(row.get(s, [])) > 1, systems, False)
      final_record = {}
      if conflict:
        final_record = deconflict(row, systems)
      else:
        for s in systems:
          id = row.get(s, None)
          if id != None:
            final_record[s] = id[0]
            all_ids_for_households[s].remove(id[0])
      final_record['LINK_ID'] = uuid.uuid1()
      writer.writerow(final_record)

    for system, unmatched_ids in all_ids_for_households.items():
      for unmatched_id in unmatched_ids:
        final_record = {system: unmatched_id}
        final_record['LINK_ID'] = uuid.uuid1()
        writer.writerow(final_record)

  print('household_pprl_links.csv created')

if args.remove:
    database.match_groups.drop()
    database.household_match_groups.drop()
