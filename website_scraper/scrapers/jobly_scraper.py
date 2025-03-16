from datetime import datetime

from bs4 import BeautifulSoup
from curl_cffi import requests
from rich import print

from website_scraper.base_scraper import SiteScraper
from website_scraper.models import Job
import logging
import time

from typing import Iterator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def _next_nav_url_gen(soup) -> Iterator[BeautifulSoup]:
    base_url = "https://www.jobly.fi/"

    while True:
        link = soup.select_one("li.pager__item--next > a")
        if not link:
            break
        next_url = base_url + link["href"]
        soup, ok = SiteScraper.extract_soup(next_url)
        if not ok:
            break
        yield soup


def _title(soup) -> str:
    title = soup.select_one("h1")
    if title:
        return title.get_text(strip=True)
    return ""

def _company(soup) -> str:
    comp = soup.select_one("div.pane-node-recruiter-company-profile-job-organization > a")
    if comp:
        return comp.get_text(strip=True)
    return ""

def _location(soup) -> str:
    loc = soup.select_one("div.pane-entity-field pane-node-field-job-region")
    if loc:
        return loc.get_text(strip=True)
    return ""

def _apply_url(soup) -> str:
    tail = soup.select_one("li.recruiter_job_application > a")["href"]
    external_url = "https://www.jobly.fi"
    url = external_url + tail

    try:
        r = requests.get(url, allow_redirects=True)
        return r.redirect_url
    except Exception as e:
        return ""


def _description(soup) -> str:
    description = soup.select_one("div.node-job")
    if description:
        return description.get_text(strip=True)
    return ""

class JoblyScraper(SiteScraper):
    source = "Jobly"

    def _get_jobs_from_date(self, date: datetime):

        init_page = "https://www.jobly.fi/tyopaikat?search=&job_geo_location=&Etsi_ty%C3%B6paikkoja=Etsi%20ty%C3%B6paikkoja&lat=&lon=&country=&administrative_area_level_1=&page=0"
        soup, ok = SiteScraper.extract_soup(init_page)
        jobs = []

        if not ok:
            return jobs

        post_urls = []
        continue_ = True
        url_generator = _next_nav_url_gen(soup)
        i = 1
        while continue_:
            try:

                logger.info(f"Finding listings from page: {i}")
                i += 1

                posts = soup.select("div.views-row")

                for post in posts:
                    promoted = post.select_one("div.mobile_job_badge > span.node--job__featured-badge")
                    if promoted:
                        continue

                    date_span = post.select_one("span.date").get_text(strip=True).split(",")[0]
                    day, month, year = date_span.split(".")[0], date_span.split(".")[1], date_span.split(".")[2]

                    post_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()

                    post_url = post.select_one("a.recruiter-job-link")["href"]

                    if post_date == date.date():
                        post_urls.append((post_date, post_url))
                    elif post_date > date.date():
                        continue
                    else:
                        continue_ = False
                        break
                soup = next(url_generator)
            except StopIteration:
                break

        len_urls = len(post_urls)
        for i, listing in enumerate(post_urls):
            logger.info(f"Extracting job from listings: {i+1} / {len_urls}")

            soup, ok = SiteScraper.extract_soup(listing[1])

            if not ok:
                continue

            title = _title(soup)
            company = _company(soup)
            location = _location(soup)
            apply_url = _apply_url(soup)
            description = _description(soup)

            if apply_url == "":
                apply_url = listing[1]

            job = Job(
                self.source,
                listing[0],
                listing[1],
                title,
                company,
                location,
                description,
                apply_url,
            )

            jobs.append(job)
            time.sleep(1.111)

        return jobs