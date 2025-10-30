/**
 * Rider Lookup Component
 * Handles rider search and performance modal display
 */

import { getDashboardData, setSelectedRider } from '../core/data.js';
import * as MainChart from './mainChart.js';
import { getSelectedYears } from './yearFilters.js';

/**
 * Show rider performance in modal and highlight on chart
 * @param {Object} rider - Rider object with performances
 */
export function showRiderPerformance(rider) {
  setSelectedRider(rider);

  // Re-render chart to show stars
  const { startYear, endYear } = getSelectedYears();
  MainChart.render(startYear, endYear);

  const riderModal = document.getElementById('riderModal');
  const riderModalName = document.getElementById('riderModalName');
  const riderModalContent = document.getElementById('riderModalContent');
  const dashboardData = getDashboardData();

  // Set rider name
  riderModalName.textContent = rider.name;

  // Calculate year-over-year changes
  const performances = rider.performances;
  const yoyChanges = [];

  for (let i = 1; i < performances.length; i++) {
    const prevPerf = performances[i - 1];
    const currPerf = performances[i];
    const timeDiff = currPerf.time_seconds - prevPerf.time_seconds;
    const pctChange = (timeDiff / prevPerf.time_seconds) * 100;

    // Get pack median for both years
    const prevYearStats = dashboardData.statistics.by_year.find(y => y.year === prevPerf.year);
    const currYearStats = dashboardData.statistics.by_year.find(y => y.year === currPerf.year);

    const prevPackMedian = prevYearStats ? prevYearStats.times.median * 60 : null;
    const currPackMedian = currYearStats ? currYearStats.times.median * 60 : null;

    const packTimeDiff = currPackMedian && prevPackMedian ? currPackMedian - prevPackMedian : null;
    const packPctChange = packTimeDiff && prevPackMedian ? (packTimeDiff / prevPackMedian) * 100 : null;

    const vsPackDiff = packPctChange !== null ? pctChange - packPctChange : null;

    yoyChanges.push({
      fromYear: prevPerf.year,
      toYear: currPerf.year,
      riderChange: pctChange,
      packChange: packPctChange,
      vsPackDiff: vsPackDiff,
      riderTimeChange: timeDiff
    });
  }

  // Build modal content
  let content = `
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="rounded-lg border p-4 border-slate-800 bg-black">
        <div class="text-xs uppercase tracking-wide text-slate-500 mb-2">Participation History</div>
        <div class="space-y-2">
          ${performances.map(perf => `
            <div class="flex items-center justify-between text-sm">
              <span class="text-slate-400">${perf.year}</span>
              <div class="text-right">
                <div class="text-slate-200 font-medium">${perf.time_formatted}</div>
                <div class="text-slate-500 text-xs">Place ${perf.place}</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="rounded-lg border p-4 border-slate-800 bg-black">
        <div class="text-xs uppercase tracking-wide text-slate-500 mb-2">Summary Stats</div>
        <div class="space-y-2 text-sm">
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Years participated</span>
            <span class="text-slate-200 font-medium">${rider.years_participated}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Best time</span>
            <span class="text-slate-200 font-medium">${performances.reduce((best, p) => p.time_seconds < best.time_seconds ? p : best).time_formatted}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-400">Best place</span>
            <span class="text-slate-200 font-medium">${Math.min(...performances.map(p => p.place))}</span>
          </div>
        </div>
      </div>
    </div>
  `;

  if (yoyChanges.length > 0) {
    content += `
      <div class="mt-4">
        <div class="text-sm font-medium text-slate-200 mb-3">Year-over-Year Performance</div>
        <div class="space-y-3">
          ${yoyChanges.map(change => {
            const riderColor = change.riderChange < 0 ? 'text-emerald-400' : 'text-rose-400';
            const packColor = change.packChange < 0 ? 'text-emerald-400' : 'text-rose-400';
            const vsPackColor = change.vsPackDiff < 0 ? 'text-emerald-400' : 'text-rose-400';
            const riderSign = change.riderChange >= 0 ? '+' : '';
            const packSign = change.packChange >= 0 ? '+' : '';
            const vsPackSign = change.vsPackDiff >= 0 ? '+' : '';

            return `
              <div class="rounded-lg border p-4 border-slate-800">
                <div class="text-sm font-medium text-slate-300 mb-3">${change.fromYear} → ${change.toYear}</div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                  <div>
                    <div class="text-slate-500 text-xs mb-1">Rider Change</div>
                    <div class="${riderColor} font-medium tabular-nums">${riderSign}${change.riderChange.toFixed(1)}%</div>
                    <div class="text-slate-500 text-xs">${riderSign}${change.riderTimeChange.toFixed(0)}s</div>
                  </div>
                  <div>
                    <div class="text-slate-500 text-xs mb-1">Pack Median Change</div>
                    <div class="${packColor} font-medium tabular-nums">${packSign}${change.packChange.toFixed(1)}%</div>
                  </div>
                  <div>
                    <div class="text-slate-500 text-xs mb-1">vs Pack</div>
                    <div class="${vsPackColor} font-medium tabular-nums">${vsPackSign}${change.vsPackDiff.toFixed(1)}%</div>
                    <div class="text-slate-500 text-xs">${change.vsPackDiff < 0 ? 'Outperformed' : 'Underperformed'}</div>
                  </div>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  }

  riderModalContent.innerHTML = content;
  riderModal.classList.remove('hidden');

  // Re-initialize lucide icons for the modal
  if (window.lucide) {
    lucide.createIcons({ attrs: { 'stroke-width': 1.5 } });
  }
}

/**
 * Initialize rider search functionality
 */
export function init() {
  const dashboardData = getDashboardData();
  const riderSearchInput = document.getElementById('riderSearch');
  const riderSearchResults = document.getElementById('riderSearchResults');

  riderSearchInput.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase().trim();

    if (query.length < 2) {
      riderSearchResults.classList.add('hidden');
      return;
    }

    if (!dashboardData || !dashboardData.riders) {
      return;
    }

    // Filter riders by name
    const matches = dashboardData.riders.filter(rider =>
      rider.name.toLowerCase().includes(query)
    );

    if (matches.length === 0) {
      riderSearchResults.classList.add('hidden');
      return;
    }

    // Populate results dropdown
    riderSearchResults.innerHTML = '';
    matches.slice(0, 10).forEach(rider => {
      const li = document.createElement('div');
      li.className = 'px-3 py-2 text-sm hover:bg-slate-950 cursor-pointer border-b border-slate-800 last:border-b-0';
      li.innerHTML = `
        <div class="flex items-center justify-between">
          <div>
            <div class="text-slate-200 font-medium">${rider.name}</div>
            <div class="text-slate-500 text-xs">${rider.years_participated} years: ${rider.performances.map(p => p.year).join(', ')}</div>
          </div>
          <span class="text-amber-400">★</span>
        </div>
      `;
      li.addEventListener('click', () => {
        showRiderPerformance(rider);
        riderSearchResults.classList.add('hidden');
        riderSearchInput.value = '';
      });
      riderSearchResults.appendChild(li);
    });

    riderSearchResults.classList.remove('hidden');
  });

  // Close search results when clicking outside
  document.addEventListener('click', (e) => {
    if (!riderSearchInput.contains(e.target) && !riderSearchResults.contains(e.target)) {
      riderSearchResults.classList.add('hidden');
    }
  });
}
