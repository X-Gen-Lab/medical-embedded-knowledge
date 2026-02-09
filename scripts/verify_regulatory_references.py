#!/usr/bin/env python3
"""
验证法规标准模块的参考文献
"""

import re
from pathlib import Path

def main():
    docs_dir = Path('docs/zh/regulatory-standards')
    
    print('法规标准模块参考文献详细统计:\n')
    print(f"{'文件':<50} {'参考文献数量':>10}")
    print('='*62)
    
    total_files = 0
    compliant_files = 0
    
    for standard_dir in sorted(docs_dir.iterdir()):
        if standard_dir.is_dir():
            print(f'\n{standard_dir.name}:')
            for md_file in sorted(standard_dir.glob('*.md')):
                total_files += 1
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 查找参考文献部分
                ref_match = re.search(r'## 参考文献\n\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
                if not ref_match:
                    ref_match = re.search(r'## 参考资料\n\n(.*?)(?=\n##|\Z)', content, re.DOTALL)
                
                if ref_match:
                    ref_section = ref_match.group(1)
                    ref_count = len(re.findall(r'^\d+\.', ref_section, re.MULTILINE))
                    status = '✅' if ref_count >= 3 else '❌'
                    if ref_count >= 3:
                        compliant_files += 1
                    print(f'  {md_file.name:<46} {ref_count:>8} {status}')
                else:
                    print(f'  {md_file.name:<46} {"无":>8} ❌')
    
    print(f'\n{"="*62}')
    print(f'总计: {total_files} 个文件')
    print(f'符合要求 (≥3个参考文献): {compliant_files} 个文件 ({compliant_files/total_files*100:.1f}%)')
    print(f'不符合要求: {total_files - compliant_files} 个文件')

if __name__ == '__main__':
    main()
