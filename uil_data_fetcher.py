"""
Fetch and parse UIL classification and district data from official PDFs
This ensures data integrity by cross-referencing schools with their official UIL classification and district
"""

import requests
import re
from pathlib import Path
import json
import pdfplumber
from io import BytesIO

class UILDataFetcher:
    """Fetches and parses official UIL basketball alignment data"""

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

        return self.uil_data

    def parse_uil_pdf(self, url, classification):
        """Parse a UIL PDF to extract schools and districts"""
        schools = []

        # Download PDF
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        # Parse PDF with pdfplumber
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            current_district = None

            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split('\n')

                for line in lines:
                    line = line.strip()

                    # Check for district header (e.g., "District 1-6A", "1-6A", "DISTRICT 1")
                    district_match = re.search(r'(?:DISTRICT\s+)?(\d+)(?:-\d+A)?', line, re.IGNORECASE)
                    if district_match and len(line) < 30:  # Short lines are likely headers
                        current_district = district_match.group(1)
                        continue

                    # Extract school names
                    # Schools are typically listed with city/location
                    # Pattern: "School Name (City)" or "City School Name"
                    school_match = re.search(r'^([A-Z][A-Za-z\s\-\'\.]+(?:\s+HS)?)', line)
                    if school_match:
                        school_name = school_match.group(1).strip()

                        # Clean up school name
                        school_name = self.clean_school_name(school_name)

                        if school_name and current_district:
                            schools.append({
                                'school_name': school_name,
                                'district': current_district,
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

    def clean_school_name(self, name):
        """Clean and normalize school name"""
        # Remove common suffixes
        name = re.sub(r'\s+HS$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+High School$', '', name, flags=re.IGNORECASE)

        # Remove extra whitespace
        name = ' '.join(name.split())

        # Skip obvious non-school entries
        skip_keywords = ['DISTRICT', 'REGION', 'AREA', 'CONFERENCE', 'DIVISION']
        if any(keyword in name.upper() for keyword in skip_keywords):
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

    def get_school_district(self, school_name, classification_code):
        """Get the official district for a school"""
        classification = self.get_classification_from_code(classification_code)

        if classification in self.uil_data:
            for school in self.uil_data[classification]:
                if school['school_name'].lower() == school_name.lower():
                    return school['district']

        return None

    def get_classification_from_code(self, code):
        """Convert internal code to classification (e.g., 'AAAAAA' -> '6A')"""
        mapping = {
            'AAAAAA': '6A',
            'AAAAA': '5A',
            'AAAA': '4A',
            'AAA': '3A',
            'AA': '2A',
            'A': '1A'
        }
        return mapping.get(code, code)


def main():
    """Fetch and save UIL data"""
    fetcher = UILDataFetcher()

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

    # Example: Find all Jefferson schools
    print("\n" + "="*50)
    print("Example: Finding 'Jefferson' schools")
    print("="*50)
    matches = fetcher.find_school('Jefferson')
    for match in matches:
        print(f"  {match['school_name']} - {match['classification']} District {match['district']}")


if __name__ == "__main__":
    main()
