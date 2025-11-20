# Rankings Display Update

**Updated:** November 20, 2025
**Commit:** `995981e` - Limit rankings display to top 25 UIL and top 10 TAPPS

---

## 📊 What Changed

The website now displays only the **top-ranked teams** for each classification:

| Classification Type | Teams Displayed |
|---------------------|-----------------|
| **UIL** (6A, 5A, 4A, 3A, 2A, 1A) | **Top 25** |
| **TAPPS** (6A, 5A, 4A, 3A, 2A, 1A) | **Top 10** |

---

## 🎯 Why This Matters

### Before:
- System attempted to display all 1,304 schools
- Caused Internal Server Error (template couldn't handle None ranks)
- Pages were cluttered with unranked teams

### After:
- Display shows only top-ranked teams
- Clean, focused rankings view
- No errors with unranked teams
- Matches traditional ranking format (top 25/top 10)

---

## 💾 What's Tracked Behind the Scenes

**Important:** The system still tracks **all 1,304 schools** in the backend for:

✅ **Record Calculation**
- All games are tracked in database (686+ games)
- Records calculated for any team that plays
- Win-loss records updated in real-time

✅ **District Assignments**
- All 1,019 UIL schools have districts
- All 285 TAPPS schools have districts
- 100% district coverage maintained

✅ **Statistics Tracking**
- PPG (Points Per Game)
- Opponent PPG
- Game counts
- All stats preserved in rankings.json

✅ **Monday Ranking Calculations**
- Efficiency ratings calculated for all teams with games
- Multi-source ranking integration (Calculated, GASO, MaxPreps, TABC)
- Teams can move in/out of top 25/10 based on performance

---

## 🔍 How Rankings Are Determined

### Weekly Update Process (Every Monday 6 AM):

1. **Scrape MaxPreps** - Get latest MaxPreps rankings
2. **Calculate Rankings** - Compute efficiency ratings from all games
3. **Integrate GASO** - Add GASO pre-season rankings (130 teams)
4. **Scrape TABC** - Get TABC rankings as backup
5. **Merge All Sources** - Priority: Calculated > GASO > MaxPreps > TABC
6. **Assign Ranks** - Top teams get ranks 1-25 (UIL) or 1-10 (TAPPS)
7. **Update Records** - Match game data to team records
8. **Display Top Teams** - Website shows only ranked teams

### What Gets Displayed:

**UIL Classifications:**
- Rank 1-25 (if that many teams have been ranked)
- Currently: Some classes have fewer (e.g., 2A has 1 team ranked)
- As season progresses, more teams will be ranked

**TAPPS Classifications:**
- Rank 1-10 (all have 10 teams currently)
- Fixed at top 10 per classification

---

## 📈 Current Status

Based on latest rankings.json (2025-11-20 10:17 AM):

| Classification | Teams Ranked | Teams Displayed |
|----------------|--------------|-----------------|
| 6A (AAAAAA) | 15 | 15 (max 25) |
| 5A (AAAAA) | 11 | 11 (max 25) |
| 4A (AAAA) | 8 | 8 (max 25) |
| 3A (AAA) | 12 | 12 (max 25) |
| 2A (AA) | 1 | 1 (max 25) |
| 1A (A) | 6 | 6 (max 25) |
| TAPPS 6A | 10 | 10 ✅ |
| TAPPS 5A | 10 | 10 ✅ |
| TAPPS 4A | 10 | 10 ✅ |
| TAPPS 3A | 10 | 10 ✅ |
| TAPPS 2A | 10 | 10 ✅ |
| TAPPS 1A | 10 | 10 ✅ |

**Note:** Some UIL classifications have fewer than 25 teams ranked because:
- Early in the season (more teams will be ranked as games are played)
- Ranking sources (TABC, GASO, MaxPreps) may not have full 25 yet
- As more games are played and submitted, rankings will expand

---

## ✅ What You'll See on the Website

### Ranking Pages Display:
1. **Rank Column** - Shows 1, 2, 3, ... (no dashes, only actual ranks)
2. **Team Name** - School name
3. **District** - District number
4. **Record** - Win-loss record (if games played)
5. **PPG** - Points per game (if games played)
6. **Opp PPG** - Opponent points per game (if games played)
7. **Margin** - Point differential (if games played)

### Example 6A Page:
```
Rank  Team                   District  Record  PPG   Opp PPG  Margin
1     Steele                 29        3-0     73.7  57.0     +16.7
2     Little Elm             5         2-1     76.3  72.7     +3.7
3     North Crowley          3         —       —     —        —
...
15    [15th ranked team]     ...       ...     ...   ...      ...
```

---

## 🔄 How Teams Move Up/Down

### Teams Can Enter Top 25/10:
- Win games (improves calculated efficiency rating)
- Get ranked by GASO, MaxPreps, or TABC
- Have strong performance metrics

### Teams Can Drop Out of Top 25/10:
- Lose games (decreases efficiency rating)
- Other teams perform better
- Removed from external ranking sources

### Records Update In Real-Time:
- Coach submits box score via website form
- Record immediately updates in rankings.json
- Ranking position may change on next Monday update

---

## 🎓 Benefits of This Approach

### For Users:
✅ Clean, focused view of top teams
✅ No clutter from unranked teams
✅ Traditional ranking format (matches TABC, MaxPreps style)
✅ Easy to see who's ranked and who's not

### For System:
✅ Tracks all 1,304 schools for comprehensive data
✅ Any team can be ranked based on performance
✅ Full district coverage for scheduling purposes
✅ Complete game record tracking

### For Coaches:
✅ Submit any game for any team
✅ Records tracked even if team isn't ranked
✅ Team can move into rankings with good performance
✅ Historical data preserved

---

## 🚀 Deployment Status

**Latest Commit:** `995981e`
**Pushed to Railway:** Just now
**Expected Live:** 2-5 minutes

### After Deployment:
1. Hard refresh browser (`Cmd+Shift+R` or `Ctrl+Shift+R`)
2. Visit any ranking page
3. You should see:
   - UIL pages: Top 25 ranked teams (or fewer if not all ranked yet)
   - TAPPS pages: Top 10 ranked teams
   - No unranked teams
   - No empty/dash ranks

---

## 📝 Summary

**Backend:** Tracks all 1,304 schools with records, districts, and stats
**Frontend:** Displays only top 25 (UIL) or top 10 (TAPPS) ranked teams
**Updates:** Monday rankings can promote/demote teams into/out of top spots
**Real-time:** Form submissions update records immediately, rankings update Monday

This gives you the best of both worlds:
- Comprehensive tracking for all schools
- Clean, professional display of top rankings
