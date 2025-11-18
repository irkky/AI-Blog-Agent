# app_logging/logger.py
import json
import os
import time
from typing import Any, Dict, Optional


LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
EVENT_LOG_PATH = os.path.join(LOG_DIR, "events.jsonl")


class AppLogger:
    """
    Very small JSONL logger for observability:
    - agent name
    - step
    - duration
    - tokens (if you add)
    - errors
    """

    def __init__(self, path: str = EVENT_LOG_PATH) -> None:
        self.path = path

    def log_event(
        self,
        *,
        event_type: str,
        agent: Optional[str] = None,
        step: Optional[str] = None,
        message: Optional[str] = None,
        duration_sec: Optional[float] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        record = {
            "ts": time.time(),
            "event_type": event_type,
            "agent": agent,
            "step": step,
            "message": message,
            "duration_sec": duration_sec,
            "extra": extra or {},
        }
        try:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            # fail-soft: don't crash if logging fails
            pass

    def log_error(self, agent: str, step: str, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        self.log_event(
            event_type="error",
            agent=agent,
            step=step,
            message=message,
            extra=extra,
        )


app_logger = AppLogger()

