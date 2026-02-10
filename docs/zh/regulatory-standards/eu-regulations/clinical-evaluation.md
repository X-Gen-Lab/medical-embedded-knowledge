---
title: 临床评价
description: MDR临床评价要求详解，包括CER编制、文献综述和临床调查
difficulty: 高级
estimated_time: 3小时
tags:
  - 临床评价
  - CER
  - 文献综述
  - 临床调查
  - PMCF
related_modules:
  - zh/regulatory-standards/eu-regulations/mdr-overview
  - zh/regulatory-standards/eu-regulations/technical-documentation
last_updated: '2026-02-10'
version: '1.0'
language: zh-CN
---

# 临床评价

## 学习目标

完成本模块后，你将能够：
- 理解MDR临床评价的要求和流程
- 编制临床评价计划（CEP）
- 进行系统文献综述
- 分析等效器械
- 编制临床评价报告（CER）
- 制定上市后临床随访计划（PMCF）
- 理解临床调查的要求

## 前置知识

- MDR法规基础
- 医学统计学基础
- 文献检索方法
- 临床研究设计基础
- 风险管理（ISO 14971）

## 内容

### 临床评价概述

**临床评价定义（MDR第2条）**：

临床评价是一个系统化和有计划的过程，用于持续生成、收集、分析和评估医疗器械的临床数据，以验证器械的安全性和性能，包括临床效益。

**临床评价的目的**：

```
临床评价目的：
├── 证明临床安全性
│   ├── 识别和评估副作用
│   ├── 评估可接受的效益-风险比
│   └── 确认风险控制措施有效
├── 证明临床性能
│   ├── 验证预期性能
│   ├── 确认技术规格
│   └── 评估性能一致性
└── 证明临床效益
    ├── 验证预期效益
    ├── 评估临床结局
    └── 与现有方法比较
```


**临床评价法规要求**：

```
MDR关键条款：
├── 第61条：临床评价
│   ├── 所有器械必须进行临床评价
│   ├── 基于临床数据
│   └── 持续更新
├── 第62条：临床调查
│   ├── 某些情况需要临床调查
│   ├── 遵循ISO 14155
│   └── 伦理委员会批准
├── 附录XIV：临床评价和PMCF
│   ├── Part A：临床评价
│   └── Part B：PMCF
└── 附录XV：临床调查
    ├── 一般要求
    ├── 调查计划
    └── 调查报告
```

### 临床评价流程

**完整临床评价流程**：

```
临床评价流程（持续过程）：

阶段1：计划（CEP）
├── 定义评价范围
├── 确定评价策略
├── 制定文献检索策略
└── 确定数据需求

阶段2：数据收集
├── 文献综述
├── 等效器械数据
├── 临床调查数据
└── PMCF数据

阶段3：数据分析
├── 数据评估
├── 证据综合
├── 效益-风险分析
└── 结论形成

阶段4：报告（CER）
├── 编制CER
├── 内部审查
├── 批准
└── 提交

阶段5：更新
├── PMCF实施
├── 定期更新CER
├── 响应新信息
└── 持续监控
```

### 临床评价计划（CEP）

**CEP的目的和内容**：

```c
// 临床评价计划结构
typedef struct {
    // 1. 计划信息
    char cep_version[20];
    char cep_date[20];
    char cep_author[100];
    
    // 2. 器械描述
    char device_name[100];
    char device_model[50];
    char intended_use[500];
    char mdr_classification[10];
    
    // 3. 评价范围
    char evaluation_scope[500];
    char clinical_questions[1000];    // 需要回答的临床问题
    bool safety_evaluation;
    bool performance_evaluation;
    bool benefit_evaluation;
    
    // 4. 评价策略
    bool literature_review;
    bool equivalent_device_data;
    bool clinical_investigation;
    bool pmcf_data;
    char strategy_rationale[500];
    
    // 5. 文献检索策略
    char databases[200];              // PubMed, Embase等
    char search_terms[500];
    char inclusion_criteria[500];
    char exclusion_criteria[500];
    char time_period[50];
    
    // 6. 等效器械
    int num_equivalent_devices;
    char equivalent_device_list[500];
    char equivalence_criteria[500];
    
    // 7. 临床调查
    bool clinical_investigation_needed;
    char investigation_rationale[500];
    char investigation_plan_reference[200];
    
    // 8. 数据分析方法
    char analysis_methods[500];
    char statistical_methods[300];
    
    // 9. 时间表
    char timeline[500];
    char milestones[500];
    
    // 10. 团队
    char evaluation_team[500];
    char qualifications[500];
} Clinical_Evaluation_Plan_t;
```

