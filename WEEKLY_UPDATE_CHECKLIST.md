# Weekly Rankings Update - Quick Checklist

**Time Required:** 10 minutes
**Last Updated:** January 13, 2026

---

## Pre-Update Checklist

- [ ] Backup current database: `cp instance/tbbas.db instance/tbbas.db.backup`
- [ ] Ensure you're on main branch: `git status`
- [ ] Pull latest changes: `git pull origin main`

---

## 6-Step Update Process (10 minutes)

### Step 1: Scrape Rankings (2-3 min)
```bash
python3 scrape_tabc_simple.py
python3 scrape_maxpreps_json.py
```

**Expected Output:**
- `tabc_rankings_scraped.json` - 150 teams (6 UIL classifications × 25 teams)
- `maxpreps_rankings_scraped.json` - Similar structure

### Step 2: Merge with Consensus (1 min)
```bash
python3 merge_all_rankings.py
```

**What This Does:**
- Blends TABC + MaxPreps + Calculated rankings
- Uses smart averaging with outlier prevention (top 15 cap)
- Creates consensus rankings in `data/rankings.json`

**⚠️ CRITICAL:** This creates the consensus - DON'T overwrite it later!

### Step 3: Trim to Top 25/10 (1 min)
```bash
python3 trim_to_top_25.py
```

**What This Does:**
- UIL classifications: Keep top 25
- TAPPS classifications: Keep top 10
- Preserves consensus ranking order

### Step 4: Clean Location Suffixes (30 sec)
```bash
python3 clean_location_suffixes.py
```

**What This Does:**
- Removes "(City, TX)" patterns from all team names
- Single purpose, no side effects

### Step 5: Fix TABC Records ONLY (1 min)
```bash
python3 fix_tabc_records_only.py
```

**What This Does:**
- Updates win-loss records from TABC
- Preserves consensus ranking order
- Does NOT change team positions

**⚠️ DO NOT USE:** `fix_tabc_records_complete.py` - it overwrites consensus!

### Step 6: Add Game Statistics (1 min)
```bash
python3 update_rankings_complete.py
```

**What This Does:**
- Adds PPG, Opp PPG, Margin columns
- Uses database game records
- Smart name matching via school_abbreviations.py

---

## Verification (30 sec)

```bash
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
```

**Expected Output:**
```
✓ uil AAAAAA: 25/25
✓ uil AAAAA: 25/25
✓ uil AAAA: 25/25
✓ uil AAA: 25/25
✓ uil AA: 25/25
✓ uil A: 25/25
✓ private 6A: 10/10
✓ private 5A: 10/10
✓ private 4A: 10/10
✓ private 3A: 10/10
✓ private 2A: 10/10
✓ private 1A: 10/10
```

**If you see ✗:** Check LESSONS_LEARNED.md for troubleshooting

---

## Deployment (1 min)

```bash
# Update master backup
cp data/rankings.json rankings.json.master

# Commit and push
git add data/rankings.json rankings.json.master
git commit -m "Weekly rankings update: TABC + MaxPreps + stats ($(date +%Y-%m-%d))"
git push origin main
```

**What Happens:**
1. GitHub receives push
2. Railway detects changes (usually within 1 min)
3. Railway auto-builds and deploys (1-3 min)
4. `ensure_data_on_startup.py` restores from rankings.json.master

**Deployment URL:** https://tbbas.teamarete.net/

---

## Post-Deployment Verification (30 sec)

```bash
./verify_deployment.sh
```

Or manually check:

```bash
# Check UIL 6A top 3
curl -s https://tbbas.teamarete.net/rankings/AAAAAA | grep -E "<td><strong>" | head -3

# Check for location suffixes (should be 0)
curl -s https://tbbas.teamarete.net/rankings/AAAAAA | grep -c "(.*TX.*)"
```

**Verification Checklist:**
- [ ] All 12 classification pages load
- [ ] Team counts correct (25 for UIL, 10 for TAPPS)
- [ ] No location suffixes visible
- [ ] Records look reasonable
- [ ] Statistics showing (PPG, Opp PPG, Margin)

---

## Manual Fixes (Only When Needed)

### Duplicate Team Found
**DON'T USE:** `clean_duplicate_teams.py` (too aggressive)

**DO THIS:** Write targeted Python script
```python
import json
with open('data/rankings.json', 'r') as f:
    rankings = json.load(f)

teams = rankings['uil']['AAAAA']
# Remove specific duplicate
for i, team in enumerate(teams):
    if team['team_name'] == 'Exact Duplicate Name':
        del teams[i]
        break

with open('data/rankings.json', 'w') as f:
    json.dump(rankings, f, indent=2)
```

### Wrong Record for Specific Team
Already handled by `fix_tabc_records_only.py` in Step 5.

If TABC is wrong, manually fix:
```python
import json
with open('data/rankings.json', 'r') as f:
    rankings = json.load(f)

for team in rankings['uil']['AAAAAA']:
    if team['team_name'] == 'Team Name':
        team['wins'] = 20
        team['losses'] = 3
        team['record'] = '20-3'
        break

with open('data/rankings.json', 'w') as f:
    json.dump(rankings, f, indent=2)
```

### Missing Team Name Mapping
Add to [school_abbreviations.py](school_abbreviations.py):
```python
SPECIAL_CASES = {
    'RR Westwood': 'Round Rock Westwood',
    # Add new mapping here
}
```
Then run `update_rankings_complete.py` again.

---

## Key Principles (Remember These!)

### 1. Consensus is Sacred
- **NEVER** use scripts that overwrite consensus rankings
- TABC is authority for **records** only, not ranking order
- fix_tabc_records_only.py = GOOD ✓
- fix_tabc_records_complete.py = BAD ✗

