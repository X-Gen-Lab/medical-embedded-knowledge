# 知识模块模板使用指南

本目录包含医疗器械嵌入式软件知识体系的内容模板。

## 模板文件

### module-template.md

这是标准的知识模块模板，用于创建新的知识内容页面。

## 使用方法

1. **复制模板**
   ```bash
   cp docs/templates/module-template.md docs/[分类]/[子分类]/[模块名称].md
   ```

2. **填写Front Matter元数据**
   - `title`: 模块的标题
   - `description`: 1-2句话的简短描述
   - `difficulty`: 选择"基础"、"中级"或"高级"
   - `estimated_time`: 预计学习时间（如"30分钟"、"1小时"）
   - `tags`: 相关标签列表
   - `related_modules`: 相关模块的路径列表
   - `last_updated`: 最后更新日期（YYYY-MM-DD格式）
   - `version`: 版本号（如"1.0"）
   - `language`: 语言代码（"zh-CN"或"en-US"）
   - `category`: 分类（"技术"、"法规"或"工程"）

3. **填写内容**
   - 按照模板结构填写各个部分
   - 保持结构的一致性
   - 确保至少包含5个自测问题

4. **验证内容**
   ```bash
   python scripts/validate_markdown.py docs/[分类]/[子分类]/[模块名称].md
   ```

## Front Matter字段说明

### 必需字段

- **title** (string): 模块标题，应简洁明了
- **description** (string): 简短描述，用于搜索结果和卡片显示
- **difficulty** (enum): 难度级别
  - `基础`: 适合初学者
  - `中级`: 需要一定基础知识
  - `高级`: 需要深入的专业知识
- **estimated_time** (string): 预计学习时间
  - 格式示例: "30分钟"、"1小时"、"2小时"
- **tags** (array): 标签列表，用于分类和搜索
  - 示例: ["RTOS", "任务调度", "优先级"]
- **last_updated** (date): 最后更新日期
  - 格式: YYYY-MM-DD
- **version** (string): 版本号
  - 格式: "主版本.次版本"（如"1.0"、"1.1"）

### 可选字段

- **related_modules** (array): 相关模块路径列表
  - 使用相对路径
  - 示例: ["rtos/synchronization", "rtos/interrupt-handling"]
- **language** (string): 内容语言
  - 默认: "zh-CN"
  - 可选: "en-US"
- **category** (string): 内容分类
  - 可选值: "技术"、"法规"、"工程"

## 内容结构说明

### 1. 学习目标
- 列出3-5个具体的学习成果
- 使用"能够..."的句式
- 确保目标可衡量和可验证

### 2. 前置知识
- 列出学习本模块所需的前置知识
- 提供相关模块的链接
- 帮助学习者评估是否准备好学习本模块

### 3. 内容
- **概念介绍**: 简明扼要地介绍核心概念
- **详细说明**: 深入讲解技术细节
- **代码示例**: 提供可运行的代码，包含详细注释
- **最佳实践**: 总结行业最佳实践
- **常见陷阱**: 警告常见错误和问题
- **医疗器械特定考虑**: 强调医疗器械开发的特殊要求

### 4. 实践练习
- 提供至少2个实践练习
- 包含任务描述、提示和参考答案
- 帮助学习者巩固知识

### 5. 自测问题
- **必须包含至少5个问题**
- 使用选择题格式
- 提供详细的答案解析
- 使用折叠语法隐藏答案

### 6. 相关资源
- 链接到相关知识模块
- 提供深入学习的资源
- 链接到实践案例

### 7. 参考文献
- **必须包含参考文献部分**
- 包含标准文档、书籍、在线资源等
- 提供完整的引用信息

## Markdown扩展语法

本系统使用MkDocs Material主题，支持以下扩展语法：

### 提示框（Admonitions）

```markdown
!!! note "标题"
    内容

!!! tip "提示"
    内容

!!! warning "警告"
    内容

!!! danger "危险"
    内容

!!! info "信息"
    内容

!!! example "示例"
    内容
```

### 折叠内容

```markdown
??? question "问题"
    问题内容
    
    ??? success "答案"
        答案内容
```

### 代码高亮

```markdown
```c
// C代码
void function() {
    // 实现
}
\```

```python
# Python代码
def function():
    # 实现
    pass
\```
```

### 任务列表

```markdown
- [x] 已完成任务
- [ ] 未完成任务
```

### 表格

```markdown
| 列1 | 列2 | 列3 |
|-----|-----|-----|
| 值1 | 值2 | 值3 |
```

## 质量检查清单

在提交新模块之前，请确保：

- [ ] Front Matter包含所有必需字段
- [ ] difficulty值为"基础"、"中级"或"高级"之一
- [ ] 包含至少3个学习目标
- [ ] 包含前置知识说明
- [ ] 代码示例包含详细注释
- [ ] 包含至少5个自测问题
- [ ] 包含参考文献部分
- [ ] 所有内部链接有效
- [ ] 内容符合医疗器械行业标准
- [ ] 语言表达清晰、准确
- [ ] 格式符合模板要求

## 示例

参考以下已完成的模块作为示例：

- `docs/technical-knowledge/rtos/task-scheduling.md`
- `docs/regulatory-standards/iec-62304/software-classification.md`
- `docs/software-engineering/coding-standards/misra-c.md`

## 获取帮助

如有问题，请：
- 查看[贡献指南](../../CONTRIBUTING.md)
- 提交[Issue](链接)
- 联系维护团队

---

**最后更新**: 2026-02-07
