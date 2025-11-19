from typing import Any, Dict
import threading


class SimpleSessionService:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def _ensure(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self._sessions:
            self._sessions[session_id] = {}
        return self._sessions[session_id]

    def get(self, session_id: str, key: str, default: Any = None) -> Any:
        with self._lock:
            session = self._sessions.get(session_id, {})
            return session.get(key, default)

    def set(self, session_id: str, key: str, value: Any) -> None:
        with self._lock:
            session = self._ensure(session_id)
            session[key] = value

    def dump(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {k: dict(v) for k, v in self._sessions.items()}


session_service = SimpleSessionService()
