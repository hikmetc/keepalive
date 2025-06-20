#!/usr/bin/env python3
"""
keep_alive.py
Ping a list of Streamlit apps once.

The script is intentionally a *single* run; GitHub Actions' scheduler
will call it again at the interval you set in keep-alive.yml.
"""
from __future__ import annotations
import datetime as _dt
import logging
import sys
from pathlib import Path

try:
    import requests
except ModuleNotFoundError:          # just in case
    sys.stderr.write("Installing requests…\n")
    import subprocess, sys as _sys
    subprocess.check_call([_sys.executable, "-m", "pip", "install", "requests"])
    import requests                 # noqa: E402

URLS = [
    "https://hikmetc-apscalculator.streamlit.app/",
    "https://verifymylab.streamlit.app/",
    "https://resulttransformer.streamlit.app/",
    "https://hikmetc-qcconstellation.streamlit.app/",
    "https://laberrorfinder.streamlit.app/",
    "https://bvcalculator.streamlit.app/",
]

LOG_FILE = Path("ping.log")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s  %(levelname)s  %(message)s",
                    handlers=[logging.FileHandler(LOG_FILE, "a"),
                              logging.StreamHandler(sys.stdout)])

def ping(url: str) -> None:
    try:
        r = requests.get(url, timeout=30)
        logging.info("%s → %s", url, r.status_code)
    except Exception as exc:
        logging.warning("%s → ERROR %s", url, exc)

def main() -> None:
    logging.info("=== keep-alive run at %s ===", _dt.datetime.utcnow().isoformat(" ", "seconds"))
    for u in URLS:
        ping(u)

if __name__ == "__main__":
    main()
