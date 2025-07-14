#!/usr/bin/env python3
"""
Twitter to Zotero Converter
将Twitter推文数据转换为Zotero可导入的CSL JSON格式
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse
import os


class TwitterToZoteroConverter:
    """Twitter数据到Zotero CSL JSON格式的转换器"""
    
    def __init__(self):
        self.output_data = []
    
    def clean_text(self, text: str) -> str:
        """清理推文文本，移除URL和特殊字符"""
        if not text:
            return ""
        
        # 移除URL
        # text = re.sub(r'https?://\S+', '', text)
        # 移除多余的空格
        text = re.sub(r'\s+', ' ', text).strip()
        # 解码HTML实体
        text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        
        return text
    
    def extract_author_from_url(self, url: str) -> str:
        """从推文URL中提取作者句柄"""
        if not url:
            return "Unknown Author"
        
        match = re.search(r'twitter\.com/([^/]+)/', url)
        if match:
            return match.group(1)
        
        return "Unknown Author"

    def parse_date(self, date_str: str) -> str:
        """解析Twitter日期格式并转换为ISO格式"""
        try:
            # Twitter日期格式: "Thu Jan 16 14:43:16 +0000 2025"
            dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return date_str
    
    def convert_tweet_to_zotero_item(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        """将单个推文转换为Zotero条目"""
        
        # 清理推文文本
        title = self.clean_text(tweet.get('full_text', ''))
        
        # 提取作者信息
        author_handle = self.extract_author_from_url(tweet.get('url', ''))
        
        # 解析日期
        date_issued = self.parse_date(tweet.get('created_at', ''))
        
        # 构建Zotero条目
        zotero_item = {
            "id": f"tweet_{tweet.get('id', '')}",
            "type": "post",
            "genre": "Tweet",
            "title": title,
            "author": [
                {
                    "literal": f"{author_handle} [@{author_handle}]"
                }
            ],
            "issued": {
                "date-parts": [[int(p) for p in date_issued.split('-')]]
            },
            "URL": tweet.get('url', ''),
            "accessed": {
                "date-parts": [[datetime.now().year, 
                               datetime.now().month, 
                               datetime.now().day]]
            },
            "container-title": "Twitter",
            "note": self._create_note(tweet),
            "language": tweet.get('lang', 'en')
        }
        
        # 添加标签（从hashtags）
        if tweet.get('hashtags'):
            zotero_item["tags"] = [{"tag": tag} for tag in tweet['hashtags']]
        
        return zotero_item
    
    def _create_note(self, tweet: Dict[str, Any]) -> str:
        """为推文创建详细的笔记"""
        note_parts = []
        
        # 添加统计信息
        stats = []
        if tweet.get('view_count'):
            stats.append(f"Views: {tweet['view_count']:,}")
        if tweet.get('favorite_count'):
            stats.append(f"Likes: {tweet['favorite_count']:,}")
        if tweet.get('retweet_count'):
            stats.append(f"Retweets: {tweet['retweet_count']:,}")
        if tweet.get('reply_count'):
            stats.append(f"Replies: {tweet['reply_count']:,}")
        if tweet.get('bookmark_count'):
            stats.append(f"Bookmarks: {tweet['bookmark_count']:,}")
        
        if stats:
            note_parts.append("Statistics: " + " | ".join(stats))
        
        # 添加媒体信息
        if tweet.get('medias'):
            media_count = len(tweet['medias'])
            note_parts.append(f"Media attachments: {media_count} item(s)")
        
        # 添加是否为引用推文
        if tweet.get('is_quote_status'):
            note_parts.append("Quote tweet: Yes")
        
        # 添加发布来源
        if tweet.get('source'):
            note_parts.append(f"Source: {tweet['source']}")
        
        # 添加用户提及
        if tweet.get('user_mentions'):
            mentions = ", ".join(tweet['user_mentions'])
            note_parts.append(f"Mentions: {mentions}")
        
        return "\n".join(note_parts)
    
    def convert_file(self, input_file: str, output_file: str) -> None:
        """转换整个JSON文件"""
        print(f"正在读取文件: {input_file}")
        
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                tweets = json.load(f)
            
            print(f"找到 {len(tweets)} 条推文")
            
            # 转换每条推文
            for i, tweet in enumerate(tweets):
                if i % 100 == 0:
                    print(f"已处理 {i}/{len(tweets)} 条推文...")
                
                zotero_item = self.convert_tweet_to_zotero_item(tweet)
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
        description="将Twitter推文数据转换为Zotero可导入的CSL JSON格式",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('input_file', help='输入的推文JSON文件路径')
    parser.add_argument('-o', '--output_file', help='输出的CSL JSON文件路径。如果未提供，将根据输入文件名自动生成。')

    args = parser.parse_args()

    output_file = args.output_file
    if not output_file:
        base_name = os.path.splitext(args.input_file)[0]
        output_file = f"{base_name}_zotero.json"
    
    converter = TwitterToZoteroConverter()
    
    print("=== Twitter to Zotero Converter ===")
    print("将Twitter推文数据转换为Zotero可导入的CSL JSON格式")
    print()
    
    converter.convert_file(args.input_file, output_file)
    
    print()
    print("使用说明:")
    print("1. 在Zotero中，选择 File -> Import")
    print(f"2. 选择生成的JSON文件 ({output_file})")
    print("3. 确保选择正确的导入格式（CSL JSON）")
    print("4. 点击导入完成")


if __name__ == "__main__":
    main() 