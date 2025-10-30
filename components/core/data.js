/**
 * Data loading and state management
 */

// Module state
let dashboardData = null;
let routeData = null;
let selectedRider = null;

/**
 * Fetch dashboard data from JSON file
 * @returns {Promise<void>}
 */
export async function fetchDashboardData() {
  try {
    const response = await fetch('data/dashboard_data.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    dashboardData = await response.json();
    console.log('Dashboard data loaded successfully');
  } catch (error) {
    console.error('Error loading dashboard data:', error);
    // Show error message to user
    document.body.innerHTML = `
      <div style="display: flex; align-items: center; justify-content: center; height: 100vh; background: #000; color: #ef4444; font-family: Inter, sans-serif;">
        <div style="text-align: center;">
          <h1 style="font-size: 24px; margin-bottom: 16px;">Failed to Load Dashboard Data</h1>
          <p style="color: #94a3b8;">Error: ${error.message}</p>
          <p style="color: #64748b; margin-top: 8px;">Please ensure data/dashboard_data.json exists and is accessible.</p>
        </div>
      </div>
    `;
  }
}

/**
 * Get dashboard data
 * @returns {Object|null}
 */
export function getDashboardData() {
  return dashboardData;
}

/**
 * Set route data
 * @param {Object} data
 */
export function setRouteData(data) {
  routeData = data;
}

/**
 * Get route data
 * @returns {Object|null}
 */
export function getRouteData() {
  return routeData;
}

/**
 * Set selected rider
 * @param {string} rider
 */
export function setSelectedRider(rider) {
  selectedRider = rider;
}

/**
 * Get selected rider
 * @returns {string|null}
 */
export function getSelectedRider() {
  return selectedRider;
}

/**
 * Get filtered data by year range
 * @param {number} startYear
 * @param {number} endYear
 * @returns {Object}
 */
export function getFilteredData(startYear, endYear) {
  if (!dashboardData) return { statistics: [], weather: [] };

  return {
    statistics: dashboardData.statistics.by_year.filter(d => d.year >= startYear && d.year <= endYear),
    weather: dashboardData.weather.by_year.filter(d => d.year >= startYear && d.year <= endYear)
  };
}
