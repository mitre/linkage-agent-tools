import csv
from pathlib import Path
from dcctools.config import Configuration
from itertools import combinations
import argparse

parser = argparse.ArgumentParser(description='Tool for scoring household linkage results')
parser.add_argument('--dotools', nargs=1, required=True, help='data-owner-tools project path')
args = parser.parse_args()

data_owner_tools_path = Path(args.dotools[0])

c = Configuration("config.json")
systems = c.systems()

true_positives = 0
false_positives = 0
perfect_true_positives = 0
perfect_false_positives = 0
partial_true_positives = 0
partial_false_positives = 0
household_pair_count = 0
household_answer_count = 0

hid_csv_path = Path(c.matching_results_folder()) / "household_id_link_ids.csv"
answer_key_path = Path(data_owner_tools_path) / 'full_answer_key.csv'

answer_key_rows = []
with open(answer_key_path) as key_csv:
  key_reader = csv.reader(key_csv)
  next(key_reader)
  for row in key_reader:
    household_answer_count += 1
    answer_key_rows.append(row)
    hids = list(filter(lambda id: len(id) > 0, row))
    combos = combinations(hids, 2)
    for a, b in combos:
      household_pair_count += 1
# Decide if we want to use all_hids with the list(set()) deduping or the partial count+=
all_hids = [] # remove
with open(hid_csv_path) as hid_csv:
  hid_reader = csv.reader(hid_csv)
  next(hid_reader)
  for row in hid_reader:
    hids = row[1:(len(systems)+1)]
    hids_filtered = list(filter(lambda id: len(id) > 0, hids))
    if hids in answer_key_rows:
      perfect_true_positives += 1
    elif len(hids_filtered) > 1:
      # Review if this makes sense or we need additional filter
      perfect_false_positives += 1

    combos = combinations(hids_filtered, 2)
    if len(hids_filtered) > 1 and all(a == b for (a,b) in combos):
      all_hids.append(hids_filtered[0])
      # partial_true_positives += 1
    elif len(hids_filtered) == 1 and hids in answer_key_rows:
      all_hids.append(hids_filtered[0])
      # partial_true_positives += 1
    elif len(hids_filtered) > 1:
      partial_false_positives += 1

    combos = combinations(hids_filtered, 2)
    for a, b in combos:
      if a == b:
        true_positives += 1
      else:
        false_positives += 1

partial_true_positives = len(list(set(all_hids)))

precision = true_positives / (true_positives + false_positives)
recall = true_positives / household_pair_count
fscore = 2 * ((precision * recall) / (precision + recall))
print("Pair-wise scoring:\nPrecision: {} Recall: {} F-Score: {}".format(precision, recall, fscore))

precision = perfect_true_positives / (perfect_true_positives + perfect_false_positives)
recall = perfect_true_positives / household_answer_count
fscore = 2 * ((precision * recall) / (precision + recall))
print("Perfect scoring:\nPrecision: {} Recall: {} F-Score: {}".format(precision, recall, fscore))

precision = partial_true_positives / (partial_true_positives + partial_false_positives)
recall = partial_true_positives / household_answer_count
fscore = 2 * ((precision * recall) / (precision + recall))
print("Partial scoring:\nPrecision: {} Recall: {} F-Score: {}".format(precision, recall, fscore))
