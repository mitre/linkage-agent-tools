from pymongo import MongoClient
from dcctools.anonlink import generate_results_information, insert_results
import json

root_path = '/Users/andrewg/projects/anonlink-multiparty/data/mulit-round/siblings'
systems = ['a', 'b', 'c']
projects = ['name-sex-dob-zip', 'name-sex-dob-phone', 'name-sex-dob-addr', 'name-sex-dob-parents']

info = generate_results_information(root_path, systems, projects)

client = MongoClient()
db = client['codi']
results_collection = db['results']

for i in info:
  with open(i['filename']) as f:
    results = json.load(f)
    insert_results(results_collection, i['left_system'], i['right_system'], i['project'], results)