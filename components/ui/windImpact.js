/**
 * Wind Impact Component
 * Analyzes and displays beneficial/detrimental wind directions
 */

import { getRouteData } from '../core/data.js';
import { calculateWindImpact } from '../core/gpxParser.js';

/**
 * Render wind benefit/detriment analysis
 */
export function init() {
  const box = document.getElementById('windBenefitBox');
  const routeData = getRouteData();

  if (!routeData) {
    box.innerHTML = '<div class="text-slate-500">Route data required for analysis</div>';
    return;
  }

  // Analyze wind directions
  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const beneficial = [];
  const detrimental = [];
  const neutral = [];

  directions.forEach((dir, i) => {
    const bearing = i * 22.5;
    const impact = calculateWindImpact(bearing, routeData);

    if (impact.impact === 'beneficial') beneficial.push(dir);
    else if (impact.impact === 'detrimental') detrimental.push(dir);
    else neutral.push(dir);
  });

  let html = '<div class="space-y-2">';

  if (beneficial.length > 0) {
    html += `
      <div class="flex items-start gap-2">
        <div class="px-2 py-0.5 rounded text-xs font-medium bg-emerald-900/30 text-emerald-400 whitespace-nowrap">Beneficial</div>
        <div class="text-slate-400 text-xs">${beneficial.join(', ')}</div>
      </div>
    `;
  }

  if (detrimental.length > 0) {
    html += `
      <div class="flex items-start gap-2">
        <div class="px-2 py-0.5 rounded text-xs font-medium bg-rose-900/30 text-rose-400 whitespace-nowrap">Detrimental</div>
        <div class="text-slate-400 text-xs">${detrimental.join(', ')}</div>
      </div>
    `;
  }

  html += '</div>';
  box.innerHTML = html;
}
