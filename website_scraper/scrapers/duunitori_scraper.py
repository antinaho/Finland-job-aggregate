from datetime import datetime
from typing import List, Iterable, Iterator

from bs4 import BeautifulSoup
import time

from website_scraper.models import Job, Listing

import logging
from rich import print

from website_scraper.site_scraper import get_soup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def _next_nav_url_gen(soup) -> Iterator[BeautifulSoup]:
    while True:
        link = soup.select("a.pagination__page-round")[-1]
        if not link:
            break

        next_url = link["href"]
        soup, ok = get_soup(next_url)
        if not ok:
            break
        yield soup

class DuunitoriScraper:

    def _get_title(self, soup):
        return soup.select_one("h1").get_text(strip=True)

    def _get_company(self, soup) -> str:
        company_tag = soup.select_one("p.header__info > a > span")
        if not company_tag:
            company_tag = soup.select_one("p.header__info > span > span")

        if company_tag:
            return company_tag.get_text(strip=True)
        else:
            return ""

    def _get_location(self, soup) -> str:
        loc_tag = soup.select_one("p.header__info")
        location = ""

        primary_location = loc_tag.select_one("a > span").get_text(strip=True)
        location += primary_location

        secondary_locations = loc_tag.select("span", recursive=False)
        for secondary in secondary_locations:
            if secondary.get_text()[0] == " ":
                continue
            location += ", "
            if secondary.has_attr("title"):
                location_name = secondary["title"]
            else:
                location_name = secondary.get_text(strip=True)
            location += location_name

        return location

    def _get_description(self, soup) -> str:
        description_div = soup.select_one("div.description")
        if description_div:
            return description_div.get_text(strip=True)
        else:
            return ""

    def _get_apply_url(self, soup, baseurl) -> str:
        apply_btn = soup.select_one("a.apply--button")
        if not apply_btn:
            return ""

        apply_url = apply_btn.get("href")

        if not apply_url:
            return ""

        if apply_url[0:1] == "/":
            apply_url = f"https://duunitori.fi{apply_url}"
        elif apply_url == "#uusitapa":
            apply_url = baseurl + "#uusitapa"
        return apply_url

    def get_jobs_from_date(self, date: datetime) -> List[Job]:

        init_page = "https://duunitori.fi/tyopaikat?order_by=date_posted&sivu=0"
        soup, ok = get_soup(init_page)
        jobs = []

        if not ok:
            return jobs

        listings = []
        continue_ = True
        url_generator = _next_nav_url_gen(soup)
        i = 1
        while continue_:
            try:
                logger.info(f"Finding listings from page {i}")
                i += 1
                for listing in self._extract_listings_from_nav_page(soup):
                    if listing.date == date.date():
                        listings.append(listing)
                    elif listing.date > date.date():
                        continue
                    else:
                        continue_ = False
                        break
                soup = next(url_generator)
            except StopIteration:
                break

        jobs = []
        listing_len = len(listings)
        for i, l in enumerate(listings):
            logger.info(f"Extracting job from listings: {i+1} / {listing_len}")
            job = self._listing_url_to_job(l)
            if job:
                jobs.append(job)

        return jobs


    nav_page_url_template = "https://duunitori.fi/tyopaikat?order_by=date_posted&sivu={0}"
    source = "Duunitori"

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

        soup, ok = get_soup(url)

        if not ok:
            return None
        warning = soup.select_one("h2.text--warning")
        if warning:
            return None

        title = self._get_title(soup)
        company = self._get_company(soup)
        location = self._get_location(soup)
        apply_url = self._get_apply_url(soup, url)
        description = self._get_description(soup)

        return Job(
            listing.source,
            listing.date,
            listing.url,
            title,
            company,
            location,
            description,
            apply_url
        )