import sqlite3
import os

SQL_DIR = os.path.dirname(__file__)

def initialize_tables(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for file in os.listdir(SQL_DIR):
        if file.endswith(".sql"):
            with open(os.path.join(SQL_DIR, file), "r") as f:
                sql_script = f.read()
            cursor.executescript(sql_script)

    conn.commit()
    cursor.close()