#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt, logging, pathlib, time
from typing import Final

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    NoSuchElementException,
    WebDriverException,
    TimeoutException,
)
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

LOG_FILE = pathlib.Path("wake_log.txt")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
)
log = logging.getLogger(__name__)


def wake(url: str, driver: webdriver.Chrome) -> None:
    """Open URL, click Wake-Up button if present, wait for websocket open."""
    for attempt in range(2):
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

    # Wait until Streamlit websocket handshake (network idle ≈ page loaded)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(("css selector", "div.stApp"))
        )
    except TimeoutException:
        pass  # still fine; the request itself woke the app


def main() -> None:
    log.info("=== run at %s ===", dt.datetime.now(dt.timezone.utc).isoformat(" ", "seconds"))

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")

    service = Service(log_path="/dev/null")  # mute chromedriver logs
    with webdriver.Chrome(service=service, options=opts) as drv:
        for url in URLS:
            try:
                wake(url, drv)
            except WebDriverException as err:
                log.warning("%s – ERROR %s", url, err)


if __name__ == "__main__":
    main()
