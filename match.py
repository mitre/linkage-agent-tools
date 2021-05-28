import time
from dcctools.config import Configuration
from pymongo import MongoClient
from dcctools.anonlink import Results, Project
from pathlib import Path

c = Configuration("config.json")
client = MongoClient(c.mongo_uri())
database = client.linkage_agent

if c.household_match():
  with open(Path(c.household_schema())) as schema_file:
    household_schema = schema_file.read()
    project_name = 'fn-phone-addr-zip'
    household_project = Project(project_name, household_schema, c.systems(), c.entity_service_url(), c.blocked())
    household_project.start_project()
    for system in c.systems():
      household_project.upload_clks(system, c.get_household_clks_raw(system, project_name))
    household_project.start_run(c.matching_threshold())
    running = True
    while running:
      status = household_project.get_run_status()
      print(status)
      if status.get('state') == 'completed':
        running = False
      time.sleep(0.5)
    result_json = household_project.get_results()
    results = Results(c.systems(), project_name, result_json)
    print(result_json)
    results.insert_results(database.household_match_groups)

if c.blocked():
  for system in c.systems():
    c.extract_clks(system)
    c.extract_blocks(system)
for project_name, schema in c.load_schema().items():
  project = Project(project_name, schema, c.systems(), c.entity_service_url(), c.blocked())
  project.start_project()
  for system in c.systems():
    if c.blocked():
      project.upload_clks_blocked(system, c.get_clk(system, project_name), c.get_block(system, project_name))
    else:
      project.upload_clks(system, c.get_clks_raw(system, project_name))
  project.start_run(c.matching_threshold())
  running = True
  while running:
    status = project.get_run_status()
    print(status)
    if status.get('state') == 'completed':
      running = False
    time.sleep(0.5)
  result_json = project.get_results()
  results = Results(c.systems(), project_name, result_json)
  print(result_json)
  results.insert_results(database.match_groups)
