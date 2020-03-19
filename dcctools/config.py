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

  def get_clks(self, system, project):
    clks = None
    clk_zip_path = Path(self.config_json['inbox_folder']) / "{}.zip".format(system)
    with ZipFile(clk_zip_path, mode='r') as clk_zip:
      with clk_zip.open("output/{}.json".format(project)) as clk_file:
        clks = clk_file.read()
    return clks

  def matching_threshold(self):
    return self.config_json['matching_threshold']

  def output_folder(self):
    return self.config_json['output_folder']