# Mount Diablo Challenge Race Analysis

Comprehensive analysis of the annual Mount Diablo Challenge race - an 11.2-mile cycling climb with 3,249 feet of elevation gain.

## Overview

This project provides complete data pipeline and analysis for the Mount Diablo Challenge race:

- **Web Scraping**: Automated collection of race results from all available years (2018-2025)
- **Weather Integration**: Historical weather data from Open-Meteo API (free, no API key needed)
- **Database Storage**: SQLite database for efficient data management
- **Statistical Analysis**: Year-over-year trends, distributions, and correlations
- **Visualization**: Publication-quality charts and interactive dashboards

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Full Pipeline

Scrape all years, fetch weather data, and generate analysis:

```bash
python3 main.py
```

This will:
- Scrape race results from years 2018, 2019, 2021-2025
- Fetch hourly weather data for race dates (7 AM - 11 AM window)
- Store everything in SQLite database
- Generate statistical analysis
- Create publication-quality visualizations in `output/charts/`

### 3. Explore Data Interactively

```bash
jupyter notebook notebooks/
```

Three comprehensive notebooks available:
- `01_data_collection.ipynb` - Data scraping and storage
- `02_analysis.ipynb` - Statistical analysis
- `03_visualization.ipynb` - Custom visualizations

## Project Structure

```
diablo/
├── src/
│   ├── scraper.py          # Web scraping logic
│   ├── weather.py          # Weather API integration
│   ├── database.py         # SQLite operations
│   └── analysis.py         # Statistical analysis
├── notebooks/              # Jupyter notebooks
├── data/
│   └── diablo_challenge.db # SQLite database
├── output/
│   └── charts/             # Generated visualizations
├── config.py               # Configuration
├── main.py                 # Main pipeline script
└── requirements.txt        # Dependencies
```

## Features

### Data Collection
- Scrapes all race results from itsyourrace.com
- Handles ASP.NET ViewState and pagination automatically
- Extracts: Place, Name, Team, Age, Gender, Chip Time, etc.
- Fetches historical weather (temperature, wind speed, gusts)
- Collects data for both start and summit locations

### Analysis
- Year-over-year performance trends
- Mean, median, and percentile statistics
- Weather correlation with race times
- **Heavy focus on wind speed** (primary performance factor)
- Demographic analysis (age, gender)

### Visualizations
- Yearly time distribution (mean, median, percentiles)
- Performance vs wind conditions
- Weather comparison (start vs summit)
- Custom multi-panel dashboards

## Command Line Options

### Full Pipeline

```bash
# Run complete pipeline (scrape all years, fetch weather, analyze)
python3 main.py

# Specific operations
python3 main.py --scrape-only      # Only scrape race data
python3 main.py --weather-only     # Only fetch weather
python3 main.py --analyze-only     # Only run analysis

# Process specific years
python3 main.py --years 2024 2025

# Force refresh (clear ALL existing data and start fresh)
python3 main.py --force
```

### Update Single Year (Recommended for Annual Updates)

When a new race happens, use this script to add just that year without re-scraping everything:

```bash
# Add or update a specific year (e.g., 2026)
python3 update_year.py 2026

# Fail if year already exists (instead of replacing)
python3 update_year.py 2026 --no-replace
```

This is **much faster** than re-running the full pipeline and won't affect your existing historical data.

## Data Sources

**Race Results**: https://mountdiablochallenge.itsyourrace.com/Results.aspx
**Weather API**: Open-Meteo Historical Weather API (free, no key needed)

## Configuration

Edit `config.py` to customize:
- Database path
- Start/Summit coordinates
- Race time window
- Weather variables
- Chart styling

## Requirements

- Python 3.9+
- See `requirements.txt` for package dependencies
- Internet connection for scraping and weather API

## Next Steps

After completing the current implementation:

1. **Apply aura.build Design**: Upload your aura.build template and apply it to visualizations
2. **Run Full Pipeline**: `python3 main.py` to collect all historical data
3. **Explore Analysis**: Open Jupyter notebooks for interactive exploration
4. **Generate Reports**: Use the analysis outputs for presentations or publications

## Future Enhancements

- [ ] Apply aura.build design template
- [ ] Create interactive Plotly/Dash dashboards
- [ ] Predictive modeling (race time prediction)
- [ ] Web-based dashboard
- [ ] Automated data refresh

## License

This project is for educational and analytical purposes.

## Author

Analysis created for Mount Diablo Challenge race data exploration
