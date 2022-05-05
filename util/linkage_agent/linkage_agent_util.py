from pymongo import MongoClient
import validate as val
import projects as p
import match as m
import link_ids as li
import data_owner_ids as doi


def validate(config):
    val.do_validate(config)


def drop(config):
    client = MongoClient(config.mongo_uri)
    database = client.linkage_agent
    database.match_groups.drop()
    database.household_match_groups.drop()
    print("Database cleared.")

def projects(config):
    p.run_projects(config)

def match(config):
    m.do_match(config)

def link_id(config):
    li.do_link_ids(config)


def data_owner_ids(config):
    doi.do_data_owner_ids(config)


def generate_link_ids(config):
    print("\nStarting Generate Link IDs...")
    print("Doing drop...")
    drop(config)
    print("Doing validation...")
    validate(config)
    print("Running projects...")
    projects(config)
    print("Doing match...")
    match(config)
    print("")
    print("--- * * *")
    print("---")
    print("--- Doing link_id...")
    print("---")
    print("--- * * *")
    print("")
    link_id(config)
    print("")
    print("--- * * *")
    print("---")
    print("--- Doing data_owner_ids...")
    print("---")
    print("--- * * *")
    print("")
    print("Doing data_owner_ids")
    data_owner_ids(config)
    print("Done.")
