#!/usr/bin/env python3
"""
内容结构验证脚本
验证所有知识模块的内容结构完整性和一致性

需求: 12.3
"""

import re
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class StructureIssue:
    """结构问题记录"""
    file_path: str
    issue_type: str
    message: str
    severity: str = "error"  # error, warning


class ContentStructureValidator:
    """内容结构验证器"""
    
    # 必需的内容部分
    REQUIRED_SECTIONS = [
        '## 学习目标',
        '## 前置知识',
        '## 内容'
    ]
    
    # 推荐的内容部分
    RECOMMENDED_SECTIONS = [
        '## 最佳实践',
        '## 常见陷阱',
        '## 实践练习',
        '## 自测问题',
        '## 参考文献'
    ]
    
    # 排除的文件和目录
    EXCLUDE_PATTERNS = ['index.md', 'README.md', 'glossary.md', 'templates/', 'learning-paths/']
    
    def __init__(self, docs_dir: str = 'docs'):
        self.docs_dir = Path(docs_dir)
        self.issues: List[StructureIssue] = []
    
    def should_validate_file(self, file_path: Path) -> bool:
        """判断文件是否需要验证"""
        file_path_str = str(file_path).replace('\\', '/')
        
        # 检查是否在排除列表中
        for pattern in self.EXCLUDE_PATTERNS:
            if pattern in file_path_str:
                return False
        
        # 排除特定文件名
        if file_path.name in ['index.md', 'README.md', 'glossary.md']:
            return False
        
        # 只验证主要知识模块目录
        main_dirs = ['technical-knowledge', 'regulatory-standards', 'software-engineering']
        return any(main_dir in file_path_str for main_dir in main_dirs)
    
    def extract_content(self, file_path: Path) -> str:
        """提取文件内容（不包含Front Matter）"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 移除Front Matter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    return parts[2]
            
            return content
        except Exception as e:
            print(f"警告: 读取文件 {file_path} 失败: {e}")
            return ""
    
    def validate_required_sections(self, file_path: Path, content: str):
        """验证必需部分"""
        for section in self.REQUIRED_SECTIONS:
            if section not in content:
                self.issues.append(StructureIssue(
                    file_path=str(file_path),
                    issue_type="缺少必需部分",
                    message=f"缺少 '{section}' 部分",
                    severity="error"
                ))
    
    def validate_recommended_sections(self, file_path: Path, content: str):
        """验证推荐部分"""
        missing_sections = []
        for section in self.RECOMMENDED_SECTIONS:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            self.issues.append(StructureIssue(
                file_path=str(file_path),
                issue_type="缺少推荐部分",
                message=f"缺少推荐部分: {', '.join(missing_sections)}",
                severity="warning"
            ))
    
    def validate_learning_objectives(self, file_path: Path, content: str):
        """验证学习目标部分"""
        if '## 学习目标' not in content:
            return
        
        # 提取学习目标部分
        sections = content.split('##')
        learning_objectives_section = None
        
        for i, section in enumerate(sections):
            if section.strip().startswith('学习目标'):
                # 获取到下一个##之前的内容
                learning_objectives_section = section
                break
        
        if learning_objectives_section:
            # 检查是否有列表项
            has_objectives = bool(re.search(r'^-\s+', learning_objectives_section, re.MULTILINE))
            if not has_objectives:
                self.issues.append(StructureIssue(
                    file_path=str(file_path),
                    issue_type="学习目标格式",
                    message="学习目标部分没有具体的目标列表",
                    severity="error"
                ))
    
    def validate_code_examples(self, file_path: Path, content: str):
        """验证代码示例"""
        # 查找代码块
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
        
        if not code_blocks:
            return  # 没有代码块，跳过
        
        # 检查是否有代码说明、注释或警告
        has_code_explanation = bool(re.search(r'\*\*代码说明\*\*|代码注释|使用说明', content))
        has_warnings = bool(re.search(r'!!! warning|!!! danger|!!! tip|常见陷阱|注意事项|最佳实践', content))
        has_inline_comments = any('//' in block or '/*' in block or '#' in block for block in code_blocks)
        
        if not (has_code_explanation or has_warnings or has_inline_comments):
            self.issues.append(StructureIssue(
                file_path=str(file_path),
                issue_type="代码示例说明",
                message=f"包含 {len(code_blocks)} 个代码示例但缺少注释、说明或警告",
                severity="warning"
            ))
    
    def validate_self_test_questions(self, file_path: Path, content: str):
        """验证自测问题"""
        # 查找自测问题部分
        if '## 自测问题' not in content and '## 自测' not in content:
            self.issues.append(StructureIssue(
                file_path=str(file_path),
                issue_type="缺少自测问题",
                message="缺少自测问题部分",
                severity="warning"
            ))
            return
        
        # 统计问题数量（使用??? question标记）
        question_count = len(re.findall(r'\?\?\? question', content))
        
        if question_count < 5:
            self.issues.append(StructureIssue(
                file_path=str(file_path),
                issue_type="自测问题数量",
                message=f"自测问题数量不足 (当前: {question_count}, 要求: 至少5个)",
                severity="warning"
            ))
        
        # 检查每个问题是否有答案
        questions = re.findall(r'\?\?\? question "(.*?)"', content)
        answers = re.findall(r'\?\?\? success "答案"', content)
        
        if len(questions) != len(answers):
            self.issues.append(StructureIssue(
                file_path=str(file_path),
                issue_type="自测问题答案",
                message=f"问题数量 ({len(questions)}) 与答案数量 ({len(answers)}) 不匹配",
                severity="error"
            ))
    
    def validate_references(self, file_path: Path, content: str):
        """验证参考文献"""
        # 查找参考文献部分
        has_references = bool(re.search(r'## 参考文献|## 参考资料|## References', content))
        
        if not has_references:
            self.issues.append(StructureIssue(
                file_path=str(file_path),
                issue_type="缺少参考文献",
                message="缺少参考文献部分",
                severity="warning"
            ))
            return
        
        # 检查是否至少有一个参考条目
        references_section = re.split(r'## 参考文献|## 参考资料|## References', content)
        if len(references_section) > 1:
            ref_content = references_section[1].split('##')[0]  # 获取参考文献部分内容
            has_entries = bool(re.search(r'^\d+\.|^-|^\*', ref_content, re.MULTILINE))
            
            if not has_entries:
                self.issues.append(StructureIssue(
                    file_path=str(file_path),
                    issue_type="参考文献为空",
                    message="参考文献部分为空",
                    severity="warning"
                ))
            else:
                # 统计参考条目数量
                entry_count = len(re.findall(r'^\d+\.|^-|^\*', ref_content, re.MULTILINE))
                if entry_count < 3:
                    self.issues.append(StructureIssue(
                        file_path=str(file_path),
                        issue_type="参考文献数量",
                        message=f"参考文献数量不足 (当前: {entry_count}, 推荐: 至少3个)",
                        severity="warning"
                    ))
    
    def validate_file(self, file_path: Path):
        """验证单个文件"""
        content = self.extract_content(file_path)
        
        if not content:
            return
        
        # 执行各项验证
        self.validate_required_sections(file_path, content)
        self.validate_recommended_sections(file_path, content)
        self.validate_learning_objectives(file_path, content)
        self.validate_code_examples(file_path, content)
        self.validate_self_test_questions(file_path, content)
        self.validate_references(file_path, content)
    
    def validate_all(self):
        """验证所有文件"""
        print("开始验证内容结构...\n")
        
        # 查找所有Markdown文件
        md_files = list(self.docs_dir.rglob('*.md'))
        validated_count = 0
        
        for md_file in md_files:
            if self.should_validate_file(md_file):
                self.validate_file(md_file)
                validated_count += 1
        
        print(f"验证了 {validated_count} 个文件")
        print(f"发现 {len(self.issues)} 个问题\n")
    
    def generate_report(self) -> str:
        """生成验证报告"""
        report = []
        report.append("=" * 80)
        report.append("内容结构验证报告")
        report.append("=" * 80)
        
        # 统计信息
        errors = [issue for issue in self.issues if issue.severity == "error"]
        warnings = [issue for issue in self.issues if issue.severity == "warning"]
        
        report.append(f"\n总问题数: {len(self.issues)}")
        report.append(f"  错误: {len(errors)}")
        report.append(f"  警告: {len(warnings)}")
        report.append("")
        
        if self.issues:
            # 按文件分组
            issues_by_file = {}
            for issue in self.issues:
                if issue.file_path not in issues_by_file:
                    issues_by_file[issue.file_path] = []
                issues_by_file[issue.file_path].append(issue)
            
            # 输出错误
            if errors:
                report.append("\n错误:")
                report.append("-" * 80)
                
                for file_path in sorted(issues_by_file.keys()):
                    file_errors = [i for i in issues_by_file[file_path] if i.severity == "error"]
                    if file_errors:
                        report.append(f"\n文件: {file_path}")
                        for issue in file_errors:
                            report.append(f"  ✗ [{issue.issue_type}] {issue.message}")
            
            # 输出警告
            if warnings:
                report.append("\n警告:")
                report.append("-" * 80)
                
                for file_path in sorted(issues_by_file.keys()):
                    file_warnings = [i for i in issues_by_file[file_path] if i.severity == "warning"]
                    if file_warnings:
                        report.append(f"\n文件: {file_path}")
                        for issue in file_warnings:
                            report.append(f"  ⚠ [{issue.issue_type}] {issue.message}")
            
            report.append("")
            report.append("=" * 80)
            if errors:
                report.append("验证失败！请修复上述错误。")
            else:
                report.append("验证通过（有警告）。建议修复警告以提高内容质量。")
            report.append("=" * 80)
        else:
            report.append("=" * 80)
            report.append("✓ 所有文件内容结构完整！")
            report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """主函数"""
    validator = ContentStructureValidator()
    validator.validate_all()
    
    # 生成并打印报告
    report = validator.generate_report()
    
    # 使用UTF-8编码打印，避免Windows控制台编码问题
    try:
        print(report)
    except UnicodeEncodeError:
        # 如果打印失败，替换特殊字符
        report_ascii = report.replace('✓', '[OK]').replace('✗', '[FAIL]').replace('⚠', '[WARN]')
        print(report_ascii)
    
    # 如果有错误，返回非零退出码
    errors = [issue for issue in validator.issues if issue.severity == "error"]
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
