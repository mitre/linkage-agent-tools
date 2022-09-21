#!/usr/bin/env python

import argparse
import csv
import json
import os
import shutil
import uuid
import zipfile
from datetime import datetime
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


def zip_and_clean(system_output_path, system, timestamp):
    with zipfile.ZipFile(
        system_output_path.parent / f"{system}.zip", mode="w"
    ) as system_archive:
        system_archive.write(
            system_output_path / f"{system}{timestamp}.csv",
            Path(system) / f"{system}{timestamp}.csv",
        )
        system_archive.write(
            system_output_path / f"{system}-metadata{timestamp}.json",
            Path(system) / f"{system}-metadata{timestamp}.json",
        )
    print(system_output_path.parent / f"{system}.zip", "created")
    shutil.rmtree(system_output_path)
    print("Uncompressed directory removed")


def process_output(link_id_path, output_path, system, metadata):
    data_owner_id_time = datetime.now()
    timestamp = data_owner_id_time.strftime("%Y%m%dT%H%M%S")
    n_rows = 0
    with open(link_id_path) as csvfile:
        reader = csv.DictReader(csvfile)
        with open(
            output_path / f"{output_path.name}{timestamp}.csv", "w", newline=""
        ) as system_csvfile:
            writer = csv.DictWriter(system_csvfile, fieldnames=["LINK_ID", system])
            writer.writeheader()
            for row in reader:
                if len(row[system]) > 0:
                    n_rows += 1
                    writer.writerow({"LINK_ID": row["LINK_ID"], system: row[system]})
    system_metadata = {
        "link_id_metadata": {
            "creation_date": metadata["creation_date"],
            "uuid1": metadata["uuid1"],
        },
        "input_system_metadata": {
            key: val for key, val in metadata["input_system_metadata"][system].items()
        },
        "output_system_metadata": {
            "creation_date": data_owner_id_time.isoformat(),
            "number_of_records": n_rows,
            "uuid1": str(uuid.uuid1()),
        },
    }
    with open(
        output_path / f"{output_path.name}-metadata{timestamp}.json", "w", newline=""
    ) as system_metadata_file:
        json.dump(system_metadata, system_metadata_file, indent=2)
    return timestamp


def do_data_owner_ids(c):
    if c.household_match:
        link_ids = sorted(
            Path(c.matching_results_folder).glob("household_link_ids*.csv")
        )
    else:
        link_ids = sorted(Path(c.matching_results_folder).glob("link_ids*.csv"))

    if len(link_ids) > 1:
        print("More than one link_id file found")
        link_id_times = [
            datetime.strptime(
                x.name.replace("link_ids", "")
                .replace("household", "")
                .replace(".csv", ""),
                "%Y%m%dT%H%M%S",
            )
            for x in link_ids
        ]
        most_recent = link_ids[link_id_times.index(max(link_id_times))]
        print(f"Using most recent link_id file: {most_recent}")

        link_id_path = most_recent
    else:
        link_id_path = link_ids[0]

    link_id_metadata_name = link_id_path.parent / link_id_path.name.replace(
        "link_ids", "link_id-metadata"
    ).replace(".csv", ".json")
    with open(link_id_metadata_name) as metadata_file:
        metadata = json.load(metadata_file)

    for system in c.systems:
        if c.household_match:
            system_output_path = Path(c.output_folder) / "{}_households".format(system)
        else:
            system_output_path = Path(c.output_folder) / system
        os.makedirs(system_output_path, exist_ok=True)
        timestamp = process_output(link_id_path, system_output_path, system, metadata)
        zip_and_clean(system_output_path, system, timestamp)


if __name__ == "__main__":
    args = parse_args()
    config = Configuration(args.config)
    do_data_owner_ids(config)
