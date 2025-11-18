"""
TAPPS District Mappings for Boys Basketball Schools
Source: TAPPS Alignment 2024-2026 (pages 35-41)
https://drive.google.com/file/d/1L9zFxC2Sd77Th6looL72ZpbihK1cM1dc/view

Manual mappings for TAPPS schools to ensure correct district assignments
"""

TAPPS_DISTRICTS = {
    # TAPPS 6A
    # District structure: (school_name, classification) -> district_number

    # Example format:
    # ('Dallas Parish Episcopal', 'TAPPS_6A'): '1',
    # ('Houston Christian', 'TAPPS_6A'): '2',

    # TAPPS 6A Schools (fill in from PDF pages 35-36)
    ('Dallas Parish Episcopal', 'TAPPS_6A'): None,  # TODO: Add district from PDF
    ('Addison Greenhill School', 'TAPPS_6A'): None,
    ('Dallas St. Mark\'s School of Texas', 'TAPPS_6A'): None,
    ('Houston Christian', 'TAPPS_6A'): None,
    ('San Antonio TMI Episcopal', 'TAPPS_6A'): None,
    ('Austin St. Michael\'s', 'TAPPS_6A'): None,
    ('San Antonio Antonian Prep', 'TAPPS_6A'): None,
    ('Plano John Paul II', 'TAPPS_6A'): None,
    ('Dallas Bishop Lynch', 'TAPPS_6A'): None,
    ('Houston The Kinkaid School', 'TAPPS_6A'): None,

    # TAPPS 5A Schools (fill in from PDF pages 36-37)
    ('Houston Second Baptist', 'TAPPS_5A'): None,
    ('Arlington Grace Prep', 'TAPPS_5A'): None,
    ('Lubbock Trinity Christian', 'TAPPS_5A'): None,
    ('Episcopal School of Dallas', 'TAPPS_5A'): None,
    ('The Woodlands Christian Academy', 'TAPPS_5A'): None,
    ('Bullard The Brook Hill School', 'TAPPS_5A'): None,
    ('Midland Christian', 'TAPPS_5A'): None,
    ('Sugar Land Fort Bend Christian Academy', 'TAPPS_5A'): None,
    ('Brownsville St. Joseph Academy', 'TAPPS_5A'): None,
    ('San Antonio St. Anthony Catholic', 'TAPPS_5A'): None,

    # TAPPS 4A Schools (fill in from PDF pages 37-38)
    ('Mckinney Christian', 'TAPPS_4A'): None,
    ('Houston St. Francis', 'TAPPS_4A'): None,
    ('Lubbock Christian', 'TAPPS_4A'): None,
    ('Houston St Thomas Episcopal', 'TAPPS_4A'): None,
    ('Tyler Bishop Gorman', 'TAPPS_4A'): None,
    ('Houston Westbury', 'TAPPS_4A'): None,
    ('Midland Christian', 'TAPPS_4A'): None,
    ('San Antonio Holy Cross', 'TAPPS_4A'): None,
    ('Colleyville Covenenat Christian', 'TAPPS_4A'): None,
    ('Boerne Geneva', 'TAPPS_4A'): None,

    # TAPPS 3A Schools (fill in from PDF pages 38-39)
    ('Dallas Yavneh', 'TAPPS_3A'): None,
    ('Waco Live Oak', 'TAPPS_3A'): None,
    ('Faith Academy of Marble Falls', 'TAPPS_3A'): None,
    ('Huntsville Alpha Omega', 'TAPPS_3A'): None,
    ('Abilene Christian', 'TAPPS_3A'): None,
    ('Keene Chisholm Trail', 'TAPPS_3A'): None,
    ('Fort Worth Covenant', 'TAPPS_3A'): None,
    ('Denton Calvary', 'TAPPS_3A'): None,
    ('Austin San Juan Diego', 'TAPPS_3A'): None,
    ('Rockwall Heritage', 'TAPPS_3A'): None,

    # TAPPS 2A Schools (fill in from PDF pages 39-40)
    ('First Baptist Academy-Dallas', 'TAPPS_2A'): None,
    ('Holy Cross Catholic Academy-Amarillo', 'TAPPS_2A'): None,
    ('All Saints Episcopal School-Lubbock', 'TAPPS_2A'): None,
    ('O\'Connell College Preparatory School-Galveston', 'TAPPS_2A'): None,
    ('Bracken Christian School-Bulverde', 'TAPPS_2A'): None,
    ('Valor Preparatory Academy-Waco', 'TAPPS_2A'): None,
    ('Ovilla Christian School', 'TAPPS_2A'): None,
    ('Calvary Baptist School-Conroe', 'TAPPS_2A'): None,
    ('Legacy Christian Academy-Beaumont', 'TAPPS_2A'): None,
    ('Victory Christian Academy-Decatur', 'TAPPS_2A'): None,

    # TAPPS 1A Schools (fill in from PDF pages 40-41)
    ('Divine Savior Academy-Missouri City', 'TAPPS_1A'): None,
    ('Texhoma Christian School-Sherman', 'TAPPS_1A'): None,
    ('Heritage School-Fredericksburg', 'TAPPS_1A'): None,
    ('The Covenant Preparatory School-Kingwood', 'TAPPS_1A'): None,
    ('Harvest Christian Academy-Edinburgh', 'TAPPS_1A'): None,
    ('Macedonian Christian Academy-Alamo', 'TAPPS_1A'): None,
    ('Regents Academy-Nacogdoches', 'TAPPS_1A'): None,
    ('Founders Christian School-Spring', 'TAPPS_1A'): None,
    ('Cornerstone Christian School-San Angelo', 'TAPPS_1A'): None,
    ('Azle Christian School', 'TAPPS_1A'): None,
}


def get_tapps_district(school_name, classification):
    """
    Get district number for a TAPPS school

    Args:
        school_name: School name from rankings
        classification: Classification (e.g., 'TAPPS_6A')

    Returns:
        District number (string) or None if not found
    """
    # Try exact match
    district = TAPPS_DISTRICTS.get((school_name, classification))

    if district:
        return district

    # Try fuzzy matching (remove common variations)
    normalized_name = school_name.lower().strip()

    for (tapps_name, tapps_class), dist in TAPPS_DISTRICTS.items():
        if tapps_class == classification:
            if normalized_name in tapps_name.lower() or tapps_name.lower() in normalized_name:
                return dist

    return None


def add_tapps_district(school_name, classification, district):
    """
    Add a TAPPS district mapping

    Args:
        school_name: School name
        classification: Classification (e.g., 'TAPPS_6A')
        district: District number (string)
    """
    TAPPS_DISTRICTS[(school_name, classification)] = district


if __name__ == "__main__":
    # Show schools missing district data
    print("TAPPS Schools Missing District Data:")
    print("=" * 80)

    missing = []
    for (school, classification), district in TAPPS_DISTRICTS.items():
        if district is None:
            missing.append((classification, school))

    # Group by classification
    from collections import defaultdict
    by_class = defaultdict(list)
    for classification, school in missing:
        by_class[classification].append(school)

    for classification in ['TAPPS_6A', 'TAPPS_5A', 'TAPPS_4A', 'TAPPS_3A', 'TAPPS_2A', 'TAPPS_1A']:
        schools = by_class.get(classification, [])
        if schools:
            print(f"\n{classification} ({len(schools)} schools):")
            for school in schools:
                print(f"  - {school}")

    print(f"\nTotal schools missing districts: {len(missing)}")
    print("\nPlease fill in district numbers from PDF pages 35-41")
