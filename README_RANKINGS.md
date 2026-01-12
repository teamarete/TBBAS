# TBBAS Rankings System Documentation

Complete documentation for the Texas Boys Basketball Analytics System rankings update process.

## 📚 Documentation Index

1. **[QUICK_UPDATE.md](QUICK_UPDATE.md)** - Fast command reference (use this for regular updates)
2. **[RANKINGS_UPDATE_GUIDE.md](RANKINGS_UPDATE_GUIDE.md)** - Detailed step-by-step guide with explanations
3. **This file** - Overview and quick start

## 🚀 Quick Start

For weekly ranking updates, use this single command block:

```bash
# Complete update process (~10 minutes)
python3 scrape_tabc_simple.py && \
python3 scrape_maxpreps_json.py && \
python3 merge_all_rankings.py && \
python3 clean_duplicate_teams.py && \
python3 clean_location_suffixes.py && \
python3 update_rankings_complete.py && \
git add data/rankings.json && \
git commit -m "Update rankings: $(date +%Y-%m-%d)" && \
git push origin main
```

Then deploy on server:
```bash
cd /path/to/tbbas && git pull origin main && sudo systemctl restart tbbas
```

## 📊 What Gets Updated

### Data Sources
- **TABC Rankings** - Win-loss records (most accurate)
- **MaxPreps Rankings** - National perspective
- **Database** - Game statistics (2,294 teams with 4,300+ games)

### Output
- **210 teams total**
  - 150 UIL (6 classifications × 25 teams)
  - 60 TAPPS (6 classifications × 10 teams)
- **~98.6% coverage** (207 teams with complete game statistics)

### Statistics Included
- Win-loss records (all teams)
- Games played (207 teams)
- Points per game
- Opponent PPG
- Net rating (point differential)
- Offensive efficiency (per 100 possessions)
- Defensive efficiency (per 100 possessions)

## 🔧 Key Scripts

| Script | Purpose |
|--------|---------|
| scrape_tabc_simple.py | Scrape TABC weekly rankings |
| scrape_maxpreps_json.py | Scrape MaxPreps rankings |
| merge_all_rankings.py | Merge sources with smart consensus |
| clean_duplicate_teams.py | Remove duplicate teams |
| clean_location_suffixes.py | Strip (City, TX) suffixes |
| update_rankings_complete.py | Add game stats from database |

## 🐛 Common Issues & Solutions

### Issue: Website shows no data
**Solution:** Server needs to pull and restart
```bash
# On server
cd /path/to/tbbas
git pull origin main
sudo systemctl restart tbbas
```

### Issue: Duplicate teams
**Solution:** Run cleaners
```bash
python3 clean_duplicate_teams.py
python3 clean_location_suffixes.py
```

### Issue: Teams missing statistics
**Solution:** Check name matching
```bash
python3 update_rankings_complete.py
# Check output for warnings
```

## 📁 Important Files

### Configuration
- data/rankings.json - Published rankings (used by website)
- app/blueprints/rankings.py - Flask routes
- models_normalized.py - Database schema

### Intermediate Files
- tabc_rankings_scraped.json - TABC source
- maxpreps_rankings_scraped.json - MaxPreps source
- rankings_merged_preview.json - After merge
- rankings_cleaned_preview.json - After cleaning

## ✅ Verification Checklist

After updating, verify:
- 210 total teams
- UIL: 25 teams per classification
- TAPPS: 10 teams per classification
- No location suffixes in team names
- No duplicate teams
- ~98% have game statistics
- Flask app tests pass locally
- Changes committed and pushed
- Server deployed successfully

## 🔄 Update Frequency

**Weekly during season:**
- TABC updates: Every Monday
- MaxPreps updates: Continuous
- Database games: Updated as reported

**Recommended schedule:**
- Update rankings every Monday after TABC releases
- Takes ~10 minutes total

## 🆘 Emergency Contact

If issues arise:
1. Check RANKINGS_UPDATE_GUIDE.md for detailed troubleshooting
2. Review recent commits: git log --oneline -10
3. Rollback if needed: git checkout HEAD~1 data/rankings.json

## 📈 System Architecture

```
TABC Rankings ──┐
                ├──> Merge ──> Clean ──> Add Stats ──> Publish ──> Website
MaxPreps ───────┤
Database Games ─┘
```

## 📝 Recent Updates

- **Jan 12, 2026** - Added complete game statistics (98.6% coverage)
- **Jan 12, 2026** - Removed all location suffixes
- **Jan 12, 2026** - Fixed Flask blueprint to display stats
- **Jan 12, 2026** - Merged La Marque duplicate
- **Jan 12, 2026** - Created comprehensive documentation

## 🎯 Next Steps

After reading this:
1. Use QUICK_UPDATE.md for regular updates
2. Refer to RANKINGS_UPDATE_GUIDE.md for details
3. Run the update process weekly during season

---

**Documentation maintained by:** TBBAS Team
**Last updated:** January 12, 2026
**Process time:** ~10 minutes
**Success rate:** 98.6% team coverage
