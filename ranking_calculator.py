"""
Ranking Calculator for TBBAS
Calculates KenPom-style efficiency ratings from box score data
"""

import json
from datetime import datetime
from pathlib import Path
from models import BoxScore
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RankingCalculator:
    """Calculate team rankings from box score data"""

    def __init__(self, app=None):
        self.app = app

    def estimate_possessions(self, fg_att, ft_att, turnovers, off_reb=None):
        """
        Estimate possessions using the standard formula:
        Possessions = FGA + 0.44 * FTA - OffReb + TO
        If offensive rebounds not available, estimate as 25% of total rebounds
        """
        if fg_att is None or fg_att == 0:
            return None

        poss = fg_att + (0.44 * (ft_att or 0)) + (turnovers or 0)

        # Subtract offensive rebounds if available (estimated)
        if off_reb:
            poss -= off_reb

        return max(poss, 1)  # Ensure at least 1 possession

    def calculate_team_stats(self, classification=None):
        """Calculate statistics for all teams"""
        logger.info(f"Calculating team stats for classification: {classification or 'ALL'}")

        if not self.app:
            logger.error("App context required")
            return {}

        with self.app.app_context():
            # Get all box scores
            query = BoxScore.query

            if classification:
                query = query.filter_by(classification=classification)

            box_scores = query.all()

            logger.info(f"Processing {len(box_scores)} games")

            # Aggregate team stats
            team_stats = defaultdict(lambda: {
                'games': 0,
                'wins': 0,
                'losses': 0,
                'points_for': 0,
                'points_against': 0,
                'possessions': 0,
                'classification': classification
            })

            for bs in box_scores:
                # Process Team 1
                team1_poss = self.estimate_possessions(
                    bs.team1_fga, bs.team1_fta, bs.team1_to
                )

                if team1_poss:
                    stats1 = team_stats[bs.team1_name]
                    stats1['games'] += 1
                    stats1['points_for'] += bs.team1_score
                    stats1['points_against'] += bs.team2_score
                    stats1['possessions'] += team1_poss

                    if bs.team1_score > bs.team2_score:
                        stats1['wins'] += 1
                    else:
                        stats1['losses'] += 1

                # Process Team 2
                team2_poss = self.estimate_possessions(
                    bs.team2_fga, bs.team2_fta, bs.team2_to
                )

                if team2_poss:
                    stats2 = team_stats[bs.team2_name]
                    stats2['games'] += 1
                    stats2['points_for'] += bs.team2_score
                    stats2['points_against'] += bs.team1_score
                    stats2['possessions'] += team2_poss

                    if bs.team2_score > bs.team1_score:
                        stats2['wins'] += 1
                    else:
                        stats2['losses'] += 1

            # Calculate efficiency ratings
            ranked_teams = []

            for team_name, stats in team_stats.items():
                if stats['games'] == 0 or stats['possessions'] == 0:
                    continue

                # Offensive Efficiency: Points per 100 possessions
                off_eff = (stats['points_for'] / stats['possessions']) * 100

                # Defensive Efficiency: Points allowed per 100 possessions
                def_eff = (stats['points_against'] / stats['possessions']) * 100

                # Net Rating
                net_rating = off_eff - def_eff

                ranked_teams.append({
                    'team_name': team_name,
                    'wins': stats['wins'],
                    'losses': stats['losses'],
                    'record': f"{stats['wins']}-{stats['losses']}",
                    'adj_offensive_eff': round(off_eff, 1),
                    'adj_defensive_eff': round(def_eff, 1),
                    'net_rating': round(net_rating, 1),
                    'games_played': stats['games'],
                    'classification': stats['classification']
                })

            # Sort by net rating
            ranked_teams.sort(key=lambda x: x['net_rating'], reverse=True)

            # Add ranks
            for i, team in enumerate(ranked_teams, 1):
                team['rank'] = i

            logger.info(f"Calculated stats for {len(ranked_teams)} teams")

            return ranked_teams

    def calculate_all_rankings(self):
        """Calculate rankings for all classifications"""
        logger.info("="*50)
        logger.info("Calculating rankings from box score data")
        logger.info("="*50)

        all_rankings = {
            'last_updated': datetime.now().isoformat(),
            'uil': {},
            'private': {},
            'source': 'calculated_from_box_scores'
        }

        # UIL Classifications
        uil_classes = ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']
        for classification in uil_classes:
            teams = self.calculate_team_stats(classification)
            all_rankings['uil'][classification] = teams[:40]  # Top 40
            logger.info(f"{classification}: {len(teams)} teams ranked")

        # TAPPS Classifications
        tapps_classes = ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']
        for classification in tapps_classes:
            teams = self.calculate_team_stats(classification)
            all_rankings['private'][classification] = teams[:10]  # Top 10
            logger.info(f"{classification}: {len(teams)} teams ranked")

        return all_rankings

    def save_rankings(self, rankings, filename='data/rankings.json'):
        """Save calculated rankings to file"""
        filepath = Path(filename)
        filepath.parent.mkdir(exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(rankings, f, indent=2)

        logger.info(f"Rankings saved to {filename}")


if __name__ == '__main__':
    # Test the calculator
    print("Testing Ranking Calculator")
    print("="*50)

    # This would need app context to actually run
    print("Note: Requires Flask app context and database with box scores")
    print("Run this through the scheduler or app routes for actual calculation")
