
"""
import argparse, json, os, time
from datetime import datetime
from config import ScraperConfig
from logger import get_logger
from validator import validate_config, RobotsChecker
from error_handler import ErrorTracker, ScraperError
from request_manager import RequestManager
from scraper import Scraper
from pagination import collect
from cleaner import clean
from exporter import export

def run(cfg: ScraperConfig) -> dict:
    log = get_logger(); errors = ErrorTracker(log); t0 = time.time()
    summary = {"started": datetime.now().isoformat(timespec="seconds"), "url": cfg.url}
    try:
        validate_config(cfg)
        rm = RequestManager(cfg, log, RobotsChecker(cfg.user_agent))
        raw, pages = collect(Scraper(rm, log), cfg, log, errors)
        records = clean(raw)
        path = export(records, cfg.output_format, cfg.output_path) if records else None
        summary.update(pages=pages, raw_records=len(raw), records=len(records),
                       duplicates_removed=len(raw) - len(records), output=path, **rm.stats)
    except ScraperError as e:
        errors.record("setup", e)
    summary.update(errors=errors.errors, seconds=round(time.time() - t0, 2),
                   status="completed" if not errors.errors else "completed_with_errors")
    os.makedirs("logs", exist_ok=True)
    with open(os.path.join("logs", f"report_{datetime.now():%Y%m%d_%H%M%S}.json"), "w") as f:
        json.dump(summary, f, indent=2)
    log.info("SCRAPING COMPLETED: %s", json.dumps({k: v for k, v in summary.items() if k != "errors"}))
    return summary

def parse_args():
    p = argparse.ArgumentParser(description="Automation & Web Scraping System")
    p.add_argument("--config"); p.add_argument("--url"); p.add_argument("--item")
    p.add_argument("--field", action="append", default=[], help="name=selector[@attr]")
    p.add_argument("--next"); p.add_argument("--max-pages", type=int, default=5)
    p.add_argument("--format", default="csv", choices=["csv", "json", "sqlite"])
    p.add_argument("--out", default="output"); p.add_argument("--every", type=float)
    p.add_argument("--no-robots", action="store_true")
    a = p.parse_args()
    if a.config:
        cfg = ScraperConfig.from_file(a.config)
    else:
        if not (a.url and a.item and a.field): p.error("--config or --url/--item/--field required")
        cfg = ScraperConfig(url=a.url, item_selector=a.item,
                            fields=dict(f.split("=", 1) for f in a.field), next_page_selector=a.next,
                            max_pages=a.max_pages, output_format=a.format, output_path=a.out,
                            respect_robots=not a.no_robots)
    if a.every: cfg.schedule_minutes = a.every
    return cfg

if __name__ == "__main__":
    cfg = parse_args()
    if cfg.schedule_minutes:
        from scheduler import run_every
        run_every(cfg.schedule_minutes, lambda: run(cfg), get_logger())
    else:
        run(cfg)
