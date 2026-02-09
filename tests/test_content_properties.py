"""
内容质量属性测试
使用属性测试验证内容的正确性属性
"""

import re
import yaml
import pytest
from pathlib import Path
from typing import List, Dict


def find_all_markdown_files(docs_dir: str = 'docs') -> List[Path]:
    """查找所有Markdown文件"""
    docs_path = Path(docs_dir)
    return list(docs_path.rglob('*.md'))


def extract_front_matter(file_path: Path) -> Dict:
    """从Markdown文件中提取Front Matter"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return {}
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}
        
        front_matter = yaml.safe_load(parts[1])
        return front_matter if front_matter else {}
    except Exception:
        return {}


def extract_content_without_front_matter(file_path: Path) -> str:
    """提取不包含Front Matter的内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2]
        
        return content
    except Exception:
        return ""


def is_major_knowledge_module(file_path: Path) -> bool:
    """判断是否为主要知识模块（非index文件）"""
    file_path_str = str(file_path).replace('\\', '/')
    
    # 排除特定文件
    if file_path.name in ['index.md', 'README.md', 'glossary.md']:
        return False
    
    # 排除特定目录
    exclude_dirs = ['templates', 'learning-paths', 'case-studies', 'javascripts', 'references']
    for exclude_dir in exclude_dirs:
        if exclude_dir in file_path_str:
            return False
    
    return True


def test_property_metadata_completeness():
    """
    属性1：知识模块元数据完整性
    对于任何知识模块文件，其Front Matter元数据必须包含所有必需字段
    
    Feature: medical-device-embedded-knowledge-system
    Property 1: 知识模块元数据完整性
    Validates: Requirements 4.3, 8.2
    """
    required_fields = ['title', 'description', 'difficulty', 'estimated_time', 'tags', 'last_updated', 'version']
    valid_difficulties = ['基础', '中级', '高级']
    
    markdown_files = find_all_markdown_files()
    failures = []
    
    print(f"\n测试 {len(markdown_files)} 个文件的元数据完整性...")
    
    for md_file in markdown_files:
        # 跳过index和模板文件
        if not is_major_knowledge_module(md_file):
            continue
        
        front_matter = extract_front_matter(md_file)
        
        # 检查必需字段
        for field in required_fields:
            if field not in front_matter:
                failures.append(f"{md_file}: 缺少字段 '{field}'")
            elif not front_matter[field]:
                failures.append(f"{md_file}: 字段 '{field}' 为空")
        
        # 检查difficulty值
        if 'difficulty' in front_matter:
            if front_matter['difficulty'] not in valid_difficulties:
                failures.append(f"{md_file}: difficulty值 '{front_matter['difficulty']}' 无效")
    
    if failures:
        report = ["\n元数据完整性测试失败:"]
        report.extend(failures)
        pytest.fail("\n".join(report))
    else:
        print(f"✓ 所有文件元数据完整")


def test_property_code_examples_have_annotations():
    """
    属性7：代码示例完整性
    对于任何包含代码示例的知识模块，代码块必须附带注释、使用说明或潜在陷阱提示
    
    Feature: medical-device-embedded-knowledge-system
    Property 7: 代码示例完整性
    Validates: Requirements 7.3
    """
    markdown_files = find_all_markdown_files()
    failures = []
    
    print(f"\n测试 {len(markdown_files)} 个文件的代码示例完整性...")
    
    for md_file in markdown_files:
        if not is_major_knowledge_module(md_file):
            continue
        
        content = extract_content_without_front_matter(md_file)
        
        # 查找代码块
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
        
        if not code_blocks:
            continue  # 没有代码块，跳过
        
        # 检查是否有代码说明、注释或警告
        has_code_explanation = bool(re.search(r'\*\*代码说明\*\*|代码注释|使用说明', content))
        has_warnings = bool(re.search(r'!!! warning|!!! danger|!!! tip|常见陷阱|注意事项|最佳实践', content))
        has_inline_comments = any('//' in block or '/*' in block or '#' in block for block in code_blocks)
        
        if not (has_code_explanation or has_warnings or has_inline_comments):
            failures.append(f"{md_file}: 包含代码示例但缺少注释、说明或警告")
    
    if failures:
        report = ["\n代码示例完整性测试失败:"]
        report.extend(failures)
        pytest.fail("\n".join(report))
    else:
        print(f"✓ 所有代码示例都有适当的注释或说明")


