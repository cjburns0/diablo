/** Separately ranked categories; never combined with the main-race charts. */
import { getDashboardData } from '../core/data.js';

function element(tag, text, className = '') {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  node.className = className;
  return node;
}

export function update(startYear, endYear) {
  const container = document.getElementById('additional-category-results');
  if (!container) return;
  const openCategories = new Set([...container.querySelectorAll('details[open]')]
    .map(detail => detail.dataset.category));
  container.replaceChildren();

  const races = (getDashboardData()?.additional_categories ?? [])
    .filter(race => race.year >= startYear && race.year <= endYear);
  if (!races.length) {
    container.append(element('p', 'No separate category results are available for the selected years.', 'text-sm text-slate-400'));
    return;
  }

  for (const race of races) {
    const details = element('details', undefined, 'rounded-lg border border-slate-800');
    details.dataset.category = `${race.year}-${race.category}`;
    details.open = openCategories.has(details.dataset.category);
    details.append(element('summary', `${race.year} · ${race.label} · ${race.finisher_count} finisher entries`,
      'px-4 py-3 text-sm font-medium text-slate-200 cursor-pointer focus-visible:outline focus-visible:outline-2 focus-visible:outline-sky-400'));

    const body = element('div', undefined, 'px-4 pb-4');
    body.append(element('p', `Median: ${race.median_formatted ?? '—'} · Fastest: ${race.fastest_time ?? '—'}`, 'text-xs text-slate-400 mb-3'));
    if (race.category === 'tandem') {
      body.append(element('p', 'The timing provider lists individual finisher entries; this count does not represent tandem teams.', 'text-xs text-slate-400 mb-3'));
    }
    if (race.untimed_count > 0) {
      body.append(element('p', `${race.untimed_count} additional entries have no published finish time and are excluded from these statistics.`, 'text-xs text-slate-400 mb-3'));
    }

    const table = element('table', undefined, 'w-full text-left text-sm');
    table.append(element('caption', `${race.year} ${race.label} finishers, in official place order. Chip times are shown exactly as published.`, 'sr-only'));
    const head = element('thead');
    const header = element('tr');
    for (const label of ['Place', 'Rider', 'Chip time']) {
      const cell = element('th', label, 'py-2 pr-3 text-xs font-medium text-slate-400');
      cell.scope = 'col';
      header.append(cell);
    }
    head.append(header);
    table.append(head);
    const rows = element('tbody', undefined, 'divide-y divide-slate-800');
    for (const result of race.results) {
      const row = element('tr');
      row.append(element('td', result.place, 'py-2 pr-3 tabular-nums text-slate-400'));
      row.append(element('td', result.name, 'py-2 pr-3 text-slate-200'));
      row.append(element('td', result.chip_time_str, 'py-2 tabular-nums whitespace-nowrap text-slate-200'));
      rows.append(row);
    }
    table.append(rows);
    body.append(table);
    const source = element('a', 'Official category results ↗', 'inline-block mt-3 text-xs text-sky-400 underline');
    // Only link to the timing provider; scraped strings are always rendered as text.
    const url = new URL(race.source_url, window.location.href);
    if (url.protocol === 'https:' && url.hostname === 'mountdiablochallenge.itsyourrace.com') {
      source.href = url.href;
      source.target = '_blank';
      source.rel = 'noopener noreferrer';
      body.append(source);
    }
    details.append(body);
    container.append(details);
  }
}
