# 医疗器械嵌入式软件知识体系

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)]()
[![Documentation](https://img.shields.io/badge/docs-latest-blue)]()
[![License](https://img.shields.io/badge/license-TBD-lightgrey)]()

## 📖 项目简介

本项目是一个**全面的医疗器械嵌入式软件知识管理系统**，旨在帮助开发人员、质量工程师和监管人员系统地学习和掌握医疗器械嵌入式软件开发所需的核心知识、技能和认知。

系统采用**文档即代码（Docs-as-Code）**的方法，使用Markdown格式组织知识内容，通过MkDocs静态站点生成器生成可浏览、可搜索的知识库网站。所有内容存储在Git仓库中，支持版本控制、协作编辑和持续集成。

### 🎯 项目目标

- 为医疗器械嵌入式软件开发人员提供系统化的学习资源
- 帮助团队理解和遵守医疗器械软件相关的国际标准和法规
- 提供实践案例和代码示例，加速知识转化为实践能力
- 建立可持续维护和更新的知识管理体系

## ✨ 主要特性

### 📚 全面的知识覆盖
- **核心技术知识**：嵌入式C/C++、RTOS、硬件接口、低功耗设计、信号处理
- **医疗法规标准**：IEC 62304、ISO 13485、ISO 14971、FDA法规、IEC 60601-1、IEC 81001-5-1
- **软件工程实践**：需求工程、架构设计、编码规范、测试策略、配置管理、静态分析

### 🎓 定制化学习路径
为不同角色提供针对性的学习路径：
- 嵌入式软件工程师路径
- 质量保证工程师路径
- 系统架构师路径
- 监管事务专员路径

### 🔍 强大的搜索功能
- 全文搜索支持
- 实时搜索建议
- 关键词高亮显示
- 标签过滤功能

### 🌍 多语言支持
- 中文和英文双语界面
- 核心模块提供双语内容
- 术语表中英文对照

### 📱 多渠道访问
- 在线浏览（响应式设计）
- PDF文档导出
- 离线HTML包
- 移动设备友好

### 💡 实践导向
- 真实的医疗器械开发案例研究
- 可运行的代码示例
- 文档模板和检查清单
- 自测问题和答案解析

### 🔄 版本控制
- 所有内容使用Git管理
- 支持协作编辑和审核
- 内容更新历史追踪
- 持续集成和自动部署

## 🚀 快速开始

### 环境要求

在开始之前，请确保您的系统满足以下要求：

- **Python**: 3.8 或更高版本
- **Git**: 用于版本控制
- **操作系统**: Windows、macOS 或 Linux

### 安装步骤

#### 1. 克隆仓库

```bash
git clone <repository-url>
cd Medical
```

#### 2. 创建虚拟环境（推荐）

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

主要依赖包括：
- `mkdocs` - 静态站点生成器
- `mkdocs-material` - Material主题
- `pymdown-extensions` - Markdown扩展
- `mkdocs-mermaid2-plugin` - Mermaid图表支持
- `pytest` 和 `hypothesis` - 测试框架

#### 4. 本地预览

启动本地开发服务器：

```bash
mkdocs serve
```

然后在浏览器中访问 `http://127.0.0.1:8000`

开发服务器支持热重载，修改Markdown文件后会自动刷新浏览器。

### 构建静态站点

构建生产环境的静态网站：

```bash
mkdocs build
```

构建后的静态文件将生成在 `site/` 目录中，可以部署到任何静态网站托管服务。

### 导出PDF

导出完整知识库为PDF文档：

```bash
# 设置环境变量启用PDF导出
set ENABLE_PDF_EXPORT=1  # Windows
export ENABLE_PDF_EXPORT=1  # macOS/Linux

# 构建并生成PDF
mkdocs build
```

PDF文件将生成在 `site/` 目录中。

### 生成离线HTML包

生成可离线使用的HTML包：

```bash
python scripts/package_offline.py
```

离线包将包含所有页面、资源和搜索功能，可在无网络环境下使用。

## 📁 项目结构

```
Medical/
├── .github/                       # GitHub Actions工作流
│   └── workflows/
│       ├── test.yml               # 自动化测试
│       └── deploy.yml             # 自动部署
├── .kiro/                         # Kiro规范文档
│   └── specs/
│       └── medical-device-embedded-knowledge-system/
├── docs/                          # 文档内容目录
│   ├── zh/                        # 中文内容
│   │   ├── index.md               # 首页
│   │   ├── getting-started/       # 入门指南
│   │   ├── technical-knowledge/   # 核心技术知识
│   │   │   ├── embedded-c-cpp/    # 嵌入式C/C++
│   │   │   ├── rtos/              # 实时操作系统
│   │   │   ├── hardware-interfaces/ # 硬件接口
│   │   │   ├── low-power-design/  # 低功耗设计
│   │   │   └── signal-processing/ # 信号处理
│   │   ├── regulatory-standards/  # 医疗法规与标准
│   │   │   ├── iec-62304/         # IEC 62304
│   │   │   ├── iso-13485/         # ISO 13485
│   │   │   ├── iso-14971/         # ISO 14971
│   │   │   ├── fda-regulations/   # FDA法规
│   │   │   ├── iec-60601-1/       # IEC 60601-1
│   │   │   └── iec-81001-5-1/     # IEC 81001-5-1
│   │   ├── software-engineering/  # 软件工程实践
│   │   │   ├── requirements-engineering/
│   │   │   ├── architecture-design/
│   │   │   ├── coding-standards/
│   │   │   ├── testing-strategy/
│   │   │   ├── configuration-management/
│   │   │   └── static-analysis/
│   │   ├── case-studies/          # 实践案例
│   │   ├── learning-paths/        # 学习路径
│   │   ├── references/            # 参考资料
│   │   └── glossary.md            # 术语表
│   ├── en/                        # 英文内容（结构同上）
│   ├── assets/                    # 静态资源
│   │   └── css/
│   │       └── pdf-styles.css     # PDF导出样式
│   ├── javascripts/               # JavaScript脚本
│   │   └── search-handler.js      # 搜索处理
│   ├── overrides/                 # 主题覆盖
│   │   ├── 404.html               # 自定义404页面
│   │   └── main.html              # 主模板
│   └── templates/                 # 内容模板
│       ├── module-template.md     # 知识模块模板
│       └── README.md              # 模板使用说明
├── scripts/                       # 工具脚本
│   ├── validate_markdown.py       # Markdown验证
│   ├── check_links.py             # 链接检查
│   ├── render_learning_paths.py   # 学习路径渲染
│   ├── package_offline.py         # 离线包生成
│   ├── scan_metadata.py           # 元数据扫描
│   └── run_all_validations.py     # 运行所有验证
├── tests/                         # 测试文件
│   ├── test_metadata_validation.py
│   ├── test_link_validation.py
│   ├── test_content_properties.py
│   └── test_pdf_export.py
├── site/                          # 构建输出目录（自动生成）
├── mkdocs.yml                     # MkDocs配置文件
├── requirements.txt               # Python依赖
├── CONTRIBUTING.md                # 贡献指南
└── README.md                      # 项目说明（本文件）
```

## 📖 内容组织

### 核心技术知识 (Technical Knowledge)

深入讲解医疗器械嵌入式软件开发的核心技术：

#### 嵌入式C/C++编程
- 内存管理（堆栈、动态分配、内存泄漏）
- 指针操作（指针运算、函数指针、指针安全）
- 位操作（位掩码、位域、寄存器操作）
- 编译器优化（优化级别、内联、循环展开）

#### 实时操作系统（RTOS）
- 任务调度（优先级调度、时间片轮转）
- 同步机制（信号量、互斥锁、事件标志）
- 中断处理（中断优先级、中断延迟、中断嵌套）
- 资源管理（内存池、消息队列、定时器）

#### 硬件接口
- I2C总线（主从模式、多主机、时钟拉伸）
- SPI总线（全双工通信、时钟极性和相位）
- UART串口（波特率、流控、错误检测）
- ADC/DAC（采样率、分辨率、参考电压）
- GPIO（输入输出、中断、防抖）

#### 低功耗设计
- 睡眠模式（深度睡眠、浅睡眠、待机）
- 时钟管理（时钟门控、动态频率调整）
- 功耗优化策略（外设管理、唤醒源配置）

#### 信号处理与算法
- 数字滤波器（FIR、IIR、中值滤波）
- 快速傅里叶变换（FFT）
- 心电信号处理（QRS检测、心率计算）
- 血氧饱和度计算（SpO2算法）

### 医疗法规与标准 (Regulatory Standards)

全面覆盖医疗器械软件相关的国际标准和法规：

#### IEC 62304 - 医疗器械软件生命周期过程
- 软件安全分类（Class A、B、C）
- 生命周期过程（开发、维护、风险管理）
- 文档要求（软件开发计划、架构设计、测试报告）

#### ISO 13485 - 质量管理体系
- 质量管理原则
- 过程方法
- 审核检查清单

#### ISO 14971 - 风险管理
- 风险分析方法（FMEA、FTA、HAZOP）
- 风险评估标准
- 风险控制措施（设计控制、保护措施、信息提示）

#### FDA法规
- 510(k)审批流程
- PMA（上市前批准）流程
- 软件验证要求

#### IEC 60601-1 - 医疗电气设备安全
- 电气安全要求
- EMC（电磁兼容）要求

#### IEC 81001-5-1 - 网络安全
- 威胁建模
- 安全控制措施
- 漏洞管理

### 软件工程实践 (Software Engineering)

系统化的软件工程方法和最佳实践：

#### 需求工程
- 需求追溯矩阵
- 需求验证方法
- 变更管理流程

#### 软件架构设计
- 分层架构（应用层、中间件层、驱动层）
- 模块化设计原则
- 接口定义规范

#### 编码规范
- MISRA C（汽车行业C语言编码标准）
- CERT C（安全编码标准）
- 代码审查检查清单

#### 测试策略
- 单元测试（白盒测试、代码覆盖率）
- 集成测试（接口测试、子系统测试）
- 系统测试（功能测试、性能测试）
- 回归测试（自动化测试、持续集成）

#### 配置管理
- 版本控制（Git工作流、分支策略）
- 基线管理（配置项识别、基线建立）
- 发布管理（版本号规则、发布清单）

#### 静态代码分析
- 工具使用（PC-lint、Coverity、SonarQube）
- 缺陷分类（严重性、优先级）
- 缺陷修复流程

## 🎓 学习路径

我们为不同角色提供了定制化的学习路径，帮助您系统地掌握所需知识：

### 1. 嵌入式软件工程师路径

**目标人群**: 从事医疗器械嵌入式软件开发的工程师

**学习重点**:
- 阶段1：嵌入式C/C++基础（内存管理、指针、位操作）
- 阶段2：RTOS核心概念（任务调度、同步、中断）
- 阶段3：硬件接口编程（I2C、SPI、UART）
- 阶段4：法规与质量（IEC 62304、MISRA C）

**预计学习时间**: 40小时

### 2. 质量保证工程师路径

**目标人群**: 负责医疗器械软件质量保证和测试的工程师

**学习重点**:
- 阶段1：医疗法规标准（IEC 62304、ISO 13485）
- 阶段2：测试策略与方法（单元测试、集成测试、系统测试）
- 阶段3：文档与追溯（需求追溯、测试文档）
- 阶段4：风险管理（ISO 14971、FMEA）

**预计学习时间**: 35小时

### 3. 系统架构师路径

**目标人群**: 负责医疗器械软件架构设计的高级工程师

**学习重点**:
- 阶段1：架构设计原则（分层架构、模块化）
- 阶段2：风险管理（ISO 14971、威胁建模）
- 阶段3：系统集成（接口设计、通信协议）
- 阶段4：法规合规（IEC 62304、IEC 81001-5-1）

**预计学习时间**: 45小时

### 4. 监管事务专员路径

**目标人群**: 负责医疗器械认证和监管事务的专员

**学习重点**:
- 阶段1：法规要求概览（IEC 62304、ISO 13485、FDA）
- 阶段2：认证流程（510(k)、PMA、CE认证）
- 阶段3：技术文档（软件开发计划、验证报告）
- 阶段4：审核准备（审核清单、常见问题）

**预计学习时间**: 30小时

### 如何使用学习路径

1. 访问网站的"学习路径"部分
2. 选择适合您角色的学习路径
3. 按照推荐顺序学习各个模块
4. 完成每个阶段的自测问题
5. 在检查点进行综合评估

## 🤝 贡献指南

我们热烈欢迎各种形式的贡献！无论是修复错误、改进文档、添加新内容，还是提出建议，都对项目有很大帮助。

### 如何贡献

#### 1. 报告问题

如果您发现了错误或有改进建议：

1. 在GitHub上创建Issue
2. 清楚描述问题或建议
3. 如果是错误，请提供复现步骤
4. 添加相关的标签（bug、enhancement、documentation等）

#### 2. 贡献内容

**准备工作**:
```bash
# Fork项目到您的GitHub账户
# 克隆您的Fork
git clone https://github.com/YOUR_USERNAME/Medical.git
cd Medical

# 创建新分支
git checkout -b feature/your-feature-name

# 安装依赖
pip install -r requirements.txt
```

**编写内容**:

1. **使用内容模板**: 参考 `docs/templates/module-template.md`
2. **添加Front Matter元数据**:
   ```yaml
   ---
   title: "模块标题"
   description: "简短描述"
   difficulty: "基础/中级/高级"
   estimated_time: "30分钟"
   tags: ["标签1", "标签2"]
   related_modules: ["相关模块路径"]
   last_updated: "YYYY-MM-DD"
   version: "1.0"
   language: "zh-CN"
   ---
   ```

3. **遵循内容结构**:
   - 学习目标
   - 前置知识
   - 核心内容
   - 代码示例（带注释）
   - 最佳实践
   - 常见陷阱
   - 自测问题（至少5个）
   - 参考资料

4. **代码示例要求**:
   - 提供完整、可运行的代码
   - 添加详细注释
   - 说明使用场景和注意事项
   - 遵循MISRA C或CERT C编码规范

5. **图表和图片**:
   - 使用Mermaid.js创建流程图和架构图
   - 图片存放在 `docs/assets/images/` 目录
   - 使用相对路径引用

**本地测试**:
```bash
# 启动本地服务器预览
mkdocs serve

# 运行验证脚本
python scripts/validate_markdown.py

# 运行测试
pytest tests/
```

**提交更改**:
```bash
# 添加更改
git add .

# 提交（使用清晰的提交信息）
git commit -m "feat: 添加RTOS任务调度模块"

# 推送到您的Fork
git push origin feature/your-feature-name
```

**创建Pull Request**:
1. 在GitHub上创建Pull Request
2. 填写PR模板，说明更改内容
3. 等待代码审查
4. 根据反馈进行修改

### 内容编写规范

#### Markdown格式
- 使用标准Markdown语法
- 代码块指定语言（```c、```python等）
- 使用admonition扩展（!!! note、!!! warning等）
- 使用折叠语法显示答案（??? question）

#### 命名规范
- 文件名使用小写字母和连字符（kebab-case）
- 例如：`task-scheduling.md`、`memory-management.md`

#### 中英文混排
- 中英文之间添加空格
- 例如："RTOS 任务调度"而不是"RTOS任务调度"

#### 术语使用
- 首次出现的专业术语提供解释
- 使用术语表中的标准术语
- 保持术语使用的一致性

### 代码审查标准

所有Pull Request都会经过代码审查，审查重点包括：

- ✅ 内容准确性和完整性
- ✅ 符合医疗器械软件标准
- ✅ 代码示例的正确性和安全性
- ✅ 文档格式和结构
- ✅ 元数据完整性
- ✅ 链接有效性
- ✅ 语言表达清晰度

### 行为准则

参与本项目时，请遵守以下准则：

- 尊重所有贡献者
- 接受建设性批评
- 关注对项目最有利的事情
- 对社区成员表现出同理心

### 获取帮助

如果您在贡献过程中遇到问题：

- 查看 [CONTRIBUTING.md](CONTRIBUTING.md) 获取详细指南
- 在Issue中提问
- 联系项目维护者

### 贡献者名单

感谢所有为本项目做出贡献的人！

<!-- 贡献者列表将自动生成 -->

---

**注意**: 更详细的贡献指南请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 文件。

## 🛠️ 技术栈

### 核心技术

- **静态站点生成器**: [MkDocs](https://www.mkdocs.org/) - Python编写的静态站点生成器
- **主题**: [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) - 现代化、响应式的文档主题
- **Markdown扩展**: [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/) - 增强的Markdown功能

### 功能插件

- **搜索**: Lunr.js - 客户端全文搜索
- **图表**: Mermaid.js - 流程图和架构图渲染
- **代码高亮**: Pygments - 多语言代码语法高亮
- **PDF导出**: mkdocs-pdf-export-plugin - PDF文档生成
- **多语言**: mkdocs-static-i18n - 国际化支持

### 开发工具

- **版本控制**: Git
- **测试框架**: 
  - pytest - Python单元测试框架
  - Hypothesis - 属性测试框架
- **代码质量**:
  - PyYAML - YAML解析和验证
  - Requests - HTTP链接检查
- **CI/CD**: GitHub Actions - 自动化测试和部署

### 部署选项

- **GitHub Pages** - 免费静态网站托管
- **Netlify** - 自动构建和部署
- **Vercel** - 边缘网络部署
- **自托管** - 任何支持静态网站的服务器

## 📊 项目统计

- **知识模块**: 100+ 个独立模块
- **代码示例**: 200+ 个实际案例
- **学习路径**: 4 条定制化路径
- **支持语言**: 中文、英文
- **文档页面**: 300+ 页
- **自测问题**: 500+ 个

## 🔧 开发指南

### 添加新模块

1. 在相应目录创建Markdown文件
2. 使用模板添加Front Matter
3. 编写内容（遵循内容结构）
4. 在 `mkdocs.yml` 中添加导航链接
5. 运行验证脚本确保格式正确

### 更新学习路径

1. 编辑 `docs/learning-paths/*.yaml` 文件
2. 运行渲染脚本：`python scripts/render_learning_paths.py`
3. 验证生成的Markdown文件

### 运行验证

```bash
# 验证所有Markdown文件的元数据
python scripts/validate_markdown.py

# 检查内部链接
python scripts/validate_internal_links.py

# 检查外部链接（较慢）
python scripts/check_links.py

# 运行所有验证
python scripts/run_all_validations.py
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_metadata_validation.py

# 运行属性测试（100次迭代）
pytest tests/test_content_properties.py -v

# 生成测试覆盖率报告
pytest --cov=scripts --cov-report=html
```

### 构建和部署

```bash
# 本地构建
mkdocs build

# 构建并检查严格模式（所有警告视为错误）
mkdocs build --strict

# 部署到GitHub Pages
mkdocs gh-deploy

# 生成离线包
python scripts/package_offline.py
```

## 🐛 故障排除

### 常见问题

**问题**: `mkdocs serve` 启动失败
```bash
# 解决方案：检查Python版本和依赖
python --version  # 应该是3.8+
pip install -r requirements.txt --upgrade
```

**问题**: 搜索功能不工作
```bash
# 解决方案：重新构建搜索索引
mkdocs build --clean
```

**问题**: PDF导出失败
```bash
# 解决方案：检查环境变量和依赖
set ENABLE_PDF_EXPORT=1
pip install mkdocs-pdf-export-plugin
```

**问题**: 链接验证报告大量失效链接
```bash
# 解决方案：检查是否是预期的外部链接
# 查看 link-check-report-*.md 文件
# 更新或移除失效链接
```

### 获取帮助

- 查看 [MkDocs文档](https://www.mkdocs.org/)
- 查看 [Material主题文档](https://squidfunk.github.io/mkdocs-material/)
- 在项目Issue中提问
- 联系项目维护者

## 📝 许可证

本项目的许可证待定。在正式确定许可证之前，请联系项目维护者了解使用条款。

## 🙏 致谢

感谢以下资源和项目对本知识体系的启发和帮助：

- [MkDocs](https://www.mkdocs.org/) - 优秀的静态站点生成器
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) - 精美的文档主题
- IEC、ISO、FDA等标准组织提供的官方文档
- 医疗器械软件开发社区的宝贵经验分享

## 📞 联系方式

如有问题、建议或合作意向，请通过以下方式联系我们：

- **GitHub Issues**: [提交Issue](https://github.com/your-org/Medical/issues)
- **电子邮件**: [待定]
- **讨论区**: [GitHub Discussions](https://github.com/your-org/Medical/discussions)

## 🗺️ 路线图

### 近期计划（2026 Q1-Q2）

- [ ] 完善所有核心技术知识模块
- [ ] 添加更多实践案例（至少10个）
- [ ] 完成英文内容翻译
- [ ] 实现用户进度跟踪功能
- [ ] 添加交互式代码示例

### 中期计划（2026 Q3-Q4）

- [ ] 集成在线编译器和调试器
- [ ] 添加视频教程
- [ ] 建立社区论坛
- [ ] 开发移动应用
- [ ] 添加更多语言支持（日语、德语）

### 长期愿景

- 成为医疗器械嵌入式软件开发的权威知识库
- 建立活跃的开发者社区
- 提供认证和培训服务
- 与医疗器械企业和培训机构合作

## 📚 相关资源

### 官方标准文档

- [IEC 62304](https://www.iec.ch/) - 医疗器械软件生命周期过程
- [ISO 13485](https://www.iso.org/) - 质量管理体系
- [ISO 14971](https://www.iso.org/) - 风险管理
- [FDA Guidance](https://www.fda.gov/) - FDA指南文档

### 推荐书籍

- 《Medical Device Software Development》
- 《Embedded Systems Design》
- 《Real-Time Systems》
- 《Software Safety and Reliability》

### 在线课程

- Coursera: Embedded Systems
- edX: Medical Device Software Development
- Udemy: RTOS Programming

### 开源项目

- FreeRTOS - 开源实时操作系统
- Zephyr - 物联网实时操作系统
- CMSIS - ARM Cortex微控制器软件接口标准

---

## ⭐ Star History

如果这个项目对您有帮助，请给我们一个Star！

[![Star History Chart](https://api.star-history.com/svg?repos=your-org/Medical&type=Date)](https://star-history.com/#your-org/Medical&Date)

---

**最后更新**: 2026-02-09  
**版本**: 1.0.0  
**维护者**: 医疗器械嵌入式软件知识体系团队

---

<div align="center">
  <sub>Built with ❤️ for the medical device software community</sub>
</div>
