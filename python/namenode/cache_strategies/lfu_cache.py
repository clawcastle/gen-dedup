from collections import deque
import os

class LFUCache:
    cache = {}
    frequencies = deque()
    CACHE_SIZE = int(os.environ.get("CACHE_SIZE"))

    def add_to_cache(self, key, value):
        if not self.is_in_cache(key):
            if len(self.cache) >= self.CACHE_SIZE:
                removed_item = self.frequencies.pop()
                self.cache.pop(removed_item["key"])
        
            self.cache[key] = value
            self.frequencies.append({"key": key, "freq": 1})
    
    def is_in_cache(self, key):
        return key in self.cache

    def get_from_cache(self, key):
        print(len(self.cache))
        if self.is_in_cache(key):
            element_index = 0
            element_frequency = 0

            # Updating the frequency of the element requested
            for i, elem in enumerate(self.frequencies):
                if elem["key"] == key: 
                    elem["freq"] = elem["freq"] + 1
                    element_frequency = elem["freq"]
                    element_index = i
                    break
            
            # Sorting the list of frequencies
            for i in range(element_index - 1, 0, -1):
                if element_frequency <= self.frequencies[i]["freq"]:
                    del self.frequencies[element_index]
                    self.frequencies.insert(i, {"key": key, "freq": element_frequency})
                    break                  

            return self.cache[key]
        else: 
            return None