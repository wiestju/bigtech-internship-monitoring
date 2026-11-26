"""HTTP helpers shared by the job scrapers."""
import logging
import time

import requests

logger = logging.getLogger(__name__)

RETRY_STATUS = {429, 500, 502, 503, 504}


def get_with_retry(url, attempts=3, backoff=5, **kwargs):
    """GET with a few retries on rate limits and server errors.

    Waits for Retry-After when the server sends it (capped at 60 s), otherwise
    backoff, 2*backoff, ... seconds. Raises like requests.get on final failure.
    """
    for attempt in range(1, attempts + 1):
        r = requests.get(url, **kwargs)
        if r.status_code not in RETRY_STATUS or attempt == attempts:
            r.raise_for_status()
            return r
        retry_after = r.headers.get("Retry-After", "")
        wait = min(int(retry_after), 60) if retry_after.isdigit() else backoff * attempt
        logger.warning(f"HTTP {r.status_code} from {url}, retry {attempt}/{attempts - 1} in {wait}s")
        time.sleep(wait)
