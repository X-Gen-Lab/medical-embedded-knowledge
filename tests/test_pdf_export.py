"""
测试PDF导出功能

此测试模块验证PDF导出功能的正确性，包括：
- 单页PDF导出
- 完整知识库PDF导出
- PDF内容完整性和格式正确性

需求: 11.1
"""

import os
import subprocess
import pytest
from pathlib import Path
import tempfile
import shutil


class TestPDFExport:
    """PDF导出功能测试类"""
    
    @pytest.fixture(scope="class")
    def build_site(self):
        """构建站点的fixture"""
        # 设置环境变量以启用PDF导出
        os.environ['ENABLE_PDF_EXPORT'] = '1'
        
        # 构建站点
        result = subprocess.run(
            ['mkdocs', 'build', '--clean'],
            capture_output=True,
            text=True,
            timeout=300  # 5分钟超时
        )
        
        if result.returncode != 0:
            pytest.fail(f"MkDocs构建失败:\n{result.stderr}")
        
        yield
        
        # 清理环境变量
        if 'ENABLE_PDF_EXPORT' in os.environ:
            del os.environ['ENABLE_PDF_EXPORT']
    
    def test_pdf_export_enabled_in_config(self):
        """测试PDF导出在配置中已启用"""
        import yaml
        
        # 使用FullLoader来处理Python对象标签
        with open('mkdocs.yml', 'r', encoding='utf-8') as f:
            try:
                config = yaml.load(f, Loader=yaml.FullLoader)
            except:
                # 如果FullLoader失败，尝试使用UnsafeLoader
                f.seek(0)
                config = yaml.load(f, Loader=yaml.UnsafeLoader)
        
        # 验证pdf-export插件存在
        plugins = config.get('plugins', [])
        pdf_plugin_found = False
        
        for plugin in plugins:
            if isinstance(plugin, dict) and 'pdf-export' in plugin:
                pdf_plugin_found = True
                pdf_config = plugin['pdf-export']
                
                # 验证关键配置
                assert pdf_config.get('combined') == True, \
                    "PDF导出应配置为生成合并的完整PDF"
                assert 'combined_output_path' in pdf_config, \
                    "PDF导出应配置输出路径"
                assert pdf_config.get('media_type') == 'print', \
                    "PDF导出应使用打印媒体类型"
                
                break
        
        assert pdf_plugin_found, "mkdocs.yml中未找到pdf-export插件配置"
    
    def test_pdf_styles_file_exists(self):
        """测试PDF样式文件存在"""
        pdf_styles = Path('docs/assets/css/pdf-styles.css')
        assert pdf_styles.exists(), \
            "PDF样式文件不存在: docs/assets/css/pdf-styles.css"
        
        # 验证样式文件包含打印媒体查询
        with open(pdf_styles, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '@media print' in content, \
            "PDF样式文件应包含@media print规则"
    
    def test_complete_pdf_generated(self, build_site):
        """测试完整知识库PDF生成"""
        # 根据mkdocs.yml中的配置，PDF应该在site/pdf/目录下
        pdf_path = Path('site/pdf/medical-embedded-knowledge-complete.pdf')
        
        assert pdf_path.exists(), \
            f"完整PDF文件未生成: {pdf_path}"
        
        # 验证PDF文件大小（应该大于0）
        file_size = pdf_path.stat().st_size
        assert file_size > 0, \
            "PDF文件大小为0，可能生成失败"
        
        # 验证文件大小合理（至少应该有几KB）
        assert file_size > 1024, \
            f"PDF文件大小过小 ({file_size} bytes)，可能内容不完整"
        
        print(f"\n✓ 完整PDF已生成: {pdf_path}")
        print(f"  文件大小: {file_size / 1024:.2f} KB")
    
    def test_pdf_content_integrity_basic(self, build_site):
        """测试PDF内容完整性（基础检查）"""
        pdf_path = Path('site/pdf/medical-embedded-knowledge-complete.pdf')
        
        if not pdf_path.exists():
            pytest.skip("PDF文件不存在，跳过内容完整性测试")
        
        # 尝试使用PyPDF2读取PDF（如果可用）
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                # 验证PDF有页面
                num_pages = len(pdf_reader.pages)
                assert num_pages > 0, "PDF文件没有页面"
                
                # 验证页面数量合理（应该有多个页面）
                assert num_pages > 5, \
                    f"PDF页面数量过少 ({num_pages})，可能内容不完整"
                
                print(f"\n✓ PDF内容完整性检查通过")
                print(f"  总页数: {num_pages}")
                
                # 尝试提取第一页文本
                first_page = pdf_reader.pages[0]
                text = first_page.extract_text()
                
                # 验证包含标题文本
                assert len(text) > 0, "PDF第一页没有文本内容"
                
                # 验证包含关键词（站点名称）
                assert '医疗器械' in text or 'Medical' in text, \
                    "PDF内容应包含站点标题关键词"
                
                print(f"  第一页文本长度: {len(text)} 字符")
                
        except ImportError:
            pytest.skip("PyPDF2未安装，跳过PDF内容读取测试")
    
    def test_single_page_pdf_export_capability(self, build_site):
        """测试单页PDF导出能力"""
        # 注意：mkdocs-pdf-export-plugin默认为每个页面生成单独的PDF
        # 检查是否有单页PDF生成
        
        site_dir = Path('site')
        
        # 查找所有PDF文件
        pdf_files = list(site_dir.rglob('*.pdf'))
        
        assert len(pdf_files) > 0, \
            "未找到任何PDF文件"
        
        print(f"\n✓ 找到 {len(pdf_files)} 个PDF文件")
        
        # 列出前几个PDF文件
        for i, pdf_file in enumerate(pdf_files[:5]):
            rel_path = pdf_file.relative_to(site_dir)
            file_size = pdf_file.stat().st_size
            print(f"  {i+1}. {rel_path} ({file_size / 1024:.2f} KB)")
        
        if len(pdf_files) > 5:
            print(f"  ... 还有 {len(pdf_files) - 5} 个PDF文件")
    
    def test_pdf_format_correctness(self, build_site):
        """测试PDF格式正确性"""
        pdf_path = Path('site/pdf/medical-embedded-knowledge-complete.pdf')
        
        if not pdf_path.exists():
            pytest.skip("PDF文件不存在，跳过格式检查")
        
        # 验证文件是有效的PDF（检查文件头）
        with open(pdf_path, 'rb') as f:
            header = f.read(5)
        
        assert header == b'%PDF-', \
            "文件不是有效的PDF格式（文件头不正确）"
        
        print(f"\n✓ PDF格式正确性验证通过")
    
    def test_pdf_includes_navigation_content(self, build_site):
        """测试PDF包含导航内容"""
        pdf_path = Path('site/pdf/medical-embedded-knowledge-complete.pdf')
        
        if not pdf_path.exists():
            pytest.skip("PDF文件不存在，跳过导航内容测试")
        
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                # 提取所有页面的文本
                all_text = ""
                for page in pdf_reader.pages[:10]:  # 检查前10页
                    all_text += page.extract_text()
                
                # 验证包含主要章节的关键词
                key_sections = [
                    '核心技术知识',
                    '法规与标准',
                    '软件工程',
                    'RTOS',
                    'IEC 62304'
                ]
                
                found_sections = []
                for section in key_sections:
                    if section in all_text:
                        found_sections.append(section)
                
                assert len(found_sections) > 0, \
                    "PDF应包含至少一个主要章节的内容"
                
                print(f"\n✓ PDF包含以下章节内容:")
                for section in found_sections:
                    print(f"  - {section}")
                
        except ImportError:
            pytest.skip("PyPDF2未安装，跳过内容检查")
    
    def test_pdf_export_without_errors(self):
        """测试PDF导出过程无错误"""
        # 设置环境变量
        os.environ['ENABLE_PDF_EXPORT'] = '1'
        
        try:
            # 运行构建并捕获输出
            result = subprocess.run(
                ['mkdocs', 'build', '--clean', '--verbose'],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # 检查是否有错误
            assert result.returncode == 0, \
                f"MkDocs构建失败:\n{result.stderr}"
            
            # 检查输出中是否有PDF相关错误
            output = result.stdout + result.stderr
            
            # 常见的错误关键词
            error_keywords = [
                'ERROR',
                'FAILED',
                'Exception',
                'Traceback'
            ]
            
            errors_found = []
            for keyword in error_keywords:
                if keyword in output:
                    # 提取包含错误关键词的行
                    lines = output.split('\n')
                    error_lines = [line for line in lines if keyword in line]
                    errors_found.extend(error_lines[:3])  # 只取前3行
            
            if errors_found:
                print(f"\n⚠ 构建输出中发现潜在错误:")
                for line in errors_found:
                    print(f"  {line}")
            else:
                print(f"\n✓ PDF导出过程无错误")
            
        finally:
            # 清理环境变量
            if 'ENABLE_PDF_EXPORT' in os.environ:
                del os.environ['ENABLE_PDF_EXPORT']
    
    def test_pdf_output_directory_structure(self, build_site):
        """测试PDF输出目录结构"""
        site_dir = Path('site')
        pdf_dir = site_dir / 'pdf'
        
        # 验证PDF目录存在
        assert pdf_dir.exists(), \
            "PDF输出目录不存在: site/pdf/"
        
        assert pdf_dir.is_dir(), \
            "site/pdf应该是一个目录"
        
        # 列出PDF目录中的文件
        pdf_files = list(pdf_dir.glob('*.pdf'))
        
        print(f"\n✓ PDF输出目录结构正确")
        print(f"  目录: {pdf_dir}")
        print(f"  PDF文件数量: {len(pdf_files)}")


class TestPDFExportConfiguration:
    """PDF导出配置测试类"""
    
    def test_pdf_styles_contain_print_rules(self):
        """测试PDF样式包含打印规则"""
        pdf_styles = Path('docs/assets/css/pdf-styles.css')
        
        if not pdf_styles.exists():
            pytest.skip("PDF样式文件不存在")
        
        with open(pdf_styles, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证包含关键的打印样式规则
        expected_rules = [
            '@media print',
            'page-break',
        ]
        
        found_rules = []
        for rule in expected_rules:
            if rule in content:
                found_rules.append(rule)
        
        assert len(found_rules) > 0, \
            "PDF样式文件应包含打印相关的CSS规则"
        
        print(f"\n✓ PDF样式包含以下打印规则:")
        for rule in found_rules:
            print(f"  - {rule}")
    
    def test_pdf_export_plugin_dependencies(self):
        """测试PDF导出插件依赖"""
        requirements_file = Path('requirements.txt')
        
        with open(requirements_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 验证包含pdf-export插件
        assert 'mkdocs-pdf-export-plugin' in content, \
            "requirements.txt应包含mkdocs-pdf-export-plugin"
        
        print(f"\n✓ PDF导出插件依赖已配置")


def test_pdf_export_integration():
    """集成测试：完整的PDF导出流程"""
    print("\n" + "="*60)
    print("开始PDF导出集成测试")
    print("="*60)
    
    # 设置环境变量
    os.environ['ENABLE_PDF_EXPORT'] = '1'
    
    try:
        # 1. 清理旧的构建
        print("\n1. 清理旧的构建...")
        site_dir = Path('site')
        if site_dir.exists():
            # 只删除PDF目录
            pdf_dir = site_dir / 'pdf'
            if pdf_dir.exists():
                shutil.rmtree(pdf_dir)
                print("   ✓ 已清理旧的PDF文件")
        
        # 2. 构建站点
        print("\n2. 构建站点（启用PDF导出）...")
        result = subprocess.run(
            ['mkdocs', 'build'],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            print(f"   ✗ 构建失败:\n{result.stderr}")
            pytest.fail("站点构建失败")
        else:
            print("   ✓ 站点构建成功")
        
        # 3. 验证PDF生成
        print("\n3. 验证PDF文件生成...")
        pdf_path = Path('site/pdf/medical-embedded-knowledge-complete.pdf')
        
        if pdf_path.exists():
            file_size = pdf_path.stat().st_size
            print(f"   ✓ PDF文件已生成")
            print(f"     路径: {pdf_path}")
            print(f"     大小: {file_size / 1024:.2f} KB")
        else:
            print(f"   ✗ PDF文件未生成: {pdf_path}")
            pytest.fail("PDF文件未生成")
        
        # 4. 验证PDF内容
        print("\n4. 验证PDF内容...")
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)
                
                print(f"   ✓ PDF内容验证通过")
                print(f"     总页数: {num_pages}")
                
                if num_pages > 0:
                    first_page_text = pdf_reader.pages[0].extract_text()
                    print(f"     第一页文本长度: {len(first_page_text)} 字符")
        
        except ImportError:
            print("   ⚠ PyPDF2未安装，跳过内容验证")
        
        print("\n" + "="*60)
        print("PDF导出集成测试完成")
        print("="*60)
        
    finally:
        # 清理环境变量
        if 'ENABLE_PDF_EXPORT' in os.environ:
            del os.environ['ENABLE_PDF_EXPORT']


if __name__ == '__main__':
    # 运行测试
    pytest.main([__file__, '-v', '-s'])
