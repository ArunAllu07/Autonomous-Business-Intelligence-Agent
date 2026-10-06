import time

from fastapi import HTTPException, status

from app.redis_client import redis_client


# Maximum requests allowed in the time window.
MAX_REQUESTS = 30
WINDOW_SECONDS = 60


def check_rate_limit(identifier: str) -> None:
    """
    Redis-backed fixed-window rate limiter.

    Allows MAX_REQUESTS within WINDOW_SECONDS for each identifier.
    """

    key = f"aura:rate_limit:{identifier}"

    try:
        current = redis_client.incr(key)

        if current == 1:
            redis_client.expire(
                key,
                WINDOW_SECONDS,
            )

        if current > MAX_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
            )

    except HTTPException:
        raise

    except Exception:
        # If Redis becomes unavailable, do not crash the API.
        # The application can continue operating.
        return