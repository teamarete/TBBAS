"""
Rankings Blueprint
Handles all ranking-related routes and views
"""
from flask import Blueprint, render_template, jsonify
from pathlib import Path
from datetime import datetime
import json

# Create blueprint (no url_prefix to maintain existing routes)
rankings_bp = Blueprint('rankings', __name__)

# Data file path
DATA_FILE = Path(__file__).parent.parent.parent / 'data' / 'rankings.json'


def load_rankings_data():
    """Load rankings from JSON file"""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading rankings: {e}")
        return None


CLASSIFICATIONS = {
    'AAAAAA': 'Class 6A (UIL)',
    'AAAAA': 'Class 5A (UIL)',
    'AAAA': 'Class 4A (UIL)',
    'AAA': 'Class 3A (UIL)',
    'AA': 'Class 2A (UIL)',
    'A': 'Class 1A (UIL)',
    'TAPPS_6A': 'TAPPS 6A / SPC 4A',
    'TAPPS_5A': 'TAPPS 5A / SPC 3A',
    'TAPPS_4A': 'TAPPS 4A',
    'TAPPS_3A': 'TAPPS 3A',
    'TAPPS_2A': 'TAPPS 2A',
    'TAPPS_1A': 'TAPPS 1A'
}


def get_last_update():
    """Get formatted last update timestamp"""
    data = load_rankings_data()
    if data and 'last_updated' in data:
        try:
            dt = datetime.fromisoformat(data['last_updated'])
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            pass
    return datetime.now().strftime('%B %d, %Y')


@rankings_bp.route('/')
def index():
    """Home page showing all classifications"""
    return render_template('index.html',
                          classifications=CLASSIFICATIONS,
                          last_update=get_last_update())


@rankings_bp.route('/rankings/<classification>')
def classification_rankings(classification):
    """Show rankings for specific classification"""
    if classification not in CLASSIFICATIONS:
        return "Classification not found", 404

    # Load data
    data = load_rankings_data()
    teams = []

    if data:
        # Determine if this is a TAPPS or UIL classification
        if classification.startswith('TAPPS_'):
            # Get TAPPS classification rankings
            raw_teams = data.get('private', {}).get(classification, [])
        else:
            # Get UIL classification rankings
            raw_teams = data.get('uil', {}).get(classification, [])

        # Always show complete rankings: UIL Top 25, TAPPS Top 10
        max_rank = 10 if classification.startswith('TAPPS_') else 25

        # Sort teams by rank (None ranks go to end)
        sorted_teams = sorted(raw_teams, key=lambda x: x.get('rank') if x.get('rank') is not None else 9999)

        # Process teams - take only those with ranks 1 through max_rank
        for team_data in sorted_teams:
            team_rank = team_data.get('rank')

            # Only include teams with valid rank within limit (1-25 or 1-10)
            if team_rank is None or team_rank < 1 or team_rank > max_rank:
                continue

            team = {
                'rank': team_rank,
                'team_name': team_data.get('team_name', 'Unknown'),
                'wins': team_data.get('wins'),
                'losses': team_data.get('losses'),
                'record': '',
                'district': team_data.get('district', ''),
                'ppg': team_data.get('ppg'),
                'opp_ppg': team_data.get('opp_ppg'),
                'games': team_data.get('games'),
                # Analytics from database
                'net_rating': team_data.get('net_rating'),
                'adj_offensive_eff': team_data.get('adj_offensive_eff'),
                'adj_defensive_eff': team_data.get('adj_defensive_eff'),
                'adj_tempo': team_data.get('adj_tempo'),
                'sos_rating': team_data.get('sos_rating')
            }

            # Format record if available
            if team['wins'] is not None and team['losses'] is not None:
                team['record'] = f"{team['wins']}-{team['losses']}"

            teams.append(team)

        # Ensure teams are sorted by rank for display
        teams.sort(key=lambda x: x['rank'])

    # If no data, show message
    if not teams:
        teams = [{
            'rank': 0,
            'team_name': 'No rankings data available. Run scraper.py to fetch latest rankings.',
            'record': '',
            'district': '',
            'net_rating': None,
            'adj_offensive_eff': None,
            'adj_defensive_eff': None
        }]

    return render_template('classification.html',
                         classification=classification,
                         classification_name=CLASSIFICATIONS[classification],
                         teams=teams,
                         last_update=get_last_update())


@rankings_bp.route('/api/rankings')
def api_rankings():
    """API endpoint returning all rankings as JSON"""
    data = load_rankings_data()

    if not data:
        return jsonify({'error': 'Unable to load rankings'}), 500

    return jsonify(data)


@rankings_bp.route('/api/rankings/<classification>')
def api_classification(classification):
    """API endpoint for specific classification"""
    data = load_rankings_data()

    if not data:
        return jsonify({'error': 'Unable to load rankings'}), 500

    # Determine league
    if classification.startswith('TAPPS_'):
        teams = data.get('private', {}).get(classification, [])
    else:
        teams = data.get('uil', {}).get(classification, [])

    if not teams:
        return jsonify({'error': f'Classification {classification} not found'}), 404

    return jsonify({
        'classification': classification,
        'teams': teams,
        'last_updated': data.get('last_updated')
    })


@rankings_bp.route('/methodology')
def methodology():
    """Methodology page explaining ranking system"""
    return render_template('methodology.html')
