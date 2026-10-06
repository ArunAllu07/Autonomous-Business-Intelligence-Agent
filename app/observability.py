import logging
import time
import uuid
from contextlib import contextmanager
from typing import Any


# ============================================================
# Logging Configuration
# ============================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

logger = logging.getLogger("AURA")


def configure_logging() -> None:
    """
    Configure application-wide logging.
    """

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
    )


# ============================================================
# Request IDs
# ============================================================

def create_request_id() -> str:
    """
    Generate a unique request ID.
    """

    return str(uuid.uuid4())


# ============================================================
# Generic Event Logging
# ============================================================

def log_event(
    event: str,
    request_id: str,
    **details: Any,
) -> None:
    """
    Log a structured AURA event.

    Example:

        log_event(
            "AGENT_SELECTED",
            request_id,
            agent="sql_agent",
        )
    """

    formatted_details = " | ".join(
        f"{key}={value}"
        for key, value in details.items()
    )

    if formatted_details:

        logger.info(
            "[%s] %s | %s",
            request_id,
            event,
            formatted_details,
        )

    else:

        logger.info(
            "[%s] %s",
            request_id,
            event,
        )


# ============================================================
# Operation Tracing
# ============================================================

@contextmanager
def trace_operation(
    operation: str,
    request_id: str,
    **metadata: Any,
):
    """
    Measure the execution time of an operation.

    Logs:

        START
        END
        FAILED

    Returns elapsed time through logging metadata.
    """

    start_time = time.perf_counter()

    log_event(
        "OPERATION_START",
        request_id,
        operation=operation,
        **metadata,
    )

    try:

        yield

        elapsed = (
            time.perf_counter()
            - start_time
        )

        log_event(
            "OPERATION_END",
            request_id,
            operation=operation,
            duration_ms=round(
                elapsed * 1000,
                2,
            ),
            status="success",
        )

    except Exception as error:

        elapsed = (
            time.perf_counter()
            - start_time
        )

        logger.exception(
            "[%s] OPERATION_FAILED | "
            "operation=%s | "
            "duration_ms=%.2f | "
            "error=%s",
            request_id,
            operation,
            elapsed * 1000,
            error,
        )

        raise


# ============================================================
# Agent Tracing
# ============================================================

def log_agent_start(
    request_id: str,
    agent_name: str,
) -> None:
    """
    Record the beginning of an agent execution.
    """

    log_event(
        "AGENT_START",
        request_id,
        agent=agent_name,
    )


def log_agent_end(
    request_id: str,
    agent_name: str,
    duration_ms: float | None = None,
) -> None:
    """
    Record successful agent completion.
    """

    details: dict[str, Any] = {
        "agent": agent_name,
        "status": "success",
    }

    if duration_ms is not None:

        details["duration_ms"] = round(
            duration_ms,
            2,
        )

    log_event(
        "AGENT_END",
        request_id,
        **details,
    )


def log_agent_error(
    request_id: str,
    agent_name: str,
    error: Exception,
) -> None:
    """
    Record an agent failure.
    """

    logger.error(
        "[%s] AGENT_ERROR | "
        "agent=%s | "
        "error=%s",
        request_id,
        agent_name,
        error,
    )


# ============================================================
# Tool Tracing
# ============================================================

def log_tool_start(
    request_id: str,
    tool_name: str,
) -> None:
    """
    Record the beginning of a tool execution.
    """

    log_event(
        "TOOL_START",
        request_id,
        tool=tool_name,
    )


def log_tool_end(
    request_id: str,
    tool_name: str,
    duration_ms: float | None = None,
    source: str | None = None,
) -> None:
    """
    Record successful tool execution.
    """

    details: dict[str, Any] = {
        "tool": tool_name,
        "status": "success",
    }

    if duration_ms is not None:

        details["duration_ms"] = round(
            duration_ms,
            2,
        )

    if source is not None:

        details["source"] = source

    log_event(
        "TOOL_END",
        request_id,
        **details,
    )


def log_tool_error(
    request_id: str,
    tool_name: str,
    error: Exception,
) -> None:
    """
    Record a tool failure.
    """

    logger.error(
        "[%s] TOOL_ERROR | "
        "tool=%s | "
        "error=%s",
        request_id,
        tool_name,
        error,
    )


# ============================================================
# Cache Observability
# ============================================================

def log_cache_hit(
    request_id: str,
    cache_type: str,
) -> None:
    """
    Record a Redis cache hit.
    """

    log_event(
        "CACHE_HIT",
        request_id,
        cache_type=cache_type,
    )


def log_cache_miss(
    request_id: str,
    cache_type: str,
) -> None:
    """
    Record a Redis cache miss.
    """

    log_event(
        "CACHE_MISS",
        request_id,
        cache_type=cache_type,
    )


# ============================================================
# Memory Observability
# ============================================================

def log_memory_event(
    request_id: str,
    event: str,
    session_id: str,
    messages: int | None = None,
) -> None:
    """
    Record Redis/session-memory activity.
    """

    details: dict[str, Any] = {
        "session_id": session_id,
    }

    if messages is not None:

        details["messages"] = messages

    log_event(
        event,
        request_id,
        **details,
    )


# ============================================================
# Evaluation Observability
# ============================================================

def log_evaluation(
    request_id: str,
    score: float,
    passed: bool,
    attempt: int,
) -> None:
    """
    Record critic/evaluation information.
    """

    log_event(
        "EVALUATION",
        request_id,
        score=score,
        passed=passed,
        attempt=attempt,
    )


# ============================================================
# Request Completion
# ============================================================

def log_request_completion(
    request_id: str,
    session_id: str | None,
    duration_ms: float,
    status_code: int,
) -> None:
    """
    Record final request statistics.
    """

    log_event(
        "REQUEST_COMPLETED",
        request_id,
        session_id=session_id,
        duration_ms=round(
            duration_ms,
            2,
        ),
        status_code=status_code,
    )