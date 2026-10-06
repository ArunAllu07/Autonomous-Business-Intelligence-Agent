import logging
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agents import Runner

from app.orchestrator import create_orchestrator
from app.sql_agent import sql_agent

from app.memory_manager import (
    format_recent_context,
    add_session_message,
)

from app.observability import (
    trace_operation,
    log_event,
)

from app.mcp_server import create_mcp_server


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("AURA_API")


# ============================================================
# FASTAPI APPLICATION
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
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


# ============================================================
# RESPONSE MODEL
# ============================================================

class ChatResponse(BaseModel):
    response: str
    session_id: str
    request_id: str


# ============================================================
# GLOBAL OBJECTS
# ============================================================

mcp_server = None
orchestrator = None


# ============================================================
# SQL FAST-PATH DETECTOR
# ============================================================

def is_obvious_sql_question(
    message: str,
) -> bool:
    """
    Detect simple database questions that should
    go directly to the SQL Agent.

    This avoids unnecessary LLM routing through
    the full orchestrator.
    """

    text = message.lower().strip()

    sql_patterns = [

        # Revenue
        "total revenue",
        "highest revenue",
        "lowest revenue",
        "highest revenue product",
        "highest revenue region",
        "revenue of",
        "revenue by region",
        "revenue by product",
        "regional revenue",

        # Cost
        "total cost",
        "cost of",
        "cost by region",
        "cost by product",

        # Profit
        "total profit",
        "highest profit",
        "lowest profit",
        "most profitable",
        "least profitable",
        "most profitable product",
        "most profitable region",
        "profit of",
        "profit by region",
        "profit by product",
        "regional profit",

        # Sales
        "how many sales",
        "sales by region",
        "sales by product",

        # Database
        "how many records",
        "sales table",
        "columns in the sales table",
        "schema of the sales table",
    ]

    return any(
        pattern in text
        for pattern in sql_patterns
    )


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup_event():

    global mcp_server
    global orchestrator

    try:

        logger.info(
            "Starting AURA API..."
        )

        # ----------------------------------------------------
        # MCP SERVER
        # ----------------------------------------------------

        mcp_server = create_mcp_server()

        logger.info(
            "MCP server initialized successfully."
        )

        # ----------------------------------------------------
        # ORCHESTRATOR
        # ----------------------------------------------------

        orchestrator = create_orchestrator(
            mcp_server
        )

        logger.info(
            "AURA orchestrator initialized successfully."
        )

    except Exception as exc:

        logger.exception(
            "Failed to initialize AURA: %s",
            exc,
        )

        raise


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "service": "AURA",
        "version": "1.0.0",
    }


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
):

    # ========================================================
    # REQUEST ID
    # ========================================================

    request_id = str(
        uuid.uuid4()
    )

    # ========================================================
    # SESSION ID
    # ========================================================

    session_id = (
        request.session_id
        if request.session_id
        else str(uuid.uuid4())
    )

    # ========================================================
    # USER MESSAGE
    # ========================================================

    message = request.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    logger.info(
        "[%s] CHAT_REQUEST | session=%s",
        request_id,
        session_id,
    )

    log_event(
        "CHAT_REQUEST",
        request_id=request_id,
        session_id=session_id,
    )

    # ========================================================
    # LOAD SHORT-TERM MEMORY
    # ========================================================

    try:

        session_context = format_recent_context(
            session_id,
            limit=10,
        )

        logger.info(
            "[%s] REDIS_MEMORY_LOADED",
            request_id,
        )

    except Exception as exc:

        logger.warning(
            "[%s] Could not load session memory: %s",
            request_id,
            exc,
        )

        session_context = ""

    # ========================================================
    # BUILD CONTEXTUAL MESSAGE
    # ========================================================

    contextual_message = message

    if session_context:

        contextual_message = f"""
Previous conversation context:

{session_context}

Current user request:

{message}
""".strip()

    # ========================================================
    # STORE USER MESSAGE
    # ========================================================

    try:

        add_session_message(
            session_id=session_id,
            role="user",
            content=message,
        )

        logger.info(
            "[%s] USER_MESSAGE_STORED",
            request_id,
        )

    except Exception as exc:

        logger.warning(
            "[%s] Failed to store user message: %s",
            request_id,
            exc,
        )

    # ========================================================
    # SELECT AGENT
    # ========================================================

    use_sql_fast_path = (
        is_obvious_sql_question(message)
    )

    if use_sql_fast_path:

        selected_agent = sql_agent
        operation_name = "sql_agent_fast_path"

        logger.info(
            "[%s] SQL_FAST_PATH_SELECTED",
            request_id,
        )

    else:

        if orchestrator is None:

            logger.error(
                "[%s] Orchestrator is not initialized.",
                request_id,
            )

            raise HTTPException(
                status_code=503,
                detail="AURA orchestrator is not ready.",
            )

        selected_agent = orchestrator
        operation_name = "orchestrator"

        logger.info(
            "[%s] ORCHESTRATOR_PATH_SELECTED",
            request_id,
        )

    # ========================================================
    # RUN AGENT
    # ========================================================

    try:

        with trace_operation(
            operation_name,
            request_id,
        ):

            result = await Runner.run(
                selected_agent,
                contextual_message,
            )

    except Exception as exc:

        logger.exception(
            "[%s] AURA execution failed: %s",
            request_id,
            exc,
        )

        log_event(
            "CHAT_ERROR",
            request_id=request_id,
            session_id=session_id,
            error=str(exc),
        )

        raise HTTPException(
            status_code=500,
            detail="AURA failed to process the request.",
        )

    # ========================================================
    # EXTRACT FINAL RESPONSE
    # ========================================================

    response_text = getattr(
        result,
        "final_output",
        None,
    )

    if not response_text:

        logger.error(
            "[%s] Empty response from AURA.",
            request_id,
        )

        raise HTTPException(
            status_code=502,
            detail="AURA returned an empty response.",
        )

    response_text = str(
        response_text
    ).strip()

    # ========================================================
    # STORE ASSISTANT RESPONSE
    # ========================================================

    try:

        add_session_message(
            session_id=session_id,
            role="assistant",
            content=response_text,
        )

        logger.info(
            "[%s] ASSISTANT_MESSAGE_STORED",
            request_id,
        )

    except Exception as exc:

        logger.warning(
            "[%s] Failed to store assistant message: %s",
            request_id,
            exc,
        )

    # ========================================================
    # FINAL LOGGING
    # ========================================================

    logger.info(
        "[%s] CHAT_COMPLETED | path=%s",
        request_id,
        operation_name,
    )

    log_event(
        "CHAT_COMPLETED",
        request_id=request_id,
        session_id=session_id,
        operation=operation_name,
    )

    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        request_id=request_id,
    )