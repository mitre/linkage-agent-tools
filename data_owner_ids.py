import csv
from pathlib import Path

from dcctools.config import Configuration

c = Configuration("config.json")
result_csv_path = Path(c.matching_results_folder) / "link_ids.csv"
household_csv_path = Path(c.matching_results_folder) / "household_link_ids.csv"
systems = c.systems

for s in systems:
    system_csv_path = Path(c.output_folder / "{}.csv".format(s))
    household_system_csv_path = Path(c.output_folder) / "{}_households.csv".format(s)
    with open(result_csv_path) as csvfile:
        reader = csv.DictReader(csvfile)
        with open(system_csv_path, "w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["LINK_ID", s])
            writer.writeheader()
            for row in reader:
                if len(row[s]) > 0:
                    writer.writerow({"LINK_ID": row["LINK_ID"], s: row[s]})
    print(f"{system_csv_path} created")
    if c.household_match:
        with open(household_csv_path) as csvfile:
            reader = csv.DictReader(csvfile)
            with open(household_system_csv_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["LINK_ID", s])
                writer.writeheader()
                for row in reader:
                    if len(row[s]) > 0:
                        writer.writerow({"LINK_ID": row["LINK_ID"], s: row[s]})
        print(f"{household_system_csv_path} created")
