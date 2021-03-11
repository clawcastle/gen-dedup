from cache_strategies import fifo_cache, lfu_cache, time_cache, simple_cache, improved_lfu_cache
import os
import csv

class Cache:
    cache = None
    filename = ""
    labels = ["filename", "chunk", "inCache"]
    measuring = bool(os.environ.get("MEASUREMENT_MODE"))

    def __init__(self):
        CACHE_STRATEGY = os.environ.get("CACHE_STRATEGY")

        if self.measuring:
            self.filename = f"./data/{CACHE_STRATEGY}_cache_hits.csv"
            with open(self.filename, "w") as f:
                writer = csv.DictWriter(f, fieldnames=self.labels)
                writer.writeheader()

        if CACHE_STRATEGY == "FIFO":
            print("FIFO", flush=True)
            self.cache = fifo_cache.FifoCache()
        elif CACHE_STRATEGY == "TIME":
            print("TIME", flush=True)
            self.cache = time_cache.TimeCache()
        elif CACHE_STRATEGY == "LFU":
            print("LFU", flush=True)
            self.cache = lfu_cache.LFUCache()
        elif CACHE_STRATEGY == "IMPROVED_LFU":
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
