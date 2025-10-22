"""
Database module for Mount Diablo Challenge race analysis.
Handles SQLite database operations for race results and weather data.
"""

import sqlite3
from datetime import datetime, date
import logging
import os
import sys

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DiabloDatabase:
    """Database handler for Mount Diablo Challenge data."""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = config.DATABASE_PATH

        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Error connecting to database: {e}")
            raise

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def create_tables(self):
        """Create the database schema."""
        logger.info("Creating database tables...")

        # Race results table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS race_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                race_date DATE,
                place INTEGER,
                name TEXT,
                team TEXT,
                city_state TEXT,
                gender TEXT,
                gender_place TEXT,
                age INTEGER,
                age_place TEXT,
                chip_time_str TEXT,
                chip_time_seconds REAL,
                pace TEXT,
                start_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create index on year for faster queries
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_race_results_year
            ON race_results(year)
        ''')

        # Create index on chip_time_seconds for faster statistics
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_race_results_chip_time
            ON race_results(chip_time_seconds)
        ''')

        # Weather data table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year INTEGER NOT NULL,
                race_date DATE,
                timestamp TIMESTAMP,
                location TEXT,
                temperature_2m REAL,
                windspeed_10m REAL,
                winddirection_10m REAL,
                wind_gusts_10m REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create index on year and location
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_weather_data_year_location
            ON weather_data(year, location)
        ''')

        self.conn.commit()
        logger.info("Database tables created successfully")

    def delete_year_data(self, year):
        """Delete all data for a specific year.

        Args:
            year: Year to delete
        """
        self.cursor.execute('DELETE FROM race_results WHERE year = ?', (year,))
        self.cursor.execute('DELETE FROM weather_data WHERE year = ?', (year,))
        self.conn.commit()
        logger.info(f"Deleted all data for year {year}")

    def year_exists(self, year):
        """Check if data for a year already exists.

        Args:
            year: Year to check

        Returns:
            True if year exists in database, False otherwise
        """
        self.cursor.execute('SELECT COUNT(*) FROM race_results WHERE year = ?', (year,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def insert_race_results(self, results, replace_existing=False):
        """Insert race results into the database.

        Args:
            results: List of dictionaries containing race result data
            replace_existing: If True, delete existing data for these years first
        """
        logger.info(f"Inserting {len(results)} race results...")

        # Get unique years in results
        if replace_existing and results:
            years_to_replace = set(r.get('year') for r in results if r.get('year'))
            for year in years_to_replace:
                if self.year_exists(year):
                    logger.info(f"Replacing existing data for year {year}")
                    self.cursor.execute('DELETE FROM race_results WHERE year = ?', (year,))

        insert_query = '''
            INSERT INTO race_results (
                year, race_date, place, name, team, city_state,
                gender, gender_place, age, age_place,
                chip_time_str, chip_time_seconds, pace, start_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        for result in results:
            # Convert date object to string if necessary
            race_date = result.get('race_date')
            if isinstance(race_date, date):
                race_date = race_date.isoformat()

            self.cursor.execute(insert_query, (
                result.get('year'),
                race_date,
                result.get('place'),
                result.get('name'),
                result.get('team'),
                result.get('city_state'),
                result.get('gender'),
                result.get('gender_place'),
                result.get('age'),
                result.get('age_place'),
                result.get('chip_time_str'),
                result.get('chip_time_seconds'),
                result.get('pace'),
                result.get('start_time')
            ))

        self.conn.commit()
        logger.info(f"Successfully inserted {len(results)} race results")

    def insert_weather_data(self, weather_records, replace_existing=False):
        """Insert weather data into the database.

        Args:
            weather_records: List of dictionaries containing weather data
            replace_existing: If True, delete existing data for these years first
        """
        logger.info(f"Inserting {len(weather_records)} weather records...")

        # Get unique years in records
        if replace_existing and weather_records:
            years_to_replace = set(r.get('year') for r in weather_records if r.get('year'))
            for year in years_to_replace:
                if self.year_exists(year):
                    self.cursor.execute('DELETE FROM weather_data WHERE year = ?', (year,))

        insert_query = '''
            INSERT INTO weather_data (
                year, race_date, timestamp, location,
                temperature_2m, windspeed_10m, winddirection_10m, wind_gusts_10m
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''

        for record in weather_records:
            # Convert date/datetime objects to strings if necessary
            race_date = record.get('race_date')
            if isinstance(race_date, date):
                race_date = race_date.isoformat()

            timestamp = record.get('timestamp')
            if isinstance(timestamp, datetime):
                timestamp = timestamp.isoformat()

            self.cursor.execute(insert_query, (
                record.get('year'),
                race_date,
                timestamp,
                record.get('location'),
                record.get('temperature_2m'),
                record.get('windspeed_10m'),
                record.get('winddirection_10m'),
                record.get('wind_gusts_10m')
            ))

        self.conn.commit()
        logger.info(f"Successfully inserted {len(weather_records)} weather records")

    def get_race_results_by_year(self, year):
        """Get all race results for a specific year."""
        query = '''
            SELECT * FROM race_results
            WHERE year = ?
            ORDER BY place
        '''
        self.cursor.execute(query, (year,))
        return self.cursor.fetchall()

    def get_all_years(self):
        """Get list of all years in the database."""
        query = '''
            SELECT DISTINCT year FROM race_results
            ORDER BY year
        '''
        self.cursor.execute(query)
        return [row[0] for row in self.cursor.fetchall()]

    def get_yearly_statistics(self):
        """Calculate statistics for each year."""
        query = '''
            SELECT
                year,
                COUNT(*) as num_racers,
                AVG(chip_time_seconds) as avg_time,
                MIN(chip_time_seconds) as min_time,
                MAX(chip_time_seconds) as max_time
            FROM race_results
            WHERE chip_time_seconds IS NOT NULL
            GROUP BY year
            ORDER BY year
        '''
        self.cursor.execute(query)

        columns = ['year', 'num_racers', 'avg_time', 'min_time', 'max_time']
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def get_percentiles_by_year(self, year, percentiles=[25, 50, 75]):
        """Calculate percentiles for chip times in a given year.

        SQLite doesn't have built-in percentile functions, so we calculate them manually.
        """
        # Get all chip times for the year, sorted
        query = '''
            SELECT chip_time_seconds
            FROM race_results
            WHERE year = ? AND chip_time_seconds IS NOT NULL
            ORDER BY chip_time_seconds
        '''
        self.cursor.execute(query, (year,))
        times = [row[0] for row in self.cursor.fetchall()]

        if not times:
            return {}

        result = {}
        for p in percentiles:
            # Calculate the index for the percentile
            idx = int(len(times) * p / 100)
            if idx >= len(times):
                idx = len(times) - 1
            result[f'p{p}'] = times[idx]

        return result

    def get_weather_by_year(self, year):
        """Get weather data for a specific year."""
        query = '''
            SELECT * FROM weather_data
            WHERE year = ?
            ORDER BY timestamp
        '''
        self.cursor.execute(query, (year,))
        return self.cursor.fetchall()

    def get_weather_summary_by_year(self, year):
        """Get summary statistics for weather by year."""
        query = '''
            SELECT
                year,
                location,
                AVG(temperature_2m) as avg_temp,
                AVG(windspeed_10m) as avg_windspeed,
                MAX(windspeed_10m) as max_windspeed,
                MAX(wind_gusts_10m) as max_gust
            FROM weather_data
            WHERE year = ?
            GROUP BY year, location
        '''
        self.cursor.execute(query, (year,))

        columns = ['year', 'location', 'avg_temp', 'avg_windspeed', 'max_windspeed', 'max_gust']
        results = []
        for row in self.cursor.fetchall():
            results.append(dict(zip(columns, row)))

        return results

    def clear_race_results(self):
        """Clear all race results from the database."""
        self.cursor.execute('DELETE FROM race_results')
        self.conn.commit()
        logger.info("Cleared all race results")

    def clear_weather_data(self):
        """Clear all weather data from the database."""
        self.cursor.execute('DELETE FROM weather_data')
        self.conn.commit()
        logger.info("Cleared all weather data")

    def get_table_counts(self):
        """Get count of records in each table."""
        counts = {}

        self.cursor.execute('SELECT COUNT(*) FROM race_results')
        counts['race_results'] = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM weather_data')
        counts['weather_data'] = self.cursor.fetchone()[0]

        return counts


def main():
    """Test the database functionality."""
    # Create database
    db = DiabloDatabase()
    db.connect()
    db.create_tables()

    # Test with sample data
    sample_results = [
        {
            'year': 2025,
            'race_date': date(2025, 10, 5),
            'place': 1,
            'name': 'Test Racer',
            'team': 'Test Team',
            'city_state': 'Test City',
            'gender': 'M',
            'gender_place': '1',
            'age': 30,
            'age_place': '1 / 10',
            'chip_time_str': '00:45:00.0',
            'chip_time_seconds': 2700.0,
            'pace': '4:00/mile',
            'start_time': '8:00 AM'
        }
    ]

    # Insert test data
    db.insert_race_results(sample_results)

    # Query data
    counts = db.get_table_counts()
    logger.info(f"Table counts: {counts}")

    # Get statistics
    stats = db.get_yearly_statistics()
    logger.info(f"Yearly statistics: {stats}")

    db.close()


if __name__ == '__main__':
    main()
