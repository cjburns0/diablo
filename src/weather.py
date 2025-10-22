"""
Weather data module for Mount Diablo Challenge race analysis.
Fetches historical weather data from Open-Meteo API.
"""

import requests
from datetime import datetime, date, timedelta
import logging
import os
import sys
import time

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherFetcher:
    """Fetches historical weather data from Open-Meteo API."""

    def __init__(self):
        self.api_url = config.WEATHER_API_URL
        self.locations = {
            'start': {
                'latitude': config.START_LATITUDE,
                'longitude': config.START_LONGITUDE
            },
            'summit': {
                'latitude': config.SUMMIT_LATITUDE,
                'longitude': config.SUMMIT_LONGITUDE
            }
        }

    def fetch_weather_for_date(self, race_date, location_name='start'):
        """Fetch weather data for a specific date and location.

        Args:
            race_date: datetime.date object for the race date
            location_name: 'start' or 'summit'

        Returns:
            Dictionary with hourly weather data
        """
        if location_name not in self.locations:
            logger.error(f"Invalid location: {location_name}")
            return None

        location = self.locations[location_name]

        # Format date as string
        if isinstance(race_date, date):
            date_str = race_date.isoformat()
        else:
            date_str = str(race_date)

        # Build API request parameters
        params = {
            'latitude': location['latitude'],
            'longitude': location['longitude'],
            'start_date': date_str,
            'end_date': date_str,
            'hourly': ','.join(config.WEATHER_VARIABLES),
            'timezone': 'America/Los_Angeles',  # Mount Diablo is in Pacific timezone
            'temperature_unit': 'fahrenheit',
            'windspeed_unit': 'mph'
        }

        try:
            logger.info(f"Fetching weather for {date_str} at {location_name} location...")
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()

            data = response.json()

            # Check if we got valid data
            if 'hourly' not in data:
                logger.error(f"No hourly data in response for {date_str}")
                return None

            return data['hourly']

        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return None

    def extract_race_window_data(self, hourly_data, race_date, year):
        """Extract weather data for the race window (7 AM - 11 AM).

        Args:
            hourly_data: Hourly weather data from API
            race_date: datetime.date object
            year: Year of the race

        Returns:
            List of weather records for the race window
        """
        if not hourly_data:
            return []

        records = []

        # Get timestamps and weather variables
        timestamps = hourly_data.get('time', [])
        temps = hourly_data.get('temperature_2m', [])
        windspeeds = hourly_data.get('windspeed_10m', [])
        winddirections = hourly_data.get('winddirection_10m', [])
        wind_gusts = hourly_data.get('wind_gusts_10m', [])

        # Filter for race window (7 AM - 11 AM)
        for i, timestamp_str in enumerate(timestamps):
            # Parse timestamp
            timestamp = datetime.fromisoformat(timestamp_str)

            # Check if within race window
            hour = timestamp.hour
            if config.RACE_START_HOUR <= hour <= config.RACE_END_HOUR:
                record = {
                    'timestamp': timestamp,
                    'temperature_2m': temps[i] if i < len(temps) else None,
                    'windspeed_10m': windspeeds[i] if i < len(windspeeds) else None,
                    'winddirection_10m': winddirections[i] if i < len(winddirections) else None,
                    'wind_gusts_10m': wind_gusts[i] if i < len(wind_gusts) else None
                }
                records.append(record)

        return records

    def fetch_weather_for_race(self, year, race_date, location_name='start'):
        """Fetch weather data for a race.

        Args:
            year: Year of the race
            race_date: datetime.date object or date string
            location_name: 'start' or 'summit'

        Returns:
            List of weather records for the database
        """
        # Convert race_date to date object if it's a string
        if isinstance(race_date, str):
            try:
                race_date = datetime.fromisoformat(race_date).date()
            except:
                logger.error(f"Invalid race_date format: {race_date}")
                return []

        # Fetch hourly data
        hourly_data = self.fetch_weather_for_date(race_date, location_name)
        if not hourly_data:
            return []

        # Extract race window data
        race_window_data = self.extract_race_window_data(hourly_data, race_date, year)

        # Add year, race_date, and location to each record
        weather_records = []
        for record in race_window_data:
            record['year'] = year
            record['race_date'] = race_date
            record['location'] = location_name
            weather_records.append(record)

        logger.info(f"Extracted {len(weather_records)} weather records for {year} at {location_name}")

        return weather_records

    def fetch_all_weather_data(self, race_dates_by_year):
        """Fetch weather data for all races at both start and summit locations.

        Args:
            race_dates_by_year: Dictionary mapping year to race_date
                Example: {2025: datetime.date(2025, 10, 5), ...}

        Returns:
            List of all weather records
        """
        all_weather_records = []

        for year, race_date in race_dates_by_year.items():
            if not race_date:
                logger.warning(f"No race date for year {year}, skipping weather fetch")
                continue

            # Fetch for both start and summit
            for location in ['start', 'summit']:
                records = self.fetch_weather_for_race(year, race_date, location)
                all_weather_records.extend(records)

                # Be nice to the API
                time.sleep(0.5)

        logger.info(f"Fetched total of {len(all_weather_records)} weather records")
        return all_weather_records

    def get_weather_summary(self, weather_records):
        """Calculate summary statistics for weather data.

        Args:
            weather_records: List of weather record dictionaries

        Returns:
            Dictionary with summary statistics
        """
        if not weather_records:
            return {}

        # Separate by location
        start_records = [r for r in weather_records if r.get('location') == 'start']
        summit_records = [r for r in weather_records if r.get('location') == 'summit']

        summary = {}

        for location_name, records in [('start', start_records), ('summit', summit_records)]:
            if not records:
                continue

            windspeeds = [r['windspeed_10m'] for r in records if r.get('windspeed_10m') is not None]
            wind_gusts = [r['wind_gusts_10m'] for r in records if r.get('wind_gusts_10m') is not None]
            temps = [r['temperature_2m'] for r in records if r.get('temperature_2m') is not None]

            summary[location_name] = {
                'avg_windspeed': sum(windspeeds) / len(windspeeds) if windspeeds else None,
                'max_windspeed': max(windspeeds) if windspeeds else None,
                'min_windspeed': min(windspeeds) if windspeeds else None,
                'avg_wind_gust': sum(wind_gusts) / len(wind_gusts) if wind_gusts else None,
                'max_wind_gust': max(wind_gusts) if wind_gusts else None,
                'avg_temp': sum(temps) / len(temps) if temps else None,
                'max_temp': max(temps) if temps else None,
                'min_temp': min(temps) if temps else None
            }

        return summary


def main():
    """Test weather fetcher."""
    fetcher = WeatherFetcher()

    # Test with 2025 race date
    test_date = date(2025, 10, 5)
    test_year = 2025

    # Fetch for start location
    start_records = fetcher.fetch_weather_for_race(test_year, test_date, 'start')
    logger.info(f"Start location records: {len(start_records)}")

    # Fetch for summit location
    summit_records = fetcher.fetch_weather_for_race(test_year, test_date, 'summit')
    logger.info(f"Summit location records: {len(summit_records)}")

    # Get summary
    all_records = start_records + summit_records
    summary = fetcher.get_weather_summary(all_records)

    logger.info("Weather Summary:")
    for location, stats in summary.items():
        logger.info(f"\n{location.upper()}:")
        for key, value in stats.items():
            if value is not None:
                logger.info(f"  {key}: {value:.2f}")

    # Print first few records
    logger.info("\nSample records:")
    for i, record in enumerate(start_records[:3]):
        logger.info(f"Record {i+1}: {record}")


if __name__ == '__main__':
    main()
