# Mount Diablo Challenge Race Analysis - Project Plan

## Overview

This document outlines the comprehensive plan to scrape, store, analyze, and visualize the Mount Diablo Challenge race results, incorporating detailed weather data.

---

## Phase 1: Scraping Race Results

### Objective
Extract all race result data from the provided URL.

### Implementation

**1. Python Environment Setup:**
- Ensure Python 3.9+ is installed
- Install necessary libraries:
  ```bash
  pip install requests beautifulsoup4 pandas matplotlib seaborn jupyter
  ```

**2. Scraping Logic:**
- Use the `requests` library to fetch HTML content from: https://mountdiablochallenge.itsyourrace.com/Results.aspx?id=11068
- Use BeautifulSoup to parse the HTML
- The results are in a `<table>` with ID `resultsTable`
- Iterate through each row (`<tr>`) of the table body (`<tbody>`)
- For each row, extract text from each cell (`<td>`)

**Columns to Extract:**
- Place
- Name
- Team Name
- City/State
- Gender
- Gender Place
- Age
- Age Place
- Chip Time
- Pace
- Start Time

**Data Storage:**
- Store scraped data in a list of dictionaries or Pandas DataFrame for manipulation

### Clarifications & Updates

**Q: How many years of data?**
- **A:** Scrape historical data from every year available (2018, 2019, 2021-2025)
- Note: 2020 is missing (likely due to COVID-19)

**Q: How to handle multiple years?**
- **A:** Years are controlled via URL parameter `&y=YEAR`
- Example: `https://mountdiablochallenge.itsyourrace.com/Results.aspx?id=11068&y=2024`

**Technical Note:**
- The site uses ASP.NET with ViewState for pagination
- Must maintain session and extract ViewState for "Next" page navigation
- Each year has different number of finishers (e.g., 2024: 768, 2025: 825)

---

## Phase 2: Data Storage in SQLite

### Objective
Create a local database to store scraped race results for persistent storage and easy querying.

### Implementation

**1. Database and Table Creation:**
- Use Python's built-in `sqlite3` library
- Create SQLite database file: `data/diablo_challenge.db`
- Define table schema with appropriate data types:
  - TEXT for names, teams, locations
  - INTEGER for age, place
  - REAL for chip_time_seconds
  - DATE for race_date

**2. Data Insertion:**
- Connect to SQLite database from Python script
- Iterate through scraped data (from Pandas DataFrame)
- Insert each record into the table
- Implement smart updating: replace existing year data when re-scraping

**Database Schema:**

