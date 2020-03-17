import itertools as it
import requests
from tinydb import Query
from tinydb.operations import set, add

class Project:
  def __init__(self, name, schema, parties, entity_service_url):
    self.name = name
    self.schema = schema
    self.parties = parties
    self.entity_service_url = entity_service_url
    self.runs = []

  def start_project(self):
    post_body = {'name': self.name, 'schema': self.schema,
      'number_parties': len(self.parties), 'result_type': 'groups'}
    response = requests.post("{}/projects".format(self.entity_service_url), json=post_body)
    response.raise_for_status()
    response_body = response.json()
    self.project_id = response_body['project_id']
    update_tokens = response_body['update_tokens']
    self.update_token_map = dict(zip(self.parties, update_tokens))
    self.result_token = response_body['result_token']

  def upload_clks(self, party, clks):
    headers = {'Authorization': self.update_token_map[party]}
    response = requests.post("{}/projects/{}/clks".format(self.entity_service_url, self.project_id),
      headers=headers, data=clks)
    response.raise_for_status()

  def start_run(self, threshold):
    headers = {'Authorization': self.result_token}
    post_body = {'threshold': threshold}
    response = requests.post("{}/projects/{}/runs".format(self.entity_service_url, self.project_id),
      headers=headers, json=post_body)
    response.raise_for_status()
    response_body = response.json()
    self.runs.append(response_body['run_id'])

  def get_run_status(self, run_id=None):
    run_to_check = run_id
    if run_to_check is None:
      run_to_check = self.runs[-1]
    headers = {'Authorization': self.result_token}
    response = requests.get("{}/projects/{}/runs/{}".format(self.entity_service_url, self.project_id, run_to_check),
      headers=headers)
    return response.json()

  def get_results(self, run_id=None):
    run_to_check = run_id
    if run_to_check is None:
      run_to_check = self.runs[-1]
    headers = {'Authorization': self.result_token}
    response = requests.get("{}/projects/{}/runs/{}/results".format(self.entity_service_url, self.project_id, run_to_check),
      headers=headers)
    return response.json()

class Results:
  def __init__(self, systems, project, results):
    self.systems = systems
    self.results = results
    self.project = project

  def insert_results(self, table):
    for result_group in self.results:
      record = {}
      for result_record in result_group:
        record[self.systems[result_record[0]]] = result_record[1]
      query = None
      RecordGroup = Query()
      for system, id in record.items():
        if query is None:
          query = RecordGroup[system].any([id])
        else:
          query = query | RecordGroup[system].any([id])
      query_result = table.search(query)
      if len(query_result) == 0:
        document_to_insert = {}
        for system, id in record.items():
          document_to_insert[system] = [id]
        run_result = record
        run_result['project'] = self.project
        document_to_insert['run_results'] = [run_result]
        table.insert(document_to_insert)
      if len(query_result) == 1:
        result_doc = query_result[0]
        for system, id in record.items():
          system_ids = result_doc.get(system)
          if system_ids is None:
            table.update(set(system, [id]), query)
          elif id not in system_ids:
            table.update(add(system, [id]), query)
        run_result = record
        run_result['project'] = self.project
        table.update(add('run_results', run_result), query)
      if len(query_result) > 1:
        raise ValueError("There should only be a single query result.")


