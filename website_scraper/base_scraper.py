from abc import ABC, abstractmethod
from curl_cffi import requests
from bs4 import BeautifulSoup
from datetime import datetime

class SiteScraper(ABC):

    @abstractmethod
    def _get_jobs_from_date(self, date: datetime):
        pass

    @staticmethod
    def extract_soup(page_url) -> (BeautifulSoup, bool):
        try:
            r = requests.get(page_url, impersonate="chrome")
            soup = BeautifulSoup(r.text, "html.parser")
            return soup, r.ok
        except Exception as e:
            print(f"Request error on {page_url}, skipping")
            return None, False


    def extract_jobs_from_date(self, date: datetime):
        jobs = self._get_jobs_from_date(date)
        return jobs