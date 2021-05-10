import numpy as np
import requests
from scipy.stats import truncnorm
import math
from time import time
import csv
import hashlib
import matplotlib.pyplot as plt
import settings


def start_session(entry):
    print(entry['cache_size'])
    res = requests.post("http://localhost:3000/measurements/session/start", data=dict(sd_files=entry['sd_files'], sd_bytes=entry['sd_bytes'], mean_files=entry['mean_files'], mean_bytes=entry['mean_bytes'], scenario=entry['scenario'], n_files=entry['n_files'], n_requests=entry['n_requests'], cache_size=entry['cache_size']))
    if res.status_code < 200 or res.status_code > 299:
        raise Exception("Session was not started")

path = "test_sd_bytes_gendedup.csv"
with open(path) as f:
    entries = [{k: v for k, v in row.items()}
        for row in csv.DictReader(f, skipinitialspace=True)]

for entry in entries: 
    print(f"Starting scenario: {entry['scenario']} with sd_files = {entry['sd_files']}")
    start_session(entry)
    request_file_ids = list(map(lambda x: math.floor(x), truncnorm.rvs((0-int(entry['mean_files']))/int(entry['sd_files']),(int(entry['n_files'])-1-int(entry['mean_files']))/int(entry['sd_files']),loc=int(entry['mean_files']),scale=int(entry['sd_files']),size=int(entry['n_requests']))))

    print("Starting get requests")
    timings = []
    labels = ["request_id", "file_id", "elapsed_time"]
    for i, id in enumerate(request_file_ids):
        # file_name = f"{entry['scenario']}_{id}"
        file_name = f"{entry['scenario']}_SD{entry['sd_bytes']}_{id}"
        start = time()
        response = requests.get(f"http://localhost:3000/file/{file_name}")
        elapsed = time() - start
        timings.append({
            "request_id": i,
            "file_id": id,
            "elapsed_time": elapsed
        })

    filename = f"./timings.csv"

    with open(filename, "a", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=labels)
        writer.writeheader()
        for elem in timings:
            writer.writerow(elem)


