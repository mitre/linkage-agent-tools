from dcctools.config import Configuration
from tinydb import TinyDB
from dcctools.deconflict import deconflict
from functools import reduce
from pathlib import Path
import uuid
import csv

c = Configuration("config.json")
database = TinyDB('results.json')

systems = c.systems()
header = ['LINK_ID']
header.extend(systems)

result_csv_path = Path(c.matching_results_folder()) / "link_ids.csv"

with open(result_csv_path, 'w', newline='') as csvfile:
  writer = csv.DictWriter(csvfile, fieldnames=header)
  writer.writeheader()

  for row in database.all():
    conflict = reduce(lambda acc, s: acc | len(row.get(s, [])) > 1, systems, False)
    final_record = {}
    if conflict:
      final_record = deconflict(row, systems)
    else:
      for s in systems:
        id = row.get(s, None)
        if id != None:
          final_record[s] = id[0]
    final_record['LINK_ID'] = uuid.uuid1()
    writer.writerow(final_record)
