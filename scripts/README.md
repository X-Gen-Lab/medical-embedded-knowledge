# Scripts 工具脚本说明

本目录包含用于维护和验证医疗器械嵌入式软件知识体系的工具脚本。

## 📁 目录结构

```
scripts/
├── utils_lib/                      # 共享工具库
│   ├── __init__.py
│   ├── file_utils.py               # 文件操作工具
│   ├── markdown_utils.py           # Markdown处理工具
│   ├── report_utils.py             # 报告生成工具
│   ├── path_utils.py               # 路径处理工具
│   ├── validation_result.py        # 验证结果类
│   └── common.py                   # 通用函数
│
├── validation/                     # 验证工具
│   ├── __init__.py
│   ├── links.py                    # 内部链接验证
│   ├── external_links.py           # 外部链接检查
│   ├── markdown.py                 # Markdown格式验证
│   ├── structure.py                # 内容结构验证
│   ├── metadata.py                 # 元数据验证
│   ├── code_examples.py            # 代码示例扫描
│   ├── self_tests.py               # 自测题验证（合并）
│   └── references.py               # 参考文献验证（合并）
│
├── fix/                            # 修复工具
│   ├── __init__.py
│   ├── links.py                    # 链接修复（合并）
│   ├── index.py                    # Index管理（合并）
│   └── missing_files_report.py     # 缺失文件报告
│
├── build/                          # 构建工具
│   ├── __init__.py
│   ├── render_paths.py             # 渲染学习路径
│   └── package.py                  # 离线打包
│
├── checkpoint_validation.py        # 检查点验证
├── run_all_validations.py          # 运行所有验证
├── README.md                       # 本文档
├── SCRIPTS_INVENTORY.md            # 脚本清单
└── SCRIPTS_REORGANIZATION_PLAN.md  # 重组计划
```

## 🚀 快速开始

### 使用统一入口（推荐）
```bash
# 运行所有验证（包含详细报告）
python scripts/main.py validate

# 运行所有修复
python scripts/main.py fix

# 运行检查点验证（包含pytest测试）
python scripts/main.py check

# 查看帮助
python scripts/main.py help
```

### 直接运行脚本
```bash
# 运行所有验证
python scripts/run_all_validations.py

# 验证链接
python scripts/validation/links.py

# 修复链接问题
python scripts/fix/links.py
```

### 修复链接问题
```bash
# 修复所有链接问题
python scripts/fix/links.py

# 只修复拼写错误
python scripts/fix/links.py spelling

# 只修复路径前缀
python scripts/fix/links.py prefix

# 检查index缺失的链接
python scripts/fix/index.py check

# 添加缺失的index链接
python scripts/fix/index.py add

# 修复index中的无效链接
python scripts/fix/index.py fix
```

### 构建和打包
```bash
# 渲染学习路径
python scripts/build/render_paths.py

# 打包离线版本
python scripts/build/package.py --version 1.0.0
```

## 📚 详细说明

### 验证工具

#### 链接验证
- **validation/links.py**: 验证所有内部链接的有效性，检查文件是否存在
- **validation/external_links.py**: 检查外部链接的可访问性（需要网络连接）
- **fix/check_index_links.py**: 检查index文件中是否缺少对实际文件的引用

#### 内容验证
- **validation/markdown.py**: 验证Markdown文件的格式和Front Matter
- **validation/structure.py**: 验证文档结构的一致性
- **validation/metadata.py**: 扫描并验证文档元数据的完整性
- **validation/code_examples.py**: 扫描代码示例，检查注释和说明

#### 自测验证
- **validation/self_tests.py**: 验证自测问题的答案完整性和数量（支持所有模块）

#### 参考文献验证
- **validation/references.py**: 验证参考文献完整性（支持所有模块类型）

### 修复工具

#### 链接修复
- **fix/links.py**: 链接修复工具（拼写错误、路径前缀）
- **fix/index.py**: Index文件链接管理（检查、添加、修复）

#### 分析工具
- **fix/missing_files_report.py**: 生成详细的缺失文件报告

### 构建工具

- **build/render_paths.py**: 从YAML配置渲染学习路径Markdown文件
- **build/package.py**: 构建并打包离线HTML版本

### 集成工具

- **checkpoint_validation.py**: 运行检查点验证，生成完整报告
- **run_all_validations.py**: 运行所有验证脚本，生成综合报告

## 🔧 工具模块

### utils_lib/

共享工具库，提供以下模块：

- **file_utils.py**: 文件读写操作
- **markdown_utils.py**: Markdown解析和处理
- **report_utils.py**: 报告生成
- **path_utils.py**: 路径处理
- **validation_result.py**: 验证结果管理
- **common.py**: 通用函数（UTF-8设置、进度显示等）

