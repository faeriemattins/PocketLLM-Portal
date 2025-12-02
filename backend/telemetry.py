import time
from collections import deque
import threading

class TelemetryManager:
    def __init__(self):
        self._lock = threading.Lock()
        self.request_timestamps = deque(maxlen=1000)  # For QPS calculation
        self.latencies = deque(maxlen=100)
        self.total_requests = 0
        self.cache_hits = 0
        self.blocked_requests = 0
        self.total_tokens = 0
        self.start_time = time.time()

    def record_request(self):
        with self._lock:
            self.total_requests += 1
            self.request_timestamps.append(time.time())

    def record_latency(self, latency_ms):
        with self._lock:
            self.latencies.append(latency_ms)

    def record_cache_hit(self):
        with self._lock:
            self.cache_hits += 1

    def record_blocked(self):
        with self._lock:
            self.blocked_requests += 1

    def record_tokens(self, count):
        with self._lock:
            self.total_tokens += 1

    def get_stats(self):
        with self._lock:
            now = time.time()
            # Calculate QPS (requests in last 60 seconds)
            recent_requests = [t for t in self.request_timestamps if now - t <= 60]
            qps = len(recent_requests) / 60.0 if recent_requests else 0.0

            avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0
            
            hit_ratio = (self.cache_hits / self.total_requests * 100) if self.total_requests > 0 else 0
            
            uptime = now - self.start_time
            tokens_per_sec = self.total_tokens / uptime if uptime > 0 else 0

            return {
                "qps": round(qps, 2),
                "avg_latency_ms": round(avg_latency, 2),
                "cache_hit_ratio": round(hit_ratio, 2),
                "blocked_requests": self.blocked_requests,
                "total_requests": self.total_requests,
                "tokens_per_sec": round(tokens_per_sec, 2)
            }

telemetry_manager = TelemetryManager()
