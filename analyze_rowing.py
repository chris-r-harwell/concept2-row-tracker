#!/usr/bin/env python3
"""
Concept2 Rowing Data Analyzer.

Downloads are read from ``~/concept2_detailed_workouts``. The analyzer reports
workout summaries from CSV exports and rhythm/efficiency trends from stroke JSON.

Examples
--------
>>> from pathlib import Path
>>> workout_datetime(Path("workout_2026-07-05_08-11-00_3406m_118201695.csv"))
datetime.datetime(2026, 7, 5, 8, 11)
>>> workout_datetime(Path("strokes_2026-07-05_08-11-00_3406m_118201695.json"))
datetime.datetime(2026, 7, 5, 8, 11)
>>> workout_datetime(Path("not_a_workout.csv")) is None
True
>>> stroke_json_for_csv(Path("workout_2026-07-05_08-11-00_3406m_118201695.csv"))
PosixPath('strokes_2026-07-05_08-11-00_3406m_118201695.json')
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

DOWNLOAD_DIR = Path.home() / "concept2_detailed_workouts"
WORKOUT_FILE_RE = re.compile(
    r"^(?:workout|strokes)_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_\d+m_\d+\.(?:csv|json)$"
)


def workout_datetime(path: Path) -> datetime | None:
    """Parse workout timestamp from downloader filename.

    Filenames look like ``workout_2026-07-05_08-11-00_3406m_118201695.csv``.
    The same timestamp is used for companion stroke JSON files.
    """
    match = WORKOUT_FILE_RE.match(path.name)
    if not match:
        return None
    return datetime.strptime(match.group(1), "%Y-%m-%d_%H-%M-%S")


def stroke_json_for_csv(csv_path: Path) -> Path:
    """Map a workout CSV path to its companion strokes JSON."""
    return csv_path.with_name(
        csv_path.name.replace("workout_", "strokes_").replace(".csv", ".json")
    )


def recent_workout_files(data_dir: Path, limit: int = 8) -> list[Path]:
    """Return the most recent workout CSVs, newest first."""
    files = list(data_dir.glob("*.csv"))
    return sorted(
        files,
        key=lambda p: workout_datetime(p) or datetime.min,
        reverse=True,
    )[:limit]


def compute_csv_metrics(df: pd.DataFrame) -> dict:
    """Compute summary metrics from a Concept2 workout CSV export."""
    duration_min = df["Time (seconds)"].max() / 60
    distance_m = df["Distance (meters)"].max()
    avg_hr = df["Heart Rate"].mean()
    max_hr = df["Heart Rate"].max()
    avg_pace = df["Pace (seconds)"].mean()
    avg_watts = df["Watts"].mean()
    avg_sr = df["Stroke Rate"].mean()

    mid = len(df) // 2
    cardiac_drift = df["Heart Rate"].iloc[mid:].mean() - df["Heart Rate"].iloc[:mid].mean()

    return {
        "duration_min": duration_min,
        "distance_m": distance_m,
        "avg_hr": avg_hr,
        "max_hr": max_hr,
        "avg_pace": avg_pace,
        "avg_watts": avg_watts,
        "avg_sr": avg_sr,
        "cardiac_drift": cardiac_drift,
    }


def format_csv_metrics(name: str, metrics: dict) -> str:
    """Format CSV metrics for terminal output."""
    avg_hr = metrics["avg_hr"]
    max_hr = metrics["max_hr"]
    cardiac_drift = metrics["cardiac_drift"]

    hr_line = (
        f"Avg HR: {avg_hr:.1f} bpm  |  Max: {max_hr:.0f} bpm"
        if pd.notna(avg_hr) and pd.notna(max_hr)
        else "Avg HR: n/a  |  Max: n/a"
    )
    drift_line = (
        f"Cardiac Drift: {cardiac_drift:+.1f} bpm"
        if pd.notna(cardiac_drift)
        else "Cardiac Drift: n/a"
    )

    lines = [
        f"\n🔍 {name}",
        f"Duration: {metrics['duration_min']:.1f} min",
        f"Distance: {metrics['distance_m']:,.1f} m",
        hr_line,
        f"Avg Pace: {metrics['avg_pace']:.1f} s/500m",
        f"Avg Watts: {metrics['avg_watts']:.1f}",
        f"Avg SR: {metrics['avg_sr']:.1f} spm",
        drift_line,
    ]
    return "\n".join(lines)


def analyze_detailed_csv(file_path: Path) -> pd.DataFrame:
    """Analyze one detailed workout CSV and print summary metrics."""
    df = pd.read_csv(file_path)
    metrics = compute_csv_metrics(df)
    print(format_csv_metrics(file_path.name, metrics))
    return df


def compute_stroke_metrics(strokes: list[dict]) -> dict | None:
    """Compute rhythm and fatigue metrics from stroke JSON records.

    Concept2 stroke JSON stores ``t``, ``d``, and ``p`` in tenths of a unit.
    Divide by 10 to get seconds, meters, and seconds per 500 m.
    """
    if len(strokes) < 2:
        return None

    times = [s["t"] / 10 for s in strokes]
    distances = [s["d"] / 10 for s in strokes]
    paces = [s["p"] / 10 for s in strokes if s["p"] > 0]
    stroke_rates = [s["spm"] for s in strokes if s["spm"] > 0]

    stroke_intervals = [
        times[i] - times[i - 1] for i in range(1, len(times)) if times[i] > times[i - 1]
    ]
    distance_per_stroke = [
        distances[i] - distances[i - 1]
        for i in range(1, len(distances))
        if distances[i] > distances[i - 1]
    ]

    mid = len(paces) // 2
    mid_sr = len(stroke_rates) // 2
    pace_series = pd.Series(paces)
    dps_series = pd.Series(distance_per_stroke)
    sr_series = pd.Series(stroke_rates)

    return {
        "stroke_count": len(strokes),
        "avg_interval": pd.Series(stroke_intervals).mean(),
        "interval_std": pd.Series(stroke_intervals).std(),
        "avg_dps": dps_series.mean(),
        "best_dps": max(distance_per_stroke),
        "avg_pace": pace_series.mean(),
        "best_pace": min(paces),
        "worst_pace": max(paces),
        "avg_sr": sr_series.mean(),
        "sr_std": sr_series.std(),
        "pace_drift": pace_series.iloc[mid:].mean() - pace_series.iloc[:mid].mean(),
        "dps_drift": dps_series.iloc[mid:].mean() - dps_series.iloc[:mid].mean(),
        "sr_drift": sr_series.iloc[mid_sr:].mean() - sr_series.iloc[:mid_sr].mean(),
    }


def format_stroke_metrics(name: str, metrics: dict) -> str:
    """Format stroke metrics for terminal output."""
    lines = [
        f"\n🧩 {name}",
        f"Strokes: {metrics['stroke_count']}",
        (
            f"Avg interval: {metrics['avg_interval']:.2f} s  |  "
            f"σ: {metrics['interval_std']:.2f} s"
        ),
        (
            f"Avg DPS: {metrics['avg_dps']:.2f} m  |  "
            f"Best: {metrics['best_dps']:.2f} m"
        ),
        (
            f"Avg pace: {metrics['avg_pace']:.1f} s/500m  |  "
            f"Best: {metrics['best_pace']:.1f}  |  "
            f"Worst: {metrics['worst_pace']:.1f}"
        ),
        (
            f"Avg SR: {metrics['avg_sr']:.1f} spm  |  "
            f"σ: {metrics['sr_std']:.1f}"
        ),
        f"Pace drift (2nd half − 1st): {metrics['pace_drift']:+.1f} s/500m",
        f"DPS drift (2nd half − 1st): {metrics['dps_drift']:+.2f} m",
        f"SR drift (2nd half − 1st): {metrics['sr_drift']:+.1f} spm",
    ]
    return "\n".join(lines)


def analyze_strokes_json(file_path: Path) -> list[dict]:
    """Analyze per-stroke JSON and print rhythm/efficiency metrics."""
    with open(file_path) as f:
        strokes = json.load(f).get("data", [])

    metrics = compute_stroke_metrics(strokes)
    if metrics is None:
        print(f"\n🧩 {file_path.name}")
        print("Not enough stroke data to analyze.")
        return strokes

    print(format_stroke_metrics(file_path.name, metrics))
    return strokes


def main() -> None:
    """Analyze the eight most recent workouts in the download directory."""
    print("🚣 Concept2 Rowing Analyzer\n")
    data_dir = DOWNLOAD_DIR
    csv_files = recent_workout_files(data_dir)

    if not csv_files:
        print("No detailed CSVs found. Run the downloader first!")
        return

    print(f"Found {len(csv_files)} detailed workout files.\n")

    for csv_file in csv_files:
        analyze_detailed_csv(csv_file)
        stroke_json = stroke_json_for_csv(csv_file)
        if stroke_json.exists():
            analyze_strokes_json(stroke_json)
        else:
            print(f"   (no stroke JSON: {stroke_json.name})")

    print("\n✅ Analysis complete! Great work on your consistency.")


if __name__ == "__main__":
    main()