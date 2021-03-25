from measurement_session import get_settings


class SimpleCache: 
    settings = get_settings()
    CACHE_SIZE = settings["cache_size"]

    cache = {}

    def add_to_cache(self, key, value):
        if not self.is_in_cache(key):
            self.cache[key] = value

    def is_in_cache(self, key):
        return key in self.cache

    def get_from_cache(self, key):
        if self.is_in_cache(key):
            return self.cache[key]
        else:
            return None

    def clear(self):
        self.settings = get_settings()
        self.CACHE_SIZE = self.settings["cache_size"]
        self.cache = {}
