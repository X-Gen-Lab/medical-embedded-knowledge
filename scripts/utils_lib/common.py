"""通用辅助函数"""

import sys
import io


def setup_utf8_output():
    """设置UTF-8输出编码"""
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def print_progress(current: int, total: int, prefix: str = "进度"):
    """打印进度"""
    percentage = (current / total) * 100 if total > 0 else 0
    print(f"\r{prefix}: {current}/{total} ({percentage:.1f}%)", end='', flush=True)
    if current == total:
        print()  # 换行
