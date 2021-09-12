import csv
from pathlib import Path
from dcctools.config import Configuration
from itertools import combinations
import argparse

parser = argparse.ArgumentParser(description='Tool for scoring individual linkage results')
parser.add_argument('--answerkey', nargs=1, required=True, help='Path to answer key file')
args = parser.parse_args()

answer_key_file = Path(args.answerkey[0])
​
c = Configuration("config.json")
systems = c.systems
​
true_positives = 0
false_positives = 0
​
answer_key = []
​
with open(answer_key_file) as ak_csv:
  ak_reader = csv.reader(ak_csv)
  next(ak_reader)
  for row in ak_reader:
    if row[3] == '1':
      answer_pair = [row[1], row[2]]
      answer_pair.sort()
      answer_key.append(answer_pair)
​
answer_key_length = len(answer_key)
​
patid_csv_path = Path(c.matching_results_folder) / "patid_link_ids.csv"
​
with open(patid_csv_path) as patid_csv:
  pat_id_reader = csv.reader(patid_csv)
  next(pat_id_reader)
  for row in pat_id_reader:
    patids = row[1:6]
    patids = list(filter(lambda id: len(id) > 0, patids))
    combos = combinations(patids, 2)
    for a, b in combos:
      pair = [a, b]
      pair.sort()
      if pair in answer_key:
        true_positives += 1
      else:
        false_positives += 1
​
precision = true_positives / (true_positives + false_positives)
recall = true_positives / answer_key_length
fscore = 2 * ((precision * recall) / (precision + recall))
​
​
print("Precision: {} Recall: {} F-Score: {}".format(precision, recall, fscore))
print("Answer Key Size: {}".format(answer_key_length))
print("Proposed pairs: {}".format(true_positives + false_positives))
