/**
 * Year Filters Component
 * Manages year range selection dropdowns
 */

import { getDashboardData } from '../core/data.js';
import { setText } from '../utils/domUtils.js';

/**
 * Populate year dropdown menus
 */
export function init() {
  const dashboardData = getDashboardData();
  if (!dashboardData) return;

  const years = dashboardData.years;
  const startList = document.getElementById('startYearList');
  const endList = document.getElementById('endYearList');

  years.forEach(y => {
    const liStart = document.createElement('li');
    liStart.innerHTML = `<button data-select="startYear" class="w-full text-left px-3 py-2 text-sm hover:bg-slate-950">${y}</button>`;
    startList.appendChild(liStart);

    const liEnd = document.createElement('li');
    liEnd.innerHTML = `<button data-select="endYear" class="w-full text-left px-3 py-2 text-sm hover:bg-slate-950">${y}</button>`;
    endList.appendChild(liEnd);
  });

  // Set initial values
  setText('startYearValue', years[0]);
  setText('endYearValue', years[years.length - 1]);
}

/**
 * Get currently selected year range
 * @returns {Object} Object with startYear and endYear
 */
export function getSelectedYears() {
  const startYear = parseInt(document.getElementById('startYearValue').textContent);
  const endYear = parseInt(document.getElementById('endYearValue').textContent);
  return { startYear, endYear };
}

/**
 * Reset year filters to full range
 * @param {Function} onReset - Callback function to call after reset
 */
export function resetFilters(onReset) {
  const dashboardData = getDashboardData();
  if (!dashboardData) return;

  const years = dashboardData.years;
  setText('startYearValue', years[0]);
  setText('endYearValue', years[years.length - 1]);

  if (onReset) onReset();
}
