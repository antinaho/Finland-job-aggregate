from datetime import datetime
from typing import List


from website_scraper.models import Job, Listing

import logging
from rich import print
import random

from website_scraper.parsers.duunitori_parser import DuunitoriPostParser, DuunitoriNavPageParser
from website_scraper.site_scraper import get_soup_async

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class DuunitoriScraper:

    nav_page_url_template = "https://duunitori.fi/tyopaikat?order_by=date_posted&sivu={0}"
    source = "Duunitori"
    post_parser = DuunitoriPostParser()
    nav_parser = DuunitoriNavPageParser()

    async def get_jobs_from_date(self, date: datetime) -> List[Job]:
        logger.info(f"--- Starting scraper for {self.source} ---")
        init_page = "https://duunitori.fi/tyopaikat?order_by=date_posted&sivu=0"
        soup, ok = await get_soup_async(init_page)
        jobs = []

        if not ok:
            return jobs

        listings = []
        continue_ = True
        url_generator = self.nav_parser.get_next_nav_page_gen(soup)
        i = 1
        tries = 0
        while continue_:
            try:
                i += 1

                earliest = datetime.now().date()
                for listing in self.nav_parser.get_listing_from_nav_page_gen(soup):
                    if listing.date == date.date():
                        tries = 0
                        listings.append(listing)
                    elif listing.date > date.date():
                        continue
                    else:
                        earliest = listing.date

                if earliest < date.date():
                    tries += 1
                    if tries >= 2:
                        continue_ = False
                next_url = next(url_generator)
                soup, ok = await get_soup_async(next_url)
                if not ok:
                    break
            except StopIteration:
                break

        jobs = []
        listing_len = len(listings)
        for i, l in enumerate(listings):
            job = await self._listing_url_to_job(l)
            if job:
                jobs.append(job)

        return jobs

    async def _listing_url_to_job(self, listing) -> Job:
        url = listing.url

        soup, ok = await get_soup_async(url)

        if not ok:
            return None
        warning = soup.select_one("h2.text--warning")
        if warning:
            return None

        title = self.post_parser.get_title(soup)
        company = self.post_parser.get_company(soup)
        location = self.post_parser.get_location(soup)
        apply_url = self.post_parser.get_apply_url(soup)
        description = self.post_parser.get_description(soup)
        if apply_url == "#uusitapa":
            apply_url = url + "#uusitapa"

        return Job(
            self.source,
            listing.date,
            listing.url,
            title,
            company,
            location,
            description,
            apply_url
        )