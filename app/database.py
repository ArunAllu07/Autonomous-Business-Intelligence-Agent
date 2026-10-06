import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATABASE_TYPE = os.getenv(
    "DATABASE_TYPE",
    "sqlite"
).lower()

SQLITE_DATABASE_PATH = Path(
    os.getenv(
        "SQLITE_DATABASE_PATH",
        "data/business.db"
    )
)

POSTGRES_DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


# ============================================================
# SQLITE
# ============================================================

def get_sqlite_connection():
    """
    Create a connection to the local SQLite database.
    """

    SQLITE_DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(
        SQLITE_DATABASE_PATH
    )


# ============================================================
# POSTGRESQL
# ============================================================

def get_postgres_connection():
    """
    Create a PostgreSQL database connection.

    PostgreSQL is loaded only when it is selected through
    DATABASE_TYPE=postgresql.
    """

    if not POSTGRES_DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    try:
        import psycopg
    except ImportError as error:
        raise RuntimeError(
            "psycopg is not installed. "
            "Install psycopg before using PostgreSQL."
        ) from error

    return psycopg.connect(
        POSTGRES_DATABASE_URL
    )


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Return a database connection based on DATABASE_TYPE.
    """

    if DATABASE_TYPE == "sqlite":
        return get_sqlite_connection()

    if DATABASE_TYPE in {
        "postgres",
        "postgresql"
    }:
        return get_postgres_connection()

    raise RuntimeError(
        f"Unsupported DATABASE_TYPE: {DATABASE_TYPE}"
    )


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def create_database():
    """
    Create the sales table if it does not already exist.
    """

    connection = get_connection()
    cursor = connection.cursor()

    try:

        if DATABASE_TYPE == "sqlite":

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    product TEXT,
                    category TEXT,
                    region TEXT,
                    quantity INTEGER,
                    revenue REAL,
                    cost REAL
                )
                """
            )

        else:

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sales (
                    id SERIAL PRIMARY KEY,
                    date DATE,
                    product VARCHAR(255),
                    category VARCHAR(255),
                    region VARCHAR(255),
                    quantity INTEGER,
                    revenue DOUBLE PRECISION,
                    cost DOUBLE PRECISION
                )
                """
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    create_database()

    print(
        "Business database initialized successfully."
    )

    print(
        f"Database type: {DATABASE_TYPE}"
    )

    if DATABASE_TYPE == "sqlite":

        print(
            f"Database path: "
            f"{SQLITE_DATABASE_PATH}"
        )

    else:

        print(
            "PostgreSQL connection configured."
        )