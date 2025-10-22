#!/usr/bin/env python3
"""
Quick update script for adding a new race year to the database.

This script is designed for annual updates - it will:
1. Scrape results for the specified year
2. Fetch weather data for that year
3. Replace existing data if the year already exists in the database
4. Regenerate analysis and charts

Usage:
    python3 update_year.py 2026
    python3 update_year.py 2026 --no-replace  # Don't replace if year exists
"""

import argparse
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import DiabloScraper
from weather import WeatherFetcher
from database import DiabloDatabase
from analysis import DiabloAnalyzer
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def update_year(year, replace=True):
    """Update data for a specific year.

    Args:
        year: Year to update
        replace: If True, replace existing data for this year
    """
    logger.info("="*80)
    logger.info(f"UPDATING YEAR: {year}")
    logger.info("="*80)

    # Check if year already exists
    db = DiabloDatabase()
    db.connect()
    db.create_tables()  # Ensure tables exist before checking
    year_exists = db.year_exists(year)
    db.close()

    if year_exists and not replace:
        logger.error(f"Year {year} already exists in database and --no-replace was specified")
        logger.error(f"Use --replace to update existing data, or remove --no-replace flag")
        return False

    if year_exists:
        logger.info(f"Year {year} exists in database - will replace with fresh data")
    else:
        logger.info(f"Year {year} is new - adding to database")

    # Step 1: Scrape race results
    logger.info(f"\nStep 1: Scraping race results for {year}")
    scraper = DiabloScraper()
    race_results = scraper.scrape_year(year)

    if not race_results:
        logger.error(f"Failed to scrape results for year {year}")
        return False

    logger.info(f"Scraped {len(race_results)} race results")

    # Extract race date
    race_date = race_results[0].get('race_date') if race_results else None
    if not race_date:
        logger.error(f"Could not extract race date for year {year}")
        return False

    logger.info(f"Race date: {race_date}")

    # Step 2: Fetch weather data
    logger.info(f"\nStep 2: Fetching weather data for {race_date}")
    fetcher = WeatherFetcher()

    weather_records = []
    for location in ['start', 'summit']:
        records = fetcher.fetch_weather_for_race(year, race_date, location)
        weather_records.extend(records)

    logger.info(f"Fetched {len(weather_records)} weather records")

    # Step 3: Store in database
    logger.info(f"\nStep 3: Storing data in database")
    db = DiabloDatabase()
    db.connect()
    db.create_tables()

    # Insert with replace_existing=True to update if year exists
    db.insert_race_results(race_results, replace_existing=True)
    db.insert_weather_data(weather_records, replace_existing=True)

    counts = db.get_table_counts()
    logger.info(f"Database now contains:")
    logger.info(f"  - Race results: {counts['race_results']}")
    logger.info(f"  - Weather records: {counts['weather_data']}")

    db.close()

    # Step 4: Regenerate analysis
    logger.info(f"\nStep 4: Regenerating analysis and charts")
    analyzer = DiabloAnalyzer()
    analyzer.generate_all_plots()
    analyzer.close()

    logger.info("\n" + "="*80)
    logger.info(f"SUCCESS! Year {year} has been updated")
    logger.info("="*80)

    return True


def main():
    parser = argparse.ArgumentParser(
        description='Update database with a specific race year'
    )
    parser.add_argument(
        'year',
        type=int,
        help='Year to update (e.g., 2026)'
    )
    parser.add_argument(
        '--no-replace',
        action='store_true',
        help='Fail if year already exists instead of replacing'
    )

    args = parser.parse_args()

    # Validate year
    if args.year < 2018 or args.year > 2030:
        logger.error(f"Year {args.year} seems invalid. Expected range: 2018-2030")
        sys.exit(1)

    try:
        success = update_year(args.year, replace=not args.no_replace)
        if not success:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\nUpdate interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Update failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
