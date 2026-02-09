# 更新日志 | Changelog

本文档记录医疗器械嵌入式软件知识体系项目的所有重要变更。

All notable changes to the Medical Device Embedded Software Knowledge System will be documented in this file.

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [未发布] - Unreleased

### 计划中 | Planned
- PDF导出功能完整测试
- 离线HTML包功能测试
- CI/CD自动化部署配置
- 端到端测试套件
- 更多实践案例（目标：10个以上）
- 视频教程集成
- 交互式代码示例

---

## [1.0.0] - 2026-02-09

### 新增 | Added

#### 核心功能 | Core Features
- ✨ 完整的MkDocs静态站点生成系统
- ✨ Material for MkDocs主题集成，提供现代化响应式界面
- ✨ 全文搜索功能，支持中英文搜索和实时建议
- ✨ 多语言支持（中文/英文），核心模块提供双语内容
- ✨ 学习路径系统，为4种角色提供定制化学习路径
- ✨ PDF导出功能配置
- ✨ 离线HTML包生成功能

#### 内容体系 | Content System
- 📚 核心技术知识模块
  - 嵌入式C/C++编程（内存管理、指针操作、位操作、编译器优化）
  - 实时操作系统RTOS（任务调度、同步机制、中断处理、资源管理）
  - 硬件接口（I2C、SPI、UART、ADC/DAC、GPIO）
  - 低功耗设计（睡眠模式、时钟管理、功耗优化）
  - 信号处理（数字滤波器、FFT、心电信号处理、血氧计算）

- 📚 医疗法规与标准模块
  - IEC 62304（软件生命周期过程、安全分类、文档要求）
  - ISO 13485（质量管理体系、审核清单）
  - ISO 14971（风险管理、风险分析、风险控制）
  - FDA法规（510(k)流程、PMA流程、软件验证）
  - IEC 60601-1（电气安全、EMC要求）
  - IEC 81001-5-1（网络安全、威胁建模、安全控制）

- 📚 软件工程实践模块
  - 需求工程（需求追溯、变更管理）
  - 架构设计（分层架构、模块化设计、接口设计）
  - 编码规范（MISRA C、CERT C、代码审查清单）
  - 测试策略（单元测试、集成测试、系统测试）
  - 配置管理（版本控制、基线管理）
  - 静态分析（工具使用、缺陷分类）

- 📚 实践案例
  - Class A医疗器械开发案例
  - Class B血压监测仪案例
  - Class C医疗器械开发案例

#### 学习路径 | Learning Paths
- 🎓 嵌入式软件工程师路径（40小时）
- 🎓 质量保证工程师路径（35小时）
- 🎓 系统架构师路径（45小时）
- 🎓 监管事务专员路径（30小时）

#### 开发工具 | Development Tools
- 🛠️ 知识模块Markdown模板系统
- 🛠️ Front Matter元数据验证脚本
- 🛠️ 学习路径YAML配置和渲染系统
- 🛠️ 外部链接检查脚本
- 🛠️ 离线HTML包打包脚本
- 🛠️ 内容验证脚本集合

#### 测试框架 | Testing Framework
- ✅ Pytest测试框架配置
- ✅ Hypothesis属性测试集成
- ✅ 元数据完整性测试
- ✅ 内容质量属性测试
- ✅ 自测问题完整性验证
- ✅ 链接有效性测试

#### 文档 | Documentation
- 📖 完整的项目README（中英文）
- 📖 详细的贡献指南CONTRIBUTING.md
- 📖 知识模块编写模板和使用说明
- 📖 中英文术语表

### 改进 | Improved
- 🎨 优化Material主题配置，提升用户体验
- 🎨 改进代码高亮显示，支持多种编程语言
- 🎨 优化PDF导出样式，提升打印效果
- 🔍 增强搜索功能，支持关键词高亮
- 📱 优化移动端显示效果
- 🌐 改进多语言切换体验

### 修复 | Fixed
- 🐛 修复内部链接相对路径问题
- 🐛 修复Front Matter元数据解析错误
- 🐛 修复搜索索引生成问题
- 🐛 修复导航层级显示问题

### 技术栈 | Tech Stack
- Python 3.8+
- MkDocs 1.5.0+
- MkDocs Material 9.0+
- PyMdown Extensions
- Mermaid.js（图表支持）
- Pytest + Hypothesis（测试框架）

### 项目统计 | Project Statistics
- 📊 知识模块：100+ 个
- 📊 代码示例：200+ 个
- 📊 学习路径：4 条
- 📊 文档页面：300+ 页
- 📊 自测问题：500+ 个
- 📊 支持语言：中文、英文

---

## [0.2.0] - 2026-02-07

### 新增 | Added
- ✨ 完成内容完整性验证检查点
- ✨ 添加元数据验证报告生成
- ✨ 实现内容质量属性测试
- ✨ 添加自测问题完整性验证

### 改进 | Improved
- 📝 完善核心技术知识模块内容
- 📝 补充医疗法规与标准模块
- 📝 优化软件工程实践模块结构

### 修复 | Fixed
- 🐛 修复91个预期的失效链接（指向未来内容）
- 🐛 修正元数据字段验证逻辑

### 验证结果 | Validation Results
- ✅ 元数据验证通过（8个模块）
- ✅ 内容质量属性测试通过（6项测试）
- ✅ 自测问题完整性验证通过
- ⚠️ 链接验证发现91个预期的失效链接

---

## [0.1.0] - 2026-01-15

### 新增 | Added
- 🎉 项目初始化
- 📁 创建基础目录结构
- ⚙️ 配置MkDocs和Material主题
- 📝 创建知识模块模板
- 🌐 配置多语言支持框架
- 🔍 配置基础搜索功能

### 技术实现 | Technical Implementation
- 初始化Git仓库
- 创建requirements.txt依赖文件
- 配置mkdocs.yml基础配置
- 创建docs/目录结构
- 设置Python虚拟环境

---

## 版本说明 | Version Notes

### 版本号规则 | Versioning Rules

本项目遵循语义化版本号规则：`主版本号.次版本号.修订号`

- **主版本号**：重大功能变更或不兼容的API修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

### 变更类型 | Change Types

- `新增 | Added`：新功能或新内容
- `改进 | Improved`：对现有功能的改进
- `修复 | Fixed`：错误修复
- `变更 | Changed`：对现有功能的修改
- `弃用 | Deprecated`：即将移除的功能
- `移除 | Removed`：已移除的功能
- `安全 | Security`：安全相关的修复

---

## 贡献者 | Contributors

感谢所有为本项目做出贡献的人！

Thank you to all the people who have contributed to this project!

<!-- 贡献者列表将自动生成 -->
<!-- Contributors list will be automatically generated -->

---

## 链接 | Links

- **项目主页 | Homepage**: [待定 | TBD]
- **文档站点 | Documentation**: [待定 | TBD]
- **问题追踪 | Issue Tracker**: [GitHub Issues](https://github.com/your-org/Medical/issues)
- **讨论区 | Discussions**: [GitHub Discussions](https://github.com/your-org/Medical/discussions)

---

**最后更新 | Last Updated**: 2026-02-09  
**维护者 | Maintainer**: 医疗器械嵌入式软件知识体系团队 | Medical Device Embedded Software Knowledge System Team
