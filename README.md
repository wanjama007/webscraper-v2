# Python Web Scraper

A beginner-friendly web scraper with a small desktop interface and a configurable command-line mode. Use it to practice collecting information from websites that allow scraping.

## Features

- Desktop interface for collecting headings, paragraphs, links, images, tables, and email addresses
- Command-line mode for extracting specific fields with CSS selectors
- Pagination, request delays, timeouts, and retries
- Output as CSV, JSON, or SQLite
- Logging and a JSON summary report for command-line runs

## Requirements

- Python 3.10 or newer
- The packages listed in `requirements.txt`

## Install

Open PowerShell in this project folder, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If you do not want to activate a virtual environment, install the packages with `py -m pip install -r requirements.txt` and use `py` in the run commands below.

## Simple mode: desktop app

```powershell
python app.py
```

Enter a website, choose what to collect, select how many pages to visit, and choose an output format. Results are saved in the `output` folder. The simple mode automatically collects common page content; it does not create dedicated product columns such as price or stock status.

## Advanced mode: choose fields with CSS selectors

Run the included example configuration:

```powershell
python main.py --config example_config.json
```

Or provide the settings directly. This example collects quote text and author names, follows pagination, and writes JSON:

```powershell
python main.py --url https://quotes.toscrape.com --item ".quote" --field text=.text --field author=.author --next "li.next a" --format json
```

In the command above, `--item` selects each repeated record, and each `--field` defines an output column and a selector within that record. For example, `--field author=.author` creates an `author` column from the `.author` element.

The advanced mode supports `csv`, `json`, and `sqlite` output formats. Use `--max-pages` to set the page limit and `--out` to choose the output directory. Run `python main.py --help` to see all command-line options.

## Output and logs

- Scraped files are written to `output/` by default.
- Logs and command-line run reports are written to `logs/`.
- These generated folders are excluded from Git by `.gitignore`.

## Scrape responsibly

Only scrape websites when you have permission. Check the website's terms and `robots.txt`, keep request delays reasonable, and avoid collecting private or sensitive information. The advanced mode respects `robots.txt` by default.
