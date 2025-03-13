from curl_cffi import requests

from typing import List

from datetime import datetime
from dateutil.relativedelta import relativedelta

from website_scraper.base_scraper import SiteScraper
from website_scraper.models import Job

from rich import print
import time
import random

class TyomarkkinatoriScraper(SiteScraper):

    def _get_jobs_from_date(self, date: datetime):
        week_ago = datetime.now().date() - relativedelta(weeks=1)
        formatted_datetime = week_ago.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        json_data['paging']['pageNumber'] = 0
        json_data['filters']['publishedAfter'] = json_data['filters']['publishedAfter'].format(
            published_after=formatted_datetime)

        response = requests.post(
            'https://tyomarkkinatori.fi/api/jobpostingfulltext/search/v1/search',
            json = json_data,
            impersonate="chrome"
        )

        if response.status_code != 200:
            return []

        max_page = min(response.json()["totalPages"], 100)

        jobs = []
        continue_ = True

        response_loc = requests.get(
            'https://tyomarkkinatori.fi/api/codes/v1/koodistot/KUNTA/koodit',
            impersonate="chrome"
        )

        if not response_loc.ok:
            return []


        for i in range(0, max_page):
            if not continue_: break
            json = {
                'query': '',
                'paging': {
                    'pageSize': 90,
                    'pageNumber': i,
                },
                'filters': {
                    'publishedAfter': '{published_after}',
                    'closesBefore': None,
                },
                'sorting': 'LATEST',
            }
            json['filters']['publishedAfter'] = json['filters']['publishedAfter'].format(
                published_after=formatted_datetime)

            response = requests.post(
                'https://tyomarkkinatori.fi/api/jobpostingfulltext/search/v1/search',
                json=json,
                impersonate="chrome"
            )

            for item in response.json()["content"]:
                r = requests.get(
                    f'https://tyomarkkinatori.fi/api/jobposting/v1/jobpostings/{item["id"]}',
                    impersonate="chrome"
                )

                if r.status_code != 200:
                    return []

                data = r.json()

                publish_date = data["publishDate"]

                print(f"{date.date()} ::: {datetime.strptime(publish_date.split("T")[0], "%Y-%m-%d").date()}")
                if datetime.strptime(publish_date.split("T")[0], "%Y-%m-%d").date() > date.date():
                    continue
                elif datetime.strptime(publish_date.split("T")[0], "%Y-%m-%d").date() < date.date():
                    continue_ = False
                    break

                language_versions = data["languageVersions"]

                main_language = ""
                if "fi" in language_versions:
                    main_language = "fi"
                elif "en" in language_versions:
                    main_language = "en"
                elif "sv" in language_versions:
                    main_language = "sv"

                if main_language == "":
                    return []

                url = f"https://tyomarkkinatori.fi/henkiloasiakkaat/avoimet-tyopaikat/{item["id"]}/{main_language}/"

                title = data["title"]["values"][main_language]
                company = data["businessName"]["values"][main_language]
                description = data["jobDescription"]["values"][main_language]

                location = ""
                municipalities = data["municipalities"]

                matches = [item for item in response_loc.json() if item.get("Koodi") in municipalities]
                if matches:
                    for match in matches:
                        location += match["Selitteet"][0]["Teksti"]
                        location += ", "

                apply_url = data["applicationUrl"]["values"].get(main_language, url)

                job = Job(
                    self.source,
                    datetime.strptime(publish_date.split("T")[0], "%Y-%m-%d").date(),

                    title,
                    company,
                    location,
                    description,
                    apply_url
                )

                jobs.append(job)

                time.sleep(random.random() * 1.2 + 0.3)

        return jobs

    def listing_url_to_job(self, url) -> Job:
        pass

    source = "Työmarkkinatori"

    def _get_nav_page_url(self) -> List[str]:
        pass

    def test(self, date: datetime):
        listings = self._get_jobs_from_date(date)
        print(len(listings))


cookies = {
    'CookieConsent': '{stamp:%27Xy8Pd5FLJ2jRlBdMUBFYhcPHVhIYeNUekCpOYsbEm/LQhCBOlK4gPw==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1724572734317%2Cregion:%27fi%27}',
    'csrf': 'QMlciFpKeVogXmQ2hvojdUe4o03OUNSCQKEiJeHZL6yYg83Bo8JNaVexQ1bqA3aCmU_Sdb7O2Jyhtot16JkKQQ:AAABlY5HZ14:rzc2WHjDdu2lMzAVu6qm_A',
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:136.0) Gecko/20100101 Firefox/136.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'fi-FI,fi;q=0.8,en-US;q=0.5,en;q=0.3',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://tyomarkkinatori.fi/',
    'Content-Type': 'application/json',
    'Origin': 'https://tyomarkkinatori.fi',
    'Connection': 'keep-alive',
    # 'Cookie': 'CookieConsent={stamp:%27Xy8Pd5FLJ2jRlBdMUBFYhcPHVhIYeNUekCpOYsbEm/LQhCBOlK4gPw==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1724572734317%2Cregion:%27fi%27}; csrf=QMlciFpKeVogXmQ2hvojdUe4o03OUNSCQKEiJeHZL6yYg83Bo8JNaVexQ1bqA3aCmU_Sdb7O2Jyhtot16JkKQQ:AAABlY5HZ14:rzc2WHjDdu2lMzAVu6qm_A',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

json_data = {
    'query': '',
    'paging': {
        'pageSize': 90,
        'pageNumber': '{page_num}',
    },
    'filters': {
        'publishedAfter': '{published_after}',
        'closesBefore': None,
    },
    'sorting': 'LATEST',
}




