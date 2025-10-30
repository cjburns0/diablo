/**
 * GPX file parsing and route analysis
 */

import { haversineDistance, calculateBearing, bearingToDirection, toRadians } from '../utils/geoUtils.js';

/**
 * Parse GPX file and calculate route directional distribution
 * @returns {Promise<Object|null>} Route data with points, distances, and directional distribution
 */
export async function fetchAndParseGPX() {
  try {
    const response = await fetch('data/Diablo%20Standard%20Uphill%20Only.gpx');
    if (!response.ok) {
      console.warn('GPX file not found. Wind directionality features will be disabled.');
      return null;
    }

    const gpxText = await response.text();
    const parser = new DOMParser();
    const gpxDoc = parser.parseFromString(gpxText, 'text/xml');

    // Extract track points
    const trkpts = gpxDoc.querySelectorAll('trkpt');
    if (trkpts.length === 0) {
      console.warn('No track points found in GPX file.');
      return null;
    }

    const points = Array.from(trkpts).map(pt => ({
      lat: parseFloat(pt.getAttribute('lat')),
      lon: parseFloat(pt.getAttribute('lon'))
    }));

    console.log(`Parsed ${points.length} GPS points from route`);

    // Calculate distance traveled in each direction
    const directionDistances = {};
    const directions = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'];
    directions.forEach(dir => directionDistances[dir] = 0);

    let totalDistance = 0;

    for (let i = 0; i < points.length - 1; i++) {
      const p1 = points[i];
      const p2 = points[i + 1];

      const distance = haversineDistance(p1.lat, p1.lon, p2.lat, p2.lon);
      const bearing = calculateBearing(p1.lat, p1.lon, p2.lat, p2.lon);
      const direction = bearingToDirection(bearing);

      directionDistances[direction] += distance;
      totalDistance += distance;
    }

    // Convert to percentages
    const directionPercentages = {};
    directions.forEach(dir => {
      directionPercentages[dir] = (directionDistances[dir] / totalDistance) * 100;
    });

    console.log('Route directional distribution:', directionPercentages);

    return {
      points: points,
      directionDistances: directionDistances,
      directionPercentages: directionPercentages,
      totalDistance: totalDistance,
      primaryDirection: Object.keys(directionPercentages).reduce((a, b) =>
        directionPercentages[a] > directionPercentages[b] ? a : b
      )
    };
  } catch (error) {
    console.error('Error parsing GPX file:', error);
    return null;
  }
}

/**
 * Calculate wind benefit for a given wind direction based on route
 * @param {number} windDirection - Wind direction in degrees
 * @param {Object} routeData - Route data from fetchAndParseGPX
 * @returns {Object} Wind impact analysis with impact category and score
 */
export function calculateWindImpact(windDirection, routeData) {
  if (!routeData || !routeData.directionPercentages) return { impact: 'neutral', score: 0 };

  // Calculate component of wind in each travel direction
  let totalBenefit = 0;

  Object.keys(routeData.directionPercentages).forEach(travelDir => {
    const travelBearing = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW'].indexOf(travelDir) * 22.5;
    const travelPct = routeData.directionPercentages[travelDir];

    // Calculate angle difference (tailwind is 180° behind travel direction)
    let angleDiff = Math.abs(windDirection - travelBearing);
    if (angleDiff > 180) angleDiff = 360 - angleDiff;

    // Tailwind component: cos(angleDiff) where 0° = headwind, 180° = tailwind
    const tailwindComponent = -Math.cos(toRadians(angleDiff));

    // Weight by distance traveled in this direction
    totalBenefit += tailwindComponent * travelPct;
  });

  // Normalize score (-1 = pure headwind, +1 = pure tailwind)
  const normalizedScore = totalBenefit / 100;

  let impact;
  if (normalizedScore < -0.3) impact = 'detrimental';
  else if (normalizedScore > 0.3) impact = 'beneficial';
  else impact = 'neutral';

  return { impact, score: normalizedScore };
}
