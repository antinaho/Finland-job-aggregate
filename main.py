from database.storage import listings_to_db, job_to_db, failed_job_extract
from sql.table_initialization import initialize_tables
from website_scraper import extract_listings, listings_to_jobs_gen

from datetime import datetime
import sys

def main() -> None:
    if len(sys.argv) > 1:
        date = sys.argv[1]
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"Custom date must be in 'YYYY-MM-DD' format (e.g., {datetime.strftime(datetime.now(), "%Y-%m-%d")})")
    else:
        date = datetime.strftime(datetime.now(), "%Y-%m-%d")

    initialize_tables("app.db")

    _listings_etl(date)

    _jobs_etl()

def _listings_etl(date):
    print(f"Extracting listings from date {date}")
    listings = extract_listings(date)
    print(f"Extracted {len(listings)} listings. Loading into database.")
    listings_to_db(listings)

def _jobs_etl():
    print("Extraction and loading jobs from listings...")
    for job, listing in listings_to_jobs_gen():
        if job is None:
            failed_job_extract(listing[0], listing[1])
        else:
            job_to_db(job)

if __name__ == "__main__":
    main()
