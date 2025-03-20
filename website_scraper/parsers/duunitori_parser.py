from bs4 import BeautifulSoup, Tag
from typing import Iterator
from datetime import datetime

from website_scraper.models import Listing
from website_scraper.site_scraper import get_soup


class DuunitoriPostParser:
    def get_title(self, soup: BeautifulSoup) -> str:
        return soup.select_one("h1").get_text(strip=True)

    def get_company(self, soup: BeautifulSoup) -> str:
        company_tag = soup.select_one("p.header__info > a > span")
        if not company_tag:
            company_tag = soup.select_one("p.header__info > span > span")

        return company_tag.get_text(strip=True)

    def get_location(self, soup: BeautifulSoup) -> str:
        loc_tag = soup.select_one("p.header__info")
        if not loc_tag:
            return ""
        location_container = loc_tag.select_one("span.js-remove-leading-whitespace")
        if not location_container:
            return ""
        locations = []
        for child in location_container.children:
            if isinstance(child, Tag):
                if child.name == "a":
                    span_inside = child.find("span")
                    if span_inside:
                        location = span_inside.get_text(strip=True)
                        if location.startswith("-"):
                            location = location[1:].strip()
                        locations.append(location)
                elif child.name == "span":
                    location = child.get_text(strip=True)
                    title = child.get("title")
                    title_locations = []
                    if title:
                        title_locs = [loc.strip() for loc in title.split(",") if loc.strip()]
                        title_locations.extend(title_locs)
                    for attr_name in child.attrs:
                        if attr_name.lower() != "title" and attr_name != "class":
                            title_locations.append(attr_name.capitalize())
                    locations.extend(title_locations)
                    if location and not title:
                        locations.append(location)
        return ", ".join(locations)

    def get_description(self, soup: BeautifulSoup) -> str:
        description_div = soup.select_one("div.description")
        if description_div:
            return description_div.get_text(strip=True)
        else:
            return ""

    def get_apply_url(self, soup: BeautifulSoup) -> str:
        apply_btn = soup.select_one("a.apply--button")
        if not apply_btn:
            return ""

        apply_url = apply_btn.get("href")

        if not apply_url:
            return ""

        if apply_url[0:1] == "/":
            apply_url = f"https://duunitori.fi{apply_url}"
        elif apply_url == "#uusitapa":
            apply_url = "#uusitapa"
        return apply_url

class DuunitoriNavPageParser:

    def get_next_nav_page_gen(self, soup: BeautifulSoup) -> Iterator[str]:
        while True:
            link = soup.select("a.pagination__page-round")[-1]
            if not link:
                break

            next_url = link["href"]
            if not next_url:
                break
            yield next_url

    def get_listing_from_nav_page_gen(self, nav_page: BeautifulSoup) -> Iterator[BeautifulSoup]:
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

            yield Listing(datetime.strptime(formatted_date, "%Y-%m-%d").date(), url_to_job_post)

