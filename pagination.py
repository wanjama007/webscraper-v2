"""Multiple-page collection: follow 'next' links until done."""
from urllib.parse import urljoin
from extractor import extract

def collect(scraper, cfg, logger, errors) -> tuple[list[dict], int]:
    url, visited, records = cfg.url, set(), []
    while url and url not in visited and len(visited) < cfg.max_pages:
        visited.add(url)
        current = url
        try:
            soup = scraper.fetch(url)
        except Exception as e:
            errors.record(f"fetch {url}", e); break
        page = extract(soup, cfg, url)
        logger.info("Page %d: %d records", len(visited), len(page))
        records.extend(page)
        url = None
        if cfg.next_page_selector:
            nxt = soup.select_one(cfg.next_page_selector)
            if nxt and nxt.get("href"):
                url = urljoin(current, nxt["href"])
    return records, len(visited)
