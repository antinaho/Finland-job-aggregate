from datetime import datetime
from typing import Iterator, Protocol

import time
import sqlite3
import os

from bs4 import BeautifulSoup
from curl_cffi import requests

def get_soup(page_url) -> (BeautifulSoup, bool):
    try:
        r = requests.get(page_url, impersonate="chrome")
        soup = BeautifulSoup(r.text, "html.parser")
        return soup, r.ok
    except Exception as e:
        print(f"Request error on {page_url}, skipping")
        return None, False

DB_PATH = os.getenv("DB_PATH")
