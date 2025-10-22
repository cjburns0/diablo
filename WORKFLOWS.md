# Common Workflows

Quick reference for common tasks in the Mount Diablo Challenge analysis project.

## Initial Setup (First Time Only)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run full pipeline to collect all historical data
python3 main.py
```

This will take 5-10 minutes and scrape all years (2018, 2019, 2021-2025).

---

## Annual Update (When New Race Happens)

**Recommended approach** when a new race finishes:

```bash
python3 update_year.py 2026
```

This will:
- ✅ Scrape only 2026 results (~30 seconds)
- ✅ Fetch weather data for 2026
- ✅ Add to database without touching historical data
- ✅ Regenerate all charts with updated trends

**DO NOT** run the full `python3 main.py` for annual updates - it will re-scrape everything!

---

## Updating Existing Year (If Results Changed)

If you need to re-scrape a year (e.g., results were corrected):

```bash
python3 update_year.py 2025
```

By default, this will **replace** the existing 2025 data with fresh data.

To fail instead of replacing:
```bash
python3 update_year.py 2025 --no-replace
```

---

## Analyzing Existing Data

If you just want to regenerate charts from existing database:

```bash
python3 main.py --analyze-only
```

---

## Interactive Exploration

```bash
jupyter notebook notebooks/
```

Open:
- `01_data_collection.ipynb` - See how scraping works
- `02_analysis.ipynb` - Statistical analysis
- `03_visualization.ipynb` - Create custom charts

---

## Checking What's in the Database

```python
python3 -c "
import sys
sys.path.insert(0, 'src')
from database import DiabloDatabase

db = DiabloDatabase()
db.connect()

# Show years and counts
years = db.get_all_years()
print(f'Years: {years}')

for year in years:
    results = db.get_race_results_by_year(year)
    print(f'  {year}: {len(results)} results')

db.close()
"
```

---

## Advanced: Processing Specific Years

```bash
# Process multiple specific years
python3 main.py --years 2023 2024 2025

# Just scrape (don't fetch weather or analyze)
python3 main.py --scrape-only --years 2024

# Clear everything and start fresh
python3 main.py --force
```

---

## Troubleshooting

### "Year already exists in database"
Use `update_year.py` instead of `main.py` - it handles updates automatically.

### Charts look wrong
Regenerate them:
```bash
python3 main.py --analyze-only
```

### Want to start completely fresh
```bash
rm data/diablo_challenge.db
python3 main.py
```

---

## File Locations

- **Database**: `data/diablo_challenge.db`
- **Charts**: `output/charts/*.png`
- **Source code**: `src/*.py`
- **Notebooks**: `notebooks/*.ipynb`
