import pytest
from dcctools.anonlink import generate_results_information

def test_generate_results_information():
  root_path = '/foo'
  systems = ['a', 'b', 'c']
  projects = ['name-sex-dob', 'name-phone-dob']
  info = generate_results_information(root_path, systems, projects)
  assert len(info) == 6
  assert info[0]['filename'] == '/foo/name-sex-dob/output-a-b.json'
  assert info[5]['filename'] == '/foo/name-phone-dob/output-b-c.json'
