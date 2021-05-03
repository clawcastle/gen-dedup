from expiringdict import ExpiringDict
import os
from measurement_session import get_settings
from collections import deque

class CodedCache:
    file_metadata = {} #{count: 0, n_fragments: 0}
    cache = {}
    total_count = 0
    settings = get_settings()
    CACHE_SIZE = settings["cache_size"]
    #{file1: [{frag1: [...]}, {frag2: [...]}]}
    def add_to_cache(self, key, values):
        if key not in self.file_metadata:
            self.file_metadata[key] = {"count": 0, "n_fragments": 0}

        if self.file_metadata[key]['n_fragments'] == 10:
            return

        count = self.file_metadata[key]['count']
        percentage = 100 if self.total_count == 0 else round(count / self.total_count * 100, 1)

        if percentage >= 100 // self.CACHE_SIZE and percentage > self.file_metadata[key]['n_fragments'] / self.CACHE_SIZE * 10:
            n_frags = 10 if percentage >= 1 else int(percentage * 10)
            frags_to_be_removed = n_frags - self.file_metadata[key]['n_fragments']
            self.file_metadata[key]['n_fragments'] = n_frags
            self.cache[key] = values[:n_frags]
            
            for _ in range(frags_to_be_removed):
                self.remove_from_cache()

    def remove_from_cache(self):
        for key, val in self.cache.items():
            count = self.file_metadata[key]['count']
            percentage = round(count / self.total_count * 100, 1)
            if percentage <= 100 // self.CACHE_SIZE:
                self.cache.pop(key)
            elif percentage < self.file_metadata[key]['n_fragments'] / self.CACHE_SIZE * 10:
                self.cache[key] = self.cache[key][1:]
                self.file_metadata[key]['n_fragments'] = self.file_metadata[key]['n_fragments'] - 1

    def is_in_cache(self, key):
        return key in self.cache

    def clear(self):
        self.settings = get_settings()
        self.CACHE_SIZE = self.settings["cache_size"]
        self.cache = {}
        self.file_metadata = {}
        self.total_count = 0

    def get_from_cache(self, key):
        print(self.CACHE_SIZE, flush=True)
        self.total_count += 1
        if key in self.file_metadata:
            self.file_metadata[key]["count"] += 1
        if self.is_in_cache(key):
            return self.cache[key]
        else:
            self.file_metadata[key] = {"count": 1, "n_fragments": 0}
            return []