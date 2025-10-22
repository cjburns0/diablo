# diablo
This project provides for analysis on the Diablo Challenge race in Lafayette, CA.

## Methodology
We scrape the Diablo Challenge race time finish results for all the details possible using a Python scraper and store it in a SQLite database. Given the results are fairly static and not updated more than once per year, we don't need a fully functioning backend database. Then we take a design template that I designed elsewhere to chart the data showing bottom 25th percentile, mean, median, and 75th percentile. The idea is to plot these by year on the x-axis and then be able to gauge analysis from different times per year. The key overlay here is that we pull in public weather data that is extremely detailed for the time of day as well as the specific location. Given we are on a Diablo Mountain, the general town weather will not work. We will need things like wind at the summit versus wind at the start to show how it impacted the times for that year. 
