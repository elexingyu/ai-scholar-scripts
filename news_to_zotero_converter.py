import csv
import json
import argparse
import os

def convert_csv_to_csl_json(csv_file_path, json_file_path):
    """
    Converts a CSV file from a news search into a Zotero-compatible CSL JSON file.
    """
    csl_items = []
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            # Clean up title by removing leading characters like '|' and spaces
            title = row.get('result', '').lstrip('| ').strip()
            
            # Skip rows without a URL or title
            if not row.get('url_header href') or not title:
                continue

            # Construct the author from highlight fields if available, otherwise default
            author_given = row.get('highlight', 'Lisa')
            author_family = f"{row.get('highlight 2', 'Feldman')} {row.get('highlight 3', 'Barrett')}".strip()

            csl_item = {
                "type": "webpage",
                "title": title,
                "URL": row.get('url_header href'),
                "abstract": row.get('content', ''),
                "author": [
                    {
                        "given": author_given,
                        "family": author_family
                    }
                ]
            }
            csl_items.append(csl_item)

    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(csl_items, json_file, indent=4, ensure_ascii=False)

    print(f"Successfully converted {len(csl_items)} items from '{csv_file_path}' to '{json_file_path}'.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts a CSV file from a news search into a Zotero-compatible CSL JSON file.')
    parser.add_argument('input_csv', help='The path to the input CSV file.')
    parser.add_argument('-o', '--output_json', help='The path to the output JSON file. If not provided, it will be generated based on the input filename.')
    
    args = parser.parse_args()

    output_json_path = args.output_json
    if not output_json_path:
        base_name = os.path.splitext(args.input_csv)[0]
        output_json_path = f"{base_name}-zotero.json"

    convert_csv_to_csl_json(args.input_csv, output_json_path) 