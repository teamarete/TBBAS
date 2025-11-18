"""
Improved UIL Data Fetcher - Parses UIL alignment PDFs more accurately
Handles multi-column district format
"""

import requests
import re
from pathlib import Path
import json
import pdfplumber
from io import BytesIO

class UILDataFetcherV2:
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
        """Parse a UIL PDF using character positions to extract schools and districts"""
        schools = []

        # Download PDF
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        # Parse PDF with pdfplumber
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            for page in pdf.pages:
                # Extract words with their positions
                words = page.extract_words()

                if not words:
                    continue

                # Find all district headers by looking for "District" followed by a number
                district_headers = []
                for i, word in enumerate(words):
                    if 'district' in word['text'].lower():
                        # Look for number after "District"
                        if i + 1 < len(words) and words[i + 1]['text'].isdigit():
                            district_num = words[i + 1]['text']
                            district_headers.append({
                                'district': district_num,
                                'x0': word['x0'],
                                'x1': words[i + 1]['x1'],
                                'top': word['top'],
                                'y': word['top']
                            })

                # Sort districts by position (left to right, top to bottom)
                district_headers.sort(key=lambda d: (d['y'], d['x0']))

                # For each district, find schools below it
                for dist_idx, district_info in enumerate(district_headers):
                    district_num = district_info['district']

                    # Define the column boundaries
                    col_left = district_info['x0'] - 10  # A bit of tolerance

                    # Find right boundary (next district on same row or right edge)
                    col_right = page.width
                    for other_dist in district_headers:
                        if other_dist['district'] != district_num and abs(other_dist['y'] - district_info['y']) < 15:
                            if other_dist['x0'] > district_info['x0']:
                                col_right = other_dist['x0']
                                break

                    # Find bottom boundary (next district row or page bottom)
                    row_bottom = page.height
                    for other_dist in district_headers:
                        if other_dist['y'] > district_info['y'] + 15:
                            row_bottom = other_dist['y']
                            break

                    # Extract schools in this column
                    school_words = []
                    current_school = []

                    for word in words:
                        # Check if word is in this district's column
                        if (word['x0'] >= col_left and word['x0'] < col_right and
                            word['top'] > district_info['top'] + 10 and word['top'] < row_bottom):

                            # Skip obviously non-school words
                            if word['text'].lower() in ['district', 'region', 'conference']:
                                continue

                            # If this is a new line (significant vertical gap), process previous school
                            if current_school and len(current_school) > 0:
                                # Check if this word is on a new line
                                prev_word = current_school[-1]
                                if word['top'] - prev_word['top'] > 5:
                                    # Process accumulated school name
                                    school_name = ' '.join([w['text'] for w in current_school])
                                    school_name = self.clean_school_name(school_name)
                                    if school_name:
                                        schools.append({
                                            'school_name': school_name,
                                            'district': district_num,
                                            'classification': classification,
                                            'classification_code': self.get_classification_code(classification)
                                        })
                                    current_school = []

                            current_school.append(word)

                    # Process last school in column
                    if current_school:
                        school_name = ' '.join([w['text'] for w in current_school])
                        school_name = self.clean_school_name(school_name)
                        if school_name:
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
        skip_keywords = ['DISTRICT', 'REGION', 'AREA', 'CONFERENCE', 'DIVISION', 'FOOTBALL', 'BASKETBALL']
        if any(keyword in name.upper() for keyword in skip_keywords):
            return None

        # Must be at least 3 characters
        if len(name) < 3:
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
    fetcher = UILDataFetcherV2()

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
        print(f"\n{classification} (showing first 5):")
        for school in schools[:5]:
            print(f"  • {school['school_name']} - District {school['district']}")


if __name__ == "__main__":
    main()
