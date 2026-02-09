# 贡献指南 | Contributing Guide

欢迎来到医疗器械嵌入式软件知识体系项目！我们热烈欢迎各种形式的贡献，无论是修复错误、改进文档、添加新内容，还是提出建议，都对项目有很大帮助。

Welcome to the Medical Device Embedded Software Knowledge System! We warmly welcome all forms of contributions, whether it's fixing bugs, improving documentation, adding new content, or making suggestions.

---

## 📋 目录 | Table of Contents

- [行为准则](#行为准则--code-of-conduct)
- [如何贡献](#如何贡献--how-to-contribute)
- [内容编写规范](#内容编写规范--content-writing-standards)
- [模板使用指南](#模板使用指南--template-usage-guide)
- [提交流程](#提交流程--submission-process)
- [代码审查标准](#代码审查标准--code-review-standards)
- [获取帮助](#获取帮助--getting-help)

---

## 行为准则 | Code of Conduct

### 我们的承诺

为了营造一个开放和友好的环境，我们作为贡献者和维护者承诺：无论年龄、体型、残疾、种族、性别认同和表达、经验水平、国籍、个人外貌、种族、宗教或性取向如何，参与我们的项目和社区的每个人都不会受到骚扰。

### 我们的标准

有助于创造积极环境的行为包括：

- ✅ 使用友好和包容的语言
- ✅ 尊重不同的观点和经验
- ✅ 优雅地接受建设性批评
- ✅ 关注对社区最有利的事情
- ✅ 对其他社区成员表现出同理心

不可接受的行为包括：

- ❌ 使用性化的语言或图像，以及不受欢迎的性关注或挑逗
- ❌ 恶意评论、侮辱性/贬损性评论以及人身或政治攻击
- ❌ 公开或私下骚扰
- ❌ 未经明确许可发布他人的私人信息
- ❌ 在专业环境中可能被合理认为不适当的其他行为

### 我们的责任

项目维护者有责任澄清可接受行为的标准，并对任何不可接受的行为采取适当和公平的纠正措施。

---

## 如何贡献 | How to Contribute


### 1. 报告问题 | Reporting Issues

如果您发现了错误、有改进建议或想要请求新功能：

**步骤**：

1. **搜索现有Issue**：首先检查是否已有类似的Issue
2. **创建新Issue**：如果没有找到相关Issue，创建一个新的
3. **提供详细信息**：
   - 清楚描述问题或建议
   - 如果是错误，提供复现步骤
   - 包含相关的截图或日志
   - 说明您的环境（操作系统、Python版本等）
4. **添加标签**：选择合适的标签（bug、enhancement、documentation等）

**Issue模板示例**：

```markdown
**问题描述**
简短描述问题

**复现步骤**
1. 进入 '...'
2. 点击 '...'
3. 滚动到 '...'
4. 看到错误

**预期行为**
描述您期望发生什么

**实际行为**
描述实际发生了什么

**截图**
如果适用，添加截图帮助解释问题

**环境**
- 操作系统: [例如 Windows 11]
- Python版本: [例如 3.10.0]
- MkDocs版本: [例如 1.5.0]

**附加信息**
添加任何其他相关信息
```

### 2. 贡献内容 | Contributing Content

#### 准备工作

**Fork和克隆项目**：

```bash
# 1. Fork项目到您的GitHub账户（在GitHub网页上点击Fork按钮）

# 2. 克隆您的Fork到本地
git clone https://github.com/YOUR_USERNAME/medical-embedded-knowledge.git
cd medical-embedded-knowledge

# 3. 添加上游仓库
git remote add upstream https://github.com/X-Gen-Lab/medical-embedded-knowledge.git

# 4. 创建新分支
git checkout -b feature/your-feature-name
# 或者修复bug时使用
git checkout -b fix/bug-description
```

**安装依赖**：

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**验证安装**：

```bash
# 启动本地服务器
mkdocs serve

# 在浏览器中访问 http://127.0.0.1:8000
# 如果能看到网站，说明安装成功
```


#### 贡献类型

**A. 添加新知识模块**

适用于创建全新的知识内容模块。

**B. 改进现有内容**

适用于修正错误、补充信息、改进表达等。

**C. 添加代码示例**

适用于为现有模块添加实际代码示例。

**D. 翻译内容**

适用于将中文内容翻译为英文，或反之。

**E. 修复错误**

适用于修复文档中的错误、失效链接等。

**F. 改进基础设施**

适用于改进构建脚本、测试、CI/CD等。

---

## 内容编写规范 | Content Writing Standards

### 文件命名规范

**规则**：
- 使用小写字母
- 单词之间使用连字符（kebab-case）
- 使用描述性名称
- 文件扩展名为 `.md`

**示例**：
```
✅ 正确：task-scheduling.md
✅ 正确：memory-management.md
✅ 正确：iec-62304-overview.md

❌ 错误：TaskScheduling.md
❌ 错误：task_scheduling.md
❌ 错误：ts.md
```

### 目录结构规范

新内容应放置在适当的目录中：

```
docs/
├── zh/                           # 中文内容
│   ├── technical-knowledge/      # 核心技术知识
│   ├── regulatory-standards/     # 医疗法规与标准
│   ├── software-engineering/     # 软件工程实践
│   ├── case-studies/             # 实践案例
│   ├── learning-paths/           # 学习路径
│   └── references/               # 参考资料
└── en/                           # 英文内容（结构同上）
```

### Front Matter元数据规范

**必需字段**：

每个知识模块文件必须包含以下Front Matter元数据：

```yaml
---
title: "模块标题"                    # 必需：模块的标题
description: "简短描述"              # 必需：1-2句话概括内容
difficulty: "基础"                   # 必需：基础/中级/高级
estimated_time: "30分钟"            # 必需：预计学习时间
tags: ["标签1", "标签2"]            # 必需：相关标签
last_updated: "2026-02-09"          # 必需：最后更新日期（YYYY-MM-DD）
version: "1.0"                      # 必需：版本号
language: "zh-CN"                   # 必需：语言代码
---
```

**可选字段**：

```yaml
category: "技术"                    # 可选：技术/法规/工程
related_modules:                    # 可选：相关模块列表
  - "rtos/synchronization"
  - "hardware-interfaces/i2c"
prerequisites:                      # 可选：前置知识
  - "C语言基础"
  - "基本的电子电路知识"
```

**字段说明**：

- **title**: 清晰、简洁的标题，准确描述模块内容
- **description**: 1-2句话的简短描述，用于搜索结果和摘要
- **difficulty**: 只能是"基础"、"中级"或"高级"之一
- **estimated_time**: 格式如"30分钟"、"1小时"、"2小时"
- **tags**: 相关的关键词标签，便于搜索和分类
- **last_updated**: 使用ISO 8601日期格式（YYYY-MM-DD）
- **version**: 遵循语义化版本号（如1.0、1.1、2.0）
- **language**: 使用标准语言代码（zh-CN、en-US等）


### Markdown格式规范

#### 标题层级

```markdown
# 一级标题（文件标题，每个文件只有一个）
## 二级标题（主要章节）
### 三级标题（子章节）
#### 四级标题（详细内容）
```

**规则**：
- 不要跳过标题层级
- 标题后空一行再开始内容
- 使用描述性标题，避免"简介"、"概述"等通用词

#### 代码块

**指定语言**：

```markdown
```c
// C语言代码
void example() {
    printf("Hello, World!\n");
}
\```

```python
# Python代码
def example():
    print("Hello, World!")
\```
```

**支持的语言标识**：
- `c` - C语言
- `cpp` - C++
- `python` - Python
- `bash` - Shell脚本
- `yaml` - YAML配置
- `json` - JSON数据
- `makefile` - Makefile

#### 强调和提示框

使用MkDocs Material的admonition扩展：

```markdown
!!! note "提示"
    这是一个提示信息

!!! tip "最佳实践"
    这是最佳实践建议

!!! warning "注意事项"
    这是需要注意的内容

!!! danger "严重错误"
    这是可能导致严重后果的错误

!!! info "医疗器械开发注意事项"
    医疗器械特定的考虑事项

!!! example "实际应用示例"
    实际应用的例子
```

#### 折叠内容

用于自测问题和答案：

```markdown
??? question "问题描述"
    问题的详细内容
    
    ??? success "答案"
        答案和解析
```

#### 链接

**内部链接**（使用相对路径）：

```markdown
[相关模块](../rtos/task-scheduling.md)
[返回首页](../../index.md)
```

**外部链接**：

```markdown
[IEC官网](https://www.iec.ch/)
```

#### 图片

```markdown
![图片描述](../assets/images/diagram.png)
```

**图片要求**：
- 使用描述性的alt文本
- 图片存放在 `docs/assets/images/` 目录
- 使用相对路径引用
- 优先使用Mermaid图表（流程图、架构图）

#### 表格

```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 数据1 | 数据2 | 数据3 |
| 数据4 | 数据5 | 数据6 |
```

### 内容结构规范

每个知识模块应包含以下结构（参考模板）：

1. **Front Matter元数据**
2. **模块标题**
3. **学习目标**（3-5个具体目标）
4. **前置知识**（2-4个前置要求）
5. **内容**
   - 概念介绍
   - 详细说明
   - 代码示例（带注释和说明）
   - 最佳实践
   - 常见陷阱
   - 医疗器械特定考虑
6. **实践练习**（1-3个练习）
7. **自测问题**（至少5个问题）
8. **相关资源**
9. **参考文献**


### 代码示例规范

#### 代码质量要求

**必须**：
- ✅ 代码必须是完整的、可编译的
- ✅ 添加详细的注释说明每个关键步骤
- ✅ 遵循MISRA C或CERT C编码规范
- ✅ 包含错误处理代码
- ✅ 使用有意义的变量和函数名

**示例**：

```c
/**
 * @brief 初始化I2C外设
 * @param i2c_instance I2C实例指针
 * @param speed_mode 速度模式（标准/快速）
 * @return 0表示成功，负值表示错误码
 * 
 * @note 此函数必须在使用I2C通信前调用
 * @warning 确保时钟已正确配置
 */
int i2c_init(I2C_TypeDef *i2c_instance, I2C_SpeedMode speed_mode) {
    // 参数验证
    if (i2c_instance == NULL) {
        return -1;  // 无效参数
    }
    
    // 使能I2C时钟
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;
    
    // 配置速度模式
    if (speed_mode == I2C_SPEED_STANDARD) {
        i2c_instance->CCR = 0x50;  // 100kHz
    } else {
        i2c_instance->CCR = 0x14;  // 400kHz
    }
    
    // 使能I2C外设
    i2c_instance->CR1 |= I2C_CR1_PE;
    
    return 0;  // 成功
}
```

#### 代码说明要求

每个代码示例后必须包含：

1. **代码说明**：解释关键代码行的作用
2. **使用说明**：如何编译、运行和测试
3. **注意事项**：使用时需要注意的问题

**示例**：

```markdown
**代码说明**：
- **第10-12行**：参数验证，确保传入的指针有效
- **第15行**：使能I2C外设时钟，这是使用外设的前提
- **第18-22行**：根据速度模式配置时钟控制寄存器
- **第25行**：使能I2C外设

**使用说明**：
1. 编译：`gcc -o i2c_example i2c_example.c`
2. 需要的硬件：STM32F4系列微控制器
3. 依赖：CMSIS库

**注意事项**：
- 调用此函数前必须先配置GPIO引脚为I2C功能
- 确保系统时钟已正确初始化
- 在医疗器械应用中，建议添加超时机制
```

### 语言和表达规范

#### 中英文混排

**规则**：
- 中英文之间添加一个空格
- 中文与数字之间添加一个空格
- 专业术语首次出现时提供英文原文

**示例**：

```markdown
✅ 正确：RTOS 任务调度机制
✅ 正确：IEC 62304 标准要求软件安全分类
✅ 正确：采样率为 1000 Hz

❌ 错误：RTOS任务调度机制
❌ 错误：IEC62304标准要求软件安全分类
❌ 错误：采样率为1000Hz
```

#### 术语使用

**一致性**：
- 使用术语表中的标准术语
- 保持整个文档中术语使用的一致性
- 首次出现时提供解释

**示例**：

```markdown
实时操作系统（Real-Time Operating System, RTOS）是一种...

在后续内容中，统一使用"RTOS"而不是"实时操作系统"或"实时OS"。
```

#### 表达清晰度

**要求**：
- 使用简洁、清晰的语言
- 避免过于复杂的句子结构
- 使用主动语态
- 提供具体的例子

**示例**：

```markdown
✅ 正确：使用互斥锁保护共享资源，防止数据竞争。
❌ 错误：共享资源的保护可以通过互斥锁的使用来实现，从而避免可能发生的数据竞争情况。

✅ 正确：调用 xTaskCreate() 创建新任务。
❌ 错误：新任务的创建是通过 xTaskCreate() 函数来完成的。
```


### 医疗器械特定要求

#### 安全性考虑

在编写医疗器械相关内容时，必须强调：

1. **风险管理**：说明相关的风险和缓解措施
2. **法规要求**：引用相关的标准和法规
3. **验证测试**：说明如何验证功能的正确性
4. **文档要求**：说明需要记录的内容

**示例**：

```markdown
!!! info "医疗器械开发注意事项"
    在医疗器械嵌入式软件开发中，使用中断处理时需要特别注意：
    
    - **安全性**：中断处理程序必须尽可能短，避免影响系统实时性
    - **法规要求**：根据IEC 62304，中断处理代码属于关键代码，需要进行详细的单元测试
    - **文档要求**：必须在软件设计文档中记录所有中断源、优先级和处理流程
    - **验证测试**：需要进行中断延迟测试和最坏情况执行时间（WCET）分析
```

#### 标准引用

引用标准时使用正确的格式：

```markdown
根据 IEC 62304:2006+AMD1:2015 第5.5节的要求...

ISO 14971:2019 定义的风险管理流程包括...
```

---

## 模板使用指南 | Template Usage Guide

### 知识模块模板

位置：`docs/templates/module-template.md`

**使用步骤**：

1. **复制模板**：
   ```bash
   cp docs/templates/module-template.md docs/zh/technical-knowledge/your-module.md
   ```

2. **填写Front Matter**：
   - 更新所有必需字段
   - 根据需要添加可选字段
   - 确保日期格式正确

3. **编写内容**：
   - 按照模板结构填写各个部分
   - 删除不需要的部分（如某些子章节）
   - 保持至少5个自测问题

4. **添加代码示例**：
   - 提供完整、可运行的代码
   - 添加详细注释
   - 包含使用说明

5. **添加参考资料**：
   - 至少包含一个参考文献
   - 链接到相关的官方文档

### 模板各部分说明

#### 学习目标

**目的**：明确告诉学习者完成本模块后能够掌握什么。

**要求**：
- 3-5个具体、可衡量的目标
- 使用动词开头（理解、掌握、能够、学会等）
- 具体而非笼统

**示例**：

```markdown
## 学习目标

完成本模块后，你将能够：
- 理解RTOS任务调度的基本原理和调度算法
- 掌握FreeRTOS中任务优先级的配置方法
- 能够分析和解决任务调度相关的问题
- 学会使用调度器API创建和管理任务
```

#### 前置知识

**目的**：帮助学习者评估是否准备好学习本模块。

**要求**：
- 2-4个前置知识点
- 可以链接到相关的基础模块
- 明确说明必需和推荐的前置知识

**示例**：

```markdown
## 前置知识

在学习本模块之前，建议你已经掌握：
- C语言基础（必需）：指针、结构体、函数
- 基本的操作系统概念（推荐）：进程、线程、并发
- [嵌入式C编程基础](../embedded-c-cpp/index.md)（推荐）
```

#### 代码示例

**目的**：提供实际的、可运行的代码帮助理解概念。

**要求**：
- 代码完整、可编译
- 包含详细注释
- 提供使用说明
- 说明潜在问题

**示例结构**：

```markdown
### 代码示例

```c
// 完整的代码
\```

**代码说明**：
- 解释关键部分

**使用说明**：
1. 编译方法
2. 运行方法
3. 预期结果

**注意事项**：
- 潜在问题
- 使用限制
```


#### 自测问题

**目的**：帮助学习者检验学习效果。

**要求**：
- 至少5个问题
- 使用折叠语法隐藏答案
- 提供详细的答案解析
- 回顾相关知识点

**示例**：

```markdown
## 自测问题

??? question "问题1：在FreeRTOS中，如果两个任务具有相同的优先级，调度器如何选择执行哪个任务？"
    
    A. 随机选择  
    B. 先创建的任务优先  
    C. 时间片轮转  
    D. 后创建的任务优先
    
    ??? success "答案"
        **正确答案**：C. 时间片轮转
        
        **解析**：
        在FreeRTOS中，当多个任务具有相同的优先级时，调度器使用时间片轮转（Round-Robin）算法。
        每个任务在其时间片内运行，时间片结束后切换到下一个相同优先级的就绪任务。
        时间片的长度由configTICK_RATE_HZ配置。
        
        **知识点回顾**：
        - 优先级调度：高优先级任务总是优先于低优先级任务
        - 时间片轮转：相同优先级任务之间的公平调度机制
        - 抢占式调度：高优先级任务可以抢占低优先级任务
```

### 案例研究模板

对于实践案例，应包含：

1. **项目背景**：医疗器械类型、应用场景
2. **技术挑战**：遇到的具体问题
3. **解决方案**：采用的技术方案
4. **实施细节**：关键代码和配置
5. **验证测试**：如何验证解决方案
6. **经验教训**：总结和建议
7. **法规合规**：相关的标准和认证

---

## 提交流程 | Submission Process

### 本地开发和测试

#### 1. 本地预览

在提交前，务必在本地预览您的更改：

```bash
# 启动本地开发服务器
mkdocs serve

# 在浏览器中访问 http://127.0.0.1:8000
# 检查内容显示是否正确
```

**检查清单**：
- ✅ 页面能正常显示
- ✅ 代码高亮正确
- ✅ 链接可以点击
- ✅ 图片正常显示
- ✅ 格式符合预期

#### 2. 运行验证脚本

运行自动化验证脚本检查内容质量：

```bash
# 验证Markdown文件的元数据
python scripts/validate_markdown.py

# 验证内部链接
python scripts/validate_internal_links.py

# 扫描元数据
python scripts/scan_metadata.py

# 运行所有验证（推荐）
python scripts/run_all_validations.py
```

**常见错误和解决方法**：

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| 缺少必需字段 | Front Matter不完整 | 添加缺失的字段 |
| difficulty值无效 | 使用了非标准值 | 改为"基础"、"中级"或"高级" |
| 内部链接失效 | 链接指向不存在的文件 | 检查文件路径是否正确 |
| 日期格式错误 | 日期格式不符合要求 | 使用YYYY-MM-DD格式 |

#### 3. 运行测试（如果修改了脚本）

如果您修改了Python脚本或添加了新功能：

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_metadata_validation.py

# 运行测试并显示详细输出
pytest -v

# 生成测试覆盖率报告
pytest --cov=scripts --cov-report=html
```

### Git提交规范

#### 提交信息格式

使用清晰、描述性的提交信息，遵循以下格式：

```
<类型>(<范围>): <简短描述>

<详细描述>（可选）

<相关Issue>（可选）
```

**类型**：
- `feat`: 新功能或新内容
- `fix`: 修复错误
- `docs`: 文档更新
- `style`: 格式调整（不影响代码含义）
- `refactor`: 重构（既不是新功能也不是修复）
- `test`: 添加或修改测试
- `chore`: 构建过程或辅助工具的变动

**范围**（可选）：
- `rtos`: RTOS相关内容
- `iec62304`: IEC 62304相关内容
- `scripts`: 脚本相关
- `ci`: CI/CD相关

**示例**：

```bash
# 好的提交信息
git commit -m "feat(rtos): 添加任务调度模块"
git commit -m "fix(iec62304): 修正软件分类描述错误"
git commit -m "docs: 更新贡献指南"

# 带详细描述
git commit -m "feat(rtos): 添加FreeRTOS任务调度示例

- 添加任务创建和删除的代码示例
- 包含优先级配置说明
- 添加5个自测问题

Closes #123"
```


#### 提交步骤

```bash
# 1. 查看更改
git status
git diff

# 2. 添加更改到暂存区
git add docs/zh/technical-knowledge/your-module.md
# 或添加所有更改
git add .

# 3. 提交更改
git commit -m "feat(technical): 添加新模块"

# 4. 推送到您的Fork
git push origin feature/your-feature-name
```

### 创建Pull Request

#### 1. 在GitHub上创建PR

1. 访问您的Fork仓库
2. 点击"Pull Request"按钮
3. 选择base分支（通常是main）和compare分支（您的功能分支）
4. 填写PR标题和描述

#### 2. PR标题格式

```
<类型>: <简短描述>
```

**示例**：
```
feat: 添加RTOS任务调度模块
fix: 修正IEC 62304软件分类错误
docs: 更新贡献指南
```

#### 3. PR描述模板

```markdown
## 更改类型
- [ ] 新功能/新内容
- [ ] 错误修复
- [ ] 文档改进
- [ ] 代码重构
- [ ] 其他（请说明）

## 更改描述
简要描述您的更改内容和原因。

## 相关Issue
Closes #123
Fixes #456

## 检查清单
- [ ] 已在本地预览更改
- [ ] 已运行验证脚本
- [ ] 已添加/更新测试（如适用）
- [ ] 遵循了内容编写规范
- [ ] 更新了相关文档
- [ ] 提交信息清晰明确

## 截图（如适用）
添加截图帮助审查者理解更改。

## 附加信息
任何其他相关信息。
```

#### 4. 等待审查

- PR创建后，维护者会进行审查
- 可能会收到反馈和修改建议
- 根据反馈进行修改并推送更新
- 所有讨论解决后，PR将被合并

#### 5. 响应审查意见

```bash
# 根据反馈进行修改
# 编辑文件...

# 提交修改
git add .
git commit -m "fix: 根据审查意见修改内容"

# 推送更新
git push origin feature/your-feature-name

# PR会自动更新
```

### 保持同步

定期同步上游仓库的更改：

```bash
# 获取上游更改
git fetch upstream

# 切换到主分支
git checkout main

# 合并上游更改
git merge upstream/main

# 推送到您的Fork
git push origin main

# 更新功能分支（可选）
git checkout feature/your-feature-name
git rebase main
```

---

## 代码审查标准 | Code Review Standards

### 审查重点

所有Pull Request都会经过代码审查，审查重点包括：

#### 1. 内容准确性
- ✅ 技术内容准确无误
- ✅ 符合医疗器械软件标准
- ✅ 引用的标准和法规正确
- ✅ 代码示例正确且安全

#### 2. 内容完整性
- ✅ 包含所有必需的部分
- ✅ 至少5个自测问题
- ✅ 包含参考文献
- ✅ 代码示例有详细注释

#### 3. 格式规范
- ✅ Front Matter元数据完整
- ✅ Markdown格式正确
- ✅ 代码块指定了语言
- ✅ 链接使用相对路径

#### 4. 语言表达
- ✅ 语言清晰、简洁
- ✅ 中英文混排规范
- ✅ 术语使用一致
- ✅ 无拼写和语法错误

#### 5. 代码质量
- ✅ 代码完整、可编译
- ✅ 遵循编码规范
- ✅ 包含错误处理
- ✅ 有详细注释

#### 6. 链接有效性
- ✅ 内部链接指向存在的文件
- ✅ 外部链接可访问
- ✅ 使用相对路径

### 审查流程

1. **自动检查**：CI/CD自动运行验证脚本
2. **人工审查**：维护者审查内容质量
3. **反馈**：提供具体的修改建议
4. **修改**：贡献者根据反馈修改
5. **批准**：所有问题解决后批准PR
6. **合并**：合并到主分支

### 常见审查意见

| 问题 | 说明 | 解决方法 |
|------|------|----------|
| 缺少代码注释 | 代码示例没有足够的注释 | 添加详细的行内注释 |
| 自测问题不足 | 少于5个自测问题 | 添加更多问题 |
| 链接失效 | 内部链接指向不存在的文件 | 修正链接路径 |
| 术语不一致 | 同一概念使用不同术语 | 统一术语使用 |
| 缺少医疗器械考虑 | 没有说明医疗器械特定要求 | 添加相关说明 |


---

## 获取帮助 | Getting Help

### 文档资源

- **项目README**: [README.md](README.md) - 项目概述和快速开始
- **模板文件**: `docs/templates/module-template.md` - 知识模块模板
- **模板说明**: `docs/templates/README.md` - 模板使用详细说明
- **MkDocs文档**: [https://www.mkdocs.org/](https://www.mkdocs.org/)
- **Material主题文档**: [https://squidfunk.github.io/mkdocs-material/](https://squidfunk.github.io/mkdocs-material/)

### 提问渠道

如果您在贡献过程中遇到问题：

1. **搜索现有Issue**：问题可能已经被讨论过
2. **查看文档**：检查README和本贡献指南
3. **创建Issue**：如果找不到答案，创建新Issue提问
4. **GitHub Discussions**：参与社区讨论
5. **联系维护者**：通过Issue或邮件联系

### 常见问题 FAQ

#### Q1: 我不熟悉Git，如何开始？

**A**: 推荐以下资源学习Git基础：
- [Git官方教程](https://git-scm.com/book/zh/v2)
- [GitHub入门指南](https://docs.github.com/cn/get-started)
- 或者先从简单的文档修正开始，逐步学习

#### Q2: 我的英文不好，可以只贡献中文内容吗？

**A**: 当然可以！我们欢迎中文内容贡献。英文翻译可以由其他贡献者或维护者完成。

#### Q3: 我发现了错误但不知道如何修复，怎么办？

**A**: 请创建Issue报告错误，即使您不能修复它。报告问题也是重要的贡献！

#### Q4: 我想添加新内容，但不确定是否合适，怎么办？

**A**: 建议先创建Issue讨论您的想法，获得反馈后再开始编写。

#### Q5: 代码审查需要多长时间？

**A**: 通常在1-3个工作日内会有初步反馈。复杂的PR可能需要更长时间。

#### Q6: 我的PR被拒绝了，怎么办？

**A**: 不要气馁！查看拒绝原因，进行修改后可以重新提交。或者在Issue中讨论如何改进。

#### Q7: 如何成为项目维护者？

**A**: 持续贡献高质量内容，积极参与社区讨论。维护者会邀请活跃的贡献者加入维护团队。

#### Q8: 我可以使用AI工具（如ChatGPT）帮助编写内容吗？

**A**: 可以使用AI工具辅助，但必须：
- 仔细审查和验证AI生成的内容
- 确保技术准确性
- 确保符合医疗器械标准
- 最终内容由您负责

#### Q9: 如何处理版权和许可问题？

**A**: 
- 只提交您自己创作的内容或有权使用的内容
- 引用他人内容时注明出处
- 代码示例应使用项目许可证
- 不确定时请咨询维护者

#### Q10: 我想贡献但时间有限，有什么建议？

**A**: 小的贡献也很有价值！可以：
- 修正拼写错误
- 改进现有内容的表达
- 添加代码注释
- 报告问题
- 参与讨论

---

## 贡献者名单 | Contributors

感谢所有为本项目做出贡献的人！

<!-- 贡献者列表将自动生成 -->

### 如何出现在贡献者名单中

- 提交被合并的Pull Request
- 报告有价值的Issue
- 参与代码审查
- 改进文档
- 帮助其他贡献者

---

## 许可证 | License

通过贡献本项目，您同意您的贡献将按照项目许可证进行许可。

---

## 致谢 | Acknowledgments

感谢您考虑为医疗器械嵌入式软件知识体系做出贡献！您的努力将帮助更多开发者学习和掌握医疗器械软件开发的知识和技能。

---

## 附录：快速参考 | Quick Reference

### 常用命令

```bash
# 克隆和设置
git clone https://github.com/YOUR_USERNAME/medical-embedded-knowledge.git
cd medical-embedded-knowledge
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 创建分支
git checkout -b feature/your-feature-name

# 本地预览
mkdocs serve

# 验证
python scripts/validate_markdown.py
python scripts/run_all_validations.py

# 测试
pytest
pytest -v

# 提交
git add .
git commit -m "feat: 添加新模块"
git push origin feature/your-feature-name

# 同步上游
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

### 文件路径快速参考

```
docs/
├── zh/                                    # 中文内容
│   ├── technical-knowledge/               # 核心技术
│   │   ├── embedded-c-cpp/               # C/C++
│   │   ├── rtos/                         # RTOS
│   │   ├── hardware-interfaces/          # 硬件接口
│   │   ├── low-power-design/             # 低功耗
│   │   └── signal-processing/            # 信号处理
│   ├── regulatory-standards/              # 法规标准
│   │   ├── iec-62304/                    # IEC 62304
│   │   ├── iso-13485/                    # ISO 13485
│   │   ├── iso-14971/                    # ISO 14971
│   │   ├── fda-regulations/              # FDA
│   │   ├── iec-60601-1/                  # IEC 60601-1
│   │   └── iec-81001-5-1/                # IEC 81001-5-1
│   ├── software-engineering/              # 软件工程
│   ├── case-studies/                      # 案例研究
│   ├── learning-paths/                    # 学习路径
│   └── references/                        # 参考资料
├── en/                                    # 英文内容（结构同上）
├── templates/                             # 模板
│   ├── module-template.md                # 知识模块模板
│   └── README.md                         # 模板说明
└── assets/                                # 资源文件
    ├── images/                           # 图片
    └── css/                              # 样式
```

### Front Matter模板

```yaml
---
title: "模块标题"
description: "简短描述"
difficulty: "基础"  # 基础/中级/高级
estimated_time: "30分钟"
tags: ["标签1", "标签2"]
related_modules:
  - "相关模块路径"
last_updated: "2026-02-09"  # YYYY-MM-DD
version: "1.0"
language: "zh-CN"  # zh-CN 或 en-US
category: "技术"  # 技术/法规/工程
---
```

---

**最后更新**: 2026-02-09  
**版本**: 1.0  
**维护者**: 医疗器械嵌入式软件知识体系团队

---

<div align="center">
  <p>感谢您的贡献！Together we build better medical device software. 🚀</p>
</div>
