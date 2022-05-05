#!/usr/bin/env python

import argparse
import logging
from pathlib import Path
import json

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


if __name__ == "__main__":
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    config = Configuration(args.config)

    client = MongoClient(config.mongo_uri)
    database = client.linkage_agent
    do_match(config)
