# 脚本说明

本目录包含用于维护和验证医疗器械嵌入式软件知识体系的核心脚本。

## 核心验证脚本

### 链接验证
- **check_links.py** - 检查文档中的内部链接有效性
- **validate_internal_links.py** - 验证内部链接的完整性

### 内容验证
- **validate_content_structure.py** - 验证文档结构的一致性
- **validate_markdown.py** - 验证Markdown格式的正确性
- **validate_self_test_answers.py** - 验证自测问题的答案完整性
- **validate_software_engineering_self_tests.py** - 验证软件工程模块的自测问题

### 参考文献验证
- **verify_regulatory_references.py** - 验证法规标准模块的参考文献
- **verify_software_engineering_references.py** - 验证软件工程模块的参考文献
- **verify_technical_references.py** - 验证技术知识模块的参考文献

## 扫描和分析脚本

- **scan_code_examples.py** - 扫描代码示例，检查注释和说明的完整性
- **scan_metadata.py** - 扫描文档元数据，检查必需字段

## 工具脚本

- **render_learning_paths.py** - 渲染学习路径配置文件
- **checkpoint_validation.py** - 运行检查点验证，生成完整报告
- **run_all_validations.py** - 运行所有验证脚本
- **package_offline.py** - 打包离线HTML包，生成ZIP压缩文件

## 使用方法

### 运行所有验证
```bash
python scripts/run_all_validations.py
```

### 运行单个验证
```bash
# 验证链接
python scripts/check_links.py

# 扫描代码示例
python scripts/scan_code_examples.py

# 验证内容结构
python scripts/validate_content_structure.py
```

### 生成检查点报告
```bash
python scripts/checkpoint_validation.py
```

### 打包离线HTML包
```bash
# 基本用法（构建并打包）
python scripts/package_offline.py

# 指定版本号
python scripts/package_offline.py --version 2.0.0

# 自定义输出文件名
python scripts/package_offline.py --output my-offline-package.zip

# 清理构建并打包
python scripts/package_offline.py --clean --version 1.5.0

# 跳过构建，直接打包现有site目录
python scripts/package_offline.py --no-build
```

## 注意事项

1. 所有脚本应从项目根目录运行
2. 确保已安装必要的Python依赖
3. 验证脚本会生成报告文件到scripts目录
4. 定期运行验证脚本以确保内容质量

## 维护

- 这些脚本是持续质量保证的核心工具
- 不要删除这些脚本
- 如需添加新的验证功能，请遵循现有脚本的命名和结构规范
