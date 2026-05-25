#!/usr/bin/env python3
"""
Concept2 Per-Workout Detailed Data Downloader
Improved: Skips existing files + better organization
"""

import requests
import time
import json
from pathlib import Path

# ========================= CONFIGURATION =========================
CONFIG_PATH = Path.home() / ".config" / "concept2" / "api_key"

DOWNLOAD_DIR = Path.home() / "concept2_detailed_workouts"
DOWNLOAD_DIR.mkdir(exist_ok=True)

RATE_LIMIT_DELAY = 1.1
# ================================================================


def load_api_token():
    if not CONFIG_PATH.exists():
        print(f"❌ Token not found at {CONFIG_PATH}")
        raise SystemExit(1)
    return CONFIG_PATH.read_text().strip()


def main():
    print("🚣 Concept2 Per-Workout Downloader Starting...\n")
    API_TOKEN = load_api_token()

    headers = {"Authorization": f"Bearer {API_TOKEN}", "Accept": "application/json"}

    session = requests.Session()
    session.headers.update(headers)

    # Fetch workout list
    workouts = []
    page = 1
    while True:
        resp = session.get(
            f"https://log.concept2.com/api/users/me/results?page={page}&per_page=50"
        )
        if resp.status_code != 200:
            print(f"Error fetching list: {resp.status_code}")
            break
        data = resp.json().get("data", [])
        workouts.extend(data)
        print(f"Fetched page {page}: {len(data)} workouts")
        if len(data) < 50:
            break
        page += 1
        time.sleep(RATE_LIMIT_DELAY)

    print(f"\nTotal workouts found: {len(workouts)}\n")

    # Download detailed data
    successful = 0
    skipped = 0

    for w in workouts:
        wid = w.get("id")
        if not wid:
            continue

        date_str = w.get("date", "unknown").replace(":", "-").replace(" ", "_")
        distance = w.get("distance", 0)

        # Define filenames
        csv_filename = DOWNLOAD_DIR / f"workout_{date_str}_{distance}m_{wid}.csv"
        json_filename = DOWNLOAD_DIR / f"strokes_{date_str}_{distance}m_{wid}.json"

        # Skip if CSV already exists
        if csv_filename.exists():
            print(f"⏭️  Skipping (already exists): {date_str} ({distance}m)")
            skipped += 1
            continue

        print(f"📥 Processing: {date_str} ({distance}m) ...")

        # Try CSV export first (preferred)
        csv_url = f"https://log.concept2.com/api/users/me/results/{wid}/export/csv"
        resp = session.get(csv_url)

        if resp.status_code == 200:
            with open(csv_filename, "wb") as f:
                f.write(resp.content)
            print(f"   ✅ Saved detailed CSV!")
            successful += 1
        else:
            print(f"   ⚠️  CSV failed (Status {resp.status_code})")

        # Optional: Also save strokes as JSON
        strokes_url = f"https://log.concept2.com/api/users/me/results/{wid}/strokes"
        resp = session.get(strokes_url)
        if resp.status_code == 200 and not json_filename.exists():
            with open(json_filename, "w") as f:
                json.dump(resp.json(), f, indent=2)
            print(f"   ✅ Saved strokes JSON")

        time.sleep(RATE_LIMIT_DELAY)

    print(f"\n🎉 Download complete!")
    print(f"   ✅ New files downloaded: {successful}")
    print(f"   ⏭️  Skipped (already existed): {skipped}")
    print(f"   📁 All files saved in: {DOWNLOAD_DIR.resolve()}")


if __name__ == "__main__":
    main()
