# TAPPS District Mapping Guide

## Overview
This guide explains how to add TAPPS district information to the rankings system.

## Current Status
- **TAPPS Data File**: `tapps_district_mappings.py`
- **Schools Loaded**: 60 schools (10 per classification)
- **Districts Assigned**: 0 (all need to be filled in)

## Data Source
TAPPS Alignment 2024-2026 PDF (pages 35-41)
- Link: https://drive.google.com/file/d/1L9zFxC2Sd77Th6looL72ZpbihK1cM1dc/view
- Pages 35-41 contain Boys Basketball alignments

## How to Add District Data

### Option 1: Manual Entry (Quickest)

1. **Download the PDF** from the Google Drive link above
2. **Open** `tapps_district_mappings.py` in your editor
3. **Navigate to pages 35-41** in the PDF
4. **For each school**, update the district number:

```python
# Before (None means no district assigned):
('Dallas Parish Episcopal', 'TAPPS_6A'): None,

# After (replace None with actual district number from PDF):
('Dallas Parish Episcopal', 'TAPPS_6A'): '1',  # District 1
```

5. **Save** the file
6. **Run** `python update_rankings_with_records.py` to apply the districts

### Option 2: Using the PDF Parser (Automated)

1. **Download the PDF** from the link above
2. **Save it** in the project root as: `TAPPS_Alignment_2024-2026.pdf`
3. **Install pdfplumber** if needed: `pip install pdfplumber`
4. **Run the parser**: `python tapps_data_fetcher.py`
5. **Review the output** in `data/tapps_schools.json`
6. **Update** `tapps_district_mappings.py` with the parsed data

## TAPPS Classification Structure

Based on web search results:

- **6A**: District 1 through District 4
- **5A**: District 1 through District 5
- **4A**: District 1 through District 5
- **3A**: District 1 through District 5
- **2A**: District 1 through District 8
- **1A**: District 1 through District 8

## Schools Currently in Rankings

### TAPPS 6A (10 schools)
1. Dallas Parish Episcopal
2. Addison Greenhill School
3. Dallas St. Mark's School of Texas
4. Houston Christian
5. San Antonio TMI Episcopal
6. Austin St. Michael's
7. San Antonio Antonian Prep
8. Plano John Paul II
9. Dallas Bishop Lynch
10. Houston The Kinkaid School

### TAPPS 5A (10 schools)
1. Houston Second Baptist
2. Arlington Grace Prep
3. Lubbock Trinity Christian
4. Episcopal School of Dallas
5. The Woodlands Christian Academy
6. Bullard The Brook Hill School
7. Midland Christian
8. Sugar Land Fort Bend Christian Academy
9. Brownsville St. Joseph Academy
10. San Antonio St. Anthony Catholic

### TAPPS 4A (10 schools)
1. Mckinney Christian
2. Houston St. Francis
3. Lubbock Christian
4. Houston St Thomas Episcopal
5. Tyler Bishop Gorman
6. Houston Westbury
7. Midland Christian
8. San Antonio Holy Cross
9. Colleyville Covenenat Christian
10. Boerne Geneva

### TAPPS 3A (10 schools)
1. Dallas Yavneh
2. Waco Live Oak
3. Faith Academy of Marble Falls
4. Huntsville Alpha Omega
5. Abilene Christian
6. Keene Chisholm Trail
7. Fort Worth Covenant
8. Denton Calvary
9. Austin San Juan Diego
10. Rockwall Heritage

### TAPPS 2A (10 schools)
1. First Baptist Academy-Dallas
2. Holy Cross Catholic Academy-Amarillo
3. All Saints Episcopal School-Lubbock
4. O'Connell College Preparatory School-Galveston
5. Bracken Christian School-Bulverde
6. Valor Preparatory Academy-Waco
7. Ovilla Christian School
8. Calvary Baptist School-Conroe
9. Legacy Christian Academy-Beaumont
10. Victory Christian Academy-Decatur

### TAPPS 1A (10 schools)
1. Divine Savior Academy-Missouri City
2. Texhoma Christian School-Sherman
3. Heritage School-Fredericksburg
4. The Covenant Preparatory School-Kingwood
5. Harvest Christian Academy-Edinburgh
6. Macedonian Christian Academy-Alamo
7. Regents Academy-Nacogdoches
8. Founders Christian School-Spring
9. Cornerstone Christian School-San Angelo
10. Azle Christian School

## Verification

After adding districts, run:

```bash
python -c "from tapps_district_mappings import TAPPS_DISTRICTS; missing = [k for k,v in TAPPS_DISTRICTS.items() if v is None]; print(f'{len(TAPPS_DISTRICTS) - len(missing)}/{len(TAPPS_DISTRICTS)} schools have districts')"
```

## Questions?

If you encounter any issues:
1. Check that school names match exactly (case-sensitive)
2. Verify classification format (e.g., 'TAPPS_6A' not '6A')
3. District numbers should be strings (e.g., '1' not 1)
