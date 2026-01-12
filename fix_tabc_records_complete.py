"""
Complete fix for rankings - use TABC as the authoritative source
Ensure exactly 25 UIL teams per classification with correct TABC records
"""
import json
from datetime import datetime

def fix_rankings_complete():
    # Load TABC rankings
    with open('tabc_rankings_scraped.json', 'r') as f:
        tabc_data = json.load(f)

    # Load current rankings
    with open('data/rankings.json', 'r') as f:
        rankings = json.load(f)

    print("="*90)
    print("FIXING RANKINGS - USING TABC AS AUTHORITATIVE SOURCE")
    print("="*90)

    fixes_applied = 0

    # Process each UIL classification
    for classification_key in ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']:
        print(f"\n{classification_key}:")

        tabc_teams = tabc_data['uil'][classification_key]
        current_teams = rankings['uil'][classification_key]

        # Create map of current teams with their game stats
        current_map = {team['team_name']: team for team in current_teams}

        # Build new list from TABC rankings (top 25)
        new_teams = []
        for tabc_team in tabc_teams[:25]:  # Only top 25
            team_name = tabc_team['team_name']

            # Start with TABC data
            new_team = {
                'rank': tabc_team['rank'],
                'team_name': team_name,
                'wins': tabc_team['wins'],
                'losses': tabc_team['losses'],
                'record': f"{tabc_team['wins']}-{tabc_team['losses']}",
                'classification': classification_key,
                'tabc_rank': tabc_team['rank'],
                'maxpreps_rank': None,
                'calc_rank': None,
                'consensus_rank': float(tabc_team['rank'])
            }

            # If team exists in current rankings, preserve game stats and maxpreps rank
            if team_name in current_map:
                existing = current_map[team_name]
                new_team['maxpreps_rank'] = existing.get('maxpreps_rank')
                new_team['games'] = existing.get('games', 0)
                new_team['ppg'] = existing.get('ppg', 0)
                new_team['opp_ppg'] = existing.get('opp_ppg', 0)
                new_team['net_rating'] = existing.get('net_rating', 0)
                new_team['adj_offensive_eff'] = existing.get('adj_offensive_eff', 0)
                new_team['adj_defensive_eff'] = existing.get('adj_defensive_eff', 0)

                # Check if record changed
                if existing['wins'] != tabc_team['wins'] or existing['losses'] != tabc_team['losses']:
                    print(f"  ✓ {team_name}: {existing['wins']}-{existing['losses']} → {tabc_team['wins']}-{tabc_team['losses']}")
                    fixes_applied += 1
            else:
                # New team from TABC
                new_team['games'] = 0
                new_team['ppg'] = 0
                new_team['opp_ppg'] = 0
                new_team['net_rating'] = 0
                new_team['adj_offensive_eff'] = 0
                new_team['adj_defensive_eff'] = 0
                print(f"  + {team_name} ({tabc_team['wins']}-{tabc_team['losses']})")
                fixes_applied += 1

            new_teams.append(new_team)

        # Check for removed teams
        new_team_names = {t['team_name'] for t in new_teams}
        for team in current_teams:
            if team['team_name'] not in new_team_names:
                print(f"  - Removed {team['team_name']} (not in TABC top 25)")
                fixes_applied += 1

        # Replace classification teams
        rankings['uil'][classification_key] = new_teams

        print(f"  Final count: {len(new_teams)} teams")

    # Update metadata
    rankings['last_updated'] = datetime.now().isoformat()
    rankings['complete_stats'] = True
    rankings['teams_with_stats'] = sum(
        1 for c in ['uil', 'private']
        for cl, teams in rankings[c].items()
        for t in teams if t.get('games', 0) > 0
    )

    print("\n" + "="*90)
    print(f"SUMMARY: {fixes_applied} changes applied")
    print("="*90)

    # Verify counts
    print("\nVerifying team counts...")
    for category in ['uil', 'private']:
        expected = 25 if category == 'uil' else 10
        for classification, teams in rankings[category].items():
            status = "✓" if len(teams) == expected else "✗ WRONG COUNT"
            print(f"  {status} {category.upper()} {classification}: {len(teams)}/{expected} teams")

    # Save fixed rankings
    with open('data/rankings.json', 'w') as f:
        json.dump(rankings, f, indent=2)

    print("\n" + "="*90)
    print("✓ Fixed rankings saved to data/rankings.json")
    print("="*90)

    return rankings

if __name__ == "__main__":
    fix_rankings_complete()
