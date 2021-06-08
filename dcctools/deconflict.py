def deconflict(result_document, systems):
  final_record = {}
  system_conflicts = []
  for s in systems:
    if len(result_document.get(s, [])) > 1:
      system_conflicts.append(s)
    else:
      if result_document.get(s) is not None:
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

def household_deconflict(household_links, individual_links, systems, config):
  house_mappings = {}
  conflicts = []
  single_households = {}
  metrics = {'equal': 0, 'conflict': 0, 'combine': 0, 'skipped': 0}
  for s in systems:
    house_mappings[s] = config.get_data_owner_household_links(s)
    single_households[s] = []
  new_links = convert_ilinks_to_hlinks(individual_links, house_mappings, systems)
  for new in new_links:
    for s in systems:
      if new[s]:
        found = next((link for link in household_links if s in link.keys() and new[s] == link[s]), None)
        if found:
          # Check if new link is already in list and skip rest of new parse if so
          if found == new:
            metrics['equal'] += 1
            break
          # Check if new conflicts with found
          for i, sys in enumerate(systems):
            if sys in found.keys() and found[sys] and new[sys] and (found[sys] != new[sys]):
              metrics['conflict'] += 1
              add_to_singles(single_households, systems, new)
              conflicts.append(new)
              household_links.remove(found)
              break
            else:
              if i == (len(systems) - 1):
                metrics['combine'] += 1
              if sys in found.keys() and found[sys]:
                new[sys] = found[sys]
              else:
                found[sys] = new[sys]
        else:
          # If not found in the household_links it must have been removed due to conflict
          metrics['skipped'] += 1
          conflicts.append(new)
          add_to_singles(single_households, systems, new)
          break
  print('After deconflict and before add singles: ' + str(len(household_links)))
  add_single_households(household_links, single_households, systems)
  print('Final linkage count: ' + str(len(household_links)))
  print("Exact individual links found in pprl household links: {}".format(str(metrics['equal'])))
  print("Number of individual links conflicting with pprl links: {}".format(str(metrics['conflict'])))
  print("Number of individual links combined into PPRL links: {}".format(str(metrics['combine'])))
  print("Number of individual links skipped from previous conflict: {}".format(str(metrics['skipped'])))

def add_single_households(household_links, single_households, systems):
  for s in systems:
    single_households_deduped = list(dict.fromkeys(single_households[s]))
    single_link = {}
    for house in single_households_deduped:
      single_link[s] = house
      household_links.append(single_link)

def add_to_singles(single_households, systems, new):
  for sys in systems:
    if new[sys]:
      single_households[sys].append(new[sys])

def convert_ilinks_to_hlinks(individual_links, house_mappings, systems):
  new_links = []
  for ilink in individual_links:
    new_link = {}
    for s in systems:
      if s in ilink.keys() and house_mappings[s] and house_mappings[s][str(ilink[s])]:
        new_link[s] = house_mappings[s][str(ilink[s])]
      else:
        new_link[s] = None
    new_links.append(new_link)
  return new_links
