import csv
from pathlib import Path
from dcctools.config import Configuration

c = Configuration("config.json")
systems = c.systems()
header = ['LINK_ID']
header.extend(systems)

household_pos_csv_path = Path(c.matching_results_folder()) / "household_link_ids.csv"
hid_csv_path = Path(c.matching_results_folder()) / "household_id_link_ids.csv"

hid_line_map = {}

for s in systems:
  hid_mapping_path = Path('/Users/apellitieri/Desktop/CDC/CODI/data-owner-tools') / "{}-hid-mapping.csv".format(s)
  with open(hid_mapping_path) as hid_csv:
    hid_reader = csv.reader(hid_csv)
    next(hid_reader)
    hid_line_map[s] = list(hid_reader)

with open(household_pos_csv_path) as csvfile:
  link_id_reader = csv.DictReader(csvfile)
  with open(hid_csv_path, 'w', newline='', encoding='utf-8') as hid_file:
    writer = csv.DictWriter(hid_file, fieldnames=header)
    writer.writeheader()
    for link in link_id_reader:
      row = {'LINK_ID': link['LINK_ID']}
      for s in systems:
        if len(link[s]) > 0:
          hid_pos_line = link[s]
          household_id = hid_line_map[s][int(hid_pos_line)][1]
          row[s] = household_id
      writer.writerow(row)

print('results/household_id_link_ids.csv created')
