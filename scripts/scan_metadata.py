#!/usr/bin/env python3
"""
扫描所有文档的Front Matter元数据
识别缺失或错误的元数据字段，生成修复清单
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class MetadataIssue:
    """元数据问题记录"""
    file_path: str
    issue_type: str  # 'missing_field', 'invalid_value', 'wrong_format'
    field_name: str
    current_value: Optional[str] = None
    expected_value: Optional[str] = None
    severity: str = 'warning'  # 'error', 'warning', 'info'


@dataclass
class MetadataScanResult:
    """元数据扫描结果"""
    total_files: int = 0
    files_with_front_matter: int = 0
    files_without_front_matter: int = 0
    issues: List[MetadataIssue] = field(default_factory=list)
    
    def add_issue(self, issue: MetadataIssue):
        """添加问题"""
        self.issues.append(issue)
    
    def get_issues_by_severity(self, severity: str) -> List[MetadataIssue]:
        """按严重性获取问题"""
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_file(self, file_path: str) -> List[MetadataIssue]:
        """按文件获取问题"""
        return [issue for issue in self.issues if issue.file_path == file_path]


class MetadataScanner:
    """元数据扫描器"""
    
    # 必需字段
    REQUIRED_FIELDS = [
        'title',
        'description',
        'difficulty',
        'estimated_time',
        'tags',
        'last_updated',
        'version'
    ]
    
    # 有效的difficulty值
    VALID_DIFFICULTIES_ZH = ['基础', '中级', '高级']
    VALID_DIFFICULTIES_EN = ['Beginner', 'Intermediate', 'Advanced']
    
    # 主要模块目录（需要完整元数据）
    MAIN_MODULE_DIRS = [
        'technical-knowledge',
        'regulatory-standards',
        'software-engineering',
        'case-studies',
        'getting-started',
        'references'
    ]
    
    def __init__(self, docs_dir: str = 'docs'):
        self.docs_dir = Path(docs_dir)
        self.result = MetadataScanResult()
    
    def extract_front_matter(self, content: str) -> Tuple[Optional[Dict], bool]:
        """
        提取Front Matter
        返回: (front_matter_dict, has_front_matter)
        """
        if not content.strip().startswith('---'):
            return None, False
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return None, False
        
        try:
            front_matter = yaml.safe_load(parts[1])
            return front_matter, True
        except yaml.YAMLError as e:
            return None, True  # 有Front Matter但解析失败
    
    def is_main_module_file(self, file_path: Path) -> bool:
        """判断是否是主要模块文件（需要完整元数据）"""
        # 跳过index文件
        if file_path.name == 'index.md':
            return False
        
        # 检查是否在主要模块目录下
        for module_dir in self.MAIN_MODULE_DIRS:
            if module_dir in file_path.parts:
                return True
        
        return False
    
    def validate_difficulty(self, difficulty: str, language: str = 'zh') -> bool:
        """验证difficulty值"""
        if language == 'zh':
            return difficulty in self.VALID_DIFFICULTIES_ZH
        else:
            # 对于英文文件，接受英文或中文difficulty值
            return difficulty in self.VALID_DIFFICULTIES_EN or difficulty in self.VALID_DIFFICULTIES_ZH
    
    def validate_date_format(self, date_str: str) -> bool:
        """验证日期格式 (YYYY-MM-DD)"""
        try:
            datetime.strptime(str(date_str), '%Y-%m-%d')
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_tags(self, tags) -> bool:
        """验证tags格式"""
        return isinstance(tags, list) and len(tags) > 0
    
    def scan_file(self, file_path: Path):
        """扫描单个文件"""
        self.result.total_files += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            self.result.add_issue(MetadataIssue(
                file_path=str(file_path),
                issue_type='read_error',
                field_name='file',
                current_value=str(e),
                severity='error'
            ))
            return
        
        # 提取Front Matter
        front_matter, has_front_matter = self.extract_front_matter(content)
        
        if not has_front_matter:
            self.result.files_without_front_matter += 1
            # 只对主要模块文件报告缺失Front Matter
            if self.is_main_module_file(file_path):
                self.result.add_issue(MetadataIssue(
                    file_path=str(file_path),
                    issue_type='missing_front_matter',
                    field_name='front_matter',
                    severity='error'
                ))
            return
        
        if front_matter is None:
            # Front Matter解析失败
            self.result.add_issue(MetadataIssue(
                file_path=str(file_path),
                issue_type='parse_error',
                field_name='front_matter',
                severity='error'
            ))
            return
        
        self.result.files_with_front_matter += 1
        
        # 只对主要模块文件进行完整验证
        if not self.is_main_module_file(file_path):
            return
        
        # 检查必需字段
        for field in self.REQUIRED_FIELDS:
            if field not in front_matter:
                self.result.add_issue(MetadataIssue(
                    file_path=str(file_path),
                    issue_type='missing_field',
                    field_name=field,
                    severity='error'
                ))
        
        # 验证difficulty值
        if 'difficulty' in front_matter:
            difficulty = front_matter['difficulty']
            # 判断语言
            language = 'en' if '/en/' in str(file_path) or '\\en\\' in str(file_path) else 'zh'
            
            if not self.validate_difficulty(difficulty, language):
                if language == 'zh':
                    expected = self.VALID_DIFFICULTIES_ZH
                else:
                    expected = self.VALID_DIFFICULTIES_EN
                
                self.result.add_issue(MetadataIssue(
                    file_path=str(file_path),
                    issue_type='invalid_value',
                    field_name='difficulty',
                    current_value=str(difficulty),
                    expected_value=f"应为: {', '.join(expected)}",
                    severity='error'
                ))
        
        # 验证日期格式
        if 'last_updated' in front_matter:
            if not self.validate_date_format(front_matter['last_updated']):
                self.result.add_issue(MetadataIssue(
                    file_path=str(file_path),
                    issue_type='wrong_format',
                    field_name='last_updated',
                    current_value=str(front_matter['last_updated']),
                    expected_value='YYYY-MM-DD',
                    severity='warning'
                ))
        
        # 验证tags格式
        if 'tags' in front_matter:
            if not self.validate_tags(front_matter['tags']):
                self.result.add_issue(MetadataIssue(
                    file_path=str(file_path),
                    issue_type='invalid_value',
                    field_name='tags',
                    current_value=str(front_matter.get('tags')),
                    expected_value='应为非空列表',
                    severity='warning'
                ))
    
    def scan_directory(self, directory: Path = None):
        """扫描目录下的所有Markdown文件"""
        if directory is None:
            directory = self.docs_dir
        
        for md_file in directory.rglob('*.md'):
            self.scan_file(md_file)
    
    def generate_report(self) -> str:
        """生成扫描报告"""
        report = []
        report.append("=" * 80)
        report.append("元数据扫描报告")
        report.append("=" * 80)
        report.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 统计信息
        report.append("统计信息:")
        report.append(f"  总文件数: {self.result.total_files}")
        report.append(f"  包含Front Matter: {self.result.files_with_front_matter}")
        report.append(f"  缺少Front Matter: {self.result.files_without_front_matter}")
        report.append(f"  发现问题数: {len(self.result.issues)}")
        report.append("")
        
        # 按严重性分类
        errors = self.result.get_issues_by_severity('error')
        warnings = self.result.get_issues_by_severity('warning')
        
        report.append(f"  错误 (Error): {len(errors)}")
        report.append(f"  警告 (Warning): {len(warnings)}")
        report.append("")
        
        # 按问题类型统计
        issue_types = {}
        for issue in self.result.issues:
            key = f"{issue.issue_type} - {issue.field_name}"
            issue_types[key] = issue_types.get(key, 0) + 1
        
        if issue_types:
            report.append("问题类型统计:")
            for issue_type, count in sorted(issue_types.items(), key=lambda x: -x[1]):
                report.append(f"  {issue_type}: {count}")
            report.append("")
        
        # 详细问题列表
        if self.result.issues:
            report.append("=" * 80)
            report.append("详细问题列表")
            report.append("=" * 80)
            report.append("")
            
            # 按文件分组
            files_with_issues = {}
            for issue in self.result.issues:
                if issue.file_path not in files_with_issues:
                    files_with_issues[issue.file_path] = []
                files_with_issues[issue.file_path].append(issue)
            
            for file_path in sorted(files_with_issues.keys()):
                issues = files_with_issues[file_path]
                report.append(f"文件: {file_path}")
                report.append(f"  问题数: {len(issues)}")
                
                for issue in issues:
                    severity_marker = "❌" if issue.severity == 'error' else "⚠️"
                    report.append(f"  {severity_marker} [{issue.severity.upper()}] {issue.issue_type}")
                    report.append(f"     字段: {issue.field_name}")
                    if issue.current_value:
                        report.append(f"     当前值: {issue.current_value}")
                    if issue.expected_value:
                        report.append(f"     期望值: {issue.expected_value}")
                
                report.append("")
        
        return "\n".join(report)
    
    def save_repair_checklist(self, output_file: str = 'metadata-repair-checklist.json'):
        """保存修复清单为JSON格式"""
        checklist = {
            'scan_time': datetime.now().isoformat(),
            'summary': {
                'total_files': self.result.total_files,
                'files_with_front_matter': self.result.files_with_front_matter,
                'files_without_front_matter': self.result.files_without_front_matter,
                'total_issues': len(self.result.issues),
                'errors': len(self.result.get_issues_by_severity('error')),
                'warnings': len(self.result.get_issues_by_severity('warning'))
            },
            'issues': [
                {
                    'file_path': issue.file_path,
                    'issue_type': issue.issue_type,
                    'field_name': issue.field_name,
                    'current_value': issue.current_value,
                    'expected_value': issue.expected_value,
                    'severity': issue.severity
                }
                for issue in self.result.issues
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(checklist, f, ensure_ascii=False, indent=2)
        
        print(f"修复清单已保存到: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='扫描文档元数据')
    parser.add_argument('--docs-dir', default='docs', help='文档目录路径')
    parser.add_argument('--output', default='metadata-scan-report.txt', help='报告输出文件')
    parser.add_argument('--checklist', default='metadata-repair-checklist.json', help='修复清单输出文件')
    parser.add_argument('--language', choices=['zh', 'en', 'all'], default='all', help='扫描语言')
    
    args = parser.parse_args()
    
    # 扫描指定语言
    if args.language == 'all':
        scan_dirs = [Path(args.docs_dir)]
    else:
        scan_dirs = [Path(args.docs_dir) / args.language]
    
    scanner = MetadataScanner(args.docs_dir)
    
    for scan_dir in scan_dirs:
        if scan_dir.exists():
            print(f"正在扫描: {scan_dir}")
            scanner.scan_directory(scan_dir)
    
    # 生成报告
    report = scanner.generate_report()
    print(report)
    
    # 保存报告
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n报告已保存到: {args.output}")
    
    # 保存修复清单
    scanner.save_repair_checklist(args.checklist)
    
    # 返回状态码
    errors = scanner.result.get_issues_by_severity('error')
    return 1 if errors else 0


if __name__ == '__main__':
    exit(main())
