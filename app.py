from flask import Flask, render_template, jsonify
import numpy as np
from datetime import datetime
import os

app = Flask(__name__)
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False') == 'True'

CLASSIFICATIONS = {
    'AAAAAA': 'Class 6A',
    'AAAAA': 'Class 5A',
    'AAAA': 'Class 4A',
    'AAA': 'Class 3A',
    'AA': 'Class 2A',
    'A': 'Class 1A',
    'Private': 'Private Schools (TAPPS/SPC)'
}

@app.route('/')
def index():
    return render_template('index.html', 
                         classifications=CLASSIFICATIONS,
                         last_update=datetime.now().strftime('%B %d, %Y'))

@app.route('/rankings/<classification>')
def classification_rankings(classification):
    if classification not in CLASSIFICATIONS:
        return "Classification not found", 404
    
    teams = []
    for i in range(1, 41):
        teams.append({
            'rank': i,
            'team_name': f'Team {i}',
            'wins': np.random.randint(15, 30),
            'losses': np.random.randint(0, 10),
            'net_rating': round(25 - i * 0.5 + np.random.random() * 5, 1),
            'adj_offensive_eff': round(105 - i * 0.3, 1),
            'adj_defensive_eff': round(95 + i * 0.2, 1),
            'adj_tempo': round(65 + np.random.random() * 10, 1),
            'sos_rating': round(np.random.random() * 10, 1),
            'district': f'{np.random.randint(1, 13)}',
            'record': ''
        })
    
    for team in teams:
        team['record'] = f"{team['wins']}-{team['losses']}"
    
    return render_template('classification.html',
                         classification=classification,
                         classification_name=CLASSIFICATIONS[classification],
                         teams=teams,
                         last_update=datetime.now().strftime('%B %d, %Y'))

@app.route('/methodology')
def methodology():
    return render_template('methodology.html')

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
