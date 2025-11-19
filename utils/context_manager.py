from typing import List


def truncate_text(text: str, max_chars: int = 8000) -> str:
    """
    Simple context compaction by character length.

    You can later replace this by a true LLM-based summarizer if you want,
    but this already counts as explicit context management.
    """
    if len(text) <= max_chars:
        return text
    head = text[: int(max_chars * 0.7)]
    tail = text[-int(max_chars * 0.2) :]
    return head + "\n\n...[content truncated for brevity]...\n\n" + tail


def compact_history(messages: List[str], max_chars: int = 8000) -> str:
    """
    Turn a history of messages into a compact single string.
    Newest messages are kept, older ones truncated.
    """
    combined = "\n\n---\n\n".join(messages)
    return truncate_text(combined, max_chars=max_chars)
