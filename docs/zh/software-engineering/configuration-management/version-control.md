---
title: 版本控制
description: 版本控制基础知识，包括Git工作流、分支策略、提交规范和医疗器械软件版本管理最佳实践
difficulty: 中级
estimated_time: 3小时
tags:
- 版本控制
- Git
- 分支策略
- 配置管理
related_modules:
- zh/software-engineering/configuration-management/baseline-management
- zh/software-engineering/requirements-engineering/change-management
- zh/software-engineering/coding-standards/code-review-checklist
last_updated: '2026-02-09'
version: '1.0'
language: zh-CN
---

# 版本控制

## 学习目标

完成本模块后，你将能够：
- 理解版本控制的概念和重要性
- 掌握Git基本操作和高级功能
- 应用适合医疗器械软件的分支策略
- 编写规范的提交信息
- 管理软件版本和发布
- 遵循IEC 62304对配置管理的要求

## 前置知识

- 基本的命令行操作
- 软件开发流程基础
- 团队协作概念
- IEC 62304标准基础知识

## 内容

### 版本控制基础

**版本控制定义**：
版本控制是一种记录文件内容变化，以便将来查阅特定版本修订情况的系统。

**版本控制的目的**：
- 跟踪代码变更历史
- 支持团队协作开发
- 管理不同版本和分支
- 支持代码回滚和恢复
- 实现变更可追溯性
- 满足法规要求（IEC 62304）

**版本控制系统类型**：

```
集中式版本控制（CVCS）：
- SVN、CVS
- 单一中央服务器
- 需要网络连接

分布式版本控制（DVCS）：
- Git、Mercurial
- 每个开发者都有完整仓库
- 支持离线工作
- 更灵活的工作流
```

**为什么选择Git**：
- 分布式架构，更可靠
- 强大的分支管理
- 快速的性能
- 广泛的工具支持
- 活跃的社区
- 适合医疗器械软件的可追溯性需求


### Git基础操作

#### 仓库初始化和配置

**创建新仓库**：

```bash
# 初始化新仓库
git init

# 或克隆现有仓库
git clone https://github.com/company/medical-device-software.git

# 配置用户信息
git config --global user.name "Zhang San"
git config --global user.email "zhangsan@company.com"

# 配置编辑器
git config --global core.editor "vim"

# 查看配置
git config --list
```


**基本工作流程**：

```bash
# 1. 查看状态
git status

# 2. 添加文件到暂存区
git add temperature_sensor.c
git add .  # 添加所有修改

# 3. 提交更改
git commit -m "feat: 添加温度传感器读取功能"

# 4. 查看提交历史
git log
git log --oneline --graph --all

# 5. 推送到远程仓库
git push origin main
```

**代码说明**：
- `git add`：将修改添加到暂存区
- `git commit`：创建提交记录
- `git push`：推送到远程仓库
- `git log`：查看提交历史


#### 分支管理

**分支基本操作**：

```bash
# 创建新分支
git branch feature/ecg-processing

# 切换分支
git checkout feature/ecg-processing

# 创建并切换（推荐）
git checkout -b feature/ecg-processing

# 查看所有分支
git branch -a

# 删除分支
git branch -d feature/ecg-processing

# 强制删除未合并分支
git branch -D feature/ecg-processing
```


**合并分支**：

```bash
# 切换到目标分支
git checkout main

# 合并功能分支
git merge feature/ecg-processing

# 如果有冲突，解决后：
git add resolved_file.c
git commit -m "merge: 合并ECG处理功能"
```

**变基操作**：

```bash
# 将当前分支变基到main
git checkout feature/blood-pressure
git rebase main

# 交互式变基（整理提交历史）
git rebase -i HEAD~3

# 继续变基
git rebase --continue

# 中止变基
git rebase --abort
```

**代码说明**：
- `merge`：保留完整历史，创建合并提交
- `rebase`：线性历史，更清晰但改写历史
- 医疗器械软件建议使用merge保留完整追溯


#### 远程仓库操作

```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add origin https://github.com/company/repo.git

# 获取远程更新
git fetch origin

# 拉取并合并
git pull origin main

# 推送分支
git push origin feature/alarm-system

# 推送标签
git push origin v1.0.0
git push origin --tags
```


### Git工作流

#### Git Flow工作流

Git Flow是一种适合发布周期明确的项目的分支策略，特别适合医疗器械软件。

**分支类型**：

```
主分支（长期存在）：
├── main (master)     - 生产环境代码，每个提交都是一个发布版本
└── develop          - 开发分支，包含最新的开发进度

支持分支（临时）：
├── feature/*        - 功能开发分支
├── release/*        - 发布准备分支
├── hotfix/*         - 紧急修复分支
└── bugfix/*         - Bug修复分支
```

**工作流程图**：

```
main      ●─────────●─────────────●──────────●
          │         │             │          │
          │    v1.0 │        v1.1 │     v1.2 │
          │         │             │          │
hotfix    │         │      ●──●───┘          │
          │         │      │  │              │
release   │    ●────┴──────┘  │              │
          │    │              │              │
develop   ●────●──●──●──●─────●──●──●────────●
               │  │  │  │        │  │
feature        └──┴──┴──┘        └──┘
```

**功能开发流程**：

```bash
# 1. 从develop创建功能分支
git checkout develop
git checkout -b feature/spo2-calculation

# 2. 开发功能
# ... 编写代码 ...
git add .
git commit -m "feat: 实现SpO2计算算法"

# 3. 完成后合并回develop
git checkout develop
git merge --no-ff feature/spo2-calculation

# 4. 删除功能分支
git branch -d feature/spo2-calculation

# 5. 推送到远程
git push origin develop
```

**代码说明**：
- `--no-ff`：禁用快进合并，保留分支历史
- 功能分支命名：`feature/功能描述`
- 每个功能独立开发，互不干扰


**发布流程**：

```bash
# 1. 从develop创建发布分支
git checkout develop
git checkout -b release/1.1.0

# 2. 更新版本号和文档
echo "1.1.0" > VERSION
git add VERSION
git commit -m "chore: 更新版本号到1.1.0"

# 3. 测试和修复bug
# ... 进行测试 ...
git commit -m "fix: 修复发布前发现的问题"

# 4. 合并到main并打标签
git checkout main
git merge --no-ff release/1.1.0
git tag -a v1.1.0 -m "Release version 1.1.0"

# 5. 合并回develop
git checkout develop
git merge --no-ff release/1.1.0

# 6. 删除发布分支
git branch -d release/1.1.0

# 7. 推送所有更改
git push origin main develop --tags
```

