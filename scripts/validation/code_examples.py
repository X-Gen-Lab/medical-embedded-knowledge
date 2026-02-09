#!/usr/bin/env python3
"""
扫描所有代码示例并检查是否有说明或注释

根据需求9.5：所有代码示例必须包含注释和说明
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
import yaml


class CodeBlock:
    """代码块数据类"""
    def __init__(self, file_path: Path, language: str, code: str, line_number: int):
        self.file_path = file_path
        self.language = language
        self.code = code
        self.line_number = line_number
        self.has_comments = False
        self.has_explanation = False
        self.explanation_text = ""
    
    def check_has_comments(self) -> bool:
        """检查代码块内是否有注释"""
        # 检查常见的注释模式
        comment_patterns = [
            r'//.*',           # C/C++/Java 单行注释
            r'/\*.*?\*/',      # C/C++/Java 多行注释
            r'#.*',            # Python/Shell 注释
            r'<!--.*?-->',     # HTML/XML 注释
        ]
        
        for pattern in comment_patterns:
            if re.search(pattern, self.code, re.DOTALL):
                self.has_comments = True
                return True
        
        return False
    
    def check_has_explanation(self, content_after: str) -> bool:
        """检查代码块后是否有说明文本"""
        # 检查代码块后的内容
        # 如果紧接着有文本段落（不是另一个代码块或标题），认为有说明
        
        # 提取代码块后的下一段内容（最多500字符）
        next_content = content_after[:500].strip()
        
        if not next_content:
            return False
        
        # 如果下一行是标题、代码块或列表，认为没有说明
        if next_content.startswith('#') or \
           next_content.startswith('```') or \
           next_content.startswith('- ') or \
           next_content.startswith('* ') or \
           next_content.startswith('1. '):
            return False
        
        # 检查是否有"代码说明"、"说明"、"解释"等关键词
        explanation_keywords = [
            '代码说明', '说明', '解释', '注释', '描述',
            'Code explanation', 'Explanation', 'Description',
            '**代码说明**', '**说明**'
        ]
        
        for keyword in explanation_keywords:
            if keyword in next_content:
                self.has_explanation = True
                self.explanation_text = next_content[:200]
                return True
        
        # 如果有实质性的文本内容（超过20个字符），也认为有说明
        if len(next_content) > 20 and not next_content.startswith('```'):
            self.has_explanation = True
            self.explanation_text = next_content[:200]
            return True
        
        return False


def extract_code_blocks(file_path: Path) -> List[CodeBlock]:
    """从Markdown文件中提取所有代码块"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"警告: 无法读取文件 {file_path}: {e}")
        return []
    
    # 跳过Front Matter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    
    code_blocks = []
    
    # 使用正则表达式匹配代码块
    # 匹配 ```language 到 ``` 的内容
    pattern = r'```(\w*)\n(.*?)```'
    
    for match in re.finditer(pattern, content, re.DOTALL):
        language = match.group(1) or 'text'
        code = match.group(2)
        
        # 计算行号
        line_number = content[:match.start()].count('\n') + 1
        
        # 获取代码块后的内容
        content_after = content[match.end():]
        
        code_block = CodeBlock(file_path, language, code, line_number)
        code_block.check_has_comments()
        code_block.check_has_explanation(content_after)
        
        code_blocks.append(code_block)
    
    return code_blocks


def scan_all_code_examples(docs_dir: Path) -> Dict[str, List[CodeBlock]]:
    """扫描所有文档中的代码示例"""
    all_code_blocks = {}
    
    # 扫描中文文档
    zh_dir = docs_dir / 'zh'
    if zh_dir.exists():
        for md_file in zh_dir.rglob('*.md'):
            code_blocks = extract_code_blocks(md_file)
            if code_blocks:
                relative_path = md_file.relative_to(docs_dir)
                all_code_blocks[str(relative_path)] = code_blocks
    
    # 扫描英文文档
    en_dir = docs_dir / 'en'
    if en_dir.exists():
        for md_file in en_dir.rglob('*.md'):
            code_blocks = extract_code_blocks(md_file)
            if code_blocks:
                relative_path = md_file.relative_to(docs_dir)
                all_code_blocks[str(relative_path)] = code_blocks
    
    return all_code_blocks


