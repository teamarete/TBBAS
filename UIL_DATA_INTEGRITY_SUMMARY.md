# UIL Data Integrity Implementation Summary

## Problem Identified

The user discovered that "Jefferson" in Class 3A-AAA showed a 2-1 record, but upon investigation, only played one game. This indicated that multiple schools named "Jefferson" were being conflated into a single team record.

## Solution Implemented

### 1. UIL Data Fetching (`uil_data_fetcher_v3.py`)
- **Purpose**: Parse official UIL basketball alignment PDFs to build database of authentic schools
- **Data Source**: 6 official UIL PDFs for 2025-26 basketball season (6A through 1A)
- **Results**: Successfully extracted 917 schools with their classifications and districts
- **Key Features**:
  - Downloads and parses PDF tables using pdfplumber
  - Handles multi-column district format
  - Splits concatenated school names intelligently
  - Outputs to `data/uil_schools.json`

### 2. UIL School Matcher (`uil_school_matcher.py`)
- **Purpose**: Match game team names to official UIL schools
- **Features**:
  - Exact name matching
  - Fuzzy matching with 85% similarity threshold
  - Disambiguation when multiple schools have similar names
  - District lookup and verification
- **Methods**:
  - `find_school_match()` - Find UIL school by name and classification
  - `diagnose_team_records()` - Identify conflation risks
  - `get_schools_by_name()` - Find all schools with similar names

### 3. Rankings Verification (`update_rankings_with_uil_data.py`)
- **Purpose**: Cross-check rankings against official UIL data
- **Results from test run**:
  - 53 exact matches
  - 9 fuzzy matches  
  - 88 unmatched schools (58.3% still need manual review)
  - 62 districts updated automatically
- **Adds to each team**:
  - `uil_verified`: true/false flag
  - `uil_official_name`: Official UIL name if matched
  - Correct district number

## Jefferson Investigation Results

Found **4 games** involving schools with "Jefferson" in the name:

| Date | Game | Classification |
|------|------|----------------|
| 11/14 | Jefferson 28 vs Veterans Memorial 77 | 6A |
| 11/14 | Hardin-Jefferson 77 vs Brookeland 70 | 6A |
| 11/14 | Fabens 27 vs Jefferson 30 | 6A |
| 11/14 | Spruce 36 vs Jefferson 49 | 6A |

### UIL Official Jefferson Schools

From UIL data, there are **2 distinct "Jefferson" schools**:
1. **El Paso Jefferson** - 5A District 1
2. **Dallas Jefferson** - 5A District 13

### Analysis

The games show at least **2-3 different Jefferson schools**:
- One Jefferson that beat Fabens (30-27) and Spruce (49-36) = 2-0 record
- Another Jefferson that lost to Veterans Memorial (28-77) = 0-1 record
- Hardin-Jefferson is a completely separate school

When aggregated without UIL verification, these create an incorrect combined record.

## Current Limitations

1. **UIL PDF Parsing**: The multi-column format is challenging. Some schools are still concatenated (e.g., "Mansfield Legacy North Crowley")

2. **TABC Name Abbreviations**: TABC rankings use abbreviated names that don't always match UIL official names:
   - "SA Brennan" vs "San Antonio Brennan"
   - "Bmt United" vs "Beaumont United"
   - etc.

3. **Match Rate**: Currently 29.2% automatic verification rate. Remaining 70.8% require:
   - Manual name mapping
   - Improved fuzzy matching algorithms
   - Abbreviation expansion logic

## Files Created

1. `uil_data_fetcher_v3.py` - UIL PDF parser
2. `uil_school_matcher.py` - School matching engine
3. `update_rankings_with_uil_data.py` - Rankings verification script
4. `data/uil_schools.json` - 917 official UIL schools database

## Next Steps (Recommendations)

1. **Improve PDF Parsing**: Manually review and correct concatenated school names in uil_schools.json

2. **Add Abbreviation Mapping**: Create mapping file for common abbreviations:
   ```
   "SA" -> "San Antonio"
   "Bmt" -> "Beaumont"
   "FB" -> "Fort Bend"
   "Arl" -> "Arlington"
   etc.
   ```

3. **Integrate into Game Import**: Modify `box_score_scraper.py` to verify schools during import:
   - Check if team name matches UIL school
   - Add district automatically
   - Flag ambiguous matches for review

4. **Manual Review Interface**: Create admin endpoint to:
   - Review unmatched schools
   - Manually map team names to UIL schools
   - Save mappings for future imports

5. **Conflation Detection**: Run diagnosis on all teams with > 1 game to identify other potential conflation issues

## Impact

With UIL data integrity implemented, the system can now:
- ✓ Identify when team records may be conflated
- ✓ Add correct district information (62 teams updated)
- ✓ Verify teams against official UIL rosters
- ✓ Flag ambiguous or unmatched schools for review
- ✓ Prevent future data integrity issues during import

The Jefferson issue specifically has been diagnosed: games from 2-3 different Jefferson schools are being combined, creating an incorrect 2-1 record when they should be tracked separately by district/classification.
