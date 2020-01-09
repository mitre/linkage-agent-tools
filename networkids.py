from pymongo import MongoClient
from dcctools.deconflict import deconflict
from functools import reduce
import uuid

systems = ['a', 'b', 'c']

client = MongoClient()
db = client['codi']
results_collection = db['results']
networkid_collection = db['networkids']

for r in results_collection.find():
  conflict = reduce(lambda acc, s: acc | len(r.get(s, [])) > 1, systems, False)
  final_record = {}
  if conflict:
    final_record = deconflict(r, systems)
  else:
    for s in systems:
      id = r.get(s, None)
      if id != None:
        final_record[s] = id[0]
  final_record['networkid'] = uuid.uuid1()
  networkid_collection.insert_one(final_record)
