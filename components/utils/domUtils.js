/**
 * DOM utility functions for tooltips, popovers, and modals
 */

/**
 * Show tooltip near mouse cursor
 * @param {Event} event - Mouse event
 * @param {string} content - HTML content for tooltip
 */
export function showTooltip(event, content) {
  const tooltip = document.getElementById('chart-tooltip');
  const tooltipContent = document.getElementById('tooltip-content');

  tooltipContent.innerHTML = content;
  tooltip.classList.remove('hidden');

  // Position tooltip near mouse cursor
  const svg = document.getElementById('main-chart');
  const svgRect = svg.getBoundingClientRect();
  const x = event.clientX - svgRect.left;
  const y = event.clientY - svgRect.top;

  tooltip.style.left = `${x + 10}px`;
  tooltip.style.top = `${y - 10}px`;
}

/**
 * Hide tooltip
 */
export function hideTooltip() {
  const tooltip = document.getElementById('chart-tooltip');
  tooltip.classList.add('hidden');
}

/**
 * Close all popovers
 */
export function closeAllPopovers() {
  document.querySelectorAll('[data-popover]').forEach(p => p.classList.add('hidden'));
}

/**
 * Set text content of element by ID
 * @param {string} id - Element ID
 * @param {string} value - Text value to set
 */
export function setText(id, value) {
  const el = document.getElementById(id);
  if (el) el.textContent = value;
}

/**
 * Close rider modal and clear selection
 * @param {Function} clearSelectionCallback - Callback to clear rider selection
 */
export function closeRiderModalAndClearStars(clearSelectionCallback) {
  const riderModal = document.getElementById('riderModal');
  riderModal.classList.add('hidden');
  if (clearSelectionCallback) clearSelectionCallback();
}

/**
 * Initialize popover event listeners
 */
export function initPopovers() {
  document.querySelectorAll('[data-popover-button]').forEach(btn => {
    const targetSel = btn.getAttribute('data-popover-button');
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const pop = document.querySelector(targetSel);
      const isOpen = pop && !pop.classList.contains('hidden');
      closeAllPopovers();
      if (pop && !isOpen) pop.classList.remove('hidden');
    });
  });
  document.addEventListener('click', closeAllPopovers);
}
