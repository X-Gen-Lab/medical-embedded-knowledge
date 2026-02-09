#!/usr/bin/env python3
"""
验证软件工程模块的参考文献

检查：
- 每个模块是否有参考文献部分
- 每个模块至少有3个参考条目
"""

import re
from pathlib import Path

def count_references(content):
    """统计参考文献数量"""
    # 查找参考文献部分
    ref_match = re.search(r'## 参考文献\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not ref_match:
        return 0
    
    ref_section = ref_match.group(1)
    # 统计编号列表项
    ref_items = re.findall(r'^\d+\.\s+', ref_section, re.MULTILINE)
    return len(ref_items)


def has_reference_section(content):
    """检查是否有参考文献部分"""
    return '## 参考文献' in content or '## 参考资料' in content


def verify_module(file_path):
    """验证单个模块"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    has_refs = has_reference_section(content)
    ref_count = count_references(content)
    
    return {
        'file': file_path.name,
        'has_section': has_refs,
        'count': ref_count,
        'valid': has_refs and ref_count >= 3
    }


def main():
    """主函数"""
    docs_dir = Path('docs/zh/software-engineering')
    
    if not docs_dir.exists():
        print(f"错误：目录不存在 {docs_dir}")
        return
    
    print("验证软件工程模块参考文献...\n")
    print("=" * 80)
    
    all_results = []
    categories = [
        'requirements-engineering',
        'architecture-design',
        'coding-standards',
        'testing-strategy',
        'configuration-management',
        'static-analysis'
    ]
    
    for category in categories:
        category_dir = docs_dir / category
        if not category_dir.exists():
            continue
        
        print(f"\n📁 {category}")
        print("-" * 80)
        
        # 获取所有.md文件
        md_files = sorted(category_dir.glob('*.md'))
        
        for md_file in md_files:
            result = verify_module(md_file)
            all_results.append(result)
            
            status = "✅" if result['valid'] else "❌"
            ref_info = f"({result['count']} 个参考文献)" if result['has_section'] else "(无参考文献部分)"
            
            print(f"  {status} {result['file']:<40} {ref_info}")
    
    # 统计
    print("\n" + "=" * 80)
    print("统计结果：")
    print("-" * 80)
    
    total = len(all_results)
    valid = sum(1 for r in all_results if r['valid'])
    has_section = sum(1 for r in all_results if r['has_section'])
    missing_section = total - has_section
    insufficient = sum(1 for r in all_results if r['has_section'] and r['count'] < 3)
    
    print(f"总文件数：{total}")
    print(f"符合要求（≥3个参考文献）：{valid}")
    print(f"有参考文献部分：{has_section}")
    print(f"缺少参考文献部分：{missing_section}")
    print(f"参考文献不足3个：{insufficient}")
    
    if valid == total:
        print("\n✅ 所有软件工程模块都有足够的参考文献！")
    else:
        print(f"\n⚠️  还有 {total - valid} 个模块需要补充参考文献")
        
        # 列出需要补充的文件
        print("\n需要补充的文件：")
        for result in all_results:
            if not result['valid']:
                print(f"  - {result['file']}")
    
    print("=" * 80)


if __name__ == '__main__':
    main()
