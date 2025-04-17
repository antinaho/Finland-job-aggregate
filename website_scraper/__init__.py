from website_scraper.models import Job
from website_scraper.scrapers.duunitori_scraper import DuunitoriScraper
from website_scraper.scrapers.jobly_scraper import JoblyScraper
from website_scraper.scrapers.tyomarkkinatori_scraper import TyomarkkinatoriScraper

from typing import List

import asyncio

async def run_scrapers_async(date) -> List[Job]:
    scrapers = [
        DuunitoriScraper(),
        JoblyScraper(),
        TyomarkkinatoriScraper()
    ]

    tasks = [scraper.get_jobs_from_date(date) for scraper in scrapers]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    jobs = []
    for result in results:
        if isinstance(result, Exception):
            print(f"Scraper failed: {result}")
        else:
            jobs.extend(result)
    return jobs
