"""
UIL School Matcher - Matches game team names to official UIL schools
Ensures data integrity by verifying schools against official UIL data
"""

import json
from pathlib import Path
from difflib import SequenceMatcher
from school_name_normalizer import SchoolNameNormalizer

class UILSchoolMatcher:
    """Matches team names to official UIL schools"""

    def __init__(self, uil_data_path='data/uil_schools.json'):
        self.uil_data_path = Path(__file__).parent / uil_data_path
        self.uil_schools = self.load_uil_data()
        self.normalizer = SchoolNameNormalizer()

        # Build lookup indexes for faster matching
        self.school_by_name = {}
        self.schools_by_classification = {}

        for classification, schools in self.uil_schools.items():
            self.schools_by_classification[classification] = schools
            for school in schools:
                name = school['school_name']
                if name not in self.school_by_name:
                    self.school_by_name[name] = []
                self.school_by_name[name].append(school)

    def load_uil_data(self):
        """Load UIL school data from JSON"""
        if not self.uil_data_path.exists():
            print(f"Warning: UIL data file not found at {self.uil_data_path}")
            return {}

        with open(self.uil_data_path, 'r') as f:
            return json.load(f)

    def find_school_match(self, team_name, classification_code=None):
        """
        Find the best UIL school match for a team name

        Args:
            team_name: Name of the team from game data
            classification_code: Optional classification (AAAAAA, AAAAA, etc.)

        Returns:
            dict with match info or None if no match found
        """
        if not team_name:
            return None

        # Convert classification code to UIL format if provided
        classification = None
        if classification_code:
            classification = self.classification_code_to_uil(classification_code)

        # Try exact match first
        normalized_name = self.normalize_team_name(team_name)
        for uil_name, schools in self.school_by_name.items():
            if self.normalize_team_name(uil_name) == normalized_name:
                # If multiple schools with same name, use classification to disambiguate
                if len(schools) > 1 and classification:
                    for school in schools:
                        if school['classification'] == classification:
                            return {
                                'matched': True,
                                'confidence': 'exact',
                                'official_name': school['school_name'],
                                'district': school['district'],
                                'classification': school['classification'],
                                'classification_code': school['classification_code'],
                                'ambiguous': False
                            }
                    # Classification provided but didn't match - ambiguous
                    return {
                        'matched': True,
                        'confidence': 'exact_name_wrong_class',
                        'official_name': schools[0]['school_name'],
                        'district': schools[0]['district'],
                        'classification': schools[0]['classification'],
                        'classification_code': schools[0]['classification_code'],
                        'ambiguous': True,
                        'possible_schools': schools
                    }
                else:
                    # Single match or no classification to disambiguate
                    school = schools[0]
                    return {
                        'matched': True,
                        'confidence': 'exact',
                        'official_name': school['school_name'],
                        'district': school['district'],
                        'classification': school['classification'],
                        'classification_code': school['classification_code'],
                        'ambiguous': len(schools) > 1
                    }

        # Try fuzzy matching
        best_match = None
        best_score = 0.0

        for classification_key, schools in self.uil_schools.items():
            # If classification specified, only search that classification
            if classification and classification_key != classification:
                continue

            for school in schools:
                uil_name = school['school_name']
                score = self.similarity_score(normalized_name, self.normalize_team_name(uil_name))

                if score > best_score and score >= 0.85:  # 85% similarity threshold
                    best_score = score
                    best_match = {
                        'matched': True,
                        'confidence': 'fuzzy',
                        'similarity_score': score,
                        'official_name': school['school_name'],
                        'district': school['district'],
                        'classification': school['classification'],
                        'classification_code': school['classification_code'],
                        'ambiguous': False,
                        'original_name': team_name
                    }

        if best_match:
            return best_match

        # No match found
        return {
            'matched': False,
            'confidence': 'none',
            'original_name': team_name,
            'classification_code': classification_code
        }

    def normalize_team_name(self, name):
        """Normalize team name for comparison"""
        if not name:
            return ""

        # Use existing normalizer
        canonical = self.normalizer.normalize(name)

        # Additional normalization
        canonical = canonical.lower()
        canonical = canonical.replace('high school', '').replace('hs', '')
        canonical = canonical.replace('.', '').replace(',', '')
        canonical = ' '.join(canonical.split())  # Remove extra whitespace

        return canonical.strip()

    def similarity_score(self, str1, str2):
        """Calculate similarity score between two strings"""
        return SequenceMatcher(None, str1, str2).ratio()

    def classification_code_to_uil(self, code):
        """Convert classification code to UIL format (AAAAAA -> 6A)"""
        mapping = {
            'AAAAAA': '6A',
            'AAAAA': '5A',
            'AAAA': '4A',
            'AAA': '3A',
            'AA': '2A',
            'A': '1A'
        }
        return mapping.get(code, code)

    def uil_to_classification_code(self, uil_class):
        """Convert UIL format to classification code (6A -> AAAAAA)"""
        mapping = {
            '6A': 'AAAAAA',
            '5A': 'AAAAA',
            '4A': 'AAAA',
            '3A': 'AAA',
            '2A': 'AA',
            '1A': 'A'
        }
        return mapping.get(uil_class, uil_class)

    def get_schools_by_name(self, partial_name):
        """Find all UIL schools with similar names"""
        matches = []
        normalized_search = self.normalize_team_name(partial_name)

        for classification, schools in self.uil_schools.items():
            for school in schools:
                normalized_school = self.normalize_team_name(school['school_name'])
                if normalized_search in normalized_school or normalized_school in normalized_search:
                    matches.append(school)

        return matches

    def diagnose_team_records(self, team_name, classification_code, games_count):
        """
        Diagnose if a team's record might be incorrect due to school conflation

        Args:
            team_name: Team name to check
            classification_code: Classification they're listed under
            games_count: Number of games recorded

        Returns:
            dict with diagnosis info
        """
        match = self.find_school_match(team_name, classification_code)
        possible_schools = self.get_schools_by_name(team_name)

        diagnosis = {
            'team_name': team_name,
            'classification_code': classification_code,
            'games_count': games_count,
            'match': match,
            'possible_schools': possible_schools,
            'conflation_risk': len(possible_schools) > 1
        }

        if len(possible_schools) > 1:
            diagnosis['warning'] = f"Found {len(possible_schools)} schools with similar names"
            diagnosis['recommendation'] = "Review games to ensure they're all from the same school"

        return diagnosis


