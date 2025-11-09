from flask import Flask, render_template, jsonify, redirect, url_for
import numpy as np
from datetime import datetime
import os
import json
from pathlib import Path

app = Flask(__name__)
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False') == 'True'

# Data file path
DATA_FILE = Path(__file__).parent / 'data' / 'rankings.json'

CLASSIFICATIONS = {
    'AAAAAA': 'Class 6A',
    'AAAAA': 'Class 5A',
    'AAAA': 'Class 4A',
    'AAA': 'Class 3A',
    'AA': 'Class 2A',
    'A': 'Class 1A',
    'Private': 'Private Schools (TAPPS/SPC)'
}


def load_rankings_data():
    """Load rankings from JSON file"""
    try:
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading rankings: {e}")
    return None


def get_last_update():
    """Get last update timestamp"""
    data = load_rankings_data()
    if data and 'last_updated' in data:
        try:
            dt = datetime.fromisoformat(data['last_updated'])
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            pass
    return datetime.now().strftime('%B %d, %Y')

@app.route('/')
def index():
    return render_template('index.html',
                         classifications=CLASSIFICATIONS,
                         last_update=get_last_update())

@app.route('/rankings/<classification>')
def classification_rankings(classification):
    if classification not in CLASSIFICATIONS:
        return "Classification not found", 404

    # Load data
    data = load_rankings_data()
    teams = []

    if data:
        if classification == 'Private':
            # Get private school rankings
            raw_teams = data.get('private', [])
        else:
            # Get UIL classification rankings
            raw_teams = data.get('uil', {}).get(classification, [])

        # Process teams
        for team_data in raw_teams:
            team = {
                'rank': team_data.get('rank', 0),
                'team_name': team_data.get('team_name', 'Unknown'),
                'wins': team_data.get('wins'),
                'losses': team_data.get('losses'),
                'record': '',
                'district': team_data.get('district', ''),
                # Placeholder analytics - will be calculated from game data later
                'net_rating': None,
                'adj_offensive_eff': None,
                'adj_defensive_eff': None,
                'adj_tempo': None,
                'sos_rating': None
            }

            # Format record if available
            if team['wins'] is not None and team['losses'] is not None:
                team['record'] = f"{team['wins']}-{team['losses']}"

            teams.append(team)

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

@app.route('/methodology')
def methodology():
    return render_template('methodology.html')


@app.route('/refresh')
def refresh_data():
    """Refresh rankings data from TABC"""
    try:
        from scraper import TABCScraper
        scraper = TABCScraper()
        data = scraper.scrape_all()

        if data:
            scraper.save_to_file(data)
            return jsonify({
                'status': 'success',
                'message': 'Rankings updated successfully',
                'last_updated': data.get('last_updated')
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to fetch rankings'
            }), 500

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*50)
    print("TBBAS Server Starting...")
    print("="*50)
    print("\nAccess the application at:")
    print("  → http://localhost:5000")
    print("\nPress Ctrl+C to stop the server\n")

    # Use environment variables for host and port
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True') == 'True'

    app.run(debug=debug, host=host, port=port)
