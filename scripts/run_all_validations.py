#!/usr/bin/env python3
"""
综合验证脚本
运行所有验证检查并生成综合报告

需求: 12.1, 12.2, 12.3, 12.6, 12.7
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Tuple


class ValidationRunner:
    """验证运行器"""
    
    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
    
    def run_script(self, script_name: str, description: str) -> Tuple[bool, str]:
        """
        运行验证脚本
        返回: (是否成功, 输出内容)
        """
        print(f"\n{'=' * 80}")
        print(f" {description}")
        print(f"{'=' * 80}\n")
        
        try:
            result = subprocess.run(
                ['python', f'scripts/{script_name}'],
                capture_output=True,
                text=True,
                check=False
            )
            
            # 打印输出
            output = result.stdout
            if result.stderr:
                output += "\n" + result.stderr
            
            print(output)
            
            # 检查返回码
            success = result.returncode == 0
            
            if success:
                print(f"\n✓ {description} - 通过")
            else:
                print(f"\n✗ {description} - 失败")
            
            return success, output
        
        except Exception as e:
            error_msg = f"✗ {description} - 错误: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def run_all_validations(self):
        """运行所有验证"""
        print("\n" + "=" * 80)
        print(" 开始运行所有验证检查")
        print("=" * 80)
        print(f" 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        # 1. 内部链接验证
        success, output = self.run_script(
            'validate_internal_links.py',
            '1. 内部链接验证'
        )
        self.results.append(('内部链接验证', success, output))
        
        # 2. 元数据验证
        success, output = self.run_script(
            'validate_markdown.py',
            '2. 元数据验证'
        )
        self.results.append(('元数据验证', success, output))
        
        # 3. 内容结构验证
        success, output = self.run_script(
            'validate_content_structure.py',
            '3. 内容结构验证'
        )
        self.results.append(('内容结构验证', success, output))
    
    def generate_summary_report(self) -> str:
        """生成综合报告"""
        report = []
        report.append("\n" + "=" * 80)
        report.append(" 验证综合报告")
        report.append("=" * 80)
        report.append(f" 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        # 统计信息
        total = len(self.results)
        passed = sum(1 for _, success, _ in self.results if success)
        failed = total - passed
        
        report.append(f"总验证项: {total}")
        report.append(f"通过: {passed}")
        report.append(f"失败: {failed}")
        report.append("")
        
        # 详细结果
        report.append("详细结果:")
        report.append("-" * 80)
        
        for name, success, _ in self.results:
            status = "[OK] 通过" if success else "[FAIL] 失败"
            report.append(f"{name:30s} {status}")
        
        report.append("-" * 80)
        report.append("")
        
        # 总结
        if failed == 0:
            report.append("=" * 80)
            report.append(" [OK] 所有验证通过！")
            report.append("=" * 80)
        else:
            report.append("=" * 80)
            report.append(f" [FAIL] {failed} 项验证失败，请查看上述详细信息")
            report.append("=" * 80)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = 'validation-report.txt'):
        """保存验证报告到文件"""
        report_content = []
        report_content.append("=" * 80)
        report_content.append(" 完整验证报告")
        report_content.append("=" * 80)
        report_content.append(f" 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_content.append("=" * 80)
        report_content.append("")
        
        for name, success, output in self.results:
            report_content.append("\n" + "=" * 80)
            report_content.append(f" {name}")
            report_content.append("=" * 80)
            report_content.append("")
            report_content.append(output)
        
        report_content.append(self.generate_summary_report())
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_content))
        
        print(f"\n完整报告已保存到: {filename}")


def main():
    """主函数"""
    runner = ValidationRunner()
    
    # 运行所有验证
    runner.run_all_validations()
    
    # 生成并打印综合报告
    summary = runner.generate_summary_report()
    print(summary)
    
    # 保存完整报告
    runner.save_report()
    
    # 如果有失败的验证，返回非零退出码
    failed = sum(1 for _, success, _ in runner.results if not success)
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
