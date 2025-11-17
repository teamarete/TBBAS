# MaxPreps Score Scraping Guide

## Overview

The TBBAS project now has a fully functional MaxPreps scraper that:
- Uses Selenium to handle JavaScript-rendered pages
- Scrapes completed game scores from MaxPreps
- Supports configurable date sequences for daily updates
- Automatically normalizes team names

## Recent Updates

### Fixed Issues
1. **JavaScript Rendering**: MaxPreps loads games dynamically via JavaScript, so the scraper now uses Selenium with headless Chrome
2. **HTML Structure**: Updated parsing to match MaxPreps' actual structure:
   - Team names are in `<div class="name">`
   - Scores are in `<div class="score">`
   - Completed games have `data-contest-state="boxscore"`

### Files Modified
- [box_score_scraper.py](box_score_scraper.py): Updated `scrape_daily_scores()` method to use Selenium
- [scheduler.py](scheduler.py): Added `SCRAPE_DATES` configuration for custom date sequences

## Configuration

### Setting Up Daily Score Updates

To configure which dates to scrape, edit [scheduler.py](scheduler.py):

```python
# MaxPreps scraping configuration
# Format: list of date strings in MM/DD/YYYY format
SCRAPE_DATES = ["11/14/2025", "11/15/2025"]  # Specific dates
# OR
SCRAPE_DATES = []  # Empty = scrape yesterday only (default)
```

### How It Works

1. **Daily Collection** (6:00 AM every day):
   - If `SCRAPE_DATES` is **empty**: Scrapes yesterday's games
   - If `SCRAPE_DATES` has **dates**: Scrapes those specific dates

2. **Weekly Rankings** (6:00 AM every Monday):
   - Scrapes MaxPreps rankings
   - Calculates rankings from collected scores
   - Scrapes TABC rankings as backup
   - Merges all sources

### Date Sequence for Daily Updates

To scrape a sequence of dates every day (e.g., always scrape the last 2 days):

**Option 1: Static dates** (manually update)
```python
SCRAPE_DATES = ["11/14/2025", "11/15/2025"]
```

**Option 2: Dynamic dates** (recommended for ongoing scraping)

Modify the `collect_box_scores()` function in [scheduler.py](scheduler.py:46-90):

```python
def collect_box_scores():
    """Collect box scores from various sources daily"""
    now = datetime.now()

    # ... season checks ...

    collector = BoxScoreCollector(app=_app)

    # Dynamic date configuration - scrape last N days
    DAYS_TO_SCRAPE = 2  # Number of days to go back
    target_dates = [
        (now - timedelta(days=i)).strftime('%m/%d/%Y')
        for i in range(1, DAYS_TO_SCRAPE + 1)
    ]

    logger.info(f"Scraping dates: {', '.join(target_dates)}")
    games = collector.collect_daily_box_scores(target_dates=target_dates)
    # ...
```

## Testing

### Test the Scraper

Run the standalone test script:

```bash
python test_maxpreps_standalone.py
```

This will test the scraper with the dates `11/14/2025` and `11/15/2025` and show you the games found.

### Verify HTML Structure

If you need to debug the HTML parsing:

```bash
python debug_maxpreps_html.py
```

This saves the page HTML to `maxpreps_debug.html` and shows the structure.

### Inspect Specific Date

To test a specific date:

```bash
python inspect_completed_game.py
```

Edit the file to change the date.

## Example Usage

### Scrape Specific Dates Manually

```python
from box_score_scraper import MaxPrepsBoxScoreScraper
from datetime import datetime

scraper = MaxPrepsBoxScoreScraper(use_selenium=True)

# Scrape specific date
games = scraper.scrape_daily_scores(datetime(2025, 11, 14))
print(f"Found {len(games)} games")

for game in games[:5]:  # Show first 5
    print(f"{game['team1_name']} {game['team1_score']} vs "
          f"{game['team2_name']} {game['team2_score']}")
```

### Scrape Multiple Dates

```python
from box_score_scraper import BoxScoreCollector

collector = BoxScoreCollector(app=None)  # No Flask app needed for testing

# Scrape multiple dates
dates = ["11/14/2025", "11/15/2025", "11/16/2025"]
games = collector.collect_daily_box_scores(target_dates=dates)

print(f"Total games: {len(games)}")
```

## Season Configuration

The scraper only runs during the configured season:

```python
# In scheduler.py
START_DATE = datetime(2025, 11, 11)  # November 11, 2025
END_DATE = datetime(2026, 3, 9)      # March 9, 2026
```

Outside this window, the scraper will log a message and skip execution.

## Dependencies

Required packages (already in [requirements.txt](requirements.txt)):
- `selenium>=4.15.0` - Browser automation
- `webdriver-manager>=4.0.0` - Automatic ChromeDriver management
- `beautifulsoup4>=4.12.0` - HTML parsing
- `requests>=2.31.0` - HTTP requests

## Troubleshooting

### No Games Found

1. **Check the date format**: Must be `MM/DD/YYYY`
2. **Verify the date has games**: Visit `https://www.maxpreps.com/tx/basketball/scores/?date=MM/DD/YYYY`
3. **Check contest state**: Only games with `data-contest-state="boxscore"` are scraped (completed games)

### ChromeDriver Issues

The scraper uses `webdriver-manager` to automatically download and manage ChromeDriver. If you have issues:

```bash
# Clear the driver cache
rm -rf ~/.wdm
```

### Selenium Timeout

If pages load slowly, increase the timeout in [box_score_scraper.py](box_score_scraper.py:150-155):

```python
WebDriverWait(driver, 20).until(  # Increase from 10 to 20 seconds
    EC.presence_of_element_located((By.CLASS_NAME, "contest-box-item"))
)
```

## Performance Notes

- **Selenium is slower** than plain requests (5-10 seconds per date)
- Each date requires a separate page load
- Scraping 581 games (one day) takes ~10 seconds
- Daily scraping of 2-3 days should complete in <30 seconds

## Email Notifications

The scheduler sends email notifications for:
- **Daily collection success**: Game count by source
- **Daily collection errors**: Full error traceback
- **Weekly rankings update**: Team counts by classification

Configure email settings in your environment variables.

---

**Last Updated**: November 17, 2025
**Tested With**: 11/14/2025 (581 games found), 11/15/2025
