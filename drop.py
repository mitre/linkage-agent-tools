#!/usr/bin/env python

import argparse

from pymongo import MongoClient

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


if __name__ == "__main__":
    args = parse_args()
    c = Configuration(args.config)
    client = MongoClient(c.mongo_uri)
    database = client.linkage_agent
    database.match_groups.drop()
    database.household_match_groups.drop()
    print("Database cleared.")
