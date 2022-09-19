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
    missing, unexpected, metadata_issues = c.validate_all_present()
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

    if len(metadata_issues) == 0:
        print("\nNo issues are present in the metadata files for each system")
    else:
        if len(metadata_issues) == 1:
            print(f"\nWARNING: {metadata_issues[0]}")
        else:
            print("\nWARNING: multiple issues found with metadata files")
            for issue in metadata_issues:
                print(f"\t{issue}")

    config_issues = c.validate_config()
    if config_issues:
        print(f"\nWARNING: Found {len(config_issues)} issues in config file:")
        for issue in config_issues:
            print(f"\t{issue}")
    else:
        print("\nNo issues are present in config file")


if __name__ == "__main__":
    args = parse_args()
    config = Configuration(args.config)
    do_validate(config)
