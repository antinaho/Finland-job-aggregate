from typing import List

from utils.url_trim import trim_tracking_params
import sqlite3

import os

from website_scraper.models import Job

DB_PATH = os.getenv("DB_PATH")


def jobs_to_db(jobs: List[Job]) -> None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        with open("./sql/insert_jobs_ddl.sql", "r") as sql_file:
            insert_query = sql_file.read()

        job_data = [
            (
                job.source,
                job.post_date,
                job.title,
                job.company,
                job.location,
                job.description,
                trim_tracking_params(job.apply_url)
            )
            for job in jobs
        ]

        try:
            cursor.executemany(insert_query, job_data)
        except sqlite3.IntegrityError as e:
            print(f"Error occurred: {e}")

        conn.commit()
    except sqlite3.Error as e:
        print(f"General error occurred: {e}")
    finally:
        if conn:
            conn.close()
