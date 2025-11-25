import os
from diskcache import Cache
import time

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
SESSION_TRACKING_KEY = "_session_tracking"

class CacheManager:
    def __init__(self, size_limit_bytes=1024*1024*1024): # Default 1GB
        self.cache = Cache(CACHE_DIR, size_limit=size_limit_bytes)

    def get(self, key: str):
        data = self.cache.get(key)
        if data is None:
            return None
        
        # Handle legacy strings vs new dicts
        if isinstance(data, dict) and "content" in data:
            # Increment access count
            data["access_count"] = data.get("access_count", 0) + 1
            # Update cache without resetting TTL (if possible, else just set)
            self.cache.set(key, data)
            return data["content"]
        return data

    def set(self, key: str, value: str, expire: int = None):
        # Check if exists to preserve access count
        existing = self.cache.get(key)
        access_count = 0
        timestamp = time.time()
        
        if isinstance(existing, dict) and "access_count" in existing:
            access_count = existing["access_count"]
            # Keep original timestamp? Or update? Usually update on set.
            # But if it's a "new" set, maybe reset? 
            # If the content is identical, we might want to keep stats?
            # But set() usually implies overwriting.
            # Let's reset access count on overwrite? Or keep it?
            # User wants to see "access count". If I overwrite, it's a new entry.
            # But in chat.py, we set() every time we generate.
            # If we generate, it means it wasn't in cache (or we forced it).
            # If it wasn't in cache, access_count starts at 0.
            # If it WAS in cache, chat.py calls get() first.
            # So set() is only called on MISS.
            # So access_count should be 0 (or 1 since we just accessed it to create it?)
            pass

        # Store with metadata
        data = {
            "content": value,
            "timestamp": timestamp,
            "access_count": access_count
        }
        self.cache.set(key, data, expire=expire)

    def clear(self):
        self.cache.clear()

    def set_size_limit(self, size_limit_bytes: int):
        # diskcache allows updating size_limit dynamically
        self.cache.size_limit = size_limit_bytes
        # Trigger cull to enforce new limit immediately if needed
        self.cache.cull()

    def check_and_enforce_limit(self):
        """
        Explicitly check if cache size exceeds limit and cull if necessary.
        This ensures old items are deleted when the limit is reached.
        """
        # diskcache usually handles this automatically on set(), but we can force it
        if self.cache.size > self.cache.size_limit:
            self.cache.cull()

    def stats(self):
        # diskcache doesn't have a direct 'hit_rate' metric built-in easily without tracking,
        # but we can return size and volume.
        try:
            cached_sessions_count = len(self.get_cached_sessions())
        except Exception:
            cached_sessions_count = 0
        
        try:
            size_bytes = int(self.cache.size)
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
            "cached_sessions": cached_sessions_count,
            "size_limit_bytes": self.cache.size_limit
        }

    def get_size_limit(self):
        return self.cache.size_limit

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
        """
        Remove cache from oldest sessions if limit is exceeded.
        """
        try:
            cached_sessions = self.get_cached_sessions()
            if len(cached_sessions) > max_sessions:
                # Calculate how many to remove
                num_to_remove = len(cached_sessions) - max_sessions
                sessions_to_remove = cached_sessions[:num_to_remove] # Oldest first
                
                session_tracking = self.cache.get(SESSION_TRACKING_KEY, {})
                
                for session_id, _ in sessions_to_remove:
                    # 1. Remove from tracking
                    if session_id in session_tracking:
                        del session_tracking[session_id]
                    
                    # 2. Remove actual cache items for this session
                    # Iterate all keys and find those starting with session_id
                    keys_to_delete = []
                    for key in self.cache:
                        try:
                            if isinstance(key, str) and key.startswith(f"{session_id}:"):
                                keys_to_delete.append(key)
                        except:
                            continue
                    
                    for key in keys_to_delete:
                        self.cache.delete(key)
                
                # Update tracking
                self.cache.set(SESSION_TRACKING_KEY, session_tracking)
        except Exception as e:
            print(f"Error cleaning up old sessions: {e}")

    def clear_session_cache(self, session_id: str):
        """
        Delete all cache entries for a specific session.
        NOTE: With global caching, we cannot delete 'session' cache without affecting others.
        This function is now effectively a no-op for global keys, or we could implement 
        a way to track which sessions used which global keys (ref counting), but that's complex.
        For now, we'll leave it as a no-op or just clear session tracking.
        """
        try:
            # Remove from session tracking
            session_tracking = self.cache.get(SESSION_TRACKING_KEY, {})
            if session_id in session_tracking:
                del session_tracking[session_id]
                self.cache.set(SESSION_TRACKING_KEY, session_tracking)
        except Exception:
            pass

    def get_all_items(self):
        """Get all items in the cache."""
        items = []
        try:
            for key in self.cache:
                try:
                    # Use direct access to avoid triggering our get() wrapper which increments access_count
                    data = self.cache[key]
                    
                    # Handle binary keys
                    if isinstance(key, bytes):
                        key_str = key.decode('utf-8', errors='ignore')
                    else:
                        key_str = str(key)
                        
                    # Skip internal keys
                    if key_str == SESSION_TRACKING_KEY:
                        continue

                    value_str = ""
                    timestamp = time.time() # Default fallback
                    access_count = 0

                    # Handle new dict format vs legacy
                    if isinstance(data, dict) and "content" in data:
                        value = data["content"]
                        timestamp = data.get("timestamp", timestamp)
                        access_count = data.get("access_count", 0)
                    else:
                        value = data
                    
                    # Handle binary values in content
                    if isinstance(value, bytes):
                        try:
                            value_str = value.decode('utf-8')
                        except:
                            value_str = f"<Binary Data: {len(value)} bytes>"
                    else:
                        value_str = str(value)
                        
                    items.append({
                        "key": key_str,
                        "value": value_str,
                        "store_time": timestamp,
                        "access_count": access_count
                    })
                except Exception:
                    continue
        except Exception:
            pass
        return items

cache_manager = CacheManager()
