#!/usr/bin/env python3
"""
外部链接检查脚本

检查文档中的外部链接有效性，生成链接检查报告。
用于定期验证参考资料和外部资源的可访问性。

需求: 12.5
"""

import re
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
from urllib.parse import urlparse
import time

try:
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.util.retry import Retry
except ImportError:
    print("错误: 需要安装 requests 库")
    print("请运行: pip install requests")
    sys.exit(1)


class LinkChecker:
    """外部链接检查器"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        初始化链接检查器
        
        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = self._create_session()
        self.checked_urls = {}  # 缓存已检查的URL
        
    def _create_session(self) -> requests.Session:
        """创建带重试机制的会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置User-Agent避免被某些网站拒绝
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; LinkChecker/1.0)'
        })
        
        return session
    
    def check_url(self, url: str) -> Tuple[int, str]:
        """
        检查单个URL的有效性
        
        Args:
            url: 要检查的URL
            
        Returns:
            (状态码, 错误信息) 元组
        """
        # 检查缓存
        if url in self.checked_urls:
            return self.checked_urls[url]
        
        try:
            # 首先尝试HEAD请求（更快）
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            
            # 某些服务器不支持HEAD，尝试GET
            if response.status_code == 405:
                response = self.session.get(url, timeout=self.timeout, allow_redirects=True)
            
            result = (response.status_code, "")
            
        except requests.exceptions.Timeout:
            result = (0, "超时")
        except requests.exceptions.ConnectionError:
            result = (0, "连接错误")
        except requests.exceptions.TooManyRedirects:
            result = (0, "重定向过多")
        except requests.exceptions.RequestException as e:
            result = (0, f"请求错误: {str(e)}")
        except Exception as e:
            result = (0, f"未知错误: {str(e)}")
        
        # 缓存结果
        self.checked_urls[url] = result
        return result
    
    def extract_links_from_file(self, file_path: Path) -> List[Dict]:
        """
        从Markdown文件中提取外部链接
        
        Args:
            file_path: Markdown文件路径
            
        Returns:
            链接信息列表
        """
        links = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 匹配Markdown链接格式: [text](url)
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            
            for match in re.finditer(link_pattern, content):
                text = match.group(1)
                url = match.group(2)
                
                # 只处理外部链接（http/https）
                if url.startswith('http://') or url.startswith('https://'):
                    links.append({
                        'file': str(file_path),
                        'text': text,
                        'url': url,
                        'line': content[:match.start()].count('\n') + 1
                    })
        
        except Exception as e:
            print(f"警告: 读取文件 {file_path} 失败: {e}")
        
        return links
    
    def check_links_in_directory(self, directory: Path, pattern: str = "**/*.md") -> List[Dict]:
        """
        检查目录中所有Markdown文件的外部链接
        
        Args:
            directory: 要检查的目录
            pattern: 文件匹配模式
            
        Returns:
            检查结果列表
        """
        results = []
        
        # 查找所有Markdown文件
        md_files = list(directory.glob(pattern))
        
        print(f"找到 {len(md_files)} 个Markdown文件")
        
        # 提取所有链接
        all_links = []
        for md_file in md_files:
            links = self.extract_links_from_file(md_file)
            all_links.extend(links)
        
        print(f"找到 {len(all_links)} 个外部链接")
        
        # 获取唯一URL列表
        unique_urls = list(set(link['url'] for link in all_links))
        print(f"检查 {len(unique_urls)} 个唯一URL...")
        
        # 检查每个链接
        for i, link in enumerate(all_links, 1):
            url = link['url']
            
            # 显示进度
            if i % 10 == 0 or i == len(all_links):
                print(f"进度: {i}/{len(all_links)}")
            
            # 检查URL
            status_code, error_msg = self.check_url(url)
            
            result = {
                'file': link['file'],
                'line': link['line'],
                'text': link['text'],
                'url': url,
                'status_code': status_code,
                'error': error_msg,
                'is_valid': 200 <= status_code < 400
            }
            
            results.append(result)
            
            # 避免请求过快
            time.sleep(0.1)
        
        return results


