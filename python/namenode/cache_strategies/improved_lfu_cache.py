from collections import deque
import os

class ImprovedLFUCache:
    cache = {}
    frequencies = deque()
    CACHE_SIZE = int(os.environ.get("CACHE_SIZE"))
    threshold = CACHE_SIZE - CACHE_SIZE // 5

    def add_to_cache(self, key, value):
        if not self.is_in_cache(key):
            if len(self.cache) >= self.CACHE_SIZE:
                self.cache.pop(self.frequencies[self.threshold]["key"])
                del self.frequencies[self.threshold]
        
            self.cache[key] = value
            self.frequencies.append({"key": key, "freq": 1})
    
    def is_in_cache(self, key):
        return key in self.cache

    def get_from_cache(self, key):
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
            for i in range(element_index - 1, -1, -1):
                if element_frequency <= self.frequencies[i]["freq"] or i == 0:
                    del self.frequencies[element_index]
                    self.frequencies.insert(i, {"key": key, "freq": element_frequency})
                    break                  

            return self.cache[key]
        else: 
            return None