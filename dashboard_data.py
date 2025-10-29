#!/usr/bin/env python3
"""
Generate JSON data for the interactive Mount Diablo Challenge dashboard.
Extracts race statistics and weather data from SQLite database.
"""

import json
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import DiabloDatabase
from analysis import DiabloAnalyzer
import config

def seconds_to_minutes(seconds):
    """Convert seconds to minutes."""
    if seconds is None:
        return None
    return round(seconds / 60, 2)

def seconds_to_mmss(seconds):
    """Convert seconds to MM:SS format."""
    if seconds is None:
        return None
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"

def calculate_correlation(x_values, y_values):
    """Calculate Pearson correlation coefficient."""
    import numpy as np

    # Filter out None values
    valid_pairs = [(x, y) for x, y in zip(x_values, y_values) if x is not None and y is not None]

    if len(valid_pairs) < 2:
        return None

    x = np.array([p[0] for p in valid_pairs])
    y = np.array([p[1] for p in valid_pairs])

    return round(np.corrcoef(x, y)[0, 1], 3)

def generate_dashboard_data():
    """Generate all data needed for the dashboard."""

    print("Connecting to database...")
    analyzer = DiabloAnalyzer()
    db = analyzer.db

    # Get race statistics
    print("Calculating race statistics...")
    stats = analyzer.calculate_yearly_statistics()

    # Get weather statistics
    print("Calculating weather statistics...")
    combined = analyzer.get_combined_statistics()

    # Prepare data structure
    dashboard_data = {
        "race_name": "Mount Diablo Challenge",
        "generated_at": datetime.now().isoformat(),
        "years": [],
        "statistics": {
            "overall": {},
            "by_year": []
        },
        "weather": {
            "by_year": []
        }
    }

    # Process each year
    years = sorted(stats['year'].tolist())
    dashboard_data['years'] = years

    # Calculate overall statistics
    all_median_times = stats['median'].tolist()
    dashboard_data['statistics']['overall'] = {
        "total_years": len(years),
        "year_range": f"{min(years)}-{max(years)}",
        "overall_median_minutes": seconds_to_minutes(sum(all_median_times) / len(all_median_times)),
        "overall_median_formatted": seconds_to_mmss(sum(all_median_times) / len(all_median_times)),
        "fastest_year_by_winner": int(stats.loc[stats['min'].idxmin(), 'year']),
        "fastest_time": seconds_to_mmss(stats['min'].min()),
        "fastest_year_by_median": int(stats.loc[stats['median'].idxmin(), 'year']),
        "fastest_median_time": seconds_to_mmss(stats['median'].min()),
        "total_finishers": int(stats['count'].sum())
    }

    # Process statistics by year
    for _, row in stats.iterrows():
        year = int(row['year'])

        year_data = {
            "year": year,
            "count": int(row['count']),
            "times": {
                "min": seconds_to_minutes(row['min']),
                "p25": seconds_to_minutes(row['p25']),
                "median": seconds_to_minutes(row['median']),
                "mean": seconds_to_minutes(row['mean']),
                "p75": seconds_to_minutes(row['p75']),
                "max": seconds_to_minutes(row['max'])
            },
            "times_formatted": {
                "min": seconds_to_mmss(row['min']),
                "p25": seconds_to_mmss(row['p25']),
                "median": seconds_to_mmss(row['median']),
                "mean": seconds_to_mmss(row['mean']),
                "p75": seconds_to_mmss(row['p75']),
                "max": seconds_to_mmss(row['max'])
            }
        }

        dashboard_data['statistics']['by_year'].append(year_data)

    # Process weather data by year
    for _, row in combined.iterrows():
        year = int(row['year'])

        weather_data = {
            "year": year,
            "start": {
                "wind_speed_avg": round(row.get('windspeed_10m_mean_start', 0), 1) if 'windspeed_10m_mean_start' in row else None,
                "wind_speed_max": round(row.get('windspeed_10m_max_start', 0), 1) if 'windspeed_10m_max_start' in row else None,
                "wind_gust_max": round(row.get('wind_gusts_10m_max_start', 0), 1) if 'wind_gusts_10m_max_start' in row else None,
                "temperature_avg": round(row.get('temperature_2m_mean_start', 0), 1) if 'temperature_2m_mean_start' in row else None,
                "wind_direction_avg": round(row.get('winddirection_10m_mean_start', 0), 1) if 'winddirection_10m_mean_start' in row else None
            },
            "summit": {
                "wind_speed_avg": round(row.get('windspeed_10m_mean_summit', 0), 1) if 'windspeed_10m_mean_summit' in row else None,
                "wind_speed_max": round(row.get('windspeed_10m_max_summit', 0), 1) if 'windspeed_10m_max_summit' in row else None,
                "wind_gust_max": round(row.get('wind_gusts_10m_max_summit', 0), 1) if 'wind_gusts_10m_max_summit' in row else None,
                "temperature_avg": round(row.get('temperature_2m_mean_summit', 0), 1) if 'temperature_2m_mean_summit' in row else None,
                "wind_direction_avg": round(row.get('winddirection_10m_mean_summit', 0), 1) if 'winddirection_10m_mean_summit' in row else None
            }
        }

        dashboard_data['weather']['by_year'].append(weather_data)

    # Calculate wind correlation with median times
    median_times = [row['times']['median'] for row in dashboard_data['statistics']['by_year']]
    summit_wind_speeds = [w['summit']['wind_speed_avg'] for w in dashboard_data['weather']['by_year']]

    wind_correlation = calculate_correlation(summit_wind_speeds, median_times)
    dashboard_data['statistics']['overall']['wind_correlation'] = wind_correlation

    # Extract rider performance data
    print("Extracting rider performance data...")
    riders_data = extract_rider_performances(db, years)
    dashboard_data['riders'] = riders_data
    print(f"  - Found {len(riders_data)} riders with multiple years")

    analyzer.close()

    return dashboard_data

