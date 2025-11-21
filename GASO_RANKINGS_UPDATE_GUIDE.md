# GASO Rankings Update Guide

## Overview

GASO (Great American Shootout) rankings are manually integrated into the TBBAS system. When new GASO rankings are published, follow this guide to update them.

## Current Status

✅ **GASO Pre-Season Rankings Loaded**
- 6A: 25 teams
- 5A: 25 teams
- 4A: 25 teams
- 3A: 10 teams
- 2A: 10 teams
- 1A: 10 teams
- TAPPS/SPC: 25 teams combined

**Total**: 130 teams ranked

## How to Update GASO Rankings

### Step 1: Edit the GASO Scraper File

Open the file:
```
gaso_scraper.py
```

### Step 2: Update Rankings in the `__init__` Method

Find the `__init__` method (around line 20) and update the rankings dictionaries:

#### For UIL Rankings:

```python
self.gaso_preseason_rankings = {
    # Class 6A (Top 25)
    'AAAAAA': [
        'Team Name 1',  # Rank 1
        'Team Name 2',  # Rank 2
        ...
    ],
    # Class 5A (Top 25)
    'AAAAA': [
        ...
    ],
    # ... etc
}
```

#### For TAPPS/SPC Rankings:

```python
self.gaso_tapps_rankings = [
    'Team Name 1',  # Rank 1
    'Team Name 2',  # Rank 2
    ...
]
```

### Step 3: Save the File

After making your updates, save [gaso_scraper.py](gaso_scraper.py).

### Step 4: Verify the Update

Test the updated rankings:

```bash
python gaso_scraper.py
```

You should see output confirming the rankings are loaded.

### Step 5: Rankings Will Auto-Update

The next Monday morning (6:00 AM), the weekly rankings update will automatically:
1. Load your updated GASO rankings
2. Merge with calculated rankings, MaxPreps, and TABC
3. Update all 1,304 schools in the system

## Example Update

### Before:
```python
'AAAAAA': [
    'Humble Atascocita',
    'San Antonio Brennan',
    ...
]
```

### After (with new rankings):
```python
'AAAAAA': [
    'New #1 Team',      # Updated
    'New #2 Team',      # Updated
    'Humble Atascocita', # Now #3
    ...
]
```

## Ranking Priority in System

When rankings are merged each Monday:

1. **Calculated KenPom-Style** (from actual game data) - HIGHEST PRIORITY
2. **GASO Rankings** (your manual updates) - SECOND
3. **MaxPreps Rankings** - THIRD
4. **TABC Rankings** - BACKUP

This means:
- If a team has played games, calculated efficiency rank is used
- If no calculated rank, GASO rank is used
- If not in GASO, MaxPreps rank is used
- If not in MaxPreps, TABC rank is used

## Important Notes

### Team Name Matching

Make sure team names in GASO match the names in your database:

**Good Examples**:
- ✅ "San Antonio Brennan" (matches database)
- ✅ "Katy Seven Lakes" (matches database)
- ✅ "Dallas Carter" (matches database)

**Problematic Examples**:
- ❌ "SA Brennan" (won't match "San Antonio Brennan")
- ❌ "Seven Lakes" (won't match "Katy Seven Lakes")
- ❌ "D. Carter" (won't match "Dallas Carter")

**Tip**: Check existing team names in [data/rankings.json](data/rankings.json) to ensure exact matches.

### TAPPS Classification Assignment

Currently, GASO provides combined TAPPS/SPC rankings (top 25) without specifying classification.

The system assigns all GASO TAPPS teams to `TAPPS_6A` since most top-ranked TAPPS teams are 6A.

If you know a team's specific classification, you can manually split them:

```python
# Instead of one combined list:
self.gaso_tapps_rankings = [...]

# You could create separate lists (future enhancement):
self.gaso_tapps_6a = [...]
self.gaso_tapps_5a = [...]
```

## Frequency of Updates

**GASO Rankings Schedule** (typical):
- Pre-season rankings (November)
- Week 3 rankings (December)
- Week 6 rankings (January)
- Week 9 rankings (February)
- Final rankings (March)

Update [gaso_scraper.py](gaso_scraper.py) each time new rankings are published.

## Troubleshooting

### Rankings Not Showing Up?

1. **Check file saved**: Make sure you saved gaso_scraper.py after edits
2. **Check syntax**: Run `python gaso_scraper.py` to test
3. **Check team names**: Ensure names match database exactly
4. **Check logs**: Look at scheduler logs on Monday morning

### Team Name Not Matching?

If a GASO-ranked team isn't showing up with a rank:

1. Check the exact spelling in [data/rankings.json](data/rankings.json)
2. Look for city prefixes (e.g., "San Antonio" vs "SA")
3. Update GASO team name to match database exactly

### Want to See Current Rankings?

```bash
python -c "from gaso_scraper import GASOScraper; s = GASOScraper(); d = s.scrape_all(); print(d['uil']['AAAAAA'][:5])"
```

This shows the top 5 6A teams in GASO rankings.

## Questions?

- **File to edit**: [gaso_scraper.py](gaso_scraper.py)
- **Lines to update**: Around line 22-175 in `__init__` method
- **When updates take effect**: Next Monday 6:00 AM
- **Priority**: GASO ranks are 2nd highest (after calculated efficiency)

---

**Your GASO rankings will be automatically integrated into the weekly update process!** 🏀
