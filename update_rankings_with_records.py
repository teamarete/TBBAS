"""
Update rankings.json with win-loss records from game data
Also adds district information from UIL data
"""

import json
from app import app
from models import BoxScore
from collections import defaultdict
from datetime import datetime
from school_name_normalizer import SchoolNameNormalizer
from school_abbreviations import expand_abbreviations, get_search_variations
from manual_district_mappings import get_manual_district
from tapps_district_mappings import get_tapps_district
from pathlib import Path

def load_uil_districts():
    """Load UIL school districts from data file"""
    uil_file = Path(__file__).parent / 'data' / 'uil_schools.json'

    if not uil_file.exists():
        print("Warning: UIL schools data not found - districts will not be added")
        return {}

    try:
        with open(uil_file, 'r') as f:
            uil_data = json.load(f)

        # Build lookup: (team_name_normalized, classification) -> district
        district_lookup = {}
        normalizer = SchoolNameNormalizer()

        for classification, schools in uil_data.items():
            # Convert UIL classification to internal code (6A -> AAAAAA)
            class_map = {
                '6A': 'AAAAAA',
                '5A': 'AAAAA',
                '4A': 'AAAA',
                '3A': 'AAA',
                '2A': 'AA',
                '1A': 'A'
            }
            class_code = class_map.get(classification, classification)

            for school in schools:
                school_name = school['school_name']
                normalized = normalizer.normalize(school_name).lower()
                district = school['district']

                # Store with multiple keys for better matching
                district_lookup[(school_name, class_code)] = district
                district_lookup[(normalized, class_code)] = district
                district_lookup[(school_name.lower(), class_code)] = district

        print(f"Loaded {len(district_lookup)} district mappings from UIL data")
        return district_lookup

    except Exception as e:
        print(f"Error loading UIL districts: {e}")
        return {}


def calculate_team_records():
    """Calculate win-loss records from game data"""
    print("Calculating team records from game data...")

    with app.app_context():
        games = BoxScore.query.all()

        team_records = defaultdict(lambda: {
            'wins': 0,
            'losses': 0,
            'games': 0,
            'points_for': 0,
            'points_against': 0
        })

        for game in games:
            # Team 1
            team_records[game.team1_name]['games'] += 1
            team_records[game.team1_name]['points_for'] += game.team1_score
            team_records[game.team1_name]['points_against'] += game.team2_score

            if game.team1_score > game.team2_score:
                team_records[game.team1_name]['wins'] += 1
            else:
                team_records[game.team1_name]['losses'] += 1

            # Team 2
            team_records[game.team2_name]['games'] += 1
            team_records[game.team2_name]['points_for'] += game.team2_score
            team_records[game.team2_name]['points_against'] += game.team1_score

            if game.team2_score > game.team1_score:
                team_records[game.team2_name]['wins'] += 1
            else:
                team_records[game.team2_name]['losses'] += 1

        print(f"Calculated records for {len(team_records)} teams from {len(games)} games")
        return team_records


def update_rankings_with_records():
    """Update rankings.json with actual records and districts"""

    # Load existing rankings
    print("\nLoading rankings.json...")
    with open('data/rankings.json', 'r') as f:
        rankings = json.load(f)

    # Load UIL districts
    district_lookup = load_uil_districts()

    # Calculate records
    team_records = calculate_team_records()

    # Initialize normalizer for matching team names
    normalizer = SchoolNameNormalizer()

    # Update each ranking entry with records and districts
    updated_count = 0
    districts_added = 0

    for category in ['uil', 'private']:
        if category not in rankings:
            continue

        for classification, teams in rankings[category].items():
            for team in teams:
                team_name = team['team_name']

                # Try to find record (exact match first, then variations, then normalized)
                record = team_records.get(team_name)

                if not record:
                    # Try all search variations (including abbreviation expansions and special cases)
                    search_variations = get_search_variations(team_name)
                    for variation in search_variations:
                        record = team_records.get(variation)
                        if record:
                            break

                if not record:
                    # Try normalized matching as last resort
                    canonical_name = normalizer.find_canonical_name([team_name])
                    if canonical_name:
                        record = team_records.get(canonical_name)

                if record:
                    team['wins'] = record['wins']
                    team['losses'] = record['losses']
                    team['games'] = record['games']
                    team['ppg'] = round(record['points_for'] / record['games'], 1) if record['games'] > 0 else 0
                    team['opp_ppg'] = round(record['points_against'] / record['games'], 1) if record['games'] > 0 else 0
                    updated_count += 1

                # Add district for UIL schools (always try, even if already has one - ensures data integrity)
                if category == 'uil':
                    district = None

                    # Try manual mapping first (highest priority)
                    district = get_manual_district(team_name, classification)

                    if not district:
                        # Get all search variations (including abbreviation expansions)
                        search_variations = get_search_variations(team_name)
                        normalized = normalizer.normalize(team_name).lower()

                        # Try exact matches with all variations
                        for variation in search_variations:
                            # Also try manual mapping with variations
                            district = get_manual_district(variation, classification)
                            if district:
                                break

                            district = (
                                district_lookup.get((variation, classification)) or
                                district_lookup.get((variation.lower(), classification)) or
                                district_lookup.get((normalizer.normalize(variation).lower(), classification))
                            )
                            if district:
                                break

                        # If no exact match, try fuzzy matching (variation appears in UIL name)
                        if not district:
                            for variation in search_variations:
                                if len(variation) <= 4:  # Skip very short variations
                                    continue
                                variation_lower = variation.lower()
                                for (uil_name, class_code), dist in district_lookup.items():
                                    if class_code == classification and isinstance(uil_name, str):
                                        # Check if variation appears in UIL name
                                        if variation_lower in uil_name.lower():
                                            district = dist
                                            break
                                if district:
                                    break

                    # Add district if found (count as added only if it was missing)
                    if district:
                        if not team.get('district'):
                            districts_added += 1
                        team['district'] = district

                # Add district for TAPPS/Private schools
                elif category == 'private':
                    district = get_tapps_district(team_name, classification)

                    if district:
                        if not team.get('district'):
                            districts_added += 1
                        team['district'] = district

    # Update timestamp
    rankings['last_updated'] = datetime.now().isoformat()
    rankings['records_from_games'] = True
    rankings['games_analyzed'] = len(team_records)
    rankings['districts_from_uil'] = districts_added

    # Save updated rankings
    print(f"\nUpdated {updated_count} team records")
    print(f"Added {districts_added} districts from UIL data")

    with open('data/rankings.json', 'w') as f:
        json.dump(rankings, f, indent=2)

    print("✓ Rankings updated with game records and districts!")
    print(f"  Teams with records: {updated_count}")
    print(f"  Districts added: {districts_added}")
    print(f"  Total teams analyzed: {len(team_records)}")

    return rankings


if __name__ == "__main__":
    update_rankings_with_records()
