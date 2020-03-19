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
    id_to_link_count = {}
    for cid in conflicting_ids:
      id_to_link_count[cid] = link_count(result_document, sc, cid)
    final_record[sc] = max(id_to_link_count, key=lambda key: id_to_link_count[key])

  return final_record

def link_count(result_document, system, id):
  count = 0
  for rr in result_document['run_results']:
    if rr.get(system, None) == id:
      count += 1
  return count
