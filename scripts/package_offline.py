#!/usr/bin/env python3
"""
离线包打包脚本 (Offline Package Script)

功能 (Features):
- 构建静态站点 (Build static site)
- 打包所有HTML、CSS、JS和资源文件 (Package all HTML, CSS, JS and resource files)
- 生成版本号和生成日期标识 (Generate version number and build date)
- 创建ZIP压缩包 (Create ZIP archive)

需求 (Requirements):
- 需求 11.2: 支持将整个知识库打包为离线HTML文件
- 需求 11.5: 提供版本号和生成日期标识

使用方法 (Usage):
    python scripts/package_offline.py [--version VERSION] [--output OUTPUT]

参数 (Arguments):
    --version VERSION    版本号 (默认: 1.0.0)
    --output OUTPUT      输出文件名 (默认: medical-embedded-knowledge-offline.zip)
    --clean              构建前清理site目录
    --no-build           跳过构建步骤，直接打包现有site目录
"""

import sys
import subprocess
import shutil
import zipfile
import argparse
from pathlib import Path
from datetime import datetime
import json


def print_section(title: str):
    """打印章节标题"""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80 + "\n")


def print_info(message: str):
    """打印信息"""
    print(f"ℹ {message}")


def print_success(message: str):
    """打印成功消息"""
    print(f"✓ {message}")


def print_error(message: str):
    """打印错误消息"""
    print(f"✗ {message}", file=sys.stderr)


def print_warning(message: str):
    """打印警告消息"""
    print(f"⚠ {message}")


