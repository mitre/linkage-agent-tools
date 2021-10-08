from pymongo import MongoClient
import validate as val
import match as m
import link_ids as li

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

