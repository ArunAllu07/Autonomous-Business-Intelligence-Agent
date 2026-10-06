import json
import re
from datetime import datetime
from typing import Any

from app.redis_client import (
    get_value,
    set_value,
    delete_value,
)


# Redis configuration
SESSION_TTL = 60 * 60 * 24  # 24 hours
MAX_RECENT_MESSAGES = 20


def _session_key(session_id: str) -> str:
    """Generate Redis key for a conversation session."""
    return f"aura:session:{session_id}"


def _load_session(session_id: str) -> list[dict[str, Any]]:
    """Load short-term conversation memory from Redis."""
    try:
        raw_data = get_value(_session_key(session_id))

        if not raw_data:
            return []

        data = json.loads(raw_data)

        if not isinstance(data, list):
            return []

        return data

    except (json.JSONDecodeError, TypeError, ValueError):
        return []


def _save_session(
    session_id: str,
    messages: list[dict[str, Any]],
) -> bool:
    """Save short-term conversation memory to Redis."""

    # Keep only the most recent messages
    messages = messages[-MAX_RECENT_MESSAGES:]

    try:
        return set_value(
            _session_key(session_id),
            json.dumps(messages, ensure_ascii=False),
            SESSION_TTL,
        )
    except (TypeError, ValueError):
        return False


def add_session_message(
    session_id: str,
    role: str,
    content: str,
) -> bool:
    """
    Add a message to the user's short-term Redis memory.
    """

    if not session_id or not content:
        return False

    messages = _load_session(session_id)

    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat(),
    }

    messages.append(message)

    return _save_session(session_id, messages)


def get_session_messages(
    session_id: str,
) -> list[dict[str, Any]]:
    """Return recent conversation messages."""

    if not session_id:
        return []

    return _load_session(session_id)


def clear_session(session_id: str) -> bool:
    """Delete a conversation session from Redis."""

    if not session_id:
        return False

    return delete_value(_session_key(session_id))


def get_session_count(session_id: str) -> int:
    """Return number of messages stored in a session."""

    return len(get_session_messages(session_id))


def get_recent_context(
    session_id: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """
    Return the most recent messages for agent context.
    """

    messages = get_session_messages(session_id)

    if limit <= 0:
        return []

    return messages[-limit:]


def format_recent_context(
    session_id: str,
    limit: int = 10,
) -> str:
    """
    Convert recent Redis memory into text that can be
    passed to an agent.
    """

    messages = get_recent_context(session_id, limit)

    if not messages:
        return ""

    formatted = []

    for message in messages:
        role = message.get("role", "unknown")
        content = message.get("content", "")

        formatted.append(
            f"{role.upper()}: {content}"
        )

    return "\n".join(formatted)


# -------------------------------------------------------------------
# Simple fact extraction
# -------------------------------------------------------------------

def extract_facts(text: str) -> dict[str, str]:
    """
    Extract simple user facts from conversation text.

    This is intentionally conservative.
    """

    if not text:
        return {}

    facts: dict[str, str] = {}

    patterns = {
        "name": [
            r"\bmy name is ([A-Za-z][A-Za-z ]{1,50})",
            r"\bi am ([A-Za-z][A-Za-z ]{1,50})",
        ],
        "college": [
            r"\bi study at ([A-Za-z0-9 .&'-]{2,100})",
            r"\bi am studying at ([A-Za-z0-9 .&'-]{2,100})",
        ],
        "role": [
            r"\bi work as ([A-Za-z0-9 .&'-]{2,100})",
            r"\bi am working as ([A-Za-z0-9 .&'-]{2,100})",
        ],
    }

    for fact_name, regex_list in patterns.items():

        for pattern in regex_list:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE,
            )

            if match:
                value = match.group(1).strip()

                if value:
                    facts[fact_name] = value

                break

    return facts


# -------------------------------------------------------------------
# Redis health
# -------------------------------------------------------------------

def redis_memory_available() -> bool:
    """
    Check whether Redis-backed memory is available.
    """

    try:
        from app.redis_client import check_redis_connection

        return check_redis_connection()

    except Exception:
        return False