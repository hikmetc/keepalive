#!/usr/bin/env python3
"""
wake_up_streamlit.py
Open each Streamlit URL in a headless Chrome,
click the 'Wake up' button if present, wait 5 s,
then quit.  Tested June 2025.
"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import time, logging, pathlib, datetime as dt

URLS = [
    "https://hikmetc-apscalculator.streamlit.app/",
    "https://verifymylab.streamlit.app/",
    "https://resulttransformer.streamlit.app/",
    "https://hikmetc-qcconstellation.streamlit.app/",
    "https://laberrorfinder.streamlit.app/",
    "https://bvcalculator.streamlit.app/",
]

log_file = pathlib.Path("wake_log.txt")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)

def wake(url: str, driver: webdriver.Chrome) -> None:
    driver.get(url)
    try:
        # the button has text “Yes, get this app back up!”
        btn = driver.find_element("xpath", "//button[contains(.,'get this app back up')]")
        btn.click()
        logging.info("%s – clicked wake button", url)
    except NoSuchElementException:
        logging.info("%s – already awake", url)
    time.sleep(5)  # let the websocket establish

def main():
    logging.info("=== run at %s ===", dt.datetime.now(dt.timezone.utc).isoformat())
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    with webdriver.Chrome(options=opts) as drv:
        for u in URLS:
            try:
                wake(u, drv)
            except WebDriverException as e:
                logging.warning("%s – ERROR %s", u, e)

if __name__ == "__main__":
    main()
