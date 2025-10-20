# scrape.py
import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timezone
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://www.atl.com/times"
OUT_DIR = "data"
OUT_CSV = os.path.join(OUT_DIR, "atl_tsa_wait_times.csv")

os.makedirs(OUT_DIR, exist_ok=True)

def fetch_times():
    # Lightly identify ourselves; some sites dislike default python UA.
    headers = {"User-Agent": "ATL TSA Wait Times Bot (+https://github.com/<your-username>/atl-tsa-wait-times)"}
    resp = requests.get(URL, headers=headers, timeout=30, verify=False)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    rows = []

    # DOMESTIC (left column)
    for section in soup.find_all("div", class_="col-lg-4"):
        for h2 in section.find_all("h2"):
            span = h2.find_next("span")
            if span and span.get_text(strip=True).isdigit():
                rows.append({
                    "region": "DOMESTIC",
                    "checkpoint": h2.get_text(strip=True),
                    "wait_time": int(span.get_text(strip=True)),
                })

    # INT'L (right column)
    for section in soup.find_all("div", class_="col-lg-5"):
        for h2 in section.find_all("h2"):
            span = h2.find_next("span")
            if span and span.get_text(strip=True).isdigit():
                rows.append({
                    "region": "INTL",
                    "checkpoint": h2.get_text(strip=True),
                    "wait_time": int(span.get_text(strip=True)),
                })

    # Stamp in UTC so it’s consistent in CI
    ts = datetime.now(timezone.utc).replace(microsecond=0)
    for r in rows:
        r["timestamp_utc"] = ts.isoformat()

    return pd.DataFrame(rows)

def main():
    df = fetch_times()
    print(df)

    file_exists = os.path.isfile(OUT_CSV)
    df.to_csv(OUT_CSV, mode="a", index=False, header=not file_exists)
    print(f"Appended {len(df)} rows to {OUT_CSV}")

if __name__ == "__main__":
    main()
