from bs4 import BeautifulSoup
import json
import chompjs
from curl_cffi import requests

class JoblyPostParser:

    def __init__(self, soup):
        self.dic = self._get_dic(soup)

    def is_active_post(self):
        return self.dic is not None

    def _get_dic(self, soup):
        script_tag = soup.select('script[type="application/ld+json"]')
        for script in script_tag:
            json_content = script.string
            if json_content:
                data = json.loads(json_content)
                if data.get('@type') == 'JobPosting':
                    return chompjs.parse_js_object(script.text)

    def get_title(self, soup: BeautifulSoup = None) -> str:
        return self.dic.get('title')

    def get_company(self, soup: BeautifulSoup = None) -> str:
        return self.dic.get("hiringOrganization").get("name")

    def get_location(self, soup: BeautifulSoup = None) -> str:
        locations = self.dic.get("jobLocation")
        l = ""
        for item in locations:
            try:
                locality = item["address"].get("addressLocality")
                l += locality
                l += ", "
            except Exception as e:
                continue
        if len(l) > 0:
            return l[:-2]
        else:
            return ""


    def get_description(self, soup: BeautifulSoup = None) -> str:
        return self.dic.get("description")

    async def get_apply_url(self, soup: BeautifulSoup = None) -> str:
        apply_tag = soup.select_one("li.recruiter_job_application > a").get("href")
        url = "https://jobly.fi"

        try:
            async with AsyncSession() as session:
                response = await session.get(url + apply_tag, impersonate="chrome")
                if response.status_code == 200:
                    return response.url
        except Exception as e:
            return ""

from curl_cffi.requests import AsyncSession