**临床问题示例**：

```c
// 临床问题定义
typedef struct {
    int question_id;
    char question[300];
    char rationale[300];
    char data_source[200];
    char acceptance_criteria[300];
} Clinical_Question_t;

// 示例：血糖监测系统的临床问题
Clinical_Question_t clinical_questions[] = {
    {
        .question_id = 1,
        .question = "器械的测量准确度是否符合ISO 15197:2013要求？",
        .rationale = "准确度直接影响患者治疗决策",
        .data_source = "性能测试数据，文献综述，临床研究",
        .acceptance_criteria = "95%结果在±15 mg/dL或±15%范围内"
    },
    {
        .question_id = 2,
        .question = "器械是否安全，副作用可接受？",
        .rationale = "确保患者安全",
        .data_source = "文献综述，不良事件数据，PMCF数据",
        .acceptance_criteria = "严重不良事件发生率<0.1%"
    },
    {
        .question_id = 3,
        .question = "器械是否改善血糖控制？",
        .rationale = "证明临床效益",
        .data_source = "文献综述，临床研究",
        .acceptance_criteria = "HbA1c降低≥0.5%"
    },
    {
        .question_id = 4,
        .question = "患者能否正确使用器械？",
        .rationale = "确保实际使用中的安全性和有效性",
        .data_source = "可用性测试，PMCF数据",
        .acceptance_criteria = "使用错误率<5%"
    }
};
```

### 文献综述

**系统文献综述流程**：

```
文献综述步骤：

步骤1：制定检索策略
├── 确定检索问题（PICO）
│   ├── P (Population): 目标人群
│   ├── I (Intervention): 干预措施（器械）
│   ├── C (Comparison): 对照
│   └── O (Outcome): 结局指标
├── 选择数据库
│   ├── PubMed/MEDLINE
│   ├── Embase
│   ├── Cochrane Library
│   ├── Web of Science
│   └── 器械特定数据库
├── 确定检索词
│   ├── 主题词（MeSH）
│   ├── 自由词
│   ├── 布尔运算符
│   └── 截词符
└── 定义时间范围
    └── 通常：过去10年

步骤2：文献检索
├── 执行检索
├── 记录检索过程
├── 导出检索结果
└── 去重

步骤3：文献筛选
├── 标题和摘要筛选
├── 全文评估
├── 应用纳入/排除标准
└── 记录筛选过程（PRISMA流程图）

步骤4：数据提取
├── 设计数据提取表
├── 提取关键信息
├── 双人独立提取
└── 解决分歧

步骤5：质量评估
├── 选择评估工具
│   ├── RCT: Cochrane RoB工具
│   ├── 观察性研究: Newcastle-Ottawa量表
│   └── 诊断研究: QUADAS-2
├── 评估偏倚风险
└── 评估证据质量（GRADE）

步骤6：证据综合
├── 定性综合
├── 定量综合（Meta分析，如适用）
└── 形成结论
```

**文献检索策略示例**：

```c
// 文献检索策略
typedef struct {
    // PICO框架
    char population[200];             // 目标人群
    char intervention[200];           // 干预（器械）
    char comparison[200];             // 对照
    char outcome[200];                // 结局
    
    // 检索策略
    char databases[300];
    char search_terms[1000];
    char boolean_operators[200];
    char time_period[50];
    char language[50];
    
    // 纳入排除标准
    char inclusion_criteria[500];
    char exclusion_criteria[500];
    
    // 检索结果
    int total_identified;
    int after_deduplication;
    int after_title_abstract_screening;
    int after_full_text_assessment;
    int final_included;
} Literature_Search_Strategy_t;

// 示例：血糖监测系统文献检索
Literature_Search_Strategy_t glucose_meter_search = {
    .population = "糖尿病患者（1型和2型）",
    .intervention = "血糖自我监测系统",
    .comparison = "实验室参考方法或其他血糖仪",
    .outcome = "测量准确度，临床结局（HbA1c），安全性",
    
    .databases = "PubMed, Embase, Cochrane Library",
    .search_terms = "(\"blood glucose\" OR \"glucose monitoring\" OR \"glucometer\") "
                   "AND (\"self-monitoring\" OR \"SMBG\") "
                   "AND (\"accuracy\" OR \"performance\" OR \"clinical outcome\")",
    .time_period = "2013-2023 (10 years)",
    .language = "English",
    
    .inclusion_criteria = "1) 糖尿病患者研究\n"
                         "2) 血糖自我监测\n"
                         "3) 报告准确度或临床结局\n"
                         "4) 同行评审期刊",
    .exclusion_criteria = "1) 动物研究\n"
                         "2) 体外研究（无临床数据）\n"
                         "3) 会议摘要\n"
                         "4) 非英语文献",
    
    .total_identified = 850,
    .after_deduplication = 620,
    .after_title_abstract_screening = 120,
    .after_full_text_assessment = 65,
    .final_included = 55
};
```

