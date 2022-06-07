#!/usr/bin/env python

import argparse
import logging
from pathlib import Path
import time
import json

from dcctools.anonlink import Project
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
    return parser.parse_args()

def run_projects(c):
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

            if type(c.household_threshold) == list:
                threshold = c.household_threshold[0]
            else:
                threshold = c.household_threshold

            household_project.start_run(threshold)
            running = True
            print("\n--- RUNNING ---\n")
            while running:
                status = household_project.get_run_status()
                print(status)
                if status.get("state") == "completed":
                    running = False
                    break
                time.sleep(SLEEP_TIME)
            print("\n--- Getting results ---\n")
            result_json = household_project.get_results()
            Path(c.project_results_dir).mkdir(parents=True, exist_ok=True)
            with open(Path(c.project_results_dir) / f'{project_name}.json', 'w') as json_file:
                json.dump(result_json, json_file)
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
            Path(c.project_results_dir).mkdir(parents=True, exist_ok=True)
            with open(Path(c.project_results_dir) / f'{project_name}.json', 'w') as json_file:
                json.dump(result_json, json_file)

if __name__ == "__main__":
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    config = Configuration(args.config)
    run_projects(config)

