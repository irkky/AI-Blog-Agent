from typing import Optional

from google.adk.tools.function_tool import FunctionTool
from google.genai import Client, types
from google.genai.types import GenerateContentConfig, Tool

MODEL_ID = "gemini-2.5-flash"


class GoogleSearchTool(FunctionTool):

    def __init__(self, model_id: str = MODEL_ID):
        self.model_id = model_id
        self._client_instance: Optional[Client] = None

        def google_search(query: str, *, fallback_summary: Optional[str] = None) -> str:
            return self._search(query=query, fallback_summary=fallback_summary)

        google_search.__name__ = "google_search"
        super().__init__(google_search)
        self.description = (
            "Performs a grounded Google Search and returns a concise summary."
        )
        self._tool_config = GenerateContentConfig(
            tools=[Tool(google_search=types.GoogleSearch())]
        )

    def _ensure_client(self) -> Client:
        if self._client_instance is None:
            self._client_instance = Client()
        return self._client_instance

    def _search(self, query: str, *, fallback_summary: Optional[str] = None) -> str:
        """
        Perform a grounded Google search.

        Args:
            query: Natural-language query the agent wants to research.
            fallback_summary: Optional text returned if the search response is empty.
        """
        query = (query or "").strip()
        if not query:
            return "Error: missing 'query' for google_search."

        try:
            response = self._ensure_client().models.generate_content(
                model=self.model_id,
                contents=query,
                config=self._tool_config,
            )
        except Exception as exc:
            return f"Google Search error: {exc}"

        parts: list[str] = []
        try:
            if getattr(response, "candidates", None):
                for candidate in response.candidates:
                    for part in getattr(candidate.content, "parts", []):
                        text = getattr(part, "text", "")
                        if text:
                            parts.append(text)
        except Exception:
            # Fall back to whatever the SDK serialized.
            parts = [getattr(response, "text", "")]

        parts = [p for p in parts if p]
        if parts:
            return "\n\n".join(parts)

        if fallback_summary:
            return fallback_summary

        return f"No search results or empty response for query: {query}"
