import csv
from pymongo import MongoClient

systems = ['a', 'b', 'c']

client = MongoClient()
db = client['codi']
networkid_collection = db['networkids']

with open('network_ids.csv', 'w', newline='') as csvfile:
  writer = csv.writer(csvfile)
  header = ['network_id']
  header.extend(systems)
  writer.writerow(header)
  for nid in networkid_collection.find():
    row = []
    row.append(nid['networkid'])
    for s in systems:
      row.append(nid.get(s, ''))
    writer.writerow(row)
