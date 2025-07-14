import csv
import json
from datetime import datetime
from urllib.parse import urlparse
import argparse
import os

def convert_csv_to_zotero_json(csv_file_path, json_file_path):
    """
    将播客元数据的CSV文件转换为Zotero的CSL JSON格式。
    """
    zotero_items = []
    
    with open(csv_file_path, mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                date_str = row['lfb-links-date']
                issued_date = datetime.strptime(date_str, '%B %d, %Y')
                issued_date_parts = [issued_date.year, issued_date.month, issued_date.day]
            except (ValueError, KeyError) as e:
                print(f"因日期处理错误跳过此行: {row}. 错误: {e}")
                continue

            try:
                url = row['lfb-links-link href']
                if not url: # check for empty url string
                    print(f"因URL为空跳过此行: {row}")
                    continue
                parsed_url = urlparse(url)
                source = parsed_url.hostname
            except KeyError:
                print(f"因缺少URL跳过此行: {row}")
                continue

            today = datetime.now()
            accessed_date_parts = [today.year, today.month, today.day]

            item = {
                "type": "song",  # 根据用户示例，播客使用 'song' 类型
                "title": row.get('lfb-links-link', 'No Title'),
                "URL": url,
                "abstract": row.get('lfb-links-description', ''),
                "source": source,
                "language": "en-US", # 播客是英文的
                "issued": {
                    "date-parts": [
                        issued_date_parts
                    ]
                },
                "accessed": {
                    "date-parts": [
                        [today.year, today.month, today.day]
                    ]
                }
            }
            zotero_items.append(item)

    with open(json_file_path, mode='w', encoding='utf-8') as jsonfile:
        json.dump(zotero_items, jsonfile, indent=4, ensure_ascii=False)

    print(f"转换成功，输出文件已写入 {json_file_path}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='将播客元数据的CSV文件转换为Zotero的CSL JSON格式。')
    parser.add_argument('input_csv', help='输入的CSV文件路径')
    parser.add_argument('-o', '--output_json', help='输出的JSON文件路径。如果未提供，将根据输入文件名自动生成。')

    args = parser.parse_args()

    output_json_path = args.output_json
    if not output_json_path:
        base_name = os.path.splitext(args.input_csv)[0]
        output_json_path = f"{base_name}_zotero.json"

    convert_csv_to_zotero_json(args.input_csv, output_json_path) 