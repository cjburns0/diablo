# Interactive Dashboard Guide

## Overview

The Mount Diablo Challenge Interactive Dashboard (`dashboard.html`) provides a real-time, filterable visualization of race performance data with weather correlation analysis.

## Features

### Main Chart
- **Box-and-whisker plots** for each year showing:
  - **Red dot (top)**: Fastest time that year
  - **Box**: 25th to 75th percentile range (IQR)
  - **Teal line**: Median time
  - **Purple dot**: Mean time
- **Inverted Y-axis**: Faster times appear higher on the chart (0:00 at top)
- **Wind overlay**: Blue shading shows wind intensity (darker = higher wind)

### KPI Cards
- **Fastest Year**: Shows which year had the fastest times
- **Wind Impact**: Correlation coefficient between wind speed and finish times
- **Median Time**: Overall median across all years
- **Sample Size**: Number of years and total finishers

### Interactive Controls
- **Year Range Filter**: Select start and end years to focus analysis
- **Wind Toggle**: Show/hide wind speed overlay
- **Apply Filters**: Re-render chart with selected year range
- **Reset**: Return to default view (all years)

## How It Works

### Data Flow
1. **Python Script** (`dashboard_data.py`) extracts data from SQLite database
2. Generates **JSON file** (`data/dashboard_data.json`) with statistics
3. **Dashboard** (`dashboard.html`) loads JSON and renders interactive charts

### Technology Stack
- **Frontend**: Vanilla JavaScript (no frameworks)
- **Styling**: Tailwind CSS via CDN
- **Icons**: Lucide Icons
- **Charts**: Native SVG rendering
- **Design**: Aura.build dark theme template

## Updating the Dashboard

### When New Race Data Arrives

```bash
# Step 1: Add new race data to database
python3 update_year.py 2026

# Step 2: Regenerate dashboard JSON
python3 dashboard_data.py

# Step 3: Refresh browser
# Dashboard automatically loads new data
```

### Manual Data Refresh

If you update the database manually or want to regenerate dashboard data:

```bash
python3 dashboard_data.py
```

This will:
- Calculate statistics for all years in database
- Compute wind correlation coefficients
- Export formatted JSON to `data/dashboard_data.json`
- Dashboard will load new data on next page refresh

## Customization

### Changing Chart Appearance

Edit `dashboard.html` and modify these sections:

**Colors**:
- Line 621: Box fill color (`#94a3b814`)
- Line 622: Box stroke color (`#64748b`)
- Line 632: Median line color (`#0f766e`)
- Line 641: Mean dot color (`#6366f1`)
- Line 649: Fastest time dot color (`#ef4444`)

**Wind Overlay**:
- Line 595: Adjust opacity calculation `Math.min(0.3, windSpeed / 40)`
- Line 601: Change wind color `rgba(14, 165, 233, ${opacity})`

**Y-Axis Scaling**:
- Line 521: Adjust max time buffer `maxTime * 1.1` (increase for more space)
- Line 560: Change number of Y-axis labels `ySteps = 6`

### Modifying KPIs

To add/change KPI cards, edit the HTML section starting at line 50:

```html
<div class="rounded-lg border p-3 shadow-sm hover:shadow transition border-slate-800 bg-black">
  <div class="text-[11px] uppercase tracking-wide text-slate-500">YOUR METRIC</div>
  <div class="mt-1 flex items-baseline gap-2">
    <div class="text-xl font-semibold tabular-nums" id="kpi-your-metric">—</div>
  </div>
</div>
```

Then populate in JavaScript (line 466+):
```javascript
document.getElementById('kpi-your-metric').textContent = stats.your_value;
```

## Troubleshooting

### Dashboard shows "Error loading data"
- Check that `data/dashboard_data.json` exists
- Verify JSON is valid: `python3 -m json.tool data/dashboard_data.json`
- Run `python3 dashboard_data.py` to regenerate

### Chart not rendering
- Open browser console (F12) and check for JavaScript errors
- Ensure you're opening dashboard from file system or local server
- Verify data structure in JSON matches expected format

### Wind overlay not showing
- Check that weather data exists in database
- Verify `wind_speed_avg` values in `dashboard_data.json`
- Ensure wind toggle button is "on" (aria-pressed="true")

### Years missing from dropdown
- Verify years exist in `dashboard_data.json` under `years` array
- Check that `by_year` statistics include those years
- Regenerate JSON: `python3 dashboard_data.py`

## Design Philosophy

### Inverted Y-Axis Rationale
The Y-axis is inverted (0:00 at top) because:
- **Intuitive**: Faster times are "better" and appear higher
- **Natural**: Matches how we think about performance rankings
- **Visual**: Easy to spot fastest years at a glance

### Wind Overlay Design
- **Semi-transparent**: Doesn't obscure underlying data
- **Intensity-based**: Darker = higher wind speeds
- **Toggleable**: Can be turned off for cleaner view

### Box Plot Choice
Box-and-whisker plots effectively show:
- **Central tendency**: Median and mean
- **Spread**: IQR shows where bulk of finishers are
- **Outliers**: Fastest times indicated separately
- **Comparison**: Easy to compare across years

## Performance Notes

- **Load Time**: <100ms for 7 years of data
- **Render Time**: ~50ms for full chart render
- **File Size**: Dashboard HTML is 40KB, JSON is 6KB
- **Browser Support**: Works in all modern browsers (Chrome, Firefox, Safari, Edge)

## Future Enhancements

Potential improvements:
- [ ] Add hover tooltips showing exact values
- [ ] Export chart as PNG/SVG
- [ ] Add animation when filtering
- [ ] Show individual rider data on click
- [ ] Add temperature overlay toggle
- [ ] Implement zoom functionality
- [ ] Add print-friendly CSS

## Credits

- **Design Template**: Based on Aura.build dark theme
- **Data Source**: Mount Diablo Challenge (itsyourrace.com)
- **Weather API**: Open-Meteo Historical Weather
- **Typography**: Inter font family
