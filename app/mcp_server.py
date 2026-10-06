from mcp.server.mcpserver import MCPServer

from app.database import get_connection
from app.guardrails import (
    requires_approval,
    contains_dangerous_sql,
    is_read_only_sql,
    request_approval,
)


mcp = MCPServer("AURA Business Data Server")


# ============================================================
# DATABASE HELPER
# ============================================================

def _is_postgres_connection(connection) -> bool:
    """
    Detect whether the active database connection
    is PostgreSQL.
    """

    return "psycopg" in (
        type(connection).__module__.lower()
    )


# ============================================================
# SALES SCHEMA
# ============================================================

@mcp.tool()
def get_sales_schema() -> str:
    """
    Return the schema of the sales table.

    Works with both SQLite and PostgreSQL.
    """

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # ----------------------------------------------------
        # PostgreSQL
        # ----------------------------------------------------

        if _is_postgres_connection(connection):

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

            columns = cursor.fetchall()

            if not columns:
                return "Sales table was not found."

            schema = []

            for column in columns:

                column_name = column[0]
                data_type = column[1]
                nullable = column[2]

                schema.append(
                    f"{column_name} ({data_type}, "
                    f"nullable: {nullable})"
                )

            return "\n".join(schema)

        # ----------------------------------------------------
        # SQLite
        # ----------------------------------------------------

        cursor.execute(
            "PRAGMA table_info(sales)"
        )

        columns = cursor.fetchall()

        if not columns:
            return "Sales table was not found."

        schema = []

        for column in columns:

            column_name = column[1]
            data_type = column[2]
            nullable = (
                "YES"
                if column[3] == 0
                else "NO"
            )

            schema.append(
                f"{column_name} ({data_type}, "
                f"nullable: {nullable})"
            )

        return "\n".join(schema)

    except Exception:
        return (
            "Unable to retrieve the sales schema."
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ============================================================
# READ-ONLY SALES QUERY
# ============================================================

@mcp.tool()
def query_sales(sql: str) -> str:
    """
    Execute a strictly read-only query against
    the sales database.

    Only a single SELECT or WITH query is allowed.
    """

    if not sql or not sql.strip():
        return "SQL query cannot be empty."

    cleaned_sql = sql.strip()

    # --------------------------------------------------------
    # CENTRALIZED READ-ONLY SECURITY
    # --------------------------------------------------------

    if not is_read_only_sql(cleaned_sql):

        return (
            "Unsafe SQL rejected. "
            "Only single-statement read-only "
            "SELECT queries are allowed."
        )

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            cleaned_sql
        )

        rows = cursor.fetchall()

        if not rows:

            return (
                "Query executed successfully "
                "but returned no rows."
            )

        if cursor.description is None:

            return (
                "Query returned no columns."
            )

        column_names = [
            description[0]
            for description in cursor.description
        ]

        result = [
            dict(
                zip(
                    column_names,
                    row
                )
            )
            for row in rows
        ]

        return str(result)

    except Exception:
        return "SQL query failed."

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ============================================================
# APPROVED DATABASE MODIFICATION
# ============================================================

@mcp.tool()
def execute_sql(sql: str) -> str:
    """
    Execute a database modification only after
    explicit human approval.

    This tool is intentionally separate from
    query_sales(), which is read-only.
    """

    if not sql or not sql.strip():
        return "SQL query cannot be empty."

    cleaned_sql = sql.strip()

    # --------------------------------------------------------
    # QUERY SIZE
    # --------------------------------------------------------

    if len(cleaned_sql) > 5000:

        return (
            "SQL query is too long."
        )

    # --------------------------------------------------------
    # DANGEROUS OPERATION CHECK
    # --------------------------------------------------------

    if not contains_dangerous_sql(
        cleaned_sql
    ):

        return (
            "This tool only handles database "
            "operations that require approval."
        )

    # --------------------------------------------------------
    # REMOVE ONE TRAILING SEMICOLON
    # --------------------------------------------------------

    statement = (
        cleaned_sql
        .rstrip(";")
        .strip()
    )

    # --------------------------------------------------------
    # MULTIPLE STATEMENT PROTECTION
    # --------------------------------------------------------

    if ";" in statement:

        return (
            "Multiple SQL statements "
            "are not allowed."
        )

    # --------------------------------------------------------
    # IDENTIFY SQL OPERATION
    # --------------------------------------------------------

    parts = statement.split()

    if not parts:

        return (
            "SQL query cannot be empty."
        )

    first_word = parts[0].upper()

    if not requires_approval(
        first_word
    ):

        return (
            "The requested database operation "
            "is not recognized as an approved "
            "modification."
        )

    # --------------------------------------------------------
    # HUMAN APPROVAL
    # --------------------------------------------------------

    approved = request_approval(
        statement
    )

    if not approved:

        return (
            "Database operation rejected "
            "by human approval."
        )

    # --------------------------------------------------------
    # EXECUTE AFTER APPROVAL
    # --------------------------------------------------------

    connection = None
    cursor = None

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            statement
        )

        connection.commit()

        return (
            "SQL operation executed successfully."
        )

    except Exception:

        if connection is not None:
            connection.rollback()

        return (
            "SQL operation failed."
        )

    finally:

        if cursor is not None:
            cursor.close()

        if connection is not None:
            connection.close()


# ============================================================
# MCP SERVER ENTRY POINT
# ============================================================

if __name__ == "__main__":
    mcp.run()