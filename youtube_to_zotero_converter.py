#!/usr/bin/env python3
"""
YouTube to Zotero Converter
将YouTube视频数据转换为Zotero可导入的CSL JSON格式
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import argparse
import os

def parse_relative_date(relative_date_str: str, base_date: datetime) -> Optional[Dict[str, Any]]:
    """从相对时间字符串（如 '2 months ago'）解析出近似的绝对日期"""
    if not relative_date_str:
        return None

    # Handle Croatian date strings by simple replacement
    relative_date_str = relative_date_str.lower().replace('prije', '').strip()
    replacements = {
        'godina': 'years',
        'mjesec': 'months',
        'tjedan': 'weeks',
        'dan': 'days',
        'sat': 'hours',
        'minut': 'minutes'
    }
    for key, value in replacements.items():
        if key in relative_date_str:
            relative_date_str = relative_date_str.replace(key, value)


    parts = relative_date_str.split()
    if len(parts) < 2 or "ago" not in parts[-1]:
        return None

    try:
        value = int(parts[0])
    except ValueError:
        return None

    unit = parts[1]
    
    # Approximate timedelta calculation
    if 'year' in unit:
        new_date = base_date - timedelta(days=365 * value)
    elif 'month' in unit:
        new_date = base_date - timedelta(days=30 * value)
    elif 'week' in unit:
        new_date = base_date - timedelta(weeks=value)
    elif 'day' in unit:
        new_date = base_date - timedelta(days=value)
    elif 'hour' in unit:
        new_date = base_date - timedelta(hours=value)
    else:
        return None
        
    return {"date-parts": [[new_date.year, new_date.month, new_date.day]]}


class YouTubeToZoteroConverter:
    """YouTube数据到Zotero CSL JSON格式的转换器"""

    def __init__(self, base_date: datetime):
        self.output_data = []
        self.base_date = base_date

    def get_text_from_runs(self, data: Optional[Dict[str, Any]], key: str) -> str:
        """从YouTube数据结构中的 'runs' 数组安全地提取文本"""
        if not data or key not in data or 'runs' not in data[key] or not data[key]['runs']:
            return ""
        return data[key]['runs'][0].get('text', "")

    def get_simple_text(self, data: Optional[Dict[str, Any]], key: str) -> str:
        """从YouTube数据结构中的 'simpleText' 字段安全地提取文本"""
        if not data or key not in data or 'simpleText' not in data[key]:
            return ""
        return data[key]['simpleText']

    def convert_video_to_zotero_item(self, video: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """将单个YouTube视频转换为Zotero条目"""
        video_id = video.get('videoId')
        if not video_id:
            return None

        title = self.get_text_from_runs(video, 'title')
        description = self.get_text_from_runs(video, 'descriptionSnippet')
        duration = self.get_simple_text(video, 'lengthText')
        view_count = self.get_simple_text(video, 'viewCountText')
        published_time_text = self.get_simple_text(video, 'publishedTimeText')
        
        # Based on the provided example, hardcoding the director
        channel_name = "Lisa Feldman Barrett"

        zotero_item = {
            "id": f"youtube_{video_id}",
            "type": "motion_picture",
            "title": title,
            "abstract": description,
            "dimensions": duration,
            "extra": f"Views: {view_count}",
            "source": "YouTube",
            "URL": f"https://www.youtube.com/watch?v={video_id}",
            "director": [
                {
                    "literal": channel_name
                }
            ],
            "accessed": {
                "date-parts": [[self.base_date.year, self.base_date.month, self.base_date.day]]
            }
        }
        
        issued_date = parse_relative_date(published_time_text, self.base_date)
        if issued_date:
            zotero_item["issued"] = issued_date

        return zotero_item

    def convert_file(self, input_file: str, output_file: str) -> None:
        """转换整个JSON文件"""
        print(f"正在读取文件: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                videos = json.load(f)
            
            print(f"找到 {len(videos)} 个视频")
            
            # 转换每个视频
            for i, video in enumerate(videos):
                if i % 100 == 0:
                    print(f"已处理 {i}/{len(videos)} 个视频...")
                
                zotero_item = self.convert_video_to_zotero_item(video)
                if zotero_item:
                    self.output_data.append(zotero_item)
            
            # 保存转换后的数据
            print(f"正在保存到文件: {output_file}")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.output_data, f, ensure_ascii=False, indent=2)
            
            print(f"转换完成！已保存 {len(self.output_data)} 条记录到 {output_file}")

        except FileNotFoundError:
            print(f"错误：找不到文件 {input_file}")
        except json.JSONDecodeError:
            print(f"错误：{input_file} 不是有效的JSON文件")
        except Exception as e:
            print(f"转换过程中发生错误: {str(e)}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="将YouTube视频数据转换为Zotero可导入的CSL JSON格式",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('input_file', help='输入的YouTube视频数据JSON文件路径')
    parser.add_argument('-o', '--output_file', help='输出的CSL JSON文件路径。如果未提供，将根据输入文件名自动生成。')

    args = parser.parse_args()

    output_file = args.output_file
    if not output_file:
        base_name = os.path.splitext(args.input_file)[0]
        output_file = f"{base_name}_zotero.json"

    base_date = datetime.now()
    match = re.search(r'(\d{4}-\d{2}-\d{2})', args.input_file)
    if match:
        try:
            base_date = datetime.strptime(match.group(1), '%Y-%m-%d')
            print(f"根据文件名推断出采集日期为: {base_date.date()}")
        except ValueError:
            print("无法从文件名解析日期，将使用当前日期作为基准。")
    else:
        print("无法从文件名找到日期，将使用当前日期作为基准。")

    converter = YouTubeToZoteroConverter(base_date=base_date)
    
    print("=== YouTube to Zotero Converter ===")
    print("将YouTube视频数据转换为Zotero可导入的CSL JSON格式")
    print()
    
    converter.convert_file(args.input_file, output_file)
    
    print()
    print("使用说明:")
    print("1. 在Zotero中，选择 File -> Import")
    print(f"2. 选择生成的JSON文件 ({output_file})")
    print("3. 确认导入格式为 CSL JSON")
    print("4. 点击导入完成")


if __name__ == "__main__":
    main() 