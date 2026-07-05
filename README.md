# Concept2 Row Tracker

Tools for downloading and analyzing detailed Concept2 rowing workout data.

This repository downloads detailed Concept2 workout exports and analyzes both
workout-level CSV summaries and per-stroke JSON rhythm/efficiency trends.

## Scripts

| Script | Purpose |
|--------|---------|
| `concept2_downloader.py` | Download detailed CSV and stroke JSON files from the Concept2 API |
| `analyze_rowing.py` | Analyze the 8 most recent workouts from local files |

## Setup

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Save your Concept2 API token:

   ```bash
   mkdir -p ~/.config/concept2
   echo "YOUR_API_TOKEN_HERE" > ~/.config/concept2/api_key
   ```

3. Download workouts:

   ```bash
   python3 concept2_downloader.py
   ```

4. Analyze recent workouts:

   ```bash
   python3 analyze_rowing.py
   ```

## File Layout

Downloads are saved in `~/concept2_detailed_workouts/` using paired filenames:

```text
workout_2026-07-05_08-11-00_3406m_118201695.csv
strokes_2026-07-05_08-11-00_3406m_118201695.json
```

The timestamp in the filename is the workout date from the Concept2 API.
`analyze_rowing.py` parses that timestamp to select the most recent workouts,
not directory order.

## Glossary

| Term | Meaning |
|------|---------|
| **API** | Application Programming Interface; how this project talks to Concept2 servers |
| **bpm** | Beats per minute; heart rate unit |
| **Cal/Hr** | Calories burned per hour |
| **Cardiac drift** | Heart-rate rise from the first half to the second half of a workout at similar effort |
| **Concept2** | Manufacturer of the rowing ergometer and online logbook used here |
| **CSV** | Comma-Separated Values; spreadsheet-style workout export |
| **DPS** | Distance per stroke; meters covered between consecutive strokes |
| **HR** | Heart rate |
| **JSON** | JavaScript Object Notation; format used for per-stroke data |
| **m** | Meters |
| **min** | Minutes |
| **Pace** | Time required to row 500 meters; lower is faster |
| **spm** | Strokes per minute; also called stroke rate (**SR**) |
| **SR** | Stroke rate; how many strokes you take per minute |
| **σ (sigma)** | Standard deviation; measures variability. Lower usually means more consistent |
| **s/500m** | Seconds per 500 meters; numeric pace format used in the analyzer |
| **Watts** | Power output on the erg |

## What Each Analyzer Reports

### CSV workout summary (`analyze_detailed_csv`)

- **Duration**: total workout time
- **Distance**: total meters rowed
- **Avg HR / Max HR**: average and peak heart rate
- **Avg Pace**: mean pace across the workout
- **Avg Watts**: mean power output
- **Avg SR**: mean stroke rate
- **Cardiac drift**: second-half average HR minus first-half average HR

### Stroke JSON analysis (`analyze_strokes_json`)

Stroke JSON stores cumulative values per stroke:

| JSON field | Stored as | Display unit |
|------------|-----------|--------------|
| `t` | tenths of a second | seconds |
| `d` | tenths of a meter | meters |
| `p` | tenths of a second | seconds per 500 m |
| `spm` | strokes per minute | spm |
| `hr` | beats per minute | bpm (often missing/zero in these exports) |

Reported metrics:

- **Strokes**: number of stroke records
- **Avg interval / σ**: time between strokes and rhythm consistency
- **Avg DPS / Best DPS**: efficiency per stroke
- **Avg pace / Best / Worst**: central tendency and spread
- **Avg SR / σ**: stroke-rate level and consistency
- **Pace drift**: second-half average pace minus first-half average pace
- **DPS drift**: change in distance per stroke from first half to second half
- **SR drift**: change in stroke rate from first half to second half

## How to Read the Numbers

These are practical guides for steady-state fitness rowing, not racing targets.
Your exact ranges depend on session length, recovery, and conditions.

### Pace (`s/500m`)

Lower is faster.

| Trend | Usually good | Worth attention |
|-------|--------------|-----------------|
| Steady-state average | Controlled, repeatable pace for the session distance | Wildly different day-to-day without an obvious reason |
| Best vs worst spread | Small spread during steady work | Very large spread, meaning many surges and recoveries |
| Pace drift | Zero to slightly negative (negative split) | More than about `+8 s/500m` fade in the second half |

Example: `2:00.0 /500m` is shown as `120.0 s/500m`.

### Heart rate and cardiac drift

| Metric | Usually good | Worth attention |
|--------|--------------|-----------------|
| Avg HR for easy aerobic work | Roughly 115-140 bpm for many masters athletes | Session feels hard but HR stays unusually low or spikes early |
| Cardiac drift on longer rows | About `+3` to `+8 bpm` | More than about `+12 bpm`, suggesting the first half was too aggressive |

Cardiac drift is only available when the CSV contains HR data.

### Stroke rate (SR)

| Metric | Usually good | Worth attention |
|--------|--------------|-----------------|
| Steady-state SR | About 18-24 spm for aerobic work | SR climbing sharply while pace fades |
| SR σ | Low variability in steady rows | Very high σ, meaning rate is swinging constantly |

### Distance per stroke (DPS)

| Metric | Usually good | Worth attention |
|--------|--------------|-----------------|
| Avg DPS at moderate SR | Often about 7-10 m for many recreational rowers | DPS falling sharply in the second half |
| DPS drift | Stable or slightly positive | About `-0.5 m` or worse, especially with rising SR |

Rising SR together with falling DPS often means you are working harder for less boat speed.

### Stroke interval rhythm

| Metric | Usually good | Worth attention |
|--------|--------------|-----------------|
| Interval σ | Below about `0.5 s` on steady rows | Above about `1.0 s`, meaning rhythm is uneven |

### Watts

Higher watts mean more power. Compare watts mostly against your own history on
similar workout types, not someone else's numbers.

## Example Interpretation

Good steady-state signs:

- Pace drift near zero or negative
- DPS drift near zero
- Low interval σ
- Cardiac drift under about `+8 bpm`

Fatigue or pacing-risk signs:

- Pace drift more than about `+8 s/500m`
- DPS drift more than about `-0.5 m`
- SR drift more than about `+4 spm` while pace fades
- Cardiac drift more than about `+12 bpm`

## Testing

Run the full unit and doctest suite:

```bash
pytest -v
```

Run only doctests embedded in module docstrings:

```bash
python3 -m doctest analyze_rowing.py
python3 -m doctest concept2_downloader.py
```

Tests use fixtures in `tests/fixtures/` and do not call the live Concept2 API.

## Security

Do not commit secrets or personal information to GitHub.

- Keep your Concept2 API token in `~/.config/concept2/api_key` (outside this repo).
- Workout CSV/JSON exports belong in `~/concept2_detailed_workouts/`, not in git.
- Use placeholders like `YOUR_API_TOKEN_HERE` in docs and examples.

This repo includes a `safe-to-commit` agent skill (`.grok/skills/safe-to-commit/`)
that reminds the coding agent to check for credentials and PII before commits.
Run `/safe-to-commit` or ask the agent to review changes before you push.

## Design Notes

- The downloader skips workouts whose CSV already exists locally.
- The analyzer processes the 8 newest workouts by filename timestamp.
- CSV exports include watts and heart rate; stroke JSON is best for rhythm and
  efficiency trends. When both exist for a workout, the analyzer prints both views.

Built to support consistent rowing, heart-rate tracking, and long-term fitness
progress with a focus on sustainable health.