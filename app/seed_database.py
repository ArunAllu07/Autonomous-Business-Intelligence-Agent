import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

from app.database import (
    DATABASE_TYPE,
    SQLITE_DATABASE_PATH,
    create_database,
    get_connection,
)


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

SOURCE_SQLITE_PATH = Path(
    os.getenv(
        "SQLITE_DATABASE_PATH",
        "data/business.db"
    )
)


# ============================================================
# READ EXISTING SQLITE DATA
# ============================================================

def load_sqlite_sales():
    """
    Read the existing sales records from the local SQLite
    database.

    This database acts as the migration source when moving
    AURA to PostgreSQL.
    """

    if not SOURCE_SQLITE_PATH.exists():
        raise FileNotFoundError(
            f"SQLite database not found: "
            f"{SOURCE_SQLITE_PATH}"
        )

    connection = sqlite3.connect(
        SOURCE_SQLITE_PATH
    )

    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            SELECT
                id,
                date,
                product,
                category,
                region,
                quantity,
                revenue,
                cost
            FROM sales
            ORDER BY id
            """
        )

        rows = cursor.fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:

        cursor.close()
        connection.close()


# ============================================================
# COUNT TARGET RECORDS
# ============================================================

def get_target_record_count(connection):
    """
    Return the number of records currently present
    in the target database.
    """

    cursor = connection.cursor()

    try:

        cursor.execute(
            "SELECT COUNT(*) FROM sales"
        )

        result = cursor.fetchone()

        return int(result[0])

    finally:

        cursor.close()


# ============================================================
# INSERT RECORDS
# ============================================================

def insert_sales_records(
    connection,
    records
):
    """
    Insert sales records into the configured database.

    Existing IDs are skipped so running the seed script
    multiple times does not create duplicates.
    """

    if not records:
        return 0

    cursor = connection.cursor()

    inserted = 0

    try:

        if DATABASE_TYPE == "sqlite":

            for record in records:

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO sales (
                        id,
                        date,
                        product,
                        category,
                        region,
                        quantity,
                        revenue,
                        cost
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record["id"],
                        record["date"],
                        record["product"],
                        record["category"],
                        record["region"],
                        record["quantity"],
                        record["revenue"],
                        record["cost"],
                    )
                )

                if cursor.rowcount > 0:
                    inserted += 1

        else:

            for record in records:

                cursor.execute(
                    """
                    INSERT INTO sales (
                        id,
                        date,
                        product,
                        category,
                        region,
                        quantity,
                        revenue,
                        cost
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    ON CONFLICT (id) DO NOTHING
                    """,
                    (
                        record["id"],
                        record["date"],
                        record["product"],
                        record["category"],
                        record["region"],
                        record["quantity"],
                        record["revenue"],
                        record["cost"],
                    )
                )

                if cursor.rowcount > 0:
                    inserted += 1

        connection.commit()

        return inserted

    except Exception:

        connection.rollback()

        raise

    finally:

        cursor.close()


# ============================================================
# SEED / MIGRATION
# ============================================================

def seed_database():
    """
    Initialize the configured database and migrate the
    existing SQLite sales records when PostgreSQL is selected.
    """

    print(
        "\n=============================="
    )

    print(
        "AURA DATABASE SEED"
    )

    print(
        "=============================="
    )

    print(
        f"\nTarget database: {DATABASE_TYPE}"
    )

    # --------------------------------------------------------
    # Create target database/table
    # --------------------------------------------------------

    create_database()

    # --------------------------------------------------------
    # Open target connection
    # --------------------------------------------------------

    connection = get_connection()

    try:

        existing_count = (
            get_target_record_count(
                connection
            )
        )

        print(
            f"Existing target records: "
            f"{existing_count}"
        )

        # ----------------------------------------------------
        # SQLite mode
        # ----------------------------------------------------

        if DATABASE_TYPE == "sqlite":

            print(
                "\nSQLite is already the local "
                "source database."
            )

            print(
                "No migration is required."
            )

            return

        # ----------------------------------------------------
        # PostgreSQL mode
        # ----------------------------------------------------

        print(
            "\nLoading records from SQLite..."
        )

        records = load_sqlite_sales()

        print(
            f"Source SQLite records: "
            f"{len(records)}"
        )

        if not records:

            print(
                "\nNo records were found "
                "in the SQLite source database."
            )

            return

        inserted = insert_sales_records(
            connection,
            records
        )

        print(
            f"\nRecords inserted: {inserted}"
        )

        final_count = (
            get_target_record_count(
                connection
            )
        )

        print(
            f"Final target records: "
            f"{final_count}"
        )

        print(
            "\nDatabase migration completed."
        )

    finally:

        connection.close()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        seed_database()

        print(
            "\nAURA database initialization "
            "completed successfully."
        )

    except Exception as error:

        print(
            "\nAURA database initialization failed."
        )

        print(
            f"Reason: {error}"
        )