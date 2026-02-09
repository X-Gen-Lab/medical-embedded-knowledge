#!/usr/bin/env python3
"""
验证软件工程模块自测问题完整性

检查所有software-engineering下的主要模块是否包含至少5个自测问题。
"""

import re
from pathlib import Path
from typing import List, Tuple


def count_self_test_questions(file_path: Path) -> int:
    """
    统计文件中的自测问题数量
    
    支持两种格式:
    1. ??? question "问题标题"
    2. ### 问题N：问题标题
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配 ??? question 格式
        pattern1 = r'\?\?\? question'
        matches1 = re.findall(pattern1, content)
        
        # 匹配 ### 问题N： 格式
        pattern2 = r'### 问题\d+：'
        matches2 = re.findall(pattern2, content)
        
        return len(matches1) + len(matches2)
    except Exception as e:
        print(f"错误: 无法读取文件 {file_path}: {e}")
        return 0


def validate_software_engineering_modules() -> Tuple[List[str], List[str]]:
    """
    验证所有软件工程模块的自测问题
    
    Returns:
        (passed_modules, failed_modules): 通过和失败的模块列表
    """
    base_dir = Path('docs/zh/software-engineering')
    
    if not base_dir.exists():
        print(f"错误: 目录不存在 {base_dir}")
        return [], []
    
    passed = []
    failed = []
    
    # 扫描所有主要模块文件（排除index.md和event子目录）
    for md_file in base_dir.rglob('*.md'):
        # 跳过index文件
        if md_file.name == 'index.md':
            continue
        
        # 跳过event子目录（待补充内容）
        if 'event' in md_file.parts:
            continue
        
        # 统计自测问题数量
        count = count_self_test_questions(md_file)
        
        # 获取相对路径
        rel_path = md_file.relative_to(Path('docs/zh'))
        
        if count >= 5:
            passed.append(f"✓ {rel_path}: {count} 个问题")
        else:
            failed.append(f"✗ {rel_path}: {count} 个问题 (需要至少5个)")
    
    return passed, failed


def main():
    """主函数"""
    print("=" * 80)
    print("软件工程模块自测问题验证")
    print("=" * 80)
    print()
    
    passed, failed = validate_software_engineering_modules()
    
    print(f"通过的模块 ({len(passed)}):")
    print("-" * 80)
    for module in sorted(passed):
        print(module)
    
    if failed:
        print()
        print(f"需要补充的模块 ({len(failed)}):")
        print("-" * 80)
        for module in sorted(failed):
            print(module)
        print()
        print("❌ 验证失败: 部分模块自测问题不足5个")
        return 1
    else:
        print()
        print("=" * 80)
        print("✅ 验证通过: 所有软件工程模块都包含至少5个自测问题")
        print("=" * 80)
        return 0


if __name__ == '__main__':
    exit(main())
