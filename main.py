from database.storage import jobs_to_db
from sql.table_initialization import initialize_tables

from datetime import datetime
import os

from website_scraper.scrapers.jobly_scraper import JoblyScraper
from website_scraper.site_scraper import extract_jobs

DB_PATH = os.getenv("DB_PATH")

def main() -> None:
    date = os.getenv("DATE")
    if not date:
        date = datetime.today()
    else:
        date = datetime.strptime(os.getenv("DATE"), "%Y-%m-%d")

    initialize_tables(DB_PATH)

    _jobs_etl(date)

from rich import print

def _jobs_etl(date: datetime) -> None:
    print(f"Extracting listings from date {date.date()}")
    jobs = extract_jobs(date)
    jobs_to_db(jobs)


if __name__ == "__main__":
    main()
