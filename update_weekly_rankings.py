"""
Update Weekly Rankings
Runs every Monday at 4 PM CST to calculate and publish new rankings

Process:
1. Load TABC + MaxPreps rankings from 2 PM scrape
2. Calculate efficiency rankings from box score database
3. Calculate stats from database (PPG, Opp PPG, W-L)
4. Compute weighted average: 33% Calculated + 33% TABC + 33% MaxPreps
5. Update rankings.json and rankings.json.master
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
from ranking_calculator import RankingCalculator

def load_weekly_scraped_rankings():
    """Load the most recent weekly rankings scrape"""
    data_dir = Path(__file__).parent / 'data'

    # Find the most recent weekly rankings file
    weekly_files = sorted(data_dir.glob('weekly_rankings_*.json'), reverse=True)

    if not weekly_files:
        print("ERROR: No weekly rankings files found")
        return None

    latest_file = weekly_files[0]
    print(f"Loading weekly rankings from {latest_file.name}...")

    with open(latest_file, 'r') as f:
        return json.load(f)

def calculate_efficiency_rankings_from_db():
    """Calculate efficiency rankings from box score database"""
    print("Calculating efficiency rankings from database...")

    db_path = Path(__file__).parent / 'instance' / 'tbbas.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all teams with games
    cursor.execute('''
        SELECT DISTINCT team1_name FROM box_score
        UNION
        SELECT DISTINCT team2_name FROM box_score
    ''')

    teams = [row[0] for row in cursor.fetchall()]

    # Calculate efficiency rating for each team
    team_ratings = {}

    for team in teams:
        # Get all games for this team
        cursor.execute('''
            SELECT
                CASE WHEN team1_name = ? THEN team1_score ELSE team2_score END as points_for,
                CASE WHEN team1_name = ? THEN team2_score ELSE team1_score END as points_against,
                CASE WHEN team1_name = ? THEN team1_fg ELSE team2_fg END as fg,
                CASE WHEN team1_name = ? THEN team1_fga ELSE team2_fga END as fga,
                CASE WHEN team1_name = ? THEN team1_to ELSE team2_to END as turnovers
            FROM box_score
            WHERE team1_name = ? OR team2_name = ?
        ''', (team, team, team, team, team, team, team))

        games = cursor.fetchall()

        if not games:
            continue

        # Simple efficiency calculation: avg points scored - avg points allowed
        total_for = sum(g[0] for g in games if g[0] is not None)
        total_against = sum(g[1] for g in games if g[1] is not None)
        game_count = len(games)

        if game_count > 0:
            efficiency = (total_for - total_against) / game_count
            team_ratings[team] = {
                'efficiency': efficiency,
                'games': game_count,
                'ppg': round(total_for / game_count, 1),
                'opp_ppg': round(total_against / game_count, 1)
            }

    conn.close()

    # Rank teams by efficiency
    sorted_teams = sorted(team_ratings.items(), key=lambda x: x[1]['efficiency'], reverse=True)

    # Assign ranks
    calculated_rankings = {}
    for rank, (team_name, stats) in enumerate(sorted_teams, 1):
        calculated_rankings[team_name] = {
            'rank': rank,
            'efficiency': stats['efficiency'],
            'games': stats['games'],
            'ppg': stats['ppg'],
            'opp_ppg': stats['opp_ppg']
        }

    print(f"  Calculated rankings for {len(calculated_rankings)} teams")

    return calculated_rankings

def get_team_stats_from_db(team_name):
    """Get PPG, Opp PPG, and game count from database for a specific team with fuzzy matching"""
    db_path = Path(__file__).parent / 'instance' / 'tbbas.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Try exact match first
    cursor.execute('''
        SELECT COUNT(*) as game_count,
               SUM(CASE WHEN team1_name = ? THEN team1_score ELSE team2_score END) as total_points,
               SUM(CASE WHEN team1_name = ? THEN team2_score ELSE team1_score END) as total_opp_points
        FROM box_score
        WHERE team1_name = ? OR team2_name = ?
    ''', (team_name, team_name, team_name, team_name))

    result = cursor.fetchone()

    # If no exact match, try fuzzy matching with name variations
    if result[0] == 0:
        # Try multiple search strategies
        name_parts = team_name.split()
        search_terms = []

        # Strategy 1: Last significant word (skip common suffixes)
        if len(name_parts) > 0:
            last_word = name_parts[-1].replace('-', ' ').strip()
            if last_word.lower() not in ['academy', 'school', 'christian', 'catholic', 'prep', 'preparatory']:
                search_terms.append(last_word)

        # Strategy 2: Last two words
        if len(name_parts) >= 2:
            last_two = ' '.join(name_parts[-2:])
            search_terms.append(last_two)

        # Strategy 3: First two words (for "First Baptist", "Holy Cross", etc.)
        if len(name_parts) >= 2:
            first_two = ' '.join(name_parts[:2])
            search_terms.append(first_two)

        # Strategy 4: Remove city suffix (e.g., "Academy-Dallas" → "Academy")
        for part in name_parts:
            if '-' in part:
                base = part.split('-')[0]
                if base:
                    search_terms.append(base)

        # Try each search term until we find matches
        for search_term in search_terms:
            if not search_term:
                continue

            cursor.execute('''
                SELECT COUNT(*) as game_count,
                       SUM(CASE WHEN team1_name LIKE ? THEN team1_score ELSE team2_score END) as total_points,
                       SUM(CASE WHEN team1_name LIKE ? THEN team2_score ELSE team1_score END) as total_opp_points
                FROM box_score
                WHERE team1_name LIKE ? OR team2_name LIKE ?
            ''', (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))

            result = cursor.fetchone()
            if result[0] > 0:  # Found matches
                break

    conn.close()

    if result[0] > 0:
        games = result[0]
        ppg = round(result[1] / games, 1) if games > 0 else None
        opp_ppg = round(result[2] / games, 1) if games > 0 else None
        return {
            'games': games,
            'ppg': ppg,
            'opp_ppg': opp_ppg
        }

    return None

def normalize_team_name(name):
    """
    Normalize team name for matching across sources
    Handles common variations like 'SA Brennan' vs 'Brennan'
    """
    name = name.lower().strip()

    # Common full city names to abbreviations
    city_replacements = {
        'san antonio': 'sa',
        'houston': 'hou',
        'beaumont': 'bmt',
        'fort worth': 'fw',
        'mansfield': 'mans',
        'el paso': 'ep',
        'fort bend': 'fb',
        'corpus christi': 'cc'
    }

    for full, abbr in city_replacements.items():
        name = name.replace(full, abbr)

    # Remove extra spaces
    name = ' '.join(name.split())

    return name

def get_base_school_name(name):
    """
    Extract base school name without city/district prefix
    'SA Brennan' -> 'brennan', 'Brennan' -> 'brennan'
    'Katy Seven Lakes' -> 'seven lakes', 'Seven Lakes' -> 'seven lakes'

    NOTE: Do NOT strip prefixes that are part of the school's actual name
    'Plano East' should stay as 'plano east', NOT become 'east'
    'Allen' should stay as 'allen' (it's the school name, not a city prefix)
    """
    norm = normalize_team_name(name)

    # Split into words
    words = norm.split()

    if len(words) <= 1:
        return norm

    # Common city/district prefixes that should ONLY be removed when followed by a school name
    # Only strip these when there are 2+ words AND the prefix is clearly separate from the school name
    city_prefixes_to_strip = [
        'sa', 'hou', 'bmt', 'fw', 'mans', 'ep', 'fb', 'cc',
        'dallas', 'austin', 'tyler', 'waco', 'lubbock',
        'katy', 'converse', 'denton', 'frisco', 'colleyville'
    ]

    # DO NOT strip directional prefixes - they are part of the school name
    # "South Grand Prairie" and "Grand Prairie" are DIFFERENT schools
    # "North Shore" and "Shore" are DIFFERENT schools
    # These should NOT be normalized to the same base name

    # Strip city prefixes only when followed by more words
    if words[0] in city_prefixes_to_strip:
        return ' '.join(words[1:])

    # For everything else, return the full normalized name (don't strip)
    # This preserves: Allen, Plano, Plano East, McKinney, Lancaster, etc.
    return norm

def calculate_weighted_rank(calculated_rank, tabc_rank, maxpreps_rank, db_games=0):
    """
    Calculate weighted average rank using 33/33/33 formula

    If a team has fewer than 15 games in the database, we exclude the calculated rank
    to avoid penalizing teams for incomplete data. In that case, we use 50/50 TABC/MaxPreps.

    Args:
        calculated_rank: Rank from efficiency calculations (or None)
        tabc_rank: Rank from TABC (or None)
        maxpreps_rank: Rank from MaxPreps (or None)
        db_games: Number of games in database for this team (default 0)

    Returns:
        Weighted average rank (lower is better)
    """
    ranks = []

    # Only include calculated rank if team has sufficient database games (15+)
    # This prevents penalizing teams that appear highly ranked but have incomplete game data
    # Example: McKinney (#20 TABC) has only 11 games with poor efficiency, would rank #513 weighted
    if calculated_rank is not None and db_games >= 15:
        ranks.append(calculated_rank)

    if tabc_rank is not None:
        ranks.append(tabc_rank)

    if maxpreps_rank is not None:
        ranks.append(maxpreps_rank)

    if not ranks:
        return None

    # Calculate average (equal weight for each source present)
    return sum(ranks) / len(ranks)

def merge_rankings_3way(tabc_rankings, maxpreps_rankings, calculated_rankings):
    """
    Merge TABC, MaxPreps, and Calculated rankings using 33/33/33 weighted average

    Returns: Dictionary of merged rankings by classification
    """
    print("\nMerging rankings with 33/33/33 weighting...")

    merged = {}

    # Process UIL classifications
    uil_classifications = {
        '6A': 'AAAAAA',
        '5A': 'AAAAA',
        '4A': 'AAAA',
        '3A': 'AAA',
        '2A': 'AA',
        '1A': 'A'
    }

    for short_code, long_code in uil_classifications.items():
        # Get teams from each source with normalized name lookup
        tabc_teams_raw = tabc_rankings.get(short_code, [])
        maxpreps_teams_raw = maxpreps_rankings.get(short_code, [])

        # Create lookup with base school names pointing to original team data
        # Use base name (without city prefix) to match teams across sources
        tabc_lookup = {}
        for t in tabc_teams_raw:
            base_name = get_base_school_name(t['team_name'])
            if base_name not in tabc_lookup:
                tabc_lookup[base_name] = t

        maxpreps_lookup = {}
        for t in maxpreps_teams_raw:
            base_name = get_base_school_name(t['team_name'])
            if base_name not in maxpreps_lookup:
                maxpreps_lookup[base_name] = t

        # Collect all unique base school names
        all_teams = set(tabc_lookup.keys()) | set(maxpreps_lookup.keys())

        team_scores = []

        for norm_team_name in all_teams:
            tabc_team = tabc_lookup.get(norm_team_name, {})
            maxpreps_team = maxpreps_lookup.get(norm_team_name, {})

            tabc_rank = tabc_team.get('rank')
            maxpreps_rank = maxpreps_team.get('rank')

            # Use TABC name if available (most authoritative), otherwise MaxPreps
            display_name = tabc_team.get('team_name') or maxpreps_team.get('team_name')

            # Check calculated rankings with both original and normalized names
            calculated_rank = calculated_rankings.get(display_name, {}).get('rank')
            if calculated_rank is None:
                # Try normalized name
                calculated_rank = calculated_rankings.get(norm_team_name, {}).get('rank')

            # Get stats from database (need this for db_games count)
            stats = get_team_stats_from_db(display_name)
            db_games = stats['games'] if stats else 0

            # Calculate weighted average (passing db_games to avoid penalizing teams with few database games)
            weighted_rank = calculate_weighted_rank(calculated_rank, tabc_rank, maxpreps_rank, db_games)

            if weighted_rank is None:
                continue

            # Build team data
            team_data = {
                'team_name': display_name,
                'weighted_rank': weighted_rank,
                'tabc_rank': tabc_rank,
                'maxpreps_rank': maxpreps_rank,
                'calculated_rank': calculated_rank
            }

            # Get record from TABC (most up-to-date)
            if tabc_team:
                team_data['wins'] = tabc_team.get('wins')
                team_data['losses'] = tabc_team.get('losses')
                team_data['record'] = tabc_team.get('record')

            # Add stats to team data
            if stats:
                team_data['ppg'] = stats['ppg']
                team_data['opp_ppg'] = stats['opp_ppg']
                team_data['games'] = stats['games']

            team_scores.append(team_data)

        # Sort by weighted rank and assign final ranks
        team_scores.sort(key=lambda x: x['weighted_rank'])

        for rank, team in enumerate(team_scores[:25], 1):  # Top 25 for UIL
            team['rank'] = rank

        merged[long_code] = team_scores[:25]
        print(f"  UIL {short_code}: {len(merged[long_code])} teams")

    # Process TAPPS classifications
    tapps_classifications = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']

    for cls_code in tapps_classifications:
        # Get teams from each source with normalized name lookup
        tabc_teams_raw = tabc_rankings.get(cls_code, [])
        maxpreps_teams_raw = maxpreps_rankings.get(cls_code, [])

        # Create lookup with base school names pointing to original team data
        # Use base name (without city prefix) to match teams across sources
        tabc_lookup = {}
        for t in tabc_teams_raw:
            base_name = get_base_school_name(t['team_name'])
            if base_name not in tabc_lookup:
                tabc_lookup[base_name] = t

        maxpreps_lookup = {}
        for t in maxpreps_teams_raw:
            base_name = get_base_school_name(t['team_name'])
            if base_name not in maxpreps_lookup:
                maxpreps_lookup[base_name] = t

        # Collect all unique base school names
        all_teams = set(tabc_lookup.keys()) | set(maxpreps_lookup.keys())

        team_scores = []

        for norm_team_name in all_teams:
            tabc_team = tabc_lookup.get(norm_team_name, {})
            maxpreps_team = maxpreps_lookup.get(norm_team_name, {})

            tabc_rank = tabc_team.get('rank')
            maxpreps_rank = maxpreps_team.get('rank')

            # Use TABC name if available (most authoritative), otherwise MaxPreps
            display_name = tabc_team.get('team_name') or maxpreps_team.get('team_name')

            # Check calculated rankings with both original and normalized names
            calculated_rank = calculated_rankings.get(display_name, {}).get('rank')
            if calculated_rank is None:
                # Try normalized name
                calculated_rank = calculated_rankings.get(norm_team_name, {}).get('rank')

            # Get stats from database (need this for db_games count)
            stats = get_team_stats_from_db(display_name)
            db_games = stats['games'] if stats else 0

            # Calculate weighted average (passing db_games to avoid penalizing teams with few database games)
            weighted_rank = calculate_weighted_rank(calculated_rank, tabc_rank, maxpreps_rank, db_games)

            if weighted_rank is None:
                continue

            # Build team data
            team_data = {
                'team_name': display_name,
                'weighted_rank': weighted_rank,
                'tabc_rank': tabc_rank,
                'maxpreps_rank': maxpreps_rank,
                'calculated_rank': calculated_rank
            }

            # Get record from TABC (most up-to-date)
            if tabc_team:
                team_data['wins'] = tabc_team.get('wins')
                team_data['losses'] = tabc_team.get('losses')
                team_data['record'] = tabc_team.get('record')

            # Add stats to team data
            if stats:
                team_data['ppg'] = stats['ppg']
                team_data['opp_ppg'] = stats['opp_ppg']
                team_data['games'] = stats['games']

            team_scores.append(team_data)

        # Sort by weighted rank and assign final ranks
        team_scores.sort(key=lambda x: x['weighted_rank'])

        for rank, team in enumerate(team_scores[:10], 1):  # Top 10 for TAPPS
            team['rank'] = rank

        merged[cls_code] = team_scores[:10]
        print(f"  {cls_code}: {len(merged[cls_code])} teams")

    return merged

def update_weekly_rankings():
    """Main function to update weekly rankings"""
    print("=" * 80)
    print(f"WEEKLY RANKINGS UPDATE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 1. Load weekly scraped rankings
    weekly_data = load_weekly_scraped_rankings()
    if not weekly_data:
        return False

    tabc_uil = weekly_data.get('tabc', {}).get('uil', {})
    tabc_private = weekly_data.get('tabc', {}).get('private', {})
    maxpreps_uil = weekly_data.get('maxpreps', {}).get('uil', {})
    maxpreps_tapps = weekly_data.get('maxpreps', {}).get('tapps', {})

    print(f"\nTABC UIL: {sum(len(teams) for teams in tabc_uil.values())} teams across {len(tabc_uil)} classifications")
    print(f"TABC Private: {sum(len(teams) for teams in tabc_private.values())} teams across {len(tabc_private)} classifications")
    print(f"MaxPreps UIL: {sum(len(teams) for teams in maxpreps_uil.values())} teams across {len(maxpreps_uil)} classifications")
    print(f"MaxPreps TAPPS: {sum(len(teams) for teams in maxpreps_tapps.values())} teams across {len(maxpreps_tapps)} classifications")

    # 2. Calculate efficiency rankings from database
    calculated_rankings = calculate_efficiency_rankings_from_db()

    # 3. Merge UIL rankings (33/33/33)
    uil_merged = merge_rankings_3way(tabc_uil, maxpreps_uil, calculated_rankings)

    # 4. Merge TAPPS rankings (33/33/33)
    tapps_merged = merge_rankings_3way(tabc_private, maxpreps_tapps, calculated_rankings)

    # 5. Create final rankings structure
    final_rankings = {
        'last_updated': datetime.now().isoformat(),
        'uil': uil_merged,
        'private': tapps_merged
    }

    # 6. Save to rankings.json
    rankings_file = Path(__file__).parent / 'data' / 'rankings.json'
    rankings_file.parent.mkdir(exist_ok=True)

    with open(rankings_file, 'w') as f:
        json.dump(final_rankings, f, indent=2)

    print(f"\n✓ Updated {rankings_file}")

    # 7. Update gold master
    master_file = Path(__file__).parent / 'rankings.json.master'
    with open(master_file, 'w') as f:
        json.dump(final_rankings, f, indent=2)

    print(f"✓ Updated gold master: {master_file}")

    print("=" * 80)
    print("Weekly rankings update complete!")
    print("=" * 80)

    return True

if __name__ == '__main__':
    update_weekly_rankings()