### 2. One Problem at a Time
- Fix one issue, verify, then move to next
- Don't run multiple transformations hoping they work together
- If something breaks, revert and try differently

### 3. Simple is Better
- 6 core steps is better than 10 complex steps
- Each script should do ONE thing
- Avoid scripts with multiple purposes

### 4. Manual Fixes are OK
- Better to manually fix 1-2 issues than break everything
- Python REPL is your friend for targeted fixes
- Document what you did

### 5. Trust the Consensus
- merge_all_rankings.py does the hard work
- Just trim, clean suffixes, fix records, add stats
- Don't second-guess the consensus algorithm

---

## Scripts Reference

### ✅ Use These Every Week
| Script | Purpose | Time |
|--------|---------|------|
| `scrape_tabc_simple.py` | Get TABC rankings | 1-2 min |
| `scrape_maxpreps_json.py` | Get MaxPreps rankings | 1-2 min |
| `merge_all_rankings.py` | Create consensus | 1 min |
| `trim_to_top_25.py` | Trim to 25/10 teams | 30 sec |
| `clean_location_suffixes.py` | Remove location suffixes | 30 sec |
| `fix_tabc_records_only.py` | Fix records, preserve consensus | 1 min |
| `update_rankings_complete.py` | Add game stats | 1 min |

### ❌ DON'T Use These
| Script | Why Not | Alternative |
|--------|---------|-------------|
| `fix_tabc_records_complete.py` | Overwrites consensus | Use fix_tabc_records_only.py |
| `fix_tabc_records.py` | Doesn't remove non-TABC teams | Use fix_tabc_records_only.py |
| `clean_duplicate_teams.py` | Too aggressive, removes legitimate teams | Manual Python script |

---

## Troubleshooting

### Issue: Team counts wrong after update
**Symptoms:** 19/25 or 24/25 instead of 25/25

**Causes:**
- Used clean_duplicate_teams.py (too aggressive)
- Removed teams that shouldn't be removed

**Fix:**
1. Restore from backup: `cp instance/tbbas.db.backup instance/tbbas.db`
2. Revert: `git checkout data/rankings.json`
3. Start over from Step 2
4. Don't use clean_duplicate_teams.py

### Issue: Rankings not showing consensus order
**Symptoms:** Rankings match pure TABC order

**Causes:**
- Used fix_tabc_records_complete.py instead of fix_tabc_records_only.py
- Accidentally overwrote consensus_rank values

**Fix:**
1. Restore from git: `git checkout data/rankings.json`
2. Re-run Step 5 with correct script: `fix_tabc_records_only.py`
3. Verify consensus_rank values differ from tabc_rank

### Issue: Railway not deploying
**Symptoms:** Website still shows old data after push

**Causes:**
- Railway deployment takes 1-3 minutes
- rankings.json.master not updated

**Fix:**
1. Wait 3-5 minutes
2. Check Railway dashboard: https://railway.app/
3. If still not deployed, force redeploy:
   ```bash
   echo "# $(date)" >> Procfile
   git add Procfile
   git commit -m "Force Railway redeploy"
   git push origin main
   ```

### Issue: Website shows errors after deployment
**Symptoms:** 500 errors or crashes

**Immediate Action:**
1. Check Railway logs for Python exceptions
2. Roll back to previous deployment in Railway dashboard

**Common Causes:**
- rankings.json format issue (missing fields)
- Import errors (wrong file paths)

**Fix:**
1. Test locally first: `python app.py`
2. Verify rankings.json format
3. Push fix to GitHub

---

## Time Comparison

### This Week (Before Streamlining): ~2 hours
- Scraping: 3 min
- Merging: 1 min
- Multiple failed cleaning attempts: 30 min
- Manual fixes for wrong counts: 45 min
- Multiple deploy attempts: 30 min
- Debugging: 15 min

### Next Week (After Streamlining): ~10 minutes
- Scraping: 3 min
- Merging: 1 min
- Trimming: 1 min
- Clean suffixes: 30 sec
- Fix records: 1 min
- Add stats: 1 min
- Verify: 30 sec
- Deploy: 1 min
- Buffer: 1 min

**Savings: 110 minutes (92% faster)**

---

## Quick Commands Summary

```bash
# Full update (copy/paste this block)
python3 scrape_tabc_simple.py && \
python3 scrape_maxpreps_json.py && \
python3 merge_all_rankings.py && \
python3 trim_to_top_25.py && \
python3 clean_location_suffixes.py && \
python3 fix_tabc_records_only.py && \
python3 update_rankings_complete.py

# Verify
python3 -c "import json; r=json.load(open('data/rankings.json')); print('\\n'.join([f\"{'✓' if len(r[c][cl])==(25 if c=='uil' else 10) else '✗'} {c} {cl}: {len(r[c][cl])}/{25 if c=='uil' else 10}\" for c in ['uil','private'] for cl in r[c]]))"

# Deploy
cp data/rankings.json rankings.json.master && \
git add data/rankings.json rankings.json.master && \
git commit -m "Weekly rankings update: TABC + MaxPreps + stats ($(date +%Y-%m-%d))" && \
git push origin main
```

---

**Created:** January 13, 2026
**Next Update:** Week of January 19, 2026
**Expected Time:** 10 minutes

**See Also:**
- [LESSONS_LEARNED.md](LESSONS_LEARNED.md) - What worked and what didn't
- [QUICK_UPDATE.md](QUICK_UPDATE.md) - Fast command reference
- [DEPLOYMENT_INSTRUCTIONS.md](DEPLOYMENT_INSTRUCTIONS.md) - Deployment troubleshooting
