"""报告生成工具"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime
from .file_utils import FileUtils


class ReportUtils:
    """报告生成工具类"""
    
    @staticmethod
    def generate_header(title: str, width: int = 80) -> str:
        """生成报告头部"""
        lines = []
        lines.append("=" * width)
        lines.append(title)
        lines.append("=" * width)
        lines.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        return "\n".join(lines)
    
    @staticmethod
    def generate_summary(stats: Dict[str, int]) -> str:
        """生成统计摘要"""
        lines = ["\n## 统计摘要\n"]
        for key, value in stats.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    @staticmethod
    def generate_table(headers: List[str], rows: List[List[str]]) -> str:
        """生成Markdown表格"""
        lines = []
        # 表头
        lines.append("| " + " | ".join(headers) + " |")
        # 分隔线
        lines.append("|" + "|".join(["---" for _ in headers]) + "|")
        # 数据行
        for row in rows:
            lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
        return "\n".join(lines)
    
    @staticmethod
    def save_report(file_path: Path, content: str) -> bool:
        """保存报告文件"""
        return FileUtils.write_file(file_path, content)
