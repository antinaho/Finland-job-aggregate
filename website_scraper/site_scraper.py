from datetime import datetime
from typing import Iterator, Protocol

import time
import sqlite3
import os

from bs4 import BeautifulSoup
from curl_cffi import requests
from curl_cffi.requests import AsyncSession

async def get_soup_async(page_url) -> (BeautifulSoup, bool):
    try:
        async with AsyncSession() as session:
            response = await session.get(page_url, impersonate="chrome")
            if response.status_code == 200:
                content = response.text
                soup = BeautifulSoup(content, "html.parser")
                return soup, True
            else:
                return None, False
    except Exception as e:
        print(f"Error fetching {page_url}: {e}")
        return None, False

def get_soup(page_url) -> (BeautifulSoup, bool):
    try:
        r = requests.get(page_url, impersonate="chrome")
        soup = BeautifulSoup(r.text, "html.parser")
        return soup, r.ok
    except Exception as e:
        print(f"Request error on {page_url}, skipping")
        return None, False

DB_PATH = os.getenv("DB_PATH")
