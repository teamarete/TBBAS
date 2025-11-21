# TBBAS Ranking System Analysis

## Current State (As of 2025-11-19)

### ✅ What's Working

#### 1. **Complete District Coverage** - 100% ✓
- **UIL**: 150/150 teams (25 per classification: 6A, 5A, 4A, 3A, 2A, 1A)
- **TAPPS**: 60/60 teams (10 per classification: 6A, 5A, 4A, 3A, 2A, 1A)
- **Total**: 210 teams with complete district assignments

#### 2. **Ranking Sources Currently Integrated**
The weekly Monday update process (`scheduler.py::update_rankings()`) currently integrates:

1. **Calculated Rankings** (PRIMARY) - From box score data using KenPom-style efficiency ratings
   - Source: `ranking_calculator.py`
   - Metrics: Offensive Efficiency, Defensive Efficiency, Net Rating
   - Based on collected game data from MaxPreps, coach submissions, newspapers

2. **MaxPreps Rankings** (SECONDARY) - Scraped from MaxPreps Texas rankings
   - Source: `box_score_scraper.py::MaxPrepsBoxScoreScraper.scrape_maxpreps_rankings()`
   - Both UIL and TAPPS classifications

3. **TABC Rankings** (BACKUP) - Official TABC Hoops rankings
   - Source: `scraper.py::TABCScraper`
   - UIL: https://tabchoops.org/uil-boys-rankings/
   - Private: https://tabchoops.org/private-school-boys-rankings/

**Priority Order**: Calculated > MaxPreps > TABC

#### 3. **Data Collection Working**
- **Daily**: Box scores from MaxPreps, newspapers, coach submissions
- **Weekly**: Rankings from all sources merged intelligently
- **Data Preservation**: Stats and districts preserved through updates

### ⚠️ What's Missing - Your Requirements

You requested rankings based on:
1. ✅ **TABC Rankings** - Currently integrated
2. ❌ **KenPom Ratings** - NOT currently integrated (but we have KenPom-STYLE calculations)
3. ❌ **GASO Rankings** - Mentioned in code comments but NOT actually scraped
4. ✅ **MaxPrep Rankings** - Currently integrated
5. ✅ **Records** - Currently integrated from box scores and coach submissions
6. ✅ **Stats** - Currently integrated (PPG, Opp PPG, efficiency ratings)

### 🔴 Critical Issue: Limited Team Coverage

**Current Coverage**: Only **TOP 25** UIL teams and **TOP 10** TAPPS teams per classification

**Your Requirement**: "Include **ALL** Schools in the UIL for each Classification and all the TAPPS/SPC Schools"

#### Current Limitations:

**scraper.py (TABC)**:
```python
rankings[class_code] = teams[:25]  # Top 25 UIL
private_rankings[class_code] = teams[:10]  # Top 10 TAPPS
```

**ranking_calculator.py**:
```python
all_rankings['uil'][classification] = teams[:40]  # Top 40 (but only ranked teams with games)
all_rankings['private'][classification] = teams[:10]  # Top 10
```

**Problem**: TABC only publishes Top 25 (UIL) and Top 10 (TAPPS). We can't get ALL schools from TABC.

## Required Changes

### 1. Expand Team Coverage to ALL Schools

We need to get complete school lists from other sources since TABC only ranks top teams.

**Option A: Use MaxPreps State Rankings**
MaxPreps has state-wide rankings that include far more teams. We already have the scraper infrastructure.

**Option B: Create Master School Lists**
- UIL: ~1,200 schools across 6 classifications playing basketball
- TAPPS: ~300 schools across 6 classifications

**Option C: Hybrid Approach** (RECOMMENDED)
1. Start with TABC rankings for top teams (with all our stats/districts)
2. Add unranked schools from our district mappings (we have 1,885 UIL schools mapped)
3. As games are played, teams get records/stats and move into rankings

### 2. Add GASO Rankings Integration

GASO (Greater Austin Sports Online) publishes Texas high school basketball rankings.

**URL**: Likely https://www.gaso.com/ or similar

**Action Needed**:
- Research GASO's ranking page structure
- Create GASO scraper similar to TABC scraper
- Add to `scheduler.py::update_rankings()` merge process

### 3. Add Real KenPom Ratings (If Available)

**Note**: Ken Pomeroy (KenPom.com) primarily focuses on college basketball. High school KenPom-style ratings may not exist as an external source.

**Current State**: We already calculate KenPom-STYLE efficiency ratings from our box score data.

