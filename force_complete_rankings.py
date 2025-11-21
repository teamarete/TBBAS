"""
Force complete top 25 UIL and top 10 TAPPS rankings using TABC data
"""

import json
from scraper import TABCScraper
from pathlib import Path

def force_complete_rankings():
    """Ensure all classifications have complete top 25 (UIL) or top 10 (TAPPS)"""

    # Load current rankings
    rankings_file = Path('data/rankings.json')
    with open(rankings_file, 'r') as f:
        data = json.load(f)

    # Get fresh TABC rankings
    print("Scraping TABC rankings...")
    scraper = TABCScraper()
    tabc_uil = scraper.scrape_uil_rankings()
    tabc_private = scraper.scrape_private_rankings()

    print("\nProcessing UIL classifications...")
    for classification in ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']:
        teams = data['uil'].get(classification, [])
        tabc_teams = tabc_uil.get(classification, [])

        # Get existing team names
        existing_names = {t['team_name']: t for t in teams}

        # Get currently ranked teams
        ranked_teams = [t for t in teams if t.get('rank') and 1 <= t.get('rank') <= 25]
        print(f"\n{classification}: Currently has {len(ranked_teams)}/25 ranked")

        # Add any missing TABC top 25 teams
        added = 0
        for tabc_team in tabc_teams[:25]:
            team_name = tabc_team.get('team_name')
            if team_name and team_name not in existing_names:
                # Add this team
                new_team = {
                    'team_name': team_name,
                    'rank': None,  # Will be assigned below
                    'district': tabc_team.get('district'),
                    'wins': None,
                    'losses': None,
                    'games': None,
                    'ppg': None,
                    'opp_ppg': None
                }
                teams.append(new_team)
                existing_names[team_name] = new_team
                added += 1
                print(f"  Added: {team_name} (TABC Rank {tabc_team.get('rank')})")

        if added > 0:
            print(f"  Total added: {added} teams")

        # Now assign ranks to ensure we have exactly 25 ranked teams
        # Priority: Use TABC top 25 as the ranked teams
        for team in teams:
            team['rank'] = None  # Reset all ranks

        # Assign ranks 1-25 to TABC top 25 teams
        for i, tabc_team in enumerate(tabc_teams[:25], start=1):
            team_name = tabc_team.get('team_name')
            if team_name in existing_names:
                existing_names[team_name]['rank'] = i
                # Also ensure district is set
                if not existing_names[team_name].get('district'):
                    existing_names[team_name]['district'] = tabc_team.get('district')

        # Verify
        ranked_count = sum(1 for t in teams if t.get('rank') and 1 <= t.get('rank') <= 25)
        print(f"  ✅ Now has {ranked_count}/25 ranked")

        data['uil'][classification] = teams

    print("\nProcessing TAPPS classifications...")
    for classification in ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']:
        teams = data['private'].get(classification, [])
        tabc_teams = tabc_private.get(classification, [])

        # Get existing team names
        existing_names = {t['team_name']: t for t in teams}

        # Get currently ranked teams
        ranked_teams = [t for t in teams if t.get('rank') and 1 <= t.get('rank') <= 10]
        print(f"\n{classification}: Currently has {len(ranked_teams)}/10 ranked")

        # Add any missing TABC top 10 teams
        added = 0
        for tabc_team in tabc_teams[:10]:
            team_name = tabc_team.get('team_name')
            if team_name and team_name not in existing_names:
                # Add this team
                new_team = {
                    'team_name': team_name,
                    'rank': None,  # Will be assigned below
                    'district': tabc_team.get('district'),
                    'wins': None,
                    'losses': None,
                    'games': None,
                    'ppg': None,
                    'opp_ppg': None
                }
                teams.append(new_team)
                existing_names[team_name] = new_team
                added += 1
                print(f"  Added: {team_name} (TABC Rank {tabc_team.get('rank')})")

        if added > 0:
            print(f"  Total added: {added} teams")

        # Now assign ranks to ensure we have exactly 10 ranked teams
        for team in teams:
            team['rank'] = None  # Reset all ranks

        # Assign ranks 1-10 to TABC top 10 teams
        for i, tabc_team in enumerate(tabc_teams[:10], start=1):
            team_name = tabc_team.get('team_name')
            if team_name in existing_names:
                existing_names[team_name]['rank'] = i
                # Also ensure district is set
                if not existing_names[team_name].get('district'):
                    existing_names[team_name]['district'] = tabc_team.get('district')

        # Verify
        ranked_count = sum(1 for t in teams if t.get('rank') and 1 <= t.get('rank') <= 10)
        print(f"  ✅ Now has {ranked_count}/10 ranked")

        data['private'][classification] = teams

    # Update last_updated
    from datetime import datetime
    data['last_updated'] = datetime.now().isoformat()
    data['source'] = 'TABC rankings (forced complete top 25/10)'

    # Save
    print(f"\nSaving to {rankings_file}...")
    with open(rankings_file, 'w') as f:
        json.dump(data, f, indent=2)

    print("✅ Complete! All classifications now have full rankings.")

    # Final verification
    print("\n" + "=" * 70)
    print("FINAL VERIFICATION")
    print("=" * 70)

    print("\nUIL:")
    for classification in ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']:
        teams = data['uil'][classification]
        ranked = sum(1 for t in teams if t.get('rank') and 1 <= t.get('rank') <= 25)
        status = '✅' if ranked == 25 else '❌'
        print(f"  {classification}: {ranked}/25 {status}")

    print("\nTAPPS:")
    for classification in ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']:
        teams = data['private'][classification]
        ranked = sum(1 for t in teams if t.get('rank') and 1 <= t.get('rank') <= 10)
        status = '✅' if ranked == 10 else '❌'
        print(f"  {classification}: {ranked}/10 {status}")


if __name__ == '__main__':
    force_complete_rankings()
