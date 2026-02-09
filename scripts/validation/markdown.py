#!/usr/bin/env python3
"""
元数据验证脚本
验证所有Markdown文件的Front Matter元数据完整性和有效性
"""

import os
import sys
import yaml
from pathlib import Path
from typing import List, Dict, Tuple

# 必需的元数据字段
REQUIRED_FIELDS = ['title', 'description', 'difficulty', 'estimated_time', 'tags', 'last_updated', 'version']

# 有效的difficulty值
VALID_DIFFICULTIES = ['基础', '中级', '高级']

# 排除的文件和目录
EXCLUDE_PATTERNS = ['index.md', 'README.md', 'glossary.md', 'templates/', 'learning-paths/']


class ValidationError:
    """验证错误类"""
    def __init__(self, file_path: str, error_type: str, message: str):
        self.file_path = file_path
        self.error_type = error_type
        self.message = message
    
    def __str__(self):
        return f"[{self.error_type}] {self.file_path}: {self.message}"


def should_validate_file(file_path: Path) -> bool:
    """判断文件是否需要验证"""
    file_path_str = str(file_path).replace('\\', '/')
    
    # 检查是否在排除列表中
    for pattern in EXCLUDE_PATTERNS:
        if pattern in file_path_str:
            return False
    
    # 排除特定文件名
    if file_path.name in ['index.md', 'README.md', 'glossary.md']:
        return False
    
    return True


def extract_front_matter(file_path: Path) -> Tuple[Dict, List[str]]:
    """
    从Markdown文件中提取Front Matter
    返回: (front_matter_dict, errors)
    """
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否有Front Matter
        if not content.startswith('---'):
            errors.append(f"文件缺少Front Matter")
            return {}, errors
        
        # 分割Front Matter
        parts = content.split('---', 2)
        if len(parts) < 3:
            errors.append(f"Front Matter格式错误")
            return {}, errors
        
        # 解析YAML
        try:
            front_matter = yaml.safe_load(parts[1])
            if front_matter is None:
                errors.append(f"Front Matter为空")
                return {}, errors
            return front_matter, errors
        except yaml.YAMLError as e:
            errors.append(f"YAML解析错误: {str(e)}")
            return {}, errors
            
    except Exception as e:
        errors.append(f"读取文件错误: {str(e)}")
        return {}, errors


def validate_front_matter(file_path: Path, front_matter: Dict) -> List[ValidationError]:
    """验证Front Matter的完整性和有效性"""
    validation_errors = []
    
    # 检查必需字段
    for field in REQUIRED_FIELDS:
        if field not in front_matter:
            validation_errors.append(
                ValidationError(str(file_path), "缺少字段", f"缺少必需字段: {field}")
            )
        elif not front_matter[field]:
            validation_errors.append(
                ValidationError(str(file_path), "字段为空", f"字段 '{field}' 不能为空")
            )
    
    # 验证difficulty字段值
    if 'difficulty' in front_matter:
        difficulty = front_matter['difficulty']
        if difficulty not in VALID_DIFFICULTIES:
            validation_errors.append(
                ValidationError(
                    str(file_path), 
                    "无效值", 
                    f"difficulty值 '{difficulty}' 无效，必须是: {', '.join(VALID_DIFFICULTIES)}"
                )
            )
    
    # 验证tags字段是列表
    if 'tags' in front_matter:
        if not isinstance(front_matter['tags'], list):
            validation_errors.append(
                ValidationError(str(file_path), "类型错误", "tags字段必须是列表")
            )
        elif len(front_matter['tags']) == 0:
            validation_errors.append(
                ValidationError(str(file_path), "字段为空", "tags列表不能为空")
            )
    
    # 验证related_modules字段（如果存在）
    if 'related_modules' in front_matter:
        if not isinstance(front_matter['related_modules'], list):
            validation_errors.append(
                ValidationError(str(file_path), "类型错误", "related_modules字段必须是列表")
            )
    
    # 验证language字段（如果存在）
    if 'language' in front_matter:
        valid_languages = ['zh-CN', 'en-US']
        if front_matter['language'] not in valid_languages:
            validation_errors.append(
                ValidationError(
                    str(file_path), 
                    "无效值", 
                    f"language值 '{front_matter['language']}' 无效"
                )
            )
    
    return validation_errors


def validate_all_markdown_files(docs_dir: str = 'docs') -> Tuple[int, int, List[ValidationError]]:
    """
    验证所有Markdown文件
    返回: (总文件数, 验证的文件数, 错误列表)
    """
    docs_path = Path(docs_dir)
    all_errors = []
    total_files = 0
    validated_files = 0
    
    # 遍历所有Markdown文件
    for md_file in docs_path.rglob('*.md'):
        total_files += 1
        
        # 检查是否需要验证
        if not should_validate_file(md_file):
            continue
        
        validated_files += 1
        
        # 提取Front Matter
        front_matter, extract_errors = extract_front_matter(md_file)
        
        # 如果提取失败，记录错误
        if extract_errors:
            for error_msg in extract_errors:
                all_errors.append(
                    ValidationError(str(md_file), "提取错误", error_msg)
                )
            continue
        
        # 验证Front Matter
        validation_errors = validate_front_matter(md_file, front_matter)
        all_errors.extend(validation_errors)
    
    return total_files, validated_files, all_errors


def generate_report(total_files: int, validated_files: int, errors: List[ValidationError]) -> str:
    """生成验证报告"""
    report = []
    report.append("=" * 80)
    report.append("元数据验证报告")
    report.append("=" * 80)
    report.append(f"\n总文件数: {total_files}")
    report.append(f"验证的文件数: {validated_files}")
    report.append(f"跳过的文件数: {total_files - validated_files}")
    report.append(f"发现的错误数: {len(errors)}")
    report.append("")
    
    if errors:
        report.append("错误详情:")
        report.append("-" * 80)
        
        # 按文件分组错误
        errors_by_file = {}
        for error in errors:
            if error.file_path not in errors_by_file:
                errors_by_file[error.file_path] = []
            errors_by_file[error.file_path].append(error)
        
        # 输出每个文件的错误
        for file_path in sorted(errors_by_file.keys()):
            report.append(f"\n文件: {file_path}")
            for error in errors_by_file[file_path]:
                report.append(f"  - [{error.error_type}] {error.message}")
        
        report.append("")
        report.append("=" * 80)
        report.append("验证失败！请修复上述错误。")
        report.append("=" * 80)
    else:
        report.append("=" * 80)
        report.append("✓ 所有文件验证通过！")
        report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """主函数"""
    print("开始验证Markdown文件元数据...\n")
    
    # 验证所有文件
    total_files, validated_files, errors = validate_all_markdown_files()
    
    # 生成并打印报告
    report = generate_report(total_files, validated_files, errors)
    
    # 使用UTF-8编码打印，避免Windows控制台编码问题
    try:
        print(report)
    except UnicodeEncodeError:
        # 如果打印失败，替换特殊字符
        report_ascii = report.replace('✓', '[OK]').replace('✗', '[FAIL]')
        print(report_ascii)
    
    # 如果有错误，返回非零退出码
    if errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