def main():
    """Test the UIL school matcher"""
    matcher = UILSchoolMatcher()

    print("="*60)
    print("UIL School Matcher - Testing")
    print("="*60)

    # Test exact matches
    print("\n1. Testing exact matches:")
    test_cases = [
        ("North Crowley", "AAAAAA"),
        ("Allen", "AAAAAA"),
        ("Lancaster", "AAAAAA"),
    ]

    for team_name, class_code in test_cases:
        result = matcher.find_school_match(team_name, class_code)
        print(f"\n  {team_name} ({class_code}):")
        if result['matched']:
            print(f"    ✓ Matched: {result['official_name']}")
            print(f"    District: {result['district']}")
            print(f"    Classification: {result['classification']}")
            print(f"    Confidence: {result['confidence']}")
        else:
            print(f"    ✗ No match found")

    # Test ambiguous case - Jefferson
    print("\n2. Testing ambiguous case (Jefferson):")
    result = matcher.find_school_match("Jefferson", "AAA")
    print(f"\n  Jefferson (AAA):")
    print(f"    Matched: {result['matched']}")
    print(f"    Confidence: {result['confidence']}")
    if result.get('ambiguous'):
        print(f"    ⚠ AMBIGUOUS - Multiple schools found")
    if result.get('official_name'):
        print(f"    Official name: {result['official_name']}")
        print(f"    District: {result['district']}")
        print(f"    Classification: {result['classification']}")

    # Show all Jefferson schools
    print("\n3. All schools with 'Jefferson' in name:")
    jefferson_schools = matcher.get_schools_by_name("Jefferson")
    for school in jefferson_schools:
        print(f"    - {school['school_name']}")
        print(f"      {school['classification']} District {school['district']}")

    # Diagnose Jefferson's record
    print("\n4. Diagnosing Jefferson record issue:")
    diagnosis = matcher.diagnose_team_records("Jefferson", "AAA", games_count=2)
    print(f"\n  Team: {diagnosis['team_name']}")
    print(f"  Games recorded: {diagnosis['games_count']}")
    print(f"  Conflation risk: {diagnosis['conflation_risk']}")
    if diagnosis.get('warning'):
        print(f"  ⚠ {diagnosis['warning']}")
        print(f"  → {diagnosis['recommendation']}")
    print(f"\n  Possible schools:")
    for school in diagnosis['possible_schools']:
        print(f"    - {school['school_name']} ({school['classification']} Dist {school['district']})")


if __name__ == "__main__":
    main()