使用示例：
```python
from utils_lib import FileUtils, MarkdownUtils, ValidationResult

# 读取文件
content = FileUtils.read_file(Path('docs/zh/index.md'))

# 提取链接
links = MarkdownUtils.extract_links(content)

# 创建验证结果
result = ValidationResult("链接验证")
result.add_error("链接无效", "file.md", 10)
print(result.generate_report())
```

## 📋 使用场景

### 场景1: 新增内容后验证

```bash
# 1. 验证Markdown格式
python scripts/validation/markdown.py

# 2. 验证链接
python scripts/validation/links.py

# 3. 检查index完整性
python scripts/fix/index.py check
```

### 场景2: 发现链接问题后修复

```bash
# 1. 运行链接验证
python scripts/validation/links.py

# 2. 修复链接问题
python scripts/fix/links.py

# 3. 添加缺失的index链接
python scripts/fix/index.py add

# 4. 再次验证
python scripts/validation/links.py
```

或使用统一入口：
```bash
python scripts/main.py validate links
python scripts/main.py fix links
python scripts/main.py fix index
python scripts/main.py validate links
```

### 场景3: 发布前完整检查

```bash
# 运行所有验证
python scripts/run_all_validations.py

# 打包离线版本
python scripts/build/package.py --version 1.0.0
```

## ⚙️ 配置说明

### 环境要求

- Python 3.8+
- 依赖包: `pyyaml`, `requests`

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行位置

所有脚本应从项目根目录运行：

```bash
# 正确 ✓
python scripts/validation/links.py

# 错误 ✗
cd scripts/validation
python links.py
```

## 📊 输出说明

### 验证脚本输出

- **退出码 0**: 验证通过
- **退出码 1**: 验证失败

### 报告文件

验证脚本会生成报告文件：
- `link-check-report.md`: 外部链接检查报告
- `validation-report-*.md`: 各类验证报告

### 控制台输出

```
开始验证内部链接...
找到 140 个Markdown文件
验证完成！

发现的失效链接数: 0
✓ 所有内部链接有效！
```

## 🔄 持续集成

### GitHub Actions 集成

```yaml
name: Validate Documentation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run validations
        run: python scripts/run_all_validations.py
```

## 📝 开发指南

### 添加新的验证脚本

1. 导入共享工具模块
2. 使用 `ValidationResult` 管理结果
3. 遵循现有命名规范
4. 更新本README

示例：
```python
#!/usr/bin/env python3
from pathlib import Path
from utils import ValidationResult, FileUtils, setup_utf8_output

def main():
    setup_utf8_output()
    result = ValidationResult("新验证")
    
    # 执行验证逻辑
    # ...
    
    # 生成报告
    print(result.generate_report())
    
    # 返回退出码
    return 0 if result.is_success() else 1

if __name__ == '__main__':
    sys.exit(main())
```

## 🐛 故障排除

### 常见问题

**Q: 脚本运行失败，提示找不到模块**
```bash
# 确保从项目根目录运行
cd /path/to/Medical
python scripts/validate_internal_links.py
```

**Q: 外部链接检查很慢**
```bash
# 外部链接检查需要网络请求，可能需要几分钟
# 可以跳过外部链接检查
python scripts/run_all_validations.py --skip-external
```

**Q: 编码错误**
```bash
# 脚本已自动处理UTF-8编码
# 如果仍有问题，检查文件编码
file -i docs/zh/index.md
```

## 📞 支持

如有问题或建议：
1. 查看本README
2. 查看脚本内的文档字符串
3. 在GitHub Issues中提问

## 📜 变更日志

### 2026-02-09
- ✅ 完成scripts目录深度重组和模块化
- ✅ 创建模块化工具库 `utils_lib/`（6个模块）
- ✅ 合并重复功能的脚本：
  - 3个references验证 → 1个统一工具
  - 2个self_tests验证 → 1个增强工具
  - 3个index管理 → 1个完整工具
  - 2个链接修复 → 1个统一工具
- ✅ 创建统一入口 `main.py`（整合所有功能）
- ✅ 删除冗余脚本：
  - checkpoint_validation.py（功能整合到main.py）
  - run_all_validations.py（功能整合到main.py）
- ✅ 删除所有临时文档
- ✅ 脚本数量减少62%（21→8个核心脚本）

### 历史版本
- 2026-02-08: 添加链接修复工具
- 2026-02-07: 初始版本

---

**维护者**: 医疗器械嵌入式软件知识体系团队  
**最后更新**: 2026-02-09
