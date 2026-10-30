"""Input validation: URL, configuration and permissions (robots.txt)."""
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from error_handler import ValidationError, PermissionDenied

FORMATS = {"csv", "json", "sqlite"}

def validate_url(url: str) -> None:
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.netloc:
        raise ValidationError(f"Invalid URL: {url!r}")

def validate_config(cfg) -> None:
    validate_url(cfg.url)
    if not cfg.item_selector:
        raise ValidationError("item_selector is required")
    if not cfg.fields:
        raise ValidationError("fields must define at least one field")
    if cfg.output_format not in FORMATS:
        raise ValidationError(f"output_format must be one of {FORMATS}")
    if cfg.max_pages < 1 or cfg.max_retries < 0 or cfg.timeout <= 0:
        raise ValidationError("max_pages>=1, max_retries>=0, timeout>0 required")

class RobotsChecker:
    """Access & Compliance: caches robots.txt per host."""
    def __init__(self, user_agent: str):
        self.ua, self.cache = user_agent, {}

    def check(self, url: str) -> None:
        p = urlparse(url); base = f"{p.scheme}://{p.netloc}"
        if base not in self.cache:
            rp = RobotFileParser(urljoin(base, "/robots.txt"))
            try: rp.read()
            except Exception: rp = None   # unreachable robots.txt => allow
            self.cache[base] = rp
        rp = self.cache[base]
        if rp is not None and not rp.can_fetch(self.ua, url):
            raise PermissionDenied(f"robots.txt disallows {url}")
