#!/usr/bin/env python

import argparse
import json
import logging
import os
from pathlib import Path
import time
import zipfile

from datetime import datetime
from datetime import timedelta
from pymongo import MongoClient

from dcctools.anonlink import Project, Results
from dcctools.config import Configuration

# Delay between run status checks
SLEEP_TIME = 10.0

log = logging.getLogger(__name__)


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
    args = parser.parse_args()
    return args


def do_match(c):
    client = MongoClient(c.mongo_uri)
    database = client.linkage_agent

    if c.household_match:
        log.debug("Processing households")
        with open(Path(c.household_schema)) as schema_file:
            household_schema = schema_file.read()
            project_name = "fn-phone-addr-zip"
            household_project = Project(
                project_name,
                household_schema,
                c.systems,
                c.entity_service_url,
                c.blocked,
            )
            household_project.start_project()
            for system in c.systems:
                household_project.upload_clks(
                    system, c.get_household_clks_raw(system, project_name)
                )
            if type(c.matching_threshold) == list:
                threshold = c.matching_threshold[0]
            else:
                threshold = c.matching_threshold
            household_project.start_run(threshold)
            running = True
            while running:
                status = household_project.get_run_status()
                print(status)
                if status.get("state") == "completed":
                    running = False
                    break
                time.sleep(SLEEP_TIME)
            result_json = household_project.get_results()
            results = Results(c.systems, project_name, result_json)
            results.insert_results(database.household_match_groups)
    else:
        log.debug("Processing individuals")
        if c.blocked:
            log.debug("Blocked, extracting CLKs and blocks")
            for system in c.systems:
                c.extract_clks(system)
                c.extract_blocks(system)

        iter_num = 0
        for i, (project_name, schema) in enumerate(c.load_schema().items()):
            iter_num = iter_num + 1
            project = Project(
                project_name, schema, c.systems, c.entity_service_url, c.blocked
            )
            project.start_project()
            for system in c.systems:
                if c.blocked:
                    project.upload_clks_blocked(
                        system,
                        c.get_clk(system, project_name),
                        c.get_block(system, project_name),
                    )
                else:
                    project.upload_clks(system, c.get_clks_raw(system, project_name))
            if type(c.matching_threshold) == list:
                threshold = c.matching_threshold[i]
            else:
                threshold = c.matching_threshold
            project.start_run(threshold)
            running = True
            print("\n--- RUNNING ---\n")
            while running:
                status = project.get_run_status()
                print(status)
                if status.get("state") == "completed":
                    running = False
                    break
                time.sleep(SLEEP_TIME)
            print("\n--- Getting results ---\n")
            result_json = project.get_results()
            results = Results(c.systems, project_name, result_json)
            print(
                "Matching groups for system "
                + str(iter_num)
                + " of "
                + str(len(c.load_schema().items()))
            )
            results.insert_results(database.match_groups)


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
    timestamps = validate_metadata(config)
    print(timestamps)
    do_match(config, timestamps)