**PRISMA流程图**：

```
文献筛选流程（PRISMA）：

识别阶段：
├── 数据库检索：n = 850
├── 其他来源：n = 20
└── 总计：n = 870

筛选阶段：
├── 去重后：n = 620
├── 标题摘要筛选：n = 620
│   └── 排除：n = 500
├── 全文评估：n = 120
│   └── 排除：n = 55
│       ├── 不符合纳入标准：n = 30
│       ├── 数据不充分：n = 15
│       └── 质量不合格：n = 10
└── 最终纳入：n = 65

纳入阶段：
├── 定性综合：n = 65
└── 定量综合（Meta分析）：n = 25
```


### 等效器械分析

**等效性概念**：

```
等效性三要素：
├── 技术等效性
│   ├── 相同的技术特征
│   ├── 相同的生物学特征
│   └── 相同的作用机制
├── 生物学等效性
│   ├── 相同的材料
│   ├── 相同的与人体接触方式
│   └── 相同的生物学效应
└── 临床等效性
    ├── 相同的临床适应症
    ├── 相同的目标人群
    └── 相同的预期临床效果
```

**等效性评估流程**：

```c
// 等效器械评估
typedef struct {
    // 参考器械信息
    char reference_device_name[100];
    char manufacturer[100];
    char model[50];
    char ce_certificate[50];
    int years_on_market;
    
    // 技术特征比较
    char technical_comparison[1000];
    bool same_technology;
    bool same_materials;
    bool same_design_principles;
    bool same_performance_specs;
    
    // 生物学特征比较
    char biological_comparison[500];
    bool same_body_contact;
    bool same_contact_duration;
    bool same_biological_effects;
    
    // 临床特征比较
    char clinical_comparison[1000];
    bool same_intended_use;
    bool same_indications;
    bool same_target_population;
    bool same_contraindications;
    bool same_clinical_benefits;
    
    // 差异分析
    char differences[1000];
    char differences_impact[1000];
    bool differences_acceptable;
    
    // 临床数据可用性
    bool clinical_data_available;
    char clinical_data_sources[500];
    bool data_sufficient;
    
    // 等效性结论
    bool technically_equivalent;
    bool biologically_equivalent;
    bool clinically_equivalent;
    bool overall_equivalent;
} Equivalent_Device_Assessment_t;
```

**等效性判定标准**：

```
等效性判定：

完全等效（可直接使用临床数据）：
├── 技术等效：✓
├── 生物学等效：✓
├── 临床等效：✓
└── 差异：无或可忽略

部分等效（需要补充数据）：
├── 技术等效：✓
├── 生物学等效：✓
├── 临床等效：部分
└── 差异：需要评估影响

不等效（需要独立临床数据）：
├── 技术等效：✗
├── 生物学等效：✗
├── 临床等效：✗
└── 差异：显著
```

### 临床评价报告（CER）

**CER结构（MDCG 2020-13）**：

