"""Configuration Manager: settings and scraper rules."""
import json
from dataclasses import dataclass, field, asdict

@dataclass
class ScraperConfig:
    url: str
    item_selector: str                       # CSS selector for each record
    fields: dict                             # name -> "css selector" or "css selector@attr"
    next_page_selector: str | None = None    # CSS selector for "next" link
    max_pages: int = 5
    output_format: str = "csv"               # csv | json | sqlite
    output_path: str = "output"
    timeout: float = 15.0
    max_retries: int = 3
    delay_seconds: float = 1.0               # rate limit between requests
    respect_robots: bool = True
    user_agent: str = "PyScraper/1.0 (+contact@example.com)"
    headers: dict = field(default_factory=dict)
    schedule_minutes: int | None = None      # run repeatedly every N minutes

    @classmethod
    def from_file(cls, path: str) -> "ScraperConfig":
        with open(path, encoding="utf-8") as f:
            return cls(**json.load(f))

    def to_dict(self) -> dict:
        return asdict(self)
