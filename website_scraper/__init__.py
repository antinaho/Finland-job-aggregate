from typing import List, Iterator

from website_scraper.scrapers.duunitori_scraper import DuunitoriScraper
from website_scraper.site_scraper import Listing, SiteScraper, Job

scrapers = [
        DuunitoriScraper()
    ]

def extract_listings(date: str) -> List[Listing]:
    listings = []
    for scraper in scrapers:
        listings.extend(scraper.extract_listings_from_date(date))

    return listings

import time
import sqlite3

def listings_to_jobs_gen() -> Iterator[Job]:
    for scraper in scrapers:
        source = scraper.source
        try:
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()

            cursor.execute("SELECT source, post_date, post_url FROM listings WHERE status = 'pending' AND source = ?", (source, ))
            rows = cursor.fetchall()
            for row in rows:
                url = row[2]
                time.sleep(2.4)
                yield scraper.listing_url_to_job(url)
        except sqlite3.Error as e:
            print(f"Error occurred: {e}")
        finally:
            if conn:
                conn.close()