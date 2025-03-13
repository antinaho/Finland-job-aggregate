from datetime import datetime
from typing import List, Iterator

import time
import sqlite3
import os

from website_scraper.models import Job
from website_scraper.scrapers.duunitori_scraper import DuunitoriScraper
from website_scraper.scrapers.tyomarkkinatori_scraper import TyomarkkinatoriScraper

scrapers = [
        DuunitoriScraper(),
        TyomarkkinatoriScraper()
    ]

def extract_jobs(date: datetime):
    jobs = []
    for scraper in scrapers:
        jobs.extend(scraper.extract_jobs_from_date(date))

    return jobs

DB_PATH = os.getenv("DB_PATH")

def listings_to_jobs_gen() -> (Iterator[Job], int):
    for scraper in scrapers:
        source = scraper.source
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("SELECT source, post_date, post_url FROM listings WHERE status = 'pending' AND source = ?", (source, ))
            rows = cursor.fetchall()
            for row in rows:
                url = row[2]
                time.sleep(2.4)
                yield (scraper.listing_url_to_job(url), [source, url])
        except sqlite3.Error as e:
            print(f"Error occurred: {e}")
        finally:
            if conn:
                conn.close()