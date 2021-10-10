from pymongo import MongoClient
import validate as val
import match as m
import link_ids as li
import data_owner_ids as doi
import util.config.config_util as cu


def validate(config):
    val.do_validate(config)


def drop(config):
    client = MongoClient(config.mongo_uri)
    database = client.linkage_agent
    database.match_groups.drop()
    database.household_match_groups.drop()
    print("Database cleared.")


def match(config):
    m.do_match(config)


def link_id(config):
    li.do_link_ids(config)


def data_owner_ids(config):
    doi.do_data_owner_ids(config)


def generate_link_ids(config):
    print("\nStarting test...")
    config = cu.get_config("test/linkage-agent/no-household/config-no-households.json")
    print("Doing drop...")
    drop(config)
    print("Doing validation...")
    validate(config)
    print("Doing match...")
    match(config)
    print("Doing link_id...")
    link_id(config)
    print("Doing data_owner_ids")
    data_owner_ids(config)
    print("Doing drop...")
    drop(config)
    print("Done.")
