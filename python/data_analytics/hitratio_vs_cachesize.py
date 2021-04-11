import csv
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import OrderedDict
import dataloader

types = ["IMPROVED_LFU"]
sdbs = ["5"]
sdfs = ["200"]
#scenarios = ["ScenarioFULL_FILE"]
cache_sizes = ["10", "20", "30", "50", "70", "100", "150", "200", "400", "800"]
n_files = ["500"]
file = "cache_hits"


# cache_ratio = {}
# i = 0
# for occurences, entries in dataloader.load_data(scenarios, cache_sizes, n_files, types, sdfs, sdbs, file):
#     in_cache_values = sum(list(map(lambda x: int(x["inCache"]), entries)))
#
#     cache_ratio[int(cache_sizes[i])] = in_cache_values / 1000
#     i = i + 1
#
# lists = sorted(cache_ratio.items())
# x, y = zip(*lists)
# plt.plot(x, y)
# plt.show()

scenarios = ["FULL_FILE", "GEN_DEDUP", "DEDUP"]
for scenario in scenarios:
    cache_ratio = {}
    i = 0
    x = []
    y = []
    if scenario == "FULL_FILE":
        cache_sizes = ["10", "20", "30", "50", "70", "100", "150", "200"]
    else:
        cache_sizes = ["100", "200", "300", "500", "700", "1000", "1500", "2000"]

    for occurences, entries in dataloader.load_data(["Scenario" + scenario], cache_sizes, n_files, types, sdfs, sdbs, file):
        entries = entries[5000:] if scenario == "GEN_DEDUP" or scenario == "DEDUP" else entries[500:]
        
        in_cache_values = sum(list(map(lambda x: int(x["inCache"]), entries)))

        if scenario == "FULL_FILE":
            cache_ratio[int(cache_sizes[i])*10] = in_cache_values / 500
        else:
            cache_ratio[int(cache_sizes[i])] = in_cache_values / 5000
        i = i + 1

    lists = sorted(cache_ratio.items())
    x, y = zip(*lists)
    plt.plot(x, y, label=scenario)
plt.xlabel("Cache size")
plt.ylabel("Cache utilization ratio")
plt.title("FIFO cache")
plt.legend(loc="upper right")
plt.show()

# types = ["TIME"]
# sdbs = ["30"]
# sdfs = ["60"]
# scenarios = ["ScenarioGEN_DEDUP"]
# cache_sizes = ["100", "200", "300", "500", "700", "1000", "1500", "2000", "4000", "8000"]
# n_files = ["500"]
# file = "cache_hits"
#
# cache_ratio = {}
# i = 0
# for occurences, entries in dataloader.load_data(scenarios, cache_sizes, n_files, types, sdfs, sdbs, file):
#     in_cache_values = sum(list(map(lambda x: int(x["inCache"]), entries)))
#
#     cache_ratio[int(cache_sizes[i])] = in_cache_values / 10000
#     i = i + 1
#
# lists = sorted(cache_ratio.items())
# x, y = zip(*lists)
# plt.plot(x, y)
# plt.show()