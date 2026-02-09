#!/usr/bin/env python3
"""
验证自测问题答案完整性

检查所有自测问题是否都有对应的答案解析。
"""

import re
from pathlib import Path
from typing import List, Tuple


def validate_answers_in_file(file_path: Path) -> Tuple[int, int, List[str]]:
    """
    验证文件中的自测问题答案完整性
    
    Returns:
        (total_questions, questions_with_answers, issues): 
        总问题数、有答案的问题数、问题列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return 0, 0, [f"无法读取文件: {e}"]
    
    issues = []
    
    # 检查 ??? question 格式
    question_pattern = r'\?\?\? question "([^"]+)"'
    answer_pattern = r'\?\?\? success "答案"'
    
    questions = re.findall(question_pattern, content)
    answers = re.findall(answer_pattern, content)
    
    # 检查 ### 问题N： 格式
    question_pattern2 = r'### 问题\d+：([^\n]+)'
    answer_pattern2 = r'<summary>点击查看答案</summary>'
    
    questions2 = re.findall(question_pattern2, content)
    answers2 = re.findall(answer_pattern2, content)
    
    total_questions = len(questions) + len(questions2)
    total_answers = len(answers) + len(answers2)
    
    # 简单检查：答案数量应该等于问题数量
    if total_questions > 0 and total_answers < total_questions:
        issues.append(f"问题数量({total_questions}) > 答案数量({total_answers})")
    
    return total_questions, total_answers, issues


def validate_software_engineering_answers() -> Tuple[List[str], List[str]]:
    """
    验证所有软件工程模块的自测问题答案
    
    Returns:
        (passed_modules, failed_modules): 通过和失败的模块列表
    """
    base_dir = Path('docs/zh/software-engineering')
    
    if not base_dir.exists():
        print(f"错误: 目录不存在 {base_dir}")
        return [], []
    
    passed = []
    failed = []
    
    for md_file in base_dir.rglob('*.md'):
        if md_file.name == 'index.md' or 'event' in md_file.parts:
            continue
        
        total_q, total_a, issues = validate_answers_in_file(md_file)
        
        if total_q == 0:
            continue  # 跳过没有问题的文件
        
        rel_path = md_file.relative_to(Path('docs/zh'))
        
        if not issues:
            passed.append(f"✓ {rel_path}: {total_q} 个问题, {total_a} 个答案")
        else:
            failed.append(f"✗ {rel_path}: {', '.join(issues)}")
    
    return passed, failed


def main():
    """主函数"""
    print("=" * 80)
    print("软件工程模块自测问题答案验证")
    print("=" * 80)
    print()
    
    passed, failed = validate_software_engineering_answers()
    
    print(f"通过的模块 ({len(passed)}):")
    print("-" * 80)
    for module in sorted(passed):
        print(module)
    
    if failed:
        print()
        print(f"需要补充答案的模块 ({len(failed)}):")
        print("-" * 80)
        for module in sorted(failed):
            print(module)
        print()
        print("❌ 验证失败: 部分模块的自测问题缺少答案")
        return 1
    else:
        print()
        print("=" * 80)
        print("✅ 验证通过: 所有自测问题都有对应的答案解析")
        print("=" * 80)
        return 0


if __name__ == '__main__':
    exit(main())
