"""Collect separately ranked race categories without mixing the main field."""

import math
import time
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from bs4 import BeautifulSoup

ADDITIONAL_CATEGORIES = {
    'e_assisted': 'E-Assisted Bike',
    'tandem': 'Tandem',
}


def results_url(base_url, year, race_id=None):
    parts = urlsplit(base_url)
    query = dict(parse_qsl(parts.query))
    query['y'] = str(year)
    if race_id is not None:
        query['eid'] = str(race_id)
    return urlunsplit(parts._replace(query=urlencode(query)))


def scrape_category(scraper, year, category, race_id):
    """Return a complete category or raise before any database writes."""
    label = ADDITIONAL_CATEGORIES[category]
    url = results_url(scraper.base_url, year, race_id)
    response = scraper.session.get(url, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    results = []
    seen_pages = set()
    expected = None
    race_date = None

    for page in range(100):
        selected_year = soup.select_one('#ddlYear option[selected]')
        selected_race = soup.select_one('#ddlRace option[selected]')
        date = scraper.get_race_date(soup)
        if (selected_year is None or selected_year.get('value') != str(year)
                or selected_race is None or selected_race.get('value') != str(race_id)
                or selected_race.get_text(strip=True) != label
                or date is None or date.year != year):
            raise ValueError(f'Unexpected year, category or date for {label}')
        if race_date is not None and date != race_date:
            raise ValueError(f'Race date changed while collecting {label}')
        race_date = date

        count_label = soup.find('span', class_='title', string='Finishers')
        count = count_label.parent.find('span', class_='number') if count_label else None
        if count is None:
            raise ValueError(f'Missing published finisher count for {label}')
        page_count = int(count.get_text(strip=True).replace(',', ''))
        if expected is not None and page_count != expected:
            raise ValueError(f'Finisher count changed while collecting {label}')
        expected = page_count

        if soup.find('table', id='resultsTable') is None:
            raise ValueError(f'Missing results table for {label}')
        rows = scraper.parse_results_table(soup, year)
        if any(r['chip_time_str'] and r['chip_time_seconds'] is None for r in rows):
            raise ValueError(f'Invalid chip time for {label}')
        fingerprint = tuple((r['place'], r['name'], r['chip_time_str']) for r in rows)
        if fingerprint in seen_pages:
            raise ValueError(f'Repeated results page for {label}')
        seen_pages.add(fingerprint)
        for row in rows:
            row['race_date'] = date.isoformat()
        results.extend(rows)

        if not soup.find('a', string='Next >'):
            break
        if not rows:
            raise ValueError(f'Empty intermediate results page for {label}')
        fields = scraper.extract_viewstate(soup)
        for select in soup.find_all('select', attrs={'name': True}):
            option = select.find('option', selected=True) or select.find('option')
            if option is not None:
                fields[select['name']] = option.get('value', '')
        fields['__EVENTTARGET'] = 'ctl00$ContentPlaceHolder1$btnNext'
        fields['__EVENTARGUMENT'] = ''
        time.sleep(0.5)
        response = scraper.session.post(url, data=fields, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
    else:
        raise ValueError(f'Pagination limit reached for {label}')

    finishers = [r for r in results if r['chip_time_seconds'] is not None]
    if (len(finishers) != expected
            or len({r['place'] for r in finishers}) != len(finishers)
            or any(not r['place'] or r['place'] < 1
                   or not math.isfinite(r['chip_time_seconds'])
                   or r['chip_time_seconds'] <= 0 for r in finishers)):
        raise ValueError(f'Incomplete or invalid finisher results for {label}')

    return {
        'year': year, 'category': category, 'label': label,
        'race_date': race_date.isoformat(), 'source_url': url,
        'finisher_count': expected, 'untimed_count': len(results) - len(finishers),
        'results': finishers, 'source_rows': results,
    }


def scrape_additional_categories(scraper, year):
    """Discover this year's category IDs; IDs are not stable across years."""
    response = scraper.session.get(results_url(scraper.base_url, year), timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    selected_year = soup.select_one('#ddlYear option[selected]')
    if selected_year is None or selected_year.get('value') != str(year):
        raise ValueError(f'Cannot discover race categories for {year}')
    options = {o.get_text(strip=True): o.get('value') for o in soup.select('#ddlRace option')}
    if not options:
        raise ValueError(f'Missing category selector for {year}')
    return [scrape_category(scraper, year, category, options[label])
            for category, label in ADDITIONAL_CATEGORIES.items() if options.get(label)]
