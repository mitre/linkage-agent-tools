import json


def pretty_print(json_obj):
    return json.dumps(json_obj, indent=2, sort_keys=False)


def get_str(json_object):
    return str(json.dumps(json_object))



