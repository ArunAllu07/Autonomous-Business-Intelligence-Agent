import logging
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agents import Runner
from agents.exceptions import InputGuardrailTripwireTriggered

from app.model_config import model
from app.orchestrator import create_orchestrator
from app.memory import add_memory
from app.memory_manager import (
    add_session_message,
    get_recent_context,
)
from app.observability import (
    configure_logging,
    create_request_id,
    trace_operation,
    log_event,
)
from app.mcp_server import create_mcp_server


# ============================================================
# Configuration
# ============================================================

MAX_MESSAGE_LENGTH = 4000
MAX_CONTEXT_MESSAGES = 10

logger = logging.getLogger("AURA.API")

configure_logging()


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="AURA API",
    description="Autonomous Business Intelligence Agent",
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


# ============================================================
# Request / Response Models
# ============================================================

class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=MAX_MESSAGE_LENGTH,
    )

    session_id: str | None = Field(
        default=None,
        max_length=100,
    )


class ChatResponse(BaseModel):
    response: str
    session_id: str
    request_id: str


# ============================================================
# Application State
# ============================================================

mcp_server = None
orchestrator = None


# ============================================================
# Startup / Shutdown
# ============================================================

@app.on_event("startup")
async def startup_event():

    global mcp_server
    global orchestrator

    logger.info("Starting AURA API...")

    try:
        mcp_server = create_mcp_server()

        orchestrator = create_orchestrator(
            mcp_server=mcp_server
        )

        logger.info("AURA orchestrator initialized successfully.")

    except Exception:

        logger.exception(
            "Failed to initialize AURA orchestrator."
        )

        raise


@app.on_event("shutdown")
async def shutdown_event():

    logger.info("Shutting down AURA API...")


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "service": "AURA",
        "version": "1.0.0",
    }


# ============================================================
# Chat Endpoint
# ============================================================

@app.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest):

    request_id = create_request_id()

    # --------------------------------------------------------
    # Generate / validate session
    # --------------------------------------------------------

    session_id = request.session_id

    if not session_id:
        session_id = str(uuid.uuid4())

    log_event(
        "CHAT_REQUEST",
        request_id,
        session_id=session_id,
    )

    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    message = request.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    if len(message) > MAX_MESSAGE_LENGTH:

        raise HTTPException(
            status_code=400,
            detail="Message exceeds the maximum allowed length.",
        )

    # --------------------------------------------------------
    # Load Redis short-term memory
    # --------------------------------------------------------

    try:

        recent_context = get_recent_context(
            session_id=session_id,
            limit=MAX_CONTEXT_MESSAGES,
        )

        log_event(
            "REDIS_MEMORY_LOADED",
            request_id,
            session_id=session_id,
            messages=len(recent_context),
        )

    except Exception as exc:

        logger.warning(
            "[%s] Redis memory retrieval failed: %s",
            request_id,
            exc,
        )

        recent_context = []

    # --------------------------------------------------------
    # Build contextual message
    # --------------------------------------------------------

    if recent_context:

        context_lines = []

        for item in recent_context:

            role = item.get(
                "role",
                "unknown",
            )

            content = item.get(
                "content",
                "",
            )

            context_lines.append(
                f"{role.upper()}: {content}"
            )

        conversation_context = "\n".join(
            context_lines
        )

        contextual_message = f"""
Previous conversation context:

{conversation_context}

Current user message:

{message}
"""

    else:

        contextual_message = message

    # --------------------------------------------------------
    # Save user message to Redis
    # --------------------------------------------------------

    try:

        add_session_message(
            session_id=session_id,
            role="user",
            content=message,
        )

        log_event(
            "USER_MESSAGE_STORED",
            request_id,
            session_id=session_id,
        )

    except Exception as exc:

        logger.warning(
            "[%s] Failed to store user message in Redis: %s",
            request_id,
            exc,
        )

    # --------------------------------------------------------
    # Run AURA
    # --------------------------------------------------------

    if orchestrator is None:

        logger.error(
            "[%s] Orchestrator is not initialized.",
            request_id,
        )

        raise HTTPException(
            status_code=503,
            detail="AURA service is not ready.",
        )

    try:

        with trace_operation(
            "orchestrator",
            request_id,
        ):

            result = await Runner.run(
                orchestrator,
                contextual_message,
            )

    except InputGuardrailTripwireTriggered:

        logger.warning(
            "[%s] Input guardrail triggered.",
            request_id,
        )

        raise HTTPException(
            status_code=400,
            detail="The request was blocked by AURA safety controls.",
        )

    except Exception as exc:

        logger.exception(
            "[%s] Orchestrator execution failed.",
            request_id,
        )

        error_text = str(exc).lower()

        if (
            "connection" in error_text
            or "timeout" in error_text
            or "api" in error_text
        ):

            raise HTTPException(
                status_code=503,
                detail="AURA's model service is temporarily unavailable.",
            )

        raise HTTPException(
            status_code=500,
            detail="AURA could not complete the request.",
        )

    # --------------------------------------------------------
    # Extract response
    # --------------------------------------------------------

    response_text = getattr(
        result,
        "final_output",
        None,
    )

    if not response_text:

        logger.error(
            "[%s] Empty response from orchestrator.",
            request_id,
        )

        raise HTTPException(
            status_code=502,
            detail="AURA returned an empty response.",
        )

    response_text = str(
        response_text
    ).strip()

    # --------------------------------------------------------
    # Store assistant response in Redis
    # --------------------------------------------------------

    try:

        add_session_message(
            session_id=session_id,
            role="assistant",
            content=response_text,
        )

        log_event(
            "ASSISTANT_MESSAGE_STORED",
            request_id,
            session_id=session_id,
        )

    except Exception as exc:

        logger.warning(
            "[%s] Failed to store assistant message in Redis: %s",
            request_id,
            exc,
        )

    # --------------------------------------------------------
    # Existing long-term memory
    # --------------------------------------------------------

    try:

        add_memory(
            role="user",
            content=message,
            memory_type="conversation",
        )

        add_memory(
            role="assistant",
            content=response_text,
            memory_type="conversation",
        )

        log_event(
            "LONG_TERM_MEMORY_UPDATED",
            request_id,
            session_id=session_id,
        )

    except Exception as exc:

        logger.warning(
            "[%s] Long-term memory persistence failed: %s",
            request_id,
            exc,
        )

    # --------------------------------------------------------
    # Final logging
    # --------------------------------------------------------

    log_event(
        "CHAT_COMPLETED",
        request_id,
        session_id=session_id,
    )

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        request_id=request_id,
    )