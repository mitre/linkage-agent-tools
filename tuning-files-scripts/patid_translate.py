import argparse
import csv
import sys
from pathlib import Path

from dcctools.config import Configuration

parser = argparse.ArgumentParser(
    description="Tool for translating linkage table to patid table for scoring"
)
parser.add_argument(
    "--dotools", nargs=1, required=True, help="data-owner-tools project path"
)
args = parser.parse_args()

data_owner_tools_path = Path(args.dotools[0])

c = Configuration("config.json")
systems = c.systems
header = ["LINK_ID"]
header.extend(systems)

pii_line_map = {}

for s in systems:
    pii_csv_path = Path(data_owner_tools_path) / "temp-data/pii_{}.csv".format(s)
    with open(pii_csv_path) as pii_csv:
        pii_reader = csv.reader(pii_csv)
        next(pii_reader)
        pii_line_map[s] = list(pii_reader)

result_csv_path = Path(c.matching_results_folder) / "link_ids.csv"
patid_csv_path = Path(c.matching_results_folder) / "patid_link_ids.csv"

with open(result_csv_path) as csvfile:
    link_id_reader = csv.DictReader(csvfile)
    with open(patid_csv_path, "w", newline="", encoding="utf-8") as patid_file:
        writer = csv.DictWriter(patid_file, fieldnames=header)
        writer.writeheader()
        for link in link_id_reader:
            row = {"LINK_ID": link["LINK_ID"]}
            for s in systems:
                if len(link[s]) > 0:
                    pii_line = link[s]
                    patid = pii_line_map[s][int(pii_line)][0]
                    row[s] = patid
            writer.writerow(row)

print("results/patid_link_ids.csv created")
