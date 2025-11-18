"""
UIL Data Fetcher V3 - Uses table extraction for accurate parsing
"""

import requests
import re
from pathlib import Path
import json
import pdfplumber
from io import BytesIO

class UILDataFetcherV3:
    """Fetches and parses official UIL basketball alignment data using table extraction"""

    # Official UIL alignment PDFs for 2025-26 basketball season
    UIL_PDFS = {
        '6A': 'https://www.uiltexas.org/files/alignments/25-266A_BB.pdf',
        '5A': 'https://www.uiltexas.org/files/alignments/25-265A_BB.pdf',
        '4A': 'https://www.uiltexas.org/files/alignments/4ABB_Rvsd7-25.pdf',
        '3A': 'https://www.uiltexas.org/files/alignments/25-263ABB_rvsd3-28.pdf',
        '2A': 'https://www.uiltexas.org/files/alignments/25-262A_BB.pdf',
        '1A': 'https://www.uiltexas.org/files/alignments/25-261ABB_Rvsd4-4.pdf'
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.uil_data = {}

    def fetch_all_uil_data(self):
        """Fetch and parse all UIL PDFs"""
        print("Fetching UIL basketball alignment data...")

        for classification, url in self.UIL_PDFS.items():
            print(f"\nFetching {classification} data from {url}")
            try:
                schools = self.parse_uil_pdf(url, classification)
                self.uil_data[classification] = schools
                print(f"  ✓ Found {len(schools)} schools in {classification}")
            except Exception as e:
                print(f"  ✗ Error parsing {classification}: {e}")
                import traceback
                traceback.print_exc()

        return self.uil_data

    def parse_uil_pdf(self, url, classification):
        """Parse a UIL PDF using table extraction"""
        schools = []

        # Download PDF
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        # Parse PDF with pdfplumber
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract tables
                table_settings = {
                    'vertical_strategy': 'text',
                    'horizontal_strategy': 'text',
                    'intersection_tolerance': 15
                }

                tables = page.extract_tables(table_settings)

                if not tables:
                    continue

                for table in tables:
                    # Process each column as a district
                    num_cols = len(table[0]) if table else 0

                    for col_idx in range(num_cols):
                        district_num = None
                        schools_in_district = []

                        for row_idx, row in enumerate(table):
                            if col_idx >= len(row):
                                continue

                            cell = row[col_idx]

                            if not cell or not cell.strip():
                                continue

                            # Check if this cell contains a district number
                            district_match = re.search(r'District\s+(\d+)', cell, re.IGNORECASE)
                            if district_match:
                                # If we already have a district with schools, save them first
                                if district_num and schools_in_district:
                                    for school_name in schools_in_district:
                                        schools.append({
                                            'school_name': school_name,
                                            'district': district_num,
                                            'classification': classification,
                                            'classification_code': self.get_classification_code(classification)
                                        })
                                    schools_in_district = []

                                # Start new district
                                district_num = district_match.group(1)
                                continue

                            # If we have a district number, this is a school
                            if district_num:
                                # Clean the school name (may be split across cells or have multiple schools)
                                school_text = cell.strip()

                                # Merge with previous school if it looks incomplete (starts with lowercase)
                                if schools_in_district and len(schools_in_district[-1]) < 15 and school_text and not school_text[0].isupper():
                                    schools_in_district[-1] += ' ' + school_text
                                else:
                                    # Split by school names (capital letter after space typically indicates new school)
                                    # But need to be careful with names like "El Paso" or "Fort Bend"
                                    potential_schools = self.split_school_names(school_text)

                                    for school_name in potential_schools:
                                        school_name = self.clean_school_name(school_name)
                                        if school_name:
                                            schools_in_district.append(school_name)

                        # Save any remaining schools for this column
                        if district_num and schools_in_district:
                            for school_name in schools_in_district:
                                schools.append({
                                    'school_name': school_name,
                                    'district': district_num,
                                    'classification': classification,
                                    'classification_code': self.get_classification_code(classification)
                                })

        # Remove duplicates
        seen = set()
        unique_schools = []
        for school in schools:
            key = (school['school_name'], school['district'])
            if key not in seen:
                seen.add(key)
                unique_schools.append(school)

        return unique_schools

    def split_school_names(self, text):
        """
        Split a cell that may contain multiple school names

        School names typically start with a capital letter after a space.
        Common patterns: "School1 School2 School3" or "City1 School1 City2 School2"
        """
        if not text:
            return []

        # Split on pattern: space followed by capital letter, but not for common multi-word city names
        # Common prefixes that should stay together: El, Fort, San, La, Las, Los, Del, De
        protected_prefixes = ['El', 'Fort', 'San', 'La', 'Las', 'Los', 'Del', 'De', 'Van', 'North', 'South', 'East', 'West', 'New', 'Port', 'Mount', 'Lake']

        # Common city/school suffixes that are part of the name
        protected_suffixes = ['Paso', 'Worth', 'Bend', 'Antonio', 'Angelo', 'Springs', 'Vista', 'Ridge', 'Point', 'Rock', 'Park', 'City', 'Valley', 'Hills', 'Heights']

        schools = []
        current_school = []
        words = text.split()

        for i, word in enumerate(words):
            if i == 0:
                current_school.append(word)
                continue

            # Check if this word starts a new school
            # New school if: starts with capital AND previous word is not a protected prefix AND current word is not a protected suffix
            if word[0].isupper():
                prev_word = words[i-1] if i > 0 else ''
                is_protected_continuation = prev_word in protected_prefixes or word in protected_suffixes

                # Also check if current_school is very short (1-2 words) - likely part of same name
                is_short_name = len(current_school) <= 2

                if not is_protected_continuation and not is_short_name and current_school:
                    # Check if current school makes sense (not just a single short word)
                    school_name = ' '.join(current_school)
                    if len(school_name) >= 5:  # Increased minimum length
                        schools.append(school_name)
                    current_school = [word]
                else:
                    current_school.append(word)
            else:
                current_school.append(word)

        # Add the last school
        if current_school:
            school_name = ' '.join(current_school)
            if len(school_name) >= 5:  # Increased minimum length
                schools.append(school_name)

        # If no schools found (everything was too short), return original text
        return schools if schools else [text]

    def clean_school_name(self, name):
        """Clean and normalize school name"""
        if not name:
            return None

        # Remove common suffixes
        name = re.sub(r'\s+HS$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+High School$', '', name, flags=re.IGNORECASE)

        # Remove extra whitespace
        name = ' '.join(name.split())

        # Skip obvious non-school entries
        skip_keywords = ['DISTRICT', 'REGION', 'AREA', 'CONFERENCE', 'DIVISION', 'FOOTBALL', 'BASKETBALL', 'OFFICIAL', 'ALIGNMENT']
        if any(keyword in name.upper() for keyword in skip_keywords):
            return None

        # Must be at least 3 characters
        if len(name) < 3:
            return None

        # Skip numeric-only or single character names
        if name.isdigit() or len(name) == 1:
            return None

        return name.strip()

    def get_classification_code(self, classification):
        """Convert classification to internal code (e.g., '6A' -> 'AAAAAA')"""
        mapping = {
            '6A': 'AAAAAA',
            '5A': 'AAAAA',
            '4A': 'AAAA',
            '3A': 'AAA',
            '2A': 'AA',
            '1A': 'A'
        }
        return mapping.get(classification, classification)

    def save_to_json(self, filename='data/uil_schools.json'):
        """Save UIL data to JSON file"""
        output_path = Path(__file__).parent / filename
        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(self.uil_data, f, indent=2)

        print(f"\n✓ UIL data saved to {output_path}")

    def find_school(self, school_name, classification=None):
        """Find a school by name, optionally filtering by classification"""
        matches = []

        for class_code, schools in self.uil_data.items():
            if classification and class_code != classification:
                continue

            for school in schools:
                # Exact match
                if school['school_name'].lower() == school_name.lower():
                    matches.append(school)
                # Partial match
                elif school_name.lower() in school['school_name'].lower():
                    matches.append(school)

        return matches


def main():
    """Fetch and save UIL data"""
    fetcher = UILDataFetcherV3()

    # Fetch all data
    data = fetcher.fetch_all_uil_data()

    # Print summary
    print("\n" + "="*50)
    print("UIL Data Summary")
    print("="*50)
    total = 0
    for classification, schools in data.items():
        count = len(schools)
        total += count
        print(f"{classification}: {count} schools")
    print(f"\nTotal: {total} schools")

    # Save to JSON
    fetcher.save_to_json()

    # Show sample schools from each classification
    print("\n" + "="*50)
    print("Sample Schools from Each Classification")
    print("="*50)
    for classification, schools in data.items():
        print(f"\n{classification} (showing first 10):")
        for school in schools[:10]:
            print(f"  • {school['school_name']} - District {school['district']}")

    # Search for specific schools to verify
    print("\n" + "="*50)
    print("Verification - Searching for specific schools")
    print("="*50)

    test_schools = ['Allen', 'North Crowley', 'Lancaster', 'Jefferson']
    for test_name in test_schools:
        matches = fetcher.find_school(test_name)
        print(f"\n'{test_name}' - Found {len(matches)} matches:")
        for match in matches[:5]:  # Show first 5
            print(f"  • {match['school_name']} ({match['classification']} District {match['district']})")


if __name__ == "__main__":
    main()
