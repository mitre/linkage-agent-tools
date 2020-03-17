import json
import os
from pathlib import Path

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
