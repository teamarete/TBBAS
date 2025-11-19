"""
Manual District Mappings for Schools Not Found in UIL Data

These schools are in TABC rankings but can't be automatically matched to UIL schools
due to UIL PDF parsing issues (truncated names) or naming discrepancies.

Format: (team_name, classification) -> district_number
"""

MANUAL_DISTRICTS = {
    # 6A Schools
    ('SA Brennan', 'AAAAAA'): '27',  # San Antonio Brennan
    ('San Antonio Brennan', 'AAAAAA'): '27',
    ('Brennan', 'AAAAAA'): '27',

    ('SA Harlan', 'AAAAAA'): '28',  # San Antonio Harlan
    ('San Antonio Harlan', 'AAAAAA'): '28',
    ('Harlan', 'AAAAAA'): '28',

    ('Steele', 'AAAAAA'): '27',  # Cibolo Steele
    ('Cibolo Steele', 'AAAAAA'): '27',

    ('Katy Seven Lakes', 'AAAAAA'): '1',  # Katy Seven Lakes
    ('Seven Lakes', 'AAAAAA'): '1',

    ('Little Elm', 'AAAAAA'): '5',  # Little Elm (Denton area)

    ('Conroe Grand Oaks', 'AAAAAA'): '13',  # Conroe Grand Oaks
    ('Grand Oaks', 'AAAAAA'): '13',

    ('Austin Westlake', 'AAAAAA'): '26',  # Austin Westlake
    ('Westlake', 'AAAAAA'): '26',

    ('Arl Martin', 'AAAAAA'): '8',  # Arlington Martin
    ('Arlington Martin', 'AAAAAA'): '8',
    ('Martin', 'AAAAAA'): '8',

    ('Mesquite Horn', 'AAAAAA'): '11',  # Mesquite Horn
    ('Horn', 'AAAAAA'): '11',

    ('Cy Falls', 'AAAAAA'): '17',  # Cypress Falls
    ('Cypress Falls', 'AAAAAA'): '17',

    ('Katy Jordan', 'AAAAAA'): '19',  # Katy Jordan
    ('Jordan', 'AAAAAA'): '19',

    ('Katy Seven Lakes', 'AAAAAA'): '19',  # Katy Seven Lakes
    ('Seven Lakes', 'AAAAAA'): '19',

    ('Summer Creek', 'AAAAAA'): '22',  # Alvin Shadow Creek
    ('Alvin Shadow Creek', 'AAAAAA'): '22',
    ('Humble Summer Creek', 'AAAAAA'): '22',

    ('SA Brennan', 'AAAAAA'): '28',  # Northside Brennan (San Antonio)
    ('San Antonio Brennan', 'AAAAAA'): '28',
    ('Brennan', 'AAAAAA'): '28',
    ('Northside Brennan', 'AAAAAA'): '28',

    ('Steele', 'AAAAAA'): '29',  # Cibolo Steele
    ('Cibolo Steele', 'AAAAAA'): '29',

    ('Converse Judson', 'AAAAAA'): '29',  # Converse Judson
    ('Judson', 'AAAAAA'): '29',

    ('Vandegrift', 'AAAAAA'): '25',  # Vandegrift (Austin area)

    # 5A Schools (add as needed)

    # 4A Schools (add as needed)

    # 3A Schools (add as needed)

    # 2A Schools (add as needed)

    # 1A Schools (add as needed)
}

def get_manual_district(team_name, classification):
    """
    Get district number for a team from manual mappings

    Args:
        team_name: Team name from rankings
        classification: Classification code (e.g., 'AAAAAA')

    Returns:
        District number (string) or None if not found
    """
    return MANUAL_DISTRICTS.get((team_name, classification))


def add_manual_mapping(team_name, classification, district):
    """
    Add a new manual district mapping

    Args:
        team_name: Team name
        classification: Classification code
        district: District number (string)
    """
    MANUAL_DISTRICTS[(team_name, classification)] = district


if __name__ == "__main__":
    # Test the manual mappings
    test_teams = [
        ('SA Brennan', 'AAAAAA'),
        ('Steele', 'AAAAAA'),
        ('Little Elm', 'AAAAAA'),
        ('Katy Seven Lakes', 'AAAAAA'),
    ]

    print("Manual District Mappings Test")
    print("=" * 60)
    for team_name, classification in test_teams:
        district = get_manual_district(team_name, classification)
        print(f"{team_name} ({classification}): District {district}")
