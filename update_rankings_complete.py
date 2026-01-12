"""
Update rankings.json with complete statistics from game data
Combines win-loss records, game counts, AND efficiency ratings
Uses normalized schema for fast lookups
"""

import json
from app_refactored import create_app
from models_normalized import db, Team, Game, TeamGameStats
from collections import defaultdict
from datetime import datetime
from school_name_normalizer import SchoolNameNormalizer
from school_abbreviations import get_search_variations
from pathlib import Path
import re


def strip_location_suffix(team_name):
    """
    Remove location suffixes like (City, TX) or (TX) from team names
    Examples:
        'Cypress Springs (Cypress, TX)' -> 'Cypress Springs'
        'New Braunfels (TX)' -> 'New Braunfels'
    """
    # Remove patterns like (City, TX) or (TX)
    cleaned = re.sub(r'\s*\([^)]*TX[^)]*\)$', '', team_name)
    return cleaned.strip()


def estimate_possessions(fga, fta, turnovers):
    """
    Estimate possessions using the standard formula:
    Possessions = FGA + 0.44 * FTA + TO
    """
    if fga is None or fga == 0:
        return None

    poss = fga + (0.44 * (fta or 0)) + (turnovers or 0)
    return max(poss, 1)  # Ensure at least 1 possession


def calculate_complete_team_stats(app):
    """
    Calculate complete statistics including efficiency ratings
    Returns dict with all stats needed for rankings
    """
    print("Calculating complete team statistics from game data...")

    with app.app_context():
        teams = Team.query.all()

        team_stats_dict = {}

        for team in teams:
            # Get all game stats for this team
            stats_records = TeamGameStats.query.filter_by(team_id=team.id).all()

            if not stats_records:
                continue

            # Initialize accumulators
            wins = 0
            losses = 0
            total_points_for = 0
            total_points_against = 0
            total_possessions = 0
            games_count = len(stats_records)

            # Process each game
            for stat in stats_records:
                game = stat.game

                # Points scored
                total_points_for += stat.score

                # Find opponent's stats
                opponent_stats = [s for s in game.team_stats if s.team_id != team.id]
                if opponent_stats:
                    opponent_stat = opponent_stats[0]
                    total_points_against += opponent_stat.score

                    # Win/loss
                    if stat.score > opponent_stat.score:
                        wins += 1
                    else:
                        losses += 1

                # Calculate possessions for this game (if available)
                poss = estimate_possessions(stat.fga, stat.fta, stat.to)
                if poss:
                    total_possessions += poss

            # Calculate efficiency ratings
            # If we have possession data, use true efficiency
            if total_possessions > 0:
                # Offensive Efficiency: Points per 100 possessions
                off_eff = (total_points_for / total_possessions) * 100

                # Defensive Efficiency: Points allowed per 100 possessions
                def_eff = (total_points_against / total_possessions) * 100

                # Net Rating
                net_rating = off_eff - def_eff
            else:
                # Fallback: Use point differential per game as proxy
                # This is simpler but still useful when detailed stats aren't available
                ppg = total_points_for / games_count if games_count > 0 else 0
                opp_ppg = total_points_against / games_count if games_count > 0 else 0

                # Net rating = point differential per game
                net_rating = ppg - opp_ppg

                # Estimate offensive/defensive efficiency using average tempo (70 possessions/game)
                # These are rough estimates but better than 0
                avg_possessions_per_game = 70
                off_eff = (ppg / avg_possessions_per_game) * 100
                def_eff = (opp_ppg / avg_possessions_per_game) * 100

            # Store complete stats
            team_stats_dict[team.display_name] = {
                'wins': wins,
                'losses': losses,
                'games': games_count,
                'ppg': round(total_points_for / games_count, 1) if games_count > 0 else 0,
                'opp_ppg': round(total_points_against / games_count, 1) if games_count > 0 else 0,
                'net_rating': round(net_rating, 1),
                'adj_offensive_eff': round(off_eff, 1),
                'adj_defensive_eff': round(def_eff, 1)
            }

            # Also store by normalized name for better matching
            team_stats_dict[team.normalized_name] = team_stats_dict[team.display_name]

        print(f"Calculated complete stats for {len(teams)} teams")
        return team_stats_dict


def update_rankings_with_complete_stats():
    """Update rankings.json with complete game statistics"""

    # Create Flask app
    app = create_app()

    # Load existing rankings
    print("\nLoading rankings.json...")
    with open('data/rankings.json', 'r') as f:
        rankings = json.load(f)

    # Calculate complete stats
    team_stats = calculate_complete_team_stats(app)

    # Initialize normalizer for matching
    normalizer = SchoolNameNormalizer()

    # Update each ranking entry
    updated_count = 0
    stats_added = 0

    for category in ['uil', 'private']:
        if category not in rankings:
            continue

        for classification, teams in rankings[category].items():
            print(f"\nUpdating {category} {classification}...")

            for team in teams:
                team_name = team['team_name']

                # FIRST: Strip location suffix (this is the key fix!)
                clean_name = strip_location_suffix(team_name)

                # Try to find stats (exact match first)
                stats = team_stats.get(team_name)

                if not stats and clean_name != team_name:
                    # Try without location suffix
                    stats = team_stats.get(clean_name)

                if not stats:
                    # Try normalized name
                    normalized = normalizer.normalize(clean_name)
                    stats = team_stats.get(normalized)

                if not stats:
                    # Try all search variations
                    search_variations = get_search_variations(clean_name)
                    for variation in search_variations:
                        stats = team_stats.get(variation)
                        if stats:
                            break
                        # Also try normalized version
                        normalized_var = normalizer.normalize(variation)
                        stats = team_stats.get(normalized_var)
                        if stats:
                            break

                if stats:
                    # Update game statistics
                    team['games'] = stats['games']
                    team['ppg'] = stats['ppg']
                    team['opp_ppg'] = stats['opp_ppg']

                    # Update efficiency statistics (these were missing!)
                    team['net_rating'] = stats['net_rating']
                    team['adj_offensive_eff'] = stats['adj_offensive_eff']
                    team['adj_defensive_eff'] = stats['adj_defensive_eff']

                    stats_added += 1

                    # Only update wins/losses if TABC record is 0-0
                    current_wins = team.get('wins', 0)
                    current_losses = team.get('losses', 0)

                    if current_wins == 0 and current_losses == 0:
                        team['wins'] = stats['wins']
                        team['losses'] = stats['losses']
                        team['record'] = f"{stats['wins']}-{stats['losses']}"
                        updated_count += 1
                else:
                    # Show both original and cleaned name if different
                    if clean_name != team_name:
                        print(f"  ⚠ No stats found for: {team_name} (tried: {clean_name})")
                    else:
                        print(f"  ⚠ No stats found for: {team_name}")

    # Update metadata
    rankings['last_updated'] = datetime.now().isoformat()
    rankings['complete_stats'] = True
    rankings['teams_with_stats'] = stats_added

    # Save updated rankings
    with open('data/rankings.json', 'w') as f:
        json.dump(rankings, f, indent=2)

    print("\n" + "="*60)
    print("✓ Rankings updated with complete statistics!")
    print(f"  Teams with complete stats: {stats_added}")
    print(f"  Win-loss records updated: {updated_count}")
    print("="*60)

    return rankings


if __name__ == "__main__":
    update_rankings_with_complete_stats()
