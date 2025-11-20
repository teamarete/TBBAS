#!/usr/bin/env python3
"""
Initialize ALL UIL and TAPPS schools in rankings
- Load all schools from district mappings
- Initialize with districts but no rank
- Preserve existing ranked teams and their data
- Expand coverage from 210 to 2,000+ schools
"""

import json
from datetime import datetime
from manual_district_mappings import MANUAL_DISTRICTS
from tapps_district_mappings import TAPPS_DISTRICTS
from uil_school_matcher import UILSchoolMatcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_all_uil_schools():
    """Get all UIL schools from district mappings"""
    schools_by_class = {
        'AAAAAA': set(),
        'AAAAA': set(),
        'AAAA': set(),
        'AAA': set(),
        'AA': set(),
        'A': set()
    }

    # From manual mappings
    for (school_name, classification), district in MANUAL_DISTRICTS.items():
        if classification in schools_by_class:
            schools_by_class[classification].add((school_name, district))

    # From UIL official data
    try:
        # Load UIL data
        uil_file = 'data/uil_schools.json'
        with open(uil_file, 'r') as f:
            uil_data = json.load(f)

        # UIL file is structured as: {"6A": [...], "5A": [...], etc}
        for class_name, schools in uil_data.items():
            for school in schools:
                classification_code = school.get('classification_code')
                district = school.get('district')
                school_name = school.get('school_name')

                if classification_code in schools_by_class and district and school_name:
                    schools_by_class[classification_code].add((school_name, district))

        logger.info("Loaded UIL official data")
    except Exception as e:
        logger.warning(f"Could not load UIL data: {e}")

    logger.info("UIL Schools Summary:")
    for classification, schools in schools_by_class.items():
        logger.info(f"  {classification}: {len(schools)} schools")

    total = sum(len(schools) for schools in schools_by_class.values())
    logger.info(f"Total UIL Schools: {total}")

    return schools_by_class


def get_all_tapps_schools():
    """Get all TAPPS schools from district mappings"""
    schools_by_class = {
        'TAPPS_6A': set(),
        'TAPPS_5A': set(),
        'TAPPS_4A': set(),
        'TAPPS_3A': set(),
        'TAPPS_2A': set(),
        'TAPPS_1A': set()
    }

    # From TAPPS mappings
    for (school_name, classification), district in TAPPS_DISTRICTS.items():
        if classification in schools_by_class and district:
            schools_by_class[classification].add((school_name, district))

    logger.info("\nTAPPS Schools Summary:")
    for classification, schools in schools_by_class.items():
        logger.info(f"  {classification}: {len(schools)} schools")

    total = sum(len(schools) for schools in schools_by_class.values())
    logger.info(f"Total TAPPS Schools: {total}")

    return schools_by_class


