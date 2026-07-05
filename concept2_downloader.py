#!/usr/bin/env python3
"""
Concept2 Per-Workout Detailed Data Downloader.

Fetches workout lists from the Concept2 API and saves detailed CSV exports plus
optional per-stroke JSON for each workout.

Examples
--------
>>> format_date_str("2026-07-05 08:11:00")
'2026-07-05_08-11-00'
>>> paths = build_workout_paths("2026-07-05_08-11-00", 3406, 118201695)
>>> paths["csv"].name
'workout_2026-07-05_08-11-00_3406m_118201695.csv'
>>> paths["json"].name
'strokes_2026-07-05_08-11-00_3406m_118201695.json'
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import requests

CONFIG_PATH = Path.home() / ".config" / "concept2" / "api_key"
DOWNLOAD_DIR = Path.home() / "concept2_detailed_workouts"
RATE_LIMIT_DELAY = 1.1


def format_date_str(date_value: str) -> str:
    """Normalize an API workout date for use in local filenames."""
    return date_value.replace(":", "-").replace(" ", "_")


def build_workout_paths(
    date_str: str,
    distance: int,
    workout_id: int,
    download_dir: Path = DOWNLOAD_DIR,
) -> dict[str, Path]:
    """Build CSV and stroke JSON paths for one workout."""
    base = f"{date_str}_{distance}m_{workout_id}"
    return {
        "csv": download_dir / f"workout_{base}.csv",
        "json": download_dir / f"strokes_{base}.json",
    }


def load_api_token(config_path: Path = CONFIG_PATH) -> str:
    """Read the Concept2 API token from disk."""
    if not config_path.exists():
        print(f"❌ Token not found at {config_path}")
        raise SystemExit(1)
    return config_path.read_text().strip()


def main() -> None:
    """Download detailed workout files that are not already saved locally."""
    print("🚣 Concept2 Per-Workout Downloader Starting...\n")
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    api_token = load_api_token()

    headers = {"Authorization": f"Bearer {api_token}", "Accept": "application/json"}

    session = requests.Session()
    session.headers.update(headers)

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

    successful = 0
    skipped = 0

    for workout in workouts:
        workout_id = workout.get("id")
        if not workout_id:
            continue

        date_str = format_date_str(workout.get("date", "unknown"))
        distance = workout.get("distance", 0)
        paths = build_workout_paths(date_str, distance, workout_id)

        if paths["csv"].exists():
            print(f"⏭️  Skipping (already exists): {date_str} ({distance}m)")
            skipped += 1
            continue

        print(f"📥 Processing: {date_str} ({distance}m) ...")

        csv_url = (
            f"https://log.concept2.com/api/users/me/results/{workout_id}/export/csv"
        )
        resp = session.get(csv_url)

        if resp.status_code == 200:
            with open(paths["csv"], "wb") as f:
                f.write(resp.content)
            print("   ✅ Saved detailed CSV!")
            successful += 1
        else:
            print(f"   ⚠️  CSV failed (Status {resp.status_code})")

        strokes_url = (
            f"https://log.concept2.com/api/users/me/results/{workout_id}/strokes"
        )
        resp = session.get(strokes_url)
        if resp.status_code == 200 and not paths["json"].exists():
            with open(paths["json"], "w") as f:
                json.dump(resp.json(), f, indent=2)
            print("   ✅ Saved strokes JSON")

        time.sleep(RATE_LIMIT_DELAY)

    print("\n🎉 Download complete!")
    print(f"   ✅ New files downloaded: {successful}")
    print(f"   ⏭️  Skipped (already existed): {skipped}")
    print(f"   📁 All files saved in: {DOWNLOAD_DIR.resolve()}")


if __name__ == "__main__":
    main()