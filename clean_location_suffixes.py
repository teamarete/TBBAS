"""
Clean location suffixes from team names and merge duplicates
Ensures consistent naming across all rankings
"""
import json
import re

def strip_location_suffix(team_name):
    """Remove location suffixes like (City, TX) or (TX)"""
    cleaned = re.sub(r'\s*\([^)]*TX[^)]*\)$', '', team_name)
    return cleaned.strip()

def merge_duplicate_teams(team1, team2):
    """
    Merge two duplicate team entries, keeping the best data from each
    Priority: TABC record > MaxPreps record, more games > fewer games
    """
    # Determine which has better record data
    if team1.get('tabc_rank') and not team2.get('tabc_rank'):
        # Team1 has TABC rank, use its record
        wins = team1.get('wins', 0)
        losses = team1.get('losses', 0)
        record = team1.get('record', f"{wins}-{losses}")
        tabc_rank = team1.get('tabc_rank')
        maxpreps_rank = team2.get('maxpreps_rank') or team1.get('maxpreps_rank')
    elif team2.get('tabc_rank') and not team1.get('tabc_rank'):
        # Team2 has TABC rank, use its record
        wins = team2.get('wins', 0)
        losses = team2.get('losses', 0)
        record = team2.get('record', f"{wins}-{losses}")
        tabc_rank = team2.get('tabc_rank')
        maxpreps_rank = team1.get('maxpreps_rank') or team2.get('maxpreps_rank')
    else:
        # Both have or both don't have TABC, use the one with more wins
        if team1.get('wins', 0) >= team2.get('wins', 0):
            wins = team1.get('wins', 0)
            losses = team1.get('losses', 0)
            record = team1.get('record', f"{wins}-{losses}")
            tabc_rank = team1.get('tabc_rank')
            maxpreps_rank = team1.get('maxpreps_rank') or team2.get('maxpreps_rank')
        else:
            wins = team2.get('wins', 0)
            losses = team2.get('losses', 0)
            record = team2.get('record', f"{wins}-{losses}")
            tabc_rank = team2.get('tabc_rank')
            maxpreps_rank = team2.get('maxpreps_rank') or team1.get('maxpreps_rank')

    # Use game stats from the one with more games
    if team1.get('games', 0) >= team2.get('games', 0):
        games = team1.get('games', 0)
        ppg = team1.get('ppg', 0)
        opp_ppg = team1.get('opp_ppg', 0)
        net_rating = team1.get('net_rating', 0)
        adj_offensive_eff = team1.get('adj_offensive_eff', 0)
        adj_defensive_eff = team1.get('adj_defensive_eff', 0)
    else:
        games = team2.get('games', 0)
        ppg = team2.get('ppg', 0)
        opp_ppg = team2.get('opp_ppg', 0)
        net_rating = team2.get('net_rating', 0)
        adj_offensive_eff = team2.get('adj_offensive_eff', 0)
        adj_defensive_eff = team2.get('adj_defensive_eff', 0)

    # Merge into single team (use clean name without suffix)
    clean_name = strip_location_suffix(team1['team_name'])
    if '(' in clean_name:  # If team1 still has suffix, try team2
        clean_name = strip_location_suffix(team2['team_name'])

    merged = {
        'team_name': clean_name,
        'wins': wins,
        'losses': losses,
        'record': record,
        'classification': team1.get('classification'),
        'tabc_rank': tabc_rank,
        'maxpreps_rank': maxpreps_rank,
        'games': games,
        'ppg': ppg,
        'opp_ppg': opp_ppg,
        'net_rating': net_rating,
        'adj_offensive_eff': adj_offensive_eff,
        'adj_defensive_eff': adj_defensive_eff,
    }

    # Preserve other fields if they exist
    for key in ['rank', 'calc_rank', 'consensus_rank', 'district', 'source']:
        if key in team1:
            merged[key] = team1[key]
        elif key in team2:
            merged[key] = team2[key]

    return merged


def clean_rankings():
    """Remove location suffixes and merge duplicates"""

    # Load rankings
    with open('data/rankings.json', 'r') as f:
        rankings = json.load(f)

    print("="*90)
    print("CLEANING LOCATION SUFFIXES FROM TEAM NAMES")
    print("="*90)

    teams_cleaned = 0
    duplicates_merged = 0

    for category in ['uil', 'private']:
        for classification, teams in rankings[category].items():
            print(f"\n{category.upper()} {classification}:")

            # Track clean names to find duplicates
            clean_name_map = {}
            teams_to_keep = []
            indices_to_remove = []

            for i, team in enumerate(teams):
                team_name = team['team_name']
                clean_name = strip_location_suffix(team_name)

                # Check if we already have this clean name
                if clean_name.lower() in clean_name_map:
                    # Duplicate found!
                    orig_idx = clean_name_map[clean_name.lower()]
                    original = teams_to_keep[orig_idx]

                    print(f"  DUPLICATE: '{team_name}' matches '{original['team_name']}'")
                    print(f"    Merging data...")

                    # Merge the two teams
                    merged = merge_duplicate_teams(original, team)
                    teams_to_keep[orig_idx] = merged

                    duplicates_merged += 1
                    teams_cleaned += 1

                else:
                    # New team or location suffix to clean
                    if clean_name != team_name:
                        print(f"  Cleaning: '{team_name}' → '{clean_name}'")
                        team['team_name'] = clean_name
                        teams_cleaned += 1

                    teams_to_keep.append(team)
                    clean_name_map[clean_name.lower()] = len(teams_to_keep) - 1

            # Update classification with cleaned teams
            rankings[category][classification] = teams_to_keep

            # Re-rank teams
            for i, team in enumerate(rankings[category][classification], 1):
                team['rank'] = i

    print("\n" + "="*90)
    print("SUMMARY")
    print("="*90)
    print(f"Teams with location suffixes cleaned: {teams_cleaned}")
    print(f"Duplicate teams merged: {duplicates_merged}")

    # Verify counts
    print("\nVerifying team counts...")
    for category in ['uil', 'private']:
        expected = 25 if category == 'uil' else 10
        for classification, teams in rankings[category].items():
            status = "✓" if len(teams) == expected else "✗ WRONG COUNT"
            print(f"  {status} {category.upper()} {classification}: {len(teams)} teams")

    # Save cleaned rankings
    with open('data/rankings.json', 'w') as f:
        json.dump(rankings, f, indent=2)

    print("\n" + "="*90)
    print("✓ Cleaned rankings saved to data/rankings.json")
    print("="*90)

    return rankings


if __name__ == "__main__":
    clean_rankings()
