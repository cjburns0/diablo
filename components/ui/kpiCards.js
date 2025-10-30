/**
 * KPI Cards Component
 * Manages the 4 KPI cards: Fastest Year, Wind Impact, Median Time, Sample Size
 */

import { getDashboardData } from '../core/data.js';

/**
 * Populate KPI cards with data
 */
export function init() {
  const dashboardData = getDashboardData();
  if (!dashboardData) return;

  const stats = dashboardData.statistics.overall;

  document.getElementById('kpi-fastest-year').textContent = `${stats.fastest_year_by_median} / ${stats.fastest_year_by_winner}`;
  document.getElementById('kpi-fastest-pct').textContent = `Median / Winner`;
  document.getElementById('kpi-wind-corr').textContent = `r = ${stats.wind_correlation || 'N/A'}`;
  document.getElementById('kpi-median-time').textContent = stats.overall_median_formatted;
  document.getElementById('kpi-fastest-time').textContent = `Fastest: ${stats.fastest_time}`;
  document.getElementById('kpi-total-years').textContent = `${stats.total_years} yrs`;
  document.getElementById('kpi-year-range').textContent = stats.year_range;
  document.getElementById('filter-wind-corr').textContent = `r = ${stats.wind_correlation || 'N/A'}`;
}
