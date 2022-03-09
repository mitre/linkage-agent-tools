#!/usr/bin/env python

import argparse

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


def do_validate(c):
    missing_files = set(c.validate_all_present())
    if len(missing_files) == 0:
        print("All necessary input is present")
    else:
        print("One or more files missing from data owners:")
        for filename in missing_files:
            print(filename)


if __name__ == "__main__":
    args = parse_args()
    config = Configuration(args.config)
    do_validate(config)
