"""Offline checks for source completeness, category isolation and atomic writes."""
import copy
from pathlib import Path
import sqlite3
import sys
import unittest
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup
import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from category_results import scrape_category, scrape_additional_categories
from database import DiabloDatabase
from scraper import DiabloScraper

FIXTURES = Path(__file__).parent / 'fixtures'


def response(html):
    result = Mock()
    result.content = html.encode()
    return result


class CategoryResultsTests(unittest.TestCase):
    def setUp(self):
        self.e = (FIXTURES / '2026-e-assisted.html').read_text()
        self.t = (FIXTURES / '2026-tandem.html').read_text()
        self.scraper = DiabloScraper()
        self.scraper.session = Mock()

    def scrape(self, html=None, category='e_assisted', race_id='141456'):
        self.scraper.session.get.return_value = response(self.e if html is None else html)
        return scrape_category(self.scraper, 2026, category, race_id)

    def test_published_counts_and_fractional_times(self):
        e = self.scrape()
        t = self.scrape(self.t, 'tandem', '141457')
        self.assertEqual((e['finisher_count'], e['untimed_count'], len(e['source_rows'])), (20, 3, 23))
        self.assertEqual((t['finisher_count'], t['untimed_count']), (9, 0))
        self.assertEqual(t['results'][0]['chip_time_seconds'], 3620.8)
        self.assertEqual(e['results'][-1]['chip_time_str'], '02:35:42.4')

    def test_discovers_year_specific_ids(self):
        self.scraper.session.get.side_effect = [response(self.e), response(self.e), response(self.t)]
        races = scrape_additional_categories(self.scraper, 2026)
        self.assertEqual([r['category'] for r in races], ['e_assisted', 'tandem'])
        urls = [call.args[0] for call in self.scraper.session.get.call_args_list]
        self.assertTrue(urls[1].endswith('y=2026&eid=141456'))
        self.assertTrue(urls[2].endswith('y=2026&eid=141457'))

    def test_rejects_wrong_year_category_date_or_missing_table(self):
        for selector, value in [('#ddlYear option[selected]', '2025'),
                                ('#ddlRace option[selected]', '141455')]:
            soup = BeautifulSoup(self.e, 'html.parser')
            soup.select_one(selector)['value'] = value
            with self.subTest(selector=selector), self.assertRaises(ValueError):
                self.scrape(str(soup))
        with self.assertRaises(ValueError):
            self.scrape(self.e.replace('October 4, 2026', 'October 4, 2025'))
        soup = BeautifulSoup(self.e, 'html.parser')
        soup.select_one('#resultsTable').decompose()
        with self.assertRaises(ValueError):
            self.scrape(str(soup))

    def test_rejects_incomplete_duplicate_or_malformed_finishers(self):
        for defect in ['missing', 'duplicate', 'bad_time']:
            soup = BeautifulSoup(self.e, 'html.parser')
            rows = [r for r in soup.select('#resultsTable tr') if len(r.find_all('td')) >= 13]
            if defect == 'missing':
                rows[0].decompose()
            elif defect == 'duplicate':
                rows[1].find_all('td')[0].string = '1'
            else:
                rows[0].find_all('td')[9].string = 'unparseable'
            with self.subTest(defect=defect), self.assertRaises(ValueError):
                self.scrape(str(soup))

    @patch('category_results.time.sleep')
    def test_pagination_preserves_category_and_checks_completeness(self, sleep):
        first = BeautifulSoup(self.e, 'html.parser')
        second = BeautifulSoup(self.e, 'html.parser')
        for page, keep_first in [(first, True), (second, False)]:
            rows = page.select('#resultsTable tr')[1:]
            # The source includes a supplemental detail row after each result.
            for index, row in enumerate(rows):
                if (index < 20) != keep_first:
                    row.decompose()
        first.append(BeautifulSoup('<a>Next &gt;</a>', 'html.parser'))
        self.scraper.session.get.return_value = response(str(first))
        self.scraper.session.post.return_value = response(str(second))
        race = scrape_category(self.scraper, 2026, 'e_assisted', '141456')
        self.assertEqual(race['finisher_count'], 20)
        fields = self.scraper.session.post.call_args.kwargs['data']
        self.assertEqual(fields['ctl00$ContentPlaceHolder1$ddlRace'], '141456')
        self.assertEqual(fields['ctl00$ContentPlaceHolder1$ddlYear'], '2026')

    @patch('category_results.time.sleep')
    def test_repeated_page_and_http_failures_abort(self, sleep):
        repeated = self.e + '<a>Next &gt;</a>'
        self.scraper.session.post.return_value = response(repeated)
        with self.assertRaisesRegex(ValueError, 'Repeated'):
            self.scrape(repeated)
        self.scraper.session.get.return_value = response(self.e)
        self.scraper.session.get.return_value.raise_for_status.side_effect = requests.HTTPError('503')
        with self.assertRaises(requests.HTTPError):
            scrape_category(self.scraper, 2026, 'e_assisted', '141456')

    def test_storage_is_isolated_idempotent_and_atomic(self):
        races = [self.scrape(), self.scrape(self.t, 'tandem', '141457')]
        db = DiabloDatabase(':memory:')
        db.connect()
        self.addCleanup(db.close)
        db.create_tables()
        db.conn.execute("INSERT INTO race_results (year, name, chip_time_seconds) VALUES (2026, 'Main rider', 3000)")
        db.conn.commit()
        db.replace_additional_races(races)
        before = db.get_additional_races()
        db.replace_additional_races(races)
        self.assertEqual(db.get_additional_races(), before)
        self.assertEqual(db.conn.execute('SELECT COUNT(*) FROM additional_race_results').fetchone()[0], 29)
        self.assertEqual(db.conn.execute('SELECT name FROM race_results').fetchall(), [('Main rider',)])
        invalid = copy.deepcopy(races)
        invalid[0]['results'][0]['name'] = 'Should be rolled back'
        invalid[1]['results'][0]['name'] = None  # Fail the second category's DB constraint.
        with self.assertRaises(sqlite3.IntegrityError):
            db.replace_additional_races(invalid)
        self.assertEqual(db.get_additional_races(), before)
        invalid = copy.deepcopy(races)
        invalid[1]['results'].pop()
        with self.assertRaises(ValueError):
            db.replace_additional_races(invalid)
        self.assertEqual(db.get_additional_races(), before)
        db.delete_year_data(2026)
        self.assertEqual(db.get_additional_races(), [])
        self.assertEqual(db.conn.execute('SELECT COUNT(*) FROM additional_race_results').fetchone()[0], 0)
        self.assertEqual(db.conn.execute('SELECT COUNT(*) FROM race_results').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main()
