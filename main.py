#!/usr/bin/env python3
"""
Main pipeline script for Mount Diablo Challenge race analysis.

This script orchestrates the entire data collection and analysis workflow:
1. Scrape race results from all years
2. Fetch weather data for race dates
3. Store data in SQLite database
4. Generate analysis and visualizations
"""

import argparse
import logging
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import DiabloScraper
from weather import WeatherFetcher
from database import DiabloDatabase
from analysis import DiabloAnalyzer
import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_race_data(years=None, force=False):
    """Scrape race results from all specified years.

    Args:
        years: List of years to scrape (default: config.RACE_YEARS)
        force: If True, clear existing data before scraping

    Returns:
        List of all race results
    """
    logger.info("="*80)
    logger.info("STEP 1: SCRAPING RACE RESULTS")
    logger.info("="*80)

    if years is None:
        years = config.RACE_YEARS

    logger.info(f"Scraping results for years: {years}")

    scraper = DiabloScraper()
    all_results = scraper.scrape_all_years(years)

    logger.info(f"Scraped {len(all_results)} total race results")

    return all_results


def fetch_weather_data(race_dates_by_year):
    """Fetch weather data for all race dates.

    Args:
        race_dates_by_year: Dictionary mapping year to race_date

    Returns:
        List of all weather records
    """
    logger.info("\n" + "="*80)
    logger.info("STEP 2: FETCHING WEATHER DATA")
    logger.info("="*80)

    logger.info(f"Fetching weather for {len(race_dates_by_year)} race dates")

    fetcher = WeatherFetcher()
    weather_records = fetcher.fetch_all_weather_data(race_dates_by_year)

    logger.info(f"Fetched {len(weather_records)} weather records")

    return weather_records


def store_data(race_results, weather_records, force=False, replace_existing=True):
    """Store race and weather data in the database.

    Args:
        race_results: List of race result dictionaries
        weather_records: List of weather record dictionaries
        force: If True, clear ALL existing data before inserting
        replace_existing: If True, replace data for years being inserted (default True)
    """
    logger.info("\n" + "="*80)
    logger.info("STEP 3: STORING DATA IN DATABASE")
    logger.info("="*80)

    db = DiabloDatabase()
    db.connect()
    db.create_tables()

    if force:
        logger.info("Clearing ALL existing data...")
        db.clear_race_results()
        db.clear_weather_data()
        replace_existing = False  # No need to replace if we just cleared everything

    # Insert race results
    if race_results:
        db.insert_race_results(race_results, replace_existing=replace_existing)

    # Insert weather data
    if weather_records:
        db.insert_weather_data(weather_records, replace_existing=replace_existing)

    # Show counts
    counts = db.get_table_counts()
    logger.info(f"Database now contains:")
    logger.info(f"  - Race results: {counts['race_results']}")
    logger.info(f"  - Weather records: {counts['weather_data']}")

    db.close()


def run_analysis():
    """Run analysis and generate visualizations."""
    logger.info("\n" + "="*80)
    logger.info("STEP 4: RUNNING ANALYSIS")
    logger.info("="*80)

    analyzer = DiabloAnalyzer()

    # Print summary statistics
    analyzer.print_summary_statistics()

    # Generate all plots
    logger.info("\nGenerating visualizations...")
    analyzer.generate_all_plots()

    analyzer.close()


def main():
    """Main pipeline execution."""
    parser = argparse.ArgumentParser(
        description='Mount Diablo Challenge Race Analysis Pipeline'
    )
    parser.add_argument(
        '--scrape-only',
        action='store_true',
        help='Only scrape race results, do not fetch weather or analyze'
    )
    parser.add_argument(
        '--weather-only',
        action='store_true',
        help='Only fetch weather data (requires existing race results in database)'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Only run analysis on existing data in database'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Clear existing data before running pipeline'
    )
    parser.add_argument(
        '--years',
        nargs='+',
        type=int,
        help='Specific years to process (default: all years in config)'
    )

    args = parser.parse_args()

    try:
        if args.analyze_only:
            # Only run analysis
            run_analysis()

        elif args.weather_only:
            # Only fetch weather data
            # Get race dates from database
            db = DiabloDatabase()
            db.connect()

            query = 'SELECT DISTINCT year, race_date FROM race_results ORDER BY year'
            db.cursor.execute(query)
            rows = db.cursor.fetchall()

            race_dates_by_year = {}
            for row in rows:
                year, race_date_str = row
                if race_date_str:
                    from datetime import datetime
                    race_date = datetime.fromisoformat(race_date_str).date()
                    race_dates_by_year[year] = race_date

            db.close()

            logger.info(f"Found race dates for {len(race_dates_by_year)} years in database")

            weather_records = fetch_weather_data(race_dates_by_year)
            store_data([], weather_records, force=args.force)

        elif args.scrape_only:
            # Only scrape race results
            race_results = scrape_race_data(years=args.years, force=args.force)
            store_data(race_results, [], force=args.force)

        else:
            # Full pipeline
            logger.info("\n" + "#"*80)
            logger.info("# MOUNT DIABLO CHALLENGE ANALYSIS PIPELINE")
            logger.info("#"*80 + "\n")

            # Step 1: Scrape race results
            race_results = scrape_race_data(years=args.years, force=args.force)

            # Extract race dates from results
            race_dates_by_year = {}
            for result in race_results:
                year = result['year']
                race_date = result.get('race_date')
                if race_date and year not in race_dates_by_year:
                    race_dates_by_year[year] = race_date

            logger.info(f"\nExtracted race dates for {len(race_dates_by_year)} years:")
            for year, date in sorted(race_dates_by_year.items()):
                logger.info(f"  {year}: {date}")

            # Step 2: Fetch weather data
            weather_records = fetch_weather_data(race_dates_by_year)

            # Step 3: Store data
            store_data(race_results, weather_records, force=args.force)

            # Step 4: Run analysis
            run_analysis()

            logger.info("\n" + "#"*80)
            logger.info("# PIPELINE COMPLETE!")
            logger.info("#"*80 + "\n")

            logger.info(f"Total race results: {len(race_results)}")
            logger.info(f"Total weather records: {len(weather_records)}")
            logger.info(f"Charts saved to: {config.CHARTS_DIR}")

    except KeyboardInterrupt:
        logger.info("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