```sql
CREATE TABLE race_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    race_date DATE,
    place INTEGER,
    name TEXT,
    team TEXT,
    city_state TEXT,
    gender TEXT,
    gender_place TEXT,
    age INTEGER,
    age_place TEXT,
    chip_time_str TEXT,
    chip_time_seconds REAL,
    pace TEXT,
    start_time TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    race_date DATE,
    timestamp TIMESTAMP,
    location TEXT,
    temperature_2m REAL,
    windspeed_10m REAL,
    winddirection_10m REAL,
    wind_gusts_10m REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Clarifications & Updates

**Smart Year Updates:**
- System checks if year exists before inserting
- `replace_existing=True` automatically replaces data for that year
- Prevents duplicates when re-scraping
- Dedicated `update_year.py` script for annual updates

---

## Phase 3: Weather Data Integration

### Objective
Obtain historical, location-specific weather data for each race day to correlate with race times.

### Implementation

**1. Weather API Selection:**
- **Chosen:** Open-Meteo Historical Weather API
- **Why:** Free for non-commercial use, no API key required, detailed historical data

**2. Geographic Coordinates:**

**Start Location (approximate):**
- Latitude: 37.885
- Longitude: -122.059

**Summit Location (approximate):**
- Latitude: 37.881
- Longitude: -121.914

**3. API Calls:**
- For each race year, construct API call to Open-Meteo
- Specify: date, coordinates, desired weather variables
- Request hourly data for both start and summit coordinates

**Weather Variables:**
- `temperature_2m` - Temperature at 2 meters
- `windspeed_10m` - **Wind speed at 10 meters (PRIMARY FOCUS)**
- `winddirection_10m` - Wind direction
- `wind_gusts_10m` - Wind gusts (max)

**4. Store Weather Data:**
- Create separate table in SQLite database
- Link weather data to race results by year
- Store data for both start and summit locations

### Clarifications & Updates

**Q: What time window for weather data?**
- **A:** Race start time (7-8 AM), extending maximum 3 hours later (until ~11 AM)
- Break into as frequent intervals as possible (hourly from Open-Meteo)

**Q: Which weather variables are most important?**
- **A:** **Wind speed is BY FAR the most important weather aspect!**
- Temperature and wind direction are secondary
- Focus heavily on wind speed, average, max, and gusts

**Implementation Details:**
- Fetch hourly data from 7 AM to 11 AM (race window)
- Get data for BOTH start and summit to show elevation-dependent conditions
- Wind speeds typically higher at summit due to elevation

---

## Phase 4: Data Analysis and Visualization

### Objective
Analyze the combined race and weather data and create specified charts.

### Implementation

**1. Data Analysis with Pandas:**
- Load race and weather data from SQLite into Pandas DataFrames
- For each year, calculate statistics for "Chip Time":
  - Mean
  - Median
  - 25th Percentile
  - 75th Percentile
- Convert chip time from string (HH:MM:SS) to total seconds for calculations

**2. Data Visualization:**
- Use Matplotlib and Seaborn for plotting
- X-axis: Year
- Y-axis: Chip Time (converted to minutes for readability)

**Charts to Generate:**

1. **Yearly Time Distribution**
   - Plot mean, median, 25th/75th percentiles for each year
   - Use line plot to connect same statistic across years
   - Fill area between percentiles (IQR)

2. **Performance vs Wind Conditions**
   - Primary Y-axis: Median chip time
   - Secondary Y-axis: Wind speed (average and max gusts)
   - Overlay to show correlation

3. **Weather Comparison: Start vs Summit**
   - Side-by-side comparison of wind speeds
   - Show both average and maximum gusts
   - Demonstrate elevation impact on conditions

**3. Correlation Analysis:**
- Calculate correlation between median times and wind speed
- Identify years with extreme weather conditions
- Analyze impact on race performance

### Clarifications & Updates

**Q: What should the final deliverable be?**
- **A:** Both automated script AND interactive notebooks

**Deliverables:**
1. **Automated Pipeline** (`main.py`):
   - One command to run everything
   - Scrape → Fetch Weather → Analyze → Visualize

2. **Interactive Notebooks:**
   - `01_data_collection.ipynb` - Data scraping demo
   - `02_analysis.ipynb` - Statistical analysis
   - `03_visualization.ipynb` - Custom visualizations

3. **Publication-Quality Charts:**
   - 300 DPI PNG files
   - Professional styling
   - Ready for presentations/reports

---

## Regarding aura.build Design

### Question
Should the aura.build design be uploaded first or second?

### Answer
**Upload it SECOND.**

### Rationale
The aura.build design is for the visualization phase. The logical workflow is:

1. **Execute the Code:** Build data pipeline (scrape → store → analyze)
2. **Generate the Data:** Get clean, calculated data (yearly statistics, weather info)
3. **Apply the Design:** Use aura.build template in visualization step (Phase 4)

**Focus on getting the data pipeline built first. The design is the final step to make results look good.**

### Clarifications & Updates

**Q: What is aura.build design?**
- **A:** It's a combination of:
  - Chart styling template
  - Dashboard layout theme
  - Base landing page template
- Focuses on design and aesthetics rather than content
- Will be applied AFTER data collection and analysis are complete

---

## Project Timeline & Execution

### Completed Steps
✅ Phase 1: Web scraping implementation (all years 2018-2025)
✅ Phase 2: SQLite database with smart year updating
✅ Phase 3: Weather data integration (Open-Meteo API)
✅ Phase 4: Analysis and visualization (automated + notebooks)

### Key Features Implemented
- Automated full pipeline (`python3 main.py`)
- Year-specific updates (`python3 update_year.py 2026`)
- Smart duplicate prevention
- Comprehensive documentation
- Publication-quality charts

### Next Steps
1. ✅ Complete initial data collection (run `python3 main.py`)
2. ⏳ Apply aura.build design template to visualizations
3. ⏳ Create interactive dashboard
4. ⏳ Generate final reports and presentations

---

## Technical Notes

### Critical Bug Fix
**Issue:** Scraper was always returning 2025 data regardless of year requested
**Root Cause:** Year is controlled by URL parameter `&y=YEAR`, not form submission
**Solution:** Append `&y={year}` to base URL before scraping

### Performance Considerations
- Full pipeline (all years): ~5-10 minutes
- Single year update: ~30 seconds
- Database queries: milliseconds
- Chart generation: ~1-2 seconds

### Best Practices
- Rate limiting: 0.5-1 second delays between requests
- Session management: Maintain cookies for ASP.NET ViewState
- Error handling: Robust logging and retry logic
- Data validation: Verify counts match website totals

---

## Maintenance

### Annual Race Updates
When a new race occurs (e.g., 2026):

```bash
python3 update_year.py 2026
```

This will:
- Scrape only that year's results (~30 seconds)
- Fetch weather for that date
- Add to database without touching historical data
- Regenerate all charts with updated trends

**DO NOT** run full `python3 main.py` for updates - it re-scrapes everything!

---

## Success Metrics

- ✅ All available years scraped (2018, 2019, 2021-2025)
- ✅ Correct result counts per year (e.g., 2024: 768, 2025: 825)
- ✅ Weather data with hourly granularity during race window
- ✅ Statistical analysis (mean, median, percentiles)
- ✅ Multi-year trend visualizations
- ✅ Wind correlation analysis

---

*This plan was developed and executed in October 2025, with comprehensive implementation completing all phases successfully.*
