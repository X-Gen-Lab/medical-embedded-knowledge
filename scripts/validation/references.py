#!/usr/bin/env python3
"""
参考文献验证工具
验证所有模块的参考文献完整性

支持的模块类型：
- regulatory: 法规标准模块
- software-engineering: 软件工程模块  
- technical: 技术知识模块
- all: 所有模块
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class ReferenceValidator:
    """参考文献验证器"""
    
    def __init__(self, min_references: int = 3):
        self.min_references = min_references
        self.results = []
    
    def count_references(self, content: str) -> int:
        """统计参考文献数量"""
        # 查找参考文献部分
        ref_match = re.search(r'## 参考文献\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        if not ref_match:
            ref_match = re.search(r'## 参考资料\s*\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
        
        if not ref_match:
            return 0
        
        ref_section = ref_match.group(1)
        # 统计编号列表项
        ref_items = re.findall(r'^\d+\.\s+', ref_section, re.MULTILINE)
        return len(ref_items)
    
    def has_reference_section(self, content: str) -> bool:
        """检查是否有参考文献部分"""
        return '## 参考文献' in content or '## 参考资料' in content
    
    def validate_file(self, file_path: Path, category: str) -> Dict:
        """验证单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_section = self.has_reference_section(content)
            ref_count = self.count_references(content)
            is_valid = has_section and ref_count >= self.min_references
            
            result = {
                'file': str(file_path),
                'category': category,
                'has_section': has_section,
                'count': ref_count,
                'valid': is_valid
            }
            
            self.results.append(result)
            return result
        
        except Exception as e:
            print(f"错误: 读取文件 {file_path} 失败: {e}")
            return None
    
    def validate_regulatory(self) -> List[Dict]:
        """验证法规标准模块"""
        docs_dir = Path('docs/zh/regulatory-standards')
        results = []
        
        for standard_dir in sorted(docs_dir.iterdir()):
            if standard_dir.is_dir():
                for md_file in sorted(standard_dir.glob('*.md')):
                    if md_file.name != 'index.md':
                        result = self.validate_file(md_file, 'regulatory')
                        if result:
                            results.append(result)
        
        return results
    
    def validate_software_engineering(self) -> List[Dict]:
        """验证软件工程模块"""
        docs_dir = Path('docs/zh/software-engineering')
        results = []
        
        for md_file in docs_dir.rglob('*.md'):
            if md_file.name != 'index.md':
                result = self.validate_file(md_file, 'software-engineering')
                if result:
                    results.append(result)
        
        return results
    
    def validate_technical(self) -> List[Dict]:
        """验证技术知识模块"""
        docs_dir = Path('docs/zh/technical-knowledge')
        results = []
        
        for md_file in docs_dir.rglob('*.md'):
            if md_file.name != 'index.md':
                result = self.validate_file(md_file, 'technical')
                if result:
                    results.append(result)
        
        return results
    
    def validate_all(self) -> List[Dict]:
        """验证所有模块"""
        self.results = []
        self.validate_regulatory()
        self.validate_software_engineering()
        self.validate_technical()
        return self.results
    
    def generate_report(self) -> str:
        """生成验证报告"""
        if not self.results:
            return "没有验证结果"
        
        lines = []
        lines.append("=" * 80)
        lines.append("参考文献验证报告")
        lines.append("=" * 80)
        lines.append("")
        
        # 按类别分组
        by_category = {}
        for result in self.results:
            category = result['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)
        
        # 统计信息
        total = len(self.results)
        valid = sum(1 for r in self.results if r['valid'])
        no_section = sum(1 for r in self.results if not r['has_section'])
        insufficient = sum(1 for r in self.results if r['has_section'] and not r['valid'])
        
        lines.append(f"总文件数: {total}")
        lines.append(f"符合要求 (≥{self.min_references}个参考文献): {valid} ({valid/total*100:.1f}%)")
        lines.append(f"缺少参考文献部分: {no_section}")
        lines.append(f"参考文献不足: {insufficient}")
        lines.append("")
        
        # 按类别显示详细结果
        category_names = {
            'regulatory': '法规标准模块',
            'software-engineering': '软件工程模块',
            'technical': '技术知识模块'
        }
        
        for category, results in sorted(by_category.items()):
            lines.append("")
            lines.append("=" * 80)
            lines.append(f"{category_names.get(category, category)}")
            lines.append("=" * 80)
            lines.append("")
            
            # 按子目录分组
            by_subdir = {}
            for result in results:
                file_path = Path(result['file'])
                parts = file_path.parts
                if len(parts) >= 4:
                    subdir = parts[3]  # docs/zh/category/subdir/file.md
                else:
                    subdir = "其他"
                
                if subdir not in by_subdir:
                    by_subdir[subdir] = []
                by_subdir[subdir].append(result)
            
            for subdir, subdir_results in sorted(by_subdir.items()):
                lines.append(f"\n{subdir}/")
                lines.append("-" * 80)
                
                for result in sorted(subdir_results, key=lambda x: x['file']):
                    file_name = Path(result['file']).name
                    count = result['count']
                    
                    if not result['has_section']:
                        status = "✗ 缺少参考文献部分"
                    elif result['valid']:
                        status = f"✓ {count} 个参考文献"
                    else:
                        status = f"✗ {count} 个参考文献 (不足{self.min_references}个)"
                    
                    lines.append(f"  {file_name:45} {status}")
        
        lines.append("")
        lines.append("=" * 80)
        
        if valid == total:
            lines.append("✓ 所有文件的参考文献都符合要求")
        else:
            lines.append(f"✗ {total - valid} 个文件的参考文献不符合要求")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='验证参考文献完整性')
    parser.add_argument(
        'module',
        nargs='?',
        default='all',
        choices=['all', 'regulatory', 'software-engineering', 'technical'],
        help='要验证的模块类型 (默认: all)'
    )
    parser.add_argument(
        '--min-refs',
        type=int,
        default=3,
        help='最少参考文献数量 (默认: 3)'
    )
    
    args = parser.parse_args()
    
    validator = ReferenceValidator(min_references=args.min_refs)
    
    # 根据参数验证指定模块
    if args.module == 'all':
        validator.validate_all()
    elif args.module == 'regulatory':
        validator.validate_regulatory()
    elif args.module == 'software-engineering':
        validator.validate_software_engineering()
    elif args.module == 'technical':
        validator.validate_technical()
    
    # 生成并打印报告
    report = validator.generate_report()
    print(report)
    
    # 返回退出码
    valid_count = sum(1 for r in validator.results if r['valid'])
    total_count = len(validator.results)
    
    if valid_count == total_count:
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
