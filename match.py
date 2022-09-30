#!/usr/bin/env python

import argparse
import datetime
import json
import logging
import uuid
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
    available_results = set()
    expected_results = set(projects) if projects else set(config.projects)
    project_to_filenames = {}
    for expected_result in expected_results:
        found_result = [
            x.name
            for x in Path(config.project_results_dir).glob(f"{expected_result}*.json")
        ]
        if len(found_result) == 1:
            found_project_name = found_result[0][: len(expected_result)]
            project_to_filenames[expected_result] = found_result[0]
            available_results.add(found_project_name)
    if expected_results <= available_results:
        return project_to_filenames
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
    match_time = datetime.datetime.now()
    metadata = {
        "creation_date": match_time.isoformat(),
        "projects": projects,
        "uuid1": str(uuid.uuid1()),
    }
    projects_to_filenames = has_results_available(config, projects)
    for project_name in projects:
        with open(
            Path(config.project_results_dir) / projects_to_filenames[project_name]
        ) as file:
            result_json = json.load(file)
            metadata[project_name] = {
                "number_of_records": len(result_json.get("groups", []))
            }
            results = Results(config.systems, project_name, result_json)
            results.insert_results(collection)
    timestamp = match_time.strftime("%Y%m%dT%H%M%S")
    with open(
        Path(config.project_results_dir) / f"match-metadata-{timestamp}.json", "w+"
    ) as metadata_file:
        json.dump(metadata, metadata_file, indent=2)


if __name__ == "__main__":
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    config = Configuration(args.config)

    client = MongoClient(config.mongo_uri)
    database = client.linkage_agent
    do_match(config)
