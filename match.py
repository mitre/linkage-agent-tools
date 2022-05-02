#!/usr/bin/env python

import argparse
import logging
from pathlib import Path
import time
import json

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
    parser.add_argument(
        "--projects_only",
        default=False,
        action="store_true",
        help="Run projects and generate results, but don't perform matching"
    )
    parser.add_argument(
        "--match_only",
        default=False,
        action="store_true",
        help="Perform matching based on stored results"
    )
    args = parser.parse_args()
    return args

def run_projects(c):
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
            Path(c.project_results_dir).mkdir(parents=True, exist_ok=True)
            with open(Path(c.project_results_dir) / f'{project_name}.json', 'w') as json_file:
                json.dump(result_json, json_file)

def do_match(systems, project_results_dir, database):
    print(project_results_dir)
    for file_name in Path(project_results_dir).glob('*.json'):
        project_name = Path(file_name).stem
        with open(file_name) as file:
            result_json = json.load(file)
            results = Results(systems, project_name, result_json)
            print('Matching groups for system f{project_name}')
            results.insert_results(database.match_groups)

if __name__ == "__main__":
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    config = Configuration(args.config)

    client = MongoClient(config.mongo_uri)
    database = client.linkage_agent

    if args.projects_only:
        run_projects(config)
    elif args.match_only:
        do_match(config.systems, config.project_results_dir, database)
    else:
        run_projects(config)
        do_match(config.systems, config.project_results_dir, database)
