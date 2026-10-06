import ast
import json
import math
import operator
from pathlib import Path
from typing import Any

import chromadb
from dotenv import load_dotenv
from agents import function_tool

from app.cache import (
    get_cached_query,
    cache_query_result,
)
from app.database import get_connection
from app.guardrails import validate_sql


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CV_PATH = BASE_DIR / "data" / "ARUN_META_CV.pdf"
CHROMA_PATH = BASE_DIR / "data" / "chroma"

CV_COLLECTION_NAME = "aura_cv"


# ============================================================
# CHROMA / RAG
# ============================================================

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


def _get_cv_collection():
    """
    Get or create the CV vector collection.
    """

    return chroma_client.get_or_create_collection(
        name=CV_COLLECTION_NAME
    )


# ============================================================
# CALCULATOR
# ============================================================

_ALLOWED_BINARY_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def _safe_calculate_node(node: ast.AST) -> float:

    if isinstance(node, ast.Constant):

        if isinstance(node.value, (int, float)):

            if isinstance(node.value, bool):
                raise ValueError(
                    "Boolean values are not allowed."
                )

            return node.value

        raise ValueError(
            "Only numeric values are allowed."
        )

    if isinstance(node, ast.BinOp):

        operation = _ALLOWED_BINARY_OPERATORS.get(
            type(node.op)
        )

        if operation is None:
            raise ValueError(
                "Unsupported mathematical operator."
            )

        left = _safe_calculate_node(node.left)
        right = _safe_calculate_node(node.right)

        if isinstance(node.op, ast.Pow):

            if abs(right) > 100:
                raise ValueError(
                    "Exponent is too large."
                )

            if abs(left) > 1_000_000:
                raise ValueError(
                    "Base is too large."
                )

        return operation(left, right)

    if isinstance(node, ast.UnaryOp):

        operation = _ALLOWED_UNARY_OPERATORS.get(
            type(node.op)
        )

        if operation is None:
            raise ValueError(
                "Unsupported unary operator."
            )

        value = _safe_calculate_node(
            node.operand
        )

        return operation(value)

    raise ValueError(
        "Unsupported expression."
    )


@function_tool
def calculate(expression: str) -> str:
    """
    Safely calculate a mathematical expression.
    """

    if not expression or not expression.strip():
        return "Error: expression is empty."

    expression = expression.strip()

    if len(expression) > 500:
        return "Error: expression is too long."

    try:

        tree = ast.parse(
            expression,
            mode="eval",
        )

        result = _safe_calculate_node(
            tree.body
        )

        if not math.isfinite(result):
            return "Error: result is not finite."

        return str(result)

    except ZeroDivisionError:
        return "Error: division by zero."

    except Exception as error:
        return (
            "Error: invalid mathematical expression. "
            f"{error}"
        )


# ============================================================
# WEB SEARCH
# ============================================================

@function_tool
def web_search(query: str) -> str:
    """
    Search the web for current information.
    """

    if not query or not query.strip():
        return "Error: search query is empty."

    query = query.strip()

    if len(query) > 500:
        return "Error: search query is too long."

    try:

        try:
            from ddgs import DDGS

        except ImportError:

            try:
                from duckduckgo_search import DDGS

            except ImportError:

                return (
                    "Web search is unavailable because "
                    "the search package is not installed."
                )

        results = []

        with DDGS() as ddgs:

            search_results = ddgs.text(
                query,
                max_results=5,
            )

            for item in search_results:

                if not isinstance(item, dict):
                    continue

                results.append(
                    {
                        "title": item.get(
                            "title",
                            "",
                        ),
                        "url": item.get(
                            "href",
                            item.get(
                                "url",
                                "",
                            ),
                        ),
                        "snippet": item.get(
                            "body",
                            item.get(
                                "snippet",
                                "",
                            ),
                        ),
                    }
                )

        if not results:
            return (
                "No reliable search results were found."
            )

        return json.dumps(
            results,
            ensure_ascii=False,
            indent=2,
        )

    except Exception:
        return (
            "Web search failed. "
            "Please try again later."
        )


# ============================================================
# CV / RAG RETRIEVAL
# ============================================================

