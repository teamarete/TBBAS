# Lessons Learned - Rankings Update Process

**Date:** January 13, 2026
**Purpose:** Streamline future weekly updates based on what worked/didn't work

---

## What Worked ✅

### 1. Consensus Ranking Approach
**What:** Using `merge_all_rankings.py` to blend TABC + MaxPreps + Calculated
**Why it worked:**
- Provides more balanced rankings than any single source
- Smart outlier prevention (top 15 cap)
- User explicitly wanted this approach

**Keep for next week:** YES

### 2. fix_tabc_records_only.py
**What:** Updates TABC records while preserving consensus ranking order
**Why it worked:**
- Preserves the consensus we worked hard to create
- Only updates wins/losses, not ranking order
- Fast and reliable

**Keep for next week:** YES - Use this, not fix_tabc_records_complete.py

### 3. clean_location_suffixes.py
**What:** Removes "(City, TX)" patterns from all team names
**Why it worked:**
- Single purpose, does one thing well
- Cleaned 87 teams successfully
- No side effects

**Keep for next week:** YES

### 4. update_rankings_complete.py
**What:** Adds game statistics from database to rankings
**Why it worked:**
- 98.6% stats coverage achieved
- Doesn't overwrite TABC records
- Uses smart name matching

**Keep for next week:** YES

### 5. Railway Auto-Deploy
**What:** Git push → Railway detects → Auto-deploys
**Why it worked:**
- No manual server access needed
- Automatic on every push
- `ensure_data_on_startup.py` restores from `rankings.json.master`

**Keep for next week:** YES

### 6. Manual Targeted Fixes
**What:** Python scripts to fix specific issues (e.g., West Brook duplicate)
**Why it worked:**
- Precise control over changes
- Can verify before committing
- No unintended side effects

**Keep for next week:** YES - When needed

---

## What Didn't Work ❌

### 1. fix_tabc_records_complete.py
**What:** Rebuilds rankings using TABC top 25 as sole source
**Why it failed:**
- OVERWRITES consensus rankings
- Ignores MaxPreps and Calculated ranks
- Defeats the purpose of consensus

**Action:** DELETE or clearly mark as "DO NOT USE"
**Alternative:** Always use `fix_tabc_records_only.py` instead

### 2. clean_duplicate_teams.py (current version)
**What:** Attempts to remove duplicates automatically
**Why it failed:**
- Too aggressive - removed legitimate teams
- Changed team counts incorrectly (19/25 instead of 25/25)
- Created more problems than it solved

**Action:** NEEDS REWRITE - should only remove exact duplicates, not merge similar names
**Alternative:** Manual identification + targeted removal

### 3. Trying to "Fix Everything at Once"
**What:** Running multiple cleaning scripts in sequence hoping they'd work together
**Why it failed:**
- Scripts have side effects that cascade
- Team counts get messed up
- Consensus rankings get lost

**Action:** STOP doing this
**Alternative:** Fix one issue at a time, verify, then move to next

### 4. Using merge → clean → trim workflow blindly
**What:** merge_all_rankings.py → clean_duplicate_teams.py → trim to top 25
**Why it failed:**
- Cleaning step removes legitimate teams
- Trimming after cleaning gives wrong teams
- Ends up with 19-24 teams instead of 25

**Action:** SIMPLIFY - merge already gives top 40, just trim to 25
**Alternative:** merge → trim to 25 → clean suffixes only → fix records

### 5. fix_tabc_records.py (the original one)
**What:** Adds missing TABC teams and fixes records
**Why it partially failed:**
- Adds teams but doesn't remove non-TABC teams
- Can end up with more than 25 teams
- Sets consensus_rank = tabc_rank (wrong)

**Action:** DON'T USE for regular updates
**Alternative:** Use fix_tabc_records_only.py

---

## Streamlined Process for Next Week

### The New 6-Step Process (10 minutes)

