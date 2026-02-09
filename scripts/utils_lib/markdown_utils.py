"""Markdown处理工具"""

import re
import yaml
from typing import List, Tuple, Optional, Dict


class MarkdownUtils:
    """Markdown处理工具类"""
    
    @staticmethod
    def extract_front_matter(content: str) -> Tuple[Optional[Dict], str]:
        """提取Front Matter和内容"""
        if not content.startswith('---'):
            return None, content
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None, content
        
        try:
            front_matter = yaml.safe_load(parts[1])
            body = parts[2]
            return front_matter, body
        except Exception as e:
            print(f"警告: 解析Front Matter失败: {e}")
            return None, content
    
    @staticmethod
    def extract_links(content: str) -> List[Tuple[str, str, int]]:
        """
        提取Markdown链接
        返回: [(link_text, link_url, line_number), ...]
        """
        links = []
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            line_number = content[:match.start()].count('\n') + 1
            links.append((text, url, line_number))
        
        return links
    
    @staticmethod
    def extract_headings(content: str) -> List[Tuple[int, str, str]]:
        """
        提取标题
        返回: [(level, text, anchor), ...]
        """
        headings = []
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        
        for match in re.finditer(heading_pattern, content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            # 生成锚点（简化版）
            anchor = text.lower().replace(' ', '-')
            headings.append((level, text, anchor))
        
        return headings
