# 2026 results import

The October 4, 2026 Mount Diablo Challenge has **857 published timed finisher entries** across three separately ranked categories: 828 main-race, 20 e-assisted and 9 tandem entries. Results were collected on October 22, 2026 and reconciled against each category's published finisher count.

- Source: [ITS YOUR RACE, 2026 results](https://mountdiablochallenge.itsyourrace.com/Results.aspx?id=11068&y=2026)
- Main category: **Road, Mtn, Unicycle, or Elliptical Bike**, matching the existing historical charts. All 34 main-race result pages were collected. E-assisted bikes and tandems are stored and displayed separately, as described below.
- Readable source snapshot: [`data/imports/2026-results.csv`](../data/imports/2026-results.csv), containing every scraped result field, including the original chip-time strings and fractional seconds.
- CSV SHA-256: `55debe8abc963881b6e087956044eefe08a420dd60579babe3dd97d0eebefa4e`.
- The official places run from 1 to 829 with **236 absent** on source page 10. There are 828 unique published places and 828 unique names including bib numbers. Places are preserved exactly; the gap is not an omitted scrape row.

| Metric | 2026 |
| --- | --- |
| Finishers | 828 |
| Winner | Nathan Martin, 00:43:53.6 |
| Median, dashboard format | 80:31 |
| Mean, dashboard format | 87:06 |
| 25th percentile, dashboard format | 66:28 |
| 75th percentile, dashboard format | 100:29 |
| Last finisher | Ryan Ice, 03:23:55.9 |

The dashboard's existing time formatter truncates to whole seconds. The official summary rounds its average to 01:27:07; the underlying imported times retain their fractional seconds.

**Additional categories:** Each fits on one source page, with no next-page link. Original places, names including bib numbers, and fractional chip times are preserved. Tandem counts refer to the timing provider's individual entries, not a number of tandem teams or bicycles.

| Category | Timed finishers | Untimed entries | Fastest | Median, mm:ss |
| --- | --- | --- | --- | --- |
| [E-Assisted Bike](https://mountdiablochallenge.itsyourrace.com/Results.aspx?id=11068&y=2026&eid=141456) | 20 | 3 | Joe Gaidosh, 00:39:35.0 | 74:38 |
| [Tandem](https://mountdiablochallenge.itsyourrace.com/Results.aspx?id=11068&y=2026&eid=141457) | 9 | 0 | Mitchell Sains, 01:00:20.8 | 95:06 |

- [`2026-e-assisted-results.csv`](../data/imports/2026-e-assisted-results.csv) includes all 23 source entries. Ragnhild Lorentzen (#478), Diana Lowe (#481) and Markus Mayr (#524) have no published finish time; their rows remain in the snapshot, but are excluded from finisher tables and statistics. SHA-256: `422d05b29add42068d4f8e9fb125c1815e56b3d0dc651ba1c29d041d7e19d37c`.
- [`2026-tandem-results.csv`](../data/imports/2026-tandem-results.csv) includes all 9 source entries. SHA-256: `dba0cc049f96c6105f0159bffbed1843d283022a680985cc752e62a60b1a415b`.
- SQLite stores the category metadata in `additional_races` and 29 timed entries in `additional_race_results`. The JSON export's `additional_categories` contains both full result lists and independent summaries. They never enter the main `race_results` table, historical charts, KPI cards or repeat-rider comparisons.
- The dashboard has expandable tables for both categories, with official source links, original chip-time strings and an explanation of untimed entries. These tables follow the year filters; historical-only selections show an explicit unavailable-data message.

**Weather:** [`data/imports/2026-weather.json`](../data/imports/2026-weather.json) preserves the two Open-Meteo archive responses, exact request URLs, and ten imported hourly records. They cover 07:00–11:00 America/Los_Angeles at the existing configured start and summit coordinates, using mph and Fahrenheit. These are modeled historical weather estimates. The 2026 update preserves the existing methodology; correcting the start coordinate, time window and wind-direction averaging across every year is a separate audit recommendation.

**Main-race integration:** All 828 main-race finishers are in SQLite and contribute to the annual statistics. The main-race dashboard includes eight race years, 5,516 total finishers, and 1,076 rider profiles with at least two results. Rider lookup continues to include repeat main-race participants only. The chart extends to 110 minutes when 2026 is selected so its full IQR remains within the plotting area. Removing 2026 restores the previous 100-minute scale.

**Validation performed:**

- Reparsed all 34 saved source pages; selected year, race date and every extracted row match the CSV input. The final page has three finishers and no next-page link.
- Verified positive chip times, unique published places, the documented source gap, and the advertised count of 828.
- Checked SQLite integrity and exact equality of every pre-2026 database row, including all weather rows.
- Verified all prior annual statistics, weather summaries and existing rider performances remain unchanged.
- Recalculated the new mean, median and counts; serialized the entire dashboard with strict JSON validation (`allow_nan=False`).
- Regenerated dashboard data from the updated database and matched the committed export apart from its generation timestamp; generated all three Python analysis charts.
- Browser-checked the full range, the 2026-only filter, the historical range's unchanged 100-minute axis, and Nathan Martin's 2026 winner result in rider history.
- Verified the category import leaves every main-race database row, weather row and existing dashboard field exactly unchanged. Reconciled category CSV rows against SQLite and JSON.
- Added seven offline tests using extracted official HTML fixtures: category discovery, fractional times, untimed entries, pagination, wrong-year/category/date rejection, incomplete/duplicate/malformed rows, HTTP/repeated-page failure, idempotent imports and transactional rollback. Run with `python3 -m unittest discover -s tests -v`.
- Browser-checked all 29 category rows, keyboard expansion, historical-only empty state and filter reset. Checked syntax for all 16 JavaScript modules.

To refresh the year using the existing pipeline:

```sh
python3 update_year.py 2026
python3 dashboard_data.py
```

The annual updater discovers the year's e-assisted and tandem IDs and validates their date, category, published counts, unique places and pagination before writing data. Separate-category replacement is transactional. The main-race scraper still needs the broader completeness and atomic-update improvements identified in the audit, and results/weather/category writes are not one combined transaction. The checked-in source snapshots document this import and are not refreshed automatically; recheck the main-race source count and update snapshots when refreshing corrected results. Historical separate-category results have not been backfilled.
