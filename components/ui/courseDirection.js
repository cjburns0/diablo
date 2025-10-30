/**
 * Course Direction (Compass) Component
 * Renders the route direction compass visualization
 */

import { getRouteData } from '../core/data.js';
import { toRadians } from '../utils/geoUtils.js';

/**
 * Render route direction compass
 */
export function init() {
  const compass = document.getElementById('routeCompass');
  const routeData = getRouteData();

  if (!routeData) {
    compass.innerHTML = '<div class="text-slate-500">Route data not available</div>';
    return;
  }

  const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
  const directionNames = {
    'N': 'North', 'NNE': 'North-Northeast', 'NE': 'Northeast', 'ENE': 'East-Northeast',
    'E': 'East', 'ESE': 'East-Southeast', 'SE': 'Southeast', 'SSE': 'South-Southeast',
    'S': 'South', 'SSW': 'South-Southwest', 'SW': 'Southwest', 'WSW': 'West-Southwest',
    'W': 'West', 'WNW': 'West-Northwest', 'NW': 'Northwest', 'NNW': 'North-Northwest'
  };
  const size = 200;
  const center = size / 2;
  const maxRadius = center - 20;
  const metersToMiles = 0.000621371;

  // Create container with tooltip
  let html = '<div class="relative">';
  html += `<svg viewBox="0 0 ${size} ${size}" class="w-48 h-48" id="compassSvg">`;

  // Background circle
  html += `<circle cx="${center}" cy="${center}" r="${maxRadius}" fill="none" stroke="#334155" stroke-width="1"/>`;

  // Direction segments
  directions.forEach((dir, i) => {
    const angle = i * 22.5;
    const pct = routeData.directionPercentages[dir];
    const distanceMeters = routeData.directionDistances[dir];
    const distanceMiles = distanceMeters * metersToMiles;
    const radius = (pct / Math.max(...Object.values(routeData.directionPercentages))) * maxRadius;

    if (radius > 0) {
      const startAngle = angle - 11.25;
      const endAngle = angle + 11.25;

      // Create pie slice
      const x1 = center + radius * Math.sin(toRadians(startAngle));
      const y1 = center - radius * Math.cos(toRadians(startAngle));
      const x2 = center + radius * Math.sin(toRadians(endAngle));
      const y2 = center - radius * Math.cos(toRadians(endAngle));

      const largeArc = 0;

      html += `<path
        class="compass-segment cursor-pointer transition-opacity hover:opacity-100"
        data-direction="${dir}"
        data-direction-name="${directionNames[dir]}"
        data-distance-miles="${distanceMiles.toFixed(2)}"
        data-percentage="${pct.toFixed(1)}"
        d="M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z"
        fill="#0ea5e9"
        fill-opacity="${0.3 + (pct / 100)}"
        stroke="#0ea5e9"
        stroke-width="1"/>`;
    }
  });

  // Cardinal direction labels
  const labelRadius = maxRadius + 10;
  [
    {dir: 'N', angle: 0},
    {dir: 'E', angle: 90},
    {dir: 'S', angle: 180},
    {dir: 'W', angle: 270}
  ].forEach(({dir, angle}) => {
    const x = center + labelRadius * Math.sin(toRadians(angle));
    const y = center - labelRadius * Math.cos(toRadians(angle)) + 4;
    html += `<text x="${x}" y="${y}" text-anchor="middle" class="fill-slate-400 text-[10px] font-medium">${dir}</text>`;
  });

  // Center dot
  html += `<circle cx="${center}" cy="${center}" r="3" fill="#0ea5e9"/>`;
  html += '</svg>';

  // Tooltip (hidden by default)
  html += `<div id="compassTooltip" class="hidden absolute z-10 px-3 py-2 text-xs rounded-lg border border-slate-700 bg-slate-900 shadow-xl">
    <div class="font-semibold text-sky-400 mb-1" id="tooltipDirection"></div>
    <div class="text-slate-300"><span id="tooltipDistance"></span> miles</div>
    <div class="text-slate-400"><span id="tooltipPercentage"></span>% of route</div>
  </div>`;
  html += '</div>';

  // Add stats below
  const totalMiles = routeData.totalDistance * metersToMiles;
  html += `<div class="mt-2 text-center text-xs text-slate-500">
    Primary direction: <span class="text-sky-400 font-medium">${routeData.primaryDirection}</span>
  </div>`;
  html += `<div class="mt-1 text-center text-xs text-slate-500">
    Total distance: <span class="text-slate-300 font-medium">${totalMiles.toFixed(2)} miles</span>
  </div>`;

  compass.innerHTML = html;

  // Add hover event listeners
  const segments = compass.querySelectorAll('.compass-segment');
  const tooltip = document.getElementById('compassTooltip');
  const tooltipDirection = document.getElementById('tooltipDirection');
  const tooltipDistance = document.getElementById('tooltipDistance');
  const tooltipPercentage = document.getElementById('tooltipPercentage');

  segments.forEach(segment => {
    segment.addEventListener('mouseenter', (e) => {
      const dir = segment.getAttribute('data-direction');
      const dirName = segment.getAttribute('data-direction-name');
      const distance = segment.getAttribute('data-distance-miles');
      const percentage = segment.getAttribute('data-percentage');

      tooltipDirection.textContent = `${dir} - ${dirName}`;
      tooltipDistance.textContent = distance;
      tooltipPercentage.textContent = percentage;

      tooltip.classList.remove('hidden');
    });

    segment.addEventListener('mousemove', (e) => {
      const rect = compass.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      tooltip.style.left = `${x + 10}px`;
      tooltip.style.top = `${y + 10}px`;
    });

    segment.addEventListener('mouseleave', () => {
      tooltip.classList.add('hidden');
    });
  });
}
