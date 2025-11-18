"""
Update rankings with UIL data integrity checks
- Match team names to official UIL schools
- Add correct district information
- Flag ambiguous or unmatched schools
"""

import json
from pathlib import Path
from uil_school_matcher import UILSchoolMatcher
from collections import defaultdict

def load_rankings():
    """Load current rankings"""
    rankings_file = Path(__file__).parent / 'data' / 'rankings.json'
    if not rankings_file.exists():
        print("Error: rankings.json not found")
        return None

    with open(rankings_file, 'r') as f:
        return json.load(f)

def save_rankings(rankings):
    """Save updated rankings"""
    rankings_file = Path(__file__).parent / 'data' / 'rankings.json'
    with open(rankings_file, 'w') as f:
        json.dump(rankings, f, indent=2)
    print(f"✓ Rankings saved to {rankings_file}")

def update_rankings_with_uil_verification():
    """Update rankings with UIL school verification"""
    print("Loading rankings and UIL data...")

    rankings = load_rankings()
    if not rankings:
        return

    matcher = UILSchoolMatcher()

    # Track statistics
    stats = {
        'exact_matches': 0,
        'fuzzy_matches': 0,
        'no_matches': 0,
        'ambiguous': 0,
        'updated_districts': 0
    }

    unmatched_schools = []
    ambiguous_schools = []

    # Process UIL teams
    if 'uil' in rankings:
        for classification_code, teams in rankings['uil'].items():
            print(f"\nProcessing {classification_code}...")

            for team in teams:
                team_name = team['team_name']

                # Try to match with UIL data
                match_result = matcher.find_school_match(team_name, classification_code)

                if match_result['matched']:
                    # Update district if different
                    if team.get('district') != match_result['district']:
                        print(f"  Updating district for {team_name}: {team.get('district')} -> {match_result['district']}")
                        team['district'] = match_result['district']
                        stats['updated_districts'] += 1

                    # Track match type
                    if match_result['confidence'] == 'exact':
                        stats['exact_matches'] += 1
                    elif match_result['confidence'] == 'fuzzy':
                        stats['fuzzy_matches'] += 1
                        print(f"  Fuzzy match: {team_name} -> {match_result['official_name']} (score: {match_result.get('similarity_score', 0):.2f})")

                    # Check for ambiguity
                    if match_result.get('ambiguous'):
                        stats['ambiguous'] += 1
                        ambiguous_schools.append({
                            'team_name': team_name,
                            'classification': classification_code,
                            'matched_to': match_result['official_name'],
                            'possible_schools': match_result.get('possible_schools', [])
                        })

                    # Add UIL verification flag
                    team['uil_verified'] = True
                    team['uil_official_name'] = match_result['official_name']

                else:
                    # No match found
                    stats['no_matches'] += 1
                    team['uil_verified'] = False
                    unmatched_schools.append({
                        'team_name': team_name,
                        'classification': classification_code,
                        'wins': team.get('wins'),
                        'losses': team.get('losses')
                    })
                    print(f"  ✗ No UIL match found for: {team_name}")

    # Print summary
    print("\n" + "="*60)
    print("UIL Verification Summary")
    print("="*60)
    print(f"Exact matches: {stats['exact_matches']}")
    print(f"Fuzzy matches: {stats['fuzzy_matches']}")
    print(f"No matches: {stats['no_matches']}")
    print(f"Ambiguous schools: {stats['ambiguous']}")
    print(f"Districts updated: {stats['updated_districts']}")

    # Show unmatched schools
    if unmatched_schools:
        print("\n" + "="*60)
        print(f"Unmatched Schools ({len(unmatched_schools)})")
        print("="*60)
        for school in unmatched_schools[:20]:  # Show first 20
            record = f"{school.get('wins', 0)}-{school.get('losses', 0)}"
            print(f"  • {school['team_name']} ({school['classification']}) - Record: {record}")
        if len(unmatched_schools) > 20:
            print(f"  ... and {len(unmatched_schools) - 20} more")

    # Show ambiguous schools
    if ambiguous_schools:
        print("\n" + "="*60)
        print(f"Ambiguous Schools ({len(ambiguous_schools)})")
        print("="*60)
        for school in ambiguous_schools[:10]:  # Show first 10
            print(f"  • {school['team_name']} ({school['classification']})")
            print(f"    Matched to: {school['matched_to']}")
            if school.get('possible_schools'):
                print(f"    Possible alternatives:")
                for ps in school['possible_schools'][:3]:
                    print(f"      - {ps.get('school_name', ps)} ({ps.get('classification', '?')}) District {ps.get('district', '?')}")

    # Add metadata
    from datetime import datetime
    rankings['uil_verification'] = {
        'last_verified': datetime.now().isoformat(),
        'stats': stats,
        'unmatched_count': len(unmatched_schools),
        'ambiguous_count': len(ambiguous_schools)
    }

    # Save updated rankings
    save_rankings(rankings)

    return rankings, stats, unmatched_schools, ambiguous_schools


def main():
    """Run UIL verification on rankings"""
    result = update_rankings_with_uil_verification()

    if result:
        rankings, stats, unmatched, ambiguous = result

        print("\n" + "="*60)
        print("✓ UIL Verification Complete")
        print("="*60)
        print(f"Total teams processed: {sum(stats.values())}")
        print(f"Verification rate: {(stats['exact_matches'] + stats['fuzzy_matches']) / sum(stats.values()) * 100:.1f}%")


if __name__ == "__main__":
    main()
