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
from definitions import TIMESTAMP_FMT


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="config.json",
        help='Configuration file (default "config.json")',
    )
    args = parser.parse_args()
    return args


def zip_and_clean(system_output_path, system, timestamp, household_match):
    if household_match:
        zip_path = system_output_path.parent / f"{system}_households.zip"
    else:
        zip_path = system_output_path.parent / f"{system}.zip"
    with zipfile.ZipFile(zip_path, mode="w") as system_archive:
        if household_match:
            system_archive.write(
                system_output_path / "households" / f"{system}_households.csv",
                arcname=str(Path("output") / "households" / f"{system}_households.csv"),
            )
        else:
            system_archive.write(
                system_output_path / f"{system}.csv",
                arcname=str(Path("output") / f"{system}.csv"),
            )
        system_archive.write(
            system_output_path / f"{system}-metadata{timestamp}.json",
            arcname=str(Path("output") / f"{system}-metadata{timestamp}.json"),
        )

    print(zip_path.name, "created")
    shutil.rmtree(system_output_path)
    print("Uncompressed directory removed")


def process_output(link_id_path, output_path, system, metadata, household_match):
    data_owner_id_time = datetime.now()
    timestamp = data_owner_id_time.strftime(TIMESTAMP_FMT)
    n_rows = 0
    with open(link_id_path) as csvfile:
        reader = csv.DictReader(csvfile)
        if household_match:
            csv_path = output_path / "households" / f"{system}_households.csv"
        else:
            csv_path = output_path / f"{system}.csv"

        with open(csv_path, "w", newline="") as system_csvfile:
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
        output_path / f"{system}-metadata{timestamp}.json", "w", newline=""
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
        print(link_ids)
        link_id_times = [
            datetime.strptime(x.name[-19:-4], TIMESTAMP_FMT) for x in link_ids
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
        system_output_path = Path(c.output_folder) / "output"
        os.makedirs(system_output_path, exist_ok=True)
        if c.household_match:
            os.makedirs(system_output_path / "households", exist_ok=True)
        timestamp = process_output(
            link_id_path, system_output_path, system, metadata, c.household_match
        )
        zip_and_clean(system_output_path, system, timestamp, c.household_match)


if __name__ == "__main__":
    args = parse_args()
    config = Configuration(args.config)
    do_data_owner_ids(config)