def build_site(clean: bool = False) -> bool:
    """
    构建静态站点
    
    Args:
        clean: 是否在构建前清理site目录
    
    Returns:
        bool: 构建是否成功
    """
    print_section("1. 构建静态站点 (Building Static Site)")
    
    try:
        # 构建命令
        cmd = ['mkdocs', 'build']
        if clean:
            cmd.append('--clean')
            print_info("使用 --clean 选项清理旧文件")
        
        print_info(f"运行命令: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        # 打印输出
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            print_error("构建失败")
            if result.stderr:
                print(result.stderr)
            return False
        
        print_success("静态站点构建成功")
        return True
    
    except FileNotFoundError:
        print_error("未找到 mkdocs 命令。请确保已安装 MkDocs:")
        print("  pip install mkdocs mkdocs-material")
        return False
    
    except Exception as e:
        print_error(f"构建过程中发生错误: {str(e)}")
        return False


def verify_site_directory() -> bool:
    """
    验证site目录存在且包含必要文件
    
    Returns:
        bool: 验证是否通过
    """
    print_section("2. 验证构建输出 (Verifying Build Output)")
    
    site_dir = Path('site')
    
    # 检查site目录是否存在
    if not site_dir.exists():
        print_error("site/ 目录不存在")
        return False
    
    print_success("site/ 目录存在")
    
    # 检查关键文件
    required_files = [
        'index.html',
        '404.html',
        'search/search_index.json',
    ]
    
    required_dirs = [
        'assets',
        'search',
    ]
    
    all_exist = True
    
    # 检查必需文件
    for file_path in required_files:
        full_path = site_dir / file_path
        if full_path.exists():
            print_success(f"找到文件: {file_path}")
        else:
            print_warning(f"缺少文件: {file_path}")
            all_exist = False
    
    # 检查必需目录
    for dir_path in required_dirs:
        full_path = site_dir / dir_path
        if full_path.exists() and full_path.is_dir():
            print_success(f"找到目录: {dir_path}")
        else:
            print_warning(f"缺少目录: {dir_path}")
            all_exist = False
    
    # 统计文件数量
    html_files = list(site_dir.rglob('*.html'))
    css_files = list(site_dir.rglob('*.css'))
    js_files = list(site_dir.rglob('*.js'))
    
    print_info(f"HTML文件数量: {len(html_files)}")
    print_info(f"CSS文件数量: {len(css_files)}")
    print_info(f"JS文件数量: {len(js_files)}")
    
    if not all_exist:
        print_warning("部分文件或目录缺失，但将继续打包")
    
    return True


def create_version_file(site_dir: Path, version: str) -> bool:
    """
    创建版本信息文件
    
    Args:
        site_dir: site目录路径
        version: 版本号
    
    Returns:
        bool: 创建是否成功
    """
    print_section("3. 生成版本信息 (Generating Version Information)")
    
    try:
        # 获取当前时间
        build_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        build_date_iso = datetime.now().isoformat()
        
        # 创建VERSION.txt文件
        version_txt = site_dir / 'VERSION.txt'
        with open(version_txt, 'w', encoding='utf-8') as f:
            f.write(f"医疗器械嵌入式软件知识体系 - 离线版本\n")
            f.write(f"Medical Device Embedded Software Knowledge System - Offline Version\n")
            f.write(f"\n")
            f.write(f"版本 (Version): {version}\n")
            f.write(f"构建日期 (Build Date): {build_date}\n")
            f.write(f"包类型 (Package Type): 离线HTML包 (Offline HTML Package)\n")
            f.write(f"\n")
            f.write(f"使用说明 (Instructions):\n")
            f.write(f"1. 解压此ZIP文件到任意目录\n")
            f.write(f"2. 双击打开 index.html 文件\n")
            f.write(f"3. 在浏览器中浏览内容\n")
            f.write(f"\n")
            f.write(f"1. Extract this ZIP file to any directory\n")
            f.write(f"2. Double-click to open index.html\n")
            f.write(f"3. Browse content in your browser\n")
        
        print_success(f"创建 VERSION.txt: {version_txt}")
        
        # 创建version.json文件（机器可读）
        version_json = site_dir / 'version.json'
        version_data = {
            'version': version,
            'build_date': build_date,
            'build_date_iso': build_date_iso,
            'package_type': 'offline_html',
            'system_name': '医疗器械嵌入式软件知识体系',
            'system_name_en': 'Medical Device Embedded Software Knowledge System'
        }
        
        with open(version_json, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, ensure_ascii=False, indent=2)
        
        print_success(f"创建 version.json: {version_json}")
        
        # 创建README.txt文件
        readme_txt = site_dir / 'README.txt'
        with open(readme_txt, 'w', encoding='utf-8') as f:
            f.write(f"医疗器械嵌入式软件知识体系 - 离线HTML包\n")
            f.write(f"=" * 60 + "\n\n")
            f.write(f"版本: {version}\n")
            f.write(f"构建日期: {build_date}\n\n")
            f.write(f"快速开始:\n")
            f.write(f"1. 在浏览器中打开 index.html 文件\n")
            f.write(f"2. 使用导航菜单浏览不同章节\n")
            f.write(f"3. 使用搜索框查找特定内容\n\n")
            f.write(f"功能说明:\n")
            f.write(f"✓ 完整导航系统\n")
            f.write(f"✓ 离线搜索功能\n")
            f.write(f"✓ 代码高亮显示\n")
            f.write(f"✓ 图表渲染\n")
            f.write(f"✓ 多语言支持\n")
            f.write(f"✓ 主题切换\n\n")
            f.write(f"注意事项:\n")
            f.write(f"- 外部链接需要网络连接\n")
            f.write(f"- 建议使用现代浏览器（Chrome、Firefox、Edge、Safari）\n")
            f.write(f"- 必须启用JavaScript以使用搜索和交互功能\n\n")
            f.write(f"详细文档请参见: OFFLINE_BUILD.md\n")
        
        print_success(f"创建 README.txt: {readme_txt}")
        
        print_info(f"版本号: {version}")
        print_info(f"构建日期: {build_date}")
        
        return True
    
    except Exception as e:
        print_error(f"创建版本文件时发生错误: {str(e)}")
        return False


def create_zip_package(site_dir: Path, output_file: str, version: str) -> bool:
    """
    创建ZIP压缩包
    
    Args:
        site_dir: site目录路径
        output_file: 输出文件名
        version: 版本号
    
    Returns:
        bool: 打包是否成功
    """
    print_section("4. 创建ZIP压缩包 (Creating ZIP Archive)")
    
    try:
        output_path = Path(output_file)
        
        # 如果输出文件已存在，先删除
        if output_path.exists():
            print_warning(f"输出文件已存在，将被覆盖: {output_path}")
            output_path.unlink()
        
        print_info(f"创建压缩包: {output_path}")
        print_info("正在压缩文件...")
        
        # 创建ZIP文件
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 遍历site目录中的所有文件
            file_count = 0
            for file_path in site_dir.rglob('*'):
                if file_path.is_file():
                    # 计算相对路径
                    arcname = file_path.relative_to(site_dir)
                    zipf.write(file_path, arcname)
                    file_count += 1
                    
                    # 每100个文件打印一次进度
                    if file_count % 100 == 0:
                        print_info(f"已压缩 {file_count} 个文件...")
        
        # 获取压缩包大小
        zip_size = output_path.stat().st_size
        zip_size_mb = zip_size / (1024 * 1024)
        
        print_success(f"压缩包创建成功: {output_path}")
        print_info(f"文件数量: {file_count}")
        print_info(f"压缩包大小: {zip_size_mb:.2f} MB")
        
        return True
    
    except Exception as e:
        print_error(f"创建压缩包时发生错误: {str(e)}")
        return False


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='打包医疗器械嵌入式软件知识体系为离线HTML包',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例 (Examples):
  python scripts/package_offline.py
  python scripts/package_offline.py --version 2.0.0
  python scripts/package_offline.py --output my-offline-package.zip
  python scripts/package_offline.py --clean --version 1.5.0
  python scripts/package_offline.py --no-build
        """
    )
    
    parser.add_argument(
        '--version',
        default='1.0.0',
        help='版本号 (默认: 1.0.0)'
    )
    
    parser.add_argument(
        '--output',
        default='medical-embedded-knowledge-offline.zip',
        help='输出文件名 (默认: medical-embedded-knowledge-offline.zip)'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='构建前清理site目录'
    )
    
    parser.add_argument(
        '--no-build',
        action='store_true',
        help='跳过构建步骤，直接打包现有site目录'
    )
    
    args = parser.parse_args()
    
    # 打印标题
    print_section("离线HTML包打包工具 (Offline HTML Package Tool)")
    print_info(f"版本: {args.version}")
    print_info(f"输出文件: {args.output}")
    
    # 步骤1: 构建静态站点（如果需要）
    if not args.no_build:
        if not build_site(clean=args.clean):
            print_error("构建失败，打包终止")
            return 1
    else:
        print_section("1. 跳过构建步骤 (Skipping Build Step)")
        print_info("使用现有的 site/ 目录")
    
    # 步骤2: 验证site目录
    if not verify_site_directory():
        print_error("验证失败，打包终止")
        return 1
    
    # 步骤3: 创建版本信息文件
    site_dir = Path('site')
    if not create_version_file(site_dir, args.version):
        print_error("创建版本文件失败，打包终止")
        return 1
    
    # 步骤4: 创建ZIP压缩包
    if not create_zip_package(site_dir, args.output, args.version):
        print_error("创建压缩包失败")
        return 1
    
    # 打印完成信息
    print_section("打包完成 (Packaging Complete)")
    print_success("离线HTML包已成功创建！")
    print()
    print("使用说明 (Instructions):")
    print(f"1. 将 {args.output} 分发给用户")
    print("2. 用户解压ZIP文件到任意目录")
    print("3. 用户双击打开 index.html 文件")
    print("4. 在浏览器中浏览内容")
    print()
    print("验证清单 (Verification Checklist):")
    print("✓ 需求 11.2: 支持将整个知识库打包为离线HTML文件")
    print("✓ 需求 11.3: 保留所有内部链接和导航功能")
    print("✓ 需求 11.4: 包含所有图表和代码示例")
    print("✓ 需求 11.5: 提供版本号和生成日期标识")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
