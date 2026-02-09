"""
链接验证测试
验证所有内部链接的有效性
"""

import re
import pytest
from pathlib import Path
from typing import List, Tuple


def find_all_markdown_files(docs_dir: str = 'docs') -> List[Path]:
    """查找所有Markdown文件"""
    docs_path = Path(docs_dir)
    return list(docs_path.rglob('*.md'))


def extract_internal_links(file_path: Path) -> List[Tuple[str, str]]:
    """
    从Markdown文件中提取内部链接
    返回: [(link_text, link_url), ...]
    """
    links = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 匹配Markdown链接格式: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)
        
        for text, url in matches:
            # 只处理内部链接（不以http开头）
            if not url.startswith('http'):
                # 移除锚点
                url_without_anchor = url.split('#')[0]
                if url_without_anchor:  # 忽略纯锚点链接
                    links.append((text, url_without_anchor))
        
        return links
    except Exception as e:
        print(f"警告: 无法读取文件 {file_path}: {str(e)}")
        return []


def resolve_link_path(source_file: Path, link_url: str) -> Path:
    """
    解析链接的绝对路径
    """
    # 如果链接以/开头，从docs根目录开始
    if link_url.startswith('/'):
        return Path('docs') / link_url.lstrip('/')
    else:
        # 相对于当前文件的路径
        return (source_file.parent / link_url).resolve()


def test_all_internal_links_valid():
    """
    测试所有内部链接有效
    属性3：内部链接有效性
    验证：需求 4.4, 11.3
    """
    broken_links = []
    
    # 获取所有Markdown文件
    markdown_files = find_all_markdown_files()
    
    print(f"\n检查 {len(markdown_files)} 个Markdown文件的内部链接...")
    
    for md_file in markdown_files:
        # 提取内部链接
        links = extract_internal_links(md_file)
        
        for link_text, link_url in links:
            # 解析链接路径
            target_path = resolve_link_path(md_file, link_url)
            
            # 检查目标文件是否存在
            # 尝试多种可能的扩展名
            possible_paths = [
                target_path,
                target_path.with_suffix('.md'),
                target_path / 'index.md'
            ]
            
            exists = any(p.exists() for p in possible_paths)
            
            if not exists:
                broken_links.append({
                    'source_file': str(md_file),
                    'link_text': link_text,
                    'link_url': link_url,
                    'resolved_path': str(target_path)
                })
    
    # 生成报告
    if broken_links:
        report = ["\n失效的内部链接:"]
        report.append("=" * 80)
        
        for link in broken_links:
            report.append(f"\n源文件: {link['source_file']}")
            report.append(f"  链接文本: {link['link_text']}")
            report.append(f"  链接URL: {link['link_url']}")
            report.append(f"  解析路径: {link['resolved_path']}")
        
        report.append(f"\n总计: {len(broken_links)} 个失效链接")
        report.append("=" * 80)
        
        pytest.fail("\n".join(report))
    else:
        print(f"✓ 所有内部链接有效")


def test_related_modules_links_valid():
    """
    测试Front Matter中的related_modules链接有效
    """
    import yaml
    
    broken_related_links = []
    markdown_files = find_all_markdown_files()
    
    print(f"\n检查 {len(markdown_files)} 个文件的related_modules链接...")
    
    for md_file in markdown_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取Front Matter
            if not content.startswith('---'):
                continue
            
            parts = content.split('---', 2)
            if len(parts) < 3:
                continue
            
            front_matter = yaml.safe_load(parts[1])
            if not front_matter or 'related_modules' not in front_matter:
                continue
            
            # 检查每个related_modules链接
            for related_module in front_matter['related_modules']:
                # 构建目标路径
                target_path = Path('docs') / f"{related_module}.md"
                
                # 也检查index.md
                if not target_path.exists():
                    target_path = Path('docs') / related_module / 'index.md'
                
                if not target_path.exists():
                    broken_related_links.append({
                        'source_file': str(md_file),
                        'related_module': related_module,
                        'expected_path': str(target_path)
                    })
        
        except Exception as e:
            print(f"警告: 处理文件 {md_file} 时出错: {str(e)}")
    
    # 生成报告
    if broken_related_links:
        report = ["\n失效的related_modules链接:"]
        report.append("=" * 80)
        
        for link in broken_related_links:
            report.append(f"\n源文件: {link['source_file']}")
            report.append(f"  相关模块: {link['related_module']}")
            report.append(f"  期望路径: {link['expected_path']}")
        
        report.append(f"\n总计: {len(broken_related_links)} 个失效的related_modules链接")
        report.append("=" * 80)
        
        pytest.fail("\n".join(report))
    else:
        print(f"✓ 所有related_modules链接有效")


if __name__ == '__main__':
    # 允许直接运行此文件进行测试
    pytest.main([__file__, '-v'])