def test_property_self_test_questions_count():
    """
    属性9：自测问题数量要求
    对于任何主要知识模块，其内容中必须包含至少5个自测问题
    
    Feature: medical-device-embedded-knowledge-system
    Property 9: 自测问题数量要求
    Validates: Requirements 9.1
    """
    markdown_files = find_all_markdown_files()
    failures = []
    
    print(f"\n测试 {len(markdown_files)} 个文件的自测问题数量...")
    
    for md_file in markdown_files:
        if not is_major_knowledge_module(md_file):
            continue
        
        content = extract_content_without_front_matter(md_file)
        
        # 查找自测问题部分
        if '## 自测问题' not in content and '## 自测' not in content:
            failures.append(f"{md_file}: 缺少自测问题部分")
            continue
        
        # 统计问题数量（使用??? question标记）
        question_count = len(re.findall(r'\?\?\? question', content))
        
        if question_count < 5:
            failures.append(f"{md_file}: 自测问题数量不足 (当前: {question_count}, 要求: 至少5个)")
    
    if failures:
        report = ["\n自测问题数量测试失败:"]
        report.extend(failures)
        pytest.fail("\n".join(report))
    else:
        print(f"✓ 所有主要模块都有足够的自测问题")


def test_property_references_exist():
    """
    属性13：参考文献存在性
    对于任何知识模块，其内容必须包含"参考文献"或"参考资料"部分
    
    Feature: medical-device-embedded-knowledge-system
    Property 13: 参考文献存在性
    Validates: Requirements 12.1
    """
    markdown_files = find_all_markdown_files()
    failures = []
    
    print(f"\n测试 {len(markdown_files)} 个文件的参考文献...")
    
    for md_file in markdown_files:
        if not is_major_knowledge_module(md_file):
            continue
        
        content = extract_content_without_front_matter(md_file)
        
        # 查找参考文献部分
        has_references = bool(re.search(r'## 参考文献|## 参考资料|## References', content))
        
        if not has_references:
            failures.append(f"{md_file}: 缺少参考文献部分")
            continue
        
        # 检查是否至少有一个参考条目
        # 查找列表项或编号列表
        references_section = re.split(r'## 参考文献|## 参考资料|## References', content)
        if len(references_section) > 1:
            ref_content = references_section[1].split('##')[0]  # 获取参考文献部分内容
            has_entries = bool(re.search(r'^\d+\.|^-|^\*', ref_content, re.MULTILINE))
            
            if not has_entries:
                failures.append(f"{md_file}: 参考文献部分为空")
    
    if failures:
        report = ["\n参考文献存在性测试失败:"]
        report.extend(failures)
        pytest.fail("\n".join(report))
    else:
        print(f"✓ 所有模块都有参考文献")


def test_property_content_structure_consistency():
    """
    属性2：知识模块内容结构一致性
    对于任何知识模块，必须包含学习目标、前置知识等必需部分
    
    Feature: medical-device-embedded-knowledge-system
    Property 2: 知识模块内容结构一致性
    Validates: Requirements 4.1
    """
    markdown_files = find_all_markdown_files()
    failures = []
    
    print(f"\n测试 {len(markdown_files)} 个文件的内容结构...")
    
    required_sections = ['## 学习目标', '## 前置知识', '## 内容']
    
    for md_file in markdown_files:
        if not is_major_knowledge_module(md_file):
            continue
        
        content = extract_content_without_front_matter(md_file)
        
        # 检查必需部分
        for section in required_sections:
            if section not in content:
                failures.append(f"{md_file}: 缺少 '{section}' 部分")
    
    if failures:
        report = ["\n内容结构一致性测试失败:"]
        report.extend(failures)
        pytest.fail("\n".join(report))
    else:
        print(f"✓ 所有模块内容结构一致")


def test_property_learning_objectives_present():
    """
    测试学习目标部分包含具体的目标列表
    """
    markdown_files = find_all_markdown_files()
    failures = []
    
    print(f"\n测试 {len(markdown_files)} 个文件的学习目标...")
    
    for md_file in markdown_files:
        if not is_major_knowledge_module(md_file):
            continue
        
        content = extract_content_without_front_matter(md_file)
        
        if '## 学习目标' not in content:
            continue
        
        # 提取学习目标部分
        sections = content.split('##')
        learning_objectives_section = None
        for i, section in enumerate(sections):
            if section.strip().startswith('学习目标'):
                if i + 1 < len(sections):
                    learning_objectives_section = sections[i]
                break
        
        if learning_objectives_section:
            # 检查是否有列表项
            has_objectives = bool(re.search(r'^-\s+', learning_objectives_section, re.MULTILINE))
            if not has_objectives:
                failures.append(f"{md_file}: 学习目标部分没有具体的目标列表")
    
    if failures:
        report = ["\n学习目标测试失败:"]
        report.extend(failures)
        pytest.fail("\n".join(report))
    else:
        print(f"✓ 所有模块都有具体的学习目标")


if __name__ == '__main__':
    # 允许直接运行此文件进行测试
    pytest.main([__file__, '-v'])
