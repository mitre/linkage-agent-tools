import argparse
from itertools import combinations
import pandas as pd
from pathlib import Path

from config import Configuration

c = Configuration("config.json")
link_id_csv_path = Path(c.matching_results_folder) / "link_ids.csv"
link_ids = pd.read_csv(link_id_csv_path, dtype=str, index_col=0)

parser = argparse.ArgumentParser(
    description="Script for performing concordance analysis across site data"
)
parser.add_argument(
    "system_data_folder",
    help="Path to the folder containing exported system data",
)
args = parser.parse_args()

systems = c.systems
system_data = {}
system_data_folder = Path(args.system_data_folder)

for site in systems:
    system_data[site] = pd.read_csv(system_data_folder / f"concord_{site}.csv", dtype=str, index_col=0).add_suffix(f"_{site}")

for n in range(2, len(systems) + 1):
    print(f"{n}-wise concordance")
    for test_systems in combinations(systems, n):
        print(test_systems)
        # get the columns(systems) of interest, and drop rows containing any NA

        test_data = link_ids[list(test_systems)].dropna()

        print(f"Link IDs common to all {n} systems: {len(test_data)}")

        if len(test_data) == 0:
            continue

        for s in test_systems:
            test_data = test_data.merge(system_data[s], left_index=True, right_index=True)

        # index (link_id) no longer useful past this point
        test_data = test_data.reset_index()

        for field in ['birth_date', 'sex']:
            test_cols = [col for col in test_data.columns if col.startswith(field)]

            data_to_compare = test_data[test_cols]

            # count the number of unique values per row
            concordance = data_to_compare.nunique(axis=1).value_counts().to_dict()
            # a count of 1 means all columns had the same value == concordance
            # the range of possible values is 1..n
            # for this analysis there is no difference between 2, 3, ..., n

            concordance_pct = 0
            if 1 in concordance:
                concordance_pct = concordance[1] / len(data_to_compare)

            print(f"{field}: {concordance} --> {concordance_pct * 100.0}%")

        print()

    print()
    print()


