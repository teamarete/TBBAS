"""
Merge Rankings with Weighted Average
Combines TABC (50%), MaxPreps (40%), and GASO (10%) rankings

NOTE: Weights are applied internally only - not displayed on website
"""
import json
from datetime import datetime
from pathlib import Path


def load_rankings_file(filename):
    """Load rankings from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return {}


def normalize_team_name(name, is_private=False):
    """
    Enhanced normalization for matching team names across sources.

    For UIL (public schools):
    - "Seven Lakes (Katy, TX)" -> "seven lakes"
    - "Katy Seven Lakes" -> "seven lakes"
    - "SA Brennan" -> "brennan"

    For Private schools (TAPPS):
    - Keep city prefixes (Houston Christian != Lubbock Christian)
    - Only remove parenthetical info and suffixes
    """
    import re

    if not name:
        return ""

    # Convert to lowercase
    name = name.lower().strip()

    # Remove state suffix patterns like "(City, TX)" or "(TX)"
    name = re.sub(r'\s*\([^)]*,?\s*tx\s*\)', '', name)
    name = re.sub(r'\s*\(tx\)', '', name)

    # Remove other parenthetical info
    name = re.sub(r'\s*\([^)]*\)', '', name)

    # Expand common abbreviations BEFORE removing prefixes
    abbreviations = {
        'sa ': 'san antonio ',
        'bmt ': 'beaumont ',
        'hou ': 'houston ',
        'fw ': 'fort worth ',
        'cc ': 'corpus christi ',
        'rr ': 'round rock ',
        'mans ': 'mansfield ',
        'fb ': 'fort bend ',
    }
    for abbr, full in abbreviations.items():
        if name.startswith(abbr):
            name = full + name[len(abbr):]

    # Handle "Lubbock Cooper Liberty" -> "Lubbock Liberty" (Cooper is middle school name)
    name = name.replace('lubbock cooper liberty', 'lubbock liberty')

    # Handle spacing variations
    name = name.replace('lamarque', 'la marque')

    # Compound school names that should be preserved (not split by prefix removal)
    protected_school_names = ['west brook', 'west plains', 'north shore', 'south grand prairie']

    # For UIL only: Remove city prefixes
    # For TAPPS: Keep city prefixes (they distinguish schools like Houston Christian vs Lubbock Christian)
    if not is_private:
        city_prefixes = [
            'katy', 'frisco', 'dallas', 'houston', 'austin', 'san antonio',
            'fort worth', 'arlington', 'plano', 'beaumont', 'lubbock',
            'corpus christi', 'el paso', 'mckinney', 'denton', 'converse',
            'humble', 'cibolo', 'mansfield', 'fort bend', 'klein', 'cypress',
            'alvin', 'comal', 'lucas', 'prosper', 'amarillo', 'killeen',
            'tyler', 'canyon', 'waxahachie', 'palestine', 'liberty',
            'ropesville', 'waco', 'bullard', 'midland', 'round rock',
            'northwest', 'burleson', 'friendswood'
        ]

        # Sort by length (longest first) to match "san antonio" before "san"
        city_prefixes.sort(key=len, reverse=True)

        # First check if name contains a protected compound school name
        # If so, normalize to just that compound name
        for protected in protected_school_names:
            if protected in name:
                name = protected
                break
        else:
            # No protected name found, remove city prefix if present
            for city in city_prefixes:
                if name.startswith(city + ' '):
                    name = name[len(city)+1:].strip()
                    break

    # Remove common suffixes
    suffixes = ['high school', 'hs', 'h.s.', 'isd']
    for suffix in suffixes:
        if name.endswith(' ' + suffix):
            name = name[:-len(suffix)-1].strip()

    # Normalize whitespace
    name = ' '.join(name.split())

    return name


def merge_classification_rankings(tabc_teams, maxpreps_teams, gaso_teams, classification, max_teams=25):
    """
    Merge rankings from three sources using weighted average:
    - TABC: 50%
    - MaxPreps: 40%
    - GASO: 10%

    Args:
        tabc_teams: List of teams from TABC rankings
        maxpreps_teams: List of teams from MaxPreps rankings
        gaso_teams: List of teams from GASO rankings
        classification: Classification code (e.g., 'AAAAAA')
        max_teams: Maximum teams to return (25 for UIL, 10 for TAPPS)

    Returns:
        List of merged team rankings
    """
    team_data = {}
    is_tapps = classification.startswith('TAPPS')

    # Process TABC rankings (50% weight) - TABC names are authoritative
    for team in tabc_teams:
        normalized = normalize_team_name(team['team_name'], is_private=is_tapps)
        if normalized not in team_data:
            team_data[normalized] = {
                'team_name': team['team_name'],  # Use TABC name as canonical
                'classification': classification,
            }
        team_data[normalized]['tabc_rank'] = team['rank']
        team_data[normalized]['tabc_wins'] = team.get('wins', 0)
        team_data[normalized]['tabc_losses'] = team.get('losses', 0)

    # Process MaxPreps rankings (40% weight)
    for team in maxpreps_teams:
        normalized = normalize_team_name(team['team_name'], is_private=is_tapps)
        if normalized in team_data:
            # Match found - add MaxPreps rank
            team_data[normalized]['maxpreps_rank'] = team['rank']
        elif not is_tapps:
            # For UIL only: add as new team if no TABC match
            team_data[normalized] = {
                'team_name': team['team_name'],
                'classification': classification,
                'maxpreps_rank': team['rank']
            }
        # For TAPPS: skip MaxPreps-only teams (they don't have records)

    # Process GASO rankings (10% weight)
    for team in gaso_teams:
        normalized = normalize_team_name(team['team_name'], is_private=is_tapps)
        if normalized in team_data:
            # Match found - add GASO rank
            team_data[normalized]['gaso_rank'] = team['rank']
        elif not is_tapps:
            # For UIL only: add as new team if no TABC match
            team_data[normalized] = {
                'team_name': team['team_name'],
                'classification': classification,
                'gaso_rank': team['rank']
            }
        # For TAPPS: skip GASO-only teams (they don't have records)

    # Calculate weighted average rankings
    # Weights: TABC 50%, MaxPreps 40%, GASO 10%
    TABC_WEIGHT = 0.50
    MAXPREPS_WEIGHT = 0.40
    GASO_WEIGHT = 0.10

    final_teams = []

    for normalized, data in team_data.items():
        tabc_rank = data.get('tabc_rank')
        maxpreps_rank = data.get('maxpreps_rank')
        gaso_rank = data.get('gaso_rank')

        # Collect available ranks and their weights
        available_ranks = []
        total_weight = 0

        if tabc_rank is not None and tabc_rank <= 50:
            available_ranks.append((tabc_rank, TABC_WEIGHT))
            total_weight += TABC_WEIGHT

        if maxpreps_rank is not None and maxpreps_rank <= 50:
            available_ranks.append((maxpreps_rank, MAXPREPS_WEIGHT))
            total_weight += MAXPREPS_WEIGHT

        if gaso_rank is not None and gaso_rank <= 50:
            available_ranks.append((gaso_rank, GASO_WEIGHT))
            total_weight += GASO_WEIGHT

        # Calculate weighted average (normalize weights if not all sources available)
        if available_ranks and total_weight > 0:
            weighted_sum = sum(rank * weight for rank, weight in available_ranks)
            consensus_rank = weighted_sum / total_weight
        else:
            # Not ranked by any source in top 50
            consensus_rank = 999

        # Use TABC record as authoritative (they track official records)
        wins = data.get('tabc_wins', 0)
        losses = data.get('tabc_losses', 0)

        final_teams.append({
            'rank': 0,  # Will be assigned after sorting
            'team_name': data['team_name'],
            'wins': wins,
            'losses': losses,
            'record': f"{wins}-{losses}" if wins or losses else "",
            'classification': classification,
            'consensus_rank': round(consensus_rank, 2),
            # Store source ranks for reference (not displayed on website)
            'tabc_rank': tabc_rank,
            'maxpreps_rank': maxpreps_rank,
            'gaso_rank': gaso_rank,
        })

    # Sort by consensus rank (weighted average)
    final_teams.sort(key=lambda x: x['consensus_rank'])

    # Assign final sequential ranks (1, 2, 3, ...) and limit to max_teams
    result = []
    for i, team in enumerate(final_teams[:max_teams], 1):
        team['rank'] = i
        result.append(team)

    return result


def merge_all_rankings():
    """
    Merge all ranking sources using weighted average:
    - TABC: 50%
    - MaxPreps: 40%
    - GASO: 10%
    """
    print("=" * 60)
    print("MERGING RANKINGS (Weighted Average)")
    print("=" * 60)
    print()
    print("Weights: TABC 50% | MaxPreps 40% | GASO 10%")
    print()

    # Load sources
    print("Loading ranking sources...")
    tabc = load_rankings_file('tabc_rankings_scraped.json')
    maxpreps = load_rankings_file('maxpreps_rankings_scraped.json')

    # Load GASO rankings
    from gaso_scraper import GASOScraper
    gaso_scraper = GASOScraper()
    gaso_data = gaso_scraper.scrape_all()
    gaso = {
        'uil': gaso_data.get('uil', {}),
        'private': gaso_data.get('private', {})
    }

    print(f"  TABC: {'Loaded' if tabc else 'Not found'}")
    print(f"  MaxPreps: {'Loaded' if maxpreps else 'Not found'}")
    print(f"  GASO: {'Loaded' if gaso else 'Not found'}")
    print()

    print("Merging classifications...")

    # Create final rankings structure
    final_rankings = {
        'last_updated': datetime.now().isoformat(),
        'source': 'weighted_tabc_maxpreps_gaso',
        'uil': {},
        'private': {}
    }

    # UIL classifications - Top 25
    uil_classes = ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']
    for classification in uil_classes:
        tabc_teams = tabc.get('uil', {}).get(classification, [])
        maxpreps_teams = maxpreps.get('uil', {}).get(classification, [])
        gaso_teams = gaso.get('uil', {}).get(classification, [])

        merged = merge_classification_rankings(
            tabc_teams, maxpreps_teams, gaso_teams,
            classification, max_teams=25
        )
        final_rankings['uil'][classification] = merged

        print(f"  UIL {classification}: {len(merged)} teams")

    # TAPPS classifications - Top 10
    tapps_classes = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']
    for classification in tapps_classes:
        tabc_teams = tabc.get('private', {}).get(classification, [])
        maxpreps_teams = maxpreps.get('private', {}).get(classification, [])
        gaso_teams = gaso.get('private', {}).get(classification, [])

        merged = merge_classification_rankings(
            tabc_teams, maxpreps_teams, gaso_teams,
            classification, max_teams=10
        )
        final_rankings['private'][classification] = merged

        print(f"  {classification}: {len(merged)} teams")

    print()
    print("=" * 60)
    print("MERGE COMPLETE")
    print("=" * 60)

    return final_rankings


def save_rankings(rankings, output_file='data/rankings.json'):
    """Save merged rankings to file"""
    with open(output_file, 'w') as f:
        json.dump(rankings, f, indent=2)
    print(f"\nSaved to {output_file}")


if __name__ == '__main__':
    final_rankings = merge_all_rankings()

    # Save to preview file first (not directly to data/rankings.json)
    preview_file = 'rankings_weighted_preview.json'
    with open(preview_file, 'w') as f:
        json.dump(final_rankings, f, indent=2)

    print(f"\nPreview saved to {preview_file}")
    print("\nTo apply these rankings:")
    print("  1. Review the preview file")
    print("  2. Run: cp rankings_weighted_preview.json data/rankings.json")
    print("  3. Run: cp data/rankings.json rankings.json.master")
    print("  4. Commit and push to deploy")
