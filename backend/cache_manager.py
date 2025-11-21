import os
from diskcache import Cache

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")

class CacheManager:
    def __init__(self):
        self.cache = Cache(CACHE_DIR)

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value: str, expire: int = None):
        self.cache.set(key, value, expire=expire)

    def clear(self):
        self.cache.clear()

    def stats(self):
        # diskcache doesn't have a direct 'hit_rate' metric built-in easily without tracking,
        # but we can return size and volume.
        return {
            "size_bytes": self.cache.size,
            "count": len(self.cache)
        }

cache_manager = CacheManager()
