from datetime import datetime

from website_scraper.models import Job
import logging
import time


from website_scraper.parsers.jobly_parser import JoblyPostParser
from website_scraper.site_scraper import get_soup, get_soup_async

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def _next_nav_url(soup) -> str:
    base_url = "https://www.jobly.fi/"
    link = soup.select_one("li.pager__item--next > a")
    next_url = base_url + link["href"]
    return next_url

class JoblyScraper:
    source = "Jobly"

    async def get_jobs_from_date(self, date: datetime):
        logger.info(f"--- Starting scraper for {self.source} ---")

        init_page = "https://www.jobly.fi/tyopaikat?search=&job_geo_location=&Etsi_ty%C3%B6paikkoja=Etsi%20ty%C3%B6paikkoja&lat=&lon=&country=&administrative_area_level_1=&page=0"
        soup, ok = await get_soup_async(init_page)
        jobs = []

        if not ok:
            return jobs

        post_urls = []
        continue_ = True
        while continue_:
            try:
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
                next_url = _next_nav_url(soup)
                soup, ok = await get_soup_async(next_url)
                if not ok:
                    break
                time.sleep(0.3)
            except StopIteration:
                break

        len_urls = len(post_urls)
        for i, listing in enumerate(post_urls):
            date = listing[0]
            url = listing[1]

            soup, ok = await get_soup_async(url)

            if not ok:
                continue

            post_parser = JoblyPostParser(soup)
            if not post_parser.is_active_post():
                continue

            title = post_parser.get_title()
            company = post_parser.get_company()
            location = post_parser.get_location()
            apply_url = await post_parser.get_apply_url(soup)
            description = post_parser.get_description()

            job = Job(
                self.source,
                date,
                url,
                title,
                company,
                location,
                description,
                apply_url,
            )

            jobs.append(job)
            time.sleep(1.111)

        return jobs

