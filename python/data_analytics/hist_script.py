import csv
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import OrderedDict
import dataloader

types = ["IMPROVED_LFU"] #"LFU", "TIME"]
sdbs = ["30"]
sdfs = ["60"]#"S=120"]
scenarios = ["ScenarioTEST"]
cache_sizes = ["1000"]
n_files = ["500"]
file = "get_file_request"


for occurences, entries in dataloader.load_data(scenarios, cache_sizes, n_files, types, sdfs, sdbs, file):
    vals = OrderedDict(sorted(occurences.items()))
    # something = sorted(list(map(lambda x: x, occurences.items())), key=lambda x: x["filename"])
    
    plt.bar(vals.keys(), vals.values(), color='g')
    plt.show()

    cache_hits = {}

    for entry in entries:
        if entry["filename"] not in cache_hits:
            cache_hits[entry["filename"]] = int(entry["cache_hits"])
        else:
            cache_hits[entry["filename"]] = cache_hits[entry["filename"]] + int(entry["cache_hits"])

    cache_hit_vals = OrderedDict(sorted(cache_hits.items()))

    plt.bar(cache_hit_vals.keys(), cache_hit_vals.values(), color='b')
    plt.show()

    cache_hits2 = {}

    for k, v in cache_hit_vals.items():
        cache_hits2[k] = v / occurences[k]

    plt.bar(cache_hits2.keys(), cache_hits2.values(), color='b')
    plt.show()

    # in_cache_values = list(map(lambda x: int(x["inCache"]), entries))
    # window_size = 20

    # cache_series = pd.Series(in_cache_values)
    # windows = cache_series.rolling(window_size)
    # moving_average = windows.mean().tolist()[:1000]

    # without_nans = moving_average[window_size - 1:]

            
    # step = 50
    # buckets = [sum(list(map(lambda x: int(x["inCache"]), entries[i:i+step]))) / step for i in range(0, len(entries), step)]

    # plt.plot(range(len(without_nans)), without_nans)
    # plt.show()