from flask import Flask, render_template, jsonify, redirect, url_for, request, flash
import numpy as np
from datetime import datetime
import os
import json
from pathlib import Path
from models import db, BoxScore

app = Flask(__name__)
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False') == 'True'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
instance_path = Path(__file__).parent / 'instance'
instance_path.mkdir(exist_ok=True)  # Create instance directory if it doesn't exist

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'sqlite:///' + str(instance_path / 'tbbas.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Data file path
DATA_FILE = Path(__file__).parent / 'data' / 'rankings.json'

# Ensure data directory and rankings file exist
from init_rankings import ensure_rankings_file
ensure_rankings_file()

# Start automatic scheduler
if os.getenv('FLASK_ENV') != 'development':
    # Only run scheduler in production (not during debug reloads)
    from scheduler import start_scheduler
    start_scheduler(app)

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


def load_rankings_data():
    """Load rankings from JSON file"""
    try:
        print(f"Looking for rankings file at: {DATA_FILE}")
        print(f"File exists: {DATA_FILE.exists()}")
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                print(f"Successfully loaded rankings data with {len(data.get('uil', {}))} UIL classifications")
                return data
        else:
            print(f"Rankings file not found at {DATA_FILE}")
    except Exception as e:
        print(f"Error loading rankings: {e}")
        import traceback
        traceback.print_exc()
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
        # Determine if this is a TAPPS or UIL classification
        if classification.startswith('TAPPS_'):
            # Get TAPPS classification rankings
            raw_teams = data.get('private', {}).get(classification, [])
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


@app.route('/submit-boxscore', methods=['GET', 'POST'])
def submit_boxscore():
    """Submit a box score"""
    if request.method == 'POST':
        try:
            # Create new box score
            box_score = BoxScore(
                game_date=datetime.strptime(request.form['game_date'], '%Y-%m-%d').date(),
                classification=request.form['classification'],

                # Team 1
                team1_name=request.form['team1_name'],
                team1_score=int(request.form['team1_score']),
                team1_fg=int(request.form.get('team1_fg', 0) or 0),
                team1_fga=int(request.form.get('team1_fga', 0) or 0),
                team1_3pt=int(request.form.get('team1_3pt', 0) or 0),
                team1_3pta=int(request.form.get('team1_3pta', 0) or 0),
                team1_ft=int(request.form.get('team1_ft', 0) or 0),
                team1_fta=int(request.form.get('team1_fta', 0) or 0),
                team1_reb=int(request.form.get('team1_reb', 0) or 0),
                team1_ast=int(request.form.get('team1_ast', 0) or 0),
                team1_stl=int(request.form.get('team1_stl', 0) or 0),
                team1_blk=int(request.form.get('team1_blk', 0) or 0),
                team1_to=int(request.form.get('team1_to', 0) or 0),

                # Team 2
                team2_name=request.form['team2_name'],
                team2_score=int(request.form['team2_score']),
                team2_fg=int(request.form.get('team2_fg', 0) or 0),
                team2_fga=int(request.form.get('team2_fga', 0) or 0),
                team2_3pt=int(request.form.get('team2_3pt', 0) or 0),
                team2_3pta=int(request.form.get('team2_3pta', 0) or 0),
                team2_ft=int(request.form.get('team2_ft', 0) or 0),
                team2_fta=int(request.form.get('team2_fta', 0) or 0),
                team2_reb=int(request.form.get('team2_reb', 0) or 0),
                team2_ast=int(request.form.get('team2_ast', 0) or 0),
                team2_stl=int(request.form.get('team2_stl', 0) or 0),
                team2_blk=int(request.form.get('team2_blk', 0) or 0),
                team2_to=int(request.form.get('team2_to', 0) or 0),

                submitted_by=request.form.get('submitted_by', '')
            )

            db.session.add(box_score)
            db.session.commit()

            flash('Box score submitted successfully!', 'success')
            return redirect(url_for('submit_boxscore'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting box score: {str(e)}', 'error')

    return render_template('submit_boxscore.html', classifications=CLASSIFICATIONS)


@app.route('/boxscores')
def view_boxscores():
    """View all box scores"""
    # Get filter parameters
    classification = request.args.get('classification')
    team = request.args.get('team')

    query = BoxScore.query.order_by(BoxScore.game_date.desc())

    if classification:
        query = query.filter_by(classification=classification)

    if team:
        query = query.filter(
            (BoxScore.team1_name.ilike(f'%{team}%')) |
            (BoxScore.team2_name.ilike(f'%{team}%'))
        )

    boxscores = query.limit(100).all()

    return render_template('boxscores.html',
                         boxscores=boxscores,
                         classifications=CLASSIFICATIONS)


@app.route('/api/boxscores/<classification>')
def api_boxscores(classification):
    """API endpoint to get box scores for a classification"""
    boxscores = BoxScore.query.filter_by(classification=classification)\
        .order_by(BoxScore.game_date.desc())\
        .limit(50)\
        .all()

    return jsonify([bs.to_dict() for bs in boxscores])


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
