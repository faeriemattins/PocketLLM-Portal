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
        try:
            cached_sessions_count = len(self.get_cached_sessions())
        except Exception:
            cached_sessions_count = 0
        
        try:
            size_bytes = int(self.cache.volume())
        except Exception:
            size_bytes = 0
        
        try:
            count = int(len(self.cache))
        except Exception:
            count = 0
        
        try:
            size_limit = int(self.cache.size_limit)
        except Exception:
            size_limit = 1073741824  # Default 1GB
        
        return {
            "size_bytes": size_bytes,
            "count": count,
            "size_limit": size_limit,
            "cached_sessions": cached_sessions_count
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
        try:
            session_tracking = self.cache.get(SESSION_TRACKING_KEY, {})
            if not isinstance(session_tracking, dict):
                return []
            # Sort by timestamp (oldest first)
            return sorted(session_tracking.items(), key=lambda x: x[1])
        except Exception:
            return []

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
        try:
            # Find all keys that start with session_id
            keys_to_delete = []
            for key in self.cache:
                try:
                    # Handle both string and byte keys
                    if isinstance(key, bytes):
                        key_str = key.decode('utf-8', errors='ignore')
                    elif isinstance(key, str):
                        key_str = key
                    else:
                        continue
                    
                    if key_str.startswith(f"{session_id}:"):
                        keys_to_delete.append(key)
                except Exception:
                    continue
            
            for key in keys_to_delete:
                try:
                    del self.cache[key]
                except Exception:
                    pass
            
            # Remove from session tracking
            session_tracking = self.cache.get(SESSION_TRACKING_KEY, {})
            if session_id in session_tracking:
                del session_tracking[session_id]
                self.cache.set(SESSION_TRACKING_KEY, session_tracking)
        except Exception:
            pass

cache_manager = CacheManager()
