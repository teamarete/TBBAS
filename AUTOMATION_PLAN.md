# TBBAS Automation Plan - New Workflow

## Overview
This document outlines the new automated workflow for TBBAS rankings updates.

## Schedule

### Daily: Box Score Scraping (6 AM CST)
**What:** Scrape box scores from MaxPreps for the previous day's games
**When:** Every day at 6 AM CST
**Script:** `scrape_maxpreps_daily.py`
**Action:** Import new games into database

**MaxPreps URL Pattern:**
```
https://www.maxpreps.com/tx/basketball/scores/?date=MM/DD/YYYY
```

Examples:
- Monday, Dec 15: `https://www.maxpreps.com/tx/basketball/scores/?date=12/15/2025`
- Tuesday, Dec 16: `https://www.maxpreps.com/tx/basketball/scores/?date=12/16/2025`

### Weekly: Rankings Scraping (Monday 2 PM CST)
**What:** Scrape latest rankings from TABC and MaxPreps
**When:** Every Monday at 2 PM CST
**Script:** `scrape_weekly_rankings.py`
**Action:** Save raw ranking data for processing

**TABC URLs:**
- UIL: https://tabchoops.org/uil-boys-rankings/
- Private: https://tabchoops.org/private-school-boys-rankings/

**MaxPreps Rankings URLs:**

UIL:
- 6A: https://www.maxpreps.com/tx/basketball/25-26/division/division-6a/rankings/1/?statedivisionid=f30bc9a3-067d-42e3-9954-2d6496693e1a
- 5A: https://www.maxpreps.com/tx/basketball/25-26/division/division-5a/rankings/1/?statedivisionid=2a0df19a-ccb6-42ea-9f00-029bc1dfe1a6
- 4A: https://www.maxpreps.com/tx/basketball/25-26/division/division-4a/rankings/1/?statedivisionid=eb02b34b-b4b1-4cb7-aef3-cb79b153adec
- 3A: https://www.maxpreps.com/tx/basketball/25-26/division/division-3a/rankings/1/?statedivisionid=5d46b71b-854c-4f97-9b92-6e46b25e1961
- 2A: https://www.maxpreps.com/tx/basketball/25-26/division/division-2a/rankings/1/?statedivisionid=00e4af8f-674c-482f-9f1e-a5ee9e879d16
- 1A: https://www.maxpreps.com/tx/basketball/25-26/division/division-1a/rankings/1/?statedivisionid=ddc5fa20-ecdf-4e62-aa33-cfc02452bed9

TAPPS:
- 6A: https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-6a/rankings/1/?sectiondivisionid=1affa478-5b94-4e17-b8ca-dd572d9b1e02
- 5A: https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-5a/rankings/1/?sectiondivisionid=c1741f02-d83d-4726-bc6c-00f7ebf3b5c9
- 4A: https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-4a/rankings/1/?sectiondivisionid=22e9cece-a43d-46c8-8475-cf93ae55f46c
- 3A: https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-3a/rankings/1/?sectiondivisionid=f966dbd3-90d6-42da-b7d1-1cc017e3b580
- 2A: https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-2a/rankings/1/?sectiondivisionid=a8fd3dd2-936d-40b9-9ee8-8fbbcb096d11
- 1A: https://www.maxpreps.com/tx/tapps/basketball/25-26/division/division-tapps-1a/rankings/1/?sectiondivisionid=48b38de3-57bc-4d34-b578-25adac65421f

SPC:
- SPC 4A: https://www.maxpreps.com/tx/basketball/25-26/division/division-southwest-prep/rankings/1/?statedivisionid=a4d800c8-6fa7-4b2f-b520-f4c19c7da173

### Weekly: Rankings Update (Monday 4 PM CST)
**What:** Calculate and publish new rankings to website
**When:** Every Monday at 4 PM CST
**Script:** `update_weekly_rankings.py` (to be created)
**Action:**
1. Load TABC + MaxPreps rankings from 2 PM scrape
2. Calculate efficiency rankings from box score database
3. Calculate stats from database (PPG, Opp PPG, etc.)
4. Compute weighted average: **33% Calculated + 33% TABC + 33% MaxPreps**
5. Update `rankings.json` and `rankings.json.master`
6. Trigger website update

## Ranking Calculation Formula

### NEW Formula (3-way weighted average):
- **33% Calculated Rankings** - Efficiency ratings from game box scores
- **33% TABC** - Texas Association of Basketball Coaches rankings
- **33% MaxPreps** - Daily updated rankings from MaxPreps

### Removed:
- ❌ GASO - No longer used in calculations

