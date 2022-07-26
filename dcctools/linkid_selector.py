import argparse
import json
from pathlib import Path
import random
import time

import pandas as pd
from config import Configuration
from pymongo import MongoClient

c = Configuration("config.json")
link_id_csv_path = Path(c.matching_results_folder) / "link_ids.csv"
link_ids = pd.read_csv(link_id_csv_path, dtype=str, index_col=0)

parser = argparse.ArgumentParser(
    description="Script for selecting LINK IDs for further review"
)
parser.add_argument(
    "site_data_folder",
    help="Path to the folder containing exported site data",
)
parser.add_argument(
    "sites",
    nargs=2,  # TODO: consider nargs='+' to allow for arbitrarily many
    help="Sites to produce a report of LINK IDs matching certain criteria for",
)

args = parser.parse_args()

test_data = link_ids[args.sites].dropna()
print(f"Link IDs common to all {len(args.sites)} sites: {len(test_data)}")

if len(test_data) == 0:
    exit()

site_data = {}
site_data_folder = Path(args.site_data_folder)

for site in args.sites:
    curr_data = pd.read_csv(
        site_data_folder / f"concord_{site}.csv",
        dtype=str,
        # the file has many columns, we only care about a few:
        usecols=["linkid", "birth_date", "sex"],
    )
    # concordance data comes from a use case query,
    # which may contain data from multiple years.
    # birth_date and sex come from DEMOGRAPHIC table
    # which only has one row per individual total, not per year
    # so we can drop duplicates on (linkid, birth_date, sex)
    curr_data = curr_data.drop_duplicates()

    # trying to get sex values to line up.
    # prior results showed 0% concordance so we suspect maybe trailing spaces?
    curr_data["sex"] = curr_data["sex"].apply(
        lambda x: x.strip() if isinstance(x, str) else x
    )

    # the index isn't considered in the dup check,
    # so linkid gets set as index afterward
    # (there may be ways to optimize this)
    curr_data = curr_data.set_index("linkid")
    curr_data = curr_data.add_suffix(f"_{site}")
    site_data[site] = curr_data

    test_data = test_data.merge(site_data[site], left_index=True, right_index=True)

for field in ["birth_date", "sex"]:
    data_to_compare = test_data.filter(regex=f"{field}*", axis="columns")

    # count the number of unique values per row
    concordance = data_to_compare.nunique(axis="columns")

    test_data[f"concordance_{field}"] = concordance == 1

cbd_key = "concordance_birth_date"
cs_key = "concordance_sex"


# 1. Demographic Analysis
# 1a both concordant
# 1b both discordant
# 1c sex concordant only
# 1d dob concordant only
test_data = test_data.assign(
    both_concordant=lambda row: row[cbd_key] & row[cs_key],
    both_discordant=lambda row: (~row[cbd_key]) & (~row[cs_key]),
    sex_concord_only=lambda row: (~row[cbd_key]) & row[cs_key],
    dob_concord_only=lambda row: row[cbd_key] & (~row[cs_key]),
)

print("Done loading demographic analysis")

# 2. Exact Match Analysis
# For exact matches, I think we need to figure out exact matches by line number

# TODO: there are 3 projects - how do we choose? for now just do addr
for site in args.sites:
    raw_clks = c.get_clks_raw(site, "name-sex-dob-addr")
    clk_json = json.loads(raw_clks)
    site_clks = clk_json["clks"]
    clks_as_dict = {str(k): v for k, v in enumerate(site_clks)}
    test_data[f"clk_{site}"] = test_data[site].map(clks_as_dict)


# now it's basically just a concordance test again
data_to_compare = test_data.filter(regex=f"clk_*", axis="columns")

# count the number of unique values per row
concordance = data_to_compare.nunique(axis="columns")

test_data[f"exact_match"] = concordance == 1

print("Done loading exact match analysis")


# 3. Match Group Analysis
# this part comes from backtrace.py
# this approach is likely much slower than a mongo aggregation
# but easier to understand what it does

client = MongoClient(c.mongo_uri)
database = client.linkage_agent


