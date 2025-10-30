/**
 * Formatting utility functions for time, numbers, and other data
 */

/**
 * Format time in minutes as mm:ss
 * @param {number} timeMinutes - Time in minutes (can be decimal)
 * @returns {string} Formatted time string (mm:ss)
 */
export function formatTime(timeMinutes) {
  const minutes = Math.floor(timeMinutes);
  const seconds = Math.round((timeMinutes % 1) * 60);
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

/**
 * Format seconds as mm:ss
 * @param {number} timeSeconds - Time in seconds
 * @returns {string} Formatted time string (mm:ss)
 */
export function formatSeconds(timeSeconds) {
  const minutes = Math.floor(timeSeconds / 60);
  const seconds = Math.round(timeSeconds % 60);
  return `${minutes}:${String(seconds).padStart(2, '0')}`;
}

/**
 * Format number with specified decimal places
 * @param {number} value - Number to format
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted number
 */
export function formatNumber(value, decimals = 2) {
  return value.toFixed(decimals);
}

/**
 * Format percentage
 * @param {number} value - Decimal value (e.g., 0.45 for 45%)
 * @param {number} decimals - Number of decimal places
 * @returns {string} Formatted percentage string
 */
export function formatPercentage(value, decimals = 1) {
  return `${(value * 100).toFixed(decimals)}%`;
}
