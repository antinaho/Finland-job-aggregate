from abc import ABC, abstractmethod
from typing import List, Iterable
from dataclasses import dataclass
from datetime import datetime
import time
from curl_cffi import requests
from bs4 import BeautifulSoup


@dataclass
class Listing:
    source: str
    date: str
    url: str

    def formatted_date(self) -> datetime:
        return datetime.strptime(self.date, "%Y-%m-%d")

@dataclass
class Job:
    source: str
    post_url: str
    title: str
    company: str
    location: str
    description: str
    apply_url: str

class SiteScraper(ABC):

    @abstractmethod
    def _get_nav_page_urls(self) -> List[str]:
        pass

    @abstractmethod
    def _extract_listings_from_nav_page(self, nav_page: BeautifulSoup) -> Iterable[Listing]:
        pass

    @abstractmethod
    def listing_url_to_job(self, url) -> Job:
        pass

    @staticmethod
    def extract_soup(page_url) -> (BeautifulSoup, bool):
        try:
            r = requests.get(page_url, impersonate="chrome")
            html_page = BeautifulSoup(r.content, "html.parser")
            return html_page, r.ok
        except Exception as e:
            print(f"Request error: {e}")
            return None, False


    def extract_listings_from_date(self, date) -> List[Listing]:

        date_lookup = datetime.strptime(date, "%Y-%m-%d")

        continue_ = True
        listings = []
        nav_page_urls = self._get_nav_page_urls()
        for nav_url in nav_page_urls:
            if not continue_: break

            page, ok = self.extract_soup(nav_url)

            if not ok: continue

            for listing in self._extract_listings_from_nav_page(page):
                listing_date = listing.formatted_date()
                if listing_date == date_lookup:
                    listings.append(listing)
                elif listing_date > date_lookup:
                    continue
                else:
                    continue_ = False
                    break

            time.sleep(2)
        return listings