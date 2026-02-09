#!/usr/bin/env python3
"""
检查点验证脚本
运行所有内容完整性验证检查
"""

import sys
import subprocess
from pathlib import Path


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def run_command(command: list, description: str) -> bool:
    """
    运行命令并返回是否成功
    """
    print(f"运行: {description}")
    print(f"命令: {' '.join(command)}\n")
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        
        # 打印输出
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # 检查返回码
        if result.returncode == 0:
            print(f"✓ {description} - 通过\n")
            return True
        else:
            print(f"✗ {description} - 失败\n")
            return False
    
    except Exception as e:
        print(f"✗ {description} - 错误: {str(e)}\n")
        return False


def main():
    """主函数"""
    print_section("检查点 8: 内容完整性验证")
    
    all_passed = True
    results = []
    
    # 1. 元数据验证
    print_section("1. 元数据验证")
    metadata_passed = run_command(
        ['python', 'scripts/validate_markdown.py'],
        "元数据验证"
    )
    results.append(("元数据验证", metadata_passed))
    all_passed = all_passed and metadata_passed
    
    # 2. 链接验证
    print_section("2. 链接验证")
    link_passed = run_command(
        ['pytest', 'tests/test_link_validation.py', '-v'],
        "内部链接验证"
    )
    results.append(("链接验证", link_passed))
    all_passed = all_passed and link_passed
    
    # 3. 内容质量属性测试
    print_section("3. 内容质量属性测试")
    properties_passed = run_command(
        ['pytest', 'tests/test_content_properties.py', '-v'],
        "内容质量属性测试"
    )
    results.append(("内容质量属性测试", properties_passed))
    all_passed = all_passed and properties_passed
    
    # 生成总结报告
    print_section("验证总结")
    
    print("验证结果:")
    print("-" * 80)
    for test_name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"{test_name:30s} {status}")
    print("-" * 80)
    
    if all_passed:
        print("\n" + "=" * 80)
        print(" ✓ 所有验证通过！内容完整性检查点达成。")
        print("=" * 80)
        return 0
    else:
        print("\n" + "=" * 80)
        print(" ✗ 部分验证失败。请修复上述问题后重新运行验证。")
        print("=" * 80)
        return 1


if __name__ == '__main__':
    sys.exit(main())
