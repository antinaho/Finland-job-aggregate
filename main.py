from database.storage import jobs_to_db
from sql.table_initialization import initialize_tables

from datetime import datetime
from rich import print
import os
import asyncio

from website_scraper import run_scrapers_async

DB_PATH = os.getenv("DB_PATH")

def main() -> None:
    date = os.getenv("DATE")
    if not date:
        date = datetime.today()
    else:
        date = datetime.strptime(os.getenv("DATE"), "%Y-%m-%d")

    initialize_tables(DB_PATH)

    _jobs_etl(date)

def _jobs_etl(date: datetime) -> None:
    print(f"Extracting listings from date {date.date()}")

    jobs = asyncio.run(run_scrapers_async(date))

    jobs_to_db(jobs)


if __name__ == "__main__":
    main()