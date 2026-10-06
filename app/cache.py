import hashlib
import json
from typing import Any

from app.redis_client import (
    get_value,
    set_value,
    delete_value,
)


# ============================================================
# Cache Configuration
# ============================================================

DEFAULT_CACHE_TTL = 300  # 5 minutes


# ============================================================
# Key Generation
# ============================================================

def generate_cache_key(
    prefix: str,
    value: str,
) -> str:
    """
    Generate a deterministic Redis cache key.

    The actual query is hashed so that long or sensitive
    query text is not directly stored in the Redis key.
    """

    normalized_value = value.strip().lower()

    digest = hashlib.sha256(
        normalized_value.encode("utf-8")
    ).hexdigest()

    return f"aura:cache:{prefix}:{digest}"


# ============================================================
# Cache Read
# ============================================================

def get_cached_value(
    key: str,
) -> Any | None:
    """
    Retrieve a value from Redis cache.

    Returns None when the key does not exist or Redis
    is temporarily unavailable.
    """

    try:
        raw_value = get_value(key)

        if raw_value is None:
            return None

        return json.loads(raw_value)

    except (
        json.JSONDecodeError,
        TypeError,
        ValueError,
    ):
        return None


# ============================================================
# Cache Write
# ============================================================

def set_cached_value(
    key: str,
    value: Any,
    ttl: int = DEFAULT_CACHE_TTL,
) -> bool:
    """
    Store a value in Redis cache with TTL.
    """

    try:
        serialized_value = json.dumps(
            value,
            ensure_ascii=False,
        )

        return set_value(
            key,
            serialized_value,
            ttl,
        )

    except (
        TypeError,
        ValueError,
    ):
        return False


# ============================================================
# Cache Delete
# ============================================================

def delete_cached_value(
    key: str,
) -> bool:
    """
    Delete a cached value.
    """

    return delete_value(key)


# ============================================================
# Query Cache Helpers
# ============================================================

def get_cached_query(
    query: str,
) -> Any | None:
    """
    Retrieve a cached SQL/query result.
    """

    key = generate_cache_key(
        "query",
        query,
    )

    return get_cached_value(key)


def cache_query_result(
    query: str,
    result: Any,
    ttl: int = DEFAULT_CACHE_TTL,
) -> bool:
    """
    Cache the result of a query.
    """

    key = generate_cache_key(
        "query",
        query,
    )

    return set_cached_value(
        key,
        result,
        ttl,
    )


def clear_query_cache(
    query: str,
) -> bool:
    """
    Remove a specific query result from cache.
    """

    key = generate_cache_key(
        "query",
        query,
    )

    return delete_cached_value(key)