def find_match_group(row):
    query = {}
    for site in args.sites:
        query[site] = int(row[site])

    for result in database.match_groups.find(query):
        return result


def match_group_category(row):
    match_group = find_match_group(row)
    num_run_results = len(match_group["run_results"])

    if num_run_results >= 4:
        return "4+ match groups"
    elif num_run_results == 3:
        return "3 match groups"
    elif num_run_results == 2:
        proj0 = match_group["run_results"][0]["project"][13:]
        proj1 = match_group["run_results"][1]["project"][13:]
        # note the [13:] trims off the first 13 chars "name-sex-dob-"

        if proj0 > proj1:
            proj0, proj1 = proj1, proj0
            # swap them if they are not in alpha order
            # this means we only have 3 possibilities instead of 6
        return f"{proj0}+{proj1}"
    else:
        # the only possibility is == 1
        proj = match_group["run_results"][0]["project"]
        return proj


test_data["match_group_category"] = test_data.apply(
    match_group_category, axis="columns"
)

test_data = test_data.assign(
    one_match_group_Address_only=lambda df: df["match_group_category"] == "addr",
    one_match_group_Phone_only=lambda df: df["match_group_category"] == "phone",
    one_match_group_Zip_only=lambda df: df["match_group_category"] == "zip",
    two_match_groups_Address_Phone=lambda df: df["match_group_category"] == "addr+phone",
    two_match_groups_Address_Zip=lambda df: df["match_group_category"] == "addr+zip",
    two_match_groups_Zip_Phone=lambda df: df["match_group_category"] == "phone+zip",
    three_match_groups=lambda df: df["match_group_category"] == "3 match groups",
    four_match_groups=lambda df: df["match_group_category"] == "4+ match groups",
)

# 3a 1 match group
# 3ai Phone only
# 3aii Address only
# 3aiii Zip only

# 3b 2 match groups
# 3bi Phone-Zip only
# 3bii Address-Phone only
# 3bii Address-Zip only

# 3c 3 match groups

# 3d 4+ match groups

print("Done loading match group analysis")


target_counts = {
    "both_concordant": 75,
    "both_discordant": 75,
    "sex_concord_only": 75,
    "dob_concord_only": 75,
    "exact_match": 50,
    "one_match_group_Address_only": 75,
    "one_match_group_Phone_only": 75,
    "one_match_group_Zip_only": 75,
    "two_match_groups_Address_Phone": 75,
    "two_match_groups_Address_Zip": 75,
    "two_match_groups_Zip_Phone": 75,
    "three_match_groups": 75,
    "four_match_groups": "*",
}

selected_ids = set()
for label in target_counts.keys():
    # note these columns should be booleans, so
    # test_data[test_data[label]] gets us just the trues
    # then .index gets us the linkids
    all_ids_for_label = set(test_data[test_data[label]].index)

    print(f"{label}: {len(all_ids_for_label)} Total IDs Available")

    selectable_ids = all_ids_for_label - selected_ids

    print(f"{label}: {len(selectable_ids)} Selectable IDs Available (not already selected in previous steps)")

    count = target_counts[label]

    if count == "*":
        selection_for_label = list(selectable_ids)
    else:
        selection_for_label = random.sample(
            list(selectable_ids), min(count, len(selectable_ids))
        )

    print(f"{label}: {len(selection_for_label)} selected")

    selected_ids.update(selection_for_label)

    print(f"Running total {len(selected_ids)} selected")

# now filter to just the categories columns for output
all_output = test_data[target_counts.keys()]

# and filter to just the selected IDs
selected_ids_output = all_output[all_output.index.isin(selected_ids)]

timestamp = int(time.time())

all_output_file = f"all_output_{timestamp}.csv"
with open(all_output_file, "w", newline="") as output:
    all_output.to_csv(output)
    print(f"Wrote {all_output_file}")

selected_ids_output_file = f"selected_ids_output_{timestamp}.csv"
with open(selected_ids_output_file, "w", newline="") as output:
    selected_ids_output.to_csv(output)
    print(f"Wrote {selected_ids_output_file}")
