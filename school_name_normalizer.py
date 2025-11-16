"""
School Name Normalizer and Deduplication Utility
Handles Texas high school name variations, abbreviations, and duplicates
"""

import re
from difflib import SequenceMatcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SchoolNameNormalizer:
    """
    Normalizes Texas high school names to handle:
    - City abbreviations (Arlington -> Arl, Fort Worth -> FW)
    - School suffixes (HS, High School, H.S.)
    - Duplicate school names in different cities
    - Common variations and typos
    """

    # Common Texas city abbreviations
    CITY_ABBREVIATIONS = {
        'arl': 'arlington',
        'fw': 'fort worth',
        'sa': 'san antonio',
        'cc': 'corpus christi',
        'ep': 'el paso',
        'sa': 'san angelo',
        'mc': 'mission consolidated',
        'nb': 'new braunfels',
        'sg': 'spring',
        'lp': 'la porte',
        'gp': 'grand prairie',
        'hp': 'highland park',
        'up': 'university park',
    }

    # Reverse mapping for normalization
    CITY_EXPANSIONS = {
        'arlington': ['arl', 'arlington'],
        'fort worth': ['fw', 'fort worth', 'ft worth', 'ft. worth'],
        'san antonio': ['sa', 'san antonio', 'san ant'],
        'corpus christi': ['cc', 'corpus christi', 'corpus'],
        'el paso': ['ep', 'el paso'],
        'san angelo': ['san angelo'],
        'new braunfels': ['nb', 'new braunfels'],
        'grand prairie': ['gp', 'grand prairie'],
        'highland park': ['hp', 'highland park'],
    }

    # Common school name suffixes to normalize
    SCHOOL_SUFFIXES = [
        'high school', 'hs', 'h.s.', 'h s',
        'secondary school', 'academy', 'acad',
        'preparatory', 'prep', 'christian', 'chr',
        'boys', 'girls'
    ]

    # Common school names that appear in multiple cities
    COMMON_DUPLICATE_NAMES = {
        'central', 'eastside', 'westside', 'northside', 'southside',
        'north', 'south', 'east', 'west',
        'memorial', 'veterans', 'legacy', 'heritage',
        'first baptist', 'trinity christian', 'st joseph',
        'riverside', 'lakeside', 'hillside', 'parkside'
    }

    def __init__(self):
        self.known_schools = {}  # Cache of normalized names

    def normalize(self, school_name):
        """
        Normalize a school name to a standard format
        Returns: normalized name (lowercase, no suffixes, expanded city names)
        """
        if not school_name:
            return ""

        original = school_name
        name = school_name.lower().strip()

        # Remove common punctuation
        name = re.sub(r'[.,\-\'"]', ' ', name)

        # Normalize whitespace
        name = ' '.join(name.split())

        # Expand city abbreviations at the beginning
        words = name.split()
        if words and words[0] in self.CITY_ABBREVIATIONS:
            words[0] = self.CITY_ABBREVIATIONS[words[0]]
            name = ' '.join(words)

        # Remove school suffixes from the end
        for suffix in self.SCHOOL_SUFFIXES:
            if name.endswith(' ' + suffix):
                name = name[:-len(suffix)-1].strip()

        logger.debug(f"Normalized: '{original}' -> '{name}'")
        return name

    def extract_city(self, school_name):
        """
        Try to extract city name from school name
        Returns: city name or None
        """
        normalized = self.normalize(school_name)
        words = normalized.split()

        if not words:
            return None

        # Check if first word(s) are a known city
        # Try two-word cities first
        if len(words) >= 2:
            two_word = f"{words[0]} {words[1]}"
            for city, variations in self.CITY_EXPANSIONS.items():
                if two_word in variations:
                    return city

        # Try one-word cities
        if words[0] in self.CITY_ABBREVIATIONS.values():
            return words[0]

        for city, variations in self.CITY_EXPANSIONS.items():
            if words[0] in variations:
                return city

        return None

    def extract_school_base_name(self, school_name):
        """
        Extract the base school name (without city prefix)
        e.g., "Arlington Sam Houston" -> "sam houston"
        """
        normalized = self.normalize(school_name)
        city = self.extract_city(school_name)

        if city:
            # Remove city from beginning
            for variation in self.CITY_EXPANSIONS.get(city, [city]):
                if normalized.startswith(variation + ' '):
                    return normalized[len(variation)+1:].strip()

        return normalized

    def similarity_score(self, name1, name2):
        """
        Calculate similarity score between two school names (0-1)
        Uses sequence matching on normalized names
        """
        norm1 = self.normalize(name1)
        norm2 = self.normalize(name2)

        return SequenceMatcher(None, norm1, norm2).ratio()

    def are_duplicates(self, name1, name2, threshold=0.90):
        """
        Determine if two school names refer to the same school
        Uses fuzzy matching and city detection
        """
        if not name1 or not name2:
            return False

        # Exact match after normalization
        norm1 = self.normalize(name1)
        norm2 = self.normalize(name2)

        if norm1 == norm2:
            return True

        # High similarity score
        similarity = self.similarity_score(name1, name2)
        if similarity >= threshold:
            return True

        # Check if they have the same base name and city
        city1 = self.extract_city(name1)
        city2 = self.extract_city(name2)
        base1 = self.extract_school_base_name(name1)
        base2 = self.extract_school_base_name(name2)

        if city1 and city2 and base1 and base2:
            if city1 == city2 and base1 == base2:
                return True

        return False

    def find_canonical_name(self, school_names):
        """
        Given a list of potential duplicate names, find the best canonical name
        Prefers: full city name > abbreviated > shortest complete name
        """
        if not school_names:
            return None

        if len(school_names) == 1:
            return school_names[0]

        # Score each name
        scored = []
        for name in school_names:
            score = 0
            normalized = self.normalize(name)

            # Prefer names with full city names (not abbreviated)
            city = self.extract_city(name)
            if city and city in self.CITY_EXPANSIONS:
                # Check if the original uses full city name
                if city in name.lower():
                    score += 10

            # Prefer longer names (more complete)
            score += len(normalized.split()) * 2

            # Prefer capitalized names
            if name[0].isupper():
                score += 1

            scored.append((score, name))

        # Return highest scored name
        scored.sort(reverse=True)
        return scored[0][1]

    def deduplicate_schools(self, school_list, key_func=None):
        """
        Deduplicate a list of schools

        Args:
            school_list: List of school names or school dictionaries
            key_func: Optional function to extract school name from item
                     (e.g., lambda x: x['team_name'] for dict items)

        Returns:
            List of deduplicated items with canonical names
        """
        if not school_list:
            return []

        # Default key function
        if key_func is None:
            key_func = lambda x: x if isinstance(x, str) else x.get('team_name', '')

        # Group similar schools
        groups = []
        used = set()

        for i, item in enumerate(school_list):
            if i in used:
                continue

            name1 = key_func(item)
            group = [item]
            used.add(i)

            # Find all similar schools
            for j, other_item in enumerate(school_list[i+1:], start=i+1):
                if j in used:
                    continue

                name2 = key_func(other_item)
                if self.are_duplicates(name1, name2):
                    group.append(other_item)
                    used.add(j)

            groups.append(group)

        # Select best representative from each group
        deduplicated = []
        for group in groups:
            if isinstance(group[0], str):
                # List of strings
                canonical = self.find_canonical_name(group)
                deduplicated.append(canonical)
            else:
                # List of dicts - merge data and use canonical name
                names = [key_func(item) for item in group]
                canonical_name = self.find_canonical_name(names)

                # Use the item that has the canonical name, or first item
                best_item = group[0]
                for item in group:
                    if key_func(item) == canonical_name:
                        best_item = item
                        break

                # Update name to canonical
                if isinstance(best_item, dict) and 'team_name' in best_item:
                    best_item = best_item.copy()
                    best_item['team_name'] = canonical_name

                deduplicated.append(best_item)

        logger.info(f"Deduplication: {len(school_list)} schools -> {len(deduplicated)} unique schools")
        if len(school_list) != len(deduplicated):
            logger.info(f"  Removed {len(school_list) - len(deduplicated)} duplicates")

        return deduplicated


