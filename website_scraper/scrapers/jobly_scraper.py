from datetime import datetime

from bs4 import BeautifulSoup
from rich import print

from website_scraper.base_scraper import SiteScraper
from website_scraper.scrapers.duunitori_scraper import Listing

from typing import Iterator


def _next_nav_url_gen(soup) -> Iterator[BeautifulSoup]:
    base_url = "https://www.jobly.fi/"

    while True:
        link = soup.select_one("li.pager__item--next > a")
        if not link:
            break
        next_url = base_url + link["href"]
        soup, ok = SiteScraper.extract_soup(next_url)
        print(next_url)
        if not ok:
            break
        yield soup

class JoblyScraper(SiteScraper):
    source = "Jobly"

    def _get_jobs_from_date(self, date: datetime):

        init_page = "https://www.jobly.fi/tyopaikat?search=&job_geo_location=&Etsi_ty%C3%B6paikkoja=Etsi%20ty%C3%B6paikkoja&lat=&lon=&country=&administrative_area_level_1=&page=0"
        soup, ok = SiteScraper.extract_soup(init_page)
        jobs = []

        if not ok:
            return jobs

        listings = []
        continue_ = True
        url_generator = _next_nav_url_gen(soup)
        while continue_:
            try:
                soup = next(url_generator)
                posts = soup.select("div.views-row")

                for post in posts:
                    promoted = post.select_one("div.mobile_job_badge > span.node--job__featured-badge")
                    if promoted:
                        continue

                    date_span = post.select_one("span.date").get_text(strip=True).split(",")[0]
                    day, month, year = date_span.split(".")[0], date_span.split(".")[1], date_span.split(".")[2]

                    post_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d").date()

                    post_url = post.select_one("a.recruiter-job-link")["href"]

                    listing = Listing(self.source, post_date, post_url)

                    if post_date == date.date():
                        listings.append(listing)
                    elif post_date > date.date():
                        continue
                    else:
                        continue_ = False
                        break


            except StopIteration:
                break

        print(len(listings))