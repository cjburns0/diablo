# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains comprehensive analysis of the annual Mount Diablo Challenge race, a challenging 11.2-mile cycling climb with 3,249 feet of elevation gain. The project scrapes historical race results, integrates weather data, and provides detailed statistical analysis and visualizations of race performance trends.

## Tech Stack

- **Language**: Python 3.9+
- **Data Collection**: BeautifulSoup4, Requests
- **Data Storage**: SQLite
- **Analysis**: Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Interactive Analysis**: Jupyter Notebooks

## Project Structure

```
diablo/
├── src/                          # Source code modules
│   ├── scraper.py               # Web scraper for race results
│   ├── weather.py               # Open-Meteo API integration
│   ├── database.py              # SQLite database operations
│   └── analysis.py              # Statistical analysis and visualization
├── notebooks/                    # Jupyter notebooks
│   ├── 01_data_collection.ipynb # Interactive data collection demo
│   ├── 02_analysis.ipynb        # Statistical analysis
│   └── 03_visualization.ipynb   # Data visualization
├── data/                        # Data storage
│   └── diablo_challenge.db      # SQLite database
├── output/                      # Generated outputs
│   └── charts/                  # Visualization charts (PNG)
├── config.py                    # Configuration constants
├── main.py                      # Automated pipeline script
└── requirements.txt             # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Full Data Pipeline

Scrape all years, fetch weather, analyze, and generate visualizations:

```bash
python3 main.py
```

### 3. Run Specific Operations

```bash
# Only scrape race results
python3 main.py --scrape-only

# Only fetch weather data (requires existing race data)
python3 main.py --weather-only

# Only run analysis on existing data
python3 main.py --analyze-only

# Process specific years
python3 main.py --years 2024 2025

# Force refresh (clear ALL existing data)
python3 main.py --force
```

### 3b. Update Single Year (Annual Updates)

For ongoing maintenance when new races happen, use the dedicated update script:

```bash
# Add/update a specific year (e.g., when 2026 race finishes)
python3 update_year.py 2026

# This will:
# - Scrape only that year's results
# - Fetch weather data for that year
# - Replace existing data if year already exists
# - Regenerate all charts with updated data
```

**Benefits**:
- Much faster than full pipeline (~30 seconds vs 5-10 minutes)
- Doesn't touch existing historical data
- Automatically replaces if you need to re-scrape a year

### 4. Interactive Analysis

Launch Jupyter notebooks for interactive exploration:

```bash
jupyter notebook notebooks/
```

## Data Sources

### Race Results
- **Source**: https://mountdiablochallenge.itsyourrace.com/Results.aspx
- **Years Available**: 2018, 2019, 2021-2025 (2020 missing due to COVID)
- **Data Points**: Place, Name, Team, City/State, Gender, Age, Chip Time, Pace, Start Time

### Weather Data
- **API**: Open-Meteo Historical Weather API (free, no API key required)
- **Locations**:
  - Start (37.885°N, -122.059°W)
  - Summit (37.881°N, -121.914°W)
- **Time Window**: 7 AM - 11 AM (race window)
- **Frequency**: Hourly intervals
- **Variables**: Temperature, Wind Speed, Wind Direction, Wind Gusts

## Database Schema

### race_results
```sql
- id: INTEGER PRIMARY KEY
- year: INTEGER
- race_date: DATE
- place: INTEGER
- name: TEXT
- team: TEXT
- city_state: TEXT
- gender: TEXT
- gender_place: TEXT
- age: INTEGER
- age_place: TEXT
- chip_time_str: TEXT
- chip_time_seconds: REAL
- pace: TEXT
- start_time: TEXT
- created_at: TIMESTAMP
```

### weather_data
```sql
- id: INTEGER PRIMARY KEY
- year: INTEGER
- race_date: DATE
- timestamp: TIMESTAMP
- location: TEXT (start/summit)
- temperature_2m: REAL
- windspeed_10m: REAL
- winddirection_10m: REAL
- wind_gusts_10m: REAL
- created_at: TIMESTAMP
```

## Key Modules

### scraper.py (src/scraper.py)
- `DiabloScraper`: Main scraper class
  - Handles ASP.NET ViewState for form navigation
  - Scrapes all years and pages
  - Extracts race dates
  - Converts chip times to seconds

### weather.py (src/weather.py)
- `WeatherFetcher`: Weather data fetcher
  - Integrates with Open-Meteo API
  - Fetches hourly data for race window
  - Supports both start and summit locations
  - Calculates weather summaries

### database.py (src/database.py)
- `DiabloDatabase`: SQLite database handler
  - Creates schema
  - Insert/query operations
  - Calculates statistics
  - Manages data integrity

### analysis.py (src/analysis.py)
- `DiabloAnalyzer`: Statistical analysis and visualization
  - Year-over-year statistics (mean, median, percentiles)
  - Weather correlation analysis
  - Publication-quality charts
  - Export functionality

## Analysis Features

### Statistical Analysis
- Mean, median, and percentile calculations by year
- Distribution analysis
- Weather correlation with performance
- Demographic analysis (age, gender)

### Visualizations
1. **Yearly Time Distribution**: Mean, median, 25th/75th percentiles over time
2. **Performance vs Wind**: Chip times with wind speed overlay
3. **Weather Comparison**: Start vs summit conditions
4. **Custom Dashboards**: Multi-panel comprehensive analysis

## Configuration

Edit `config.py` to customize:
- Database path
- Weather API settings
- Coordinates (start/summit)
- Race time window
- Visualization settings
- Output directories

## Important Notes

### Weather Data
- **Wind speed is the primary focus** - it's the most significant weather factor affecting race performance
- Data collected for both start and summit locations to capture elevation-dependent conditions
- Hourly granularity provides detailed view of changing conditions during race

### Data Collection
- Web scraping respects rate limits (0.5-1 second delays between requests)
- ASP.NET ViewState handled automatically for pagination
- Robust error handling and logging

### Performance
- Full pipeline (all years) takes ~5-10 minutes
- Database enables fast querying and analysis
- Charts generated at 300 DPI for publication quality

## Future Enhancements

- [ ] Apply aura.build design template for dashboard styling
- [ ] Create interactive Plotly/Dash dashboards
- [ ] Add predictive modeling (race time prediction based on weather)
- [ ] Export data for web visualization
- [ ] Automated data refresh (cron job)
- [ ] Add more weather variables (humidity, precipitation)
- [ ] Correlation analysis between training data and race performance

## Troubleshooting

### Common Issues

**ImportError for modules**:
```bash
pip install -r requirements.txt
```

**Database locked**:
Close any open database connections or delete `data/diablo_challenge.db` and re-run.

**Scraping fails**:
- Check internet connection
- Verify race results URL is still valid
- Website structure may have changed - update scraper.py

**No weather data**:
- Open-Meteo API may be down
- Check date format is correct
- Verify coordinates are valid

## Contact & Contribution

For issues, enhancements, or questions about the analysis, please refer to the project repository.
