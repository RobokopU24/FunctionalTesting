import requests
import json
import jsonlines
import os
from copy import deepcopy
from datetime import datetime as dt
import random

ROBOKOP_URL = "https://aragorn.renci.org/robokop/query"
ROBOKOP_CYPHER = "https://automat.renci.org/robokopkg/cypher"

def read_template(template_name):
    with open(f"templates/{template_name}.json","r") as inf:
        template = json.load(inf)
    id_node = None
    for node_id, node in template["message"]["query_graph"]["nodes"].items():
        if "ids" in node:
            id_node = node_id
    return template,id_node

def get_all_mondos():
    query = { "query": "MATCH (n:`biolink:Disease`) RETURN n.id" }
    response = requests.post(ROBOKOP_CYPHER, json=query)
    if response.status_code != 200:
        print("Bad response getting MONDOS")
        print(response)
        exit()
    j = response.json()
    disease_ids = [d["row"][0] for d in j["results"][0]["data"]]
    mondos = list(filter(lambda x: x.startswith("MONDO"), disease_ids))
    print(f"Found {len(mondos)} MONDOs")
    return mondos


def get_identifiers(id_source, randomize=True):
    if id_source == "MONDO":
        ids = get_all_mondos()
    else:
        print("Not supported:", id_source)
        exit()
    if randomize:
        random.shuffle(ids)
    return ids

def run_test(query_template, input_node_name, curie, num_reps, outputfile):
    message = deepcopy(query_template)
    message["message"]["query_graph"]["nodes"][input_node_name]["ids"].append(curie)
    for _ in range(num_reps):
        start = dt.now()
        response = requests.post(ROBOKOP_URL,json=message)
        end = dt.now()
        time_delta = end-start
        status = response.status_code
        result = {"input": curie, "start": start.isoformat(), "end": end.isoformat(),
                  "delta_seconds": time_delta.seconds, "delta_microseconds": time_delta.microseconds,
                  "status_code": status}
        if status == 200:
            result["Num Responses"] = len(response.json()["message"]["results"])
        outputfile.write(result)

def get_output_filename(odir):
    if not os.path.exists(odir):
        os.makedirs(odir)
    return f"{odir}/output.jsonl"

def poke(template_name, id_source, n_ids = 10, n_reps = 3, output_dir = "outdir"):
    template, input_node = read_template(template_name)
    input_ids = get_identifiers(id_source)
    outfilename = get_output_filename(output_dir)
    with jsonlines.open(outfilename,"w") as outf:
        for input_curie in input_ids[:n_ids]:
            run_test(template,input_node,input_curie,n_reps,outf)

if __name__ == '__main__':
    poke("diseasegene", "MONDO", n_ids = 500)