def generate_report(all_code_blocks: Dict[str, List[CodeBlock]]) -> str:
    """生成代码示例扫描报告"""
    report_lines = []
    report_lines.append("# 代码示例扫描报告")
    report_lines.append("")
    report_lines.append(f"扫描时间: 2026-02-09")
    report_lines.append("")
    
    # 统计信息
    total_files = len(all_code_blocks)
    total_blocks = sum(len(blocks) for blocks in all_code_blocks.values())
    blocks_with_comments = sum(
        1 for blocks in all_code_blocks.values()
        for block in blocks if block.has_comments
    )
    blocks_with_explanation = sum(
        1 for blocks in all_code_blocks.values()
        for block in blocks if block.has_explanation
    )
    blocks_need_attention = sum(
        1 for blocks in all_code_blocks.values()
        for block in blocks if not (block.has_comments or block.has_explanation)
    )
    
    report_lines.append("## 统计摘要")
    report_lines.append("")
    report_lines.append(f"- 扫描文件数: {total_files}")
    report_lines.append(f"- 代码块总数: {total_blocks}")
    report_lines.append(f"- 包含注释的代码块: {blocks_with_comments} ({blocks_with_comments/total_blocks*100:.1f}%)")
    report_lines.append(f"- 包含说明的代码块: {blocks_with_explanation} ({blocks_with_explanation/total_blocks*100:.1f}%)")
    report_lines.append(f"- **需要补充说明的代码块: {blocks_need_attention} ({blocks_need_attention/total_blocks*100:.1f}%)**")
    report_lines.append("")
    
    # 需要补充说明的代码块清单
    report_lines.append("## 需要补充说明的代码块清单")
    report_lines.append("")
    report_lines.append("以下代码块既没有内部注释，也没有后续说明文本，需要补充：")
    report_lines.append("")
    
    need_attention_count = 0
    for file_path, blocks in sorted(all_code_blocks.items()):
        file_needs_attention = [
            block for block in blocks
            if not (block.has_comments or block.has_explanation)
        ]
        
        if file_needs_attention:
            report_lines.append(f"### {file_path}")
            report_lines.append("")
            
            for block in file_needs_attention:
                need_attention_count += 1
                report_lines.append(f"**代码块 #{need_attention_count}** (行 {block.line_number}, 语言: {block.language})")
                report_lines.append("")
                report_lines.append("```" + block.language)
                # 只显示前10行
                code_lines = block.code.split('\n')[:10]
                report_lines.append('\n'.join(code_lines))
                if len(block.code.split('\n')) > 10:
                    report_lines.append("... (省略)")
                report_lines.append("```")
                report_lines.append("")
                report_lines.append("**建议**: 添加代码注释或在代码块后添加说明文本")
                report_lines.append("")
    
    if need_attention_count == 0:
        report_lines.append("✅ 所有代码块都有适当的注释或说明！")
        report_lines.append("")
    
    # 良好示例
    report_lines.append("## 良好示例")
    report_lines.append("")
    report_lines.append("以下是包含良好注释或说明的代码块示例：")
    report_lines.append("")
    
    good_examples_count = 0
    for file_path, blocks in sorted(all_code_blocks.items()):
        good_blocks = [
            block for block in blocks
            if block.has_comments or block.has_explanation
        ]
        
        if good_blocks and good_examples_count < 5:  # 只显示5个示例
            for block in good_blocks[:2]:  # 每个文件最多2个示例
                if good_examples_count >= 5:
                    break
                
                good_examples_count += 1
                report_lines.append(f"### 示例 {good_examples_count}: {file_path} (行 {block.line_number})")
                report_lines.append("")
                
                if block.has_comments:
                    report_lines.append("✅ **包含代码注释**")
                if block.has_explanation:
                    report_lines.append("✅ **包含说明文本**")
                    if block.explanation_text:
                        report_lines.append(f"> {block.explanation_text[:100]}...")
                
                report_lines.append("")
    
    return '\n'.join(report_lines)


def main():
    """主函数"""
    docs_dir = Path('docs')
    
    if not docs_dir.exists():
        print(f"错误: 文档目录 {docs_dir} 不存在")
        return 1
    
    print("开始扫描代码示例...")
    all_code_blocks = scan_all_code_examples(docs_dir)
    
    print(f"扫描完成，共发现 {len(all_code_blocks)} 个包含代码块的文件")
    
    print("生成报告...")
    report = generate_report(all_code_blocks)
    
    # 保存报告
    report_path = Path('scripts/code_examples_scan_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存到: {report_path}")
    
    # 同时输出到控制台
    print("\n" + "="*80)
    print(report)
    print("="*80)
    
    return 0


if __name__ == '__main__':
    exit(main())
