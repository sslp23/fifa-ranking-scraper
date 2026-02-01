# FIFA World Rankings Scraper

This project contains a Python script to scrape historical FIFA world rankings from [Transfermarkt](https://www.transfermarkt.com). The script is designed to be efficient by only fetching and saving data for ranking dates that are not already present in the local data file.

## Features

- Scrapes historical FIFA rankings from Transfermarkt.
- Automatically discovers all available ranking dates.
- Handles pagination to retrieve all teams for a given date.
- Checks `data/resulting_data.csv` to avoid re-scraping data that has already been collected.
- Appends new data incrementally to the CSV file.
- Stores the collected data in a clean, structured CSV format.

## Automation

This scraper is set up to run automatically on the 1st and 15th of every month via GitHub Actions. It will fetch the latest FIFA rankings and update the `data/resulting_data.csv` file directly in the repository. You can also manually trigger the workflow from the 'Actions' tab in your GitHub repository.

## Requirements

To run this script, you'll need Python 3. The required libraries are listed in `requirements.txt`.

You can install them using pip:

```bash
pip install -r requirements.txt
```

## Usage

1.  Clone this repository or download the `ranking_scraper.py` file.
2.  Install the required libraries (see Requirements section).
3.  Run the script from your terminal:

```bash
python ranking_scraper.py
```

The script will first check for all available ranking dates on Transfermarkt. Then, it will compare them against the dates already saved in `data/resulting_data.csv`. If it finds any new dates, it will begin scraping them, showing a progress bar as it works. If all dates are already up-to-date, it will print a message and exit.

## Output Data

The scraped data is saved in `data/resulting_data.csv`. The file will contain the following columns:

| Column              | Description                                                  |
| ------------------- | ------------------------------------------------------------ |
| `rank`              | The team's FIFA ranking on that date.                        |
| `nation`            | The short name of the country.                               |
| `confederation`     | The football confederation the nation belongs to (e.g., UEFA, CONMEBOL). |
| `points`            | The number of ranking points.                                |
| `previous_position` | The team's rank in the previously published list.            |
| `trend`             | The ranking trend (`up`, `down`, or `stable`).               |
| `nation_url`        | The relative URL to the team's page on Transfermarkt.        |
| `flag_url`          | The URL of the nation's flag image.                          |
| `nation_full_name`  | The full name of the nation.                                 |
| `rank_date`         | The date the ranking was published (in `YYYY-MM-DD` format). |

---

_This `README.md` was generated with the help of Gemini._
