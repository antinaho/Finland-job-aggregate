from typing import Protocol, Iterator

from bs4 import BeautifulSoup

class SoupPostParser(Protocol):
    def get_title(self, soup: BeautifulSoup) -> str:
        ...

    def get_company(self, soup: BeautifulSoup) -> str:
        ...

    def get_location(self, soup: BeautifulSoup) -> str:
        ...

    def get_description(self, soup: BeautifulSoup) -> str:
        ...

    def get_apply_url(self, soup: BeautifulSoup) -> str:
        ...

class SoupNavPageParser(Protocol):
    def get_next_nav_page_gen(self, nav_page: BeautifulSoup) -> Iterator[BeautifulSoup]:
        ...

    def get_listing_from_nav_page_gen(self, nav_page: BeautifulSoup) -> Iterator[BeautifulSoup]:
        ...
