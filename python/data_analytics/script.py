import csv
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import OrderedDict
# entries = {}

# dict_from_csv = pd.read_csv('./measurements/FIFO_M=250_S=30/FIFO_cache_hits.csv', header=0, index_col=0, squeeze=True, names=["filename","chunk","inCache"]).to_dict()
# print(dict_from_csv)

types = ["IMPROVED_LFU"] #"LFU", "TIME"]
means = ["M=250"]
sds = ["S=60"]#"S=120"]


for type in types:
    for mean in means:
        for sd in sds:
            filename = f'./measurements/Scenario3/CACHESIZE_25_FILES_500/{type}_{mean}_{sd}/{type}_cache_hits.csv'

            with open(filename) as f:
                entries = [{k: v for k, v in row.items()}
                    for row in csv.DictReader(f, skipinitialspace=True)]

            occurences = {}

            for elem in entries:
                if elem["filename"] not in occurences:
                    occurences[elem["filename"]] = 1
                else:
                    occurences[elem["filename"]] = occurences[elem["filename"]] + 1 
            
            

            vals = OrderedDict(sorted(occurences.items()))
            # something = sorted(list(map(lambda x: x, occurences.items())), key=lambda x: x["filename"])
            
            plt.bar(vals.keys(), vals.values(), color='g')
            plt.show()

            in_cache_values = list(map(lambda x: int(x["inCache"]), entries))
            window_size = 20

            cache_series = pd.Series(in_cache_values)
            windows = cache_series.rolling(window_size)
            moving_average = windows.mean().tolist()[:1000]

            without_nans = moving_average[window_size - 1:]

                    
            # step = 50
            # buckets = [sum(list(map(lambda x: int(x["inCache"]), entries[i:i+step]))) / step for i in range(0, len(entries), step)]

            

            plt.title(f'{type} : {sd}')
            plt.plot(range(len(without_nans)), without_nans)
            plt.show()