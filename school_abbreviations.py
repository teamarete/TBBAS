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
    'Steele': 'Steele',                # Could be "Cibolo Steele"
    'Little Elm': 'Little Elm',
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
    'Jay': ['San Antonio Jay', 'SA Jay', 'Jay'],
    'Marshall': ['Fort Bend Marshall', 'FB Marshall', 'Marshall'],
    'Travis': ['Fort Bend Travis', 'FB Travis', 'Travis'],
    'Martin': ['Arlington Martin', 'Arl Martin', 'Martin'],
    'Lake Ridge': ['Mansfield Lake Ridge', 'Mans Lake Ridge', 'Lake Ridge'],
    'Summit': ['Mansfield Summit', 'Mans Summit', 'Summit'],
    'Timberview': ['Mansfield Timberview', 'Mans Timberview', 'Timberview'],
    'Legacy': ['Mansfield Legacy', 'Mans Legacy', 'Legacy'],
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
