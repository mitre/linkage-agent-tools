#!/usr/bin/env python

import argparse
import json
import logging
from pathlib import Path
import os
import json
import zipfile

from datetime import datetime, timedelta
from pathlib import Path
from pymongo import MongoClient

from dcctools.anonlink import Results
from dcctools.config import Configuration

# Delay between run status checks
SLEEP_TIME = 10.0

log = logging.getLogger(__name__)


class MissingResults(Exception):
    def __init__(self, expected_results, available_results, message=None):
        message = (
            message if message else self.message(expected_results, available_results)
        )
        super().__init__(message)

    def message(self, expected_results, available_results):
        missing_results = expected_results.difference(available_results)
        return f'Missing results for projects: {", ".join(missing_results)}'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="config.json",
        help='Configuration file (default "config.json")',
    )
    parser.add_argument(
        "--verbose", default=False, action="store_true", help="Show debugging output"
    )
    return parser.parse_args()


def has_results_available(config, projects=None):
    available_results = set(
        map(lambda x: x.stem, Path(config.project_results_dir).glob("*.json"))
    )
    expected_results = set(projects) if projects else set(config.projects)
    if expected_results <= available_results:
        return True
    else:
        raise MissingResults(expected_results, available_results)


def do_match(config, projects=None):
    projects = projects if projects else config.projects
    database = MongoClient(config.mongo_uri).linkage_agent
    if config.household_match:
        do_matching(config, ["fn-phone-addr-zip"], database.household_match_groups)
    else:
        do_matching(config, projects, database.match_groups)


def do_matching(config, projects, collection):
    has_results_available(config, projects)
    for project_name in projects:
        with open(Path(config.project_results_dir) / f"{project_name}.json") as file:
            result_json = json.load(file)
            results = Results(config.systems, project_name, result_json)
            print(f"Matching for project: {project_name}")
            results.insert_results(collection)


def validate_metadata(c):
    timestamps = []
    for site_archive in os.listdir(c.inbox_folder):
        if site_archive != ".DS_Store":
            with zipfile.ZipFile("/".join([c.inbox_folder, site_archive])) as archive:
                found_metadata = False
                for fname in archive.namelist():
                    if "metadata" in fname:
                        found_metadata = True
                        mname = fname.replace("output/metadata", "").replace(".json", "")
                        timestamp = datetime.strptime(mname, "%Y%m%dT%H%M%S")
                        timestamps.append(timestamp)
                        with archive.open(fname, "r") as metadata_fp:
                            metadata = json.load(metadata_fp)
                        garble_time = datetime.fromisoformat(metadata["garble_date"])
                        assert (garble_time-timestamp) < timedelta(seconds=1), f"Metadata timecode {timestamp} does not match listed garble time {garble_time}"
                assert found_metadata, f"Unable to locate metadata in archive {c.inbox_folder}/{site_archive}"

    return timestamps


if __name__ == "__main__":
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    config = Configuration(args.config)

    client = MongoClient(config.mongo_uri)
    database = client.linkage_agent

    timestamps = validate_metadata(config)
    do_match(config, timestamps)