def initialize_all_schools():
    """
    Initialize rankings with ALL schools
    - Preserve existing ranked teams (with their ranks, records, stats)
    - Add all other schools as unranked (rank: null)
    - All schools get districts
    """
    logger.info("=" * 80)
    logger.info("INITIALIZING ALL SCHOOLS IN RANKINGS")
    logger.info("=" * 80)

    # Load existing rankings
    try:
        with open('data/rankings.json', 'r') as f:
            existing_data = json.load(f)
        logger.info("Loaded existing rankings")
    except Exception as e:
        logger.error(f"Could not load existing rankings: {e}")
        existing_data = {'uil': {}, 'private': {}}

    # Get all schools from mappings
    all_uil_schools = get_all_uil_schools()
    all_tapps_schools = get_all_tapps_schools()

    # Initialize new rankings structure
    new_rankings = {
        'last_updated': datetime.now().isoformat(),
        'source': 'expanded_all_schools',
        'uil': {},
        'private': {}
    }

    # Process UIL schools
    logger.info("\n" + "=" * 80)
    logger.info("PROCESSING UIL SCHOOLS")
    logger.info("=" * 80)

    for classification in ['AAAAAA', 'AAAAA', 'AAAA', 'AAA', 'AA', 'A']:
        logger.info(f"\nProcessing {classification}...")

        # Get existing ranked teams for this classification
        existing_teams = existing_data.get('uil', {}).get(classification, [])
        existing_by_name = {team['team_name']: team for team in existing_teams}

        # Get all schools for this classification
        all_schools = all_uil_schools.get(classification, set())

        # Create team list
        teams = []
        ranked_teams = []
        unranked_teams = []

        # First, add all existing ranked teams (preserve their data)
        for school_name, district in all_schools:
            if school_name in existing_by_name:
                # This school is already ranked - preserve all its data
                team = existing_by_name[school_name].copy()
                ranked_teams.append(team)
            else:
                # This school is new/unranked - add with district but no rank
                team = {
                    'team_name': school_name,
                    'district': str(district),
                    'rank': None,  # Unranked
                    'wins': None,
                    'losses': None,
                    'games': None,
                    'ppg': None,
                    'opp_ppg': None
                }
                unranked_teams.append(team)

        # Sort ranked teams by rank (handle None values)
        ranked_teams.sort(key=lambda x: x.get('rank') if x.get('rank') is not None else 999)

        # Sort unranked teams alphabetically
        unranked_teams.sort(key=lambda x: x['team_name'])

        # Combine: ranked first, then unranked
        teams = ranked_teams + unranked_teams

        new_rankings['uil'][classification] = teams

        logger.info(f"  {classification}: {len(ranked_teams)} ranked + {len(unranked_teams)} unranked = {len(teams)} total")

    # Process TAPPS schools
    logger.info("\n" + "=" * 80)
    logger.info("PROCESSING TAPPS SCHOOLS")
    logger.info("=" * 80)

    for classification in ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']:
        logger.info(f"\nProcessing {classification}...")

        # Get existing ranked teams for this classification
        existing_teams = existing_data.get('private', {}).get(classification, [])
        existing_by_name = {team['team_name']: team for team in existing_teams}

        # Get all schools for this classification
        all_schools = all_tapps_schools.get(classification, set())

        # Create team list
        teams = []
        ranked_teams = []
        unranked_teams = []

        # First, add all existing ranked teams (preserve their data)
        for school_name, district in all_schools:
            if school_name in existing_by_name:
                # This school is already ranked - preserve all its data
                team = existing_by_name[school_name].copy()
                ranked_teams.append(team)
            else:
                # This school is new/unranked - add with district but no rank
                team = {
                    'team_name': school_name,
                    'district': str(district),
                    'rank': None,  # Unranked
                    'wins': None,
                    'losses': None,
                    'games': None,
                    'ppg': None,
                    'opp_ppg': None
                }
                unranked_teams.append(team)

        # Sort ranked teams by rank (handle None values)
        ranked_teams.sort(key=lambda x: x.get('rank') if x.get('rank') is not None else 999)

        # Sort unranked teams alphabetically
        unranked_teams.sort(key=lambda x: x['team_name'])

        # Combine: ranked first, then unranked
        teams = ranked_teams + unranked_teams

        new_rankings['private'][classification] = teams

        logger.info(f"  {classification}: {len(ranked_teams)} ranked + {len(unranked_teams)} unranked = {len(teams)} total")

    # Save expanded rankings
    logger.info("\n" + "=" * 80)
    logger.info("SAVING EXPANDED RANKINGS")
    logger.info("=" * 80)

    # Create backup of old rankings
    import shutil
    try:
        shutil.copy('data/rankings.json', 'data/rankings_backup_before_expansion.json')
        logger.info("Created backup: data/rankings_backup_before_expansion.json")
    except Exception as e:
        logger.warning(f"Could not create backup: {e}")

    # Save new rankings
    with open('data/rankings.json', 'w') as f:
        json.dump(new_rankings, f, indent=2)

    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("EXPANSION COMPLETE!")
    logger.info("=" * 80)

    total_uil = sum(len(teams) for teams in new_rankings['uil'].values())
    total_tapps = sum(len(teams) for teams in new_rankings['private'].values())
    total = total_uil + total_tapps

    logger.info(f"\nFinal Rankings Summary:")
    logger.info(f"  UIL Schools: {total_uil}")
    logger.info(f"  TAPPS Schools: {total_tapps}")
    logger.info(f"  TOTAL SCHOOLS: {total}")

    logger.info(f"\n✓ Rankings saved to data/rankings.json")
    logger.info(f"✓ Expanded from 210 to {total} schools!")


if __name__ == '__main__':
    initialize_all_schools()
