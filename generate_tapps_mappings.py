#!/usr/bin/env python3
"""
Generate TAPPS district mappings from the district list
"""

# TAPPS 6A Districts
tapps_6a = {
    '1': [
        'Argyle Liberty Christian',
        'Fort Worth Nolan Catholic',
        'Dallas Parish Episcopal',
        'Addison Trinity Christian',
    ],
    '2': [
        'Dallas Bishop Lynch',
        'Plano John Paul II',
        'Frisco Legacy Christian',
        'Plano Prestonwood',
        'Dallas Ursuline',
    ],
    '3': [
        'San Antonio Antonian',
        'San Antonio Incarnate Word',
        'Austin St. Dominic Savio',
        "Austin St. Michael's",
        'San Antonio TMI Episcopal',
    ],
    '4': [
        'Tomball Concordia Lutheran',
        'Houston Incarnate Word',
        'Houston St. Agnes',
        'Katy St. John XXIII',
        'Houston St. Pius X',
        'Houston the Village',
    ],
    'Independent': [
        'El Paso Loretto',
    ],
}

# TAPPS 5A Districts
tapps_5a = {
    '1': [
        'Fort Worth All Saints',
        'Flower Mound Coram Deo',
        'Fort Worth Christian',
        'Arlington Grace Prep',
        'Grapevine Faith',
        'Midland Christian',
        'Fort Worth Southwest Christian',
        'Lubbock Trinity Christian',
    ],
    '2': [
        'Dallas Bishop Dunne',
        'Austin Brentwood',
        'Garland Brighter Horizons',
        'Dallas Cristo Rey',
        'Tyler Grace Community',
        'Austin Hyde Park',
        'Austin Regents',
        'Bullard Brook Hill',
    ],
    '3': [
        'San Antonio Providence Catholic',
        'San Antonio Christian',
        'San Antonio St. Anthony',
        'Laredo St. Augustine',
        'Brownsville St. Joseph',
        'Victoria St. Joseph',
        "San Antonio St. Mary's Hall",
    ],
    '4': [
        'League City Bay Area Christian',
        'Fort Bend Christian Academy',
        'Sugar Land Logos Prep',
        'Houston Lutheran South',
        'Houston Second Baptist',
    ],
    '5': [
        'Houston Cypress Christian',
        'Spring Frassati Catholic',
        'The Woodlands Legacy Prep',
        'Beaumont Kelly',
        'The Woodlands Christian Academy',
    ],
}

# TAPPS 4A Districts
tapps_4a = {
    '1': [
        'Fort Worth Lake Country Christian',
        'Lubbock Christian',
        'Midland Classical',
        'Fort Worth Temple Christian',
        'Willow Park Trinity Christian',
        'Midland Trinity',
    ],
    '2': [
        'Plano Coram Deo',
        'Colleyville Covenant',
        'Arlington Pantego',
        'Carrollton Prince of Peace',
        'Dallas the Covenant',
    ],
    '3': [
        'Tyler All Saints',
        'Tyler Bishop Gorman',
        'Dallas Christian',
        'McKinney Christian',
        'Dallas Shelton',
    ],
    '4': [
        'Bryan Brazos Christian',
        'Pflugerville Concordia High',
        'Austin Hill Country Christian',
        'Round Rock Christian',
        'Texas School of the Deaf',
        'Waco Vanguard',
        'Austin Veritas Academy',
    ],
    '5': [
        'Boerne Geneva',
        'San Antonio Holy Cross',
        'Corpus Christi Incarnate Word',
        'Schertz John Paul II',
        'New Braunfels Christian',
        'Corpus Christi St. John Paul II',
        'San Antonio Castle Hills',
    ],
    '6': [
        'Pasadena First Baptist',
        'Houston Northland Christian',
        'Tomball Rosehill Christian',
        'Houston St. Francis Episcopal',
        'Houston St. Thomas Episcopal',
    ],
}

# TAPPS 3A Districts
tapps_3a = {
    '1': [
        'Abilene Christian',
        'Fort Worth Christian Life Prep',
        'Fort Worth Covenant Classical',
        'Denton Calvary',
        'Kennedale Fellowship',
        'Weatherford Christian',
    ],
    '2': [
        'Dallas Yavneh',
        'Dallas International',
        'Dallas Lakehill Prep',
        'North Dallas Adventist',
        'Irving the Highlands',
    ],
    '3': [
        'McKinney Cornerstone Christian',
        'Dallas Lutheran',
        'Rockwall Heritage',
        'Lucas Christian',
        'Wylie Prep',
    ],
    '4': [
        'Central Texas Christian',
        'Marble Falls Faith',
        'San Antonio Keystone',
        'Waco Live Oak Classical',
        'San Antonio Lutheran',
        'San Marcos Academy',
        'Austin San Juan Diego Catholic',
    ],
    '5': [
        'Huntsville Alpha Omega',
        'Conroe Covenant Christian',
        'Spring Providence Classical',
        'Houston Westbury Christian',
        'Houston Xavier Academy',
    ],
}

