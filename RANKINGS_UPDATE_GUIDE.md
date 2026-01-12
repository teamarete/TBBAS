# TBBAS Rankings Update Guide

Complete guide for updating rankings efficiently without wasted steps.

## Prerequisites

- Python 3.x installed
- Flask app configured
- Access to GitHub repository (teamarete/TBBAS)

## Step-by-Step Process

### 1. Scrape Latest Rankings

```bash
# Scrape TABC rankings
python3 scrape_tabc_simple.py

# Scrape MaxPreps rankings
python3 scrape_maxpreps_json.py
```

**Output files:**
- `tabc_rankings_scraped.json`
- `maxpreps_rankings_scraped.json`

### 2. Merge Rankings

```bash
python3 merge_all_rankings.py
```

**What it does:**
- Merges TABC + MaxPreps + calculated rankings
- Uses smart consensus algorithm (caps outliers at top 15)
- Creates `rankings_merged_preview.json`

### 3. Clean Duplicates

```bash
python3 clean_duplicate_teams.py
```

**What it does:**
- Removes duplicate teams (handles city prefixes: Katy, SA, Bmt, etc.)
- Strips location suffixes like (City, TX)
- Creates `rankings_cleaned_preview.json`

**Manual verification needed:**
- Check for any remaining duplicates
- Verify each classification has correct count (25 UIL, 10 TAPPS)

### 4. Clean Location Suffixes (if needed)

```bash
python3 clean_location_suffixes.py
```

**What it does:**
- Removes ALL location suffixes: (City, TX), (TX)
- Merges any duplicates with different naming
- Ensures consistent team names

### 5. Add Complete Game Statistics

```bash
python3 update_rankings_complete.py
```

**What it does:**
- Loads game data from normalized database (Team, Game, TeamGameStats)
- Calculates for each team:
  - Games played
  - Points per game (PPG)
  - Opponent PPG
  - Net rating (point differential)
  - Offensive efficiency (estimated)
  - Defensive efficiency (estimated)
- Matches team names using:
  1. Exact match
  2. Location suffix stripping
  3. Normalized names
  4. Search variations

**Coverage:** ~98.6% of teams (207/210)

### 6. Verify Data Quality

```bash
python3 << 'EOF'
import json

with open('data/rankings.json', 'r') as f:
    rankings = json.load(f)

# Check counts
for category in ['uil', 'private']:
    expected = 25 if category == 'uil' else 10
    for classification, teams in rankings[category].items():
        actual = len(teams)
        status = "✓" if actual == expected else "✗"
        print(f"{status} {category.upper()} {classification}: {actual}/{expected}")

# Check for location suffixes
suffix_count = 0
for category in ['uil', 'private']:
    for classification, teams in rankings[category].items():
        for team in teams:
            if '(TX)' in team['team_name'] or ', TX)' in team['team_name']:
                print(f"⚠ Suffix found: {team['team_name']}")
                suffix_count += 1

print(f"\nTotal with suffixes: {suffix_count}")

# Check stats coverage
with_games = sum(1 for c in ['uil', 'private']
                 for cl, teams in rankings[c].items()
                 for t in teams if t.get('games', 0) > 0)
print(f"\nTeams with game data: {with_games}/210 ({with_games/210*100:.1f}%)")
EOF
```

### 7. Test Flask App Locally

```bash
python3 << 'EOF'
from app_refactored import create_app

app = create_app()

with app.test_client() as client:
    # Test home page
    response = client.get('/')
    print(f"Home page: {response.status_code}")

    # Test classification page
    response = client.get('/rankings/AAAAAA')
    print(f"UIL 6A page: {response.status_code}")

    # Test API
    response = client.get('/api/rankings')
    print(f"API endpoint: {response.status_code}")

    # Test TAPPS API
    response = client.get('/api/rankings/TAPPS_6A')
    print(f"TAPPS API: {response.status_code}")

print("\n✓ All tests passed" if all([
    response.status_code == 200
]) else "✗ Tests failed")
EOF
```

### 8. Commit and Push

```bash
# Stage changes
git add data/rankings.json update_rankings_complete.py clean_location_suffixes.py app/blueprints/rankings.py

# Commit with descriptive message
git commit -m "Update rankings with complete game statistics

- Scraped latest TABC and MaxPreps rankings
- Merged with smart consensus algorithm
- Cleaned duplicates and location suffixes
- Added game statistics for 207/210 teams (98.6%)
- Verified all classifications have correct counts

Stats included: games, PPG, net rating, efficiency ratings

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to GitHub
git push origin main
```

### 9. Deploy to Server

**On the server hosting https://tbbas.teamarete.net/:**

```bash
# Navigate to project directory
cd /path/to/tbbas

# Pull latest code
git pull origin main

# Restart Flask application
sudo systemctl restart tbbas
# OR
sudo supervisorctl restart tbbas
# OR
pkill -f "python.*app_refactored.py" && nohup python3 app_refactored.py &
```

