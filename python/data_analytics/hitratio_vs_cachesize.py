import csv
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import OrderedDict
import dataloader

types = ["IMPROVED_LFU"]
sdbs = ["30"]
sdfs = ["60"]
scenarios = ["ScenarioFULL_FILE"]
cache_sizes = ["10", "20", "30", "50", "70", "100", "150", "200", "400", "800"]
n_files = ["500"]
file = "cache_hits"


cache_ratio = {}
i = 0
for occurences, entries in dataloader.load_data(scenarios, cache_sizes, n_files, types, sdfs, sdbs, file):
    in_cache_values = sum(list(map(lambda x: int(x["inCache"]), entries)))

    cache_ratio[int(cache_sizes[i])] = in_cache_values / 1000
    i = i + 1

lists = sorted(cache_ratio.items())
x, y = zip(*lists) 
plt.plot(x, y)
plt.show()







types = ["IMPROVED_LFU"]
sdbs = ["30"]
sdfs = ["60"]
scenarios = ["ScenarioDEDUP"]
cache_sizes = ["100", "200", "300", "500", "700", "1000", "1500", "2000", "4000", "8000"]
n_files = ["500"]
file = "cache_hits"

cache_ratio = {}
i = 0
for occurences, entries in dataloader.load_data(scenarios, cache_sizes, n_files, types, sdfs, sdbs, file):
    in_cache_values = sum(list(map(lambda x: int(x["inCache"]), entries)))

    cache_ratio[int(cache_sizes[i])] = in_cache_values / 10000
    i = i + 1

lists = sorted(cache_ratio.items())
x, y = zip(*lists) 
plt.plot(x, y)
plt.show()