```bash
# 1. Scrape rankings (2-3 min)
python3 scrape_tabc_simple.py
python3 scrape_maxpreps_json.py

# 2. Merge with consensus (1 min)
python3 merge_all_rankings.py

# 3. Trim to top 25/10 and save (1 min)
python3 trim_to_top_25.py

# 4. Clean location suffixes ONLY (30 sec)
python3 clean_location_suffixes.py

# 5. Fix TABC records ONLY - preserves consensus (1 min)
python3 fix_tabc_records_only.py

# 6. Add game statistics (1 min)
python3 update_rankings_complete.py

# 7. Verify (30 sec)
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

# 8. Deploy (1 min)
cp data/rankings.json rankings.json.master
git add data/rankings.json rankings.json.master
git commit -m "Weekly rankings update: TABC + MaxPreps + stats ($(date +%Y-%m-%d))"
git push origin main
```

### Manual Fixes (Only When Needed)

If you encounter specific issues during the update:

**Duplicate Team:** Write targeted Python script to remove specific duplicate (don't use clean_duplicate_teams.py)

**Wrong Record:** Already handled by fix_tabc_records_only.py

**Missing Team Name Mapping:** Add to school_abbreviations.py, run update_rankings_complete.py again

---

## Scripts to Keep

### Essential Scripts (use every week)
1. ✅ `scrape_tabc_simple.py` - Get TABC rankings
2. ✅ `scrape_maxpreps_json.py` - Get MaxPreps rankings
3. ✅ `merge_all_rankings.py` - Create consensus
4. ✅ `trim_to_top_25.py` - NEW - Trim to 25/10
5. ✅ `clean_location_suffixes.py` - Remove location suffixes
6. ✅ `fix_tabc_records_only.py` - Fix records, preserve consensus
7. ✅ `update_rankings_complete.py` - Add game stats

### Scripts to Avoid
1. ❌ `fix_tabc_records_complete.py` - Overwrites consensus (BAD)
2. ❌ `fix_tabc_records.py` - Doesn't remove non-TABC teams properly
3. ❌ `clean_duplicate_teams.py` - Too aggressive, needs rewrite

---

## Key Principles for Next Week

### 1. Consensus is Sacred
- Never use scripts that overwrite consensus rankings
- TABC records: YES (fix with fix_tabc_records_only.py)
- TABC order: NO (keep consensus order)

### 2. One Problem at a Time
- Don't run multiple transformations hoping they'll work together
- Verify after each step
- If something breaks, revert and try differently

### 3. Simple is Better
- 6 core steps is better than 10 complex steps
- Each step should do ONE thing
- Avoid scripts with multiple purposes

### 4. Manual Fixes are OK
- Better to manually fix 1-2 issues than break everything with automation
- Python REPL is your friend for targeted fixes
- Document what you did for next time

### 5. Trust the Consensus
- merge_all_rankings.py does the hard work
- Just trim, clean suffixes, fix records, add stats
- Don't second-guess the consensus algorithm

---

## Quick Reference: Which Script to Use When

| Task | Script | Why |
|------|--------|-----|
| Get TABC data | `scrape_tabc_simple.py` | Works reliably |
| Get MaxPreps data | `scrape_maxpreps_json.py` | Works reliably |
| Create consensus | `merge_all_rankings.py` | Core algorithm |
| Trim to 25/10 | `trim_to_top_25.py` | NEW - Simple, no side effects |
| Remove suffixes | `clean_location_suffixes.py` | Single purpose |
| Fix records | `fix_tabc_records_only.py` | Preserves consensus |
| Add stats | `update_rankings_complete.py` | 98.6% coverage |
| Fix duplicate | Manual Python | Too specific for automation |

---

## Time Savings for Next Week

### Old Process (this week): ~2 hours
- Scraping: 3 min
- Merging: 1 min
- Multiple failed cleaning attempts: 30 min
- Manual fixes for wrong counts: 45 min
- Multiple deploy attempts: 30 min
- Debugging: 15 min

### New Process (next week): ~10 minutes
- Scraping: 3 min
- Merging: 1 min
- Trimming: 1 min
- Clean suffixes: 30 sec
- Fix records: 1 min
- Add stats: 1 min
- Verify: 30 sec
- Deploy: 1 min
- Buffer: 1 min

**Savings: ~110 minutes** (92% faster)

---

**Created:** January 13, 2026
**Next Update:** Week of January 19, 2026
**Expected Time:** 10 minutes (vs. 2 hours this week)
