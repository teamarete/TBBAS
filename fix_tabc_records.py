"""
Fix incorrect records in rankings.json using TABC as source of truth

Issues to fix:
1. UIL 6A: Cypress Springs (2-0 → 19-4), Plano East (3-4 → no TABC rank, remove or keep with DB stats), Tompkins (5-4 → no TABC rank)
2. UIL 5A: West Brook duplicate (remove "West Brook", keep "Bmt West Brook" 18-3)
3. UIL 4A: Liberty (wrong record), Lubbock Liberty (17-4 from TABC)
4. TAPPS 5A: Trinity Christian (wrong record)
"""
import json
from datetime import datetime

def fix_records():
    # Load TABC rankings
    with open('tabc_rankings_scraped.json', 'r') as f:
        tabc_data = json.load(f)

    # Load current rankings
    with open('data/rankings.json', 'r') as f:
        rankings = json.load(f)

    print("="*90)
    print("FIXING INCORRECT RECORDS USING TABC AS SOURCE OF TRUTH")
    print("="*90)

    fixes_applied = 0

    # Fix UIL 6A: Cypress Springs
    print("\nUIL 6A Fixes:")
    for team in rankings['uil']['AAAAAA']:
        if team['team_name'] == 'Cypress Springs':
            # Find in TABC
            tabc_team = next((t for t in tabc_data['uil']['AAAAAA'] if t['team_name'] == 'Cypress Springs'), None)
            if tabc_team:
                print(f"  ✓ Cypress Springs: {team['wins']}-{team['losses']} → {tabc_team['wins']}-{tabc_team['losses']}")
                team['wins'] = tabc_team['wins']
                team['losses'] = tabc_team['losses']
                team['record'] = f"{tabc_team['wins']}-{tabc_team['losses']}"
                team['tabc_rank'] = tabc_team['rank']
                fixes_applied += 1

    # Fix UIL 5A: Remove duplicate West Brook, keep Bmt West Brook
    print("\nUIL 5A Fixes:")
    teams_5a = rankings['uil']['AAAAA']
    to_remove = None
    for i, team in enumerate(teams_5a):
        if team['team_name'] == 'West Brook' and team.get('tabc_rank') is None:
            print(f"  ✓ Removing duplicate 'West Brook' (8-1, no TABC rank)")
            to_remove = i
            break

    if to_remove is not None:
        teams_5a.pop(to_remove)
        # Re-rank
        for i, team in enumerate(teams_5a, 1):
            team['rank'] = i
        fixes_applied += 1

    # Verify Bmt West Brook has correct record
    for team in teams_5a:
        if team['team_name'] == 'Bmt West Brook':
            tabc_team = next((t for t in tabc_data['uil']['AAAAA'] if t['team_name'] == 'Bmt West Brook'), None)
            if tabc_team:
                if team['wins'] != tabc_team['wins'] or team['losses'] != tabc_team['losses']:
                    print(f"  ✓ Bmt West Brook: {team['wins']}-{team['losses']} → {tabc_team['wins']}-{tabc_team['losses']}")
                    team['wins'] = tabc_team['wins']
                    team['losses'] = tabc_team['losses']
                    team['record'] = f"{tabc_team['wins']}-{tabc_team['losses']}"
                    fixes_applied += 1

    # Fix UIL 4A: Lubbock Liberty
    print("\nUIL 4A Fixes:")
    for team in rankings['uil']['AAAA']:
        if team['team_name'] == 'Lubbock Liberty':
            tabc_team = next((t for t in tabc_data['uil']['AAAA'] if t['team_name'] == 'Lubbock Liberty'), None)
            if tabc_team:
                print(f"  ✓ Lubbock Liberty: {team['wins']}-{team['losses']} → {tabc_team['wins']}-{tabc_team['losses']}")
                team['wins'] = tabc_team['wins']
                team['losses'] = tabc_team['losses']
                team['record'] = f"{tabc_team['wins']}-{tabc_team['losses']}"
                if team.get('tabc_rank') != tabc_team['rank']:
                    team['tabc_rank'] = tabc_team['rank']
                fixes_applied += 1

        # Remove "Liberty" if it exists (wrong team)
        elif team['team_name'] == 'Liberty' and team.get('wins') == 32:
            print(f"  ⚠ Found Liberty with incorrect record 32-30 - needs manual review")

    # Check if Liberty exists and handle it
    liberty_idx = None
    for i, team in enumerate(rankings['uil']['AAAA']):
        if team['team_name'] == 'Liberty' and team.get('wins', 0) > 25:
            liberty_idx = i
            break

    if liberty_idx is not None:
        print(f"  ✓ Removing Liberty (32-30) - appears to be duplicate/wrong team")
        rankings['uil']['AAAA'].pop(liberty_idx)
        # Re-rank
        for i, team in enumerate(rankings['uil']['AAAA'], 1):
            team['rank'] = i
        fixes_applied += 1

    # Fix TAPPS: Trinity Christian (need to check if it exists in TABC TAPPS data)
    print("\nTAPPS Fixes:")
    # Check if TABC has TAPPS 5A data
    if 'TAPPS_5A' in tabc_data.get('private', {}):
        for team in rankings['private'].get('TAPPS_5A', []):
            if 'Trinity Christian' in team['team_name']:
                tabc_team = next((t for t in tabc_data['private']['TAPPS_5A'] if 'Trinity Christian' in t['team_name']), None)
                if tabc_team:
                    print(f"  ✓ {team['team_name']}: {team['wins']}-{team['losses']} → {tabc_team['wins']}-{tabc_team['losses']}")
                    team['wins'] = tabc_team['wins']
                    team['losses'] = tabc_team['losses']
                    team['record'] = f"{tabc_team['wins']}-{tabc_team['losses']}"
                    fixes_applied += 1
                else:
                    print(f"  ⚠ Trinity Christian found but no TABC record available")

    # Add missing teams from TABC
    print("\nAdding missing teams from TABC:")

    # Check UIL 5A
    tabc_5a_names = {t['team_name'] for t in tabc_data['uil']['AAAAA']}
    rankings_5a_names = {t['team_name'] for t in rankings['uil']['AAAAA']}
    missing_5a = tabc_5a_names - rankings_5a_names

    if missing_5a:
        print(f"  UIL 5A missing: {missing_5a}")
        for missing_name in missing_5a:
            tabc_team = next(t for t in tabc_data['uil']['AAAAA'] if t['team_name'] == missing_name)
            new_team = {
                'rank': len(rankings['uil']['AAAAA']) + 1,
                'team_name': tabc_team['team_name'],
                'wins': tabc_team['wins'],
                'losses': tabc_team['losses'],
                'record': f"{tabc_team['wins']}-{tabc_team['losses']}",
                'classification': 'AAAAA',
                'tabc_rank': tabc_team['rank'],
                'maxpreps_rank': None,
                'calc_rank': None,
                'consensus_rank': tabc_team['rank'],
                'net_rating': 0,
                'adj_offensive_eff': 0,
                'adj_defensive_eff': 0,
                'games': 0,
                'ppg': 0,
                'opp_ppg': 0
            }
            rankings['uil']['AAAAA'].append(new_team)
            print(f"    ✓ Added {missing_name} ({tabc_team['wins']}-{tabc_team['losses']})")
            fixes_applied += 1

        # Re-sort by TABC rank
        rankings['uil']['AAAAA'].sort(key=lambda x: x.get('tabc_rank') if x.get('tabc_rank') is not None else 999)
        # Re-rank
        for i, team in enumerate(rankings['uil']['AAAAA'], 1):
            team['rank'] = i

    # Check UIL 4A
    tabc_4a_names = {t['team_name'] for t in tabc_data['uil']['AAAA']}
    rankings_4a_names = {t['team_name'] for t in rankings['uil']['AAAA']}
    missing_4a = tabc_4a_names - rankings_4a_names

    if missing_4a:
        print(f"  UIL 4A missing: {missing_4a}")
        for missing_name in missing_4a:
            tabc_team = next(t for t in tabc_data['uil']['AAAA'] if t['team_name'] == missing_name)
            new_team = {
                'rank': len(rankings['uil']['AAAA']) + 1,
                'team_name': tabc_team['team_name'],
                'wins': tabc_team['wins'],
                'losses': tabc_team['losses'],
                'record': f"{tabc_team['wins']}-{tabc_team['losses']}",
                'classification': 'AAAA',
                'tabc_rank': tabc_team['rank'],
                'maxpreps_rank': None,
                'calc_rank': None,
                'consensus_rank': tabc_team['rank'],
                'net_rating': 0,
                'adj_offensive_eff': 0,
                'adj_defensive_eff': 0,
                'games': 0,
                'ppg': 0,
                'opp_ppg': 0
            }
            rankings['uil']['AAAA'].append(new_team)
            print(f"    ✓ Added {missing_name} ({tabc_team['wins']}-{tabc_team['losses']})")
            fixes_applied += 1

        # Re-sort by TABC rank
        rankings['uil']['AAAA'].sort(key=lambda x: x.get('tabc_rank') if x.get('tabc_rank') is not None else 999)
        # Re-rank
        for i, team in enumerate(rankings['uil']['AAAA'], 1):
            team['rank'] = i

    # Update metadata
    rankings['last_updated'] = datetime.now().isoformat()

    print("\n" + "="*90)
    print(f"SUMMARY: {fixes_applied} fixes applied")
    print("="*90)

    # Verify counts
    print("\nVerifying team counts...")
    for category in ['uil', 'private']:
        expected = 25 if category == 'uil' else 10
        for classification, teams in rankings[category].items():
            status = "✓" if len(teams) == expected else "⚠ WRONG COUNT"
            print(f"  {status} {category.upper()} {classification}: {len(teams)} teams")

    # Save fixed rankings
    with open('data/rankings.json', 'w') as f:
        json.dump(rankings, f, indent=2)

    print("\n" + "="*90)
    print("✓ Fixed rankings saved to data/rankings.json")
    print("="*90)

    return rankings

if __name__ == "__main__":
    fix_records()
