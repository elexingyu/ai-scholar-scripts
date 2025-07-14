import csv
import json
import re
import argparse
import os

def parse_name(name_str):
    """Parses a name string like 'LAST, FIRST M' into family and given names."""
    if ',' in name_str:
        parts = name_str.split(',', 1)
        family = parts[0].strip()
        given = parts[1].strip()
        # Capitalize first letter of each part of the name for better formatting
        family = ' '.join([n.capitalize() for n in family.split()])
        given = ' '.join([n.capitalize() for n in given.split()])
        return {"family": family, "given": given}
    else:
        # Simple fallback for names without a comma
        return {"literal": name_str.strip().title()}

def convert_grants_to_csl(input_csv_path, output_json_path):
    """
    Converts NIH grant data from a CSV file to a CSL JSON file for Zotero.
    """
    csl_items = []
    
    with open(input_csv_path, 'r', encoding='utf-8') as f:
        # Find the header row, skipping initial metadata lines
        lines = f.readlines()
        header_line_index = -1
        for i, line in enumerate(lines):
            if '"NIH Spending Categorization"' in line:
                header_line_index = i
                break
        
        if header_line_index == -1:
            print("Error: Could not find the header row in the CSV file.")
            return

        # Use the rest of the lines for the CSV reader
        csv_content = lines[header_line_index:]
        reader = csv.DictReader(csv_content)
        
        for row in reader:
            authors = []
            if row.get("Contact PI / Project Leader"):
                authors.append(parse_name(row["Contact PI / Project Leader"]))
            
            if row.get("Other PI or Project Leader(s)"):
                other_pis = row["Other PI or Project Leader(s)"].split(';')
                for pi in other_pis:
                    if pi.strip() and pi.strip().lower() != 'not applicable':
                        authors.append(parse_name(pi))

            # Format the issued date
            issued_date = None
            if row.get("Project Start Date"):
                try:
                    date_parts = re.split(r'[/.-]', row["Project Start Date"])
                    if len(date_parts) == 3:
                        month, day, year = map(int, date_parts)
                        issued_date = {"date-parts": [[year, month, day]]}
                except (ValueError, IndexError):
                    pass # Ignore if date format is incorrect

            # Construct keywords
            keywords = []
            if row.get("Project Terms"):
                keywords = [kw.strip() for kw in row["Project Terms"].split(';') if kw.strip()]

            # Construct a note with additional info
            note_parts = []
            if row.get("Organization Name"):
                note_parts.append(f"Awarded to: {row['Organization Name']}")
            if row.get("Project End Date"):
                note_parts.append(f"Project End: {row['Project End Date']}")
            if row.get("Total Cost"):
                note_parts.append(f"Total Cost: ${row['Total Cost']}")
            note = ". ".join(note_parts)
            
            csl_item = {
                "type": "report",
                "genre": "Grant",
                "id": row.get("Application ID", ""),
                "title": row.get("Project Title", "No Title"),
                "author": authors,
                "issued": issued_date,
                "number": row.get("Project Number", ""),
                "publisher": row.get("Funding IC(s)", ""),
                "publisher-place": f'{row.get("Organization City", "")}, {row.get("Organization State", "")}',
                "abstract": row.get("Project Abstract", ""),
                "URL": f'https://reporter.nih.gov/project-details/{row.get("Application ID", "")}' if row.get("Application ID") else "",
                "keyword": keywords,
                "note": note
            }
            csl_items.append(csl_item)

    with open(output_json_path, 'w', encoding='utf-8') as f:
        json.dump(csl_items, f, indent=4, ensure_ascii=False)

    print(f"Successfully converted {len(csl_items)} grant(s) to {output_json_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts NIH grant data from a CSV file to a CSL JSON file for Zotero.')
    parser.add_argument('input_csv', help='The path to the input CSV file.')
    parser.add_argument('-o', '--output_json', help='The path to the output JSON file. If not provided, it will be generated based on the input filename.')
    
    args = parser.parse_args()

    output_json_path = args.output_json
    if not output_json_path:
        base_name = os.path.splitext(args.input_csv)[0]
        output_json_path = f"{base_name}-csl.json"

    convert_grants_to_csl(args.input_csv, output_json_path) 