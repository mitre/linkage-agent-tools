def deconflict(result_document, systems):
  final_record = {}
  system_conflicts = []
  for s in systems:
    if len(result_document.get(s, [])) > 1:
      system_conflicts.append(s)
    else:
      final_record[s] = result_document[s][0]
  for sc in system_conflicts:
    conflicting_ids = result_document[sc]
    id_to_average_strength = {}
    for cid in conflicting_ids:
      id_to_average_strength[cid] = average_link_strength(result_document, sc, cid)
    final_record[sc] = max(id_to_average_strength, key=lambda key: id_to_average_strength[key])

  return final_record

def average_link_strength(result_document, system, id):
  scores = []
  for l in result_document['links']:
    if l.get(system, None) == id:
      scores.append(l['score'])
  return sum(scores) / len(scores)

def link_count(result_document, system, id):
  count = 0
  for l in result_document['links']:
    if l.get(system, None) == id:
      count += 1
  return count