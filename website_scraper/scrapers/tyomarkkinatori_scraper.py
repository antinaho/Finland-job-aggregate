from curl_cffi import requests

from datetime import datetime
from dateutil.relativedelta import relativedelta

from website_scraper.models import Job

import time
import random

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TyomarkkinatoriScraper:

    source = "Työmarkkinatori"

    async def get_jobs_from_date(self, date: datetime):
        logger.info(f"--- Starting scraper for {self.source} ---")
        week_ago = datetime.now().date() - relativedelta(weeks=1)
        formatted_datetime = week_ago.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        max_page = await _get_max_page(formatted_datetime)

        location_json, status = await _get_location_codes()

        if not status:
            return []

        jobs = []
        continue_ = True

        for i in range(0, max_page):
            if not continue_: break

            json_data['paging']['pageNumber'] = i
            json_data['filters']['publishedAfter'] = json_data['filters']['publishedAfter'].format(
                published_after=formatted_datetime)

            try:
                async with AsyncSession() as session:
                    response = await session.post(
                        'https://tyomarkkinatori.fi/api/jobpostingfulltext/search/v1/search',
                        json=json_data,
                        impersonate="chrome"
                    )
            except Exception as e:
                continue

            if response.status_code != 200:
                continue

            for item in response.json()["content"]:

                try:
                    async with AsyncSession() as session:
                        r = await session.get(
                            f'https://tyomarkkinatori.fi/api/jobposting/v1/jobpostings/{item["id"]}',
                            impersonate="chrome"
                        )
                except Exception as e:
                    continue

                if r.status_code != 200:
                    continue

                data = r.json()

                publish_date = _publish_date(data)

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

                title = _title(data, main_language)
                company = _company(data, main_language)
                description = _description(data, main_language)
                location = _location(data, location_json)
                apply_url = _apply_url(data, main_language, _post_url(item["id"], main_language))

                job = Job(
                    self.source,
                    _raw_to_job_date(publish_date),
                    _post_url(item["id"], main_language),
                    title,
                    company,
                    location,
                    description,
                    apply_url
                )

                jobs.append(job)

            time.sleep(random.random() * 1.22)
        return jobs

from curl_cffi.requests import AsyncSession
async def _get_max_page(formatted_datetime) -> int:

    json_data['paging']['pageNumber'] = 0
    json_data['filters']['publishedAfter'] = json_data['filters']['publishedAfter'].format(
        published_after=formatted_datetime)

    try:
        async with AsyncSession() as session:
            response = await session.post(
                'https://tyomarkkinatori.fi/api/jobpostingfulltext/search/v1/search',
                json=json_data,
                impersonate="chrome"
            )
    except Exception as e:
        return 0

    max_page = min(response.json()["totalPages"], 100)

    return max_page

async def _get_location_codes() -> (str, bool):
    try:
        async with AsyncSession() as session:
            response = await session.get(
            'https://tyomarkkinatori.fi/api/codes/v1/koodistot/KUNTA/koodit',
            impersonate="chrome"
            )
    except Exception as e:
        return 0

    if response.status_code != 200:
        return "", False

    return response.json(), True

def _raw_to_job_date(raw_date) -> datetime.date:
    return datetime.strptime(raw_date.split("T")[0], "%Y-%m-%d").date()

def _publish_date(json) -> str:
    return json["publishDate"]

def _title( json, language) -> str:
    return json["title"]["values"].get(language, "")

def _company(json, language) -> str:
    return json["businessName"]["values"].get(language, "")

def _description(json, language) -> str:
    return json["jobDescription"]["values"].get(language, "")

def _location(json, location_json) -> str:
    municipalities = json.get("municipalities", [])
    if len(municipalities) > 0:
        location = ""
        for index, code in enumerate(municipalities):

            for l in location_json:
                if l["Koodi"] == code:
                    location += l["Selitteet"][0]["Teksti"]
            if index != len(municipalities) - 1:
                location += ", "

        return location

    post_office = json.get("postOffice", "")
    if post_office != "":
        return post_office

    postal_address = json.get("postalAddress", "")
    if postal_address != "":
        return postal_address

    countries = json.get("countries", [])
    if len(countries) > 0:
        return countries[0]

    return ""

def _post_url(id, language) -> str:
    return f"https://tyomarkkinatori.fi/henkiloasiakkaat/avoimet-tyopaikat/{id}/{language}/"

def _apply_url(json, language, post_url) -> str:
    return json["applicationUrl"]["values"].get(language, post_url)


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




