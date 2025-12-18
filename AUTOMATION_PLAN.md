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
2. Calculate stats from database (PPG, Opp PPG, etc.)
3. Compute weighted average: **50% TABC + 50% MaxPreps** (no more GASO)
4. Update `rankings.json` and `rankings.json.master`
5. Trigger website update

## Ranking Calculation Changes

### OLD Formula (4-way):
- 25% Calculated (from box scores)
- 25% TABC
- 25% MaxPreps
- 25% GASO

### NEW Formula (2-way):
- **50% TABC**
- **50% MaxPreps**
- ❌ GASO removed

Stats (PPG, Opp PPG, W-L) come from database box scores and TABC records.

## Implementation Status

### ✅ Completed
- Created `scrape_maxpreps_daily.py` skeleton
- Created `scrape_weekly_rankings.py` skeleton
- Documented all URLs and schedule
- Updated automation plan

### ⚠️ TODO - Critical
1. **Implement MaxPreps box score parser** in `scrape_maxpreps_daily.py`
   - Analyze MaxPreps HTML structure
   - Extract game data (teams, scores, stats)
   - Handle different page layouts

2. **Implement MaxPreps rankings parser** in `scrape_weekly_rankings.py`
   - Parse ranking tables from MaxPreps
   - Extract team names, ranks, records

3. **Implement TABC rankings parser** in `scrape_weekly_rankings.py`
   - Reuse existing TABC scraping logic
   - Parse UIL and Private rankings

4. **Create `update_weekly_rankings.py`**
   - Load scraped TABC + MaxPreps data
   - Calculate 50/50 weighted average
   - Update stats from database
   - Save to rankings.json

5. **Update scheduler.py**
   - Add daily 6 AM job for box score scraping
   - Update Monday 2 PM job for rankings scraping
   - Add Monday 4 PM job for rankings calculation
   - Remove GASO scraping calls

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
