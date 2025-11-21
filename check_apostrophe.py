#!/usr/bin/env python3
from tapps_district_mappings import TAPPS_DISTRICTS

# Check what apostrophe we have in the dictionary
for (school_name, classification), district in TAPPS_DISTRICTS.items():
    if "Mark" in school_name and "Dallas" in school_name:
        print(f"Found: {school_name!r}")
        print(f"  Classification: {classification}")
        print(f"  District: {district}")
        apostrophes = [c for c in school_name if ord(c) > 127]
        if apostrophes:
            print(f"  Special chars: {[ord(c) for c in apostrophes]}")
        print()
