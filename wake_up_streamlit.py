#!/usr/bin/env python3
"""
Wake every URL in URLS:
• open in fresh headless-Chrome with a random User-Agent 
• click the grey “Yes, get this app back up!” button if present
• hold the page ~20 s so the Streamlit WebSocket is established
  (this is what adds a ‘viewer’ in Analytics)
• write a line to wake_log.txt
"""

from __future__ import annotations
import datetime as dt, logging, pathlib, random, time
from typing import Final

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URLS: Final[list[str]] = [
    "https://hikmetc-apscalculator.streamlit.app/",
    "https://verifymylab.streamlit.app/",
    "https://resulttransformer.streamlit.app/",
    "https://hikmetc-qcconstellation.streamlit.app/",
    "https://laberrorfinder.streamlit.app/",
    "https://bvcalculator.streamlit.app/",
]

# ── logging ───────────────────────────────────────────────────────────────────
LOG_FILE = pathlib.Path("wake_log.txt")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
log = logging.getLogger(__name__)


def wake(url: str, driver: webdriver.Chrome) -> None:
    """Visit URL, click Wake-Up button if present, stay connected 20 s."""
    for attempt in range(2):
        try:
            driver.get(url)
            break
        except WebDriverException as e:
            if attempt:
                raise
            time.sleep(2)

    try:
        driver.find_element(
            "xpath", "//button[contains(.,'get this app back up')]"
        ).click()
        log.info("%s – clicked wake button", url)
    except NoSuchElementException:
        log.info("%s – already awake", url)

    # Wait for Streamlit front-end container <div class="stApp">
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(("css selector", "div.stApp"))
        )
    except TimeoutException:
        pass

    time.sleep(5)  # total dwell time ≈ 20 s → counted by Analytics


def make_driver() -> webdriver.Chrome:
    ua = UserAgent()
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    # every run uses a random User-Agent string → unique visitor
    opts.add_argument(f"--user-agent={ua.random}")

    return webdriver.Chrome(service=Service(log_path="/dev/null"), options=opts)


def main() -> None:
    log.info("=== run at %s ===", dt.datetime.now(dt.timezone.utc).isoformat(" ", "seconds"))

    with make_driver() as drv:
        for url in URLS:
            try:
                wake(url, drv)
            except WebDriverException as err:
                log.warning("%s – ERROR %s", url, err)


if __name__ == "__main__":
    main()
