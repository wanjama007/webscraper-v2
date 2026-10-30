"""Task scheduling: run a job every N minutes (Ctrl+C to stop)."""
import time

def run_every(minutes: float, job, logger):
    logger.info("Scheduler started: every %s min", minutes)
    try:
        while True:
            start = time.monotonic()
            try: job()
            except Exception as e: logger.exception("Scheduled job failed: %s", e)
            time.sleep(max(0, minutes * 60 - (time.monotonic() - start)))
    except KeyboardInterrupt:
        logger.info("Scheduler stopped")
