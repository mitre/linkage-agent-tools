import json
import os
from pathlib import Path
from zipfile import ZipFile

class Configuration:
  def __init__(self, filename):
    self.filename = filename
    with open(filename) as f:
      self.config_json = json.load(f)

  def system_count(self):
    return len(self.config_json['systems'])

  def validate_all_present(self):
    root_path = Path(self.filename).parent
    inbox_folder = root_path / self.config_json['inbox_folder']
    for s in self.config_json['systems']:
      system_zip_path = inbox_folder / "{}.zip".format(s)
      if not os.path.exists(system_zip_path):
        return False
    return True

  def systems(self):
    return self.config_json['systems']

  def load_schema(self):
    all_schema = {}
    for p in self.config_json['projects']:
      schema_path = Path(self.config_json['schema_folder']) / "{}.json".format(p)
      with open(schema_path) as schema_file:
        all_schema[p] = schema_file.read()
    return all_schema

  def entity_service_url(self):
    return self.config_json['entity_service_url']

  def extract_clks(self, system):
    clk_zip_path = Path(self.config_json['inbox_folder']) / "{}.zip".format(system)
    extract_path = Path(self.config_json['inbox_folder']) / system
    if not os.path.exists(extract_path):
        os.mkdir(extract_path)
    with ZipFile(clk_zip_path, mode='r') as clk_zip:
      clk_zip.extractall(Path(self.config_json['inbox_folder']) / system)

  def extract_blocks(self, system):
    block_zip_path = Path(self.config_json['inbox_folder']) / "{}-block.zip".format(system)
    extract_path = Path(self.config_json['inbox_folder']) / system
    if not os.path.exists(extract_path):
        os.mkdir(extract_path)
    with ZipFile(block_zip_path, mode='r') as block_zip:
      block_zip.extractall(Path(self.config_json['inbox_folder']) / system)

  def get_clk(self, system, project):
    clk_path = Path(self.config_json['inbox_folder']) / system / "output/{}.json".format(project)
    return clk_path

  def get_clks_raw(self, system, project):
    clks = None
    clk_zip_path = Path(self.config_json['inbox_folder']) / "{}.zip".format(system)
    with ZipFile(clk_zip_path, mode='r') as clk_zip:
      with clk_zip.open("output/{}.json".format(project)) as clk_file:
        clks = clk_file.read()
    return clks

  def get_block(self, system, project):
    block_path = Path(self.config_json['inbox_folder']) / system / "blocking-output/{}.json".format(project)
    return block_path

  def matching_threshold(self):
    return self.config_json['matching_threshold']

  def output_folder(self):
    return self.config_json['output_folder']

  def matching_results_folder(self):
    return self.config_json['matching_results_folder']

  def inbox_folder(self):
    return self.config_json['inbox_folder']

  def projects(self):
    return self.config_json['projects']

  def mongo_uri(self):
    return self.config_json['mongo_uri']

  def blocked(self):
    return self.config_json['blocked']

  def blocking_schema(self):
    return self.config_json['blocking_schema']
