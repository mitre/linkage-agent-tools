import json

import util.file.file_util as fu
import util.json.json_util as ju
from dcctools.config import Configuration


def get_config_json_obj_from_abs_path(file_name):
    print("Getting config from:")
    print(file_name)
    with open(file_name) as file:
        config = json.load(file)
    return config


def get_config_json_obj(file_name):
    file_name = fu.get_file_name(file_name)
    print("Getting config from:")
    print(file_name)
    with open(file_name) as file:
        config = json.load(file)
    config["schema_folder"] = fu.get_file_name(config["schema_folder"])
    config["inbox_folder"] = fu.get_file_name(config["inbox_folder"])
    config["matching_results_folder"] = fu.get_file_name(
        config["matching_results_folder"]
    )
    config["output_folder"] = fu.get_file_name(config["output_folder"])
    config["blocking_schema"] = fu.get_file_name(config["blocking_schema"])
    config["household_schema"] = fu.get_file_name(config["household_schema"])
    return config


def get_config(file_name):
    json_obj = get_config_json_obj(file_name)
    config = Configuration(None)
    config.init(json_obj)
    return config


def get_config_from_abs_path(file_name):
    json_obj = get_config_json_obj_from_abs_path(file_name)
    config = Configuration(None)
    config.init(json_obj)
    return config


def get_config_from_string(json_string):
    json_obj = json.loads(json_string)
    config = Configuration(None)
    config.init(json_obj)
    return config


def get_json_pretty_printed(config):
    return ju.pretty_print(config.config_json)
