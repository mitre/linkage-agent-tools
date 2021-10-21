import itertools as it
import json
import subprocess
import pymongo

import requests
from tqdm import tqdm


class Project:
    def __init__(self, name, schema, parties, entity_service_url, blocked):
        self.name = name
        self.schema = json.loads(schema)
        self.parties = parties
        self.blocked = blocked
        self.entity_service_url = entity_service_url
        self.runs = []

    def start_project(self):
        post_body = {
            "name": self.name,
            "schema": self.schema,
            "number_parties": len(self.parties),
            "result_type": "groups",
            "uses_blocking": self.blocked,
        }
        response = requests.post(
            "{}/projects".format(self.entity_service_url), json=post_body
        )
        response.raise_for_status()
        response_body = response.json()
        self.project_id = response_body["project_id"]
        update_tokens = response_body["update_tokens"]
        self.update_token_map = dict(zip(self.parties, update_tokens))
        self.result_token = response_body["result_token"]

    def upload_clks_blocked(self, party, clk, block):
        subprocess.run(
            [
                "anonlink",
                "upload",
                "--project",
                self.project_id,
                "--to_entityservice",
                "--server",
                self.entity_service_url.replace("/api/v1", ""),
                "--apikey",
                self.update_token_map[party],
                "--blocks",
                block,
                clk,
            ]
        )

    def upload_clks(self, party, clks):
        headers = {
            "Authorization": self.update_token_map[party],
            "Content-Type": "application/json",
        }
        response = requests.post(
            "{}/projects/{}/clks".format(self.entity_service_url, self.project_id),
            headers=headers,
            data=clks,
        )
        response.raise_for_status()

    def start_run(self, threshold):
        headers = {"Authorization": self.result_token}
        post_body = {"threshold": threshold}
        response = requests.post(
            "{}/projects/{}/runs".format(self.entity_service_url, self.project_id),
            headers=headers,
            json=post_body,
        )
        response.raise_for_status()
        response_body = response.json()
        self.runs.append(response_body["run_id"])

    def get_run_status(self, run_id=None):
        run_to_check = run_id
        if run_to_check is None:
            run_to_check = self.runs[-1]
        headers = {"Authorization": self.result_token}
        response = requests.get(
            "{}/projects/{}/runs/{}/status".format(
                self.entity_service_url, self.project_id, run_to_check
            ),
            headers=headers,
        )
        return response.json()

    def get_results(self, run_id=None):
        run_to_check = run_id
        if run_to_check is None:
            run_to_check = self.runs[-1]
        headers = {"Authorization": self.result_token}
        response = requests.get(
            "{}/projects/{}/runs/{}/result".format(
                self.entity_service_url, self.project_id, run_to_check
            ),
            headers=headers,
        )
        return response.json()


class Results:
    def __init__(self, systems, project, results):
        self.systems = systems
        self.results = results
        self.project = project

    def insert_results(self, collection):
        matches_to_insert = len(self.results["groups"])
        insert_count = 0

        for result_group in tqdm(self.results["groups"], desc="Inserting {} records into the local database: ".format(matches_to_insert)):
            record = {}
            for result_record in result_group:
                record[self.systems[result_record[0]]] = result_record[1]
            query = []
            for system, record_id in record.items():
                collection.create_index([(system, pymongo.ASCENDING)])
                query.append({system: record_id})
            query_result = collection.find({"$or": query})
            query_result_count = collection.count_documents({"$or": query})
            if query_result_count == 0:
                document_to_insert = {}
                for system, record_id in record.items():
                    document_to_insert[system] = [record_id]
                run_result = record
                run_result["project"] = self.project
                document_to_insert["run_results"] = [run_result]
                collection.insert_one(document_to_insert)
            elif query_result_count == 1:
                result_doc = query_result[0]
                doc_id = result_doc["_id"]
                updates = {"$addToSet": {}}
                for system, record_id in record.items():
                    updates["$addToSet"][system] = record_id
                run_result = record
                run_result["project"] = self.project
                updates["$addToSet"]["run_results"] = run_result
                collection.update_one({"_id": doc_id}, updates)
            else:
                # query_result_count > 1:
                # This identifies a link between clusters that weren't
                # linked before. We will need to merge the results
                merged_document = {"run_results": []}
                docs_to_delete = []
                for qr in query_result:
                    docs_to_delete.append(qr["_id"])
                    for system, id_list in qr.items():
                        if system != "run_results" and system != "_id":
                            existing_id_list = merged_document.get(system)
                            if existing_id_list is None:
                                merged_document[system] = id_list
                            else:
                                for record_id in id_list:
                                    if record_id not in existing_id_list:
                                        existing_id_list.append(record_id)
                    merged_document["run_results"].extend(qr["run_results"])
                for system, record_id in record.items():
                    system_ids = merged_document.get(system)
                    if system_ids is None:
                        merged_document[system] = [record_id]
                    elif record_id not in system_ids:
                        system_ids.append(record_id)
                run_result = record
                run_result["project"] = self.project
                merged_document["run_results"].append(run_result)
                collection.delete_many({"_id": {"$in": docs_to_delete}})
                collection.insert_one(merged_document)
            insert_count += 1
