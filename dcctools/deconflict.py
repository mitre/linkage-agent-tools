def deconflict(result_document, systems, project_weights=None):
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
            id_to_link_scores[cid] = link_scores(result_document, sc, cid, project_weights)
        final_record[sc] = max(id_to_link_count, key=lambda key: id_to_link_count[key])

    return final_record


def link_scores(result_document, system, link_id, project_weights):
    count = 0
    for rr in result_document["run_results"]:
        if rr.get(system, None) == link_id:
            if project_weights is not None:
                count += project_weights[rr.get('project', 0)]
            else:
                count += 1
    return count