```
临床评价报告目录：

1. 执行摘要
   ├── 器械描述
   ├── 评价范围和方法
   ├── 主要发现
   └── 结论

2. 器械描述
   ├── 2.1 器械标识
   ├── 2.2 预期用途和适应症
   ├── 2.3 技术描述
   ├── 2.4 分类和合格评定程序
   └── 2.5 创新方面

3. 临床背景和当前知识
   ├── 3.1 疾病/状况描述
   ├── 3.2 流行病学
   ├── 3.3 当前诊断/治疗选择
   ├── 3.4 目标人群
   └── 3.5 预期临床效益

4. 评价范围和方法
   ├── 4.1 评价范围
   ├── 4.2 临床问题
   ├── 4.3 评价方法
   ├── 4.4 文献检索策略
   └── 4.5 数据来源

5. 器械特定临床数据
   ├── 5.1 临床前数据
   ├── 5.2 临床调查数据
   ├── 5.3 其他临床数据
   └── 5.4 PMCF数据

6. 等效器械的临床数据
   ├── 6.1 等效器械识别
   ├── 6.2 等效性分析
   ├── 6.3 等效器械临床数据
   └── 6.4 数据适用性

7. 文献综述
   ├── 7.1 文献检索过程
   ├── 7.2 文献筛选
   ├── 7.3 数据提取
   ├── 7.4 质量评估
   └── 7.5 证据综合

8. 临床数据分析
   ├── 8.1 安全性分析
   ├── 8.2 性能分析
   ├── 8.3 效益分析
   └── 8.4 不确定性分析

9. 效益-风险分析
   ├── 9.1 效益识别和评估
   ├── 9.2 风险识别和评估
   ├── 9.3 效益-风险比
   └── 9.4 可接受性判断

10. 结论
    ├── 10.1 临床安全性
    ├── 10.2 临床性能
    ├── 10.3 临床效益
    ├── 10.4 效益-风险比
    └── 10.5 符合性声明

11. PMCF计划
    ├── 11.1 PMCF目标
    ├── 11.2 数据收集方法
    ├── 11.3 时间表
    └── 11.4 成功标准

12. 参考文献

13. 附录
    ├── 文献检索详情
    ├── 数据提取表
    ├── 质量评估表
    └── 其他支持文档
```

**CER编制代码示例**：

```c
// CER文档结构
typedef struct {
    // 文档信息
    char cer_version[20];
    char cer_date[20];
    char cer_author[100];
    char cer_reviewer[100];
    char cer_approver[100];
    
    // 器械信息
    char device_name[100];
    char device_model[50];
    char intended_use[500];
    char mdr_classification[10];
    
    // 评价范围
    char evaluation_scope[500];
    int num_clinical_questions;
    
    // 数据来源
    int num_literature_studies;
    int num_equivalent_devices;
    bool clinical_investigation_data;
    bool pmcf_data;
    
    // 安全性分析
    int num_adverse_events;
    float serious_ae_rate;
    char safety_conclusion[500];
    
    // 性能分析
    char performance_data[1000];
    bool performance_acceptable;
    char performance_conclusion[500];
    
    // 效益分析
    char clinical_benefits[1000];
    bool benefits_demonstrated;
    char benefit_conclusion[500];
    
    // 效益-风险分析
    char benefit_risk_analysis[1000];
    bool benefit_risk_acceptable;
    char benefit_risk_conclusion[500];
    
    // 总体结论
    bool clinically_safe;
    bool clinically_effective;
    bool benefit_risk_positive;
    bool compliant_with_gspr;
    char overall_conclusion[1000];
    
    // PMCF
    char pmcf_plan_reference[200];
    bool pmcf_ongoing;
} Clinical_Evaluation_Report_t;
```

### 临床调查

**何时需要临床调查**：

```
需要临床调查的情况：

1. 植入器械和III类器械（通常需要）
   ├── 除非有充分的等效器械数据
   └── 或有充分的文献数据

2. 创新器械
   ├── 新技术
   ├── 新适应症
   └── 新目标人群

3. 现有数据不足
   ├── 文献数据不充分
   ├── 无等效器械
   └── 重大设计变更

4. 公告机构要求
   └── 基于风险评估
```

**临床调查类型**：

```c
// 临床调查类型
typedef enum {
    INVESTIGATION_FEASIBILITY,        // 可行性研究
    INVESTIGATION_PIVOTAL,            // 关键研究
    INVESTIGATION_PMCF,               // PMCF研究
    INVESTIGATION_REGISTRY            // 注册研究
} Investigation_Type_t;

// 临床调查设计
typedef struct {
    Investigation_Type_t type;
    
    // 研究设计
    char study_design[100];           // RCT, 单臂, 观察性
    char study_phase[50];             // I, II, III, IV
    bool randomized;
    bool blinded;
    bool controlled;
    
    // 样本量
    int planned_sample_size;
    char sample_size_justification[500];
    int num_sites;
    char countries[200];
    
    // 主要终点
    char primary_endpoint[300];
    char success_criteria[300];
    
    // 次要终点
    int num_secondary_endpoints;
    char secondary_endpoints[1000];
    
    // 时间
    int enrollment_duration_months;
    int follow_up_duration_months;
    int total_duration_months;
    
    // 法规
    bool ethics_approval_required;
    bool competent_authority_approval;
    char iso_14155_compliance[100];
} Clinical_Investigation_Design_t;
```

