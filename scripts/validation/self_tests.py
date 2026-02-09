#!/usr/bin/env python3
"""
自测问题验证工具

功能：
1. 验证自测问题答案完整性
2. 验证自测问题数量是否充足（至少5个）
3. 支持所有模块类型

使用方法：
    python scripts/validation/self_tests.py [module] [--check-type TYPE]
    
    module: all, software-engineering, technical, regulatory
    --check-type: answers, count, all (默认: all)
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict


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


def count_self_test_questions(file_path: Path) -> int:
    """统计文件中的自测问题数量"""
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
        return 0


def validate_module_answers(base_dir: Path, module_name: str) -> Tuple[List[str], List[str]]:
    """验证模块的自测问题答案完整性"""
    if not base_dir.exists():
        return [], [f"错误: 目录不存在 {base_dir}"]
    
    passed = []
    failed = []
    
    for md_file in base_dir.rglob('*.md'):
        if md_file.name == 'index.md' or 'event' in md_file.parts:
            continue
        
        total_q, total_a, issues = validate_answers_in_file(md_file)
        
        if total_q == 0:
            continue
        
        rel_path = md_file.relative_to(Path('docs/zh'))
        
        if not issues:
            passed.append(f"✓ {rel_path}: {total_q} 个问题, {total_a} 个答案")
        else:
            failed.append(f"✗ {rel_path}: {', '.join(issues)}")
    
    return passed, failed


def validate_module_count(base_dir: Path, module_name: str, min_count: int = 5) -> Tuple[List[str], List[str]]:
    """验证模块的自测问题数量"""
    if not base_dir.exists():
        return [], [f"错误: 目录不存在 {base_dir}"]
    
    passed = []
    failed = []
    
    for md_file in base_dir.rglob('*.md'):
        if md_file.name == 'index.md' or 'event' in md_file.parts:
            continue
        
        count = count_self_test_questions(md_file)
        
        if count == 0:
            continue
        
        rel_path = md_file.relative_to(Path('docs/zh'))
        
        if count >= min_count:
            passed.append(f"✓ {rel_path}: {count} 个问题")
        else:
            failed.append(f"✗ {rel_path}: {count} 个问题 (需要至少{min_count}个)")
    
    return passed, failed


def validate_all_modules(check_type: str = 'all', min_count: int = 5) -> Dict:
    """验证所有模块"""
    modules = {
        'software-engineering': Path('docs/zh/software-engineering'),
        'technical': Path('docs/zh/technical-knowledge'),
        'regulatory': Path('docs/zh/regulatory-standards')
    }
    
    results = {}
    
    for module_name, module_path in modules.items():
        results[module_name] = {
            'answers_passed': [],
            'answers_failed': [],
            'count_passed': [],
            'count_failed': []
        }
        
        if check_type in ['answers', 'all']:
            passed, failed = validate_module_answers(module_path, module_name)
            results[module_name]['answers_passed'] = passed
            results[module_name]['answers_failed'] = failed
        
        if check_type in ['count', 'all']:
            passed, failed = validate_module_count(module_path, module_name, min_count)
            results[module_name]['count_passed'] = passed
            results[module_name]['count_failed'] = failed
    
    return results


def print_results(results: Dict, check_type: str):
    """打印验证结果"""
    print("=" * 80)
    print("自测问题验证报告")
    print("=" * 80)
    print()
    
    module_names = {
        'software-engineering': '软件工程模块',
        'technical': '技术知识模块',
        'regulatory': '法规标准模块'
    }
    
    total_passed = 0
    total_failed = 0
    
    for module_key, module_result in results.items():
        print(f"\n{module_names.get(module_key, module_key)}")
        print("-" * 80)
        
        if check_type in ['answers', 'all']:
            passed = module_result['answers_passed']
            failed = module_result['answers_failed']
            
            if passed or failed:
                print(f"\n答案完整性检查:")
                print(f"  通过: {len(passed)} 个文件")
                print(f"  失败: {len(failed)} 个文件")
                
                if failed:
                    print("\n  失败详情:")
                    for item in sorted(failed):
                        print(f"    {item}")
                
                total_passed += len(passed)
                total_failed += len(failed)
        
        if check_type in ['count', 'all']:
            passed = module_result['count_passed']
            failed = module_result['count_failed']
            
            if passed or failed:
                print(f"\n问题数量检查:")
                print(f"  通过: {len(passed)} 个文件")
                print(f"  失败: {len(failed)} 个文件")
                
                if failed:
                    print("\n  失败详情:")
                    for item in sorted(failed):
                        print(f"    {item}")
                
                total_passed += len(passed)
                total_failed += len(failed)
    
    print()
    print("=" * 80)
    print(f"总计: 通过 {total_passed}, 失败 {total_failed}")
    
    if total_failed == 0:
        print("✓ 所有自测问题验证通过")
    else:
        print(f"✗ {total_failed} 个文件验证失败")
    
    print("=" * 80)
    
    return total_failed == 0


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='验证自测问题完整性')
    parser.add_argument(
        'module',
        nargs='?',
        default='all',
        choices=['all', 'software-engineering', 'technical', 'regulatory'],
        help='要验证的模块类型 (默认: all)'
    )
    parser.add_argument(
        '--check-type',
        default='all',
        choices=['answers', 'count', 'all'],
        help='检查类型: answers(答案完整性), count(问题数量), all(全部) (默认: all)'
    )
    parser.add_argument(
        '--min-count',
        type=int,
        default=5,
        help='最少问题数量 (默认: 5)'
    )
    
    args = parser.parse_args()
    
    # 验证指定模块
    if args.module == 'all':
        results = validate_all_modules(args.check_type, args.min_count)
    else:
        module_path = Path(f'docs/zh/{args.module}')
        results = {args.module: {
            'answers_passed': [],
            'answers_failed': [],
            'count_passed': [],
            'count_failed': []
        }}
        
        if args.check_type in ['answers', 'all']:
            passed, failed = validate_module_answers(module_path, args.module)
            results[args.module]['answers_passed'] = passed
            results[args.module]['answers_failed'] = failed
        
        if args.check_type in ['count', 'all']:
            passed, failed = validate_module_count(module_path, args.module, args.min_count)
            results[args.module]['count_passed'] = passed
            results[args.module]['count_failed'] = failed
    
    # 打印结果
    success = print_results(results, args.check_type)
    
    return 0 if success else 1
    
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


if __name__ == '__main__':
    sys.exit(main())
