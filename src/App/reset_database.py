import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql

# sql/ folder at the root of the project
SQL_DIR = Path(__file__).resolve().parents[2] / "sql"

# Only these schemas can be reset (safety), each with its init script
SCRIPTS = {
    "production": "production_init_db.sql",
    "test": "test_init_db.sql",
}


def reset_database(schema: str | None = None) -> None:
    """Drop the schema and recreate it with its init script.
    WARNING: all the data of the schema is lost (users, reservations...).
    Everything runs in one transaction: if the script fails, nothing is changed.
    """
    load_dotenv()
    schema = schema or os.environ["POSTGRES_SCHEMA"]
    if schema not in SCRIPTS:
        raise ValueError(f"Schema [{schema}] cannot be reset (allowed: {list(SCRIPTS)})")

    init_script = (SQL_DIR / SCRIPTS[schema]).read_text(encoding="utf-8")

    connection = psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=os.environ["POSTGRES_PORT"],
        database=os.environ["POSTGRES_DATABASE"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )
    try:
        with connection:  # commit at the end, rollback if an error is raised
            with connection.cursor() as cursor:
                cursor.execute(sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE;").format(sql.Identifier(schema)))
                cursor.execute(init_script)
    finally:
        connection.close()
    print(f"Schema [{schema}] has been reset.")


if __name__ == "__main__":
    answer = input("This erases ALL the data of the schema. Type 'yes' to continue: ")
    if answer.strip().lower() == "yes":
        reset_database()
    else:
        print("Cancelled.")