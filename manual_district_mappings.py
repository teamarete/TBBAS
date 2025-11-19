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

    # 5A Schools (AAAAA)
    ('Frisco Heritage', 'AAAAA'): '11',  # Frisco Heritage
    ('Heritage', 'AAAAA'): '11',

    ('Frisco Memorial', 'AAAAA'): '11',  # Frisco Memorial
    ('Memorial', 'AAAAA'): '11',

    ('Dallas Highland Park', 'AAAAA'): '12',  # Dallas Highland Park
    ('Highland Park', 'AAAAA'): '12',

    ('Killeen Ellison', 'AAAAA'): '16',  # Killeen Ellison
    ('Ellison', 'AAAAA'): '16',

    ('Beaumont United', 'AAAAA'): '19',  # Beaumont United
    ('Bmt United', 'AAAAA'): '19',

    ('Beaumont West Brook', 'AAAAA'): '19',  # Beaumont West Brook
    ('West Brook', 'AAAAA'): '19',
    ('Bmt West Brook', 'AAAAA'): '19',

    ('Port Arthur Memorial', 'AAAAA'): '19',  # Port Arthur Memorial
    ('PA Memorial', 'AAAAA'): '19',

    ('San Antonio Alamo Heights', 'AAAAA'): '26',  # San Antonio Alamo Heights
    ('SA Alamo Heights', 'AAAAA'): '26',
    ('Alamo Heights', 'AAAAA'): '26',

    ('San Antonio Wagner', 'AAAAA'): '26',  # San Antonio Wagner
    ('SA Wagner', 'AAAAA'): '26',
    ('Wagner', 'AAAAA'): '26',

    ('Northside Jay', 'AAAAA'): '28',  # Northside Jay (San Antonio)
    ('SA Jay', 'AAAAA'): '28',
    ('San Antonio Jay', 'AAAAA'): '28',
    ('Jay', 'AAAAA'): '28',

    ('Corpus Christi Veterans Memorial', 'AAAAA'): '29',  # Corpus Christi Veterans Memorial
    ('CC Veterans Memorial', 'AAAAA'): '29',
    ('Veterans Memorial', 'AAAAA'): '29',

    # 4A Schools (AAAA)
    ('Lubbock Estacado', 'AAAA'): '5',  # Lubbock Estacado
    ('Estacado', 'AAAA'): '5',

    ('Burkburnett', 'AAAA'): '7',  # Burkburnett

    ('Krum', 'AAAA'): '7',  # Krum

    ('Dallas Carter', 'AAAA'): '11',  # Dallas Carter
    ('Carter', 'AAAA'): '11',

    ('Dallas Kimball', 'AAAA'): '11',  # Dallas Kimball
    ('Kimball', 'AAAA'): '11',

    ('Austin Johnson', 'AAAA'): '25',  # Austin Johnson (LBJ)
    ('Austin LBJ', 'AAAA'): '25',
    ('LBJ', 'AAAA'): '25',
    ('Johnson', 'AAAA'): '25',

    ('Comal Davenport', 'AAAA'): '26',  # Comal Davenport
    ('Davenport', 'AAAA'): '26',

    ('Wimberley', 'AAAA'): '26',  # Wimberley
    ('Wimberly', 'AAAA'): '26',  # Common misspelling

    # 3A Schools (AAA)
    ('Tuscola Jim Ned', 'AAA'): '6',  # Tuscola Jim Ned
    ('Jim Ned', 'AAA'): '6',

    ('Wichita Falls City View', 'AAA'): '7',  # Wichita Falls City View
    ('City View', 'AAA'): '7',

    ('Jefferson', 'AAA'): '13',  # Jefferson

    ('Hooks', 'AAA'): '14',  # Hooks

    ('Texarkana Liberty-Eylau', 'AAA'): '14',  # Texarkana Liberty-Eylau
    ('Liberty-Eylau', 'AAA'): '14',
    ('Liberty Eylau', 'AAA'): '14',  # Without hyphen

    ('Tatum', 'AAA'): '16',  # Tatum

    ('Poth', 'AAA'): '26',  # Poth

    ('San Antonio Cole', 'AAA'): '27',  # San Antonio Cole
    ('SA Cole', 'AAA'): '27',
    ('Cole', 'AAA'): '27',

    ('Crystal City', 'AAA'): '28',  # Crystal City

    ('Lytle', 'AAA'): '28',  # Lytle

    ('Aransas Pass', 'AAA'): '29',  # Aransas Pass

    ('Corpus Christi London', 'AAA'): '29',  # Corpus Christi London
    ('CC London', 'AAA'): '29',
    ('London', 'AAA'): '29',

    # 2A Schools (AA)
    ('Thorndale', 'AA'): '27',  # Thorndale

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