@function_tool
def retrieve_cv(query: str) -> str:
    """
    Retrieve relevant information from Arun's CV.
    """

    if not query or not query.strip():
        return "Error: CV query is empty."

    query = query.strip()

    if len(query) > 500:
        return "Error: CV query is too long."

    try:

        collection = _get_cv_collection()

        count = collection.count()

        if count == 0:
            return (
                "CV knowledge base is empty. "
                "Please run the ingestion process first."
            )

        results = collection.query(
            query_texts=[query],
            n_results=min(5, count),
        )

        documents = results.get(
            "documents",
            [],
        )

        if not documents or not documents[0]:
            return (
                "No relevant CV information was found."
            )

        formatted_results = []

        for index, document in enumerate(
            documents[0],
            start=1,
        ):

            formatted_results.append(
                f"[CV Result {index}]\n{document}"
            )

        return "\n\n".join(
            formatted_results
        )

    except Exception as error:

        return (
            "CV retrieval failed. "
            f"Reason: {error}"
        )


# ============================================================
# LONG-TERM MEMORY
# ============================================================

@function_tool
def save_memory(
    content: str,
    memory_type: str = "conversation",
) -> str:
    """
    Save information into long-term memory.
    """

    if not content or not content.strip():
        return "Error: memory content is empty."

    content = content.strip()

    if len(content) > 5000:
        return "Error: memory content is too long."

    try:

        from app.memory import add_memory

        saved = add_memory(
            role="system",
            content=content,
            memory_type=memory_type,
        )

        return json.dumps(
            saved,
            ensure_ascii=False,
        )

    except Exception:
        return "Unable to save memory."


@function_tool
def recall_memory(query: str) -> str:
    """
    Retrieve relevant long-term memory.
    """

    if not query or not query.strip():
        return "Error: memory query is empty."

    query = query.strip()

    if len(query) > 500:
        return "Error: memory query is too long."

    try:

        from app.memory import load_memory

        memories = load_memory()

        if not memories:
            return "No stored memories were found."

        query_terms = {
            word.lower()
            for word in query.split()
            if len(word) > 2
        }

        scored_memories = []

        for memory in memories:

            content = str(
                memory.get(
                    "content",
                    "",
                )
            )

            content_terms = {
                word.lower()
                for word in content.split()
                if len(word) > 2
            }

            score = len(
                query_terms.intersection(
                    content_terms
                )
            )

            if score > 0:
                scored_memories.append(
                    (
                        score,
                        memory,
                    )
                )

        scored_memories.sort(
            key=lambda item: item[0],
            reverse=True,
        )

        if not scored_memories:
            return (
                "No relevant memories were found."
            )

        selected = [
            memory
            for _, memory in scored_memories[:10]
        ]

        return json.dumps(
            selected,
            ensure_ascii=False,
            indent=2,
        )

    except Exception:
        return "Unable to retrieve memory."


# ============================================================
# EXPLICIT MEMORY SAVE
# ============================================================

@function_tool
def remember_information(
    content: str,
) -> str:
    """
    Explicitly save information requested by the user
    into AURA's long-term memory.
    """

    if not content or not content.strip():
        return "Error: information to remember is empty."

    content = content.strip()

    if len(content) > 5000:
        return "Error: information is too long."

    try:

        from app.memory import add_memory

        saved = add_memory(
            role="user",
            content=content,
            memory_type="explicit",
        )

        return json.dumps(
            saved,
            ensure_ascii=False,
        )

    except Exception:
        return (
            "Unable to save the requested information."
        )


# ============================================================
# DATABASE SCHEMA
# ============================================================

@function_tool
def get_database_schema() -> str:
    """
    Return the schema of the sales database.

    Supports SQLite and PostgreSQL.
    """

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        connection_module = (
            type(connection).__module__.lower()
        )

        is_postgres = (
            "psycopg" in connection_module
        )

        # ----------------------------------------------------
        # PostgreSQL
        # ----------------------------------------------------

        if is_postgres:

            cursor.execute(
                """
                SELECT
                    column_name,
                    data_type,
                    is_nullable
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'sales'
                ORDER BY ordinal_position
                """
            )

            rows = cursor.fetchall()

            if not rows:
                return (
                    "The sales table does not exist "
                    "or contains no schema information."
                )

            schema = []

            for column_name, data_type, nullable in rows:

                schema.append(
                    {
                        "column": column_name,
                        "type": data_type,
                        "nullable": nullable,
                    }
                )

            return json.dumps(
                schema,
                ensure_ascii=False,
                indent=2,
            )

        # ----------------------------------------------------
        # SQLite
        # ----------------------------------------------------

        cursor.execute(
            "PRAGMA table_info(sales)"
        )

        rows = cursor.fetchall()

        if not rows:
            return "The sales table was not found."

        schema = []

        for row in rows:

            schema.append(
                {
                    "column": row[1],
                    "type": row[2],
                    "nullable": not bool(row[3]),
                }
            )

        return json.dumps(
            schema,
            ensure_ascii=False,
            indent=2,
        )

    except Exception as error:

        return (
            "Unable to retrieve database schema. "
            f"Reason: {error}"
        )

    finally:

        if cursor is not None:

            try:
                cursor.close()
            except Exception:
                pass

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass


