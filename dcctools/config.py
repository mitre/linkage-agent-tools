import csv
import json
import os
from pathlib import Path
import sys
from zipfile import ZipFile


class Configuration:
    def __init__(self, filename):
        if filename is not None:
            self.filename = filename
            self.config_json = json.load(open(filename))

    def init(self, json_obj):
        self.config_json = json_obj
        self.filename = ""

    @property
    def system_count(self):
        return len(self.config_json["systems"])

    def validate_all_present(self):
        missing_paths = []
        root_path = Path(self.filename).parent
        inbox_folder = root_path / self.config_json["inbox_folder"]
        for s in self.config_json["systems"]:
            system_zip_path = inbox_folder / "{}.zip".format(s)
            if not os.path.exists(system_zip_path):
                missing_paths.append(system_zip_path)
            if self.config_json["household_match"]:
                household_zip_path = inbox_folder / "{}_households.zip".format(s)
                if not os.path.exists(household_zip_path):
                    missing_paths.append(household_zip_path)
            if self.config_json["blocked"]:
                system_zip_path = inbox_folder / "{}_block.zip".format(s)
                if not os.path.exists(system_zip_path):
                    missing_paths.append(system_zip_path)
        return missing_paths

    @property
    def systems(self):
        return self.config_json["systems"]

    def load_schema(self):
        all_schema = {}
        for p in self.config_json["projects"]:
            schema_path = Path(self.config_json["schema_folder"]) / "{}.json".format(p)
            with open(schema_path) as schema_file:
                all_schema[p] = schema_file.read()
        return all_schema

    @property
    def entity_service_url(self):
        return self.config_json["entity_service_url"]

    def extract_clks(self, system):
        clk_zip_path = Path(self.config_json["inbox_folder"]) / "{}.zip".format(system)
        extract_path = Path(self.config_json["inbox_folder"]) / system
        os.makedirs(extract_path, exist_ok=True)
        with ZipFile(clk_zip_path, mode="r") as clk_zip:
            clk_zip.extractall(Path(self.config_json["inbox_folder"]) / system)

    def extract_blocks(self, system):
        block_zip_path = Path(self.config_json["inbox_folder"]) / "{}_block.zip".format(
            system
        )
        extract_path = Path(self.config_json["inbox_folder"]) / system
        os.makedirs(extract_path, exist_ok=True)
        with ZipFile(block_zip_path, mode="r") as block_zip:
            block_zip.extractall(Path(self.config_json["inbox_folder"]) / system)

    def get_clk(self, system, project):
        clk_path = (
            Path(self.config_json["inbox_folder"])
            / system
            / "output/{}.json".format(project)
        )
        return clk_path

    def get_clks_raw(self, system, project):
        clks = None
        clk_zip_path = Path(self.config_json["inbox_folder"]) / "{}.zip".format(system)
        with ZipFile(clk_zip_path, mode="r") as clk_zip:
            with clk_zip.open("output/{}.json".format(project)) as clk_file:
                clks = clk_file.read()
        return clks

    def get_household_clks_raw(self, system, schema):
        clks = None
        clk_zip_path = Path(
            self.config_json["inbox_folder"]
        ) / "{}_households.zip".format(system)
        with ZipFile(clk_zip_path, mode="r") as clk_zip:
            with clk_zip.open("output/households/{}.json".format(schema)) as clk_file:
                clks = clk_file.read()
        return clks

    def get_block(self, system, project):
        block_path = (
            Path(self.config_json["inbox_folder"])
            / system
            / "blocking-output/{}.json".format(project)
        )
        return block_path

    def get_data_owner_household_links(self, system):
        house_mapping = {}
        clk_zip_path = Path(
            self.config_json["inbox_folder"]
        ) / "{}_households.zip".format(system)
        extract_path = Path(self.config_json["inbox_folder"]) / system
        os.makedirs(extract_path, exist_ok=True)
        with ZipFile(clk_zip_path, mode="r") as clk_zip:
            clk_zip.extractall(extract_path)
        with open(
            "{}/output/households/households.csv".format(extract_path), "r"
        ) as household_file:
            household_reader = csv.reader(household_file)
            next(household_reader)
            household_csv = list(household_reader)
            for line in household_csv:
                for individual_id in line[1].split(","):
                    try:
                        # Map the household pos to the list key = individual pos
                        house_mapping[individual_id] = int(line[0])
                    except:
                        e = sys.exc_info()[0]
                        print(e)
        return house_mapping

    @property
    def matching_threshold(self):
        return self.config_json["matching_threshold"]

    @property
    def output_folder(self):
        return self.config_json["output_folder"]

    @property
    def matching_results_folder(self):
        return self.config_json["matching_results_folder"]

    @property
    def inbox_folder(self):
        return self.config_json["inbox_folder"]

    @property
    def projects(self):
        return self.config_json["projects"]

    @property
    def mongo_uri(self):
        return self.config_json["mongo_uri"]

    @property
    def blocked(self):
        return self.config_json["blocked"]

    @property
    def blocking_schema(self):
        return self.config_json["blocking_schema"]

    @property
    def household_match(self):
        return self.config_json["household_match"]

    @property
    def household_schema(self):
        return self.config_json["household_schema"]
