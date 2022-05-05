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
    parser.add_argument("--project", default=None, help="Run specific project only")
    return parser.parse_args()


def run_projects(c, project_name=None):
    if c.household_match:
        log.debug("Processing households")
        project_name = "fn-phone-addr-zip"
        run_project(c, project_name, households=True)
    else:
        log.debug("Processing individuals")
        if c.blocked:
            log.debug("Blocked, extracting CLKs and blocks")
            for system in c.systems:
                c.extract_clks(system)
                c.extract_blocks(system)
        if project_name:
            run_project(c, project_name)
        else:
            for project_name in c.load_schema().keys():
                run_project(c, project_name)


def run_project(c, project_name=None, households=False):
    schema = c.load_household_schema() if households else c.load_schema()[project_name]
    project = Project(project_name, schema, c.systems, c.entity_service_url, c.blocked)
    project.start_project()

    for system in c.systems:
        if households:
            project.upload_clks(system, c.get_household_clks_raw(system, project_name))
        else:
            if c.blocked:
                project.upload_clks_blocked(
                    system,
                    c.get_clk(system, project_name),
                    c.get_block(system, project_name),
                )
            else:
                project.upload_clks(system, c.get_clks_raw(system, project_name))
    threshold = c.get_project_threshold(project_name)
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
    with open(Path(c.project_results_dir) / f"{project_name}.json", "w") as json_file:
        json.dump(result_json, json_file)


if __name__ == "__main__":
    args = parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    config = Configuration(args.config)
    run_projects(config, args.project)
