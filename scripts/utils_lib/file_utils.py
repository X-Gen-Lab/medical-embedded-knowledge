"""文件操作工具"""

from pathlib import Path
from typing import List


class FileUtils:
    """文件操作工具类"""
    
    @staticmethod
    def read_file(file_path: Path, encoding: str = 'utf-8') -> str:
        """读取文件内容"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except Exception as e:
            print(f"错误: 读取文件 {file_path} 失败: {e}")
            return ""
    
    @staticmethod
    def write_file(file_path: Path, content: str, encoding: str = 'utf-8') -> bool:
        """写入文件内容"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"错误: 写入文件 {file_path} 失败: {e}")
            return False
    
    @staticmethod
    def find_files(directory: Path, pattern: str = "**/*.md") -> List[Path]:
        """查找匹配模式的文件"""
        try:
            return list(directory.glob(pattern))
        except Exception as e:
            print(f"错误: 查找文件失败: {e}")
            return []
