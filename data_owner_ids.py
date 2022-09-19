#!/usr/bin/env python

import argparse
import csv
import json
import os
import uuid
import warnings
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


def extract_metadata_and_zip(system, system_zip_path, system_output_dir_path, n_rows):
    print(str(system_output_dir_path))
    metadata_file_name = system_output_dir_path / (system + "_metadata.json")
    with zipfile.ZipFile(system_zip_path) as system_zip:
        metadata_files = []
        for file_name in system_zip.namelist():
            if "metadata" in file_name:
                metadata_files.append(file_name)
        if len(metadata_files) > 1:
            warnings.warn(
                f"Could not extract metadata from {system}"
                "- too many metadata files found in system archive"
            )
        elif len(metadata_files) < 1:
            warnings.warn(
                f"Could not extract metadata from {system}"
                "- no metadata file found in system archive"
            )
        else:
            with system_zip.open(metadata_files[0], mode="r") as meta_fp:
                metadata = json.load(meta_fp)
            metadata["number_of_links"] = n_rows
            with open(metadata_file_name, "w+") as fp:
                json.dump(metadata, fp)
    zpath = Path(str(system_output_dir_path) + ".zip", at=system + "/")
    with zipfile.ZipFile(zpath, mode="w") as output_zip:
        output_zip.write(metadata_file_name, f"{system}/{system}_metadata.json")
        output_zip.write(
            f"{system_output_dir_path}/{system}.csv", f"{system}/{system}.csv"
        )


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
        "output_system_metadata":{
            "creation_date": data_owner_id_time.isoformat(),
            "number_of_records": n_rows,
            "uuid1": str(uuid.uuid1())
        }
    }
    with open(
        output_path / f"{output_path.name}-metadata{timestamp}.json", "w", newline=""
    ) as system_metadata_file:
        json.dump(system_metadata, system_metadata_file, indent=2)


def process_csv_OLD(csv_path, system_output_dir_path, system, inbox_path):
    os.makedirs(system_output_dir_path, exist_ok=True)
    system_zip_path = Path(inbox_path) / f"{system}.zip"
    n_rows = 0
    with open(csv_path) as csvfile:
        reader = csv.DictReader(csvfile)
        system_path = Path(system_output_dir_path, system + ".csv")
        with open(system_path, "w", newline="") as system_csvfile:
            writer = csv.DictWriter(system_csvfile, fieldnames=["LINK_ID", system])
            writer.writeheader()
            for row in reader:
                if len(row[system]) > 0:
                    n_rows += 1
                    writer.writerow({"LINK_ID": row["LINK_ID"], system: row[system]})
    extract_metadata_and_zip(system, system_zip_path, system_output_dir_path, n_rows)


def do_data_owner_ids_OLD(c):
    if c.household_match:
        csv_path = Path(c.matching_results_folder) / "household_link_ids.csv"
    else:
        csv_path = Path(c.matching_results_folder) / "link_ids.csv"

    for system in c.systems:
        system_csv_path = Path(c.output_folder) / system
        process_csv(csv_path, system_csv_path, system, c.inbox_folder)
        print(f"{system_csv_path} created")


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

    metadata_name = link_id_path.parent / link_id_path.name.replace(
        "link_ids", "link_id-metadata"
    ).replace(".csv", ".json")
    with open(metadata_name) as metadata_file:
        metadata = json.load(metadata_file)

    for system in c.systems:
        if c.household_match:
            system_output_path = Path(c.output_folder) / "{}_households".format(system)
        else:
            system_output_path = Path(c.output_folder) / system
        os.makedirs(system_output_path, exist_ok=True)
        process_output(link_id_path, system_output_path, system, metadata)
        zip_and_clean()
        print(f"{system_output_path} created")


if __name__ == "__main__":
    args = parse_args()
    config = Configuration(args.config)
    do_data_owner_ids(config)
