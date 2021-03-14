import numpy as np
import requests
from scipy.stats import truncnorm
import math
from time import time
import csv
import hashlib
import matplotlib.pyplot as plt
import settings


def start_session():
    res = requests.post("http://localhost:3000/measurements/session/start", data=dict(sd_files=settings.SD_FILES, sd_bytes=settings.SD_BYTES, mean_files=settings.MEAN_FILES, mean_bytes=settings.MEAN_BYTES, scenario=settings.SCENARIO, n_files=settings.N_FILES, n_requests=settings.N_REQUESTS))
    if res.status_code < 200 or res.status_code > 299:
        raise Exception("Session was not started")

start_session()

request_file_ids = list(map(lambda x: math.floor(x), truncnorm.rvs((0-settings.MEAN_FILES)/settings.SD_FILES,(settings.N_FILES-1-settings.MEAN_FILES)/settings.SD_FILES,loc=settings.MEAN_FILES,scale=settings.SD_FILES,size=settings.N_REQUESTS)))

print("Starting get requests")
timings = []
labels = ["request_id", "file_id", "elapsed_time"]
for i, id in enumerate(request_file_ids):
    file_name = f"file_{id}"
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


