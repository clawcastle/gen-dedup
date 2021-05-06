from expiringdict import ExpiringDict
import os
from measurement_session import get_settings
from collections import deque
import json

class CodedCache:
    n_fragments = 0
    file_metadata = {}  # {count: 0, n_fragments: 0}
    cache = {}
    total_count = 0
    settings = get_settings()
    CACHE_SIZE = settings["cache_size"]
    THRESHOLD_FOR_SINGLE_FRAG = 100 / CACHE_SIZE

    def add_to_cache(self, key, values):
        if key not in self.file_metadata:
            self.file_metadata[key] = {"count": 0, "n_fragments": 0}

        if self.file_metadata[key]['n_fragments'] == 10:
            return

        if self.n_fragments < self.CACHE_SIZE:
            self.file_metadata[key]['n_fragments'] = self.file_metadata[key]['n_fragments'] + 1
            self.cache[key] = values[:self.file_metadata[key]['n_fragments']]
            self.n_fragments += 1
            return

        if self.is_in_cache(key):
            total = 0
            counts = []
            keys = []
            for k, v in self.cache.items():
                cache_val_count = self.file_metadata[k]["count"]
                total += cache_val_count
                counts.append(cache_val_count)
                keys.append(k)

            # Consider adding count to total

            ordered_keys = [keys for _, keys in sorted(zip(counts, keys), reverse=True)]

            potential_frags_to_remove = {}

            for k in ordered_keys:
                if k == key:
                    continue

                percentage = round(self.file_metadata[k]["count"] / total * 100, 5)
                if percentage < self.THRESHOLD_FOR_SINGLE_FRAG * self.file_metadata[k]["n_fragments"]:
                    adjusted_n_frags = percentage // self.THRESHOLD_FOR_SINGLE_FRAG
                    if adjusted_n_frags < self.file_metadata[k]["n_fragments"]:
                        potential_frags_to_remove[k] = int(self.file_metadata[k]["n_fragments"] - adjusted_n_frags)

                if percentage > self.THRESHOLD_FOR_SINGLE_FRAG * 10:
                    total = total - self.file_metadata[k]["count"] + int(
                        total / 100 * self.THRESHOLD_FOR_SINGLE_FRAG * 10)

            count = self.file_metadata[key]["count"]
            percentage = round(count / total * 100, 5)

            if percentage > self.THRESHOLD_FOR_SINGLE_FRAG * self.file_metadata[key]["n_fragments"]:
                adjusted_n_frags = 10 if percentage // self.THRESHOLD_FOR_SINGLE_FRAG > 10 else int(
                    percentage // self.THRESHOLD_FOR_SINGLE_FRAG)
                if adjusted_n_frags > self.file_metadata[key]["n_fragments"]:
                    frags_to_remove = adjusted_n_frags - self.file_metadata[key]["n_fragments"]

                    pftr_keys = list(potential_frags_to_remove.keys())
                    # random.shuffle(pftr_keys)
                    n_removed = 0
                    for _ in range(frags_to_remove):
                        if n_removed == frags_to_remove:
                            break

                        keys_to_remove = []
                        for k in pftr_keys:
                            v = potential_frags_to_remove[k]
                            if v <= frags_to_remove - n_removed:
                                if self.file_metadata[k]["n_fragments"] - v == 0:
                                    self.cache.pop(k)
                                    self.file_metadata[k]["n_fragments"] = 0
                                    keys_to_remove.append(k)
                                    n_removed += v
                                    break
                                else:
                                    self.cache[k] = self.cache[k][:self.file_metadata[k]["n_fragments"] - v]
                                    self.file_metadata[k]['n_fragments'] = self.file_metadata[k]["n_fragments"] - v
                                    n_removed += v
                                    keys_to_remove.append(k)
                                    break

                            else:
                                to_remove = frags_to_remove - n_removed
                                actual_n_frags = self.file_metadata[k]["n_fragments"] - to_remove
                                self.cache[k] = self.cache[k][:actual_n_frags]
                                self.file_metadata[k]['n_fragments'] = self.file_metadata[k]['n_fragments'] - to_remove
                                n_removed += to_remove
                                break

                        for k in keys_to_remove:
                            potential_frags_to_remove.pop(k)
                            pftr_keys.remove(k)

                    if n_removed != frags_to_remove:
                        actually_allowed = self.file_metadata[key]['n_fragments'] + n_removed
                        self.file_metadata[key]['n_fragments'] = actually_allowed
                        self.cache[key] = values[:actually_allowed]

                    else:
                        self.file_metadata[key]['n_fragments'] = adjusted_n_frags
                        self.cache[key] = values[:adjusted_n_frags]

        else:
            cache_keys = []
            percentages = []
            lowest_percentage = 100
            for k, v in self.cache.items():
                cache_val_count = self.file_metadata[k]["count"]
                percentage = round(cache_val_count / self.total_count * 100, 5)
                cache_keys.append(k)
                percentages.append(percentage)
                if percentage < lowest_percentage:
                    lowest_percentage = percentage

            percentage = round(self.file_metadata[key]["count"] / self.total_count * 100, 5)
            if percentage >= lowest_percentage:
                ordered_keys = [keys for _, keys in sorted(zip(percentages, cache_keys))]
                key_to_loose_a_frag = ordered_keys[0]

                if self.file_metadata[key_to_loose_a_frag]["n_fragments"] - 1 == 0:
                    self.cache.pop(key_to_loose_a_frag)
                    self.file_metadata[key_to_loose_a_frag]["n_fragments"] = 0
                else:
                    self.cache[key_to_loose_a_frag] = self.cache[key_to_loose_a_frag][
                                                      :self.file_metadata[key_to_loose_a_frag]["n_fragments"] - 1]
                    self.file_metadata[key_to_loose_a_frag]['n_fragments'] = self.file_metadata[key_to_loose_a_frag][
                                                                                 "n_fragments"] - 1

                self.file_metadata[key]['n_fragments'] = 1
                self.cache[key] = values[:1]

    def is_in_cache(self, key):
        return key in self.cache

    def clear(self):
        for key,val in self.file_metadata.items():
            print(f"fragment: {key}: count: {val['count']} n_frags: {val['n_fragments']}", flush=True)
        print(len([*self.cache]), flush=True)
        self.cache = {}
        self.settings = get_settings()
        self.CACHE_SIZE = self.settings["cache_size"]
        self.THRESHOLD_FOR_SINGLE_FRAG = 100 / self.CACHE_SIZE
        self.file_metadata = {}
        self.total_count = 0
        

    def get_from_cache(self, key):
        self.total_count += 1
        if key in self.file_metadata:
            self.file_metadata[key]["count"] += 1
            if self.is_in_cache(key):
                return self.cache[key]
            else:
                return []
        else:
            self.file_metadata[key] = {"count": 1, "n_fragments": 0}
            return []