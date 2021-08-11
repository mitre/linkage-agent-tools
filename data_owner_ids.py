from dcctools.config import Configuration
from pathlib import Path
import csv

c = Configuration("config.json")
result_csv_path = Path(c.matching_results_folder()) / "link_ids.csv"
systems = c.systems()

for s in systems:
  with open(result_csv_path) as csvfile:
    reader = csv.DictReader(csvfile)
    system_csv_path = Path(c.output_folder()) / "{}.csv".format(s)
    with open(system_csv_path, 'w', newline='') as csvfile:
      writer = csv.DictWriter(csvfile, fieldnames=['LINK_ID', s])
      writer.writeheader()
      for row in reader:
        if len(row[s]) > 0:
          writer.writerow({'LINK_ID': row['LINK_ID'], s: row[s]})