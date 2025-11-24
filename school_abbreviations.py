"""
School Name Abbreviation Mappings
Maps common abbreviations used in TABC rankings to full names used in UIL data
"""

# City/Location abbreviations
CITY_ABBREVIATIONS = {
    'SA': 'San Antonio',
    'Arl': 'Arlington',
    'Mans': 'Mansfield',
    'FB': 'Fort Bend',
    'FW': 'Fort Worth',
    'CC': 'Corpus Christi',
    'EP': 'El Paso',
    'Bmt': 'Beaumont',
    'PA': 'Port Arthur',
    'H': 'Houston',
    'Hou': 'Houston',
    'Cy': 'Cypress',
    'Cyp': 'Cypress',
    'Kat': 'Katy',
    'Pfl': 'Pflugerville',
    'McA': 'McAllen',
    'SGP': 'San Grande Plains',
    'LV': 'La Vega',
    'SL': 'South Lake',
}

# School name abbreviations
SCHOOL_ABBREVIATIONS = {
    'HS': 'High School',
    'Mem': 'Memorial',
    'Cent': 'Central',
    'Tech': 'Technical',
    'Prep': 'Preparatory',
    'Acad': 'Academy',
    'Chr': 'Christian',
}

# Special case mappings - full TABC name to UIL name pattern
SPECIAL_CASES = {
    # Format: 'TABC Name': 'UIL Name Pattern'
    'North Crowley': 'North Crowley',  # Could be in "Mansfield Legacy North Crowley"
    'Duncanville': 'Duncanville',      # Could be in "De Soto Duncanville"
    'Atascocita': 'Atascocita',        # Could be in "Humble Humble Atascocita"
    'Katy Seven Lakes': 'Seven Lakes',
    'Katy Jordan': 'Jordan',
    'Steele': 'Cibolo Steele',         # Cibolo Steele
    'Little Elm': 'Little Elm',
    'Summer Creek': 'Alvin Shadow Creek',  # Summer Creek is actually Alvin Shadow Creek
    'Cy Falls': 'Cypress Falls',       # Cy Falls is Cypress Falls
    'SA Harlan': 'Harlan',             # San Antonio Harlan -> Harlan in database
    'Mans Lake Ridge': 'Lake Ridge',   # Mansfield Lake Ridge -> Lake Ridge in database
    'Odessa Permian': 'Permian',       # Odessa Permian -> Permian in database
    'Austin Westlake': 'Westlake',     # Austin Westlake -> Westlake in database
    'Conroe Grand Oaks': 'Grand Oaks', # Conroe Grand Oaks -> Grand Oaks in database
    'Converse Judson': 'Judson',       # Converse Judson -> Judson in database
    'Mesquite Horn': 'Horn',           # Mesquite Horn -> Horn in database
    # UIL teams
    'Leander Glenn': 'Glenn',          # Leander Glenn -> Glenn in database
    'Dallas Kimball': 'Kimball',       # Dallas Kimball -> Kimball in database
    'Dallas Carter': 'Carter',         # Dallas Carter -> Carter in database
    'Dallas Lincoln': 'Juarez-Lincoln', # Dallas Lincoln -> Juarez-Lincoln in database
    'Liberty Eylau': 'Liberty-Eylau',  # Liberty Eylau -> Liberty-Eylau in database
    'Westwood': 'Round Rock Westwood', # Westwood (3A) -> Round Rock Westwood in database
    'Dallas Madison': 'Madison',       # Dallas Madison -> Madison in database
    'San Augustine': 'St. Augustine',  # San Augustine -> St. Augustine in database
    'Waco Meyer': 'Meyer',             # Waco Meyer -> Meyer in database
    # TAPPS teams
    'Dallas Parish Episcopal': 'Episcopal School of Dallas',  # 7 games
    'Plano John Paul II': 'John Paul II',  # 11 games
    'Mckinney Christian': 'McKinney Christian Academy',  # 5 games
    'Houston St. Francis': 'St. Francis Episcopal',  # 2 games
    'Tyler Bishop Gorman': 'Bishop Gorman',  # 2 games
    'Houston Westbury': 'Westbury',  # 3 games
    'San Antonio Holy Cross': 'Holy Cross',  # 5 games
    'Boerne Geneva': 'Geneva',  # 1 games
    'Dallas Yavneh': 'Yavneh Academy',  # 1 games
    'Waco Live Oak': 'Live Oak Classical',  # 1 games
    'Faith Academy of Marble Falls': 'Marble Falls',  # 5 games (WARNING: Could conflict with UIL Marble Falls)
    'Huntsville Alpha Omega': 'Alpha Omega Academy',  # 1 games
    'Keene Chisholm Trail': 'Chisholm Trail',  # 3 games
    'Fort Worth Covenant': 'Covenant Classical',  # 4 games
    'Denton Calvary': 'Calvary Academy',  # 3 games
    'Austin San Juan Diego': 'San Juan Diego Catholic',  # 4 games
}

