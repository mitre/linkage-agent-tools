#!/usr/bin/env python

import argparse
import csv
import json
import uuid
from functools import reduce
from pathlib import Path

from pymongo import MongoClient

from dcctools.config import Configuration
from dcctools.deconflict import deconflict


def parse_args():
    parser = argparse.ArgumentParser(
        description="Tool for generating LINK_IDs in the CODI PPRL process"
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help='Configuration file (default "config.json")',
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        default=False,
        help="Drop match_groups collection from database when done (default False)",
    )
    args = parser.parse_args()
    return args


def do_link_ids(c, remove=False):
    client = MongoClient(c.mongo_uri)
    database = client.linkage_agent

    systems = c.systems
    header = ["LINK_ID"]
    header.extend(systems)

    all_ids_for_systems = {}
    all_ids_for_households = {}
    first_project = c.projects[0]
    individual_linkages = []
    for system in systems:
        if c.household_match:
            household_clk_json = c.get_household_clks_raw(system, "fn-phone-addr-zip")
            h_clks = json.loads(household_clk_json)
            h_system_size = len(h_clks["clks"])
            all_ids_for_households[system] = list(range(h_system_size))
        else:
            clk_json = c.get_clks_raw(system, first_project)
            clks = json.loads(clk_json)
            system_size = len(clks["clks"])
            all_ids_for_systems[system] = list(range(system_size))

    if c.household_match:
        result_csv_path = Path(c.matching_results_folder) / "household_link_ids.csv"
        with open(result_csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            final_records = []
            for row in database.household_match_groups.find(no_cursor_timeout=True):
                final_record = {}
                for s in systems:
                    record_id = row.get(s, None)
                    if record_id != None:
                        final_record[s] = record_id[0]
                        all_ids_for_households[s].remove(record_id[0])
                final_records.append(final_record)

            for system, unmatched_ids in all_ids_for_households.items():
                for unmatched_id in unmatched_ids:
                    final_record = {system: unmatched_id}
                    final_records.append(final_record)

            for record in final_records:
                record["LINK_ID"] = uuid.uuid1()
                writer.writerow(record)
        print(f"{result_csv_path} created")
    else:
        result_csv_path = Path(c.matching_results_folder) / "link_ids.csv"
        with open(result_csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=header)
            writer.writeheader()
            for row in database.match_groups.find(no_cursor_timeout=True):
                conflict = reduce(
                    lambda acc, s: acc | len(row.get(s, [])) > 1, systems, False
                )
                final_record = {}
                if conflict:
                    final_record = deconflict(row, systems)
                else:
                    for s in systems:
                        record_id = row.get(s, None)
                        if record_id != None:
                            final_record[s] = record_id[0]
                            all_ids_for_systems[s].remove(record_id[0])
                final_record["LINK_ID"] = uuid.uuid1()
                individual_linkages.append(final_record)
                writer.writerow(final_record)

            for system, unmatched_ids in all_ids_for_systems.items():
                for unmatched_id in unmatched_ids:
                    final_record = {system: unmatched_id}
                    final_record["LINK_ID"] = uuid.uuid1()
                    individual_linkages.append(final_record)
                    writer.writerow(final_record)
        print(f"{result_csv_path} created")

    if remove:
        print("Removing records from database")
        database.match_groups.drop()
        database.household_match_groups.drop()
        print("Match groups deleted from database")
    else:
        print(
            "Match groups not deleted as this point (they might be deleted later in the process)"
        )


if __name__ == "__main__":
    args = parse_args()
    config = Configuration(args.config)
    do_link_ids(config, args.remove)
