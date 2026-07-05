from pathlib import Path

import pytest

import concept2_downloader as downloader


def test_format_date_str_normalizes_api_timestamp():
    assert downloader.format_date_str("2026-07-05 08:11:00") == "2026-07-05_08-11-00"


def test_build_workout_paths_uses_expected_names(tmp_path: Path):
    paths = downloader.build_workout_paths(
        "2026-07-05_08-11-00", 3406, 118201695, download_dir=tmp_path
    )

    assert paths["csv"] == tmp_path / "workout_2026-07-05_08-11-00_3406m_118201695.csv"
    assert paths["json"] == tmp_path / "strokes_2026-07-05_08-11-00_3406m_118201695.json"


def test_load_api_token_reads_config_file(tmp_path: Path):
    config_path = tmp_path / "api_key"
    config_path.write_text("secret-token\n")

    assert downloader.load_api_token(config_path) == "secret-token"


def test_load_api_token_exits_when_missing(tmp_path: Path):
    missing = tmp_path / "missing_api_key"

    with pytest.raises(SystemExit) as excinfo:
        downloader.load_api_token(missing)

    assert excinfo.value.code == 1