#!/usr/bin/env python3
"""
链接修复工具

功能：
1. 修复拼写错误的链接
2. 修复缺少语言前缀的绝对路径

使用方法：
    python scripts/fix/links.py spelling    # 修复拼写错误
    python scripts/fix/links.py prefix      # 修复路径前缀
    python scripts/fix/links.py all         # 全部修复
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


# 链接拼写错误修复映射表
SPELLING_FIXES = [
    ('software-classificationn', 'software-classification'),
    ('bit-manipulationn', 'bit-manipulation'),
    ('synchronizationn', 'synchronization'),
    ('power-optimizationn', 'power-optimization'),
    ('risk-evaluationn', 'risk-evaluation'),
    ('tool-usagee', 'tool-usage'),
    ('layered-architecturee', 'layered-architecture'),
    ('](&monitor, data', '](monitor-data'),
]


class LinkFixer:
    """链接修复器"""
    
    def __init__(self, docs_dir: str = 'docs'):
        self.docs_dir = Path(docs_dir)
        self.results = {
            'spelling': {'files': 0, 'fixes': 0, 'details': {}},
            'prefix': {'files': 0, 'fixes': 0, 'details': {}}
        }
    
    def fix_spelling_in_content(self, content: str) -> Tuple[str, List[str]]:
        """修复内容中的拼写错误"""
        fixes_applied = []
        
        for old_pattern, new_pattern in SPELLING_FIXES:
            if old_pattern in content:
                count = content.count(old_pattern)
                content = content.replace(old_pattern, new_pattern)
                fixes_applied.append(f"{old_pattern} → {new_pattern} ({count}次)")
        
        return content, fixes_applied
    
    def fix_prefix_in_content(self, content: str) -> Tuple[str, int]:
        """修复内容中的路径前缀"""
        fixes = 0
        
        # 匹配绝对路径但排除已有语言前缀的
        pattern = r'\]\((/(?!zh/|en/|http|https|#)[^)]+)\)'
        
        def replace_func(match):
            nonlocal fixes
            original_path = match.group(1)
            new_path = f'/zh{original_path}'
            fixes += 1
            return f']({new_path})'
        
        new_content = re.sub(pattern, replace_func, content)
        return new_content, fixes
    
    def fix_file(self, file_path: Path, fix_type: str) -> bool:
        """修复单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            modified = False
            
            # 修复拼写错误
            if fix_type in ['spelling', 'all']:
                content, spelling_fixes = self.fix_spelling_in_content(content)
                if spelling_fixes:
                    self.results['spelling']['details'][str(file_path)] = spelling_fixes
                    self.results['spelling']['fixes'] += len(spelling_fixes)
                    modified = True
            
            # 修复路径前缀
            if fix_type in ['prefix', 'all']:
                content, prefix_count = self.fix_prefix_in_content(content)
                if prefix_count > 0:
                    self.results['prefix']['details'][str(file_path)] = prefix_count
                    self.results['prefix']['fixes'] += prefix_count
                    modified = True
            
            # 写回文件
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            
            return False
        
        except Exception as e:
            print(f"错误: 处理文件 {file_path} 失败: {e}")
            return False
    
    def fix_all(self, fix_type: str = 'all'):
        """修复所有Markdown文件"""
        print("=" * 80)
        print("链接修复工具")
        print("=" * 80)
        
        fix_type_names = {
            'spelling': '拼写错误',
            'prefix': '路径前缀',
            'all': '所有问题'
        }
        
        print(f"\n修复类型: {fix_type_names.get(fix_type, fix_type)}")
        print("开始扫描和修复...\n")
        
        # 查找所有Markdown文件
        md_files = list(self.docs_dir.rglob('*.md'))
        print(f"找到 {len(md_files)} 个Markdown文件\n")
        
        for md_file in md_files:
            if self.fix_file(md_file, fix_type):
                if fix_type in ['spelling', 'all']:
                    self.results['spelling']['files'] += 1
                if fix_type in ['prefix', 'all']:
                    self.results['prefix']['files'] += 1
        
        self.print_results(fix_type)
    
    def print_results(self, fix_type: str):
        """打印修复结果"""
        print("\n" + "=" * 80)
        print("修复完成")
        print("=" * 80)
        print()
        
        if fix_type in ['spelling', 'all']:
            spelling = self.results['spelling']
            print(f"拼写错误修复:")
            print(f"  修改文件: {spelling['files']} 个")
            print(f"  修复数量: {spelling['fixes']} 处")
            
            if spelling['details']:
                print("\n  详细信息:")
                for file_path, fixes in sorted(spelling['details'].items()):
                    print(f"    ✓ {file_path}")
                    for fix in fixes:
                        print(f"      - {fix}")
        
        if fix_type in ['prefix', 'all']:
            prefix = self.results['prefix']
            print(f"\n路径前缀修复:")
            print(f"  修改文件: {prefix['files']} 个")
            print(f"  修复数量: {prefix['fixes']} 处")
            
            if prefix['details']:
                print("\n  详细信息:")
                for file_path, count in sorted(prefix['details'].items()):
                    print(f"    ✓ {file_path}: {count} 处")
        
        print("\n" + "=" * 80)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='链接修复工具')
    parser.add_argument(
        'fix_type',
        nargs='?',
        default='all',
        choices=['spelling', 'prefix', 'all'],
        help='修复类型: spelling(拼写错误), prefix(路径前缀), all(全部) (默认: all)'
    )
    parser.add_argument(
        '--docs-dir',
        default='docs',
        help='文档目录 (默认: docs)'
    )
    
    args = parser.parse_args()
    
    fixer = LinkFixer(args.docs_dir)
    fixer.fix_all(args.fix_type)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
