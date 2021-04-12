from cache_strategies import fifo_cache, lfu_cache, time_cache, simple_cache, improved_lfu_cache
import os
import csv
from measurement_session import get_settings
from pathlib import Path

class Cache:
    cache = None
    labels = ["filename", "chunk", "inCache"]
    measuring = bool(os.environ.get("MEASUREMENT_MODE"))
    filename = ""
    CACHE_STRATEGY = os.environ.get("CACHE_STRATEGY")


    def __init__(self):

        if self.CACHE_STRATEGY == "FIFO":
            print("FIFO", flush=True)
            self.cache = fifo_cache.FifoCache()
        elif self.CACHE_STRATEGY == "TIME":
            print("TIME", flush=True)
            self.cache = time_cache.TimeCache()
        elif self.CACHE_STRATEGY == "LFU":
            print("LFU", flush=True)
            self.cache = lfu_cache.LFUCache()
        elif self.CACHE_STRATEGY == "IMPROVED_LFU":
            print("IMPROVED_LFU", flush=True)
            self.cache = improved_lfu_cache.ImprovedLFUCache()
        else:
            self.cache = simple_cache.SimpleCache()

    def add_to_cache(self, key, value):
        self.cache.add_to_cache(key, value)

    def is_in_cache(self, key):
        return self.cache.is_in_cache(key)

    def get_from_cache(self, key, request_filename):
        cache_hit = self.cache.get_from_cache(key)

        if self.measuring:
            with open(self.filename, "a") as f:
                    writer = csv.DictWriter(f, fieldnames=self.labels)
                    writer.writerow({"filename": request_filename, "chunk": key, "inCache": 1 if cache_hit is not None else 0})

        return cache_hit

    def new_measurement_session(self):        
        settings = get_settings()
        cache_size = settings["cache_size"]
        self.cache.clear()
        if self.measuring:
            folder_path = f'./measurements/Scenario{settings["scenario"]}/CACHE_SIZE={cache_size}_NFILES={settings["n_files"]}/{self.CACHE_STRATEGY}_SDF={settings["sd_files"]}_SDB={settings["sd_bytes"]}'
            # subfolder_path = f'CACHE_SIZE={cache_size}_NFILES={settings["n_files"]}'
            # subsubfolder_path = f'{self.CACHE_STRATEGY}_SDF={settings["sd_files"]}_SDB={settings["sd_bytes"]}'

            Path(folder_path).mkdir(parents=True, exist_ok=True)

            self.filename = folder_path + f"/cache_hits.csv"
            with open(self.filename, "w") as f:
                writer = csv.DictWriter(f, fieldnames=self.labels)
                writer.writeheader()

