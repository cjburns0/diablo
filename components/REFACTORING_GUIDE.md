# Dashboard Refactoring Guide

## Overview

This document outlines the refactoring of `dashboard.html` from a monolithic 1,870-line file into modular, maintainable components.

## What Has Been Completed

### Directory Structure
```
components/
├── core/                    # Core logic (no DOM dependencies)
│   ├── data.js             ✅ Data loading & state management
│   ├── gpxParser.js        ✅ GPX parsing & wind impact calculation
│   └── kpiCalculator.js    ✅ KPI and YoY metrics calculation
├── utils/                   # Utility functions
│   ├── geoUtils.js         ✅ Geospatial calculations
│   ├── formatters.js       ✅ Time/number formatting
│   └── domUtils.js         ✅ DOM helpers (tooltips, popovers, modals)
├── ui/                      # UI Components
│   ├── kpiCards.js         ✅ KPI card population
│   ├── yearFilters.js      ✅ Year range selection
│   ├── performanceOutliers.js ✅ Outliers list
│   ├── yoyDelta.js         ✅ Year-over-Year metrics
│   ├── courseDirection.js  ✅ Compass visualization
│   └── windImpact.js       ✅ Wind analysis display
└── main.js                  ✅ Application orchestrator
```

## What Remains To Be Done

### 1. Extract Chart Rendering (`mainChart.js`)

**Location in original**: Lines 944-1300+ in `dashboard.html`

**What to extract**:
- `renderChart()` function - Main chart rendering logic
- SVG generation for box plots, whiskers, median lines
- Wind overlay rendering
- Grid and axis rendering
- Year labels and wind data display
- Multi-year rider star markers
- All chart-related helper functions

**Structure**:
```javascript
// components/ui/mainChart.js
import { getDashboardData, getRouteData, getSelectedRider } from '../core/data.js';
import { calculateWindImpact } from '../core/gpxParser.js';
import { showTooltip, hideTooltip } from '../utils/domUtils.js';
import { formatTime } from '../utils/formatters.js';

export function render(startYear, endYear) {
  // Extract renderChart() function body here
  // ~400 lines of SVG generation code
}
```

### 2. Extract Rider Lookup (`riderLookup.js`)

**Location in original**: Lines 1720-1778 in `dashboard.html`

**What to extract**:
- `showRiderPerformance()` function
- Rider search event listeners
- Rider modal population
- Search results dropdown handling

**Structure**:
```javascript
// components/ui/riderLookup.js
import { getDashboardData, setSelectedRider } from '../core/data.js';

export function init() {
  // Initialize search input event listeners
}

export function showRiderPerformance(rider) {
  // Populate rider modal
  // Generate performance comparison HTML
}
```

### 3. Create Interactions Module (`interactions.js`)

**Location in original**: Lines 1793-1868 in `dashboard.html`

**What to extract**:
- Modal event handlers (upload, feedback, rider)
- Lucide icons initialization
- Any remaining event listeners not in other components

## How to Complete the Refactoring

### Step 1: Extract Main Chart

1. Open `dashboard.html` and find the `renderChart()` function (starts around line 944)
2. Copy the entire function into `components/ui/mainChart.js`
3. Add necessary imports at the top
4. Export the function as `export function render()`
5. Test that the chart still renders correctly

### Step 2: Extract Rider Lookup

1. Find the rider search and modal code (starts around line 1720)
2. Copy into `components/ui/riderLookup.js`
3. Add imports and export functions
4. Update `main.js` to call `RiderLookup.init()`

### Step 3: Update main.js

1. Import the new `mainChart` and `riderLookup` modules
2. Call `mainChart.render()` in appropriate places
3. Call `riderLookup.init()` during initialization

### Step 4: Update dashboard.html

Replace the entire `<script>` block (lines 419-1869) with:

```html
<script type="module" src="components/main.js"></script>
```

That's it! The HTML file will go from 1,870 lines to approximately 420 lines.

## Benefits of This Refactoring

✅ **Maintainability**: Each file is under 300 lines and has a single responsibility
✅ **Testability**: Core logic can be tested independently of DOM
✅ **Readability**: Clear separation of concerns
✅ **No Build Step**: Uses native ES6 modules - works directly in browsers
✅ **Same Functionality**: All features preserved exactly as they were

## File Size Comparison

**Before**:
- `dashboard.html`: 1,870 lines (100% of code)

**After**:
- `dashboard.html`: ~420 lines (22% of original)
- Component files: ~1,450 lines (spread across 13 files averaging ~110 lines each)

## Testing Checklist

After completing the refactoring, verify:

- [ ] KPI cards display correctly
- [ ] Main chart renders with all data points
- [ ] Wind overlay toggles on/off
- [ ] Year filters work and update the chart
- [ ] Performance outliers update when filters change
- [ ] Rider search finds multi-year riders
- [ ] Rider modal shows performance comparison
- [ ] Course direction compass displays
- [ ] Wind impact analysis shows beneficial/detrimental winds
- [ ] All modals open and close properly
- [ ] Upload widget functions
- [ ] No console errors

## Notes

- All components maintain the exact same functionality and appearance
- No changes to HTML structure or CSS/styling
- Components use ES6 module syntax (requires modern browser or local server)
- Lucide icons initialization remains in `main.js`
