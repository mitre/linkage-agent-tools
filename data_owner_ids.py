#!/usr/bin/env python

import argparse
import csv
from pathlib import Path

from dcctools.config import Configuration


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="config.json",
        help='Configuration file (default "config.json")',
    )
    args = parser.parse_args()
    return args


def process_csv(csv_path, system_csv_path, system):
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile)
        with open(system_csv_path, "w", newline="") as system_csvfile:
            writer = csv.DictWriter(system_csvfile, fieldnames=["LINK_ID", system])
            writer.writeheader()
            for row in reader:
                if len(row[system]) > 0:
                    writer.writerow({"LINK_ID": row["LINK_ID"], system: row[system]})


def do_data_owner_ids(c):
    if c.household_match:
        csv_path = Path(c.matching_results_folder) / "household_link_ids.csv"
    else:
        csv_path = Path(c.matching_results_folder) / "link_ids.csv"

    for system in c.systems:
        if c.household_match:
            system_csv_path = Path(c.output_folder) / "{}_households.csv".format(system)
        else:
            system_csv_path = Path(c.output_folder) / "{}.csv".format(system)
        process_csv(csv_path, system_csv_path, system)
        print(f"{system_csv_path} created")


if __name__ == "__main__":
    args = parse_args()
    config = Configuration(args.config)
    do_data_owner_ids(config)
