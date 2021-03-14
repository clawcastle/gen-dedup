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
file = "cache_hits"


for occurences, entries in dataloader.load_data(scenarios, cache_sizes, n_files, types, sdfs, sdbs, file):
    vals = OrderedDict(sorted(occurences.items()))
    # something = sorted(list(map(lambda x: x, occurences.items())), key=lambda x: x["filename"])
    
    plt.bar(vals.keys(), vals.values(), color='g')
    plt.show()

    in_cache_values = list(map(lambda x: int(x["inCache"]), entries))
    window_size = 200

    cache_series = pd.Series(in_cache_values)
    windows = cache_series.rolling(window_size)
    moving_average = windows.mean().tolist()

    without_nans = moving_average[window_size - 1:]

            
    # step = 50
    # buckets = [sum(list(map(lambda x: int(x["inCache"]), entries[i:i+step]))) / step for i in range(0, len(entries), step)]

    plt.plot(range(len(without_nans)), without_nans)
    plt.show()