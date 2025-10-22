"""
Configuration file for Mount Diablo Challenge race analysis project.
"""

import os

# Project paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
CHARTS_DIR = os.path.join(OUTPUT_DIR, 'charts')

# Database
DATABASE_PATH = os.path.join(DATA_DIR, 'diablo_challenge.db')

# Race results URL
RACE_RESULTS_BASE_URL = 'https://mountdiablochallenge.itsyourrace.com/Results.aspx'
# Years to scrape
RACE_YEARS = list(range(2018, 2026))  # 2018 to 2025

# Mount Diablo coordinates
# Start location (approximate)
START_LATITUDE = 37.885
START_LONGITUDE = -122.059

# Summit location (approximate)
SUMMIT_LATITUDE = 37.881
SUMMIT_LONGITUDE = -121.914

# Weather data configuration
# Open-Meteo Historical Weather API
WEATHER_API_URL = 'https://archive-api.open-meteo.com/v1/archive'

# Weather variables to fetch
WEATHER_VARIABLES = [
    'temperature_2m',
    'windspeed_10m',
    'winddirection_10m',
    'wind_gusts_10m'
]

# Race time window
# Typical race start time is around 7-8 AM
# Race window extends up to 3 hours (until ~11 AM)
RACE_START_HOUR = 7
RACE_END_HOUR = 11

# Weather data frequency (hourly intervals)
# Open-Meteo supports hourly data for historical queries
WEATHER_FREQUENCY = 'hourly'

# Analysis configuration
# Statistics to calculate for chip times
STATISTICS = ['mean', 'median', 'percentile_25', 'percentile_75']

# Visualization configuration
PLOT_STYLE = 'seaborn-v0_8-darkgrid'
FIGURE_DPI = 300
FIGURE_SIZE = (12, 8)
