#!/usr/bin/env python3
"""
内部链接验证脚本
验证所有Markdown文档中的内部链接有效性

需求: 12.1
"""

import re
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class LinkType(Enum):
    """链接类型"""
    INLINE = "inline"
    RELATED_MODULE = "related_module"
    LEARNING_PATH = "learning_path"


@dataclass
class BrokenLink:
    """失效链接记录"""
    source_file: str
    link_text: str
    link_url: str
    link_type: LinkType
    line_number: int = 0
    resolved_path: str = ""


class InternalLinkValidator:
    """内部链接验证器"""
    
    def __init__(self, docs_dir: str = 'docs'):
        self.docs_dir = Path(docs_dir)
        self.broken_links: List[BrokenLink] = []
    
    def extract_inline_links(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """
        从Markdown文件中提取内联链接
        返回: [(link_text, link_url, line_number), ...]
        """
        links = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 匹配Markdown链接格式: [text](url)
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            
            for match in re.finditer(link_pattern, content):
                text = match.group(1)
                url = match.group(2)
                line_number = content[:match.start()].count('\n') + 1
                
                # 只处理内部链接（不以http开头）
                if not url.startswith('http'):
                    # 移除锚点
                    url_without_anchor = url.split('#')[0]
                    if url_without_anchor:  # 忽略纯锚点链接
                        links.append((text, url_without_anchor, line_number))
        
        except Exception as e:
            print(f"警告: 读取文件 {file_path} 失败: {e}")
        
        return links
    
    def extract_front_matter_links(self, file_path: Path) -> List[str]:
        """
        从Front Matter中提取related_modules链接
        返回: [module_path, ...]
        """
        links = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有Front Matter
            if not content.startswith('---'):
                return links
            
            # 分割Front Matter
            parts = content.split('---', 2)
            if len(parts) < 3:
                return links
            
            # 解析YAML
            front_matter = yaml.safe_load(parts[1])
            if front_matter and 'related_modules' in front_matter:
                related_modules = front_matter['related_modules']
                if isinstance(related_modules, list):
                    links.extend(related_modules)
        
        except Exception as e:
            print(f"警告: 解析Front Matter失败 {file_path}: {e}")
        
        return links
    
    def resolve_link_path(self, source_file: Path, link_url: str) -> Path:
        """
        解析链接的绝对路径
        """
        # 如果链接以/开头，从docs根目录开始
        if link_url.startswith('/'):
            return self.docs_dir / link_url.lstrip('/')
        else:
            # 相对于当前文件的路径
            return (source_file.parent / link_url).resolve()
    
    def check_link_exists(self, target_path: Path) -> bool:
        """
        检查链接目标是否存在
        尝试多种可能的路径
        """
        possible_paths = [
            target_path,
            target_path.with_suffix('.md'),
            target_path / 'index.md'
        ]
        
        return any(p.exists() for p in possible_paths)
    
    def validate_inline_links(self, file_path: Path):
        """验证文件中的内联链接"""
        links = self.extract_inline_links(file_path)
        
        for link_text, link_url, line_number in links:
            # 解析链接路径
            target_path = self.resolve_link_path(file_path, link_url)
            
            # 检查目标文件是否存在
            if not self.check_link_exists(target_path):
                self.broken_links.append(BrokenLink(
                    source_file=str(file_path),
                    link_text=link_text,
                    link_url=link_url,
                    link_type=LinkType.INLINE,
                    line_number=line_number,
                    resolved_path=str(target_path)
                ))
    
    def validate_related_modules(self, file_path: Path):
        """验证Front Matter中的related_modules链接"""
        related_modules = self.extract_front_matter_links(file_path)
        
        for module_path in related_modules:
            # 构建目标路径
            target_path = self.docs_dir / f"{module_path}.md"
            
            # 也检查index.md
            if not target_path.exists():
                target_path = self.docs_dir / module_path / 'index.md'
            
            if not target_path.exists():
                self.broken_links.append(BrokenLink(
                    source_file=str(file_path),
                    link_text=module_path,
                    link_url=module_path,
                    link_type=LinkType.RELATED_MODULE,
                    resolved_path=str(target_path)
                ))
    
    def validate_learning_path_links(self, yaml_file: Path):
        """验证学习路径YAML文件中的链接"""
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data or 'modules' not in data:
                return
            
            for module in data['modules']:
                if 'id' in module:
                    module_id = module['id']
                    
                    # 构建目标路径
                    target_path = self.docs_dir / f"{module_id}.md"
                    
                    # 也检查index.md
                    if not target_path.exists():
                        target_path = self.docs_dir / module_id / 'index.md'
                    
                    if not target_path.exists():
                        self.broken_links.append(BrokenLink(
                            source_file=str(yaml_file),
                            link_text=module.get('title', module_id),
                            link_url=module_id,
                            link_type=LinkType.LEARNING_PATH,
                            resolved_path=str(target_path)
                        ))
        
        except Exception as e:
            print(f"警告: 解析学习路径文件失败 {yaml_file}: {e}")
    
    def validate_all(self):
        """验证所有链接"""
        print("开始验证内部链接...\n")
        
        # 验证Markdown文件中的链接
        md_files = list(self.docs_dir.rglob('*.md'))
        print(f"找到 {len(md_files)} 个Markdown文件")
        
        for md_file in md_files:
            self.validate_inline_links(md_file)
            self.validate_related_modules(md_file)
        
        # 验证学习路径文件中的链接
        yaml_files = list(self.docs_dir.rglob('learning-paths/**/*.yaml'))
        print(f"找到 {len(yaml_files)} 个学习路径配置文件")
        
        for yaml_file in yaml_files:
            self.validate_learning_path_links(yaml_file)
        
        print(f"\n验证完成！")
    
    def generate_report(self) -> str:
        """生成验证报告"""
        report = []
        report.append("=" * 80)
        report.append("内部链接验证报告")
        report.append("=" * 80)
        report.append(f"\n发现的失效链接数: {len(self.broken_links)}")
        report.append("")
        
        if self.broken_links:
            # 按链接类型分组
            by_type = {}
            for link in self.broken_links:
                link_type = link.link_type.value
                if link_type not in by_type:
                    by_type[link_type] = []
                by_type[link_type].append(link)
            
            # 输出每种类型的失效链接
            for link_type, links in by_type.items():
                report.append(f"\n{link_type.upper()} 链接 ({len(links)} 个):")
                report.append("-" * 80)
                
                for link in links:
                    report.append(f"\n源文件: {link.source_file}")
                    if link.line_number:
                        report.append(f"  行号: {link.line_number}")
                    report.append(f"  链接文本: {link.link_text}")
                    report.append(f"  链接URL: {link.link_url}")
                    report.append(f"  解析路径: {link.resolved_path}")
            
            report.append("")
            report.append("=" * 80)
            report.append("验证失败！请修复上述失效链接。")
            report.append("=" * 80)
        else:
            report.append("=" * 80)
            report.append("✓ 所有内部链接有效！")
            report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """主函数"""
    validator = InternalLinkValidator()
    validator.validate_all()
    
    # 生成并打印报告
    report = validator.generate_report()
    print(report)
    
    # 如果有失效链接，返回非零退出码
    if validator.broken_links:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
