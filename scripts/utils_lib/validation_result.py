"""验证结果管理"""

from typing import Dict
from .report_utils import ReportUtils


class ValidationResult:
    """验证结果类"""
    
    def __init__(self, name: str):
        self.name = name
        self.errors = []
        self.warnings = []
        self.info = []
        self.stats = {}
    
    def add_error(self, message: str, file_path: str = "", line: int = 0):
        """添加错误"""
        self.errors.append({
            'message': message,
            'file': file_path,
            'line': line
        })
    
    def add_warning(self, message: str, file_path: str = "", line: int = 0):
        """添加警告"""
        self.warnings.append({
            'message': message,
            'file': file_path,
            'line': line
        })
    
    def add_info(self, message: str):
        """添加信息"""
        self.info.append(message)
    
    def set_stat(self, key: str, value: int):
        """设置统计信息"""
        self.stats[key] = value
    
    def is_success(self) -> bool:
        """是否验证成功"""
        return len(self.errors) == 0
    
    def generate_report(self) -> str:
        """生成报告"""
        lines = []
        lines.append(ReportUtils.generate_header(f"{self.name} - 验证报告"))
        
        # 统计信息
        if self.stats:
            lines.append(ReportUtils.generate_summary(self.stats))
        
        # 错误
        if self.errors:
            lines.append(f"\n## 错误 ({len(self.errors)}个)\n")
            for i, error in enumerate(self.errors, 1):
                lines.append(f"### 错误 {i}")
                lines.append(f"- 文件: {error['file']}")
                if error['line']:
                    lines.append(f"- 行号: {error['line']}")
                lines.append(f"- 消息: {error['message']}\n")
        
        # 警告
        if self.warnings:
            lines.append(f"\n## 警告 ({len(self.warnings)}个)\n")
            for i, warning in enumerate(self.warnings, 1):
                lines.append(f"### 警告 {i}")
                lines.append(f"- 文件: {warning['file']}")
                if warning['line']:
                    lines.append(f"- 行号: {warning['line']}")
                lines.append(f"- 消息: {warning['message']}\n")
        
        # 结果
        lines.append("\n" + "=" * 80)
        if self.is_success():
            lines.append("✓ 验证通过")
        else:
            lines.append(f"✗ 验证失败 - 发现 {len(self.errors)} 个错误")
        lines.append("=" * 80)
        
        return "\n".join(lines)
