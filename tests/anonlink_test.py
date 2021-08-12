import os

from pymongo import MongoClient
import pytest

from dcctools.anonlink import Results


def test_insert_results():
    systems = ["a", "b", "c"]
    project = "name-dob"
    anonlink_results = {
        "groups": [[[0, 1], [1, 2], [2, 3]], [[1, 5], [2, 6]], [[0, 8], [2, 9]]]
    }

    client = MongoClient(port=27017)
    database = client.test

    if "match_results" in database.list_collection_names():
        database.drop_collection("match_results")

    collection = database.match_results
    r = Results(systems, project, anonlink_results)
    r.insert_results(collection)

    assert collection.count_documents({}) == 3

    doc = collection.find_one({"a": 1})
    assert doc["b"] == [2]
    assert doc["c"] == [3]

    doc = collection.find_one({"b": 5})
    assert doc["c"] == [6]

    doc = collection.find_one({"a": 8})
    assert doc["c"] == [9]


def test_insert_conflicting_results_split_group():
    systems = ["a", "b"]
    project1 = "name-dob"
    anonlink_results1 = {"groups": [[[0, 1], [1, 2]], [[0, 8], [1, 9]]]}

    client = MongoClient(port=27017)
    database = client.test

    if "match_results" in database.list_collection_names():
        database.drop_collection("match_results")

    collection = database.match_results

    r = Results(systems, project1, anonlink_results1)
    r.insert_results(collection)

    assert collection.count_documents({}) == 2

    doc = collection.find_one({"a": 1})
    assert doc["b"] == [2]

    doc = collection.find_one({"b": 9})
    assert doc["a"] == [8]

    project2 = "name-sex"
    anonlink_results2 = {"groups": [[[0, 1], [1, 9]], [[0, 20], [1, 30]]]}

    r = Results(systems, project2, anonlink_results2)
    r.insert_results(collection)

    assert collection.count_documents({}) == 2

    doc = collection.find_one({"a": 1})
    assert doc["b"] == [2, 9]


def test_insert_conflicting_results_same_group():
    systems = ["a", "b"]
    project1 = "name-dob"
    anonlink_results1 = {"groups": [[[0, 1], [1, 2]], [[0, 8], [1, 9]]]}

    client = MongoClient(port=27017)
    database = client.test

    if "match_results" in database.list_collection_names():
        database.drop_collection("match_results")

    collection = database.match_results
    r = Results(systems, project1, anonlink_results1)
    r.insert_results(collection)

    assert collection.count_documents({}) == 2

    doc = collection.find_one({"a": 1})
    assert doc["b"] == [2]

    doc = collection.find_one({"b": 9})
    assert doc["a"] == [8]

    project2 = "name-sex"
    anonlink_results2 = {"groups": [[[0, 1], [1, 10]], [[0, 20], [1, 30]]]}

    r = Results(systems, project2, anonlink_results2)
    r.insert_results(collection)

    assert collection.count_documents({}) == 3

    doc = collection.find_one({"a": 1})
    assert doc["b"] == [2, 10]
    assert len(doc["run_results"]) == 2
