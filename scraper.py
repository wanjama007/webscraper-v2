"""HTML retrieval: download and parse a page."""
from bs4 import BeautifulSoup

class Scraper:
    def __init__(self, request_manager, logger):
        self.rm, self.log = request_manager, logger

    def fetch(self, url: str) -> BeautifulSoup:
        self.log.info("Fetching %s", url)
        resp = self.rm.get(url)
        resp.encoding = resp.encoding or resp.apparent_encoding
        return BeautifulSoup(resp.text, "lxml")