**紧急修复流程**：

```bash
# 1. 从main创建hotfix分支
git checkout main
git checkout -b hotfix/1.0.1

# 2. 修复问题
# ... 修复代码 ...
git commit -m "fix: 修复心率计算溢出问题"

# 3. 更新版本号
echo "1.0.1" > VERSION
git commit -m "chore: 更新版本号到1.0.1"

# 4. 合并到main并打标签
git checkout main
git merge --no-ff hotfix/1.0.1
git tag -a v1.0.1 -m "Hotfix version 1.0.1"

# 5. 合并到develop
git checkout develop
git merge --no-ff hotfix/1.0.1

# 6. 删除hotfix分支
git branch -d hotfix/1.0.1

# 7. 推送
git push origin main develop --tags
```


#### GitHub Flow工作流

GitHub Flow是一种更简单的工作流，适合持续部署的项目。

**工作流程**：

```
main      ●─────●─────●─────●─────●
          │     │     │     │     │
feature   └──●──┘     │     │     │
             │        │     │     │
feature      └────●───┘     │     │
                  │         │     │
feature           └─────●───┘     │
                        │         │
hotfix                  └─────●───┘
```

**操作步骤**：

```bash
# 1. 从main创建分支
git checkout main
git pull origin main
git checkout -b feature/alarm-enhancement

# 2. 开发并提交
git add .
git commit -m "feat: 增强报警功能"
git push origin feature/alarm-enhancement

# 3. 创建Pull Request（在GitHub上）
# - 描述变更内容
# - 请求代码审查
# - 运行CI/CD测试

# 4. 代码审查通过后合并
# - 在GitHub上点击"Merge"
# - 选择合并方式（Merge commit / Squash / Rebase）

# 5. 删除远程分支
git push origin --delete feature/alarm-enhancement

# 6. 本地清理
git checkout main
git pull origin main
git branch -d feature/alarm-enhancement
```

**代码说明**：
- 只有一个长期分支（main）
- 所有功能从main分支出来
- 通过Pull Request进行代码审查
- 合并后立即可部署


#### Trunk-Based Development

主干开发是一种所有开发者在单一主干（main/trunk）上协作的策略。

**特点**：
- 短生命周期分支（< 1天）
- 频繁集成到主干
- 使用特性开关（Feature Flags）
- 适合高频发布

**工作流程**：

```bash
# 1. 创建短期分支
git checkout -b short-lived-feature

# 2. 快速开发（几小时内完成）
git commit -m "feat: 添加新功能（使用特性开关）"

# 3. 尽快合并回主干
git checkout main
git merge short-lived-feature
git push origin main

# 4. 使用特性开关控制功能
# 代码中：
if (feature_flag_enabled("new_algorithm")) {
    use_new_algorithm();
} else {
    use_old_algorithm();
}
```

**适用场景**：
- 持续集成/持续部署（CI/CD）
- 快速迭代的项目
- 需要频繁发布的产品

**不适用场景**：
- 医疗器械软件（需要严格的发布流程）
- 长周期功能开发
- 需要多版本并行维护


### 分支策略选择

**医疗器械软件推荐：Git Flow**

| 工作流 | 适用场景 | 优点 | 缺点 |
|--------|---------|------|------|
| Git Flow | 医疗器械软件 | 清晰的发布流程<br/>支持多版本维护<br/>符合法规要求 | 相对复杂<br/>分支较多 |
| GitHub Flow | Web应用 | 简单易用<br/>快速部署 | 不适合多版本<br/>发布流程不明确 |
| Trunk-Based | 互联网产品 | 持续集成<br/>快速迭代 | 需要成熟的CI/CD<br/>不适合医疗器械 |

**选择建议**：

```
医疗器械软件（IEC 62304 Class B/C）：
✓ 使用Git Flow
✓ 严格的分支管理
✓ 完整的发布流程
✓ 支持多版本维护

一般软件工具：
✓ 使用GitHub Flow
✓ 简化流程
✓ 快速迭代
```

**说明**: 这是不同类型软件的分支策略选择建议。医疗器械软件(IEC 62304 Class B/C)需要严格的分支管理和完整的发布流程，支持多版本维护；一般软件工具可以使用简化的GitHub Flow，快速迭代。



### 提交规范

#### Conventional Commits规范

规范的提交信息对于医疗器械软件的可追溯性至关重要。

**提交信息格式**：

```
<类型>(<范围>): <简短描述>

<详细描述>

<页脚>
```

**类型（Type）**：

```
feat:     新功能
fix:      Bug修复
docs:     文档更新
style:    代码格式（不影响功能）
refactor: 重构（不是新功能也不是修复）
perf:     性能优化
test:     测试相关
chore:    构建过程或辅助工具的变动
revert:   回滚之前的提交
```

**示例**：

```bash
# 新功能
git commit -m "feat(ecg): 添加ECG信号滤波功能

实现了50Hz陷波滤波器，用于去除工频干扰。
算法基于IIR滤波器设计。

Refs: REQ-ECG-001"

# Bug修复
git commit -m "fix(alarm): 修复心率报警阈值判断错误

之前的实现在边界值时判断不正确。
修改为使用>而不是>=。

Fixes: BUG-123
Refs: REQ-ALARM-002"

# 文档更新
git commit -m "docs: 更新API文档

添加了新的传感器接口说明"

# 重构
git commit -m "refactor(sensor): 重构传感器读取模块

提取公共代码到基类，提高代码复用性。
不改变外部接口。"
```


**提交信息最佳实践**：

```bash
# 好的提交信息
git commit -m "feat(bp): 实现血压测量算法

- 实现示波法血压测量
- 添加数据验证
- 包含单元测试

Refs: REQ-BP-001, REQ-BP-002"

# 不好的提交信息
git commit -m "修改代码"
git commit -m "fix bug"
git commit -m "update"
```

**提交信息规则**：

