#!/usr/bin/env python3
"""
Concept2 Rowing Data Analyzer
For Chris Harwell - Row Every Day to Fitness Project
Analyzes detailed stroke-by-stroke CSVs with focus on HR trends.
"""

import re
from datetime import datetime

import pandas as pd
from pathlib import Path

DOWNLOAD_DIR = Path.home() / "concept2_detailed_workouts"
WORKOUT_CSV_RE = re.compile(
    r"^workout_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_\d+m_\d+\.csv$"
)


def workout_datetime(path: Path) -> datetime | None:
    """Parse workout timestamp from downloader filename."""
    match = WORKOUT_CSV_RE.match(path.name)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y-%m-%d_%H-%M-%S")


def recent_workout_files(data_dir: Path, limit: int = 8) -> list[Path]:
    """Return the most recent workout CSVs, newest first."""
    files = list(data_dir.glob("*.csv"))
    return sorted(
        files,
        key=lambda p: workout_datetime(p) or datetime.min,
        reverse=True,
    )[:limit]

def analyze_detailed_csv(file_path):
    """Analyze one detailed workout CSV"""
    df = pd.read_csv(file_path)

    print(f"\n🔍 {file_path.name}")
    print(f"Duration: {df['Time (seconds)'].max()/60:.1f} min")
    print(f"Distance: {df['Distance (meters)'].max():,} m")
    print(
        f"Avg HR: {df['Heart Rate'].mean():.1f} bpm  |  Max: {df['Heart Rate'].max()} bpm"
    )
    print(f"Avg Pace: {df['Pace (seconds)'].mean():.1f} s/500m")
    print(f"Avg Watts: {df['Watts'].mean():.1f}")
    print(f"Avg SR: {df['Stroke Rate'].mean():.1f} spm")

    # Cardiac drift
    mid = len(df) // 2
    drift = df["Heart Rate"].iloc[mid:].mean() - df["Heart Rate"].iloc[:mid].mean()
    print(f"Cardiac Drift: +{drift:.1f} bpm")

    return df


def main():
    print("🚣 Concept2 Rowing Analyzer\n")
    data_dir = DOWNLOAD_DIR
    csv_files = recent_workout_files(data_dir)

    if not csv_files:
        print("No detailed CSVs found. Run the downloader first!")
        return

    print(f"Found {len(csv_files)} detailed workout files.\n")

    for csv_file in csv_files:
        analyze_detailed_csv(csv_file)

    print("\n✅ Analysis complete! Great work on your consistency.")


if __name__ == "__main__":
    main()
