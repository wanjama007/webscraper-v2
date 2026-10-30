"""HTTP communication: session, headers, timeouts, rate limiting, retries."""
import time, requests
from error_handler import is_retryable

class RequestManager:
    def __init__(self, cfg, logger, robots=None):
        self.cfg, self.log, self.robots = cfg, logger, robots
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": cfg.user_agent, **cfg.headers})
        self._last = 0.0
        self.stats = {"requests": 0, "retries": 0}

    def _throttle(self):
        wait = self.cfg.delay_seconds - (time.monotonic() - self._last)
        if wait > 0: time.sleep(wait)
        self._last = time.monotonic()

    def get(self, url: str) -> requests.Response:
        if self.robots and self.cfg.respect_robots:
            self.robots.check(url)
        for attempt in range(self.cfg.max_retries + 1):
            self._throttle()
            self.stats["requests"] += 1
            try:
                r = self.session.get(url, timeout=self.cfg.timeout)
                r.raise_for_status()
                return r
            except Exception as e:   # Retry Manager
                if attempt < self.cfg.max_retries and is_retryable(e):
                    backoff = 2 ** attempt
                    self.stats["retries"] += 1
                    self.log.warning("Retry %d for %s in %ss (%s)", attempt + 1, url, backoff, e)
                    time.sleep(backoff)
                    continue
                raise
