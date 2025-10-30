/**
 * Main Application Entry Point
 * Orchestrates all dashboard components and initialization
 */

// Core modules
import { fetchDashboardData, getDashboardData, setRouteData, getRouteData, setSelectedRider } from './core/data.js';
import { fetchAndParseGPX } from './core/gpxParser.js';

// UI Components
import * as KPICards from './ui/kpiCards.js';
import * as YearFilters from './ui/yearFilters.js';
import * as PerformanceOutliers from './ui/performanceOutliers.js';
import * as YoYDelta from './ui/yoyDelta.js';
import * as CourseDirection from './ui/courseDirection.js';
import * as WindImpact from './ui/windImpact.js';
import * as MainChart from './ui/mainChart.js';
import * as RiderLookup from './ui/riderLookup.js';

// Utils
import { initPopovers, setText, closeAllPopovers } from './utils/domUtils.js';

/**
 * Initialize all dashboard components
 */
function initializeComponents() {
  // Initialize UI components
  KPICards.init();
  YearFilters.init();
  YoYDelta.init();

  // Get initial year range and render
  const { startYear, endYear } = YearFilters.getSelectedYears();
  PerformanceOutliers.update(startYear, endYear);
  MainChart.render(startYear, endYear);

  // Initialize route-dependent components
  if (getRouteData()) {
    CourseDirection.init();
    WindImpact.init();
  }

  // Initialize rider search
  RiderLookup.init();

  // Initialize popovers
  initPopovers();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
  // Year filter selection events
  document.addEventListener('click', (e) => {
    const t = e.target;
    if (!(t instanceof HTMLElement)) return;

    if (t.matches('[data-select="startYear"]')) {
      setText('startYearValue', t.textContent.trim());
      closeAllPopovers();
    }
    if (t.matches('[data-select="endYear"]')) {
      setText('endYearValue', t.textContent.trim());
      closeAllPopovers();
    }
  });

  // Apply filters button
  document.getElementById('applyFilters')?.addEventListener('click', () => {
    const dashboardData = getDashboardData();
    if (dashboardData) {
      const { startYear, endYear } = YearFilters.getSelectedYears();
      PerformanceOutliers.update(startYear, endYear);
      MainChart.render(startYear, endYear);
    }
  });

  // Reset filters button
  document.getElementById('resetFilters')?.addEventListener('click', () => {
    YearFilters.resetFilters(() => {
      const dashboardData = getDashboardData();
      if (dashboardData) {
        const { startYear, endYear } = YearFilters.getSelectedYears();
        PerformanceOutliers.update(startYear, endYear);
        MainChart.render(startYear, endYear);
      }
    });
  });

  // Wind layer toggle
  document.getElementById('toggle-wind')?.addEventListener('click', function() {
    const windLayer = document.getElementById('layer-wind');
    const pressed = this.getAttribute('aria-pressed') === 'true';

    this.setAttribute('aria-pressed', String(!pressed));

    if (windLayer) {
      windLayer.setAttribute('opacity', pressed ? '0' : '1');
    }

    if (pressed) {
      this.classList.remove('bg-sky-900');
    } else {
      this.classList.add('bg-sky-900');
    }
  });

  // Upload modal
  const uploadButton = document.getElementById('uploadButton');
  const uploadModal = document.getElementById('uploadModal');
  const closeModal = document.getElementById('closeModal');

  uploadButton?.addEventListener('click', () => {
    uploadModal?.classList.remove('hidden');
    if (window.lucide) {
      lucide.createIcons({ attrs: { 'stroke-width': 1.5 } });
    }
  });

  closeModal?.addEventListener('click', () => {
    uploadModal?.classList.add('hidden');
  });

  uploadModal?.addEventListener('click', (e) => {
    if (e.target === uploadModal) {
      uploadModal.classList.add('hidden');
    }
  });

  // Feedback modal
  const feedbackButton = document.getElementById('feedbackButton');
  const feedbackModal = document.getElementById('feedbackModal');
  const closeFeedbackModal = document.getElementById('closeFeedbackModal');

  feedbackButton?.addEventListener('click', () => {
    feedbackModal?.classList.remove('hidden');
    if (window.lucide) {
      lucide.createIcons({ attrs: { 'stroke-width': 1.5 } });
    }
  });

  closeFeedbackModal?.addEventListener('click', () => {
    feedbackModal?.classList.add('hidden');
  });

  feedbackModal?.addEventListener('click', (e) => {
    if (e.target === feedbackModal) {
      feedbackModal.classList.add('hidden');
    }
  });

  // Rider modal close handlers
  const closeRiderModal = document.getElementById('closeRiderModal');
  const riderModal = document.getElementById('riderModal');

  const closeRiderModalAndClearStars = () => {
    riderModal?.classList.add('hidden');
    setSelectedRider(null);
    const { startYear, endYear } = YearFilters.getSelectedYears();
    MainChart.render(startYear, endYear);
  };

  closeRiderModal?.addEventListener('click', closeRiderModalAndClearStars);

  riderModal?.addEventListener('click', (e) => {
    if (e.target === riderModal) {
      closeRiderModalAndClearStars();
    }
  });

  // Keyboard shortcuts (Escape key)
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (uploadModal && !uploadModal.classList.contains('hidden')) {
        uploadModal.classList.add('hidden');
      }
      if (feedbackModal && !feedbackModal.classList.contains('hidden')) {
        feedbackModal.classList.add('hidden');
      }
      if (riderModal && !riderModal.classList.contains('hidden')) {
        closeRiderModalAndClearStars();
      }
    }
  });
}

/**
 * Main initialization function
 */
async function initialize() {
  try {
    console.log('Loading dashboard data...');
    await fetchDashboardData();

    console.log('Loading route data...');
    const routeData = await fetchAndParseGPX();
    setRouteData(routeData);

    console.log('Initializing components...');
    initializeComponents();

    console.log('Setting up event listeners...');
    setupEventListeners();

    // Initialize lucide icons
    if (window.lucide) {
      lucide.createIcons({ attrs: { 'stroke-width': 1.5 } });
    }

    console.log('Dashboard initialized successfully!');
  } catch (error) {
    console.error('Error initializing dashboard:', error);
  }
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initialize);
} else {
  initialize();
}
