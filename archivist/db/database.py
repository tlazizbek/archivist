import sqlite3
from pathlib import Path
from sqlite3 import Connection


from archivist.config import DB_PATH

def get_connection() -> Connection:
    connection = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    connection.row_factory = sqlite3.Row
    return connection

def init_db() -> None:
    connection = get_connection()

    try:
        schema_path = Path(__file__).with_name("schema.sql")
        schema = schema_path.read_text(encoding="UTF-8")
        connection.executescript(schema)
        connection.commit()
    finally:
        connection.close()