**临床调查计划（CIP）要点**：

```
临床调查计划内容：

1. 研究概述
   ├── 研究标题
   ├── 研究目的
   ├── 研究设计
   └── 研究持续时间

2. 器械描述
   ├── 器械规格
   ├── 预期用途
   └── 风险分析

3. 研究目标
   ├── 主要目标
   ├── 次要目标
   └── 探索性目标

4. 研究设计
   ├── 研究类型
   ├── 对照组
   ├── 随机化
   └── 盲法

5. 受试者选择
   ├── 纳入标准
   ├── 排除标准
   ├── 样本量计算
   └── 招募策略

6. 研究程序
   ├── 筛选访视
   ├── 基线评估
   ├── 随访访视
   └── 终点评估

7. 终点和评估
   ├── 主要终点
   ├── 次要终点
   ├── 安全性评估
   └── 评估时间点

8. 统计分析
   ├── 分析人群
   ├── 统计方法
   ├── 中期分析
   └── 最终分析

9. 伦理和法规
   ├── 伦理委员会批准
   ├── 知情同意
   ├── 数据保护
   └── 法规符合性

10. 数据管理
    ├── 数据收集
    ├── 数据质量
    ├── 数据安全
    └── 数据存档
```

### 上市后临床随访（PMCF）

**PMCF的目的**：

```
PMCF目标：
├── 确认长期安全性和性能
├── 识别新出现的风险
├── 确保效益-风险比持续可接受
├── 识别误用或滥用
├── 更新临床评价
└── 支持PSUR编制
```

**PMCF计划**：

```c
// PMCF计划
typedef struct {
    // 计划信息
    char pmcf_plan_version[20];
    char pmcf_plan_date[20];
    
    // PMCF目标
    char pmcf_objectives[1000];
    char clinical_questions[1000];
    
    // PMCF方法
    bool literature_monitoring;
    bool registry_study;
    bool survey_study;
    bool clinical_follow_up_study;
    char methods_rationale[500];
    
    // 数据收集
    char data_sources[500];
    char data_collection_methods[500];
    int target_sample_size;
    int follow_up_duration_years;
    
    // 数据分析
    char analysis_methods[500];
    char success_criteria[500];
    
    // 时间表
    char pmcf_start_date[20];
    int pmcf_duration_years;
    char milestones[500];
    
    // 报告
    int reporting_frequency_years;
    char pmcf_report_template[200];
    
    // 资源
    char responsible_person[100];
    char budget[100];
} PMCF_Plan_t;
```

**PMCF方法**：

```
PMCF方法选择：

1. 文献监控
   ├── 适用：所有器械
   ├── 方法：定期文献检索
   ├── 频率：每年
   └── 成本：低

2. 注册研究
   ├── 适用：高风险器械
   ├── 方法：前瞻性数据收集
   ├── 持续时间：多年
   └── 成本：高

3. 调查研究
   ├── 适用：用户反馈
   ├── 方法：问卷调查
   ├── 频率：定期
   └── 成本：中

4. 临床随访研究
   ├── 适用：植入器械
   ├── 方法：患者随访
   ├── 持续时间：器械寿命
   └── 成本：高

5. 真实世界数据
   ├── 适用：所有器械
   ├── 方法：电子健康记录
   ├── 持续时间：持续
   └── 成本：中
```


### CER更新和维护

**CER更新要求**：

```
CER更新触发因素：
├── 定期更新
│   ├── I类：不需要（除非有新信息）
│   ├── IIa/IIb类：至少每2年
│   └── III类/植入：至少每年
├── 事件触发
│   ├── 严重不良事件
│   ├── 现场安全纠正措施（FSCA）
│   ├── 新的科学证据
│   └── 设计变更
└── 法规要求
    ├── PSUR编制
    ├── 证书更新
    └── 公告机构要求
```

## 最佳实践