```
✓ 使用现在时态："添加功能"而不是"添加了功能"
✓ 首字母小写
✓ 简短描述不超过50字符
✓ 详细描述每行不超过72字符
✓ 包含需求追溯（Refs: REQ-XXX）
✓ 包含问题追溯（Fixes: BUG-XXX）
✓ 说明"为什么"而不只是"做了什么"
```

**说明**: 这是提交信息的最佳实践规范。包括使用现在时态、首字母小写、限制长度、包含需求和问题追溯、说明原因等要求，确保提交历史清晰可读且可追溯。


#### 提交粒度

**原则**：一个提交只做一件事

```bash
# 好的做法：分开提交
git add sensor.c
git commit -m "feat(sensor): 添加温度传感器支持"

git add alarm.c
git commit -m "feat(alarm): 添加温度报警功能"

# 不好的做法：混合提交
git add sensor.c alarm.c display.c
git commit -m "添加多个功能"
```

**提交前检查**：

```bash
# 查看将要提交的内容
git diff --staged

# 部分提交
git add -p  # 交互式选择要提交的部分

# 修改最后一次提交
git commit --amend

# 拆分大的修改
git add file1.c
git commit -m "feat: 功能A"
git add file2.c
git commit -m "feat: 功能B"
```


### 版本标签管理

#### 语义化版本（Semantic Versioning）

医疗器械软件应使用语义化版本号。

**版本号格式**：`主版本号.次版本号.修订号` (MAJOR.MINOR.PATCH)

```
版本号：v1.2.3
        │ │ │
        │ │ └─ PATCH：向后兼容的问题修正
        │ └─── MINOR：向后兼容的功能性新增
        └───── MAJOR：不兼容的API修改
```

**版本号递增规则**：

```
1.0.0 → 1.0.1  修复bug
1.0.1 → 1.1.0  添加新功能（向后兼容）
1.1.0 → 2.0.0  重大变更（不向后兼容）
```

**创建标签**：

```bash
# 轻量标签
git tag v1.0.0

# 附注标签（推荐）
git tag -a v1.0.0 -m "Release version 1.0.0

主要功能：
- ECG信号采集和处理
- 心率计算和显示
- 异常心率报警

测试状态：
- 单元测试：通过
- 集成测试：通过
- 系统测试：通过

符合标准：
- IEC 62304 Class B
- IEC 60601-1

审批：
- 开发负责人：张三
- 质量负责人：李四
- 日期：2026-02-09"

# 推送标签
git push origin v1.0.0
git push origin --tags

# 查看标签
git tag -l
git show v1.0.0

# 检出特定版本
git checkout v1.0.0
```


**预发布版本**：

```bash
# Alpha版本（内部测试）
git tag -a v1.0.0-alpha.1 -m "Alpha release for internal testing"

# Beta版本（外部测试）
git tag -a v1.0.0-beta.1 -m "Beta release for external testing"

# Release Candidate（发布候选）
git tag -a v1.0.0-rc.1 -m "Release candidate 1"

# 正式版本
git tag -a v1.0.0 -m "Official release"
```

**版本号示例**：

```
开发阶段：
v0.1.0-dev
v0.2.0-dev

测试阶段：
v1.0.0-alpha.1
v1.0.0-alpha.2
v1.0.0-beta.1
v1.0.0-rc.1

发布版本：
v1.0.0
v1.0.1  (bug修复)
v1.1.0  (新功能)
v2.0.0  (重大更新)
```

**说明**: 这是不同开发阶段的版本号示例。开发阶段使用-dev后缀，测试阶段使用-alpha、-beta、-rc后缀，正式发布使用纯数字版本号，清晰标识软件的成熟度。



### 医疗器械软件版本控制最佳实践

#### 1. 符合IEC 62304要求

**配置管理要求**：

```
IEC 62304 5.1.1 - 配置管理计划：
✓ 定义配置项
✓ 建立版本控制系统
✓ 定义分支策略
✓ 定义变更控制流程

IEC 62304 5.1.9 - 配置管理：
✓ 识别配置项
✓ 控制配置项的修改
✓ 记录配置项的状态
✓ 实施配置审核
```

**实施示例**：

```bash
# 配置项标识
# 每个文件都在版本控制中
git add src/ecg_processor.c
git commit -m "feat(ecg): 添加ECG处理模块

配置项ID: CI-ECG-001
需求追溯: REQ-ECG-001
设计追溯: DES-ECG-001"

# 变更控制
# 所有变更通过Pull Request
# 需要代码审查和批准
```


#### 2. 可追溯性管理

**需求追溯**：

```bash
# 提交信息中包含需求ID
git commit -m "feat(alarm): 实现心率报警功能

实现了心率超过阈值时的报警功能。

需求追溯：
- REQ-ALARM-001: 心率报警功能
- REQ-ALARM-002: 报警阈值配置

设计追溯：
- DES-ALARM-001: 报警模块设计

测试追溯：
- TEST-ALARM-001: 心率报警测试用例"

# 使用Git Notes添加追溯信息
git notes add -m "需求: REQ-ALARM-001
设计: DES-ALARM-001
测试: TEST-ALARM-001"
```

**追溯矩阵生成**：

```bash
# 从Git历史生成追溯矩阵
git log --all --grep="REQ-" --pretty=format:"%h %s" > traceability.txt

# 使用脚本自动生成追溯报告
#!/bin/bash
echo "需求ID,提交ID,提交信息" > traceability.csv
git log --all --grep="REQ-" --pretty=format:"%h,%s" >> traceability.csv
```

#### 3. 代码审查流程

**Pull Request模板**：

```markdown
## 变更描述
简要描述本次变更的内容和目的。

## 变更类型
- [ ] 新功能
- [ ] Bug修复
- [ ] 文档更新
- [ ] 重构
- [ ] 性能优化

## 需求追溯
- REQ-XXX-XXX: 需求描述

## 测试
- [ ] 单元测试已通过
- [ ] 集成测试已通过
- [ ] 代码覆盖率 ≥ 80%

## 检查清单
- [ ] 代码符合编码规范
- [ ] 已添加必要的注释
- [ ] 已更新相关文档
- [ ] 无编译警告
- [ ] 静态分析无问题

## 审查者
@reviewer1 @reviewer2
```


**代码审查流程**：

