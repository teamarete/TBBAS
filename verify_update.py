import json

with open('data/rankings.json') as f:
    data = json.load(f)

print('Last updated:', data.get('last_updated'))
print('Source:', data.get('source'))
print('\nUIL 6A Top 5:')

teams = data['uil']['AAAAAA']
for t in [t for t in teams if t.get('rank') and t.get('rank') <= 5]:
    record = f"{t.get('wins')}-{t.get('losses')}" if t.get('wins') is not None else '—'
    print(f"  {t['rank']}. {t['team_name']} ({record})")
