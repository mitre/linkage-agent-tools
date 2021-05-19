import time
from dcctools.config import Configuration
from tinydb import TinyDB
from tinydb.storages import JSONStorage
from tinydb.middlewares import CachingMiddleware
from dcctools.anonlink import Results, Project


def match():
    c = Configuration("config.json")
    database = TinyDB('results.json', storage=CachingMiddleware(JSONStorage))
    for project_name, schema in c.load_schema().items():
        project = Project(project_name, schema, c.systems(), c.entity_service_url())
        project.start_project()
        for system in c.systems():
            project.upload_clks(system, c.get_clks(system, project_name))
        project.start_run(c.matching_threshold())
        running = True
        while running:
            status = project.get_run_status()
            print(status)
            if status.get('state') == 'completed':
                running = False
            time.sleep(0.5)
        result_json = project.get_results()
        results = Results(c.systems(), project_name, result_json)
        print(result_json)
        results.insert_results(database)

    database.close()


if __name__ == "__main__":
    match()