class ReportGenerator:
    """报告生成器"""
    
    @staticmethod
    def generate_markdown_report(results: List[Dict], output_file: Path):
        """
        生成Markdown格式的报告
        
        Args:
            results: 检查结果列表
            output_file: 输出文件路径
        """
        # 统计信息
        total_links = len(results)
        valid_links = sum(1 for r in results if r['is_valid'])
        invalid_links = total_links - valid_links
        
        # 按状态分组
        failed_links = [r for r in results if not r['is_valid']]
        
        # 生成报告
        report = []
        report.append("# 外部链接检查报告\n")
        report.append(f"**检查日期**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append("")
        
        # 摘要
        report.append("## 摘要\n")
        report.append(f"- 总链接数: {total_links}")
        report.append(f"- 有效链接: {valid_links}")
        report.append(f"- 失效链接: {invalid_links}")
        report.append(f"- 有效率: {(valid_links/total_links*100):.1f}%\n")
        
        # 失效链接详情
        if failed_links:
            report.append("## 失效链接\n")
            
            for link in failed_links:
                report.append(f"### {link['url']}\n")
                report.append(f"- **文件**: {link['file']}")
                report.append(f"- **行号**: {link['line']}")
                report.append(f"- **链接文本**: {link['text']}")
                report.append(f"- **状态码**: {link['status_code']}")
                if link['error']:
                    report.append(f"- **错误**: {link['error']}")
                report.append("")
        else:
            report.append("## 结果\n")
            report.append("✅ 所有外部链接都有效！\n")
        
        # 按文件分组的统计
        report.append("## 按文件统计\n")
        
        files_stats = {}
        for result in results:
            file_path = result['file']
            if file_path not in files_stats:
                files_stats[file_path] = {'total': 0, 'valid': 0, 'invalid': 0}
            
            files_stats[file_path]['total'] += 1
            if result['is_valid']:
                files_stats[file_path]['valid'] += 1
            else:
                files_stats[file_path]['invalid'] += 1
        
        report.append("| 文件 | 总数 | 有效 | 失效 |")
        report.append("|------|------|------|------|")
        
        for file_path, stats in sorted(files_stats.items()):
            report.append(f"| {file_path} | {stats['total']} | {stats['valid']} | {stats['invalid']} |")
        
        report.append("")
        
        # 写入文件
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        print(f"\n报告已生成: {output_file}")
    
    @staticmethod
    def generate_json_report(results: List[Dict], output_file: Path):
        """
        生成JSON格式的报告
        
        Args:
            results: 检查结果列表
            output_file: 输出文件路径
        """
        import json
        
        report = {
            'check_date': datetime.now().isoformat(),
            'summary': {
                'total_links': len(results),
                'valid_links': sum(1 for r in results if r['is_valid']),
                'invalid_links': sum(1 for r in results if not r['is_valid'])
            },
            'results': results
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"JSON报告已生成: {output_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='检查Markdown文档中的外部链接有效性'
    )
    parser.add_argument(
        'directory',
        type=str,
        nargs='?',
        default='docs',
        help='要检查的目录（默认: docs）'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='link-check-report.md',
        help='输出报告文件名（默认: link-check-report.md）'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='同时生成JSON格式报告'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=10,
        help='请求超时时间（秒，默认: 10）'
    )
    parser.add_argument(
        '--retries',
        type=int,
        default=3,
        help='最大重试次数（默认: 3）'
    )
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    directory = Path(args.directory)
    if not directory.exists():
        print(f"错误: 目录不存在: {directory}")
        sys.exit(1)
    
    print(f"开始检查目录: {directory}")
    print(f"超时时间: {args.timeout}秒")
    print(f"最大重试: {args.retries}次\n")
    
    # 创建链接检查器
    checker = LinkChecker(timeout=args.timeout, max_retries=args.retries)
    
    # 检查链接
    results = checker.check_links_in_directory(directory)
    
    if not results:
        print("\n未找到外部链接")
        return
    
    # 生成报告
    print("\n生成报告...")
    
    output_file = Path(args.output)
    ReportGenerator.generate_markdown_report(results, output_file)
    
    if args.json:
        json_file = output_file.with_suffix('.json')
        ReportGenerator.generate_json_report(results, json_file)
    
    # 显示摘要
    total = len(results)
    valid = sum(1 for r in results if r['is_valid'])
    invalid = total - valid
    
    print(f"\n检查完成!")
    print(f"总链接数: {total}")
    print(f"有效链接: {valid}")
    print(f"失效链接: {invalid}")
    
    # 如果有失效链接，返回非零退出码
    if invalid > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
