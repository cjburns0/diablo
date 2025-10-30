/**
 * Year-over-Year Delta Component
 * Displays YoY change metrics
 */

import { getDashboardData } from '../core/data.js';
import { calculateYoYMetrics } from '../core/kpiCalculator.js';

/**
 * Populate Year-over-Year metrics
 */
export function init() {
  const dashboardData = getDashboardData();
  if (!dashboardData) return;

  const stats = dashboardData.statistics.by_year;

  const metrics = calculateYoYMetrics(stats);

  if (metrics.lastYearChange === null) {
    // Not enough data for YoY calculations
    document.getElementById('yoy-last-year').textContent = 'N/A';
    document.getElementById('yoy-avg-change').textContent = 'N/A';
    document.getElementById('yoy-volatility').textContent = 'N/A';
    return;
  }

  // Last year vs prior (most recent YoY change)
  const lastYoYElement = document.getElementById('yoy-last-year');
  const lastYoYFormatted = `${metrics.lastYearChange >= 0 ? '+' : ''}${metrics.lastYearChange.toFixed(1)}%`;
  lastYoYElement.textContent = lastYoYFormatted;
  lastYoYElement.className = `font-medium tabular-nums ${metrics.lastYearChange < 0 ? 'text-emerald-400' : 'text-rose-400'}`;

  // Average annual change
  const avgChangeElement = document.getElementById('yoy-avg-change');
  const avgChangeFormatted = `${metrics.avgChange >= 0 ? '+' : ''}${metrics.avgChange.toFixed(1)}%`;
  avgChangeElement.textContent = avgChangeFormatted;
  avgChangeElement.className = `font-medium tabular-nums ${metrics.avgChange < 0 ? 'text-emerald-400' : 'text-slate-200'}`;

  // Volatility (standard deviation of YoY changes)
  document.getElementById('yoy-volatility').textContent = `σ = ${metrics.volatility.toFixed(1)}%`;
}
