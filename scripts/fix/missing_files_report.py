#!/usr/bin/env python3
"""
生成缺失文件报告
分析失效链接并生成缺失文件列表
"""

import sys
import os
from pathlib import Path
from collections import defaultdict

# 添加scripts目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from validate_internal_links import InternalLinkValidator, LinkType


def main():
    """主函数"""
    print("=" * 80)
    print("缺失文件分析报告")
    print("=" * 80)
    print()
    
    # 运行验证
    validator = InternalLinkValidator()
    validator.validate_all()
    
    if not validator.broken_links:
        print("✓ 所有链接都有效！")
        return
    
    # 按类型分组
    by_type = defaultdict(list)
    for link in validator.broken_links:
        by_type[link.link_type].append(link)
    
    # 统计缺失的文件
    missing_files = set()
    for link in validator.broken_links:
        if link.link_type == LinkType.INLINE:
            # 提取目标路径
            target = Path(link.resolved_path)
            # 尝试多种可能的文件路径
            possible_paths = [
                target,
                target.with_suffix('.md'),
                target / 'index.md'
            ]
            missing_files.update(str(p) for p in possible_paths)
    
    print(f"发现 {len(validator.broken_links)} 个失效链接")
    print(f"涉及约 {len(missing_files)} 个缺失文件\n")
    
    # 按目录分组显示缺失文件
    by_directory = defaultdict(list)
    for file_path in sorted(missing_files):
        directory = str(Path(file_path).parent)
        by_directory[directory].append(Path(file_path).name)
    
    print("=" * 80)
    print("缺失文件列表（按目录分组）")
    print("=" * 80)
    print()
    
    for directory in sorted(by_directory.keys()):
        print(f"\n📁 {directory}/")
        for filename in sorted(by_directory[directory]):
            print(f"   - {filename}")
    
    # 生成Markdown报告
    report_lines = []
    report_lines.append("# 缺失文件报告\n")
    report_lines.append(f"**生成时间**: {Path.cwd()}\n")
    report_lines.append(f"**失效链接数**: {len(validator.broken_links)}\n")
    report_lines.append(f"**缺失文件数**: {len(missing_files)}\n")
    
    report_lines.append("\n## 按目录分组的缺失文件\n")
    for directory in sorted(by_directory.keys()):
        report_lines.append(f"\n### `{directory}/`\n")
        for filename in sorted(by_directory[directory]):
            report_lines.append(f"- [ ] {filename}\n")
    
    report_lines.append("\n## 失效链接详情\n")
    for link_type, links in by_type.items():
        report_lines.append(f"\n### {link_type.value.upper()} 链接 ({len(links)}个)\n")
        for link in links:
            report_lines.append(f"\n**源文件**: `{link.source_file}`\n")
            if link.line_number:
                report_lines.append(f"- 行号: {link.line_number}\n")
            report_lines.append(f"- 链接文本: {link.link_text}\n")
            report_lines.append(f"- 链接URL: `{link.link_url}`\n")
            report_lines.append(f"- 解析路径: `{link.resolved_path}`\n")
    
    # 写入报告文件
    report_file = Path('missing_files_report.md')
    with open(report_file, 'w', encoding='utf-8') as f:
        f.writelines(report_lines)
    
    print(f"\n\n详细报告已保存到: {report_file}")
    print("=" * 80)


if __name__ == '__main__':
    main()
