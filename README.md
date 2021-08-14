## Python web scraper for tech position keywords on Finn.no

### About the project

- Scrapes all ads found on site [https://www.finn.no/job/fulltime/search.html](https://www.finn.no/job/fulltime/search.html) with query params set to filter on IT-developing positions.
- Extracts keywords from ads, and attempts to generalize them by formatting them into a standard way for easier grouping (lowercase, no-white-space in start and end of phrase)
- Group keywords by number of appearences and sort ascending, before writing to a file `/output/results.txt`

### TODO

- Do job descripion string analysis, looking for "wanted keywords" (e.g. Java, C#, Python, AWS, Azure, Salesforce, ...) and group by these. As there is a lot of various keywords in the ads, this might give a cleaner representation of techology occurences.
- Filter out unwanted results (e.g. redundant and uninteresting keywords)
- Result formatting: Save as .csv and visualize the results.

### Required dependencies and packages

Dependencies
* python 3.8

Python packages
* requests 2.24.0
* asyncio 3.4.3
* aiohttp 3.7.4

Install required packages using:
```
pip install requests, asyncio, aiohttp
```

### How to run

Run program with
```
python main.py
```
