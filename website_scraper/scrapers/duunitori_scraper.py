from typing import List, Iterable

from website_scraper.site_scraper import SiteScraper, Listing, Job
from bs4 import BeautifulSoup

class DuunitoriScraper(SiteScraper):
    nav_page_url_template = "https://duunitori.fi/tyopaikat?order_by=date_posted&sivu={0}"
    lookup_url = "https://duunitori.fi/tyopaikat"
    source = "Duunitori"

    def _get_nav_page_urls(self) -> List[str]:
        soup, ok = SiteScraper.extract_soup(self.lookup_url)

        if not ok:
            print(f"Couldn't get nav page urls from {self.lookup_url}")
            return []

        max_page = 0
        page_nav = soup.find_all("a", class_="pagination__pagenum")
        for page in page_nav:
            if int(page.get_text().strip()) > max_page:
                max_page = int(page.get_text())

        urls = []
        for i in range(max_page):
            if i == 1:
                continue
            formatted_url = self.nav_page_url_template.format(i)
            urls.append(formatted_url)

        return urls

    def _extract_listings_from_nav_page(self, nav_page: BeautifulSoup) -> Iterable[Listing]:
        divs = nav_page.select("div.grid-sandbox--tight-bottom div.grid.grid--middle.job-box.job-box--lg")
        for item in divs:
            href = item.find("a")["href"]
            url_to_job_post = f"https://duunitori.fi{href}"
            posted_date = item.find("span", class_="job-box__job-posted")

            date_text_split = posted_date.text.split(" ")
            date_split = date_text_split[1].split(".")
            day = date_split[0].zfill(2)
            month = date_split[1].zfill(2)
            year = "2025"
            formatted_date = f"{year}-{month}-{day}"

            yield Listing(self.source, formatted_date, url_to_job_post)

    def listing_url_to_job(self, url) -> Job:
        soup, ok = SiteScraper.extract_soup(url)

        if not ok:
            return None
        warning = soup.find("h2", class_="text--warning")
        if warning:
            return None


        title = soup.find("h1").get_text().strip()

        company_tag = soup.select_one("p.header__info > a > span")
        if not company_tag:
            company_tag = soup.select_one("p.header__info > span > span")
        company = company_tag.get_text(strip=True)

        location_a_tag = soup.find("a", href=lambda href: href and "/alue/" in href)
        location = location_a_tag.find("span").get_text(strip=True)

        apply_btn = soup.find("a", class_="apply--button")
        apply_url = apply_btn["href"]
        if apply_url[0:1] == "/":
            apply_url = f"https://duunitori.fi{apply_url}"
        elif apply_url == "#uusitapa":
            apply_url = url + "#uusitapa"

        description = soup.find("div", class_="description")
        description_text = description.get_text(strip=True)

        return Job(
            self.source,
            url,
            title,
            company,
            location,
            description_text,
            apply_url
        )