"""Logging: execution tracking to console and file."""
import logging, os

def get_logger(name="scraper", log_dir="logs") -> logging.Logger:
    os.makedirs(log_dir, exist_ok=True)
    log = logging.getLogger(name)
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    for h in (logging.StreamHandler(), logging.FileHandler(os.path.join(log_dir, "scraper.log"), encoding="utf-8")):
        h.setFormatter(fmt); log.addHandler(h)
    return log
