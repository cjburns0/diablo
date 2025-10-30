/**
 * Performance Outliers Component
 * Displays years that are outliers relative to overall median
 */

import { getDashboardData } from '../core/data.js';
import { calculateOutliers } from '../core/kpiCalculator.js';

/**
 * Populate outliers list
 * @param {number} startYear - Filter start year
 * @param {number} endYear - Filter end year
 */
export function update(startYear, endYear) {
  const dashboardData = getDashboardData();
  if (!dashboardData) return;

  const stats = dashboardData.statistics.by_year;
  const weather = dashboardData.weather.by_year;
  const overallMedian = dashboardData.statistics.overall.overall_median_minutes;

  // Calculate top 3 outliers
  const topOutliers = calculateOutliers(stats, weather, overallMedian, startYear, endYear, 3);

  // Populate the list
  const outliersList = document.getElementById('outliers-list');
  outliersList.innerHTML = '';

  topOutliers.forEach(outlier => {
    const li = document.createElement('li');
    li.className = 'py-2 flex items-center justify-between text-sm';

    const pctSign = outlier.pctDiff >= 0 ? '+' : '';
    const colorClass = outlier.pctDiff >= 0 ? 'text-rose-400' : 'text-emerald-400';

    li.innerHTML = `
      <span class="text-slate-400">${outlier.year} (${outlier.windLabel})</span>
      <span class="font-medium tabular-nums ${colorClass}">${pctSign}${outlier.pctDiff.toFixed(1)}%</span>
    `;

    outliersList.appendChild(li);
  });
}