def expand_abbreviations(school_name):
    """
    Expand abbreviations in school name

    Examples:
        'SA Brennan' -> 'San Antonio Brennan'
        'Mans Lake Ridge' -> 'Mansfield Lake Ridge'
        'FB Marshall' -> 'Fort Bend Marshall'
    """
    # Split name into parts
    parts = school_name.split()

    # Expand each part if it's an abbreviation
    expanded_parts = []
    for i, part in enumerate(parts):
        # Check city abbreviations
        if part in CITY_ABBREVIATIONS:
            expanded_parts.append(CITY_ABBREVIATIONS[part])
        # Check school abbreviations
        elif part in SCHOOL_ABBREVIATIONS:
            expanded_parts.append(SCHOOL_ABBREVIATIONS[part])
        else:
            expanded_parts.append(part)

    return ' '.join(expanded_parts)

def get_search_variations(school_name):
    """
    Generate multiple search variations of a school name for better matching

    Returns a list of possible name variations to search for
    """
    variations = []

    # Original name
    variations.append(school_name)

    # Expanded abbreviations
    expanded = expand_abbreviations(school_name)
    if expanded != school_name:
        variations.append(expanded)

    # Check special cases
    if school_name in SPECIAL_CASES:
        variations.append(SPECIAL_CASES[school_name])

    # Remove common suffixes for partial matching
    name_without_hs = school_name.replace(' HS', '').replace(' High School', '')
    if name_without_hs != school_name:
        variations.append(name_without_hs)

    # For abbreviated names, try just the last part (school name)
    parts = school_name.split()
    if len(parts) >= 2 and parts[0] in CITY_ABBREVIATIONS:
        # "SA Brennan" -> also try "Brennan"
        variations.append(' '.join(parts[1:]))

    return variations

def add_abbreviation(abbrev, full_name, category='city'):
    """
    Add a new abbreviation mapping

    Args:
        abbrev: The abbreviation (e.g., 'SA')
        full_name: The full name (e.g., 'San Antonio')
        category: 'city' or 'school'
    """
    if category == 'city':
        CITY_ABBREVIATIONS[abbrev] = full_name
    elif category == 'school':
        SCHOOL_ABBREVIATIONS[abbrev] = full_name

