import csv
import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import OrderedDict


def load_csv(scenario, cache_size, n_file, type, sdf, sdb, file):
    parent_folder = './measurements'
    scenario_folder = f'/{scenario}'
    settings_folder = f'/CACHE_SIZE={cache_size}_NFILES={n_file}'
    strategy_folder = f'/{type}_SDF={sdf}_SDB={sdb}'
    filename = f'/{file}.csv'

    path = parent_folder + scenario_folder + settings_folder + strategy_folder + filename

    with open(path) as f:
        entries = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]

    occurences = {}

    for elem in entries:
        if elem["filename"] not in occurences:
            occurences[elem["filename"]] = 1
        else:
            occurences[elem["filename"]] = occurences[elem["filename"]] + 1 
    
    return occurences, entries


def load_data(scenarios, cache_sizes, n_files, types, sdfs, sdbs, file):
    for scenario in scenarios: 
        for cache_size in cache_sizes:
            for n_file in n_files:
                for type in types: 
                    for sdf in sdfs: 
                        for sdb in sdbs: 
                            yield load_csv(scenario, cache_size, n_file, type, sdf, sdb, file)

                