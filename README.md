# Mount Diablo Challenge Race Analysis

Comprehensive analysis of the annual Mount Diablo Challenge race - an 11.2-mile cycling climb with 3,249 feet of elevation gain.

## Background in Plain English 

We scrape the Diablo Challenge race time finish results for all the details possible using a Python scraper and store it in a SQLite database. Given the results are fairly static and not updated more than once per year, we don't need a fully functioning backend database. Then we take a design template that I designed elsewhere to chart the data showing bottom 25th percentile, mean, median, and 75th percentile. The idea is to plot these by year on the x-axis and then be able to gauge analysis from different times per year. The key overlay here is that we pull in public weather data that is extremely detailed for the time of day as well as the specific location. Given we are on a Diablo Mountain, the general town weather will not work. We will need things like wind at the summit versus wind at the start to show how it impacted the times for that year. 


## Overview

This project provides complete data pipeline and analysis for the Mount Diablo Challenge race:

- **Web Scraping**: Automated collection of race results from all available years (2018-2025)
- **Weather Integration**: Historical weather data from Open-Meteo API (free, no API key needed)
- **Database Storage**: SQLite database for efficient data management
- **Statistical Analysis**: Year-over-year trends, distributions, and correlations
- **Visualization**: Publication-quality charts and interactive dashboards
- **Frontend Deployment**: Dashboard hosted on [Vercel](https://vercel.com) with automatic updates

## Architecture

- **Frontend**: Static HTML/JavaScript dashboard hosted on Vercel at [diablo-topaz.vercel.app](https://diablo-topaz.vercel.app)
- **Data Pipeline**: Python scripts run locally to scrape race data and generate dashboard JSON
- **Database**: SQLite database stored locally, updated manually after each race
- **Deployment**: Dashboard data (`dashboard_data.json`) is committed to git and auto-deployed to Vercel

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

### 3. Update Dashboard Data

Generate the JSON data file for the dashboard:

```bash
python3 dashboard_data.py
```

This creates `data/dashboard_data.json` which powers the frontend dashboard.

### 4. View Interactive Dashboard

**Live Dashboard**: https://diablo-topaz.vercel.app

Or view locally:

```bash
python3 -m http.server 8080
# Then open http://localhost:8080/dashboard.html
```

The interactive dashboard features:
- **Box-and-whisker plots** showing time distribution (25th-75th percentile, median, mean)
- **Inverted Y-axis** with fastest times at the top
- **Wind overlay** showing correlation between wind speed and performance
- **Dynamic filtering** by year range
- **Real-time KPI cards** displaying key race statistics

### 5. Explore Data in Jupyter

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
├── notebooks/              # Jupyter notebooks for exploration
├── data/
│   ├── diablo_challenge.db # SQLite database
│   └── dashboard_data.json # JSON data for dashboard
├── dashboard.html          # Interactive web dashboard
├── dashboard_data.py       # Dashboard data generator
├── config.py               # Configuration
├── main.py                 # Main pipeline script
├── update_year.py          # Single-year update script
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
- **Interactive Dashboard** (`dashboard.html`): Real-time, filterable charts with wind overlays
- Box-and-whisker plots showing time distribution per year
- Inverted Y-axis design (faster times appear higher)
- Wind speed correlation overlay (blue shading indicates wind intensity)
- Dynamic year range filtering
- KPI cards showing key statistics

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

### Deploy Updates to Vercel

After updating the data locally, deploy to the live dashboard:

```bash
# 1. Update the data
python3 update_year.py 2026  # or python3 main.py

# 2. Regenerate dashboard JSON
python3 dashboard_data.py

# 3. Commit and push to trigger Vercel deployment
git add data/dashboard_data.json
git commit -m "Update race data for 2026"
git push
```

Vercel will automatically redeploy the dashboard with the updated data within 30-60 seconds.

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
cjburns0