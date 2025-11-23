import os
from diskcache import Cache
import time

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
SESSION_TRACKING_KEY = "_session_tracking"

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
            "count": len(self.cache),
            "size_limit": self.cache.size_limit,
            "cached_sessions": len(self.get_cached_sessions())
        }

    def get_size_limit(self):
        return self.cache.size_limit

    def set_size_limit(self, size_bytes: int):
        self.cache.size_limit = size_bytes

    def track_session_cache(self, session_id: str):
        """Track when a session uses cache by updating its last access time."""
        session_tracking = self.cache.get(SESSION_TRACKING_KEY, {})
        session_tracking[session_id] = time.time()
        self.cache.set(SESSION_TRACKING_KEY, session_tracking)

    def get_cached_sessions(self):
        """Get list of sessions with cached data, sorted by last access time."""
        session_tracking = self.cache.get(SESSION_TRACKING_KEY, {})
        # Sort by timestamp (oldest first)
        return sorted(session_tracking.items(), key=lambda x: x[1])

    def cleanup_old_sessions(self, max_sessions: int = 10):
        """Remove cache from oldest sessions if limit is exceeded."""
        sessions = self.get_cached_sessions()
        if len(sessions) > max_sessions:
            # Delete oldest sessions
            sessions_to_delete = sessions[:len(sessions) - max_sessions]
            for session_id, _ in sessions_to_delete:
                self.clear_session_cache(session_id)

    def clear_session_cache(self, session_id: str):
        """Delete all cache entries for a specific session."""
        # Find all keys that start with session_id
        keys_to_delete = [key for key in self.cache if isinstance(key, str) and key.startswith(f"{session_id}:")]
        for key in keys_to_delete:
            del self.cache[key]
        
        # Remove from session tracking
        session_tracking = self.cache.get(SESSION_TRACKING_KEY, {})
        if session_id in session_tracking:
            del session_tracking[session_id]
            self.cache.set(SESSION_TRACKING_KEY, session_tracking)

cache_manager = CacheManager()
