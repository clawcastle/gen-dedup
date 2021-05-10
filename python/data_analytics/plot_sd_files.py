import csv
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import OrderedDict
# import dataloader

def get_ratio(scenario, cache_size, n_file, type, sdf, sdb, file):
    parent_folder = './measurements'
    scenario_folder = f'/{scenario}'
    settings_folder = f'/CACHE_SIZE={cache_size}_NFILES={n_file}'
    strategy_folder = f'/{type}_SDF={sdf}_SDB={sdb}'
    filename = f'/{file}.csv'

    path = parent_folder + scenario_folder + settings_folder + strategy_folder + filename

    print(path)
    with open(path) as f:
        entries = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]

    occurences = {}

    entries = entries[5000:]

    for elem in entries:
        if elem["filename"] not in occurences:
            occurences[elem["filename"]] = 1
        else:
            occurences[elem["filename"]] = occurences[elem["filename"]] + 1 
    
    in_cache_values = sum(list(map(lambda x: int(x["inCache"]), entries)))

    x = 1000 if scenario == "ScenarioFULL_FILE" else 10000
    cache_ratio = in_cache_values / x

    return cache_ratio


types = ["CODED"] #"LFU", "TIME"]
sdb = "30"
sdfs = ["25", "50", "100", "150", "200", "250"]#"S=120"]
scenarios = ["ScenarioCODED"]
cache_size = "800"
n_files = "1000"
file = "cache_hits"

cache_ratio = {}

for scenario in scenarios:
    for t in types:
        for sdf in sdfs:
            size = "80" if scenario == "ScenarioFULL_FILE" else "800"
            ratio = get_ratio(scenario, size, n_files, t, sdf, sdb, file)
            cache_ratio[int(sdf)] = ratio
    lists = sorted(cache_ratio.items())
    x, y = zip(*lists)
    p, = plt.plot(x, y)
    p.set_label(scenario)
    plt.legend()

plt.xlabel("Requested files standard deviation")
plt.ylabel("Cache utilization ratio")
plt.title("SD Files")

plt.show()