```bash
# 1. 创建功能分支
git checkout -b feature/new-sensor

# 2. 开发并提交
git commit -m "feat(sensor): 添加新传感器支持"

# 3. 推送到远程
git push origin feature/new-sensor

# 4. 创建Pull Request
# 在GitHub/GitLab上创建PR

# 5. 代码审查
# 审查者检查代码质量、测试覆盖率等

# 6. 修改反馈
git commit -m "fix: 根据审查意见修改"
git push origin feature/new-sensor

# 7. 审查通过后合并
# 在平台上点击"Merge"

# 8. 删除分支
git push origin --delete feature/new-sensor
```

#### 4. 分支保护规则

**保护主要分支**：

```yaml
# GitHub分支保护规则示例
main:
  protected: true
  require_pull_request: true
  required_approving_reviews: 2
  dismiss_stale_reviews: true
  require_code_owner_reviews: true
  require_status_checks: true
  required_status_checks:
    - continuous-integration
    - code-coverage
    - static-analysis
  enforce_admins: true
  restrict_pushes: true

develop:
  protected: true
  require_pull_request: true
  required_approving_reviews: 1
  require_status_checks: true
```

**实施方法**：

```bash
# 在GitHub上设置分支保护
# Settings → Branches → Add rule

# 规则示例：
# - Require pull request reviews before merging
# - Require status checks to pass before merging
# - Require branches to be up to date before merging
# - Include administrators
```


#### 5. 持续集成配置

**GitHub Actions示例**：

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: 设置编译环境
      run: |
        sudo apt-get update
        sudo apt-get install -y gcc-arm-none-eabi
    
    - name: 编译代码
      run: make all
    
    - name: 运行单元测试
      run: make test
    
    - name: 代码覆盖率检查
      run: |
        make coverage
        if [ $(cat coverage.txt | grep -oP '\d+(?=%)') -lt 80 ]; then
          echo "代码覆盖率低于80%"
          exit 1
        fi
    
    - name: 静态分析
      run: |
        cppcheck --enable=all --error-exitcode=1 src/
    
    - name: MISRA C检查
      run: |
        misra-checker src/
    
    - name: 生成构建报告
      if: always()
      uses: actions/upload-artifact@v2
      with:
        name: build-report
        path: |
          build/
          coverage/
          test-results/
```


#### 6. .gitignore配置

**医疗器械项目.gitignore示例**：

```gitignore
# 编译输出
*.o
*.elf
*.hex
*.bin
*.map
build/
dist/

# 调试文件
*.dSYM/
*.su
*.idb
*.pdb

# IDE配置
.vscode/
.idea/
*.swp
*.swo
*~

# 测试覆盖率
*.gcda
*.gcno
*.gcov
coverage/
htmlcov/

# 文档生成
docs/_build/
*.pdf

# 临时文件
*.tmp
*.bak
*.log

# 操作系统文件
.DS_Store
Thumbs.db

# 但要包含重要配置
!.vscode/settings.json
!docs/requirements/

# 敏感信息
secrets.txt
*.key
*.pem
```

**代码说明**：
- 不提交编译产物
- 不提交IDE配置（除非团队统一）
- 不提交敏感信息
- 保留重要的配置文件


### 常见问题和解决方案

#### 合并冲突处理

```bash
# 1. 拉取最新代码时发生冲突
git pull origin main
# Auto-merging sensor.c
# CONFLICT (content): Merge conflict in sensor.c

# 2. 查看冲突文件
git status
# both modified: sensor.c

# 3. 打开文件解决冲突
# 文件中会显示：
<<<<<<< HEAD
int read_sensor() {
    return adc_read(0);
}
=======
int read_sensor() {
    return adc_read_channel(0);
}
>>>>>>> origin/main

# 4. 手动编辑，保留正确的代码
int read_sensor() {
    return adc_read_channel(0);
}

# 5. 标记为已解决
git add sensor.c

# 6. 完成合并
git commit -m "merge: 解决sensor.c合并冲突"
```


#### 撤销和恢复

```bash
# 撤销工作区修改
git checkout -- file.c

# 撤销暂存区修改
git reset HEAD file.c

# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃修改）
git reset --hard HEAD~1

# 撤销某个提交（创建新提交）
git revert <commit-hash>

# 恢复删除的文件
git checkout HEAD -- deleted_file.c

# 恢复到特定版本
git checkout <commit-hash> -- file.c
```

#### 查找问题提交

```bash
# 使用git bisect二分查找
git bisect start
git bisect bad                 # 当前版本有问题
git bisect good v1.0.0        # v1.0.0版本正常

# Git会自动切换到中间版本
# 测试后标记
git bisect good  # 或 git bisect bad

# 重复直到找到问题提交
# 结束后
git bisect reset

# 查找谁修改了某行代码
git blame sensor.c

# 查找删除某个函数的提交
git log -S "function_name" --source --all
```

#### 清理历史

```bash
# 清理未跟踪的文件
git clean -n  # 预览
git clean -f  # 执行清理

# 清理未跟踪的文件和目录
git clean -fd

# 压缩历史（交互式变基）
git rebase -i HEAD~5

# 在编辑器中：
# pick  → 保留提交
# squash → 合并到前一个提交
# drop  → 删除提交

