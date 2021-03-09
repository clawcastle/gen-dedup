from cache_strategies import fifo_cache, lfu_cache, time_cache, simple_cache
import os

class Cache:

    cache = None
    
    def __init__(self):
        CACHE_STRATEGY = os.environ.get("CACHE_STRATEGY")

        if CACHE_STRATEGY == "FIFO":
            print("FIFO", flush=True)
            self.cache = fifo_cache.FifoCache()
        elif CACHE_STRATEGY == "TIME":
            print("TIME", flush=True)
            self.cache = time_cache.TimeCache()
        elif CACHE_STRATEGY == "LFU":
            print("LFU", flush=True)
            self.cache = lfu_cache.LFUCache()
        else:
            self.cache = simple_cache.SimpleCache()

    def add_to_cache(self, key, value):
        self.cache.add_to_cache(key, value)

    def is_in_cache(self, key):
        return self.cache.is_in_cache(key)

    def get_from_cache(self, key):
        return self.cache.get_from_cache(key)
