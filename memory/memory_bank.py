from typing import Any, Dict, List
import threading


class MemoryBank:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._store: Dict[str, Any] = {}

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._store.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._store[key] = value

    def append_to_list(self, key: str, value: Any) -> None:
        with self._lock:
            current = self._store.get(key)
            if current is None:
                self._store[key] = [value]
            elif isinstance(current, list):
                current.append(value)
            else:
                # convert non-lists into list
                self._store[key] = [current, value]

    def all(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._store)


memory_bank = MemoryBank()