### Data Sources:
- **Box Scores**: Scraped daily from MaxPreps at 6 AM CST
- **Calculated Rankings**: Computed from box score efficiency ratings
- **TABC Rankings**: Scraped weekly (Mondays 2 PM CST) from tabchoops.org
- **MaxPreps Rankings**: Scraped weekly (Mondays 2 PM CST) from maxpreps.com
- **Stats** (PPG, Opp PPG, W-L): From database box scores + TABC records

## Implementation Status

### ✅ Completed
- Created `scrape_maxpreps_daily.py` with full Selenium-based parser
- Created `scrape_weekly_rankings.py` with complete TABC and MaxPreps parsers
- Documented all URLs and schedule
- Updated automation plan
- **MaxPreps box score scraping fully implemented**
  - Uses Selenium WebDriver to handle JavaScript-rendered content
  - Parses team names and scores from daily scores page
  - Imports games directly to database
  - Handles duplicate detection
- **TABC rankings scraping fully implemented**
  - Parses UIL (6A-1A) and Private (TAPPS 6A-1A) rankings
  - Extracts team names, ranks, and win-loss records
  - Handles multiple text patterns
- **MaxPreps rankings scraping fully implemented**
  - Uses Selenium for JavaScript-rendered rankings pages
  - Supports table and list-based ranking formats
  - Extracts team names, ranks, and records from all 13 divisions
  - Handles UIL, TAPPS, and SPC classifications

### ⚠️ TODO - Critical
1. ~~**Implement MaxPreps box score parser** in `scrape_maxpreps_daily.py`~~ ✅ DONE
   - ~~Analyze MaxPreps HTML structure~~
   - ~~Extract game data (teams, scores, stats)~~
   - ~~Handle different page layouts~~

2. ~~**Implement MaxPreps rankings parser** in `scrape_weekly_rankings.py`~~ ✅ DONE
   - ~~Parse ranking tables from MaxPreps~~
   - ~~Extract team names, ranks, records~~

3. ~~**Implement TABC rankings parser** in `scrape_weekly_rankings.py`~~ ✅ DONE
   - ~~Reuse existing TABC scraping logic~~
   - ~~Parse UIL and Private rankings~~
   - ~~Extracts team names, ranks, and win-loss records from TABC~~

4. ~~**Create `update_weekly_rankings.py`**~~ ✅ DONE
   - ~~Load scraped TABC + MaxPreps data~~
   - ~~Calculate 33/33/33 weighted average~~
   - ~~Update stats from database~~
   - ~~Save to rankings.json~~
   - Implements efficiency-based calculated rankings from box scores
   - Merges all three ranking sources with equal weighting
   - Updates team stats (PPG, Opp PPG, W-L) from database and TABC

5. ~~**Update scheduler.py**~~ ✅ DONE
   - ~~Add daily 6 AM job for box score scraping~~
   - ~~Update Monday 2 PM job for rankings scraping~~
   - ~~Add Monday 4 PM job for rankings calculation~~
   - ~~Remove GASO scraping calls and old merge_rankings function~~
   - Uses subprocess to call new automation scripts
   - Weekly jobs remain disabled (manual updates only)

6. **Remove GASO dependencies**
   - Update `ranking_calculator.py` to remove GASO weight
   - Remove GASO scraper imports where not needed

## Testing Plan

1. **Test MaxPreps box score scraping**
   - Run manually: `python scrape_maxpreps_daily.py 12/15/2025`
   - Verify games imported to database

2. **Test weekly rankings scraping**
   - Run manually: `python scrape_weekly_rankings.py`
   - Verify JSON files created with rankings

3. **Test rankings calculation**
   - Run manually: `python update_weekly_rankings.py`
   - Verify 50/50 TABC+MaxPreps weights
   - Verify stats populated from database

4. **Test scheduler**
   - Deploy to Railway
   - Monitor logs for scheduled executions
   - Verify timing (6 AM, 2 PM, 4 PM CST)

## Deployment Notes

- Scheduler runs in Railway web process (single process architecture)
- Times are in UTC, convert CST → UTC (+6 hours)
  - 6 AM CST = 12:00 PM UTC
  - 2 PM CST = 8:00 PM UTC
  - 4 PM CST = 10:00 PM UTC
- Automatic updates now disabled per user request (manual trigger only)
- Need to re-enable with new schedule after testing

## Files Modified

- `scrape_maxpreps_daily.py` - NEW
- `scrape_weekly_rankings.py` - NEW
- `update_weekly_rankings.py` - TO CREATE
- `scheduler.py` - TO UPDATE
- `ranking_calculator.py` - TO UPDATE (remove GASO)
- `AUTOMATION_PLAN.md` - THIS FILE

## Next Steps

1. Implement HTML parsers for MaxPreps
2. Create rankings update script
3. Update scheduler with new jobs
4. Test end-to-end workflow
5. Deploy to Railway
6. Monitor first week's automated updates
