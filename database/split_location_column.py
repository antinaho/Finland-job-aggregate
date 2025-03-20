import os
import sqlite3
from datetime import datetime

DB_PATH = os.getenv("DB_PATH")

def split_rows_by_date(date: datetime.date) -> None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        query = "SELECT * FROM jobs WHERE date(post_date) = ?"
        cursor.execute(query, (str(date), ))
        rows = cursor.fetchall()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs_split (
                source TEXT,
                post_date DATETIME,
                post_url TEXT,
                title TEXT,
                company TEXT,
                location TEXT,
                description TEXT,
                apply_url TEXT
            )
        """)

        for row in rows:
            location = row[6]
            if "," in location:
                locations = [loc.strip() for loc in location.split(",")]
                for loc in locations:
                    new_row = (
                        row[1],
                        row[2],
                        row[3],
                        row[4],
                        row[5],
                        loc,
                        row[7],
                        row[8]
                    )
                    cursor.execute('''
                        INSERT INTO jobs_split (source, post_date, post_url, title, company, location, description, apply_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', new_row)
            else:
                new_row = (
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8]
                )
                cursor.execute('''
                        INSERT INTO jobs_split (source, post_date, post_url, title, company, location, description, apply_url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', new_row)
        conn.commit()
    except sqlite3.Error as e:
        print(f"General error occurred: {e}")
    finally:
        if conn:
            conn.close()

