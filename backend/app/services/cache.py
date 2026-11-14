from __future__ import annotations
import time
import threading
from collections import OrderedDict
from typing import Any, Optional

class TTLCache:
    def __init__(self, maxsize: int = 128, ttl: int = 120):
        self.maxsize, self.ttl = maxsize, ttl
        self.data = OrderedDict()
        self.lock = threading.Lock()
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            item = self.data.get(key)
            if not item:
                return None
            expiry, value = item
            if expiry < time.time():
                self.data.pop(key, None); return None
            self.data.move_to_end(key)
            return value
    def set(self, key: str, value: Any) -> None:
        with self.lock:
            self.data[key] = (time.time() + self.ttl, value)
            self.data.move_to_end(key)
            while len(self.data) > self.maxsize:
                self.data.popitem(last=False)
