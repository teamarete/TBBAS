"""
Initialize rankings on startup
This runs when the app starts to ensure rankings.json exists with current data
"""

import os
import json
from pathlib import Path

def ensure_rankings_file():
    """Ensure rankings.json exists and has data"""
    data_dir = Path(__file__).parent / 'data'
    rankings_file = data_dir / 'rankings.json'

    # Create data directory if it doesn't exist
    data_dir.mkdir(exist_ok=True)

    # Check if rankings file exists and has recent data
    if rankings_file.exists():
        try:
            with open(rankings_file, 'r') as f:
                data = json.load(f)
                if 'last_updated' in data:
                    print(f"Rankings file exists with update: {data['last_updated']}")
                    return True
        except Exception as e:
            print(f"Error reading rankings file: {e}")

    print("Rankings file missing or invalid - will be created on first ranking update")
    return False

if __name__ == "__main__":
    ensure_rankings_file()
