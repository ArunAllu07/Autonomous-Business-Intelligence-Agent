import re


# ============================================================
# DANGEROUS SQL OPERATIONS
# ============================================================

DANGEROUS_ACTIONS = {
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "TRUNCATE",
    "REPLACE",
    "CREATE",
    "ATTACH",
    "DETACH",
    "VACUUM",
    "REINDEX",
    "PRAGMA",
}


# ============================================================
# SQL COMMENT REMOVAL
# ============================================================

def remove_sql_comments(sql: str) -> str:
    """
    Remove SQL comments before performing safety checks.
    """

    if not sql:
        return ""

    # Remove -- comments
    cleaned = re.sub(
        r"--[^\n]*",
        "",
        sql,
    )

    # Remove /* ... */ comments
    cleaned = re.sub(
        r"/\*.*?\*/",
        "",
        cleaned,
        flags=re.DOTALL,
    )

    return cleaned.strip()


# ============================================================
# APPROVAL CHECK
# ============================================================

def requires_approval(action: str) -> bool:
    """
    Determine whether an SQL operation requires
    explicit human approval.
    """

    if not action:
        return False

    normalized = action.strip().upper()

    return normalized in DANGEROUS_ACTIONS


# ============================================================
# DANGEROUS SQL CHECK
# ============================================================

def contains_dangerous_sql(sql: str) -> bool:
    """
    Detect dangerous SQL operations anywhere
    inside a SQL statement.
    """

    cleaned = remove_sql_comments(sql)

    if not cleaned:
        return False

    for action in DANGEROUS_ACTIONS:

        pattern = rf"\b{action}\b"

        if re.search(
            pattern,
            cleaned,
            flags=re.IGNORECASE,
        ):
            return True

    return False


# ============================================================
# READ-ONLY SQL CHECK
# ============================================================

def is_read_only_sql(sql: str) -> bool:
    """
    Determine whether SQL is a single read-only query.

    Allowed:
        SELECT
        WITH ... SELECT

    Rejected:
        INSERT
        UPDATE
        DELETE
        DROP
        ALTER
        CREATE
        TRUNCATE
        REPLACE
        ATTACH
        DETACH
        VACUUM
        REINDEX
        PRAGMA
        Multiple statements
    """

    if not sql:
        return False

    cleaned = remove_sql_comments(sql)

    if not cleaned:
        return False

    # Remove one optional trailing semicolon.
    cleaned = cleaned.rstrip(";").strip()

    # Reject multiple SQL statements.
    if ";" in cleaned:
        return False

    # Only SELECT or WITH queries are permitted.
    starts_with_select = bool(
        re.match(
            r"^SELECT\b",
            cleaned,
            flags=re.IGNORECASE,
        )
    )

    starts_with_with = bool(
        re.match(
            r"^WITH\b",
            cleaned,
            flags=re.IGNORECASE,
        )
    )

    if not (
        starts_with_select
        or starts_with_with
    ):
        return False

    # Reject dangerous operations anywhere in the query.
    if contains_dangerous_sql(cleaned):
        return False

    return True


# ============================================================
# SQL VALIDATION
# ============================================================

def validate_sql(sql: str) -> str:
    """
    Validate SQL and return the cleaned SQL query.

    Raises ValueError if the query is unsafe.

    Successful result:
        "SELECT SUM(revenue) FROM sales"

    Failed result:
        ValueError
    """

    if not sql or not sql.strip():
        raise ValueError(
            "SQL query cannot be empty."
        )

    cleaned = remove_sql_comments(sql)

    if not cleaned:
        raise ValueError(
            "SQL query cannot be empty after removing comments."
        )

    if len(cleaned) > 5000:
        raise ValueError(
            "SQL query is too long."
        )

    if not is_read_only_sql(cleaned):
        raise ValueError(
            "Only single-statement read-only SELECT "
            "queries are allowed."
        )

    # Return the actual validated SQL string.
    return cleaned


# ============================================================
# HUMAN APPROVAL
# ============================================================

def request_approval(action: str) -> bool:
    """
    Request explicit human approval for a
    potentially destructive operation.
    """

    print("\n==============================")
    print("HUMAN APPROVAL REQUIRED")
    print("==============================")

    print(
        f"\nRequested action: {action}"
    )

    response = input(
        "\nApprove this action? (yes/no): "
    ).strip().lower()

    if response == "yes":

        print(
            "\nAction approved."
        )

        return True

    print(
        "\nAction rejected."
    )

    return False