**Options**:
- Keep using our calculated efficiency ratings (already KenPom methodology)
- Research if any service provides KenPom-style ratings for TX high school basketball
- Label our current system as "KenPom-Style Efficiency Ratings" (which it is)

### 4. Enhance Ranking Merge Logic

Currently: `calculated > MaxPreps > TABC`

**Should be**: Weighted combination of all sources:
```python
def calculate_composite_ranking(team):
    """
    Composite ranking based on:
    - KenPom-Style Efficiency (40% weight)
    - TABC Ranking (25% weight)
    - GASO Ranking (20% weight)
    - MaxPreps Ranking (15% weight)
    - Records/Stats bonus
    """
```

## Immediate Action Plan

### Phase 1: Expand School Coverage ✓ READY TO IMPLEMENT
1. Load all schools from our district mappings (1,885 UIL + ~250 TAPPS)
2. Initialize unranked teams with districts but no rank
3. As games are played, teams earn rankings based on performance
4. Merge with TABC top 25/10 for initial rankings

### Phase 2: Add GASO Rankings (Research Needed)
1. Identify GASO ranking URLs
2. Analyze HTML structure
3. Create GASO scraper
4. Integrate into merge process

### Phase 3: Refine Ranking Algorithm
1. Implement weighted composite ranking
2. Add strength of schedule calculations
3. Add margin of victory considerations
4. Add home/away/neutral factors

## Current Ranking Sources - Detailed

### 1. TABC Rankings (Currently Working)
- **UIL**: Top 25 per classification
- **TAPPS**: Top 10 per classification
- **Updated**: Weekly (official TABC updates)
- **Quality**: High (official Texas Association of Basketball Coaches)

### 2. Calculated Rankings (Currently Working)
- **Coverage**: All teams with game data
- **Metrics**:
  - Offensive Efficiency (points per 100 possessions)
  - Defensive Efficiency (points allowed per 100 possessions)
  - Net Rating (Off Eff - Def Eff)
- **Updated**: Daily as games are added
- **Quality**: High (pure data-driven)

### 3. MaxPreps Rankings (Currently Working)
- **Coverage**: State-wide rankings (more than TABC)
- **Updated**: Scraped weekly
- **Quality**: Medium (algorithm-based, not human poll)

### 4. GASO Rankings (NOT WORKING - Needs Implementation)
- **Status**: Mentioned in code but not actually scraped
- **Action**: Need to add scraper

### 5. Records & Stats (Currently Working)
- **Sources**:
  - MaxPreps box scores (automated scraping)
  - Coach submissions (via web form)
  - Texas newspaper reports (planned)
- **Updated**: Daily
- **Quality**: High (primary source data)

## Files Involved

### Scrapers
- `scraper.py` - TABC rankings scraper
- `box_score_scraper.py` - MaxPreps box scores & rankings scraper
- **MISSING**: `gaso_scraper.py` - GASO rankings scraper

### Ranking Logic
- `ranking_calculator.py` - KenPom-style efficiency calculations
- `scheduler.py::merge_rankings()` - Combines all ranking sources

### Data Files
- `data/rankings.json` - Current rankings (210 teams)
- `manual_district_mappings.py` - UIL school districts (1,885 schools)
- `tapps_district_mappings.py` - TAPPS school districts (~250 schools)

## Recommendations

### Short Term (1-2 weeks)
1. ✅ **Expand coverage to all UIL/TAPPS schools with districts** - Use our district mappings
2. ❌ **Add GASO scraper** - Research and implement
3. ✅ **Document current ranking methodology** - Make transparent to users

### Medium Term (1 month)
1. Implement weighted composite rankings
2. Add strength of schedule metrics
3. Add historical rankings tracking

### Long Term (Season-long)
1. Machine learning model for predictions
2. Playoff probability calculations
3. Power rankings vs poll rankings distinction

## Summary

**Current State**: We have a solid foundation with TABC rankings, calculated efficiency ratings, MaxPreps integration, and 100% district coverage for top-ranked teams.

**Gap**: We're only tracking 210 teams (top 25/10) instead of ALL 2,000+ schools in Texas high school basketball.

**Solution**: Use our comprehensive district mappings to include all schools, initialize them with districts but no ranks, and let them earn rankings through game performance.

**Missing Source**: GASO rankings need to be researched and integrated.

**Recommendation**: Focus first on expanding coverage to all schools, then add GASO, then refine the composite ranking algorithm.
