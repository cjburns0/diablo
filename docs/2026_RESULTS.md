# 2026 results import

The October 4, 2026 Mount Diablo Challenge main race has **828 official finishers**. All 34 result pages were collected on October 22, 2026 and reconciled against the published finisher count.

- Source: [ITS YOUR RACE, 2026 results](https://mountdiablochallenge.itsyourrace.com/Results.aspx?id=11068&y=2026)
- Category: **Road, Mtn, Unicycle, or Elliptical Bike**, matching the existing dashboard. E-assisted bikes and tandems are separate source categories and are not included.
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

**Weather:** [`data/imports/2026-weather.json`](../data/imports/2026-weather.json) preserves the two Open-Meteo archive responses, exact request URLs, and ten imported hourly records. They cover 07:00–11:00 America/Los_Angeles at the existing configured start and summit coordinates, using mph and Fahrenheit. These are modeled historical weather estimates. The 2026 update preserves the existing methodology; correcting the start coordinate, time window and wind-direction averaging across every year is a separate audit recommendation.

**Integration:** All finishers are in SQLite and contribute to the annual statistics. The regenerated dashboard includes eight race years, 5,516 total finishers, and 1,076 rider profiles with at least two results. Rider lookup continues to include repeat participants only. The chart extends to 110 minutes when 2026 is selected so its full IQR remains within the plotting area. Removing 2026 restores the previous 100-minute scale.

**Validation performed:**

- Reparsed all 34 saved source pages; selected year, race date and every extracted row match the CSV input. The final page has three finishers and no next-page link.
- Verified positive chip times, unique published places, the documented source gap, and the advertised count of 828.
- Checked SQLite integrity and exact equality of every pre-2026 database row, including all weather rows.
- Verified all prior annual statistics, weather summaries and existing rider performances remain unchanged.
- Recalculated the new mean, median and counts; serialized the entire dashboard with strict JSON validation (`allow_nan=False`).
- Regenerated dashboard data from the updated database and matched the committed export apart from its generation timestamp; generated all three Python analysis charts.
- Browser-checked the full range, the 2026-only filter, the historical range's unchanged 100-minute axis, and Nathan Martin's 2026 winner result in rider history. Checked syntax for all 15 JavaScript modules.

To refresh the year using the existing pipeline:

```sh
python3 update_year.py 2026
python3 dashboard_data.py
```

The checked-in source snapshots document this import. The existing update script does not refresh those snapshots or verify scrape completeness automatically; recheck the source count and update the snapshots when refreshing corrected results.