!!! tip "临床评价成功要素"
    1. **早期规划**：在设计阶段就考虑临床评价需求
    2. **系统方法**：使用系统化的文献综述方法
    3. **质量优先**：关注证据质量而非数量
    4. **专家参与**：聘请临床专家和统计学家
    5. **持续更新**：定期更新CER，不要等到最后一刻
    6. **PMCF整合**：将PMCF作为临床评价的一部分
    7. **透明记录**：详细记录所有决策和方法
    8. **内部审查**：提交前进行彻底的内部审查

## 常见陷阱

!!! warning "注意事项"
    1. **文献检索不系统**：检索策略不充分，遗漏重要文献
    2. **等效性分析不充分**：未充分证明等效性
    3. **证据质量低**：纳入低质量研究
    4. **样本量不足**：临床调查样本量不够
    5. **效益-风险分析薄弱**：未充分分析效益-风险比
    6. **PMCF计划不具体**：PMCF计划过于笼统
    7. **更新不及时**：未按要求更新CER
    8. **结论不支持**：结论与数据不匹配

## 实践练习

1. **制定CEP**：
   - 为一个医疗器械制定临床评价计划
   - 定义临床问题
   - 设计文献检索策略

2. **文献综述**：
   - 进行系统文献检索
   - 筛选和评估文献
   - 提取和综合数据

3. **等效性分析**：
   - 识别等效器械
   - 进行技术、生物学和临床等效性分析
   - 评估数据适用性

4. **编制CER**：
   - 编制临床评价报告
   - 进行效益-风险分析
   - 形成结论

## 自测问题

??? question "问题1：临床评价的三个核心要素是什么？如何证明？"
    
    ??? success "答案"
        **临床评价三要素**：
        
        **1. 临床安全性**
        - 定义：器械在预期用途下不会造成不可接受的风险
        - 证明方法：
          - 不良事件数据分析
          - 副作用发生率
          - 严重不良事件评估
          - 与风险管理文件关联
        - 接受标准：
          - 严重不良事件发生率低
          - 副作用可预测和可管理
          - 效益大于风险
        
        **2. 临床性能**
        - 定义：器械达到制造商声称的性能
        - 证明方法：
          - 性能测试数据
          - 临床研究数据
          - 真实世界数据
          - 与技术规格对比
        - 接受标准：
          - 满足技术规格
          - 符合预期性能
          - 性能一致稳定
        
        **3. 临床效益**
        - 定义：器械对患者健康的积极影响
        - 证明方法：
          - 临床结局数据
          - 与现有方法比较
          - 患者报告结局
          - 生活质量改善
        - 接受标准：
          - 临床结局改善
          - 优于或等同于现有方法
          - 患者获益明显
        
        **证明框架**：
        ```
        临床评价证明链：
        
        安全性证明：
        ├── 临床前安全性测试
        ├── 风险管理文件
        ├── 文献综述（不良事件）
        ├── 临床调查安全性数据
        └── PMCF安全性监控
        
        性能证明：
        ├── 性能验证测试
        ├── 技术规格符合性
        ├── 文献综述（性能数据）
        ├── 临床调查性能数据
        └── PMCF性能监控
        
        效益证明：
        ├── 临床前效益评估
        ├── 文献综述（临床结局）
        ├── 临床调查效益数据
        ├── 真实世界证据
        └── PMCF效益监控
        ```
        
        **知识点回顾**：临床评价必须证明安全性、性能和效益三个方面，缺一不可。