def test_normalizer():
    """Test the school name normalizer"""
    normalizer = SchoolNameNormalizer()

    test_cases = [
        ("Arlington Sam Houston", "Arl Sam Houston"),
        ("Fort Worth Eastern Hills", "FW Eastern Hills"),
        ("Houston Westside High School", "Houston Westside"),
        ("Dallas Skyline HS", "Dallas Skyline"),
        ("San Antonio Central", "SA Central"),
    ]

    print("School Name Normalizer Tests")
    print("=" * 70)

    for name1, name2 in test_cases:
        is_dup = normalizer.are_duplicates(name1, name2)
        similarity = normalizer.similarity_score(name1, name2)
        print(f"\n'{name1}' vs '{name2}'")
        print(f"  Duplicate: {is_dup}")
        print(f"  Similarity: {similarity:.2%}")

    print("\n" + "=" * 70)
    print("\nDeduplication Test:")
    schools = [
        "Arlington Sam Houston",
        "Arl Sam Houston HS",
        "Houston Westside",
        "Houston Westside High School",
        "Dallas Skyline",
        "Fort Worth Eastern Hills"
    ]

    print(f"Original ({len(schools)}): {schools}")
    deduplicated = normalizer.deduplicate_schools(schools)
    print(f"\nDeduplicated ({len(deduplicated)}): {deduplicated}")


if __name__ == '__main__':
    test_normalizer()
