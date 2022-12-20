import argparse
import itertools
import json

from config import Configuration

parser = argparse.ArgumentParser(
    description="Tool for counting the number of exact matches (exactly identical hashes) \
                 for one project across sites."
)
group = parser.add_mutually_exclusive_group()
group.add_argument(
    "-p",
    "--project",
    default="name-sex-dob-zip",
    help="Select a project to review exact matches across sites. \
          Default: name-sex-dob-zip \
          Does not work with the household flag",
)
group.add_argument(
    "--household",
    help="Review exact household matches. \
          Does not work with the project flag",
)
args = parser.parse_args()

# note the path has to be relative to the directory
# that the script was invoked from
# python3 dcctools/exact_matches.py --> use path "./config.json"
c = Configuration("config.json")

project = None
if args.household is not None:
    project = args.household
    print(f"COUNTING EXACT MATCHES FOR households {project}")
else:
    project = args.project
    print(f"COUNTING EXACT MATCHES FOR {project}")

clks = {}
for system in c.systems:
    raw_clks = None
    if args.household is not None:
        raw_clks = c.get_household_clks_raw(system, project)
    else:
        raw_clks = c.get_clks_raw(system, project)
    clk_json = json.loads(raw_clks)
    clks[system] = set(clk_json["clks"])
    print(f"Size of {system}: {len(clks[system])}")

total_exact_matches = set()

for pair in itertools.combinations(c.systems, 2):
    pairwise_matches = clks[pair[0]].intersection(clks[pair[1]])
    print(
        f"Total exact matches between {pair[0]} and {pair[1]}: {len(pairwise_matches)}"
    )

    total_exact_matches.update(pairwise_matches)  # update means add to set

print()
print(f"Total exact matches for {project}: {len(total_exact_matches)}")