# ============================================================
# SQL RESULT FORMATTER
# ============================================================

def _rows_to_dicts(
    cursor,
    rows,
) -> list[dict[str, Any]]:
    """
    Convert database rows into JSON-safe dictionaries.
    """

    if not cursor.description:
        return []

    columns = [
        column[0]
        for column in cursor.description
    ]

    results = []

    for row in rows:

        result = {}

        for index, column in enumerate(columns):

            value = row[index]

            if (
                isinstance(
                    value,
                    (
                        str,
                        int,
                        float,
                        bool,
                    ),
                )
                or value is None
            ):

                result[column] = value

            else:

                result[column] = str(value)

        results.append(result)

    return results


# ============================================================
# SQL EXECUTION
# ============================================================

@function_tool
def execute_sql(sql: str) -> str:
    """
    Execute a strictly read-only SQL query.

    Supports PostgreSQL and SQLite.

    SQL is validated before execution.

    Redis is used as a cache for repeated queries.
    """

    if not sql or not sql.strip():
        return "Error: SQL query is empty."

    sql = sql.strip()

    if len(sql) > 5000:
        return (
            "Error: SQL query exceeds the "
            "maximum allowed length."
        )

    # --------------------------------------------------------
    # SQL VALIDATION
    # --------------------------------------------------------

    try:

        validated_sql = validate_sql(sql)

    except Exception as error:

        return json.dumps(
            {
                "success": False,
                "source": "validation",
                "error": "SQL validation failed.",
                "details": str(error),
            },
            ensure_ascii=False,
        )

    if not isinstance(
        validated_sql,
        str,
    ):

        return json.dumps(
            {
                "success": False,
                "source": "validation",
                "error": (
                    "SQL validator returned an "
                    "invalid result."
                ),
            },
            ensure_ascii=False,
        )

    validated_sql = validated_sql.strip()

    if not validated_sql:

        return json.dumps(
            {
                "success": False,
                "source": "validation",
                "error": "SQL query is empty after validation.",
            },
            ensure_ascii=False,
        )

    # --------------------------------------------------------
    # REDIS CACHE
    # --------------------------------------------------------

    try:

        cached_result = get_cached_query(
            validated_sql
        )

        if cached_result is not None:

            return json.dumps(
                {
                    "success": True,
                    "source": "redis_cache",
                    "data": cached_result,
                },
                ensure_ascii=False,
            )

    except Exception:

        # Cache failure should never prevent
        # database execution.
        pass

    # --------------------------------------------------------
    # DATABASE EXECUTION
    # --------------------------------------------------------

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            validated_sql
        )

        rows = cursor.fetchall()

        result = _rows_to_dicts(
            cursor,
            rows,
        )

        # ----------------------------------------------------
        # CACHE SUCCESSFUL RESULT
        # ----------------------------------------------------

        try:

            cache_query_result(
                validated_sql,
                result,
            )

        except Exception:
            pass

        return json.dumps(
            {
                "success": True,
                "source": "database",
                "data": result,
            },
            ensure_ascii=False,
        )

    except Exception as error:

        return json.dumps(
            {
                "success": False,
                "source": "database",
                "error": "Database query failed.",
                "details": str(error),
            },
            ensure_ascii=False,
        )

    finally:

        if cursor is not None:

            try:
                cursor.close()
            except Exception:
                pass

        if connection is not None:

            try:
                connection.close()
            except Exception:
                pass


# ============================================================
# AURA TOOL COLLECTION
# ============================================================

AURA_TOOLS = [
    calculate,
    web_search,
    retrieve_cv,
    save_memory,
    remember_information,
    recall_memory,
    get_database_schema,
    execute_sql,
]