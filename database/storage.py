from utils.url_trim import trim_tracking_params
import sqlite3
from typing import List

from website_scraper import Listing
from website_scraper.site_scraper import Job

import os
from dotenv import load_dotenv

load_dotenv()
DB_PATH = os.environ.get("DB_PATH")

def job_to_db(job: Job) -> None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        with open("./sql/insert_jobs_raw_ddl.sql", "r") as sql_file:
            insert_query = sql_file.read()

        try:
            cursor.execute(insert_query, (
                job.title,
                job.company,
                job.location,
                job.description,
                trim_tracking_params(job.apply_url)
            ))

            job_id = cursor.lastrowid

            cursor.execute("""
                UPDATE listings
                SET id = ?, status = 'scraped'
                WHERE source = ? AND post_url = ?
            """, (job_id, job.source, job.post_url))
        except sqlite3.Error as e:
            print(f"General error occurred: {e}")
            cursor.execute("""
                UPDATE listings
                SET status = 'failed'
                WHERE source = ? AND post_url = ?
            """, (job.source, job.post_url))
        conn.commit()
    except sqlite3.Error as e:
        print(f"General error occurred: {e}")
    finally:
        if conn:
            conn.close()


def listings_to_db(listings: List[Listing]) -> None:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        with open("./sql/insert_listings_ddl.sql", "r") as sql_file:
            insert_query = sql_file.read()

        for listing in listings:
            try:
                cursor.execute(insert_query, (
                    listing.source,
                    listing.date,
                    listing.url
                ))
            except sqlite3.IntegrityError as e:
                print(f"Error occurred: {e}")
        conn.commit()
    except sqlite3.Error as e:
        print(f"General error occurred: {e}")
    finally:
        if conn:
            conn.close()
