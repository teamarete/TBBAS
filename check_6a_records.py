"""Check UIL 6A record coverage"""
import json

with open('data/rankings.json') as f:
    data = json.load(f)

teams = data['uil']['AAAAAA']
ranked_teams = [t for t in teams if t.get('rank')]
teams_with_records = [t for t in ranked_teams if t.get('wins') is not None]

print(f"UIL 6A: {len(teams_with_records)}/{len(ranked_teams)} ranked teams have records\n")
print("Teams WITHOUT records:")
for t in ranked_teams:
    if t.get('wins') is None:
        print(f"  Rank {t.get('rank')}: {t.get('team_name')}")
