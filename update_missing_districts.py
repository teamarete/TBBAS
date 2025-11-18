#!/usr/bin/env python3
"""
Simple District Updater for UIL and TAPPS Schools

Updates manual_district_mappings.py and tapps_district_mappings.py
for schools that didn't auto-match to districts.

Usage:
    python update_missing_districts.py
"""

import json
from pathlib import Path


def load_current_rankings():
    """Load rankings to see which schools are missing districts"""
    with open('data/rankings.json', 'r') as f:
        return json.load(f)


def find_missing_districts():
    """Find all schools without districts"""
    rankings = load_current_rankings()

    missing_uil = []
    missing_tapps = []

    # Check UIL schools
    for classification, teams in rankings.get('uil', {}).items():
        for team in teams:
            if not team.get('district'):
                missing_uil.append({
                    'team_name': team['team_name'],
                    'classification': classification,
                    'rank': team.get('rank'),
                    'record': f"{team.get('wins') or 0}-{team.get('losses') or 0}"
                })

    # Check TAPPS schools
    for classification, teams in rankings.get('private', {}).items():
        for team in teams:
            if not team.get('district'):
                missing_tapps.append({
                    'team_name': team['team_name'],
                    'classification': classification,
                    'rank': team.get('rank'),
                    'record': f"{team.get('wins') or 0}-{team.get('losses') or 0}"
                })

    return missing_uil, missing_tapps


def update_uil_districts(updates):
    """Update manual_district_mappings.py with UIL districts"""
    file_path = Path('manual_district_mappings.py')

    # Read current file
    with open(file_path, 'r') as f:
        content = f.read()

    # Find the MANUAL_DISTRICTS section
    lines = content.split('\n')
    new_lines = []

    # Find where to insert new mappings (before the closing brace)
    insert_index = None
    for i, line in enumerate(lines):
        if line.strip() == '}' and 'MANUAL_DISTRICTS' in '\n'.join(lines[:i]):
            insert_index = i
            break

    if insert_index:
        # Add new mappings before the closing brace
        for (team_name, classification), district in updates.items():
            # Check if mapping already exists
            mapping_line = f"    ('{team_name}', '{classification}'): '{district}',"
            if mapping_line not in content:
                new_lines.append(f"\n    # Added via update script")
                new_lines.append(f"    ('{team_name}', '{classification}'): '{district}',")

        # Insert new lines
        lines = lines[:insert_index] + new_lines + lines[insert_index:]

        # Write back
        with open(file_path, 'w') as f:
            f.write('\n'.join(lines))

        print(f"✓ Updated {len(updates)} UIL districts in {file_path}")
    else:
        print("Error: Could not find MANUAL_DISTRICTS in manual_district_mappings.py")


def update_tapps_districts(updates):
    """Update tapps_district_mappings.py with TAPPS districts"""
    file_path = Path('tapps_district_mappings.py')

    # Read current file
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Update existing mappings
    new_lines = []
    updated_count = 0

    for line in lines:
        updated = False
        for (team_name, classification), district in updates.items():
            if f"('{team_name}', '{classification}')" in line and ': None' in line:
                # Replace None with district
                indent = len(line) - len(line.lstrip())
                new_line = f"{' ' * indent}('{team_name}', '{classification}'): '{district}',\n"
                new_lines.append(new_line)
                updated = True
                updated_count += 1
                break

        if not updated:
            new_lines.append(line)

    # Write back
    with open(file_path, 'w') as f:
        f.writelines(new_lines)

    print(f"✓ Updated {updated_count} TAPPS districts in {file_path}")


def main():
    print("\n" + "=" * 80)
    print("DISTRICT UPDATER - Schools Missing Districts")
    print("=" * 80)

    # Find missing
    missing_uil, missing_tapps = find_missing_districts()

    print(f"\nFound {len(missing_uil)} UIL schools and {len(missing_tapps)} TAPPS schools missing districts")

    if not missing_uil and not missing_tapps:
        print("\n✓ All schools have districts! Nothing to update.")
        return

    # Show what's missing
    if missing_uil:
        print("\n" + "=" * 80)
        print("UIL SCHOOLS MISSING DISTRICTS")
        print("=" * 80)
        for item in missing_uil:
            print(f"  {item['classification']:8s} | Rank {item['rank']:2d} | {item['team_name']:40s} ({item['record']})")

    if missing_tapps:
        print("\n" + "=" * 80)
        print("TAPPS SCHOOLS MISSING DISTRICTS")
        print("=" * 80)
        for item in missing_tapps:
            print(f"  {item['classification']:12s} | Rank {item['rank']:2d} | {item['team_name']:40s} ({item['record']})")

    print("\n" + "=" * 80)
    print("UPDATE DISTRICTS")
    print("=" * 80)
    print("\nFormat: TeamName|Classification|District")
    print("Example: Duncanville|AAAAAA|11")
    print("         Dallas Parish Episcopal|TAPPS_6A|1")
    print("\nPaste your updates below (one per line). Press ENTER twice when done:")
    print("-" * 80)

    updates_uil = {}
    updates_tapps = {}

    # Collect input
    empty_count = 0
    while True:
        line = input().strip()

        if not line:
            empty_count += 1
            if empty_count >= 2:  # Two empty lines to finish
                break
            continue
        else:
            empty_count = 0

        # Parse the line
        parts = [p.strip() for p in line.split('|')]
        if len(parts) != 3:
            print(f"  ✗ Invalid format: {line}")
            print(f"     Expected: TeamName|Classification|District")
            continue

        team_name, classification, district = parts

        # Determine if UIL or TAPPS
        if classification.startswith('TAPPS_'):
            updates_tapps[(team_name, classification)] = district
            print(f"  ✓ TAPPS: {team_name} ({classification}) → District {district}")
        else:
            updates_uil[(team_name, classification)] = district
            print(f"  ✓ UIL: {team_name} ({classification}) → District {district}")

    # Summary
    total_updates = len(updates_uil) + len(updates_tapps)
    if total_updates == 0:
        print("\nNo updates entered.")
        return

    print("\n" + "=" * 80)
    print(f"READY TO UPDATE: {len(updates_uil)} UIL + {len(updates_tapps)} TAPPS = {total_updates} total")
    print("=" * 80)

    # Confirm
    confirm = input("\nSave these updates? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Updates cancelled.")
        return

    # Save updates
    if updates_uil:
        update_uil_districts(updates_uil)

    if updates_tapps:
        update_tapps_districts(updates_tapps)

    # Apply to rankings
    print("\n" + "=" * 80)
    print("Applying districts to rankings...")
    print("=" * 80)

    try:
        from update_rankings_with_records import update_rankings_with_records
        from app import app

        with app.app_context():
            result = update_rankings_with_records()

        print("\n✓ Districts successfully applied to rankings!")

        # Show updated counts
        missing_uil_after, missing_tapps_after = find_missing_districts()
        print(f"\nBefore: {len(missing_uil)} UIL + {len(missing_tapps)} TAPPS missing")
        print(f"After:  {len(missing_uil_after)} UIL + {len(missing_tapps_after)} TAPPS missing")
        print(f"Fixed:  {(len(missing_uil) - len(missing_uil_after))} UIL + {(len(missing_tapps) - len(missing_tapps_after))} TAPPS")

    except Exception as e:
        print(f"\nError applying to rankings: {e}")
        print("You can manually run: python update_rankings_with_records.py")


if __name__ == "__main__":
    main()
