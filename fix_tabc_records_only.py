"""
Fix TABC records ONLY - preserve consensus rankings
Updates wins/losses from TABC but keeps the consensus ranking order
"""
import json
from datetime import datetime

def fix_tabc_records_only():
    # Load TABC rankings
    with open('tabc_rankings_scraped.json', 'r') as f:
        tabc_data = json.load(f)

    # Load current rankings (with consensus)
    with open('data/rankings.json', 'r') as f:
        rankings = json.load(f)

    print("="*90)
    print("FIXING TABC RECORDS ONLY - PRESERVING CONSENSUS RANKINGS")
    print("="*90)

    fixes_applied = 0

    # Process each UIL classification
    for classification_key in ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']:
        print(f"\n{classification_key}:")

        # Create map of TABC teams for quick lookup
        tabc_map = {team['team_name']: team for team in tabc_data['uil'][classification_key]}

        # Update records for teams that match TABC
        for team in rankings['uil'][classification_key]:
            team_name = team['team_name']

            if team_name in tabc_map:
                tabc_team = tabc_map[team_name]

                # Check if record needs updating
                if team['wins'] != tabc_team['wins'] or team['losses'] != tabc_team['losses']:
                    print(f"  ✓ {team_name}: {team['wins']}-{team['losses']} → {tabc_team['wins']}-{tabc_team['losses']}")
                    team['wins'] = tabc_team['wins']
                    team['losses'] = tabc_team['losses']
                    team['record'] = f"{tabc_team['wins']}-{tabc_team['losses']}"
                    team['tabc_rank'] = tabc_team['rank']
                    fixes_applied += 1
            else:
                # Team in our rankings but not in TABC top 25
                # Keep the team but note that it doesn't have a TABC rank
                if team.get('tabc_rank') is not None:
                    print(f"  ⚠ {team_name}: Not in TABC top 25 anymore (was rank {team.get('tabc_rank')})")

    # Process TAPPS classifications
    for classification_key in ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']:
        if classification_key not in tabc_data.get('private', {}):
            continue

        print(f"\n{classification_key}:")

        # Create map of TABC teams for quick lookup
        tabc_map = {team['team_name']: team for team in tabc_data['private'][classification_key]}

        # Update records for teams that match TABC
        for team in rankings['private'].get(classification_key, []):
            team_name = team['team_name']

            if team_name in tabc_map:
                tabc_team = tabc_map[team_name]

                # Check if record needs updating
                if team['wins'] != tabc_team['wins'] or team['losses'] != tabc_team['losses']:
                    print(f"  ✓ {team_name}: {team['wins']}-{team['losses']} → {tabc_team['wins']}-{tabc_team['losses']}")
                    team['wins'] = tabc_team['wins']
                    team['losses'] = tabc_team['losses']
                    team['record'] = f"{tabc_team['wins']}-{tabc_team['losses']}"
                    team['tabc_rank'] = tabc_team['rank']
                    fixes_applied += 1

    # Update metadata
    rankings['last_updated'] = datetime.now().isoformat()
    rankings['source'] = 'merged_tabc_maxpreps_calculated_with_tabc_records'

    print("\n" + "="*90)
    print(f"SUMMARY: {fixes_applied} record fixes applied")
    print("="*90)

    # Verify counts
    print("\nVerifying team counts...")
    for category in ['uil', 'private']:
        expected = 25 if category == 'uil' else 10
        for classification, teams in rankings[category].items():
            status = "✓" if len(teams) == expected else "⚠ WRONG COUNT"
            print(f"  {status} {category.upper()} {classification}: {len(teams)}/{expected} teams")

    print("\nNOTE: Rankings order preserved from consensus (TABC + MaxPreps + Calculated)")
    print("      Only win-loss records updated from TABC")

    # Save fixed rankings
    with open('data/rankings.json', 'w') as f:
        json.dump(rankings, f, indent=2)

    print("\n" + "="*90)
    print("✓ Fixed rankings saved to data/rankings.json")
    print("="*90)

    return rankings

if __name__ == "__main__":
    fix_tabc_records_only()
