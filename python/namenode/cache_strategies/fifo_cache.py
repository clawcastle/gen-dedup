import queue
from collections import OrderedDict
import os

class FifoCache:
    CACHE_SIZE = int(os.environ.get("CACHE_SIZE"))
    print(f"size: {CACHE_SIZE}")
    cache = OrderedDict()

    def add_to_cache(self, key, value):
        if not self.is_in_cache(key):
            if len(self.cache) >= self.CACHE_SIZE:
                self.cache.popitem()
            self.cache[key] = value


    def is_in_cache(self, key):
        return key in self.cache

    def get_from_cache(self, key):
        if self.is_in_cache(key):
            return self.cache[key]
        else:
            return None