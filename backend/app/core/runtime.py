from __future__ import annotations
import time
from collections import defaultdict, deque
from typing import Deque, Dict

class RateLimiter:
    def __init__(self, limit: int, window: int):
        self.limit, self.window = limit, window
        self.hits: Dict[str, Deque[float]] = defaultdict(deque)
    def allow(self, key: str) -> bool:
        now = time.monotonic()
        q = self.hits[key]
        while q and q[0] < now - self.window:
            q.popleft()
        if len(q) >= self.limit:
            return False
        q.append(now)
        return True
