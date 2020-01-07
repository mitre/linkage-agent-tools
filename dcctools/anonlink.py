import itertools as it

def insert_results(results_collection, left_system, right_system, run_name, results):
  for match in results['similarity_scores']:
    left_id = match[0]
    right_id = match[1]
    score = match[2]
    query = {'$or': [{left_system: left_id}, {right_system: right_id}]}
    existing_count = results_collection.count_documents(query)
    link = {
      left_system: left_id,
      right_system: right_id,
      'run_name': run_name,
      'score': score
    }
    if existing_count == 0:
      results_collection.insert_one({left_system: [left_id],
                                     right_system: [right_id],
                                     'links': [link]})
    else:
      results_collection.update_many(query, {
        '$addToSet': {left_system: left_id,
                      right_system: right_id,
                      'links': {link}}
      })

def generate_results_information(root_path, systems, projects):
  info = []
  system_combinations = it.combinations(systems, 2)
  for system_combo in system_combinations:
    left_system = system_combo[0]
    right_system = system_combo[1]
    for project in projects:
      info.append('{}/{}/output-{}-{}.json'.format(root_path, project, left_system, right_system))
  return info