# 删除敏感信息（慎用！）
git filter-branch --tree-filter 'rm -f passwords.txt' HEAD
```


### 最佳实践

!!! tip "版本控制最佳实践"
    
    **1. 频繁提交**
    - 每完成一个小功能就提交
    - 提交粒度要小
    - 便于回滚和追溯
    
    **2. 有意义的提交信息**
    - 使用规范的格式
    - 说明"为什么"而不只是"做了什么"
    - 包含需求追溯
    
    **3. 保持主分支稳定**
    - main分支始终可发布
    - 所有开发在功能分支进行
    - 通过CI/CD保证质量
    
    **4. 代码审查**
    - 所有代码合并前必须审查
    - 至少一人审查（关键代码两人）
    - 使用Pull Request流程
    
    **5. 定期同步**
    - 每天至少一次拉取最新代码
    - 及时解决冲突
    - 避免长期分支
    
    **6. 使用标签管理版本**
    - 每次发布打标签
    - 使用语义化版本号
    - 标签信息要详细
    
    **7. 保护敏感信息**
    - 不提交密码、密钥
    - 使用.gitignore
    - 使用环境变量
    
    **8. 文档化流程**
    - 编写Git工作流文档
    - 培训团队成员
    - 统一操作规范


### 常见陷阱

!!! warning "注意事项"
    
    **1. 直接在main分支开发**
    ```bash
    # 错误
    git checkout main
    # 直接修改代码...
    git commit -m "修改"
    
    # 正确
    git checkout -b feature/new-feature
    # 修改代码...
    git commit -m "feat: 添加新功能"
    ```
    
    **2. 提交信息不规范**
    ```bash
    # 错误
    git commit -m "修改"
    git commit -m "fix"
    git commit -m "update code"
    
    # 正确
    git commit -m "fix(sensor): 修复温度读取溢出问题
    
    修复了在极端温度下的整数溢出问题。
    
    Fixes: BUG-123
    Refs: REQ-TEMP-001"
    ```

    
    **3. 提交大量无关文件**
    ```bash
    # 错误
    git add .
    git commit -m "提交所有文件"
    # 包含了编译产物、临时文件等
    
    # 正确
    # 配置.gitignore
    git add src/sensor.c
    git commit -m "feat: 添加传感器模块"
    ```
    
    **4. 强制推送覆盖历史**
    ```bash
    # 危险！会覆盖远程历史
    git push -f origin main
    
    # 更安全的方式
    git push --force-with-lease origin main
    # 或者避免强制推送
    ```
    
    **5. 不及时解决冲突**
    ```bash
    # 错误：长期不合并主分支
    # 功能分支开发3个月，从不合并main
    # 最后合并时冲突巨大
    
    # 正确：定期合并主分支
    git checkout feature/long-term
    git merge main  # 每周至少一次
    ```
    
    **6. 在错误的分支工作**
    ```bash
    # 错误：在main分支开发
    # 发现后：
    git stash  # 暂存修改
    git checkout -b feature/correct-branch
    git stash pop  # 恢复修改
    ```
    
    **7. 提交敏感信息**
    ```bash
    # 错误：提交了密码
    git commit -m "添加配置" config.txt
    # config.txt包含密码
    
    # 补救：
    git filter-branch --tree-filter 'rm -f config.txt' HEAD
    # 或使用git-filter-repo工具
    
    # 预防：使用.gitignore和环境变量
    ```
    
    **8. 不使用分支保护**
    ```bash
    # 问题：任何人都能直接推送到main
    
    # 解决：设置分支保护规则
    # - 要求Pull Request
    # - 要求代码审查
    # - 要求CI通过
    ```


## 实践练习

1. **基础练习**：创建一个Git仓库，实践基本的提交、分支、合并操作。

2. **中级练习**：使用Git Flow工作流开发一个功能：
   - 从develop创建feature分支
   - 开发并提交代码
   - 创建release分支
   - 合并到main并打标签
   - 合并回develop

3. **高级练习**：建立完整的版本控制流程：
   - 配置分支保护规则
   - 设置Pull Request模板
   - 配置CI/CD流水线
   - 实施代码审查流程

4. **综合练习**：模拟医疗器械软件发布流程：
   - 使用Git Flow管理开发
   - 实现需求追溯
   - 生成追溯矩阵
   - 创建发布标签
   - 生成发布文档


## 自测问题

??? question "问题1：什么是Git Flow工作流？它包含哪些分支类型？"
    **问题**：解释Git Flow工作流的概念，并说明各种分支的用途。
    
    ??? success "答案"
        **Git Flow定义**：
        Git Flow是一种适合发布周期明确的项目的分支管理策略，特别适合医疗器械软件开发。
        
        **分支类型**：
        
        **1. 主分支（长期存在）**：
        
        **main（master）分支**：
        - 用途：生产环境代码
        - 特点：每个提交都是一个发布版本
        - 保护：严格保护，只能通过合并更新
        - 标签：每次合并都打版本标签
        
        **develop分支**：
        - 用途：开发主分支
        - 特点：包含最新的开发进度
        - 来源：从main分支创建
        - 合并：接收feature分支的合并
        
        **2. 支持分支（临时）**：
        
        **feature分支**：
        ```bash
        # 命名：feature/功能名称
        # 示例：feature/ecg-processing
        
        # 创建：从develop分支
        git checkout develop
        git checkout -b feature/new-sensor
        
        # 合并：回到develop分支
        git checkout develop
        git merge --no-ff feature/new-sensor
        ```
        
        **release分支**：
        ```bash
        # 命名：release/版本号
        # 示例：release/1.1.0
        
        # 创建：从develop分支
        git checkout develop
        git checkout -b release/1.1.0
        
        # 用途：
        # - 准备发布
        # - 修复小bug
        # - 更新版本号
        # - 更新文档
        
        # 合并：到main和develop
        git checkout main
        git merge --no-ff release/1.1.0
        git tag -a v1.1.0
        
        git checkout develop
        git merge --no-ff release/1.1.0
        ```
        
        **hotfix分支**：
        ```bash
        # 命名：hotfix/版本号
        # 示例：hotfix/1.0.1
        
        # 创建：从main分支
        git checkout main
        git checkout -b hotfix/1.0.1
        
        # 用途：紧急修复生产环境bug
        
        # 合并：到main和develop
        git checkout main
        git merge --no-ff hotfix/1.0.1
        git tag -a v1.0.1
        
        git checkout develop
        git merge --no-ff hotfix/1.0.1
        ```
        
        **工作流程图**：
        ```
        main      ●─────────●─────────────●──────────●
                  │    v1.0 │        v1.1 │     v1.2 │
        hotfix    │         │      ●──●───┘          │
        release   │    ●────┴──────┘  │              │
        develop   ●────●──●──●──●─────●──●──●────────●
        feature        └──┴──┴──┘        └──┘
        ```
        
        **优势**：
        - 清晰的发布流程
        - 支持多版本并行维护
        - 适合医疗器械软件的法规要求
        - 便于追溯和审计
        
        **知识点回顾**：Git Flow通过明确的分支策略，实现了清晰的开发和发布流程。

??? question "问题2：什么是语义化版本？如何正确使用版本号？"
    **问题**：解释语义化版本的概念和版本号递增规则。
    
    ??? success "答案"
        **语义化版本定义**：
        语义化版本（Semantic Versioning）是一种版本号命名规范，格式为：主版本号.次版本号.修订号（MAJOR.MINOR.PATCH）。
        
        **版本号格式**：
        ```
        v1.2.3
         │ │ │
         │ │ └─ PATCH：向后兼容的问题修正
         │ └─── MINOR：向后兼容的功能性新增
         └───── MAJOR：不兼容的API修改
        ```
        
        **递增规则**：
        
        **MAJOR（主版本号）**：
        - 何时递增：不兼容的API修改
        - 示例：
          ```
          v1.5.3 → v2.0.0
          
          原因：
          - 删除了旧的API
          - 修改了函数签名
          - 重大架构变更
          ```
        
        **MINOR（次版本号）**：
        - 何时递增：向后兼容的功能新增
        - 示例：
          ```
          v1.2.5 → v1.3.0
          
          原因：
          - 添加了新功能
          - 添加了新API
          - 标记某些功能为废弃（但仍可用）
          ```
        
        **PATCH（修订号）**：
        - 何时递增：向后兼容的问题修正
        - 示例：
          ```
          v1.2.3 → v1.2.4
          
          原因：
          - 修复bug
          - 性能优化
          - 文档更新
          ```
        
        **预发布版本**：
        ```
        v1.0.0-alpha.1   # Alpha版本（内部测试）
        v1.0.0-beta.1    # Beta版本（外部测试）
        v1.0.0-rc.1      # Release Candidate（发布候选）
        v1.0.0           # 正式版本
        ```
        
        **版本号比较**：
        ```
        1.0.0 < 1.0.1 < 1.1.0 < 2.0.0
        
        1.0.0-alpha < 1.0.0-beta < 1.0.0-rc.1 < 1.0.0
        ```
        
        **医疗器械软件版本管理**：
        ```
        开发阶段：
        v0.1.0-dev
        v0.2.0-dev
        
        测试阶段：
        v1.0.0-alpha.1  # 内部测试
        v1.0.0-beta.1   # 外部测试
        v1.0.0-rc.1     # 发布候选
        
        发布版本：
        v1.0.0          # 首次发布
        v1.0.1          # Bug修复
        v1.1.0          # 新功能
        v2.0.0          # 重大更新
        ```
        
        **Git标签创建**：
        ```bash
        # 创建附注标签
        git tag -a v1.0.0 -m "Release version 1.0.0
        
        主要功能：
        - ECG信号处理
        - 心率监测
        - 异常报警
        
        符合标准：
        - IEC 62304 Class B
        - IEC 60601-1"
        
        # 推送标签
        git push origin v1.0.0
        ```
        
        **版本号选择建议**：
        - 0.x.x：开发阶段，API不稳定
        - 1.0.0：首次公开发布
        - 1.x.x：稳定版本，向后兼容
        - 2.0.0：重大变更，不向后兼容
        
        **知识点回顾**：语义化版本通过规范的版本号，清晰地传达了版本间的兼容性信息。

??? question "问题3：什么是Conventional Commits？如何编写规范的提交信息？"
    **问题**：解释Conventional Commits规范，并给出提交信息示例。
    
    ??? success "答案"
        **Conventional Commits定义**：
        Conventional Commits是一种提交信息规范，通过结构化的提交信息，使提交历史更易读、更易于自动化处理。
        
        **提交信息格式**：
        ```
        <类型>(<范围>): <简短描述>
        
        <详细描述>
        
        <页脚>
        ```
        
        **类型（Type）**：
        ```
        feat:     新功能
        fix:      Bug修复
        docs:     文档更新
        style:    代码格式（不影响功能）
        refactor: 重构
        perf:     性能优化
        test:     测试相关
        chore:    构建过程或辅助工具
        revert:   回滚提交
        ```
        
        **范围（Scope）**：
        - 可选字段
        - 指明修改的模块或组件
        - 示例：ecg, alarm, sensor, ui
        
        **示例1：新功能**：
        ```bash
        git commit -m "feat(ecg): 添加ECG信号滤波功能
        
        实现了50Hz陷波滤波器，用于去除工频干扰。
        算法基于IIR滤波器设计，满足IEC 60601-2-27要求。
        
        需求追溯：
        - REQ-ECG-001: ECG信号处理
        - REQ-ECG-002: 噪声滤除
        
        测试：
        - 单元测试覆盖率：95%
        - 集成测试：通过"
        ```
        
        **示例2：Bug修复**：
        ```bash
        git commit -m "fix(alarm): 修复心率报警阈值判断错误
        
        问题描述：
        在边界值（200 bpm）时，报警未正确触发。
        
        根本原因：
        使用了>而不是>=进行判断。
        
        修复方法：
        将判断条件从 hr > 200 改为 hr >= 200。
        
        影响范围：
        - 仅影响报警模块
        - 不影响其他功能
        
        Fixes: BUG-123
        Refs: REQ-ALARM-002"
        ```
        
        **示例3：重构**：
        ```bash
        git commit -m "refactor(sensor): 重构传感器读取模块
        
        重构内容：
        - 提取公共代码到基类
        - 统一错误处理
        - 改进命名
        
        影响：
        - 不改变外部接口
        - 提高代码复用性
        - 降低维护成本
        
        测试：
        - 所有现有测试通过
        - 无功能变更"
        ```
        
        **提交信息规则**：
        ```
        ✓ 使用现在时态："添加"而不是"添加了"
        ✓ 首字母小写
        ✓ 简短描述不超过50字符
        ✓ 详细描述每行不超过72字符
        ✓ 包含需求追溯（Refs: REQ-XXX）
        ✓ 包含问题追溯（Fixes: BUG-XXX）
        ✓ 说明"为什么"而不只是"做了什么"
        ✓ 一个提交只做一件事
        ```
        
        **不好的提交信息**：
        ```bash
        # 太简单
        git commit -m "修改代码"
        git commit -m "fix bug"
        git commit -m "update"
        
        # 太复杂（应该拆分）
        git commit -m "添加新功能、修复bug、更新文档"
        
        # 没有上下文
        git commit -m "修改sensor.c"
        ```
        
        **好的提交信息**：
        ```bash
        git commit -m "feat(bp): 实现血压测量算法
        
        实现了示波法血压测量算法：
        - 充气和放气控制
        - 脉搏波检测
        - 收缩压和舒张压计算
        
        算法参考：
        - AAMI SP10标准
        - 《无创血压测量技术》
        
        Refs: REQ-BP-001, REQ-BP-002
        
        测试：
        - 单元测试：通过
        - 准确性测试：±5mmHg"
        ```
        
        **自动化应用**：
        ```bash
        # 自动生成CHANGELOG
        git log --pretty=format:"%s" | grep "^feat" > CHANGELOG.md
        
        # 自动确定版本号
        # feat → MINOR版本递增
        # fix → PATCH版本递增
        # BREAKING CHANGE → MAJOR版本递增
        ```
        
        **知识点回顾**：规范的提交信息提高了代码历史的可读性，支持自动化工具，便于追溯和审计。


??? question "问题4：如何处理Git合并冲突？"
    **问题**：解释合并冲突的原因和解决方法。
    
    ??? success "答案"
        **合并冲突原因**：
        当两个分支修改了同一文件的同一部分，Git无法自动合并时，就会产生冲突。
        
        **冲突场景示例**：
        ```
        main分支：
        int read_sensor() {
            return adc_read(0);
        }
        
        feature分支：
        int read_sensor() {
            return adc_read_channel(0);
        }
        
        合并时：Git不知道保留哪个版本
        ```
        
        **冲突标记**：
        ```c
        int read_sensor() {
        <<<<<<< HEAD
            return adc_read(0);
        =======
            return adc_read_channel(0);
        >>>>>>> feature/new-sensor
        }
        ```
        
        **标记说明**：
        - `<<<<<<< HEAD`：当前分支的内容开始
        - `=======`：分隔符
        - `>>>>>>> feature/new-sensor`：合并分支的内容结束
        
        **解决步骤**：
        
        **1. 识别冲突**：
        ```bash
        git merge feature/new-sensor
        # Auto-merging sensor.c
        # CONFLICT (content): Merge conflict in sensor.c
        # Automatic merge failed; fix conflicts and then commit the result.
        
        # 查看冲突文件
        git status
        # both modified: sensor.c
        ```
        
        **2. 打开文件解决冲突**：
        ```c
        // 原始冲突标记
        int read_sensor() {
        <<<<<<< HEAD
            return adc_read(0);
        =======
            return adc_read_channel(0);
        >>>>>>> feature/new-sensor
        }
        
        // 解决后（保留正确的版本）
        int read_sensor() {
            return adc_read_channel(0);
        }
        ```
        
        **3. 标记为已解决**：
        ```bash
        git add sensor.c
        ```
        
        **4. 完成合并**：
        ```bash
        git commit -m "merge: 解决sensor.c合并冲突
        
        冲突原因：
        - main分支使用adc_read()
        - feature分支使用adc_read_channel()
        
        解决方案：
        - 采用feature分支的实现
        - adc_read_channel()提供更好的灵活性
        
        测试：
        - 单元测试通过
        - 集成测试通过"
        ```
        
        **冲突解决策略**：
        
        **策略1：保留一方**：
        ```bash
        # 保留当前分支（ours）
        git checkout --ours sensor.c
        git add sensor.c
        
        # 保留合并分支（theirs）
        git checkout --theirs sensor.c
        git add sensor.c
        ```
        
        **策略2：手动合并**：
        ```c
        // 结合两个版本的优点
        int read_sensor() {
            // 使用新的API，但添加错误检查
            int result = adc_read_channel(0);
            if (result < 0) {
                log_error("ADC read failed");
                return -1;
            }
            return result;
        }
        ```
        
        **策略3：使用合并工具**：
        ```bash
        # 配置合并工具
        git config --global merge.tool vimdiff
        
        # 使用工具解决冲突
        git mergetool
        ```
        
        **预防冲突**：
        
        **1. 频繁同步**：
        ```bash
        # 每天至少一次
        git checkout feature/my-feature
        git merge main
        ```
        
        **2. 小步提交**：
        ```bash
        # 频繁提交小的改动
        # 而不是一次提交大量修改
        ```
        
        **3. 沟通协调**：
        ```
        - 团队成员之间沟通
        - 避免同时修改同一文件
        - 使用代码所有者机制
        ```
        
        **4. 模块化设计**：
        ```
        - 清晰的模块边界
        - 减少文件间依赖
        - 降低冲突概率
        ```
        
        **复杂冲突处理**：
        ```bash
        # 如果冲突太复杂，可以中止合并
        git merge --abort
        
        # 重新规划合并策略
        # 或寻求团队帮助
        ```
        
        **知识点回顾**：合并冲突是正常现象，通过理解冲突标记、选择合适的解决策略，可以安全地解决冲突。

??? question "问题5：医疗器械软件版本控制有哪些特殊要求？"
    **问题**：说明医疗器械软件在版本控制方面需要满足的法规要求和最佳实践。
    
    ??? success "答案"
        **IEC 62304配置管理要求**：
        
        **5.1.1 配置管理计划**：
        ```
        必须建立配置管理计划，包括：
        ✓ 配置项识别
        ✓ 变更控制
        ✓ 配置状态记录
        ✓ 配置审核
        ```
        
        **5.1.9 配置管理**：
        ```
        必须：
        ✓ 识别所有配置项
        ✓ 控制配置项的修改
        ✓ 记录配置项的状态
        ✓ 实施配置审核
        ```
        
        **实施要求**：
        
        **1. 完整的可追溯性**：
        ```bash
        # 提交信息必须包含追溯信息
        git commit -m "feat(ecg): 实现ECG信号处理
        
        需求追溯：
        - REQ-ECG-001: ECG信号采集
        - REQ-ECG-002: 信号滤波
        
        设计追溯：
        - DES-ECG-001: ECG处理模块设计
        
        测试追溯：
        - TEST-ECG-001: ECG处理单元测试
        - TEST-ECG-002: ECG处理集成测试
        
        风险追溯：
        - RISK-ECG-001: 信号失真风险"
        ```
        
        **2. 严格的变更控制**：
        ```yaml
        # 分支保护规则
        main:
          protected: true
          require_pull_request: true
          required_approving_reviews: 2  # 至少2人审查
          require_code_owner_reviews: true
          require_status_checks: true
          required_status_checks:
            - unit-tests
            - integration-tests
            - code-coverage
            - static-analysis
            - misra-check
        ```
        
        **3. 完整的审计追踪**：
        ```bash
        # 所有变更都有记录
        git log --all --pretty=format:"%h %an %ad %s" > audit_trail.txt
        
        # 生成追溯矩阵
        git log --all --grep="REQ-" --pretty=format:"%h,%s" > traceability.csv
        ```
        
        **4. 版本标识**：
        ```bash
        # 每个发布版本都有唯一标识
        git tag -a v1.0.0 -m "Release version 1.0.0
        
        发布信息：
        - 版本号：1.0.0
        - 发布日期：2026-02-09
        - 软件安全分类：Class B
        - 符合标准：IEC 62304, IEC 60601-1
        
        包含功能：
        - ECG信号处理
        - 心率监测
        - 异常报警
        
        测试状态：
        - 单元测试：100%通过
        - 集成测试：100%通过
        - 系统测试：100%通过
        - 代码覆盖率：95%
        
        审批记录：
        - 开发负责人：张三 (2026-02-08)
        - 测试负责人：李四 (2026-02-08)
        - 质量负责人：王五 (2026-02-09)
        - 法规负责人：赵六 (2026-02-09)"
        ```
        
        **5. 基线管理**：
        ```bash
        # 建立基线
        git tag -a baseline-v1.0 -m "Baseline for version 1.0
        
        基线内容：
        - 所有源代码
        - 构建脚本
        - 测试用例
        - 文档
        
        基线状态：已批准
        基线日期：2026-02-09"
        
        # 基线不可修改
        # 任何变更都需要创建新基线
        ```
        
        **6. 分支策略**：
        ```
        医疗器械软件推荐使用Git Flow：
        
        main分支：
        - 只包含发布版本
        - 每个提交都有版本标签
        - 严格保护，不允许直接推送
        
        develop分支：
        - 开发主分支
        - 集成所有功能
        - 需要代码审查
        
        feature分支：
        - 功能开发
        - 从develop创建
        - 完成后合并回develop
        
        release分支：
        - 发布准备
        - 从develop创建
        - 合并到main和develop
        
        hotfix分支：
        - 紧急修复
        - 从main创建
        - 合并到main和develop
        ```
        
        **7. 文档管理**：
        ```bash
        # 文档也纳入版本控制
        docs/
        ├── requirements/
        │   ├── SRS_v1.0.md
        │   └── traceability_matrix.xlsx
        ├── design/
        │   ├── SDD_v1.0.md
        │   └── architecture.png
        ├── test/
        │   ├── test_plan_v1.0.md
        │   └── test_report_v1.0.md
        └── regulatory/
            ├── risk_management_v1.0.md
            └── validation_report_v1.0.md
        ```
        
        **8. 持续集成**：
        ```yaml
        # CI/CD流水线
        stages:
          - build
          - test
          - analyze
          - report
        
        build:
          - 编译代码
          - 检查编译警告
        
        test:
          - 运行单元测试
          - 运行集成测试
          - 检查代码覆盖率（≥80%）
        
        analyze:
          - 静态分析（cppcheck）
          - MISRA C检查
          - 复杂度分析
        
        report:
          - 生成测试报告
          - 生成覆盖率报告
          - 生成追溯矩阵
        ```
        
        **9. 访问控制**：
        ```
        权限管理：
        - 开发人员：读写feature分支
        - 高级开发：读写develop分支
        - 项目经理：读写release分支
        - 质量经理：批准合并到main
        
        审计日志：
        - 记录所有访问
        - 记录所有操作
        - 定期审查
        ```
        
        **10. 备份和恢复**：
        ```bash
        # 定期备份
        # 1. 远程仓库备份
        git clone --mirror https://github.com/company/repo.git
        
        # 2. 导出所有分支和标签
        git bundle create repo-backup.bundle --all
        
        # 3. 恢复
        git clone repo-backup.bundle repo-restored
        ```
        
        **检查清单**：
        ```
        ☐ 建立配置管理计划
        ☐ 使用Git Flow工作流
        ☐ 配置分支保护规则
        ☐ 实施代码审查流程
        ☐ 提交信息包含追溯信息
        ☐ 每个发布版本打标签
        ☐ 标签信息详细完整
        ☐ 建立基线管理流程
        ☐ 配置CI/CD流水线
        ☐ 生成追溯矩阵
        ☐ 定期备份仓库
        ☐ 实施访问控制
        ☐ 记录审计日志
        ☐ 定期配置审核
        ```
        
        **知识点回顾**：医疗器械软件的版本控制需要满足严格的法规要求，包括可追溯性、变更控制、审计追踪等。

## 相关资源

### 相关知识模块

- [基线管理](baseline-management.md) - 配置基线管理
- [变更管理](../requirements-engineering/change-management.md) - 需求变更控制
- [代码审查检查清单](../coding-standards/code-review-checklist.md) - 代码审查标准

### 深入学习

- [配置管理概述](index.md) - 配置管理整体框架
- [静态分析](../static-analysis/index.md) - 代码质量检查

### 工具和资源

- [Git官方文档](https://git-scm.com/doc) - Git完整文档
- [Pro Git书籍](https://git-scm.com/book/zh/v2) - Git权威指南（中文版）
- [GitHub Flow](https://guides.github.com/introduction/flow/) - GitHub工作流指南
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) - Git Flow原始文章
- [Conventional Commits](https://www.conventionalcommits.org/) - 提交信息规范

## 参考文献

1. IEC 62304:2006+AMD1:2015 - Medical device software - Software life cycle processes, Section 5.1 (Software Development Planning) and 8 (Configuration Management)
2. "Pro Git" by Scott Chacon and Ben Straub - Git权威指南
3. "Version Control with Git" by Jon Loeliger and Matthew McCullough - Git版本控制
4. FDA Guidance for the Content of Premarket Submissions for Software Contained in Medical Devices (2005) - FDA软件提交指南
5. "Git Flow" by Vincent Driessen - Git Flow工作流原始文章
6. ISO 13485:2016 - Medical devices - Quality management systems, Section 4.2.4 (Control of records) - 记录控制要求