def extract_rider_performances(db, years):
    """
    Extract individual rider performances across multiple years.
    Only includes riders who have participated in 2+ years.
    """
    import pandas as pd

    # Query to get all rider performances
    query = """
        SELECT
            name,
            year,
            chip_time_seconds,
            place,
            gender,
            age
        FROM race_results
        WHERE chip_time_seconds IS NOT NULL
        ORDER BY name, year
    """

    df = pd.read_sql_query(query, db.conn)

    # Group by rider name and count years
    rider_groups = df.groupby('name')

    riders_list = []

    for name, group in rider_groups:
        # Only include riders with 2+ years of data
        if len(group) >= 2:
            performances = []

            for _, row in group.iterrows():
                performances.append({
                    "year": int(row['year']),
                    "time_seconds": round(row['chip_time_seconds'], 1),
                    "time_formatted": seconds_to_mmss(row['chip_time_seconds']),
                    "place": int(row['place']),
                    "gender": row['gender'],
                    "age": int(row['age']) if row['age'] is not None else None
                })

            # Sort performances by year
            performances.sort(key=lambda x: x['year'])

            riders_list.append({
                "name": name,
                "years_participated": len(performances),
                "performances": performances
            })

    # Sort riders by name
    riders_list.sort(key=lambda x: x['name'])

    return riders_list

def main():
    """Main execution."""
    print("="*80)
    print("Generating Dashboard Data")
    print("="*80)

    # Generate data
    data = generate_dashboard_data()

    # Save to JSON file
    output_path = os.path.join(config.DATA_DIR, 'dashboard_data.json')
    os.makedirs(config.DATA_DIR, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✓ Dashboard data saved to: {output_path}")
    print(f"  - Total years: {data['statistics']['overall']['total_years']}")
    print(f"  - Total finishers: {data['statistics']['overall']['total_finishers']}")
    print(f"  - Riders with multiple years: {len(data['riders'])}")
    print(f"  - Fastest year by winner: {data['statistics']['overall']['fastest_year_by_winner']}")
    print(f"  - Fastest year by median: {data['statistics']['overall']['fastest_year_by_median']}")
    print(f"  - Wind correlation: {data['statistics']['overall']['wind_correlation']}")
    print("\nDashboard data generation complete!")

if __name__ == '__main__':
    main()
