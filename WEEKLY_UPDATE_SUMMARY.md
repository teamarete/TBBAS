# Weekly Rankings Update - Summary & Improvements

**Date:** January 12, 2026
**Session Focus:** Fix incorrect TABC records and streamline weekly update process

---

## What Was Fixed This Week

### 1. Incorrect Records Fixed
All records now use TABC as the authoritative source:

- **UIL 6A (AAAAAA)**
  - ✓ Cypress Springs: 2-0 → 19-4 (TABC rank #22)
  - ✓ Plano East: Removed (3-4 record, not in TABC top 25)
  - ✓ Tompkins: Removed (5-4 record, not in TABC top 25)

- **UIL 5A (AAAAA)**
  - ✓ West Brook duplicate removed
  - ✓ Bmt West Brook: Correct record 18-3 (TABC rank #10)

- **UIL 4A (AAAA)**
  - ✓ Liberty (32-30) removed - was incorrect entry
  - ✓ Lubbock Liberty: Correct record 17-4 (TABC rank #10)

### 2. Team Name Mapping Issues Fixed
Added missing abbreviation mappings to `school_abbreviations.py`:

```python
# City abbreviations
'RR': 'Round Rock',  # Line 27

# Special cases
'RR Westwood': 'Round Rock Westwood',  # Line 67
```

**Result:** RR Westwood now has complete game statistics (12 games, 66.8 PPG)

### 3. Final Data Quality
- ✓ All classifications: Exactly 25 UIL / 10 TAPPS teams
- ✓ Teams with stats: 204/210 (97.1%)
- ✓ TABC records used for all ranked teams
- ✓ Game statistics from database preserved

---

## New Scripts Created

### 1. `fix_tabc_records.py`
Initial attempt to fix records - adds missing teams but doesn't remove extras.

### 2. `fix_tabc_records_complete.py` ⭐ **Use This One**
Complete fix using TABC as authoritative source:
- Rebuilds each classification from TABC top 25
- Preserves game statistics from database
- Removes teams not in TABC top 25
- Ensures correct team counts

**Usage:**
```bash
python3 fix_tabc_records_complete.py
```

---

## Improved Weekly Update Process

### Current Best Practice (Updated)

```bash
# 1. Scrape rankings (2-3 min)
python3 scrape_tabc_simple.py
python3 scrape_maxpreps_json.py

# 2. Merge rankings (1 min)
python3 merge_all_rankings.py

# 3. Clean duplicates (1 min)
python3 clean_duplicate_teams.py

# 4. Remove location suffixes (1 min)
python3 clean_location_suffixes.py

# 5. Fix any TABC record discrepancies (NEW - 1 min)
python3 fix_tabc_records_complete.py

# 6. Add game statistics (1 min)
python3 update_rankings_complete.py

# 7. Verify data (1 min)
python3 << 'EOF'
import json
with open('data/rankings.json') as f:
    r = json.load(f)
    for c in ['uil', 'private']:
        exp = 25 if c == 'uil' else 10
        for cl, t in r[c].items():
            status = "✓" if len(t) == exp else "✗"
            print(f"{status} {c} {cl}: {len(t)}/{exp}")
    stats_count = sum(1 for c in ['uil', 'private']
                     for cl, teams in r[c].items()
                     for t in teams if t.get('games', 0) > 0)
    print(f"\nTeams with stats: {stats_count}/210 ({stats_count/210*100:.1f}%)")
EOF

# 8. Test locally (1 min)
python3 << 'EOF'
from app_refactored import create_app
app = create_app()
with app.test_client() as client:
    tests = [
        ('/', 'Home'),
        ('/rankings/AAAAAA', 'UIL 6A'),
        ('/api/rankings', 'API'),
        ('/api/rankings/TAPPS_6A', 'TAPPS API')
    ]
    for url, name in tests:
        r = client.get(url)
        print(f"{'✓' if r.status_code == 200 else '✗'} {name}: {r.status_code}")
EOF

# 9. Commit and push (2 min)
git add data/rankings.json
git commit -m "Weekly rankings update: TABC + MaxPreps + game stats ($(date +%Y-%m-%d))"
git push origin main

# 10. Deploy to server
# SSH to server and run:
# cd /path/to/tbbas && git pull origin main && sudo systemctl restart tbbas
```

---

## Key Lessons Learned

### Problem: Teams Missing Game Statistics

**Root Cause:** Name mismatches between TABC rankings and database

**Examples Found:**
- "RR Westwood" (TABC) vs "Round Rock Westwood" (database)
- "Bmt West Brook" (TABC) vs "Beaumont West Brook" (database)

**Solution:** Add mappings to `school_abbreviations.py`
- Check `CITY_ABBREVIATIONS` for city prefix mappings
- Check `SPECIAL_CASES` for full name mappings

**How to Debug:**
```bash
python3 << 'EOF'
from app_refactored import create_app
from models_normalized import Team
from sqlalchemy import or_

app = create_app()
with app.app_context():
    # Search for team variations
    teams = Team.query.filter(
        or_(
            Team.display_name.ilike('%TEAM_NAME%'),
            Team.normalized_name.ilike('%TEAM_NAME%')
        )
    ).all()

    for team in teams:
        print(f"{team.display_name} (normalized: {team.normalized_name})")
        print(f"  Classification: {team.classification}")
EOF
```

### Problem: TABC Records Overridden by Database Games

**Root Cause:** `update_rankings_complete.py` was updating records even when TABC had them

**Solution:** The script now only updates if current record is 0-0:
```python
if current_wins == 0 and current_losses == 0:
    team['wins'] = stats['wins']
    team['losses'] = stats['losses']
```

**Best Practice:** Always use `fix_tabc_records_complete.py` BEFORE `update_rankings_complete.py`

### Problem: Wrong Team Counts (Not 25/10)

**Root Cause:** Manual fixes or merges sometimes added/removed teams incorrectly

**Solution:** Use `fix_tabc_records_complete.py` which:
1. Takes only TABC top 25 as source of truth
2. Removes any teams not in TABC top 25
3. Adds any teams from TABC top 25 that are missing
4. Re-ranks based on TABC rank

---

## Files Modified This Session

### Core Application
- `app/blueprints/rankings.py` - Fixed statistics display and TAPPS data key
- `school_abbreviations.py` - Added RR Westwood mapping

### Data Files
- `data/rankings.json` - Updated with correct TABC records and game stats

### New Scripts
- `fix_tabc_records.py` - Initial fix attempt (partial)
- `fix_tabc_records_complete.py` - Complete TABC-based rebuild ⭐

### Documentation
- `QUICK_UPDATE.md` - Quick command reference (already existed)
- `RANKINGS_UPDATE_GUIDE.md` - Detailed step-by-step guide (already existed)
- `WEEKLY_UPDATE_SUMMARY.md` - This file (NEW)

---

## Common Issues & Quick Fixes

### Issue: Team has 0 games but should have stats

**Check:**
```bash
# Find team in database with variations
python3 << 'EOF'
from app_refactored import create_app
from models_normalized import Team, TeamGameStats
from sqlalchemy import or_

app = create_app()
with app.app_context():
    teams = Team.query.filter(
        or_(
            Team.display_name.ilike('%TEAM_NAME%'),
            Team.normalized_name.ilike('%TEAM_NAME%')
        )
    ).all()

    for team in teams:
        stats_count = TeamGameStats.query.filter_by(team_id=team.id).count()
        print(f"{team.display_name}: {stats_count} games")
EOF
```

**Fix:** Add name mapping to `school_abbreviations.py`

### Issue: Team record doesn't match TABC

**Fix:**
```bash
python3 fix_tabc_records_complete.py
python3 update_rankings_complete.py
```

### Issue: Duplicate teams appearing

**Fix:**
```bash
python3 clean_duplicate_teams.py
python3 clean_location_suffixes.py
```

### Issue: Wrong team count (not 25 UIL / 10 TAPPS)

**Fix:**
```bash
python3 fix_tabc_records_complete.py
```

---

## Next Week's Checklist

Before starting:
- [ ] Verify TABC has published new rankings
- [ ] Backup current rankings: `cp data/rankings.json data/rankings.json.backup`

During update:
- [ ] Scrape TABC and MaxPreps
- [ ] Merge rankings
- [ ] Clean duplicates and location suffixes
- [ ] **NEW:** Run `fix_tabc_records_complete.py` to ensure TABC accuracy
- [ ] Add game statistics
- [ ] Verify team counts and stats coverage
- [ ] Test locally
- [ ] Commit and push
- [ ] Deploy to server

After deployment:
- [ ] Check website shows correct data
- [ ] Verify a few teams have correct records
- [ ] Check that stats are displaying

---

## Technical Debt / Future Improvements

1. **Automate name mapping detection**
   - Script to detect TABC teams with 0 games and suggest database matches
   - Fuzzy matching to find similar team names

2. **Improve error reporting**
   - `update_rankings_complete.py` should report all name mismatches in a structured way
   - Generate a "review needed" list for manual checking

3. **Add validation tests**
   - Automated tests to verify team counts
   - Tests to ensure all TABC top 25 teams are present
   - Tests to check for duplicate teams

4. **Consider database triggers**
   - Auto-update team records when games are added
   - Maintain running statistics in real-time

---

## Important Notes

### TABC is Always Right
The TABC rankings are the official source of truth for:
- Win-loss records
- Team rankings (1-25 for UIL, varies for TAPPS)
- Which teams should be displayed

Database games are used ONLY for:
- Game statistics (PPG, efficiency ratings, etc.)
- Additional context beyond the record

### Don't Trust Database Records
If a team's database games show a different record than TABC, always use TABC. The database may:
- Be missing games
- Have incomplete data
- Include games that TABC doesn't count

### Always Verify After Push
The website cache auto-invalidates based on file modification time, but:
1. Server must pull latest code: `git pull origin main`
2. App must restart: `sudo systemctl restart tbbas`
3. Browser may cache: Do hard refresh (Cmd+Shift+R)

---

## Contact Info for Issues

If something goes wrong:
1. Check git history: `git log --oneline -10`
2. Rollback if needed: `git checkout HEAD~1 data/rankings.json`
3. Review this document for common fixes
4. Check the detailed guide: `RANKINGS_UPDATE_GUIDE.md`

---

**Last Updated:** January 12, 2026
**Next Update Due:** Week of January 19, 2026
**Estimated Time:** 10-12 minutes (with new verification step)
