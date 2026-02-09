# 学习路径模板说明

## 概述

本目录包含学习路径的YAML配置模板，用于定义不同角色的系统化学习计划。

## 模板文件

- `path-template.yaml`: 学习路径配置的标准模板

## 配置格式说明

### 基本信息

- **path_id**: 路径的唯一标识符，使用kebab-case格式（如：embedded-engineer-path）
- **title**: 路径的中文标题
- **title_en**: 路径的英文标题（可选）
- **description**: 路径的详细描述
- **estimated_total_time**: 完成整个路径的预计时间
- **difficulty**: 难度级别（基础、中级、高级）
- **target_role**: 目标学习者角色

### 前置要求 (prerequisites)

列出学习者在开始此路径前应具备的基础知识和技能。

### 学习目标 (learning_objectives)

明确列出完成此路径后学习者应达到的能力目标。

### 学习阶段 (stages)

学习路径分为多个阶段，每个阶段包含：

- **stage**: 阶段编号（从1开始）
- **title**: 阶段标题
- **description**: 阶段描述
- **estimated_time**: 阶段预计学习时间
- **modules**: 该阶段包含的知识模块列表

#### 模块配置

每个模块包含：

- **id**: 模块的文件路径（相对于docs/目录，不含.md扩展名）
- **title**: 模块标题（可选，用于显示）
- **required**: 是否必修（true/false）
- **estimated_time**: 预计学习时间（可选）

### 检查点 (checkpoints)

在关键阶段后设置检查点，用于评估学习效果：

- **after_stage**: 在哪个阶段之后
- **title**: 检查点标题
- **assessment**: 评估方式描述
- **required_score**: 要求的最低分数（可选）

### 推荐资源 (recommended_resources)

列出额外的学习资源：

- **type**: 资源类型（book、course、tool、article等）
- **title**: 资源标题
- **url**: 资源链接

### 元数据 (metadata)

- **version**: 配置版本号
- **last_updated**: 最后更新日期
- **author**: 作者
- **status**: 状态（active、draft、archived）
- **tags**: 标签列表

## 使用指南

### 创建新的学习路径

1. 复制 `path-template.yaml` 文件
2. 重命名为 `[role-name]-path.yaml`（如：embedded-engineer-path.yaml）
3. 根据目标角色修改配置内容
4. 确保所有模块ID指向实际存在的文档文件
5. 运行验证脚本检查配置有效性

### 模块ID格式

模块ID应该是相对于 `docs/` 目录的路径，不包含 `.md` 扩展名。

示例：
- ✅ `technical-knowledge/rtos/task-scheduling`
- ✅ `regulatory-standards/iec-62304/index`
- ❌ `docs/technical-knowledge/rtos/task-scheduling.md`
- ❌ `/technical-knowledge/rtos/task-scheduling`

### 阶段设计建议

1. **循序渐进**: 从基础到高级，逐步深入
2. **模块化**: 每个阶段聚焦特定主题或技能
3. **实践导向**: 包含案例研究和实践练习
4. **检查点**: 在关键节点设置评估，确保学习效果

### 必修与选修

- **必修模块** (required: true): 核心知识，必须完成
- **选修模块** (required: false): 扩展知识，可根据兴趣选择

## 验证配置

使用渲染脚本验证配置文件：

```bash
python scripts/render_learning_paths.py --validate path-config.yaml
```

**说明**: 此命令用于验证学习路径配置文件的正确性。运行此脚本可以检查YAML文件的格式、必需字段、模块ID引用等是否符合规范，确保学习路径配置的质量。


## 示例

参考以下实际配置文件：

- `embedded-engineer-path.yaml`: 嵌入式软件工程师路径
- `qa-engineer-path.yaml`: 质量保证工程师路径
- `architect-path.yaml`: 系统架构师路径
- `regulatory-specialist-path.yaml`: 监管事务专员路径

## 最佳实践

1. **明确目标**: 清晰定义学习目标和前置要求
2. **合理时长**: 每个模块的学习时间应该实际可行
3. **平衡必修与选修**: 核心内容必修，扩展内容选修
4. **设置检查点**: 在关键阶段后评估学习效果
5. **提供资源**: 推荐额外的学习资源
6. **保持更新**: 定期更新配置以反映最新内容

## 相关文档

- [学习路径系统设计](../../design.md#学习路径管理组件)
- [需求文档 - 学习路径定制](../../requirements.md#需求-5学习路径定制)
