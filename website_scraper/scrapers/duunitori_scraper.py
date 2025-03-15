from datetime import datetime
from typing import List, Iterable

from bs4 import BeautifulSoup
import time

from website_scraper.base_scraper import SiteScraper
from website_scraper.models import Job

from dataclasses import dataclass

import logging
from rich import print

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class Listing:
    source: str
    date: datetime.date
    url: str

def _title(soup) -> str:
    return soup.select_one("h1").get_text(strip=True)

def _company(soup) -> str:
    company_tag = soup.select_one("p.header__info > a > span")
    if not company_tag:
        company_tag = soup.select_one("p.header__info > span > span")
    return company_tag.get_text(strip=True)

def _location(soup) -> str:
    location_a_tag = soup.find("a", href=lambda href: href and "/alue/" in href)
    return location_a_tag.select_one("span").get_text(strip=True)

def _apply_url(soup, baseurl) -> str:
    apply_btn = soup.select_one("a.apply--button")
    if not apply_btn:
        return ""

    apply_url = apply_btn["href"]
    if apply_url[0:1] == "/":
        apply_url = f"https://duunitori.fi{apply_url}"
    elif apply_url == "#uusitapa":
        apply_url = baseurl + "#uusitapa"
    return apply_url

def _description(soup) -> str:
    return soup.select_one("div.description").get_text(strip=True)

class DuunitoriScraper(SiteScraper):
    def _get_jobs_from_date(self, date: datetime):
        listings = []
        continue_ = True
        nav_page_urls = self._get_nav_page_urls()
        for i, nav_url in enumerate(nav_page_urls):
            if not continue_: break
            logger.info(f"Finding listings from page {i+1}")

            page, ok = self.extract_soup(nav_url)
            if not ok: continue

            for listing in self._extract_listings_from_nav_page(page):

                if listing.date == date.date():
                    listings.append(listing)
                elif listing.date > date.date():
                    continue
                else:
                    continue_ = False
                    break

            time.sleep(2)

        jobs = []
        listing_len = len(listings)
        for i, l in enumerate(listings):
            logger.info(f"Extracting job from listings: {i+1} / {listing_len}")
            job = self._listing_url_to_job(l)
            if job:
                jobs.append(job)

        return jobs


    nav_page_url_template = "https://duunitori.fi/tyopaikat?order_by=date_posted&sivu={0}"
    lookup_url = "https://duunitori.fi/tyopaikat"
    source = "Duunitori"

    def _get_nav_page_urls(self) -> List[str]:
        soup, ok = SiteScraper.extract_soup(self.lookup_url)

        if not ok:
            print(f"Couldn't get nav page urls from {self.lookup_url}")
            return []

        max_page = soup.select("a.pagination__pagenum")[-1].get_text(strip=True)

        urls = [self.nav_page_url_template.format(i) for i in range(int(max_page)) if i != 1]

        return urls

    def _extract_listings_from_nav_page(self, nav_page: BeautifulSoup) -> Iterable[Listing]:
        divs = nav_page.select("div.grid-sandbox--tight-bottom div.grid.grid--middle.job-box.job-box--lg")
        for item in divs:
            href = item.select_one("a")["href"]
            url_to_job_post = f"https://duunitori.fi{href}"
            posted_date = item.select_one("span.job-box__job-posted")

            date_text_split = posted_date.text.split(" ")
            date_split = date_text_split[1].split(".")
            day = date_split[0].zfill(2)
            month = date_split[1].zfill(2)
            year = "2025"
            formatted_date = f"{year}-{month}-{day}"

            yield Listing(self.source, datetime.strptime(formatted_date, "%Y-%m-%d").date(), url_to_job_post)

    def _listing_url_to_job(self, listing) -> Job:
        url = listing.url

        soup, ok = SiteScraper.extract_soup(url)

        if not ok:
            return None
        warning = soup.select_one("h2.text--warning")
        if warning:
            return None

        title = _title(soup)
        company = _company(soup)
        location = _location(soup)
        apply_url = _apply_url(soup, url)
        description = _description(soup)

        return Job(
            listing.source,
            listing.date,
            url,
            title,
            company,
            location,
            description,
            apply_url
        )