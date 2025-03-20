from website_scraper.scrapers.duunitori_scraper import DuunitoriScraper
from website_scraper.scrapers.jobly_scraper import JoblyScraper
from website_scraper.scrapers.tyomarkkinatori_scraper import TyomarkkinatoriScraper

from typing import List


scrapers = [
    DuunitoriScraper(),
    #JoblyScraper(),
    #TyomarkkinatoriScraper()
]

def run_scrapers(date):
    jobs = []
    for scraper in scrapers:
        jobs.extend(scraper.get_jobs_from_date(date))
    return jobs
