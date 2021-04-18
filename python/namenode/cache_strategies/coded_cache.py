from expiringdict import ExpiringDict
import os
from measurement_session import get_settings
from collections import deque
from enum import enum

class Tier(Enum):
    A_TIER = 5
    B_TIER = 4
    C_TIER = 3
    D_TIER = 2
    E_TIER = 1

class CodedCache:
    file_counts = deque()
    settings = get_settings()
    CACHE_SIZE = settings["cache_size"]
    N_FRAGMENTS = CACHE_SIZE // 5 
    A_TIER_SIZE = N_FRAGMENTS // 10 
    B_TIER_SIZE = N_FRAGMENTS // 8
    C_TIER_SIZE = N_FRAGMENTS // 5
    D_TIER_SIZE = N_FRAGMENTS // 3
    E_TIER_SIZE = N_FRAGMENTS
    TOTAL_SIZE = A_TIER_SIZE + B_TIER_SIZE + C_TIER_SIZE + D_TIER_SIZE + E_TIER_SIZE

    A_TIER_THRESHOLD = 100 - A_TIER_SIZE / TOTAL_SIZE * 100
    B_TIER_THRESHOLD = A_TIER_THRESHOLD - B_TIER_SIZE / TOTAL_SIZE * 100
    C_TIER_THRESHOLD = B_TIER_THRESHOLD - C_TIER_SIZE / TOTAL_SIZE * 100
    D_TIER_THRESHOLD = C_TIER_THRESHOLD - D_TIER_SIZE / TOTAL_SIZE * 100
    
    tier_a = {}
    tier_b = {}
    tier_c = {}
    tier_d = {}
    tier_e = {}

    def add_to_cache(self, key, values):
        current_tier = self.is_in_cache(key)
        if current_tier:
            earned_tier = determine_tier(key)
            if (self.is_higher_tier(current_tier, earned_tier))



        else:
            if len(self.cache) >= self.CACHE_SIZE:
                self.cache.pop(self.frequencies[self.threshold]["key"])
                del self.frequencies[self.threshold]
        
            self.cache[key] = value
            self.frequencies.append({"key": key, "freq": 1})

    def determine_tier(self, key):
        for i, elem in enumerate(self.file_counts)[:self.TOTAL_SIZE]:
            if elem["key"] == key:
                placement = 100 - i / self.TOTAL_SIZE * 100
                if placement > self.A_TIER_THRESHOLD:
                    return Tier.A_TIER
                elif placement > self.B_TIER_THRESHOLD:
                    return Tier.B_TIER
                elif placement > self.C_TIER_THRESHOLD:
                    return Tier.C_TIER
                elif placement > self.D_TIER_THRESHOLD:
                    return Tier.D_TIER
                else:
                    return Tier.E_TIER
        return None
    
    def is_higher_tier(self, current_tier, earned_tier):
        if (current_tier.value < earned_tier.value):
            return True
        return False

    def is_in_cache(self, key):
        if key in self.tier_a:
            return Tier.A_TIER
        elif key in self.tier_b:
            return Tier.B_TIER
        elif key in self.tier_c:
            return Tier.C_TIER
        elif key in self.tier_d:
            return Tier.D_TIER
        elif key in self.tier_e:
            return Tier.E_TIER

        return False
    
    def get_from_cache(self, key):
        
    
    #"file123": [frag1, frag2, frag3, frag4]

    cache = ExpiringDict(max_len=CACHE_SIZE, max_age_seconds=600)


