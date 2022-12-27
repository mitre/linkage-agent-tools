import csv
import json
import os
import sys
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from zipfile import ZipFile

from definitions import TIMESTAMP_FMT


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

    def validate_config(self):
        config_issues = []
        if (
            self.config_json["household_match"]
            and "household_threshold" not in self.config_json.keys()
        ):
            config_issues.append(
                "config file specifies household match without \
                        float household matching threshold"
            )
        elif type(self.config_json["matching_threshold"]) == list:
            proj_len = len(self.config_json["projects"])
            thresh_len = len(self.config_json["matching_threshold"])
            if proj_len != thresh_len:
                config_issues.append(
                    f"Number of projects ({proj_len}) and thresholds ({thresh_len}) \
                            is unequal \n\tThreshold must either be float or list of \
                            floats equal in length to the number of projects"
                )
        if "project_deconfliction_weights" in self.config_json:
            for proj in self.config_json["projects"]:
                conflict_weights = self.config_json["project_deconfliction_weights"]
                if proj not in conflict_weights:
                    config_issues.append(
                        f"Project {proj} is missing a deconfliction weighting"
                    )
                elif conflict_weights[proj] > 1.0:
                    config_issues.append(
                        f"Project {proj} has a deconfliction "
                        f"weight of {conflict_weights[proj]} "
                        f"which is greater than 1.0"
                    )
        return config_issues

    def validate_metadata(self, system_path):
        metadata_issues = []
        with zipfile.ZipFile(system_path) as archive:
            metadata_files = []
            for fname in archive.namelist():
                if "metadata" in fname:
                    metadata_files.append(fname)
                    anchor = fname.rfind("T")
                    mname = fname[(anchor - 8) : (anchor + 7)]
                    timestamp = datetime.strptime(mname, TIMESTAMP_FMT)
                    with archive.open(fname, "r") as metadata_fp:
                        metadata = json.load(metadata_fp)
                    garble_time = datetime.fromisoformat(metadata["creation_date"])
                    if (garble_time - timestamp) >= timedelta(seconds=1):
                        metadata_issues.append(
                            f"{system_path.name} metadata timecode {timestamp} does "
                            "not match listed garble time {garble_time}"
                        )
            if len(metadata_files) == 0:
                metadata_issues.append(
                    f"could not find metadata file within {system_path.name}"
                )
            elif len(metadata_files) > 1:
                metadata_issues.append(
                    f"Too many metadata files found in {system_path.name}:"
                    + "\n\t".join([metadata_file for metadata_file in metadata_files])
                )
        return metadata_issues

    def validate_all_present(self):
        missing_paths = []
        expected_paths = []
        unexpected_paths = []
        metadata_issues = []
        root_path = Path(self.filename).parent
        inbox_folder = root_path / self.config_json["inbox_folder"]
        for s in self.config_json["systems"]:
            system_zip_path = inbox_folder / "{}.zip".format(s)
            household_zip_path = inbox_folder / "{}_households.zip".format(s)
            if self.config_json["household_match"]:
                expected_paths.append(household_zip_path)
                if not os.path.exists(household_zip_path):
                    missing_paths.append(household_zip_path)
                else:
                    metadata_issues.extend(self.validate_metadata(household_zip_path))
                if os.path.exists(system_zip_path):
                    unexpected_paths.append(system_zip_path)
            else:
                expected_paths.append(system_zip_path)
                if not os.path.exists(system_zip_path):
                    missing_paths.append(system_zip_path)
                else:
                    metadata_issues.extend(self.validate_metadata(system_zip_path))
                if os.path.exists(household_zip_path):
                    unexpected_paths.append(household_zip_path)
            if self.config_json["blocked"]:
                system_zip_path = inbox_folder / "{}_block.zip".format(s)
                if not os.path.exists(system_zip_path):
                    missing_paths.append(system_zip_path)
        # Check for additional files in inbox that don't match these two patterns
        expected_paths_set = set(expected_paths)
        inbox_paths_present = set(
            [
                f
                for f in inbox_folder.glob("*")
                if f.is_file() and not f.name.startswith(".")
            ]
        )
        # If it's the same size or smaller, any issues meeting the above patterns
        # should already be accounted for, so check only for additional unexpected
        if len(inbox_paths_present) > len(expected_paths_set):
            for p in inbox_paths_present - expected_paths_set:
                unexpected_paths.append(p)

        for d in ["matching_results_folder", "output_folder"]:
            path_to_check = root_path / getattr(self, d)
            if not os.path.exists(path_to_check):
                missing_paths.append(path_to_check)
        return set(missing_paths), set(unexpected_paths), metadata_issues

    @property
    def systems(self):
        return self.config_json["systems"]

    def load_schema(self):
        all_schema = {}
        for p in self.config_json["projects"]:
            if not p.startswith("exact:"):
                schema_path = Path(self.config_json["schema_folder"]) / "{}.json".format(p)
                with open(schema_path) as schema_file:
                    all_schema[p] = schema_file.read()
            else:
                all_schema[p] = None
        return all_schema

    def load_household_schema(self):
        with open(Path(self.household_schema)) as schema_file:
            household_schema = schema_file.read()
        return household_schema

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

    def get_metadata(self, system):
        archive_name = (
            f"{system}_households.zip" if self.household_match else f"{system}.zip"
        )
        archive_path = Path(self.config_json["inbox_folder"]) / archive_name
        with ZipFile(archive_path, mode="r") as archive:
            for file_name in archive.namelist():
                if "metadata" in file_name:
                    with archive.open(file_name) as metadata_file:
                        return json.load(metadata_file)

    def get_clk(self, system, project):
        clk_path = (
            Path(self.config_json["inbox_folder"])
            / system
            / "output/{}.json".format(project)
        )
        return clk_path

    def get_clks_raw(self, system, project):
        clk_zip_path = Path(self.config_json["inbox_folder"]) / "{}.zip".format(system)
        with ZipFile(clk_zip_path, mode="r") as clk_zip:
            project_file = None
            for file_name in clk_zip.namelist():
                if f"{project}.json" in file_name:
                    project_file = file_name
                    break
            if project_file is not None:
                with clk_zip.open(project_file) as clk_file:
                    clks = clk_file.read()
            else:
                raise KeyError(
                    f"There is no item named '{project}.json' "
                    f"in the archive {system}.zip"
                )
        return clks

    def get_household_clks_raw(self, system, schema):
        clks = None
        clk_zip_path = Path(
            self.config_json["inbox_folder"]
        ) / "{}_households.zip".format(system)
        with ZipFile(clk_zip_path, mode="r") as clk_zip:
            for file_name in clk_zip.namelist():
                if f"{schema}.json" in file_name:
                    project_file = file_name
                    break
            with clk_zip.open(project_file) as clk_file:
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
                    except Exception:
                        e = sys.exc_info()[0]
                        print(e)
        return house_mapping

    def get_project_threshold(self, project_name):
        config_threshold = (
            self.household_threshold
            if self.household_match
            else self.matching_threshold
        )
        if type(config_threshold) == list:
            project_index = self.projects.index(project_name)
            threshold = config_threshold[project_index]
        else:
            threshold = config_threshold
        return threshold

    @property
    def matching_threshold(self):
        return self.config_json["matching_threshold"]

    @property
    def household_threshold(self):
        return self.config_json["household_threshold"]

    @property
    def output_folder(self):
        return self.config_json["output_folder"]

    @property
    def matching_results_folder(self):
        return self.config_json["matching_results_folder"]

    @property
    def project_deconfliction_weights(self):
        return self.config_json.get("project_deconfliction_weights", None)

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

    @property
    def project_results_dir(self):
        return self.config_json["project_results_folder"]
