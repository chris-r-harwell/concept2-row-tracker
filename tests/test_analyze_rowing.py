import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest

import analyze_rowing as ar

FIXTURES = Path(__file__).parent / "fixtures"


def test_workout_datetime_parses_csv_and_json_names():
    csv_path = Path("workout_2026-07-05_08-11-00_3406m_118201695.csv")
    json_path = Path("strokes_2026-07-05_08-11-00_3406m_118201695.json")
    expected = datetime(2026, 7, 5, 8, 11)

    assert ar.workout_datetime(csv_path) == expected
    assert ar.workout_datetime(json_path) == expected


def test_workout_datetime_rejects_unknown_names():
    assert ar.workout_datetime(Path("random.csv")) is None
    assert ar.workout_datetime(Path("summary_2026-07-05.json")) is None


def test_stroke_json_for_csv_maps_companion_file():
    csv_path = Path("workout_2026-07-05_08-11-00_3406m_118201695.csv")
    assert ar.stroke_json_for_csv(csv_path).name == (
        "strokes_2026-07-05_08-11-00_3406m_118201695.json"
    )


def test_recent_workout_files_sorts_newest_first(tmp_path: Path):
    older = tmp_path / "workout_2020-03-16_18-42-00_500m_1.csv"
    newer = tmp_path / "workout_2026-07-05_08-11-00_3000m_2.csv"
    middle = tmp_path / "workout_2024-01-01_12-00-00_1000m_3.csv"
    for path in (older, newer, middle):
        path.write_text("Number,Time (seconds)\n1,1.0\n")

    recent = ar.recent_workout_files(tmp_path, limit=2)
    assert [p.name for p in recent] == [newer.name, middle.name]


def test_compute_csv_metrics_from_fixture():
    df = pd.read_csv(FIXTURES / "sample_workout.csv")
    metrics = ar.compute_csv_metrics(df)

    assert metrics["duration_min"] == pytest.approx(29.0 / 60)
    assert metrics["distance_m"] == pytest.approx(75.0)
    assert metrics["avg_hr"] == pytest.approx(129.0)
    assert metrics["max_hr"] == pytest.approx(138.0)
    assert metrics["avg_pace"] == pytest.approx(df["Pace (seconds)"].mean())
    assert metrics["cardiac_drift"] == pytest.approx(10.0)


def test_format_csv_metrics_handles_missing_hr():
    metrics = {
        "duration_min": 10.0,
        "distance_m": 1000.0,
        "avg_hr": float("nan"),
        "max_hr": float("nan"),
        "avg_pace": 180.0,
        "avg_watts": 100.0,
        "avg_sr": 22.0,
        "cardiac_drift": float("nan"),
    }
    output = ar.format_csv_metrics("workout.csv", metrics)

    assert "Avg HR: n/a" in output
    assert "Cardiac Drift: n/a" in output


def test_compute_stroke_metrics_from_fixture():
    strokes = json.loads((FIXTURES / "sample_strokes.json").read_text())["data"]
    metrics = ar.compute_stroke_metrics(strokes)

    assert metrics is not None
    assert metrics["stroke_count"] == 10
    assert metrics["avg_interval"] == pytest.approx(2.789, rel=1e-2)
    assert metrics["avg_dps"] == pytest.approx(7.46, rel=1e-2)
    assert metrics["best_dps"] == pytest.approx(8.0)
    assert metrics["avg_pace"] == pytest.approx(200.18, rel=1e-2)
    assert metrics["best_pace"] == pytest.approx(180.0)
    assert metrics["worst_pace"] == pytest.approx(270.9)
    assert metrics["avg_sr"] == pytest.approx(21.33, rel=1e-2)


def test_compute_stroke_metrics_returns_none_for_short_data():
    assert ar.compute_stroke_metrics([]) is None
    assert ar.compute_stroke_metrics([{"t": 10, "d": 20, "p": 1000, "spm": 20}]) is None


def test_analyze_detailed_csv_prints_summary(capsys):
    df = ar.analyze_detailed_csv(FIXTURES / "sample_workout.csv")
    output = capsys.readouterr().out

    assert "sample_workout.csv" in output
    assert "Distance: 75.0 m" in output
    assert "Cardiac Drift: +10.0 bpm" in output
    assert len(df) == 10


def test_analyze_strokes_json_prints_summary(capsys):
    strokes = ar.analyze_strokes_json(FIXTURES / "sample_strokes.json")
    output = capsys.readouterr().out

    assert "sample_strokes.json" in output
    assert "Strokes: 10" in output
    assert "Pace drift" in output
    assert len(strokes) == 10