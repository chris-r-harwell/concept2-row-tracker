#!/usr/bin/env python3
"""
Concept2 Rowing Data Analyzer
For Chris Harwell - Row Every Day to Fitness Project
Analyzes detailed stroke-by-stroke CSVs with focus on HR trends.
"""

import pandas as pd
from pathlib import Path

def analyze_detailed_csv(file_path):
    """Analyze one detailed workout CSV"""
    df = pd.read_csv(file_path)
    
    print(f"\n🔍 {file_path.name}")
    print(f"Duration: {df['Time (seconds)'].max()/60:.1f} min")
    print(f"Distance: {df['Distance (meters)'].max():,} m")
    print(f"Avg HR: {df['Heart Rate'].mean():.1f} bpm  |  Max: {df['Heart Rate'].max()} bpm")
    print(f"Avg Pace: {df['Pace (seconds)'].mean():.1f} s/500m")
    print(f"Avg Watts: {df['Watts'].mean():.1f}")
    print(f"Avg SR: {df['Stroke Rate'].mean():.1f} spm")
    
    # Cardiac drift
    mid = len(df) // 2
    drift = df['Heart Rate'].iloc[mid:].mean() - df['Heart Rate'].iloc[:mid].mean()
    print(f"Cardiac Drift: +{drift:.1f} bpm")
    
    return df

def main():
    print("🚣 Concept2 Rowing Analyzer\n")
    data_dir = Path("concept2_detailed_workouts")
    csv_files = sorted(list(data_dir.glob("*.csv")))
    
    if not csv_files:
        print("No detailed CSVs found. Run the downloader first!")
        return
    
    print(f"Found {len(csv_files)} detailed workout files.\n")
    
    for csv_file in csv_files[:8]:  # Analyze recent ones
        analyze_detailed_csv(csv_file)
    
    print("\n✅ Analysis complete! Great work on your consistency.")

if __name__ == "__main__":
    main()