## Common Issues and Solutions

### Issue: Team names have duplicates

**Cause:** Same team with different naming (e.g., "LaMarque" vs "La Marque")

**Solution:**
```bash
# Run the duplicate cleaner
python3 clean_duplicate_teams.py

# If still issues, manually merge in the script or JSON
```

### Issue: Location suffixes causing duplicates

**Cause:** Team names like "Cypress Springs (Cypress, TX)" not matching "Cypress Springs"

**Solution:**
```bash
# Run location suffix cleaner
python3 clean_location_suffixes.py
```

### Issue: Teams missing game statistics

**Cause:** Team name in rankings doesn't match database name

**Solution:**
- Check `update_rankings_complete.py` output for "⚠ No stats found"
- Add name variations to `school_abbreviations.py`
- Or manually add mapping in the script

### Issue: Website not showing data after push

**Causes and solutions:**

1. **Server hasn't pulled latest code**
   ```bash
   # On server
   git pull origin main
   ```

2. **Flask app not restarted**
   ```bash
   sudo systemctl restart tbbas
   ```

3. **Wrong data key in rankings.py**
   - TAPPS data uses `'private'` key, not `'tapps'`
   - Check line 163 in app/blueprints/rankings.py

4. **Statistics hardcoded to None**
   - Lines 107-111 should use `team_data.get('net_rating')` not `None`

## File Reference

### Input Files
- `tabc_rankings_scraped.json` - TABC weekly rankings with records
- `maxpreps_rankings_scraped.json` - MaxPreps rankings

### Intermediate Files
- `rankings_merged_preview.json` - After merging sources
- `rankings_cleaned_preview.json` - After duplicate removal

### Output Files
- `data/rankings.json` - Final published rankings (used by website)

### Scripts
- `scrape_tabc_simple.py` - Scrape TABC rankings
- `scrape_maxpreps_json.py` - Scrape MaxPreps rankings
- `merge_all_rankings.py` - Merge all ranking sources
- `clean_duplicate_teams.py` - Remove duplicate teams
- `clean_location_suffixes.py` - Remove location suffixes
- `update_rankings_complete.py` - Add game statistics from database

### Application Files
- `app_refactored.py` - Main Flask application
- `app/blueprints/rankings.py` - Rankings routes and API
- `models_normalized.py` - Database models (Team, Game, TeamGameStats)

## Data Structure

### rankings.json Structure

```json
{
  "last_updated": "2026-01-12T16:12:43.951859",
  "source": "merged_tabc_maxpreps_calculated_cleaned",
  "complete_stats": true,
  "teams_with_stats": 207,
  "uil": {
    "AAAAAA": [
      {
        "rank": 1,
        "team_name": "Katy Seven Lakes",
        "wins": 24,
        "losses": 0,
        "record": "24-0",
        "classification": "AAAAAA",
        "tabc_rank": 1,
        "maxpreps_rank": 2,
        "calc_rank": null,
        "consensus_rank": 1.5,
        "net_rating": 14.0,
        "adj_offensive_eff": 108.9,
        "adj_defensive_eff": 88.9,
        "games": 4,
        "ppg": 76.2,
        "opp_ppg": 62.2
      }
    ]
  },
  "private": {
    "TAPPS_6A": [...]
  }
}
```

## Expected Results

After following all steps:

- ✓ 210 total teams (150 UIL + 60 TAPPS)
- ✓ Each UIL classification: exactly 25 teams
- ✓ Each TAPPS classification: exactly 10 teams
- ✓ No duplicate teams
- ✓ No location suffixes in team names
- ✓ All teams have win-loss records
- ✓ ~98.6% of teams have game statistics
- ✓ Website displays all data correctly

## Quick Verification Checklist

```bash
# 1. Check file exists and is recent
ls -lh data/rankings.json

# 2. Count teams per classification
python3 << 'EOF'
import json
with open('data/rankings.json') as f:
    r = json.load(f)
    for c in ['uil', 'private']:
        for cl, t in r[c].items():
            print(f"{c} {cl}: {len(t)} teams")
EOF

# 3. Check for location suffixes
grep -o '([^)]*TX[^)]*)' data/rankings.json | head -5

# 4. Test Flask app
curl http://localhost:5000/api/rankings | jq '.uil.AAAAAA | length'

# 5. Check git status
git status

# 6. Verify latest commit
git log -1 --oneline
```

## Time Estimates

- Scraping: 2-3 minutes
- Merging: 1 minute
- Cleaning: 1-2 minutes
- Adding statistics: 1 minute
- Verification: 2 minutes
- Commit/Push: 1 minute
- **Total: ~10 minutes**

## Notes

- TABC records are more accurate and current - always prioritize them
- Game statistics come from the normalized database schema
- Smart consensus caps outliers at top 15 to prevent ranking manipulation
- Cache auto-invalidates based on file modification time
- Server deployment varies by hosting setup

## Last Updated

January 12, 2026 - Process streamlined and documented after successful deployment
