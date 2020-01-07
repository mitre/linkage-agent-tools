def deconflict(result_document, systems):
  system_conflicts = []
  for s in systems:
    if len(result_document[s]) > 1:
      system_conflicts.append(s)


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