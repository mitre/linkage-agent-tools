import pytest
import os
from tinydb import TinyDB, Query
from dcctools.anonlink import Results

def test_insert_results():
  db_location = 'tests/test_db.json'
  systems = ['a', 'b', 'c']
  project = 'name-dob'
  anonlink_results = {'groups': [[[0, 1], [1, 2], [2, 3]],
    [[1, 5], [2, 6]],
    [[0, 8], [2, 9]]]}

  if os.path.exists(db_location):
    os.remove(db_location)

  database = TinyDB(db_location)

  r = Results(systems, project, anonlink_results)
  r.insert_results(database)

  assert len(database) == 3

  RecordGroup = Query()

  doc = database.search(RecordGroup['a'].any([1]))
  assert doc[0]['b'] == [2]
  assert doc[0]['c'] == [3]

  doc = database.search(RecordGroup['b'].any([5]))
  assert doc[0]['c'] == [6]

  doc = database.search(RecordGroup['a'].any([8]))
  assert doc[0]['c'] == [9]