import csv
from pathlib import Path
from dcctools.config import Configuration
from itertools import combinations

c = Configuration("config.json")
systems = c.systems()

true_positives = 0
false_positives = 0
perfect_true_positives = 0
perfect_false_positives = 0
partial_true_positives = 0
partial_false_positives = 0
# true_pairs = []
# false_pairs = []
household_pair_count = 0 # do this dynamically
household_answer_count = 0
# with open('/Users/apellitieri/Downloads/allrecords.csv') as all_csv:
# ...   count_list = []
# ...   hid_reader = csv.reader(all_csv)
# ...   next(hid_reader)
# ...   for row in hid_reader:
# ...     count_list.append(row[2])
# ...   unique = list(set(count_list))
# ...   print(len(unique))
# hid_csv_path = Path('/Users/apellitieri/Desktop/CDC/CODI/data-owner-tools') / 'full_answer_key.csv'
hid_csv_path = Path('/Users/apellitieri/Desktop/CDC/CODI/results') / "household_id_link_ids.csv"
answer_key_path = Path('/Users/apellitieri/Desktop/CDC/CODI/data-owner-tools') / 'full_answer_key.csv'

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
      all_hids.append(hids_filtered[0]) # remove
      # partial_true_positives += 1
    elif len(hids_filtered) == 1 and hids in answer_key_rows:
      all_hids.append(hids_filtered[0]) # remove
      # partial_true_positives += 1
    elif len(hids_filtered) > 1:
      partial_false_positives += 1

    combos = combinations(hids_filtered, 2)
    for a, b in combos:
      if a == b:
        # true_pairs.append([demographics[a], demographics[b]])
        true_positives += 1
      else:
        # false_pairs.append([demographics[a], demographics[b]])
        false_positives += 1
#remove:
partial_true_positives = len(list(set(all_hids)))
# real_dupe = 0
# for hids in all_hids:
#   dupe_count = 0
#   for hids2 in all_hids:
#     if hids[0] == hids2[0]:
#       dupe_count+=1
#   if dupe_count > 1:
#     print(dupe_count)
#     real_dupe += 1
# print(real_dupe)

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
