import csv
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import OrderedDict
import dataloader

types = ["IMPROVED_LFU", "CODED"]
sdbs = ["1250"]
sdfs = ["10", "40", "70", "100", "130", "160", "190", "220", "250"]
#scenarios = ["ScenarioFULL_FILE"]
# cache_sizes = ["100","200","400","600","800","1000","1200","1400","1600","1800","2000"]
cache_sizes = ["1000"]
n_files = ["1000"]
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

labels = {"CODED": "Coded", "DEDUP_SdFiles": "Dedup", "GEN_DEDUP_SdFiles": "GenDedup", "FULL_FILE": "Full file"}

scenarios = ["CODED", "FULL_FILE", "DEDUP_SdFiles", "GEN_DEDUP_SdFiles"]
for scenario in scenarios:
    cache_ratio = {}
    i = 0
    x = []
    y = []
    if scenario == "FULL_FILE":
        cache_sizes = ["100"]
        # cache_sizes = ["10","20","40","60","80","100","120","140","160","180","200"]
    else:
        cache_sizes = ["1000"]
        # cache_sizes = ["100","200","400","600","800","1000","1200","1400","1600","1800","2000"]



    types = ["CODED"] if scenario == "CODED" else ["IMPROVED_LFU"]
    for occurences, entries in dataloader.load_data(["Scenario" + scenario], cache_sizes, n_files, types, sdfs, sdbs, file):
        entries = entries[1000:] if scenario == "FULL_FILE" else entries[10000:]
        
        in_cache_values = sum(list(map(lambda x: int(x["inCache"]), entries)))
        if scenario == "FULL_FILE":
            cache_ratio[int(sdfs[i])] = in_cache_values / 2000
        else:
            cache_ratio[int(sdfs[i])] = in_cache_values / 20000
        i = i + 1

    lists = sorted(cache_ratio.items())
    x, y = zip(*lists)
    plt.plot(x, y, label=labels[scenario])
plt.xlabel("SD Files")
plt.ylabel("Cache utilization ratio")
plt.title("Cache utilization ratios")
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