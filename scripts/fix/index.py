#!/usr/bin/env python3
"""
Index文件链接管理工具

功能：
1. 检查index文件中缺失的链接引用
2. 自动添加缺失的链接
3. 修复无效的链接

使用方法：
    python scripts/fix/index.py check    # 检查缺失的链接
    python scripts/fix/index.py add      # 添加缺失的链接
    python scripts/fix/index.py fix      # 修复无效的链接
"""

import re
import sys
from pathlib import Path
from typing import Set, Dict, List, Tuple


class IndexManager:
    """Index文件管理器"""
    
    def __init__(self, docs_dir: str = 'docs/zh'):
        self.docs_dir = Path(docs_dir)
        self.results = []
    
    def extract_links_from_index(self, index_file: Path) -> Set[str]:
        """从index文件中提取所有链接"""
        links = set()
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            link_pattern = r'\]\(([^)]+)\)'
            for match in re.finditer(link_pattern, content):
                link_url = match.group(1)
                if not link_url.startswith(('http', '#', '/')):
                    links.add(link_url.rstrip('/'))
        
        except Exception as e:
            print(f"警告: 读取文件 {index_file} 失败: {e}")
        
        return links
    
    def get_file_title(self, file_path: Path) -> str:
        """从文件中提取标题"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试从Front Matter中提取title
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    front_matter = parts[1]
                    title_match = re.search(r'title:\s*["\']?([^"\'\n]+)["\']?', front_matter)
                    if title_match:
                        return title_match.group(1).strip()
            
            # 尝试从第一个标题提取
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if title_match:
                return title_match.group(1).strip()
            
            # 使用文件名
            return file_path.stem.replace('-', ' ').title()
        
        except Exception as e:
            return file_path.stem.replace('-', ' ').title()
    
    def check_directory(self, directory: Path) -> Dict:
        """检查目录中的文件和index引用"""
        index_file = directory / 'index.md'
        
        if not index_file.exists():
            return None
        
        # 获取index中引用的链接
        referenced_links = self.extract_links_from_index(index_file)
        
        # 获取目录中实际存在的文件
        actual_files = set()
        for md_file in directory.glob('*.md'):
            if md_file.name != 'index.md':
                actual_files.add(md_file.stem)
        
        # 查找缺失的引用
        missing_refs = []
        for file_stem in actual_files:
            # 检查是否被引用（可能是.md或不带扩展名）
            if file_stem not in referenced_links and f"{file_stem}.md" not in referenced_links:
                missing_refs.append(file_stem)
        
        if missing_refs:
            return {
                'directory': directory,
                'index_file': index_file,
                'missing': missing_refs
            }
        
        return None
    
    def check_all(self) -> List[Dict]:
        """检查所有目录"""
        print("检查index文件中缺失的链接引用...\n")
        
        missing_list = []
        
        for index_file in self.docs_dir.rglob('index.md'):
            directory = index_file.parent
            result = self.check_directory(directory)
            
            if result:
                missing_list.append(result)
        
        return missing_list
    
    def add_missing_links(self, directory: Path, missing_files: List[str]) -> bool:
        """添加缺失的链接到index文件"""
        index_file = directory / 'index.md'
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 查找合适的插入位置（在第一个##标题之后）
            insert_pos = content.find('\n## ')
            if insert_pos == -1:
                # 如果没有##标题，在文件末尾添加
                insert_pos = len(content)
            else:
                # 在##标题之前添加
                insert_pos = content.rfind('\n', 0, insert_pos)
            
            # 生成链接列表
            new_links = []
            for file_stem in sorted(missing_files):
                file_path = directory / f"{file_stem}.md"
                title = self.get_file_title(file_path)
                new_links.append(f"- [{title}]({file_stem}.md)")
            
            # 插入新链接
            if insert_pos == len(content):
                new_content = content + "\n\n" + "\n".join(new_links) + "\n"
            else:
                new_content = (
                    content[:insert_pos] + 
                    "\n\n" + "\n".join(new_links) + "\n" +
                    content[insert_pos:]
                )
            
            # 写回文件
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
        
        except Exception as e:
            print(f"错误: 处理文件 {index_file} 失败: {e}")
            return False
    
    def add_all_missing(self, missing_list: List[Dict]) -> int:
        """添加所有缺失的链接"""
        added_count = 0
        
        for item in missing_list:
            directory = item['directory']
            missing_files = item['missing']
            
            if self.add_missing_links(directory, missing_files):
                print(f"✓ 已添加 {len(missing_files)} 个链接到 {directory}/index.md")
                added_count += len(missing_files)
            else:
                print(f"✗ 添加失败: {directory}/index.md")
        
        return added_count
    
    def fix_broken_links(self, index_file: Path) -> int:
        """修复index文件中的无效链接"""
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            parent_dir = index_file.parent
            fixed_count = 0
            
            # 查找所有Markdown链接
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            
            def replace_link(match):
                nonlocal fixed_count
                link_text = match.group(1)
                link_url = match.group(2)
                
                # 跳过外部链接和锚点
                if link_url.startswith(('http', '#', '/')):
                    return match.group(0)
                
                # 解析链接路径
                target_path = (parent_dir / link_url).resolve()
                
                # 检查目标是否存在
                if target_path.exists():
                    return match.group(0)
                
                # 尝试不同的可能路径
                possible_paths = [
                    target_path.with_suffix('.md'),
                    target_path / 'index.md',
                    parent_dir / f"{link_url.rstrip('/')}.md"
                ]
                
                for possible_path in possible_paths:
                    if possible_path.exists():
                        # 计算相对路径
                        try:
                            rel_path = possible_path.relative_to(parent_dir)
                            fixed_count += 1
                            return f"[{link_text}]({rel_path})"
                        except ValueError:
                            pass
                
                # 无法修复，保持原样
                return match.group(0)
            
            content = re.sub(link_pattern, replace_link, content)
            
            # 如果有修改，写回文件
            if content != original_content:
                with open(index_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                return fixed_count
            
            return 0
        
        except Exception as e:
            print(f"错误: 处理文件 {index_file} 失败: {e}")
            return 0
    
    def fix_all_broken(self) -> int:
        """修复所有index文件中的无效链接"""
        print("修复index文件中的无效链接...\n")
        
        total_fixed = 0
        
        for index_file in self.docs_dir.rglob('index.md'):
            fixed_count = self.fix_broken_links(index_file)
            if fixed_count > 0:
                print(f"✓ 修复了 {fixed_count} 个链接: {index_file}")
                total_fixed += fixed_count
        
        return total_fixed


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Index文件链接管理工具')
    parser.add_argument(
        'action',
        choices=['check', 'add', 'fix'],
        help='操作类型: check(检查), add(添加), fix(修复)'
    )
    parser.add_argument(
        '--docs-dir',
        default='docs/zh',
        help='文档目录 (默认: docs/zh)'
    )
    
    args = parser.parse_args()
    
    manager = IndexManager(args.docs_dir)
    
    if args.action == 'check':
        # 检查缺失的链接
        missing_list = manager.check_all()
        
        if missing_list:
            print("=" * 80)
            print(f"发现 {len(missing_list)} 个index文件缺少链接引用")
            print("=" * 80)
            print()
            
            for item in missing_list:
                directory = item['directory']
                missing = item['missing']
                print(f"\n{directory}/index.md")
                print(f"  缺少 {len(missing)} 个文件的引用:")
                for file_stem in sorted(missing):
                    print(f"    - {file_stem}.md")
            
            print()
            print("=" * 80)
            print("提示: 运行 'python scripts/fix/index.py add' 自动添加这些链接")
            print("=" * 80)
            return 1
        else:
            print("✓ 所有index文件都包含了完整的链接引用")
            return 0
    
    elif args.action == 'add':
        # 添加缺失的链接
        missing_list = manager.check_all()
        
        if not missing_list:
            print("✓ 没有需要添加的链接")
            return 0
        
        print("=" * 80)
        print(f"准备为 {len(missing_list)} 个index文件添加链接")
        print("=" * 80)
        print()
        
        added_count = manager.add_all_missing(missing_list)
        
        print()
        print("=" * 80)
        print(f"完成！共添加了 {added_count} 个链接")
        print("=" * 80)
        return 0
    
    elif args.action == 'fix':
        # 修复无效的链接
        fixed_count = manager.fix_all_broken()
        
        print()
        print("=" * 80)
        if fixed_count > 0:
            print(f"完成！共修复了 {fixed_count} 个链接")
        else:
            print("✓ 没有需要修复的链接")
        print("=" * 80)
        return 0


if __name__ == '__main__':
    sys.exit(main())