# Additional common patterns
COMMON_PATTERNS = {
    # Pattern: what to look for -> what it might be in UIL
    'Seven Lakes': ['Katy Seven Lakes', 'Seven Lakes'],
    'Jordan': ['Katy Jordan', 'Jordan'],
    'Brennan': ['San Antonio Brennan', 'SA Brennan', 'Brennan'],
    'Harlan': ['San Antonio Harlan', 'SA Harlan', 'Harlan'],
    'Wagner': ['San Antonio Wagner', 'SA Wagner', 'Wagner'],
    'Jay': ['San Antonio Jay', 'SA Jay', 'Northside Jay', 'Jay'],
    'Marshall': ['Fort Bend Marshall', 'FB Marshall', 'Marshall'],
    'Travis': ['Fort Bend Travis', 'FB Travis', 'Travis'],
    'Martin': ['Arlington Martin', 'Arl Martin', 'Martin'],
    'Lake Ridge': ['Mansfield Lake Ridge', 'Mans Lake Ridge', 'Lake Ridge'],
    'Summit': ['Mansfield Summit', 'Mans Summit', 'Summit'],
    'Timberview': ['Mansfield Timberview', 'Mans Timberview', 'Timberview'],
    'Legacy': ['Mansfield Legacy', 'Mans Legacy', 'Legacy'],
    'Veterans Memorial': ['Corpus Christi Veterans Memorial', 'CC Veterans Memorial', 'Veterans Memorial'],
    'Alamo Heights': ['San Antonio Alamo Heights', 'SA Alamo Heights', 'Alamo Heights'],
    'Highland Park': ['Dallas Highland Park', 'Highland Park'],
    'West Brook': ['Beaumont West Brook', 'Bmt West Brook', 'West Brook'],
    'Carter': ['Dallas Carter', 'Carter'],
    'Kimball': ['Dallas Kimball', 'Kimball'],
    'LBJ': ['Austin Johnson', 'Austin LBJ', 'LBJ', 'Johnson'],
    'Davenport': ['Comal Davenport', 'Davenport'],
    'Wimberley': ['Wimberley', 'Wimberly'],  # Common misspelling
    'Jim Ned': ['Tuscola Jim Ned', 'Jim Ned'],
    'City View': ['Wichita Falls City View', 'City View'],
    'Liberty-Eylau': ['Texarkana Liberty-Eylau', 'Liberty-Eylau'],
    'Cole': ['San Antonio Cole', 'SA Cole', 'Cole'],
    'London': ['Corpus Christi London', 'CC London', 'London'],
    'McMullen County': ['Tilden McMullen County', 'McMullen County', 'Tilden'],
    'Permian': ['Odessa Permian', 'Permian'],
}

def find_uil_match(tabc_name, uil_schools, classification_code):
    """
    Find the best UIL match for a TABC school name

    Args:
        tabc_name: School name from TABC rankings
        uil_schools: List of UIL school dictionaries
        classification_code: Classification (e.g., 'AAAAAA')

    Returns:
        Matching UIL school dict or None
    """
    # Get all variations to search for
    variations = get_search_variations(tabc_name)

    # Try exact matches first
    for variation in variations:
        for school in uil_schools:
            if school['classification_code'] == classification_code:
                if school['school_name'].lower() == variation.lower():
                    return school

    # Try partial matches (variation appears in UIL name)
    for variation in variations:
        if len(variation) > 4:  # Only for meaningful names
            for school in uil_schools:
                if school['classification_code'] == classification_code:
                    if variation.lower() in school['school_name'].lower():
                        return school

    # Try reverse (UIL name appears in TABC name)
    for school in uil_schools:
        if school['classification_code'] == classification_code:
            school_name_parts = school['school_name'].split()
            for part in school_name_parts:
                if len(part) > 4 and part.lower() in tabc_name.lower():
                    return school

    return None


if __name__ == "__main__":
    # Test the abbreviation expansion
    test_names = [
        'SA Brennan',
        'Mans Lake Ridge',
        'FB Marshall',
        'Arl Martin',
        'North Crowley',
        'Katy Seven Lakes',
        'H Bellaire',
        'FW Chisholm Trail',
        'CC Veterans Memorial',
    ]

    print("School Name Abbreviation Expansion Test")
    print("=" * 60)
    for name in test_names:
        expanded = expand_abbreviations(name)
        variations = get_search_variations(name)
        print(f"\nOriginal: {name}")
        print(f"Expanded: {expanded}")
        print(f"Variations: {variations}")