??? question "问题2：如何进行系统文献综述？关键步骤是什么？"
    
    ??? success "答案"
        **系统文献综述7步法**：
        
        **步骤1：制定检索策略（2-4周）**
        ```
        PICO框架：
        P (Population): 糖尿病患者
        I (Intervention): 血糖自我监测
        C (Comparison): 实验室方法
        O (Outcome): 准确度、HbA1c
        
        检索策略：
        ├── 数据库：PubMed, Embase, Cochrane
        ├── 检索词：
        │   ├── 主题词（MeSH）
        │   ├── 自由词
        │   └── 布尔运算符
        ├── 时间范围：过去10年
        └── 语言：英语
        ```
        
        **步骤2：执行检索（1周）**
        ```
        检索过程：
        ├── 在各数据库执行检索
        ├── 记录检索式和结果数
        ├── 导出检索结果
        ├── 合并结果
        └── 去重
        
        示例结果：
        - PubMed: 450篇
        - Embase: 380篇
        - Cochrane: 20篇
        - 总计: 850篇
        - 去重后: 620篇
        ```
        
        **步骤3：文献筛选（2-3周）**
        ```
        两阶段筛选：
        
        阶段1：标题和摘要筛选
        ├── 应用纳入/排除标准
        ├── 双人独立筛选
        ├── 解决分歧
        └── 结果：620 → 120篇
        
        阶段2：全文评估
        ├── 获取全文
        ├── 详细评估
        ├── 应用纳入/排除标准
        └── 结果：120 → 65篇
        
        PRISMA流程图记录整个过程
        ```
        
        **步骤4：数据提取（2-3周）**
        ```
        数据提取表：
        ├── 研究基本信息
        │   ├── 作者、年份、期刊
        │   ├── 研究设计
        │   └── 样本量
        ├── 研究人群
        │   ├── 纳入/排除标准
        │   ├── 人口学特征
        │   └── 疾病特征
        ├── 干预措施
        │   ├── 器械描述
        │   ├── 使用方法
        │   └── 对照组
        ├── 结局指标
        │   ├── 主要结局
        │   ├── 次要结局
        │   └── 安全性结局
        └── 结果数据
            ├── 数值结果
            ├── 统计显著性
            └── 不良事件
        
        双人独立提取，交叉核对
        ```
        
        **步骤5：质量评估（1-2周）**
        ```
        质量评估工具：
        
        RCT研究：
        └── Cochrane RoB 2.0工具
            ├── 随机化过程
            ├── 偏离预期干预
            ├── 缺失结局数据
            ├── 结局测量
            └── 选择性报告
        
        观察性研究：
        └── Newcastle-Ottawa量表
            ├── 研究对象选择
            ├── 组间可比性
            └── 结局评估
        
        诊断研究：
        └── QUADAS-2工具
            ├── 患者选择
            ├── 待评价试验
            ├── 金标准
            └── 流程和时机
        
        证据质量（GRADE）：
        ├── 高质量
        ├── 中等质量
        ├── 低质量
        └── 极低质量
        ```
        
        **步骤6：证据综合（2-3周）**
        ```
        综合方法：
        
        定性综合：
        ├── 叙述性综述
        ├── 主题分析
        └── 证据表格
        
        定量综合（Meta分析）：
        ├── 评估异质性
        ├── 选择效应模型
        ├── 进行Meta分析
        ├── 敏感性分析
        └── 发表偏倚评估
        
        证据分级：
        └── GRADE方法
            ├── 研究设计
            ├── 风险偏倚
            ├── 不一致性
            ├── 间接性
            ├── 不精确性
            └── 发表偏倚
        ```
        
        **步骤7：报告结果（1-2周）**
        ```
        报告内容：
        ├── 检索策略
        ├── PRISMA流程图
        ├── 纳入研究特征表
        ├── 质量评估结果
        ├── 证据综合
        ├── Meta分析（如适用）
        └── 结论和建议
        
        遵循PRISMA报告规范
        ```
        
        **时间估算**：
        - 总时间：10-16周
        - 人力：2-3人
        - 成本：€10,000-20,000
        
        **知识点回顾**：系统文献综述需要系统化、透明化和可重复的方法，PRISMA是国际标准。

## 相关资源

- [MDR概述](mdr-overview.md) - MDR法规详解
- [技术文档要求](technical-documentation.md) - 技术文档编制
- [上市后监督](post-market-surveillance.md) - PMS和PMCF

## 参考文献

1. **Regulation (EU) 2017/745** - Medical Device Regulation, Articles 61-62, Annex XIV
2. **MDCG 2020-13** - Clinical Evaluation Assessment Report Template
3. **MDCG 2020-6** - Sufficient Clinical Evidence for Legacy Devices
4. **MDCG 2020-5** - Clinical Evaluation - Equivalence
5. **MDCG 2022-14** - Qualification and Classification of Software
6. **ISO 14155:2020** - Clinical investigation of medical devices for human subjects
7. **MEDDEV 2.7/1 Rev 4** - Clinical Evaluation (legacy guidance)
8. **PRISMA 2020** - Preferred Reporting Items for Systematic Reviews and Meta-Analyses
9. **Cochrane Handbook** - Systematic Reviews of Interventions
10. **GRADE Working Group** - Grading of Recommendations Assessment

