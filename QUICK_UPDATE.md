# Quick Rankings Update - Command Reference

Fast reference for updating TBBAS rankings. See [RANKINGS_UPDATE_GUIDE.md](RANKINGS_UPDATE_GUIDE.md) for detailed documentation.

## The Complete Process (10 minutes)

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

# 5. Fix TABC record discrepancies (1 min)
# IMPORTANT: Use fix_tabc_records_only.py to preserve consensus rankings
python3 fix_tabc_records_only.py

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
git add data/rankings.json update_rankings_complete.py clean_location_suffixes.py app/blueprints/rankings.py
git commit -m "Update rankings: TABC + MaxPreps + game stats ($(date +%Y-%m-%d))"
git push origin main

# 10. Deploy to server
# SSH to server and run:
# cd /path/to/tbbas && git pull origin main && sudo systemctl restart tbbas
```

## Expected Results

After completion:
- ✓ 210 teams (150 UIL + 60 TAPPS)
- ✓ UIL: 25 teams per classification
- ✓ TAPPS: 10 teams per classification
- ✓ No location suffixes
- ✓ No duplicates
- ✓ ~98% with game statistics

## Quick Fixes

**Duplicates found?**
```bash
python3 clean_duplicate_teams.py
python3 clean_location_suffixes.py
```

**Missing stats?**
```bash
python3 update_rankings_complete.py
```

**Website not updating?**
```bash
# On server:
git pull origin main
sudo systemctl restart tbbas
```

## Files Created/Updated

- `data/rankings.json` ← Final output (used by website)
- `tabc_rankings_scraped.json` ← TABC source
- `maxpreps_rankings_scraped.json` ← MaxPreps source
- `rankings_merged_preview.json` ← After merge
- `rankings_cleaned_preview.json` ← After cleaning

## Key Scripts

| Script | Purpose | Time |
|--------|---------|------|
| `scrape_tabc_simple.py` | Get TABC rankings | 1-2 min |
| `scrape_maxpreps_json.py` | Get MaxPreps rankings | 1 min |
| `merge_all_rankings.py` | Merge sources with consensus | 1 min |
| `clean_duplicate_teams.py` | Remove duplicates | 30 sec |
| `clean_location_suffixes.py` | Strip (City, TX) | 30 sec |
| `fix_tabc_records_only.py` | Fix TABC records only | 1 min |
| `update_rankings_complete.py` | Add game stats from DB | 1 min |

## Common Issues

| Issue | Solution |
|-------|----------|
| Teams with (City, TX) | Run `clean_location_suffixes.py` |
| Duplicate teams | Run `clean_duplicate_teams.py` |
| Missing stats | Check team name matching in output |
| Website blank | Check server pulled code + restarted |
| Wrong team count | Verify merge/clean scripts ran |

## Verification Commands

```bash
# Count teams
jq '.uil | to_entries | map(.value | length)' data/rankings.json

# Check for suffixes
grep '(.*TX.*)' data/rankings.json | wc -l

# List teams without games
jq -r '.uil,.private | .[] | .[] | select(.games == 0) | .team_name' data/rankings.json

# Check last update
jq -r '.last_updated' data/rankings.json
```

## Emergency Rollback

```bash
# Restore previous version
git checkout HEAD~1 data/rankings.json

# Or restore from backup
cp data/rankings.json.backup data/rankings.json

# Push fix
git add data/rankings.json
git commit -m "Rollback rankings to previous version"
git push origin main
```

---

**Last Updated:** January 12, 2026
**Total Time:** ~11 minutes (added TABC verification step)
**Success Rate:** 97.1% team coverage (204/210 teams)
