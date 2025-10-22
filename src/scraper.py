"""
Web scraper for Mount Diablo Challenge race results.
Handles multi-year data collection from itsyourrace.com.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DiabloScraper:
    """Scraper for Mount Diablo Challenge race results."""

    def __init__(self, base_url='https://mountdiablochallenge.itsyourrace.com/Results.aspx?id=11068'):
        self.base_url = base_url
        self.session = requests.Session()
        # Add headers to mimic a browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_page(self, url=None):
        """Fetch a page and return BeautifulSoup object."""
        if url is None:
            url = self.base_url

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching page: {e}")
            return None

    def extract_viewstate(self, soup):
        """Extract ASP.NET ViewState and ALL form fields."""
        form_data = {}

        # Get ALL input fields from the page
        inputs = soup.find_all('input')
        for inp in inputs:
            name = inp.get('name')
            value = inp.get('value', '')
            if name:
                form_data[name] = value

        return form_data

    def get_race_date(self, soup):
        """Extract race date from the page."""
        # Look for race date in various places
        # Try to find it in page content
        page_text = soup.get_text()

        # Common date patterns
        date_patterns = [
            r'(\w+ \d{1,2}, \d{4})',  # e.g., "October 6, 2024"
            r'(\d{1,2}/\d{1,2}/\d{4})',  # e.g., "10/6/2024"
        ]

        for pattern in date_patterns:
            matches = re.findall(pattern, page_text)
            if matches:
                # Try to parse the first match
                for match in matches:
                    try:
                        # Try different date formats
                        for fmt in ['%B %d, %Y', '%m/%d/%Y', '%b %d, %Y']:
                            try:
                                date_obj = datetime.strptime(match, fmt)
                                return date_obj.date()
                            except ValueError:
                                continue
                    except Exception:
                        continue

        logger.warning("Could not extract race date from page")
        return None

    def parse_chip_time(self, time_str):
        """Convert chip time string to seconds."""
        if not time_str or time_str.strip() == '':
            return None

        # Format: HH:MM:SS.f or MM:SS.f
        time_str = time_str.strip()

        try:
            parts = time_str.split(':')
            if len(parts) == 3:  # HH:MM:SS.f
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:  # MM:SS.f
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
        except Exception as e:
            logger.error(f"Error parsing chip time '{time_str}': {e}")
            return None

    def parse_results_table(self, soup, year):
        """Parse the results table and extract race data."""
        results = []

        table = soup.find('table', {'id': 'resultsTable'})
        if not table:
            logger.warning("Results table not found")
            return results

        rows = table.find_all('tr')[1:]  # Skip header row

        for row in rows:
            cells = row.find_all('td')
            if len(cells) < 13:
                continue

            try:
                # Extract data from cells
                place = cells[0].text.strip()
                name = cells[1].text.strip()
                team = cells[2].text.strip()
                city_state = cells[3].text.strip()
                gender = cells[4].text.strip()
                gender_place = cells[5].text.strip()
                age = cells[6].text.strip()
                age_place = cells[7].text.strip()
                chip_time_str = cells[9].text.strip()
                pace = cells[10].text.strip()
                start_time = cells[12].text.strip()

                # Convert chip time to seconds
                chip_time_seconds = self.parse_chip_time(chip_time_str)

                result = {
                    'year': year,
                    'place': int(place) if place.isdigit() else None,
                    'name': name,
                    'team': team,
                    'city_state': city_state,
                    'gender': gender,
                    'gender_place': gender_place,
                    'age': int(age) if age.isdigit() else None,
                    'age_place': age_place,
                    'chip_time_str': chip_time_str,
                    'chip_time_seconds': chip_time_seconds,
                    'pace': pace,
                    'start_time': start_time
                }

                results.append(result)

            except Exception as e:
                logger.error(f"Error parsing row: {e}")
                continue

        return results

    def scrape_year(self, year):
        """Scrape all results for a given year."""
        logger.info(f"Scraping year: {year}")

        all_results = []

        # Build URL with year parameter
        year_url = f"{self.base_url}&y={year}"

        # Get the page for this specific year
        soup = self.get_page(year_url)
        if not soup:
            logger.error(f"Failed to get page for year {year}")
            return all_results

        # Extract race date
        race_date = self.get_race_date(soup)
        logger.info(f"Race date for {year}: {race_date}")

        # Now scrape all pages for this year
        page_num = 1
        max_pages = 100  # Safety limit

        while page_num <= max_pages:
            logger.info(f"  Scraping page {page_num} for year {year}")

            # Parse results from current page
            page_results = self.parse_results_table(soup, year)
            if not page_results:
                logger.info(f"  No more results found on page {page_num}")
                break

            # Add race_date to all results
            for result in page_results:
                result['race_date'] = race_date

            all_results.extend(page_results)
            logger.info(f"  Found {len(page_results)} results on page {page_num}")

            # Check if there's a next page
            next_link = soup.find('a', text='Next >')
            if not next_link:
                logger.info(f"  No more pages for year {year}")
                break

            # Get ViewState for next page
            viewstate = self.extract_viewstate(soup)

            # Prepare form data for next page (still need to POST for pagination)
            form_data = viewstate.copy()
            form_data['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder1$btnNext'
            form_data['__EVENTARGUMENT'] = ''

            # Submit form to get next page (use year_url to maintain year context)
            try:
                response = self.session.post(year_url, data=form_data)
                soup = BeautifulSoup(response.content, 'html.parser')
                page_num += 1
                time.sleep(0.5)  # Be nice to the server
            except Exception as e:
                logger.error(f"Error getting next page: {e}")
                break

        logger.info(f"Scraped {len(all_results)} total results for year {year}")
        return all_results

    def scrape_all_years(self, years=None):
        """Scrape results for all specified years."""
        if years is None:
            # Default years (2020 likely missing due to COVID)
            years = [2018, 2019, 2021, 2022, 2023, 2024, 2025]

        all_results = []

        for year in years:
            year_results = self.scrape_year(year)
            all_results.extend(year_results)
            logger.info(f"Total results so far: {len(all_results)}")
            time.sleep(1)  # Be nice to the server between years

        logger.info(f"Scraping complete! Total results: {len(all_results)}")
        return all_results


def main():
    """Main function for testing the scraper."""
    scraper = DiabloScraper()

    # Test with just 2025 first
    results = scraper.scrape_year(2025)
    logger.info(f"Test scrape complete: {len(results)} results")

    # Print first few results
    for i, result in enumerate(results[:5]):
        logger.info(f"Result {i+1}: {result}")


if __name__ == '__main__':
    main()
