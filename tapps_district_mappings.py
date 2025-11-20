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
    ('Dallas Parish Episcopal', 'TAPPS_6A'): '1',  # TAPPS District 1
    ('Addison Greenhill School', 'TAPPS_6A'): 'SPC North',  # SPC North District
    ('Addison Greenhill', 'TAPPS_6A'): 'SPC North',
    ('Dallas St. Mark\'s School of Texas', 'TAPPS_6A'): 'SPC North',  # SPC North District
    ("Dallas St. Mark's School of Texas", 'TAPPS_6A'): 'SPC North',  # With curly apostrophe
    ('Dallas St. Mark\'s', 'TAPPS_6A'): 'SPC North',
    ("Dallas St. Mark's", 'TAPPS_6A'): 'SPC North',
    ('St. Mark\'s School of Texas', 'TAPPS_6A'): 'SPC North',
    ("St. Mark's School of Texas", 'TAPPS_6A'): 'SPC North',
    ('Dallas St. Mark’s School of Texas', 'TAPPS_6A'): 'SPC North',  # EXACT match with curly apostrophe
    ('Houston Christian', 'TAPPS_6A'): 'SPC South',  # SPC South District
    ('San Antonio TMI Episcopal', 'TAPPS_6A'): '3',  # TAPPS District 3
    ('TMI Episcopal', 'TAPPS_6A'): '3',
    ('Austin St. Michael\'s', 'TAPPS_6A'): '3',  # TAPPS District 3
    ("Austin St. Michael's", 'TAPPS_6A'): '3',  # With curly apostrophe
    ('St. Michael\'s', 'TAPPS_6A'): '3',
    ("St. Michael's", 'TAPPS_6A'): '3',
    ('Austin St. Michael’s', 'TAPPS_6A'): '3',  # EXACT match with curly apostrophe
    ('San Antonio Antonian Prep', 'TAPPS_6A'): '3',  # TAPPS District 3
    ('Antonian Prep', 'TAPPS_6A'): '3',
    ('Plano John Paul II', 'TAPPS_6A'): '2',  # TAPPS District 2
    ('John Paul II', 'TAPPS_6A'): '2',
    ('Dallas Bishop Lynch', 'TAPPS_6A'): '2',  # TAPPS District 2
    ('Bishop Lynch', 'TAPPS_6A'): '2',
    ('Houston The Kinkaid School', 'TAPPS_6A'): 'SPC South',  # SPC South District
    ('The Kinkaid School', 'TAPPS_6A'): 'SPC South',
    ('Kinkaid School', 'TAPPS_6A'): 'SPC South',
    ('Kinkaid', 'TAPPS_6A'): 'SPC South',

    # Additional SPC North Schools
    ('Episcopal Dallas', 'TAPPS_6A'): 'SPC North',
    ('Dallas Episcopal', 'TAPPS_6A'): 'SPC North',
    ('Episcopal School of Dallas', 'TAPPS_6A'): 'SPC North',

    ("St. Andrew's Episcopal", 'TAPPS_6A'): 'SPC North',
    ("St. Andrew's", 'TAPPS_6A'): 'SPC North',
    ('St. Andrew\'s Episcopal', 'TAPPS_6A'): 'SPC North',
    ('St. Andrew\'s', 'TAPPS_6A'): 'SPC North',

    ('Cistercian Preparatory', 'TAPPS_6A'): 'SPC North',
    ('Cistercian', 'TAPPS_6A'): 'SPC North',

    ('Fort Worth Country Day', 'TAPPS_6A'): 'SPC North',
    ('FWCD', 'TAPPS_6A'): 'SPC North',
    ('FW Country Day', 'TAPPS_6A'): 'SPC North',

    ("St. Stephen's Episcopal", 'TAPPS_6A'): 'SPC North',
    ("St. Stephen's", 'TAPPS_6A'): 'SPC North',
    ('St. Stephen\'s Episcopal', 'TAPPS_6A'): 'SPC North',
    ('St. Stephen\'s', 'TAPPS_6A'): 'SPC North',
    ('Austin St. Stephen\'s', 'TAPPS_6A'): 'SPC North',

    ('Trinity Valley School', 'TAPPS_6A'): 'SPC North',
    ('Trinity Valley', 'TAPPS_6A'): 'SPC North',

    ('Oakridge School', 'TAPPS_6A'): 'SPC North',
    ('Oakridge', 'TAPPS_6A'): 'SPC North',

    # Additional SPC South Schools
    ("St. John's School", 'TAPPS_6A'): 'SPC South',
    ("St. John's", 'TAPPS_6A'): 'SPC South',
    ('St. John\'s School', 'TAPPS_6A'): 'SPC South',
    ('St. John\'s', 'TAPPS_6A'): 'SPC South',
    ('Houston St. John\'s', 'TAPPS_6A'): 'SPC South',

    ('Episcopal High School', 'TAPPS_6A'): 'SPC South',
    ('Houston Episcopal', 'TAPPS_6A'): 'SPC South',

    ('Awty International School', 'TAPPS_6A'): 'SPC South',
    ('The Awty School', 'TAPPS_6A'): 'SPC South',
    ('Awty', 'TAPPS_6A'): 'SPC South',

    ('John Cooper School', 'TAPPS_6A'): 'SPC South',
    ('The John Cooper School', 'TAPPS_6A'): 'SPC South',
    ('John Cooper', 'TAPPS_6A'): 'SPC South',

    # Additional TAPPS 6A Schools
    # District Independent
    ('El Paso Loretto', 'TAPPS_6A'): 'Independent',
    # District 1
    ('Argyle Liberty Christian', 'TAPPS_6A'): '1',
    ('Fort Worth Nolan Catholic', 'TAPPS_6A'): '1',
    ('Addison Trinity Christian', 'TAPPS_6A'): '1',
    # District 2
    ('Frisco Legacy Christian', 'TAPPS_6A'): '2',
    ('Plano Prestonwood', 'TAPPS_6A'): '2',
    ('Dallas Ursuline', 'TAPPS_6A'): '2',
    # District 3
    ('San Antonio Antonian', 'TAPPS_6A'): '3',
    ('San Antonio Incarnate Word', 'TAPPS_6A'): '3',
    ('Austin St. Dominic Savio', 'TAPPS_6A'): '3',
    # District 4
    ('Tomball Concordia Lutheran', 'TAPPS_6A'): '4',
    ('Houston Incarnate Word', 'TAPPS_6A'): '4',
    ('Houston St. Agnes', 'TAPPS_6A'): '4',
    ('Katy St. John XXIII', 'TAPPS_6A'): '4',
    ('Houston St. Pius X', 'TAPPS_6A'): '4',
    ('Houston the Village', 'TAPPS_6A'): '4',

    # TAPPS 5A Schools
    # District 1
    ('Fort Worth All Saints', 'TAPPS_5A'): '1',
    ('Flower Mound Coram Deo', 'TAPPS_5A'): '1',
    ('Fort Worth Christian', 'TAPPS_5A'): '1',
    ('Arlington Grace Prep', 'TAPPS_5A'): '1',
    ('Grapevine Faith', 'TAPPS_5A'): '1',
    ('Midland Christian', 'TAPPS_5A'): '1',
    ('Fort Worth Southwest Christian', 'TAPPS_5A'): '1',
    ('Lubbock Trinity Christian', 'TAPPS_5A'): '1',
    # District 2
    ('Dallas Bishop Dunne', 'TAPPS_5A'): '2',
    ('Austin Brentwood', 'TAPPS_5A'): '2',
    ('Garland Brighter Horizons', 'TAPPS_5A'): '2',
    ('Dallas Cristo Rey', 'TAPPS_5A'): '2',
    ('Tyler Grace Community', 'TAPPS_5A'): '2',
    ('Austin Hyde Park', 'TAPPS_5A'): '2',
    ('Austin Regents', 'TAPPS_5A'): '2',
    ('Bullard Brook Hill', 'TAPPS_5A'): '2',
    ('Bullard The Brook Hill School', 'TAPPS_5A'): '2',
    # District 3
    ('San Antonio Providence Catholic', 'TAPPS_5A'): '3',
    ('San Antonio Christian', 'TAPPS_5A'): '3',
    ('San Antonio St. Anthony', 'TAPPS_5A'): '3',
    ("San Antonio St. Anthony Catholic", 'TAPPS_5A'): '3',
    ('Laredo St. Augustine', 'TAPPS_5A'): '3',
    ('Brownsville St. Joseph', 'TAPPS_5A'): '3',
    ("Brownsville St. Joseph Academy", 'TAPPS_5A'): '3',
    ('Victoria St. Joseph', 'TAPPS_5A'): '3',
    ("San Antonio St. Mary's Hall", 'TAPPS_5A'): '3',
    # District 4
    ('League City Bay Area Christian', 'TAPPS_5A'): '4',
    ('Fort Bend Christian Academy', 'TAPPS_5A'): '4',
    ('Sugar Land Fort Bend Christian Academy', 'TAPPS_5A'): '4',
    ('Sugar Land Logos Prep', 'TAPPS_5A'): '4',
    ('Houston Lutheran South', 'TAPPS_5A'): '4',
    ('Houston Second Baptist', 'TAPPS_5A'): '4',
    # District 5
    ('Houston Cypress Christian', 'TAPPS_5A'): '5',
    ('Spring Frassati Catholic', 'TAPPS_5A'): '5',
    ('The Woodlands Legacy Prep', 'TAPPS_5A'): '5',
    ('Beaumont Kelly', 'TAPPS_5A'): '5',
    ('The Woodlands Christian Academy', 'TAPPS_5A'): '5',
    ('Episcopal School of Dallas', 'TAPPS_5A'): '5',

    # TAPPS 4A Schools
    # District 1
    ('Fort Worth Lake Country Christian', 'TAPPS_4A'): '1',
    ('Lubbock Christian', 'TAPPS_4A'): '1',
    ('Midland Classical', 'TAPPS_4A'): '1',
    ('Fort Worth Temple Christian', 'TAPPS_4A'): '1',
    ('Willow Park Trinity Christian', 'TAPPS_4A'): '1',
    ('Midland Trinity', 'TAPPS_4A'): '1',
    ('Midland Christian', 'TAPPS_4A'): '1',
    # District 2
    ('Plano Coram Deo', 'TAPPS_4A'): '2',
    ('Colleyville Covenant', 'TAPPS_4A'): '2',
    ('Colleyville Covenenat Christian', 'TAPPS_4A'): '2',
    ('Arlington Pantego', 'TAPPS_4A'): '2',
    ('Carrollton Prince of Peace', 'TAPPS_4A'): '2',
    ('Dallas the Covenant', 'TAPPS_4A'): '2',
    # District 3
    ('Tyler All Saints', 'TAPPS_4A'): '3',
    ('Tyler Bishop Gorman', 'TAPPS_4A'): '3',
    ('Dallas Christian', 'TAPPS_4A'): '3',
    ('McKinney Christian', 'TAPPS_4A'): '3',
    ('Mckinney Christian', 'TAPPS_4A'): '3',
    ('Dallas Shelton', 'TAPPS_4A'): '3',
    # District 4
    ('Bryan Brazos Christian', 'TAPPS_4A'): '4',
    ('Pflugerville Concordia High', 'TAPPS_4A'): '4',
    ('Austin Hill Country Christian', 'TAPPS_4A'): '4',
    ('Round Rock Christian', 'TAPPS_4A'): '4',
    ('Texas School of the Deaf', 'TAPPS_4A'): '4',
    ('Waco Vanguard', 'TAPPS_4A'): '4',
    ('Austin Veritas Academy', 'TAPPS_4A'): '4',
    # District 5
    ('Boerne Geneva', 'TAPPS_4A'): '5',
    ('San Antonio Holy Cross', 'TAPPS_4A'): '5',
    ('Corpus Christi Incarnate Word', 'TAPPS_4A'): '5',
    ('Schertz John Paul II', 'TAPPS_4A'): '5',
    ('New Braunfels Christian', 'TAPPS_4A'): '5',
    ('Corpus Christi St. John Paul II', 'TAPPS_4A'): '5',
    ('San Antonio Castle Hills', 'TAPPS_4A'): '5',
    # District 6
    ('Pasadena First Baptist', 'TAPPS_4A'): '6',
    ('Houston Northland Christian', 'TAPPS_4A'): '6',
    ('Tomball Rosehill Christian', 'TAPPS_4A'): '6',
    ('Houston St. Francis Episcopal', 'TAPPS_4A'): '6',
    ('Houston St. Francis', 'TAPPS_4A'): '6',
    ('Houston St. Thomas Episcopal', 'TAPPS_4A'): '6',
    ('Houston St Thomas Episcopal', 'TAPPS_4A'): '6',
    ('Houston Westbury', 'TAPPS_4A'): '6',

    # TAPPS 3A Schools
    # District 1
    ('Abilene Christian', 'TAPPS_3A'): '1',
    ('Fort Worth Christian Life Prep', 'TAPPS_3A'): '1',
    ('Fort Worth Covenant Classical', 'TAPPS_3A'): '1',
    ('Fort Worth Covenant', 'TAPPS_3A'): '1',
    ('Denton Calvary', 'TAPPS_3A'): '1',
    ('Kennedale Fellowship', 'TAPPS_3A'): '1',
    ('Weatherford Christian', 'TAPPS_3A'): '1',
    ('Keene Chisholm Trail', 'TAPPS_3A'): '1',
    # District 2
    ('Dallas Yavneh', 'TAPPS_3A'): '2',
    ('Dallas International', 'TAPPS_3A'): '2',
    ('Dallas Lakehill Prep', 'TAPPS_3A'): '2',
    ('North Dallas Adventist', 'TAPPS_3A'): '2',
    ('Irving the Highlands', 'TAPPS_3A'): '2',
    # District 3
    ('McKinney Cornerstone Christian', 'TAPPS_3A'): '3',
    ('Dallas Lutheran', 'TAPPS_3A'): '3',
    ('Rockwall Heritage', 'TAPPS_3A'): '3',
    ('Lucas Christian', 'TAPPS_3A'): '3',
    ('Wylie Prep', 'TAPPS_3A'): '3',
    # District 4
    ('Central Texas Christian', 'TAPPS_3A'): '4',
    ('Marble Falls Faith', 'TAPPS_3A'): '4',
    ('Faith Academy of Marble Falls', 'TAPPS_3A'): '4',
    ('San Antonio Keystone', 'TAPPS_3A'): '4',
    ('Waco Live Oak Classical', 'TAPPS_3A'): '4',
    ('Waco Live Oak', 'TAPPS_3A'): '4',
    ('San Antonio Lutheran', 'TAPPS_3A'): '4',
    ('San Marcos Academy', 'TAPPS_3A'): '4',
    ('Austin San Juan Diego Catholic', 'TAPPS_3A'): '4',
    ('Austin San Juan Diego', 'TAPPS_3A'): '4',
    # District 5
    ('Huntsville Alpha Omega', 'TAPPS_3A'): '5',
    ('Conroe Covenant Christian', 'TAPPS_3A'): '5',
    ('Spring Providence Classical', 'TAPPS_3A'): '5',
    ('Houston Westbury Christian', 'TAPPS_3A'): '5',
    ('Houston Xavier Academy', 'TAPPS_3A'): '5',

    # TAPPS 2A Schools
    # District 1
    ('Lubbock All Saints', 'TAPPS_2A'): '1',
    ('All Saints Episcopal School-Lubbock', 'TAPPS_2A'): '1',
    ('Amarillo Ascension', 'TAPPS_2A'): '1',
    ('Lubbock Christ the King', 'TAPPS_2A'): '1',
    ('Amarillo Holy Cross', 'TAPPS_2A'): '1',
    ('Holy Cross Catholic Academy-Amarillo', 'TAPPS_2A'): '1',
    ('Midland Holy Cross', 'TAPPS_2A'): '1',
    ('Lubbock Kingdom Prep', 'TAPPS_2A'): '1',
    ('Amarillo San Jacinto', 'TAPPS_2A'): '1',
    ('Lubbock Southcrest Christian', 'TAPPS_2A'): '1',
    # District 2
    ('Fort Worth Bethesda Christian', 'TAPPS_2A'): '2',
    ('Keller Harvest Christian', 'TAPPS_2A'): '2',
    ('Fort Worth Mercy Culture Prep', 'TAPPS_2A'): '2',
    ('Crowley Nazareth Christian', 'TAPPS_2A'): '2',
    ('Muenster Sacred Heart', 'TAPPS_2A'): '2',
    ('Weatherford Victory Baptist', 'TAPPS_2A'): '2',
    ('Victory Christian Academy-Decatur', 'TAPPS_2A'): '2',
    ('Wichita Christian', 'TAPPS_2A'): '2',
    # District 3
    ('Dallas Alcuin', 'TAPPS_2A'): '3',
    ('Dallas Cambridge', 'TAPPS_2A'): '3',
    ('Dallas First Baptist', 'TAPPS_2A'): '3',
    ('First Baptist Academy-Dallas', 'TAPPS_2A'): '3',
    ('Garland Christian', 'TAPPS_2A'): '3',
    ('Red Oak Ovilla', 'TAPPS_2A'): '3',
    ('Ovilla Christian School', 'TAPPS_2A'): '3',
    ('Prosper Prestonwood Christian', 'TAPPS_2A'): '3',
    # District 4
    ('Longview Christian', 'TAPPS_2A'): '4',
    ('Greenville Christian', 'TAPPS_2A'): '4',
    ('Terrell Poetry Community Christian', 'TAPPS_2A'): '4',
    # District 5
    ('Austin Waldorf', 'TAPPS_2A'): '5',
    ('Waco Reicher Catholic', 'TAPPS_2A'): '5',
    ('Temple Holy Trinity Catholic', 'TAPPS_2A'): '5',
    ('Cedar Park Summit Christian', 'TAPPS_2A'): '5',
    ('Waco Fortis Academy', 'TAPPS_2A'): '5',
    ('Valor Preparatory Academy-Waco', 'TAPPS_2A'): '5',
    # District 6
    ('Bulverde Bracken Christian', 'TAPPS_2A'): '6',
    ('Bracken Christian School-Bulverde', 'TAPPS_2A'): '6',
    ('Victoria Faith Academy', 'TAPPS_2A'): '6',
    ('Hallettsville Sacred Heart', 'TAPPS_2A'): '6',
    ('Shiner St. Paul', 'TAPPS_2A'): '6',
    # District 7
    ('Bryan Allen Academy', 'TAPPS_2A'): '7',
    ('Conroe Calvary Baptist', 'TAPPS_2A'): '7',
    ('Calvary Baptist School-Conroe', 'TAPPS_2A'): '7',
    ('Katy Faith West', 'TAPPS_2A'): '7',
    ('Cypress Houston Adventist', 'TAPPS_2A'): '7',
    ('Bryan St. Joseph', 'TAPPS_2A'): '7',
    # District 8
    ('Brazosport Christian', 'TAPPS_2A'): '8',
    ('Chinquapin School', 'TAPPS_2A'): '8',
    ('Beaumont Legacy Christian', 'TAPPS_2A'): '8',
    ('Legacy Christian Academy-Beaumont', 'TAPPS_2A'): '8',
    ("Galveston O'Connell", 'TAPPS_2A'): '8',
    ('O\'Connell College Preparatory School-Galveston', 'TAPPS_2A'): '8',
    ('O' + chr(8217) + 'Connell College Preparatory School-Galveston', 'TAPPS_2A'): '8',  # Curly apostrophe
    ('Houston the Briarwood', 'TAPPS_2A'): '8',
    ('Houston Lutheran North', 'TAPPS_2A'): '8',

    # TAPPS 1A Schools
    # District 1
    ('El Paso Jesus Chapel', 'TAPPS_1A'): '1',
    ('El Paso Radford', 'TAPPS_1A'): '1',
    ('Amarillo Accelerate Christian', 'TAPPS_1A'): '1',
    # District 2
    ('Azle Christian', 'TAPPS_1A'): '2',
    ('Azle Christian School', 'TAPPS_1A'): '2',
    ('Wichita Falls Christ Academy', 'TAPPS_1A'): '2',
    ('Granbury Cornerstone Christian', 'TAPPS_1A'): '2',
    ('Cornerstone Christian School-San Angelo', 'TAPPS_1A'): '2',
    ('Sherman Texhoma Christian', 'TAPPS_1A'): '2',
    ('Texhoma Christian School-Sherman', 'TAPPS_1A'): '2',
    # District 3
    ('Waco Eagle Christian', 'TAPPS_1A'): '3',
    ('Dallas Fairhill School', 'TAPPS_1A'): '3',
    ('DeSoto Kingdom Prep', 'TAPPS_1A'): '3',
    ('Rockwall Providence Academy', 'TAPPS_1A'): '3',
    ('Waxahachie Prep', 'TAPPS_1A'): '3',
    # District 4
    ('Athens Christian', 'TAPPS_1A'): '4',
    ('Nacogdoches Regents', 'TAPPS_1A'): '4',
    ('Regents Academy-Nacogdoches', 'TAPPS_1A'): '4',
    ('Nacogdoches St. Boniface Catholic', 'TAPPS_1A'): '4',
    ("Longview St. Mary's", 'TAPPS_1A'): '4',
    ('Longview Trinity', 'TAPPS_1A'): '4',
    # District 5
    ('Edinburg Harvest Christian', 'TAPPS_1A'): '5',
    ('Harvest Christian Academy-Edinburgh', 'TAPPS_1A'): '5',
    ('Mission Juan Diego Academy', 'TAPPS_1A'): '5',
    ('Alamo Macedonia Christian', 'TAPPS_1A'): '5',
    ('Macedonian Christian Academy-Alamo', 'TAPPS_1A'): '5',
    ('Kingsville Presbyterian Pan American', 'TAPPS_1A'): '5',
    ('McAllen South Texas Christian', 'TAPPS_1A'): '5',
    # District 6
    ('San Antonio Cornerstone', 'TAPPS_1A'): '6',
    ('Universal City First Baptist', 'TAPPS_1A'): '6',
    ('San Marcos Hill Country Christian', 'TAPPS_1A'): '6',
    ('San Antonio Legacy', 'TAPPS_1A'): '6',
    ('Bulverde Living Rock Academy', 'TAPPS_1A'): '6',
    ('Kerrville Our Lady of the Hills', 'TAPPS_1A'): '6',
    ('Selma River City Believers', 'TAPPS_1A'): '6',
    ('Heritage School-Fredericksburg', 'TAPPS_1A'): '6',
    # District 7
    ('Cypress Covenant', 'TAPPS_1A'): '7',
    ('Kingwood Covenant', 'TAPPS_1A'): '7',
    ('The Covenant Preparatory School-Kingwood', 'TAPPS_1A'): '7',
    ('Houston Second Baptist UM', 'TAPPS_1A'): '7',
    ('Spring Founders Christian', 'TAPPS_1A'): '7',
    ('Founders Christian School-Spring', 'TAPPS_1A'): '7',
    ('Conroe Lifestyle Christian', 'TAPPS_1A'): '7',
    ('Bellville Faith Christian', 'TAPPS_1A'): '7',
    # District 8
    ('Baytown Christian', 'TAPPS_1A'): '8',
    ('Houston Faith Christian', 'TAPPS_1A'): '8',
    ('Missouri City Divine Savior Academy', 'TAPPS_1A'): '8',
    ('Divine Savior Academy-Missouri City', 'TAPPS_1A'): '8',
    ('Houston Grace Christian', 'TAPPS_1A'): '8',
    ('Alvin Living Stones Christian', 'TAPPS_1A'): '8',
    ('Houston Beren Academy', 'TAPPS_1A'): '8',
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
