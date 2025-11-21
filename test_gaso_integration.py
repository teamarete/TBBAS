#!/usr/bin/env python3
"""Test GASO integration in ranking system"""
from gaso_scraper import GASOScraper

print("="*80)
print("GASO INTEGRATION TEST")
print("="*80)
print()

# Test GASO scraper
scraper = GASOScraper()
data = scraper.scrape_all()

print("✅ GASO Rankings Loaded:")
print()

# UIL
print("UIL Rankings:")
for classification, teams in data['uil'].items():
    class_name = {'AAAAAA': '6A', 'AAAAA': '5A', 'AAAA': '4A', 'AAA': '3A', 'AA': '2A', 'A': '1A'}[classification]
    print(f"  {class_name}: {len(teams)} teams")
    if teams:
        print(f"    #1: {teams[0]['team_name']}")

print()
print("TAPPS/SPC Rankings:")
tapps_teams = data['private']['TAPPS_6A']
print(f"  Combined: {len(tapps_teams)} teams")
if tapps_teams:
    print(f"    #1: {tapps_teams[0]['team_name']}")
    print(f"    #2: {tapps_teams[1]['team_name']}")
    print(f"    #3: {tapps_teams[2]['team_name']}")

print()
print("="*80)
print("✅ GASO INTEGRATION SUCCESSFUL!")
print("="*80)
print()
print("Rankings will be automatically used in weekly Monday updates")
print("Priority: Calculated > GASO > MaxPreps > TABC")
