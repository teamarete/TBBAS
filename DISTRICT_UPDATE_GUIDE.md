# District Update Guide

## Quick Start

Run this simple command to update districts for schools that didn't auto-match:

```bash
python update_missing_districts.py
```

## How It Works

The script will:
1. **Show you all schools missing districts** (both UIL and TAPPS)
2. **Let you paste district assignments** in a simple format
3. **Save the updates** to the mapping files
4. **Apply districts** to rankings.json automatically

## Example Usage

```
$ python update_missing_districts.py

================================================================================
DISTRICT UPDATER - Schools Missing Districts
================================================================================

Found 12 UIL schools and 60 TAPPS schools missing districts

================================================================================
UIL SCHOOLS MISSING DISTRICTS
================================================================================
  AAAAAA   | Rank  3 | Katy Seven Lakes                         (0-0)
  AAAAAA   | Rank  4 | SA Brennan                               (0-0)
  ...

================================================================================
TAPPS SCHOOLS MISSING DISTRICTS
================================================================================
  TAPPS_6A     | Rank  1 | Dallas Parish Episcopal                  (0-0)
  TAPPS_6A     | Rank  2 | Addison Greenhill School                 (0-0)
  ...

================================================================================
UPDATE DISTRICTS
================================================================================

Format: TeamName|Classification|District
Example: Duncanville|AAAAAA|11
         Dallas Parish Episcopal|TAPPS_6A|1

Paste your updates below (one per line). Press ENTER twice when done:
--------------------------------------------------------------------------------
```

## Paste Your Updates

Just copy/paste lines in this format:

```
Katy Seven Lakes|AAAAAA|1
SA Brennan|AAAAAA|27
Dallas Parish Episcopal|TAPPS_6A|1
Houston Christian|TAPPS_6A|2
```

Press ENTER twice when done, then type `y` to save.

## Classification Codes

### UIL
- 6A = `AAAAAA`
- 5A = `AAAAA`
- 4A = `AAAA`
- 3A = `AAA`
- 2A = `AA`
- 1A = `A`

### TAPPS
- 6A = `TAPPS_6A`
- 5A = `TAPPS_5A`
- 4A = `TAPPS_4A`
- 3A = `TAPPS_3A`
- 2A = `TAPPS_2A`
- 1A = `TAPPS_1A`

## What Happens

The script updates:
- **UIL schools**: Adds to `manual_district_mappings.py`
- **TAPPS schools**: Updates `tapps_district_mappings.py`
- **Rankings**: Automatically runs `update_rankings_with_records.py`

## Verification

After updating, you'll see:
```
Before: 12 UIL + 60 TAPPS missing
After:  0 UIL + 0 TAPPS missing
Fixed:  12 UIL + 60 TAPPS
```

## Tips

1. **Copy from PDF**: Open the UIL/TAPPS PDF and copy school names exactly
2. **Use Text Editor**: Paste into a text editor first to prepare your list
3. **Format Template**: Create your list like:
   ```
   SchoolName|Classification|District
   ```
4. **Batch Update**: You can update many schools at once
5. **Run Again**: If you miss any, just run the script again

## Data Sources

- **UIL Districts**: UIL Alignment 2024-26
- **TAPPS Districts**: Pages 35-41 of https://drive.google.com/file/d/1L9zFxC2Sd77Th6looL72ZpbihK1cM1dc/view

## Troubleshooting

**Invalid format error?**
- Make sure you're using the pipe character `|` (not comma or space)
- Check that classification matches exactly (case-sensitive)

**School not found?**
- Make sure the school name matches exactly what's in rankings
- Check the list shown by the script

**Changes not applied?**
- Run `python update_rankings_with_records.py` manually
- Check that git committed the changes

## Example Complete Session

```
$ python update_missing_districts.py

Found 12 UIL schools and 60 TAPPS schools missing districts

...shows missing schools...

Paste your updates below (one per line). Press ENTER twice when done:
--------------------------------------------------------------------------------
Katy Seven Lakes|AAAAAA|1
SA Brennan|AAAAAA|27
  ✓ UIL: Katy Seven Lakes (AAAAAA) → District 1
  ✓ UIL: SA Brennan (AAAAAA) → District 27
Dallas Parish Episcopal|TAPPS_6A|1
  ✓ TAPPS: Dallas Parish Episcopal (TAPPS_6A) → District 1

[press ENTER twice]

================================================================================
READY TO UPDATE: 2 UIL + 1 TAPPS = 3 total
================================================================================

Save these updates? (y/n): y
✓ Updated 2 UIL districts in manual_district_mappings.py
✓ Updated 1 TAPPS districts in tapps_district_mappings.py
✓ Districts successfully applied to rankings!

Before: 12 UIL + 60 TAPPS missing
After:  10 UIL + 59 TAPPS missing
Fixed:  2 UIL + 1 TAPPS
```

Done! Your districts are now in the rankings.
