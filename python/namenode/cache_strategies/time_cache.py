from expiringdict import ExpiringDict
import os

class TimeCache:
    CACHE_SIZE = int(os.environ.get("CACHE_SIZE"))

    cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=10)

    def add_to_cache(self, key, value):
        if not self.is_in_cache(key):
            self.cache[key] = value
    
    def is_in_cache(self, key):
        return key in self.cache

    def get_from_cache(self, key):
        if self.is_in_cache(key):
            print(len(self.cache))
            return self.cache[key]
        else:
            return None

