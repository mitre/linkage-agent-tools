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

def test_insert_conflicting_results_split_group():
  db_location = 'tests/test_db.json'
  systems = ['a', 'b']
  project1 = 'name-dob'
  anonlink_results1 = {'groups': [[[0, 1], [1, 2]],
    [[0, 8], [1, 9]]]}

  if os.path.exists(db_location):
    os.remove(db_location)

  database = TinyDB(db_location)

  r = Results(systems, project1, anonlink_results1)
  r.insert_results(database)

  assert len(database) == 2

  RecordGroup = Query()

  doc = database.search(RecordGroup['a'].any([1]))
  assert doc[0]['b'] == [2]

  doc = database.search(RecordGroup['b'].any([9]))
  assert doc[0]['a'] == [8]

  project2 = 'name-sex'
  anonlink_results2 = {'groups': [[[0, 1], [1, 9]],
    [[0, 20], [1, 30]]]}

  r = Results(systems, project2, anonlink_results2)
  r.insert_results(database)

  assert len(database) == 2

  doc = database.search(RecordGroup['a'].any([1]))
  assert doc[0]['b'] == [2, 9]

def test_insert_conflicting_results_same_group():
  db_location = 'tests/test_db.json'
  systems = ['a', 'b']
  project1 = 'name-dob'
  anonlink_results1 = {'groups': [[[0, 1], [1, 2]],
    [[0, 8], [1, 9]]]}

  if os.path.exists(db_location):
    os.remove(db_location)

  database = TinyDB(db_location)

  r = Results(systems, project1, anonlink_results1)
  r.insert_results(database)

  assert len(database) == 2

  RecordGroup = Query()

  doc = database.search(RecordGroup['a'].any([1]))
  assert doc[0]['b'] == [2]

  doc = database.search(RecordGroup['b'].any([9]))
  assert doc[0]['a'] == [8]

  project2 = 'name-sex'
  anonlink_results2 = {'groups': [[[0, 1], [1, 10]],
    [[0, 20], [1, 30]]]}

  r = Results(systems, project2, anonlink_results2)
  r.insert_results(database)

  assert len(database) == 3

  doc = database.search(RecordGroup['a'].any([1]))
  assert doc[0]['b'] == [2, 10]
  assert len(doc[0]['run_results']) == 2