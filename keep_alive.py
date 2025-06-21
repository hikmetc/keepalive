#!/usr/bin/env python3
"""
wake_up_streamlit.py
────────────────────
For every URL in URLS…

1. open the page in a headless Chrome session
2. click the grey “Wake up” button (text: ‘Yes, get this app back up!’)
   – if it isn’t there, the app is already awake
3. wait 5 s so the WebSocket connects
4. log the outcome

Designed for GitHub Actions’ ubuntu-latest runner (Chrome pre-installed).
"""

from __future__ import annotations

import datetime as dt
import logging
import pathlib
import time
from typing import Final

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options

URLS: Final[list[str]] = [
    "https://hikmetc-apscalculator.streamlit.app/",
    "https://verifymylab.streamlit.app/",
    "https://resulttransformer.streamlit.app/",
    "https://hikmetc-qcconstellation.streamlit.app/",
    "https://laberrorfinder.streamlit.app/",
    "https://bvcalculator.streamlit.app/",
]

# ---------- logging ----------------------------------------------------------
LOG_FILE = pathlib.Path("wake_log.txt")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)
log = logging.getLogger(__name__)

# ---------- core helpers -----------------------------------------------------
def wake(url: str, driver: webdriver.Chrome) -> None:
    """Visit *url*; click the Wake-Up button if present."""
    for attempt in range(2):  # one retry if navigation fails
        try:
            driver.get(url)
            break
        except WebDriverException as e:
            if attempt:
                raise
            time.sleep(2)

    try:
        btn = driver.find_element(
            "xpath", "//button[contains(.,'get this app back up')]"
        )
        btn.click()
        log.info("%s – clicked wake button", url)
    except NoSuchElementException:
        log.info("%s – already awake", url)

    time.sleep(5)  # allow websocket & script load


def main() -> None:
    log.info("=== run at %s ===", dt.datetime.now(dt.timezone.utc).isoformat(" ", "seconds"))

    chrome_opts = Options()
    chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-gpu")  # safer on some runners

    with webdriver.Chrome(options=chrome_opts) as drv:
        for url in URLS:
            try:
                wake(url, drv)
            except WebDriverException as err:
                log.warning("%s – ERROR %s", url, err)


if __name__ == "__main__":
    main()
