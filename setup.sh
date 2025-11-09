#!/bin/bash

# TBBAS Complete Setup Script for Mac
# This will create all files in your current directory

echo "=========================================="
echo "TBBAS - Texas Boys Basketball Analytics System"
echo "Complete Project Setup for Mac"
echo "=========================================="
echo ""

# Create project structure
echo "Creating project directories..."
mkdir -p templates
mkdir -p static/css
mkdir -p static/js
mkdir -p .vscode

# Create requirements.txt
cat > requirements.txt << 'EOF'
flask==3.0.0
pandas==2.1.4
numpy==1.26.2
requests==2.31.0
beautifulsoup4==4.12.2
scipy==1.11.4
lxml==4.9.4
schedule==1.2.0
python-dotenv==1.0.0
gunicorn==21.2.0
EOF

# Create main app.py file
cat > app.py << 'EOF'
from flask import Flask, render_template, jsonify
import numpy as np
from datetime import datetime

app = Flask(__name__)

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
    app.run(debug=True, host='127.0.0.1', port=5000)
EOF

# Create templates
cat > templates/base.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>TBBAS - Texas Basketball Analytics</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; }
        .nav { background: #2c3e50; }
        .nav a { color: white; text-decoration: none; padding: 15px 20px; display: inline-block; }
        .nav a:hover { background: #34495e; }
        .container { max-width: 1400px; margin: 20px auto; padding: 0 20px; }
        table { width: 100%; background: white; border-radius: 8px; margin-top: 20px; }
        th { background: #f8f9fa; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #e9ecef; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Texas Boys Basketball Analytics System</h1>
        <div>KenPom-Style Ratings for Texas High School Basketball</div>
    </div>
    <nav class="nav">
        <a href="/">Home</a>
        <a href="/rankings/AAAAAA">6A</a>
        <a href="/rankings/AAAAA">5A</a>
        <a href="/rankings/AAAA">4A</a>
        <a href="/rankings/AAA">3A</a>
        <a href="/rankings/AA">2A</a>
        <a href="/rankings/A">1A</a>
        <a href="/rankings/Private">Private</a>
        <a href="/methodology">Methodology</a>
    </nav>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
EOF

cat > templates/index.html << 'EOF'
{% extends "base.html" %}
{% block content %}
<h2>2024-25 Season Rankings</h2>
<p>Select a classification above to view the Top 40 rankings.</p>
<div style="margin-top: 30px;">
    <h3>Available Classifications:</h3>
    {% for class_code, class_name in classifications.items() %}
    <div style="margin: 10px 0;">
        <a href="/rankings/{{ class_code }}" style="text-decoration: none; color: #3498db; font-size: 1.1em;">
            {{ class_name }}
        </a>
    </div>
    {% endfor %}
</div>
<p style="margin-top: 20px; color: #666;">Last Updated: {{ last_update }}</p>
{% endblock %}
EOF

cat > templates/classification.html << 'EOF'
{% extends "base.html" %}
{% block content %}
<h2>{{ classification_name }} - Top 40 Rankings</h2>
<table>
    <thead>
        <tr>
            <th>Rank</th>
            <th>Team</th>
            <th>District</th>
            <th>Record</th>
            <th>Net Rating</th>
            <th>Off Rtg</th>
            <th>Def Rtg</th>
        </tr>
    </thead>
    <tbody>
        {% for team in teams %}
        <tr>
            <td>{{ team.rank }}</td>
            <td>{{ team.team_name }}</td>
            <td>{{ team.district }}</td>
            <td>{{ team.record }}</td>
            <td>{{ team.net_rating }}</td>
            <td>{{ team.adj_offensive_eff }}</td>
            <td>{{ team.adj_defensive_eff }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
EOF

cat > templates/methodology.html << 'EOF'
{% extends "base.html" %}
{% block content %}
<h2>TBBAS Methodology</h2>
<h3>Overview</h3>
<p>KenPom-style efficiency ratings for Texas high school basketball.</p>
<h3>Core Metrics</h3>
<ul>
    <li><strong>Net Rating:</strong> Offensive - Defensive efficiency</li>
    <li><strong>Offensive Efficiency:</strong> Points per 100 possessions</li>
    <li><strong>Defensive Efficiency:</strong> Points allowed per 100 possessions</li>
</ul>
{% endblock %}
EOF

echo "✅ All files created successfully!"
echo ""
echo "Now setting up Python environment..."

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install flask pandas numpy requests beautifulsoup4 scipy

echo ""
echo "=========================================="
echo "✅ TBBAS SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "To start TBBAS:"
echo "1. source venv/bin/activate"
echo "2. python app.py"
echo "3. Open http://localhost:5000"# Make it executable
chmod +x setup.sh

# Run it
./setup.sh
# Paste the script from Step 1 here
