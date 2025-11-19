from typing import Literal, Optional

from google.adk.tools.function_tool import FunctionTool

from memory.memory_bank import memory_bank
from memory.session_service import session_service


class UserProfileTool(FunctionTool):
    def __init__(self):
        super().__init__(self._manage_profile)
        self.name = "user_profile_tool"
        self.description = (
            "Stores and retrieves user writing preferences, tone, audience, and history."
        )

    def _manage_profile(
        self,
        action: Literal["get", "set", "append"],
        key: str,
        value: Optional[str] = None,
        session_id: str = "default_session",
    ) -> str:
        """
        Manage persistent user preferences.

        Args:
            action: Operation to perform - one of get, set, append.
            key: Preference key (e.g., tone, audience).
            value: Optional value used by set/append.
            session_id: Session identifier for overrides.
        """
        key = (key or "").strip()
        if not action or not key:
            return "Error: 'action' and 'key' fields are required."

        action = action.lower()
        session_id = session_id or "default_session"

        if action == "get":
            ses_val = session_service.get(session_id, key)
            if ses_val is not None:
                return str(ses_val)
            val = memory_bank.get(key)
            return str(val) if val is not None else "None"

        if action == "set":
            memory_bank.set(key, value)
            session_service.set(session_id, key, value)
            return f"Stored {key} = {value}"

        if action == "append":
            memory_bank.append_to_list(key, value)
            return f"Appended to {key}: {value}"

        return "Error: Invalid action. Must be 'get', 'set', or 'append'."
