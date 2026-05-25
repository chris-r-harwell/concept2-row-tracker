# Concept2 Row Tracker

Personal rowing data tools for **Chris Harwell** (Age 52, Hashimoto's Thyroiditis).

**Project Goal**: "Row Every Day to Fitness"

## Features

- `concept2_downloader.py` — Automatically downloads detailed stroke-by-stroke workout data (including Heart Rate) from Concept2 API
- Smart duplicate detection (skips files already downloaded)
- Organized file naming by date + distance

## Setup

1. Make sure your API token is set:
   ```bash
   mkdir -p ~/.config/concept2
   echo "YOUR_API_TOKEN_HERE" > ~/.config/concept2/api_key
   ```

2. Run the downloader:
   ```python3 concept2_downloader.py```

3. Files
    Detailed CSVs are saved in concept2_detailed_workouts/

Built to support consistent rowing, HR tracking, and long-term fitness progress with a focus on sustainable health.

