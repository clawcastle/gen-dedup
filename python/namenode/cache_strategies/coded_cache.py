from expiringdict import ExpiringDict
import os
from measurement_session import get_settings
from collections import deque

class CodedCache:
    file_metadata = {}  # {count: 0, n_fragments: 0}
    cache = {}
    total_count = 0
    CACHE_SIZE = 100
    THRESHOLD_FOR_SINGLE_FRAG = 100 / CACHE_SIZE

    # {file1: [{frag1: [...]}, {frag2: [...]}]}

    def calculate_n_frags_allowed_in_cache(self, percentage):
        # Returns the number of fragments that the given file should have stored in cache
        n = int(percentage / self.THRESHOLD_FOR_SINGLE_FRAG)
        return 10 if n >= 10 else n

    def find_percentage_of_requests(self, count):
        # Calculates the percentage
        return 100 if self.total_count == 0 else round(count / self.total_count * 100, 1)

    def cache_should_be_updated(self, key, req_percentage):
        # Determines if the percentages of all requests is above the threshold needed to get a single fragment into the
        # cache and if the cache already has fragments of that file, it determines whether the percentage of all s
        # request allows for more entries in the cache.
        is_above_threshold = req_percentage >= self.THRESHOLD_FOR_SINGLE_FRAG
        more_frags_should_be_added = req_percentage > self.file_metadata[key]['n_fragments'] * self.THRESHOLD_FOR_SINGLE_FRAG

        return is_above_threshold and more_frags_should_be_added

    def get_length_of_cache_content(self):
        n_frags = 0
        for k, v in self.cache.items():
            n_frags = n_frags + len(v)

        return n_frags

    def remove_n_from_cache(self, n_frags_to_be_removed):
        total_removed = 0

        for i in range(n_frags_to_be_removed):
            # Since multiple fragments can be removed through one iteration, we do this check:
            if total_removed > i:
                continue
            keys_to_pop = []
            for key, val in self.cache.items():
                count = self.file_metadata[key]['count']
                req_percentage = self.find_percentage_of_requests(count)
                n_frags_allowed = self.calculate_n_frags_allowed_in_cache(req_percentage)
                n_frags_in_cache = self.file_metadata[key]['n_fragments']
                if n_frags_allowed == 0:
                    # The percentage is too low to allow any fragments in cache, hence the key is removed from the cache
                    keys_to_pop.append(key)
                    self.file_metadata[key]['n_fragments'] = 0
                    total_removed += n_frags_in_cache
                    break

                elif n_frags_allowed < self.file_metadata[key]['n_fragments']:
                    # The percentage is lower than the amount of fragments that it is permitted. Hence we need to reduce
                    # the number of fragments for that key
                    n_removed = n_frags_in_cache - n_frags_allowed

                    if n_removed > n_frags_to_be_removed - i:
                        # The percentage allows for fewer fragments, but there is no need to remove more than
                        # absolutely needed. In such a case we update n_removed and n_frags_allowed
                        n_removed = n_frags_to_be_removed - i
                        n_frags_allowed = n_frags_in_cache - n_removed

                    self.cache[key] = self.cache[key][:n_frags_allowed]
                    self.file_metadata[key]['n_fragments'] = self.file_metadata[key]['n_fragments'] - n_removed

                    if self.file_metadata[key]['n_fragments'] == 0:
                        keys_to_pop.append(key)

                    total_removed += n_removed
                    break

            for key in keys_to_pop:
                self.cache.pop(key)

        return total_removed

    def force_fragments_out(self, req_percentage, n_frags_to_be_removed):
        total_removed = 0

        for i in range(n_frags_to_be_removed):
            keys_to_pop = []
            for key, val in self.cache.items():
                count = self.file_metadata[key]['count']
                cache_req_percentage = self.find_percentage_of_requests(count)

                if req_percentage > cache_req_percentage:
                    n_frags_in_cache = self.file_metadata[key]['n_fragments']

                    if n_frags_in_cache == 1:
                        # The percentage is lower than the new file - we remove the last fragment, and thereby the element
                        keys_to_pop.append(key)
                        total_removed += 1
                        break
                    else:
                        # The percentage is lower, we remove a single fragment
                        self.cache[key] = self.cache[key][:n_frags_in_cache - 1]
                        self.file_metadata[key]['n_fragments'] = self.file_metadata[key]['n_fragments'] - 1

                        total_removed += 1
                        break
            for key in keys_to_pop:
                self.cache.pop(key)
        return total_removed

    def add_to_cache(self, key, values):
        if key not in self.file_metadata:
            self.file_metadata[key] = {"count": 0, "n_fragments": 0}

        if self.file_metadata[key]['n_fragments'] == 10:
            return

        count = self.file_metadata[key]['count']
        req_percentage = self.find_percentage_of_requests(count)

        if self.cache_should_be_updated(key, req_percentage):
            n_frags_allowed = self.calculate_n_frags_allowed_in_cache(req_percentage)
            n_frags_in_cache = self.get_length_of_cache_content()

            if n_frags_in_cache + n_frags_allowed <= self.CACHE_SIZE:
                # There is room in the cache for the fragments, hence nothing gets removed.
                self.file_metadata[key]['n_fragments'] = n_frags_allowed
                self.cache[key] = values[:n_frags_allowed]
            else:
                # We remove the number of frags needed to obtain the space needed for the n_frags_allowed
                n_frags_to_be_removed = n_frags_in_cache + n_frags_allowed - self.CACHE_SIZE

                n_removed = self.remove_n_from_cache(n_frags_to_be_removed)

                if n_frags_to_be_removed != n_removed:
                    n_frags_to_be_removed = n_frags_to_be_removed - n_removed
                    n_removed = n_removed + self.force_fragments_out(req_percentage, n_frags_to_be_removed)

                # Adding the fragments to the cache
                if n_frags_allowed - n_removed != 0:
                    self.file_metadata[key]['n_fragments'] = n_frags_allowed - n_removed
                    self.cache[key] = values[:n_frags_allowed - n_removed]

    def is_in_cache(self, key):
        return key in self.cache

    def clear(self):
        self.cache = {}
        self.file_metadata = {}
        self.total_count = 0

    def get_from_cache(self, key):
        self.total_count += 1
        if key in self.file_metadata:
            self.file_metadata[key]["count"] += 1
        if self.is_in_cache(key):
            return self.cache[key]
        else:
            self.file_metadata[key] = {"count": 1, "n_fragments": 0}
            return []
