"""路径处理工具"""

from pathlib import Path


class PathUtils:
    """路径处理工具类"""
    
    @staticmethod
    def is_external_link(url: str) -> bool:
        """判断是否为外部链接"""
        return url.startswith(('http://', 'https://', 'ftp://'))
    
    @staticmethod
    def is_anchor_link(url: str) -> bool:
        """判断是否为锚点链接"""
        return url.startswith('#')
    
    @staticmethod
    def normalize_path(path: str) -> str:
        """规范化路径"""
        # 移除尾部斜杠
        path = path.rstrip('/')
        # 统一使用正斜杠
        path = path.replace('\\', '/')
        return path
    
    @staticmethod
    def resolve_relative_path(base_path: Path, relative_path: str) -> Path:
        """解析相对路径"""
        if relative_path.startswith('/'):
            # 绝对路径（相对于docs根目录）
            return base_path / relative_path.lstrip('/')
        else:
            # 相对路径
            return (base_path.parent / relative_path).resolve()
