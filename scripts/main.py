#!/usr/bin/env python3
"""
医疗器械嵌入式软件知识体系 - 脚本工具主入口

统一的命令行接口，用于运行所有验证、修复和构建工具

使用方法:
    python scripts/main.py validate [type]    # 运行验证
    python scripts/main.py fix [type]         # 运行修复
    python scripts/main.py build [type]       # 运行构建
    python scripts/main.py check              # 运行检查点验证
"""

import sys
import subprocess
from pathlib import Path


class ScriptRunner:
    """脚本运行器"""
    
    def __init__(self):
        self.scripts_dir = Path(__file__).parent
    
    def run_script(self, script_path: str, args: list = None) -> int:
        """运行脚本"""
        cmd = ['python', str(self.scripts_dir / script_path)]
        if args:
            cmd.extend(args)
        
        result = subprocess.run(cmd, encoding='utf-8', errors='replace')
        return result.returncode
    
    def validate(self, validate_type: str = 'all') -> int:
        """运行验证"""
        if validate_type == 'all':
            # 运行所有验证并生成报告
            print("\n" + "=" * 80)
            print(" 运行所有验证")
            print("=" * 80)
            
            results = []
            
            # 1. 内部链接验证
            print("\n" + "=" * 80)
            print(" 1. 内部链接验证")
            print("=" * 80 + "\n")
            ret = self.run_script('validation/links.py')
            results.append(("内部链接验证", ret == 0))
            
            # 2. 元数据验证
            print("\n" + "=" * 80)
            print(" 2. 元数据验证")
            print("=" * 80 + "\n")
            ret = self.run_script('validation/metadata.py')
            results.append(("元数据验证", ret == 0))
            
            # 3. 内容结构验证
            print("\n" + "=" * 80)
            print(" 3. 内容结构验证")
            print("=" * 80 + "\n")
            ret = self.run_script('validation/structure.py')
            results.append(("内容结构验证", ret == 0))
            
            # 生成总结
            print("\n" + "=" * 80)
            print(" 验证总结")
            print("=" * 80)
            print()
            
            total = len(results)
            passed = sum(1 for _, success in results if success)
            
            print(f"总验证项: {total}")
            print(f"通过: {passed}")
            print(f"失败: {total - passed}")
            print()
            print("详细结果:")
            print("-" * 80)
            
            for name, success in results:
                status = "✓ 通过" if success else "✗ 失败"
                print(f"{name:30s} {status}")
            
            print("-" * 80)
            print()
            
            if passed == total:
                print("=" * 80)
                print(" ✓ 所有验证通过！")
                print("=" * 80)
                return 0
            else:
                print("=" * 80)
                print(f" ✗ {total - passed} 项验证失败")
                print("=" * 80)
                return 1
        
        elif validate_type == 'links':
            return self.run_script('validation/links.py')
        elif validate_type == 'external':
            return self.run_script('validation/external_links.py')
        elif validate_type == 'metadata':
            return self.run_script('validation/metadata.py')
        elif validate_type == 'structure':
            return self.run_script('validation/structure.py')
        elif validate_type == 'self-tests':
            return self.run_script('validation/self_tests.py')
        elif validate_type == 'references':
            return self.run_script('validation/references.py')
        elif validate_type == 'code':
            return self.run_script('validation/code_examples.py')
        else:
            print(f"未知的验证类型: {validate_type}")
            return 1
    
    def fix(self, fix_type: str = 'all') -> int:
        """运行修复"""
        if fix_type == 'all':
            # 依次运行所有修复
            self.run_script('fix/links.py', ['all'])
            return self.run_script('fix/index.py', ['add'])
        elif fix_type == 'links':
            return self.run_script('fix/links.py', ['all'])
        elif fix_type == 'spelling':
            return self.run_script('fix/links.py', ['spelling'])
        elif fix_type == 'prefix':
            return self.run_script('fix/links.py', ['prefix'])
        elif fix_type == 'index':
            return self.run_script('fix/index.py', ['add'])
        elif fix_type == 'index-check':
            return self.run_script('fix/index.py', ['check'])
        elif fix_type == 'index-fix':
            return self.run_script('fix/index.py', ['fix'])
        else:
            print(f"未知的修复类型: {fix_type}")
            return 1
    
    def build(self, build_type: str = 'all') -> int:
        """运行构建"""
        if build_type == 'all':
            self.run_script('build/render_paths.py')
            return self.run_script('build/package.py')
        elif build_type == 'paths':
            return self.run_script('build/render_paths.py')
        elif build_type == 'package':
            return self.run_script('build/package.py')
        else:
            print(f"未知的构建类型: {build_type}")
            return 1
    
    def check(self) -> int:
        """运行检查点验证（包含pytest测试）"""
        print("\n" + "=" * 80)
        print(" 检查点验证：内容完整性")
        print("=" * 80)
        
        results = []
        
        # 1. 元数据验证
        print("\n" + "=" * 80)
        print(" 1. 元数据验证")
        print("=" * 80 + "\n")
        ret = self.run_script('validation/metadata.py')
        results.append(("元数据验证", ret == 0))
        
        # 2. 链接验证（如果有pytest测试）
        print("\n" + "=" * 80)
        print(" 2. 链接验证")
        print("=" * 80 + "\n")
        
        # 尝试运行pytest测试
        import subprocess
        try:
            result = subprocess.run(
                ['pytest', 'tests/test_link_validation.py', '-v'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.stdout:
                print(result.stdout)
            results.append(("链接验证测试", result.returncode == 0))
        except FileNotFoundError:
            # pytest不可用，使用普通验证
            ret = self.run_script('validation/links.py')
            results.append(("链接验证", ret == 0))
        
        # 3. 内容质量测试（如果有pytest测试）
        print("\n" + "=" * 80)
        print(" 3. 内容质量测试")
        print("=" * 80 + "\n")
        
        try:
            result = subprocess.run(
                ['pytest', 'tests/test_content_properties.py', '-v'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            if result.stdout:
                print(result.stdout)
            results.append(("内容质量测试", result.returncode == 0))
        except FileNotFoundError:
            # pytest不可用，跳过
            print("pytest不可用，跳过内容质量测试")
        
        # 生成总结
        print("\n" + "=" * 80)
        print(" 验证总结")
        print("=" * 80)
        print()
        
        print("验证结果:")
        print("-" * 80)
        for name, success in results:
            status = "✓ 通过" if success else "✗ 失败"
            print(f"{name:30s} {status}")
        print("-" * 80)
        print()
        
        all_passed = all(success for _, success in results)
        
        if all_passed:
            print("=" * 80)
            print(" ✓ 所有验证通过！内容完整性检查点达成。")
            print("=" * 80)
            return 0
        else:
            print("=" * 80)
            print(" ✗ 部分验证失败。请修复上述问题后重新运行验证。")
            print("=" * 80)
            return 1
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
医疗器械嵌入式软件知识体系 - 脚本工具

使用方法:
    python scripts/main.py <command> [options]

命令:
    validate [type]    运行验证
        all            运行所有验证 (默认)
        links          验证内部链接
        external       验证外部链接
        metadata       验证元数据
        structure      验证内容结构
        self-tests     验证自测问题
        references     验证参考文献
        code           验证代码示例
    
    fix [type]         运行修复
        all            运行所有修复 (默认)
        links          修复所有链接问题
        spelling       修复拼写错误
        prefix         修复路径前缀
        index          添加缺失的index链接
        index-check    检查index链接
        index-fix      修复index链接
    
    build [type]       运行构建
        all            运行所有构建 (默认)
        paths          渲染学习路径
        package        打包离线版本
    
    check              运行检查点验证
    
    help               显示此帮助信息

示例:
    python scripts/main.py validate links
    python scripts/main.py fix spelling
    python scripts/main.py build paths
    python scripts/main.py check
"""
        print(help_text)


def main():
    """主函数"""
    runner = ScriptRunner()
    
    if len(sys.argv) < 2:
        runner.show_help()
        return 0
    
    command = sys.argv[1]
    
    if command == 'help' or command == '--help' or command == '-h':
        runner.show_help()
        return 0
    
    elif command == 'validate':
        validate_type = sys.argv[2] if len(sys.argv) > 2 else 'all'
        return runner.validate(validate_type)
    
    elif command == 'fix':
        fix_type = sys.argv[2] if len(sys.argv) > 2 else 'all'
        return runner.fix(fix_type)
    
    elif command == 'build':
        build_type = sys.argv[2] if len(sys.argv) > 2 else 'all'
        return runner.build(build_type)
    
    elif command == 'check':
        return runner.check()
    
    else:
        print(f"未知命令: {command}")
        print("运行 'python scripts/main.py help' 查看帮助")
        return 1


if __name__ == '__main__':
    sys.exit(main())
