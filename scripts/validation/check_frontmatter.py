#!/usr/bin/env python3
"""
检查markdown文件的Front Matter元数据完整性
"""

import os
import re
from pathlib import Path

# 必需的字段
REQUIRED_FIELDS = ['title', 'description', 'difficulty', 'estimated_time', 'tags']
# 推荐的字段
RECOMMENDED_FIELDS = ['related_modules', 'last_updated', 'version', 'language']

def check_frontmatter(file_path):
    """检查文件的frontmatter"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有frontmatter
        if not content.startswith('---'):
            return {
                'has_frontmatter': False,
                'missing_required': REQUIRED_FIELDS,
                'missing_recommended': RECOMMENDED_FIELDS
            }
        
        # 提取frontmatter
        match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not match:
            return {
                'has_frontmatter': False,
                'missing_required': REQUIRED_FIELDS,
                'missing_recommended': RECOMMENDED_FIELDS
            }
        
        frontmatter = match.group(1)
        
        # 检查必需字段
        missing_required = []
        for field in REQUIRED_FIELDS:
            if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
                missing_required.append(field)
        
        # 检查推荐字段
        missing_recommended = []
        for field in RECOMMENDED_FIELDS:
            if not re.search(rf'^{field}:', frontmatter, re.MULTILINE):
                missing_recommended.append(field)
        
        return {
            'has_frontmatter': True,
            'missing_required': missing_required,
            'missing_recommended': missing_recommended
        }
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def main():
    """检查所有markdown文件"""
    docs_dir = Path('docs')
    
    files_without_frontmatter = []
    files_missing_required = []
    files_missing_recommended = []
    
    total_files = 0
    
    # 遍历所有markdown文件
    for md_file in docs_dir.rglob('*.md'):
        # 跳过README和模板文件
        if md_file.name in ['README.md', 'module-template.md']:
            continue
        
        total_files += 1
        result = check_frontmatter(md_file)
        if result is None:
            continue
        
        if not result['has_frontmatter']:
            files_without_frontmatter.append(md_file)
        elif result['missing_required']:
            files_missing_required.append((md_file, result['missing_required']))
        elif result['missing_recommended']:
            files_missing_recommended.append((md_file, result['missing_recommended']))
    
    # 输出结果
    print("=" * 80)
    print("Front Matter 检查报告")
    print("=" * 80)
    
    if files_without_frontmatter:
        print(f"\n❌ 没有Front Matter的文件 ({len(files_without_frontmatter)}):")
        for f in files_without_frontmatter:
            print(f"  - {f}")
    
    if files_missing_required:
        print(f"\n⚠️  缺少必需字段的文件 ({len(files_missing_required)}):")
        for f, missing in files_missing_required:
            print(f"  - {f}")
            print(f"    缺少: {', '.join(missing)}")
    
    if files_missing_recommended:
        print(f"\n💡 缺少推荐字段的文件 ({len(files_missing_recommended)}):")
        for f, missing in files_missing_recommended:
            print(f"  - {f}")
            print(f"    缺少: {', '.join(missing)}")
    
    if not files_without_frontmatter and not files_missing_required:
        print("\n✅ 所有文件都有完整的必需Front Matter字段！")
    
    print(f"\n总计检查文件数: {total_files}")
    print("=" * 80)

if __name__ == '__main__':
    main()
