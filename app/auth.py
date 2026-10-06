import os
import secrets

from dotenv import load_dotenv
from fastapi import Header, HTTPException, status

load_dotenv()

AURA_API_KEY = os.getenv("AURA_API_KEY")


def verify_api_key(
    x_api_key: str | None = Header(default=None),
) -> None:
    """
    Verify the API key supplied by the client.

    The API key is read from the environment and is never
    returned in an error response.
    """

    if not AURA_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API authentication is not configured.",
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key.",
        )

    if not secrets.compare_digest(
        x_api_key,
        AURA_API_KEY,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )