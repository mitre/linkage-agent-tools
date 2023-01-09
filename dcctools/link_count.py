import datetime
from itertools import combinations
from pathlib import Path

import pandas as pd
from config import Configuration

from definitions import TIMESTAMP_FMT


c = Configuration("config.json")

if c.household_match:
    link_ids = sorted(
        Path(c.matching_results_folder).glob("household_link_ids*.csv")
    )
else:
    link_ids = sorted(Path(c.matching_results_folder).glob("link_ids*.csv"))

if len(link_ids) > 1:
    ts_len = len(datetime.now().strftime(TIMESTAMP_FMT))
    # -4 since ".csv" is 4 chars
    ts_loc = (-(4 + ts_len), -4)
    link_id_times = [
        datetime.strptime(x.name[ts_loc[0] : ts_loc[1]], TIMESTAMP_FMT)
        for x in link_ids
    ]
    most_recent = link_ids[link_id_times.index(max(link_id_times))]
    print(f"Using most recent link_id file: {most_recent}")

    link_id_path = most_recent
else:
    link_id_path = link_ids[0]

link_ids = pd.read_csv(link_id_path, dtype=str, index_col=0)

systems = c.systems
system_data = {}

for n in range(2, len(systems) + 1):
    print(f"=== {n}-wise links ===")
    for test_systems in combinations(systems, n):
        # get the columns(systems) of interest, and drop rows containing any NA
        test_data = link_ids[list(test_systems)].dropna()
        print(f"{test_systems}: {len(test_data)} Link IDs")

    print()
