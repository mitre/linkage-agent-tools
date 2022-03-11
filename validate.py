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
    missing, unexpected = c.validate_all_present()
    if len(missing) == 0:
        print("All necessary input is present")
    else:
        if len(missing) > 1:
            warning_txt = "Multiple expected files are missing"
        elif len(missing) == 1:
            warning_txt = "One expected file is missing"
        print(f"WARNING: {warning_txt}")
        print("\nMissing files:")
        for filename in sorted(missing):
            print(f"\t{filename}")

    if len(unexpected) > 0:
        print("\nWARNING: Individual and household hashes appear to be present")
        print("at the same time, or other unexpected files are in the inbox.")
        print("\nUnexpected files:")
        for filename in sorted(unexpected):
            print(f"\t{filename}")
    else:
        print("\nNo unexpected files are present")


if __name__ == "__main__":
    args = parse_args()
    config = Configuration(args.config)
    do_validate(config)
