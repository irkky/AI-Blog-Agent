# tools/code_execution_tool.py
"""
CodeExecutionTool
-----------------

Executes small Python snippets in a restricted namespace.
"""

import traceback
from typing import Any, Dict

from google.adk.tools.function_tool import FunctionTool


class CodeExecutionTool(FunctionTool):
    def __init__(self):
        super().__init__(self._execute)
        self.name = "code_execution_tool"
        self.description = (
            "Executes sandboxed Python code and returns the value of `result`."
        )

    def _execute(self, code: str) -> str:
        """
        Execute trusted Python code.

        Args:
            code: Python snippet that assigns to a variable named `result`.
        """
        code = (code or "").strip()
        if not code:
            return "Error: 'code' field missing."

        restricted_globals = {
            "__builtins__": {
                "len": len,
                "range": range,
                "min": min,
                "max": max,
                "sum": sum,
                "abs": abs,
                "sorted": sorted,
                "float": float,
                "int": int,
                "str": str,
                "print": print,
            }
        }
        restricted_locals: Dict[str, Any] = {}

        try:
            exec(code, restricted_globals, restricted_locals)
        except Exception:
            return "Execution Error:\n" + traceback.format_exc()

        if "result" not in restricted_locals:
            return "Error: Code executed but no `result` variable was set."
        return str(restricted_locals["result"])
