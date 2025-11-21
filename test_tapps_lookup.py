#!/usr/bin/env python3
from tapps_district_mappings import get_tapps_district

# Test the two problem schools
test_schools = [
    ("Dallas St. Mark's School of Texas", 'TAPPS_6A'),
    ("Austin St. Michael's", 'TAPPS_6A'),
]

for school_name, classification in test_schools:
    district = get_tapps_district(school_name, classification)
    print(f'{school_name}: {district}')
