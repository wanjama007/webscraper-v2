"""Run an automatic scrape for a URL (used by the window app)."""
import os
from config import ScraperConfig
from logger import get_logger
from validator import validate_url, RobotsChecker
from request_manager import RequestManager
from scraper import Scraper
from auto_extract import extract_auto, find_next_page
from cleaner import clean
from exporter import export

def scrape(url, kinds, pages=1, fmt="csv", out="output", log=None, respect_robots=True):
    log = log or get_logger()
    if not url.startswith(("http://", "https://")): url = "https://" + url
    validate_url(url)
    cfg = ScraperConfig(url=url, item_selector="*", fields={"x": "x"}, max_pages=pages,
                        output_format=fmt, output_path=out, respect_robots=respect_robots)
    s = Scraper(RequestManager(cfg, log, RobotsChecker(cfg.user_agent)), log)
    rows, seen, cur = [], set(), url
    while cur and cur not in seen and len(seen) < pages:
        seen.add(cur)
        soup = s.fetch(cur)
        found = extract_auto(soup, cur, set(kinds))
        log.info("Page %d: found %d items", len(seen), len(found))
        rows += found
        cur = find_next_page(soup, cur) if pages > 1 else None
    rows = clean(rows)
    if not rows: return None, 0
    return os.path.abspath(export(rows, fmt, out)), len(rows)
