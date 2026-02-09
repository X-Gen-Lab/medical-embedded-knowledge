#!/usr/bin/env python3
"""验证核心技术模块的参考文献"""

import re
from pathlib import Path

def count_references(content):
    """统计参考文献数量"""
    ref_match = re.search(r'## 参考文献\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not ref_match:
        return 0
    
    ref_section = ref_match.group(1)
    ref_items = re.findall(r'^\d+\.\s+', ref_section, re.MULTILINE)
    return len(ref_items)


def main():
    docs_dir = Path('docs/zh/technical-knowledge')
    
    # 获取所有非index的md文件
    files = [f for f in docs_dir.rglob('*.md') if f.name != 'index.md']
    
    print(f"核心技术模块参考文献验证报告")
    print("=" * 80)
    print(f"总文件数: {len(files)}\n")
    
    results = []
    for file_path in sorted(files):
        content = file_path.read_text(encoding='utf-8')
        ref_count = count_references(content)
        relative_path = file_path.relative_to(docs_dir)
        results.append((relative_path, ref_count))
    
    # 按类别分组显示
    categories = {}
    for path, count in results:
        category = path.parts[0]
        if category not in categories:
            categories[category] = []
        categories[category].append((path.name, count))
    
    for category, items in sorted(categories.items()):
        print(f"\n{category}/")
        print("-" * 80)
        for name, count in sorted(items):
            status = "✓" if count >= 3 else "✗"
            print(f"  {status} {name:40} {count} 个参考文献")
    
    # 统计
    total = len(results)
    with_refs = sum(1 for _, count in results if count >= 3)
    without_refs = total - with_refs
    
    print("\n" + "=" * 80)
    print(f"统计:")
    print(f"  ✓ 符合要求 (>=3个参考文献): {with_refs}/{total}")
    print(f"  ✗ 不符合要求 (<3个参考文献): {without_refs}/{total}")
    
    if without_refs == 0:
        print(f"\n✓ 所有核心技术模块都有至少3个参考文献！")
        return 0
    else:
        print(f"\n✗ 还有 {without_refs} 个模块需要补充参考文献")
        return 1


if __name__ == '__main__':
    exit(main())