# TAPPS 2A Districts
tapps_2a = {
    '1': [
        'Lubbock All Saints',
        'Amarillo Ascension',
        'Lubbock Christ the King',
        'Amarillo Holy Cross',
        'Midland Holy Cross',
        'Lubbock Kingdom Prep',
        'Amarillo San Jacinto',
        'Lubbock Southcrest Christian',
    ],
    '2': [
        'Fort Worth Bethesda Christian',
        'Keller Harvest Christian',
        'Fort Worth Mercy Culture Prep',
        'Crowley Nazareth Christian',
        'Muenster Sacred Heart',
        'Weatherford Victory Baptist',
        'Wichita Christian',
    ],
    '3': [
        'Dallas Alcuin',
        'Dallas Cambridge',
        'Dallas First Baptist',
        'Garland Christian',
        'Red Oak Ovilla',
        'Prosper Prestonwood Christian',
    ],
    '4': [
        'Longview Christian',
        'Greenville Christian',
        'Terrell Poetry Community Christian',
    ],
    '5': [
        'Austin Waldorf',
        'Waco Reicher Catholic',
        'Temple Holy Trinity Catholic',
        'Cedar Park Summit Christian',
        'Waco Fortis Academy',
    ],
    '6': [
        'Bulverde Bracken Christian',
        'Victoria Faith Academy',
        'Hallettsville Sacred Heart',
        'Shiner St. Paul',
    ],
    '7': [
        'Bryan Allen Academy',
        'Conroe Calvary Baptist',
        'Katy Faith West',
        'Cypress Houston Adventist',
        'Bryan St. Joseph',
    ],
    '8': [
        'Brazosport Christian',
        'Chinquapin School',
        'Beaumont Legacy Christian',
        'Galveston O\'Connell',
        'Houston the Briarwood',
        'Houston Lutheran North',
    ],
}

# TAPPS 1A Districts
tapps_1a = {
    '1': [
        'El Paso Jesus Chapel',
        'El Paso Radford',
        'Amarillo Accelerate Christian',
    ],
    '2': [
        'Azle Christian',
        'Wichita Falls Christ Academy',
        'Granbury Cornerstone Christian',
        'Sherman Texhoma Christian',
    ],
    '3': [
        'Waco Eagle Christian',
        'Dallas Fairhill School',
        'DeSoto Kingdom Prep',
        'Rockwall Providence Academy',
        'Waxahachie Prep',
    ],
    '4': [
        'Athens Christian',
        'Nacogdoches Regents',
        'Nacogdoches St. Boniface Catholic',
        'Longview St. Mary\'s',
        'Longview Trinity',
    ],
    '5': [
        'Edinburg Harvest Christian',
        'Mission Juan Diego Academy',
        'Alamo Macedonia Christian',
        'Kingsville Presbyterian Pan American',
        'McAllen South Texas Christian',
    ],
    '6': [
        'San Antonio Cornerstone',
        'Universal City First Baptist',
        'San Marcos Hill Country Christian',
        'San Antonio Legacy',
        'Bulverde Living Rock Academy',
        'Kerrville Our Lady of the Hills',
        'Selma River City Believers',
    ],
    '7': [
        'Cypress Covenant',
        'Kingwood Covenant',
        'Houston Second Baptist UM',
        'Spring Founders Christian',
        'Conroe Lifestyle Christian',
        'Bellville Faith Christian',
    ],
    '8': [
        'Baytown Christian',
        'Houston Faith Christian',
        'Missouri City Divine Savior Academy',
        'Houston Grace Christian',
        'Alvin Living Stones Christian',
        'Houston Beren Academy',
    ],
}

def generate_mappings():
    """Generate Python code for TAPPS district mappings"""

    all_mappings = []

    # Process each classification
    classifications = [
        ('TAPPS_6A', tapps_6a),
        ('TAPPS_5A', tapps_5a),
        ('TAPPS_4A', tapps_4a),
        ('TAPPS_3A', tapps_3a),
        ('TAPPS_2A', tapps_2a),
        ('TAPPS_1A', tapps_1a),
    ]

    for class_code, districts in classifications:
        all_mappings.append(f"\n    # {class_code} Schools")

        for district, schools in sorted(districts.items()):
            all_mappings.append(f"    # District {district}")
            for school in schools:
                # Add the full name
                all_mappings.append(f"    ('{school}', '{class_code}'): '{district}',")

    return '\n'.join(all_mappings)

if __name__ == "__main__":
    print(generate_mappings())
