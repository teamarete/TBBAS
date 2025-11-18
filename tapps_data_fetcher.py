"""
TAPPS School District Data Fetcher
Extracts boys basketball school alignments from TAPPS PDF

PDF Source: TAPPS Alignment 2024-2026 (pages 35-41)
https://drive.google.com/file/d/1L9zFxC2Sd77Th6looL72ZpbihK1cM1dc/view
"""

import pdfplumber
import json
import re
from pathlib import Path


class TAPPSDataFetcher:
    def __init__(self, pdf_path='TAPPS_Alignment_2024-2026.pdf'):
        self.pdf_path = Path(pdf_path)
        self.schools = []

    def fetch_basketball_schools(self, start_page=35, end_page=41):
        """
        Extract boys basketball schools from TAPPS alignment PDF

        Args:
            start_page: First page with boys basketball data (35)
            end_page: Last page with boys basketball data (41)
        """
        if not self.pdf_path.exists():
            print(f"Error: PDF not found at {self.pdf_path}")
            print(f"Please download the PDF from:")
            print("https://drive.google.com/file/d/1L9zFxC2Sd77Th6looL72ZpbihK1cM1dc/view")
            print(f"And save it as: {self.pdf_path}")
            return []

        schools_by_classification = {
            '6A': [],
            '5A': [],
            '4A': [],
            '3A': [],
            '2A': [],
            '1A': []
        }

        print(f"Opening PDF: {self.pdf_path}")

        with pdfplumber.open(self.pdf_path) as pdf:
            # Pages 35-41 contain boys basketball
            for page_num in range(start_page - 1, end_page):  # 0-indexed
                if page_num >= len(pdf.pages):
                    print(f"Warning: Page {page_num + 1} not found in PDF")
                    continue

                page = pdf.pages[page_num]
                print(f"\nProcessing page {page_num + 1}...")

                # Extract text
                text = page.extract_text()

                if 'BOYS BASKETBALL' in text or 'Boys Basketball' in text:
                    print(f"  Found Boys Basketball section on page {page_num + 1}")

                    # Try table extraction
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            schools = self.parse_basketball_table(table)
                            for school in schools:
                                classification = school.get('classification')
                                if classification in schools_by_classification:
                                    schools_by_classification[classification].append(school)
                    else:
                        # Try text-based extraction
                        schools = self.parse_basketball_text(text)
                        for school in schools:
                            classification = school.get('classification')
                            if classification in schools_by_classification:
                                schools_by_classification[classification].append(school)

        # Convert to our internal format (TAPPS_6A, etc.)
        formatted_data = {}
        for classification, schools in schools_by_classification.items():
            if schools:
                key = f'TAPPS_{classification}'
                formatted_data[key] = schools
                print(f"\n{key}: {len(schools)} schools")

        return formatted_data

    def parse_basketball_table(self, table):
        """Parse boys basketball data from extracted table"""
        schools = []
        current_classification = None
        current_district = None

        for row in table:
            if not row or all(cell is None or str(cell).strip() == '' for cell in row):
                continue

            row_text = ' '.join(str(cell) for cell in row if cell)

            # Check for classification header (6A, 5A, etc.)
            class_match = re.search(r'\b([1-6])A\b', row_text)
            if class_match:
                current_classification = class_match.group(1) + 'A'
                continue

            # Check for district header
            district_match = re.search(r'District\s+(\d+)', row_text, re.IGNORECASE)
            if district_match:
                current_district = district_match.group(1)
                continue

            # If we have a classification and district, this might be a school
            if current_classification and current_district:
                # Clean school name
                school_name = self.clean_school_name(row_text)
                if school_name and len(school_name) > 3:
                    schools.append({
                        'school_name': school_name,
                        'district': current_district,
                        'classification': current_classification
                    })

        return schools

    def parse_basketball_text(self, text):
        """Parse boys basketball data from raw text"""
        schools = []
        lines = text.split('\n')
        current_classification = None
        current_district = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for classification
            class_match = re.search(r'\b([1-6])A\b', line)
            if class_match:
                current_classification = class_match.group(1) + 'A'
                continue

            # Check for district
            district_match = re.search(r'District\s+(\d+)', line, re.IGNORECASE)
            if district_match:
                current_district = district_match.group(1)
                continue

            # School name
            if current_classification and current_district:
                school_name = self.clean_school_name(line)
                if school_name and len(school_name) > 3:
                    schools.append({
                        'school_name': school_name,
                        'district': current_district,
                        'classification': current_classification
                    })

        return schools

    def clean_school_name(self, name):
        """Clean and normalize school name"""
        if not name:
            return None

        # Remove common patterns
        name = re.sub(r'District\s+\d+', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b[1-6]A\b', '', name)
        name = re.sub(r'BOYS BASKETBALL', '', name, flags=re.IGNORECASE)
        name = re.sub(r'Boys Basketball', '', name, flags=re.IGNORECASE)

        # Clean whitespace
        name = ' '.join(name.split())
        name = name.strip()

        # Remove trailing dashes, commas, etc.
        name = name.rstrip(',-–—')

        return name if name else None

    def save_to_json(self, data, output_file='data/tapps_schools.json'):
        """Save TAPPS school data to JSON file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"\n✓ Saved TAPPS school data to {output_path}")
        return output_path


def main():
    """Main execution"""
    print("TAPPS Boys Basketball School Data Fetcher")
    print("=" * 60)

    fetcher = TAPPSDataFetcher()
    data = fetcher.fetch_basketball_schools(start_page=35, end_page=41)

    if data:
        fetcher.save_to_json(data)

        # Print summary
        print("\n" + "=" * 60)
        print("TAPPS Schools Summary:")
        print("=" * 60)
        total = 0
        for classification, schools in sorted(data.items()):
            count = len(schools)
            total += count
            print(f"{classification:12s}: {count:3d} schools")
        print(f"{'TOTAL':12s}: {total:3d} schools")
    else:
        print("\nNo data extracted. Please check the PDF file.")


if __name__ == "__main__":
    main()
