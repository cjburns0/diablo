/**
 * KPI and statistical calculations
 */

/**
 * Calculate Year-over-Year metrics
 * @param {Array} byYearStats - Statistics by year
 * @returns {Object} YoY metrics including last year change, average change, volatility, and years compared
 */
export function calculateYoYMetrics(byYearStats) {
  if (byYearStats.length < 2) {
    return {
      lastYearChange: null,
      avgChange: null,
      volatility: null,
      currentYear: null,
      priorYear: null
    };
  }

  // Calculate YoY changes in median time
  const yoyChanges = [];
  for (let i = 1; i < byYearStats.length; i++) {
    const prevMedian = byYearStats[i - 1].times.median;
    const currMedian = byYearStats[i].times.median;
    const pctChange = ((currMedian - prevMedian) / prevMedian) * 100;
    yoyChanges.push(pctChange);
  }

  // Last year vs prior (most recent YoY change)
  const lastYearChange = yoyChanges[yoyChanges.length - 1];

  // Get the years being compared (last two years in the data)
  const currentYear = byYearStats[byYearStats.length - 1].year;
  const priorYear = byYearStats[byYearStats.length - 2].year;

  // Average annual change
  const avgChange = yoyChanges.reduce((sum, val) => sum + val, 0) / yoyChanges.length;

  // Volatility (standard deviation of YoY changes)
  const squaredDiffs = yoyChanges.map(val => Math.pow(val - avgChange, 2));
  const variance = squaredDiffs.reduce((sum, val) => sum + val, 0) / yoyChanges.length;
  const volatility = Math.sqrt(variance);

  return {
    lastYearChange,
    avgChange,
    volatility,
    currentYear,
    priorYear
  };
}

/**
 * Calculate performance outliers relative to overall median
 * @param {Array} byYearStats - Statistics by year
 * @param {Array} byYearWeather - Weather by year
 * @param {number} overallMedian - Overall median time in minutes
 * @param {number} startYear - Filter start year
 * @param {number} endYear - Filter end year
 * @param {number} topN - Number of outliers to return
 * @returns {Array} Top outliers sorted by absolute percent difference
 */
export function calculateOutliers(byYearStats, byYearWeather, overallMedian, startYear, endYear, topN = 3) {
  // Calculate percent difference from overall median for each year
  const yearData = byYearStats
    .filter(yearStats => yearStats.year >= startYear && yearStats.year <= endYear)
    .map(yearStats => {
      const medianMinutes = yearStats.times.median;
      const pctDiff = ((medianMinutes - overallMedian) / overallMedian) * 100;

      // Find the correct weather index for this year
      const weatherIdx = byYearWeather.findIndex(w => w.year === yearStats.year);
      const wind = weatherIdx >= 0 ? (byYearWeather[weatherIdx]?.summit?.wind_speed_avg || 0) : 0;

      return {
        year: yearStats.year,
        pctDiff: pctDiff,
        wind: wind,
        windLabel: wind > 10 ? 'high wind' : wind < 3 ? 'calm' : 'moderate wind'
      };
    });

  // Sort by absolute percent difference to find outliers
  const sortedByDiff = [...yearData].sort((a, b) => Math.abs(b.pctDiff) - Math.abs(a.pctDiff));

  // Take top N outliers
  return sortedByDiff.slice(0, Math.min(topN, sortedByDiff.length));
}
