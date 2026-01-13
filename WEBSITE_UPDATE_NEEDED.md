# Website Update Required - Comparison Report

**Date:** January 13, 2026
**Issue:** Website showing old data, not consensus rankings

---

## Executive Summary

The production website (https://tbbas.teamarete.net/) is **OUT OF DATE** and not displaying the consensus rankings that were implemented in the latest commits. The website appears to be showing either pure TABC rankings or older data from before the consensus algorithm was implemented.

### Quick Stats:
- **Local Data Status:** ✓ Correct (consensus working)
- **Website Status:** ✗ Out of date (needs deployment)
- **Commits Pushed:** ✓ All 5 commits pushed to origin/main
- **Server Deployment:** ✗ NOT deployed yet

---

## Key Differences

### UIL 6A Top 3
| Rank | Website (Old) | Local (Correct) | Issue |
|------|---------------|-----------------|-------|
| #1 | Katy Seven Lakes | Katy Seven Lakes | ✓ Match |
| #2 | North Crowley | **Little Elm** | ✗ Wrong order |
| #3 | Little Elm | **North Crowley** | ✗ Wrong order |

**Explanation:** Our consensus has Little Elm #2 (TABC #3, MaxPreps #1 → Consensus 2.0), but website shows pure TABC order.

### UIL 1A Top 3
| Rank | Website (Old) | Local (Correct) | Issue |
|------|---------------|-----------------|-------|
| #1 | Jayton | **Gordon** | ✗ Wrong (using TABC) |
| #2 | Gordon | **Jayton** | ✗ Wrong order |
| #3 | Brookeland | **Huckabay** | ✗ Wrong team |

**Explanation:** Gordon should be #1 (TABC #2, MaxPreps #2 → Consensus 2.0), not Jayton (TABC #1).

### UIL 4A Top 3
| Team | TABC Rank | MaxPreps Rank | Consensus Rank | Website Shows |
|------|-----------|---------------|----------------|---------------|
| Dallas Carter | #1 | #2 | 1.5 (#1) | Likely #1 ✓ |
| Estacado | #9 | #7 | 8.0 (#2) | Likely #9 ✗ |
| Seminole | #13 | #4 | 8.5 (#3) | Likely #13 ✗ |

---

## Problems on Website

### 1. Rankings Not Using Consensus
- Website appears to show pure TABC order or old data
- Should show blend of TABC + MaxPreps + Calculated

### 2. Location Suffixes Present
Examples found:
- "Cypress Springs (Cypress, TX)" → Should be "Cypress Springs"
- "Plano East (Plano, TX)" → Should be "Plano East"
- "Round Rock Westwood (Austin, TX)" → Should be "Round Rock Westwood"
- "Tompkins (Katy, TX)" → Should be "Tompkins"
- "Westlake (Austin, TX)" → Should be "Westlake"

### 3. Incorrect Records
- Plano East showing "3-4" (not in TABC top 25, should be removed)
- Cypress Springs showing "2-0" (should be 19-4)
- Tompkins showing "5-4" (not in TABC top 25, should be removed)

### 4. Missing Statistics
Many teams showing "—" for PPG, Opp PPG, and Margin instead of actual stats.

### 5. Wrong Team Count
Some classifications may have more/less than 25 UIL or 10 TAPPS teams.

---

## Local Data is Correct

Our local [data/rankings.json](data/rankings.json) has:

✓ **Consensus rankings working** - All classifications show proper blend of sources
✓ **TABC records accurate** - All win-loss records match TABC
✓ **No location suffixes** - All "(City, TX)" patterns removed
✓ **Correct team counts** - Exactly 25 UIL / 10 TAPPS per classification
✓ **Complete statistics** - 206/210 teams (98.1%) have game stats
✓ **Last updated** - 2026-01-13T10:24:24.896299
✓ **Source** - merged_tabc_maxpreps_calculated_cleaned

---

## Commits Already Pushed to origin/main

All work is committed and pushed:

1. **8ccf7f6** - Update documentation to use fix_tabc_records_only.py
2. **2c494b3** - Restore consensus rankings (TABC + MaxPreps + Calculated)
3. **388703b** - Fix Huckabay statistics to match actual season performance
4. **74b0c8f** - Add comprehensive weekly update documentation
5. **8bc702b** - Add RR Westwood name mapping to fix missing stats

---

## Deployment Instructions

To fix the website, deploy the latest code on the server:

```bash
# 1. SSH to production server
ssh user@tbbas-server

# 2. Navigate to project directory
cd /path/to/tbbas

# 3. Pull latest code
git pull origin main

# 4. Restart the application
sudo systemctl restart tbbas

# 5. Verify deployment
curl -s https://tbbas.teamarete.net/rankings/AAAAAA | grep "Little Elm" | head -1
# Should show Little Elm at rank #2, not #3
```

---

## Verification After Deployment

### Check UIL 6A Rankings
```bash
curl -s https://tbbas.teamarete.net/rankings/AAAAAA | grep -E "<td><strong>" | head -3
```

**Expected output:**
```
<td><strong>Katy Seven Lakes</strong></td>
<td><strong>Little Elm</strong></td>
<td><strong>North Crowley</strong></td>
```

### Check UIL 1A Rankings
```bash
curl -s https://tbbas.teamarete.net/rankings/A | grep -E "<td><strong>" | head -3
```

**Expected output:**
```
<td><strong>Gordon</strong></td>
<td><strong>Jayton</strong></td>
<td><strong>Huckabay</strong></td>
```

### Check for Location Suffixes
```bash
curl -s https://tbbas.teamarete.net/rankings/AAAAAA | grep "(.*TX.*)" | wc -l
```

**Expected:** 0 (no location suffixes)

---

## Consensus Algorithm Verification

After deployment, verify consensus is working across all classifications:

| Classification | #1 Team | TABC Rank | MaxPreps Rank | Consensus | Differs from TABC? |
|----------------|---------|-----------|---------------|-----------|-------------------|
| UIL 6A | Katy Seven Lakes | 1 | 2 | 1.5 | No (tied #1) |
| UIL 5A | Frisco Heritage | 1 | 1 | 1.0 | No (unanimous) |
| UIL 4A | Dallas Carter | 1 | 2 | 1.5 | No (tied #1) |
| UIL 3A | Paradise | 2 | 1 | 1.5 | **Yes (#2→#1)** |
| UIL 2A | Lipan | 1 | 1 | 1.0 | No (unanimous) |
| UIL 1A | Gordon | 2 | 2 | 2.0 | **Yes (#2→#1)** |

**Result:** 2/6 classifications have #1 team different from pure TABC (33%)

Looking at top 10 teams across all classifications:
- **UIL 6A:** 7/10 teams differ from TABC order (70%)
- **UIL 5A:** 6/10 teams differ from TABC order (60%)
- **UIL 4A:** 9/10 teams differ from TABC order (90%)
- **Overall:** 60-96% of rankings show consensus differences

---

## Summary

**What needs to happen:**
1. Deploy latest code to production server (git pull + restart)
2. Verify consensus rankings displaying correctly
3. Verify location suffixes removed
4. Verify correct team counts (25 UIL / 10 TAPPS)
5. Verify statistics displaying for 98%+ of teams

**Timeline:**
- Code changes: ✓ Complete
- Git commits: ✓ Complete
- Push to origin: ✓ Complete
- Server deployment: ⏳ **PENDING** ← This is what's needed

**Once deployed, the website will show:**
- Proper consensus rankings (TABC + MaxPreps + Calculated)
- TABC records as authority for wins/losses
- Clean team names without location suffixes
- Complete game statistics for 206/210 teams

---

**Created:** January 13, 2026
**Status:** Awaiting server deployment
**Priority:** High - website showing incorrect rankings
