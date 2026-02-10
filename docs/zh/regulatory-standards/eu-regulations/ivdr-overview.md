---
title: IVDR 2017/746 概述
description: 欧盟体外诊断医疗器械法规(IVDR)详细解读，包括分类规则和特殊要求
difficulty: 中级
estimated_time: 2小时
tags:
  - IVDR
  - 体外诊断
  - 欧盟法规
  - IVD分类
related_modules:
  - zh/regulatory-standards/eu-regulations/mdr-overview
  - zh/regulatory-standards/iec-62304
  - zh/regulatory-standards/iso-13485
last_updated: '2026-02-10'
version: '1.0'
language: zh-CN
---

# IVDR 2017/746 概述

## 学习目标

完成本模块后，你将能够：
- 理解IVDR法规的核心要求
- 掌握IVD器械分类规则
- 了解性能评价要求
- 理解IVD软件的特殊考虑
- 掌握IVDR与MDR的区别
- 应用IVDR要求到IVD产品开发

## 前置知识

- 医疗器械基础知识
- MDR法规基础
- 质量管理体系概念
- 软件开发基础

## 内容

### IVDR法规背景

**IVDR (In Vitro Diagnostic Medical Device Regulation) 2017/746** 于2017年5月发布，2022年5月26日全面实施。

**IVD定义**：

体外诊断医疗器械是指制造商预期用于体外检查从人体获取的样本（包括血液和组织捐献）的任何医疗器械，无论单独使用还是组合使用，其唯一或主要目的是提供以下信息：
- 生理或病理过程或状态
- 先天性身体或精神缺陷
- 易感性
- 安全性和与潜在受体的兼容性
- 治疗反应或反应的预测
- 治疗措施的定义或监测

**IVD软件示例**：
```c
// IVD软件类型
typedef enum {
    IVD_DATA_ACQUISITION,      // 数据采集软件
    IVD_DATA_ANALYSIS,         // 数据分析软件
    IVD_RESULT_INTERPRETATION, // 结果解释软件
    IVD_LIMS,                  // 实验室信息管理系统
    IVD_QUALITY_CONTROL        // 质量控制软件
} IVD_Software_Type_t;

// 示例：血液分析软件
typedef struct {
    float wbc_count;           // 白细胞计数
    float rbc_count;           // 红细胞计数
    float hemoglobin;          // 血红蛋白
    float hematocrit;          // 红细胞压积
    float platelet_count;      // 血小板计数
    char interpretation[200];  // 结果解释
} Blood_Analysis_Result_t;
```



### IVDR与MDD的主要变化

**IVDR相比旧的IVDD指令的主要变化**：

```
IVDD (旧指令) → IVDR (新法规)
├── 更严格的分类规则（4类 vs 原来的附录II清单）
├── 性能评价要求（类似MDR的临床评价）
├── 公告机构强制参与（除A类自测试器械）
├── 欧盟参考实验室（EURL）系统
├── UDI强制要求
├── EUDAMED注册
└── 更严格的上市后监督
```

### IVD器械分类

IVDR将IVD器械分为4类：**A类、B类、C类、D类**，风险从低到高。

#### 分类规则（附录VIII）

**规则1：自测试器械**
- 制造商预期由非专业人员使用
- 分类：B类（一般）或C类（特定疾病）

**规则2：特定分析物**

根据分析物的风险分为不同类别：

**附录VIII清单A（D类 - 最高风险）**：
```
高风险分析物：
├── HIV检测（HIV 1和2、抗原/抗体）
├── HTLV I和II检测
├── 肝炎病毒（HBV、HCV）
├── 梅毒螺旋体
├── 人类细胞、组织或器官的ABO系统
├── 人类细胞、组织或器官的Rh系统（C、c、D、E、e、Kell）
├── 不规则抗体检测
├── HLA组织分型（A、B、DR）
└── 血浆蛋白（凝血因子）
```

**附录VIII清单B（C类 - 高风险）**：
```
中高风险分析物：
├── PSA（前列腺特异性抗原）
├── 风疹IgG和IgM
├── 弓形虫IgG和IgM
├── 苯丙酮尿症
├── 人类细胞、组织或器官的其他血型系统
├── HLA组织分型（其他位点）
├── 血浆蛋白（其他）
├── 先天性感染（巨细胞病毒、单纯疱疹）
├── 唐氏综合征筛查
└── 肿瘤标志物（CEA、CA125等）
```

**规则3：伴随诊断**
- 用于确定患者对特定药物或生物制品的安全性和有效性
- 分类：C类或D类（取决于药物风险）

**规则4：自我检测器械**
- 由非专业人员使用
- 分类：B类（一般）或C类（严重疾病）

**规则5：性能评价**
- 用于性能评价的器械
- 分类：与预期最终分类相同

**规则6：筛查、诊断或分期**
- 癌症筛查、诊断或分期
- 分类：C类

**规则7：其他器械**
- 不属于上述规则的器械
- 分类：A类（默认）

#### IVD软件分类

```c
// IVD软件分类示例
typedef struct {
    char software_name[100];
    char intended_use[200];
    char ivdr_class[10];
    char rationale[200];
} IVD_Software_Classification_t;

// 示例1：血液分析软件
IVD_Software_Classification_t example1 = {
    .software_name = "血液分析软件",
    .intended_use = "分析全血细胞计数，检测白细胞、红细胞、血小板",
    .ivdr_class = "A",
    .rationale = "一般血液分析，不涉及清单A/B分析物"
};

// 示例2：HIV检测软件
IVD_Software_Classification_t example2 = {
    .software_name = "HIV检测结果分析软件",
    .intended_use = "分析HIV抗体/抗原检测结果",
    .ivdr_class = "D",
    .rationale = "清单A分析物 - HIV检测"
};

// 示例3：糖尿病管理软件
IVD_Software_Classification_t example3 = {
    .software_name = "糖尿病管理软件",
    .intended_use = "记录和分析血糖数据，提供趋势分析",
    .ivdr_class = "A",
    .rationale = "数据管理和分析，不直接用于诊断"
};

// 示例4：癌症筛查AI软件
IVD_Software_Classification_t example4 = {
    .software_name = "宫颈癌筛查AI软件",
    .intended_use = "分析细胞学图像，辅助宫颈癌筛查",
    .ivdr_class = "C",
    .rationale = "规则6 - 癌症筛查"
};

// 示例5：伴随诊断软件
IVD_Software_Classification_t example5 = {
    .software_name = "HER2基因检测分析软件",
    .intended_use = "分析HER2基因状态，指导曲妥珠单抗治疗",
    .ivdr_class = "C",
    .rationale = "规则3 - 伴随诊断"
};
```

### 性能评价

IVDR引入了"性能评价"概念，类似于MDR的"临床评价"。

#### 性能评价要求

**定义**：
性能评价是评估和分析数据以验证IVD器械的科学有效性和性能的过程。

**组成部分**：

```
性能评价 = 科学有效性 + 分析性能 + 临床性能

科学有效性（Scientific Validity）：
├── 分析物与临床状况的关系
├── 生物学机制
├── 文献证据
└── 专家共识

分析性能（Analytical Performance）：
├── 准确度（Accuracy）
├── 精密度（Precision）
├── 灵敏度（Analytical Sensitivity）
├── 特异性（Analytical Specificity）
├── 检测限（Limit of Detection）
├── 测量范围（Measuring Range）
├── 线性（Linearity）
└── 干扰物质影响

临床性能（Clinical Performance）：
├── 诊断灵敏度（Diagnostic Sensitivity）
├── 诊断特异性（Diagnostic Specificity）
├── 阳性预测值（PPV）
├── 阴性预测值（NPV）
├── 似然比（Likelihood Ratio）
└── ROC曲线分析
```

#### 性能评价计划

```c
// 性能评价计划结构
typedef struct {
    // 科学有效性
    char biomarker[100];              // 生物标志物
    char clinical_condition[100];     // 临床状况
    char literature_review[500];      // 文献综述
    bool scientific_validity_established; // 科学有效性已建立
    
    // 分析性能
    float accuracy;                   // 准确度 (%)
    float precision_cv;               // 精密度 CV (%)
    float analytical_sensitivity;     // 分析灵敏度
    float analytical_specificity;     // 分析特异性
    float lod;                        // 检测限
    float measuring_range_min;        // 测量范围最小值
    float measuring_range_max;        // 测量范围最大值
    
    // 临床性能
    float diagnostic_sensitivity;     // 诊断灵敏度 (%)
    float diagnostic_specificity;     // 诊断特异性 (%)
    float ppv;                        // 阳性预测值 (%)
    float npv;                        // 阴性预测值 (%)
    int sample_size;                  // 样本量
    
    // 性能研究
    bool analytical_study_completed;  // 分析性能研究完成
    bool clinical_study_completed;    // 临床性能研究完成
    char study_report[200];           // 研究报告路径
} Performance_Evaluation_Plan_t;

// 示例：血糖检测系统性能评价
Performance_Evaluation_Plan_t glucose_meter_pe = {
    .biomarker = "血糖（葡萄糖）",
    .clinical_condition = "糖尿病诊断和监测",
    .scientific_validity_established = true,
    
    // 分析性能
    .accuracy = 95.0,                 // 95%准确度
    .precision_cv = 3.5,              // 3.5% CV
    .analytical_sensitivity = 20.0,   // 20 mg/dL
    .analytical_specificity = 99.0,   // 99%
    .lod = 10.0,                      // 10 mg/dL
    .measuring_range_min = 20.0,      // 20 mg/dL
    .measuring_range_max = 600.0,     // 600 mg/dL
    
    // 临床性能
    .diagnostic_sensitivity = 98.0,   // 98%
    .diagnostic_specificity = 97.0,   // 97%
    .ppv = 95.0,                      // 95%
    .npv = 99.0,                      // 99%
    .sample_size = 200,               // 200个样本
    
    .analytical_study_completed = true,
    .clinical_study_completed = true
};
```

#### 性能研究类型

**1. 分析性能研究**

```c
// 分析性能研究设计
typedef struct {
    // 精密度研究
    int repeatability_replicates;     // 重复性：20次
    int reproducibility_days;         // 再现性：20天
    int reproducibility_operators;    // 再现性：2个操作员
    
    // 准确度研究
    int reference_samples;            // 参考样本数量
    char reference_method[100];       // 参考方法
    
    // 线性研究
    int linearity_levels;             // 线性水平数：5-7个
    int linearity_replicates;         // 每个水平重复数：3-5次
    
    // 干扰研究
    int interferents_tested;          // 测试的干扰物质数量
    char interferents_list[500];      // 干扰物质清单
    
    // 稳定性研究
    int stability_timepoints;         // 稳定性时间点
    char storage_conditions[200];     // 储存条件
} Analytical_Performance_Study_t;
```

**2. 临床性能研究**

```c
// 临床性能研究设计
typedef struct {
    // 研究设计
    char study_type[50];              // 研究类型：前瞻性/回顾性
    int total_subjects;               // 总受试者数
    int positive_subjects;            // 阳性受试者数
    int negative_subjects;            // 阴性受试者数
    
    // 纳入/排除标准
    char inclusion_criteria[500];     // 纳入标准
    char exclusion_criteria[500];     // 排除标准
    
    // 参考标准
    char reference_standard[200];     // 金标准
    bool reference_independent;       // 参考标准独立性
    
    // 统计分析
    float required_sensitivity;       // 要求的灵敏度
    float required_specificity;       // 要求的特异性
    float confidence_level;           // 置信水平：95%
    int calculated_sample_size;       // 计算的样本量
    
    // 结果
    int true_positive;                // 真阳性
    int false_positive;               // 假阳性
    int true_negative;                // 真阴性
    int false_negative;               // 假阴性
} Clinical_Performance_Study_t;

// 计算诊断性能指标
void calculate_diagnostic_performance(Clinical_Performance_Study_t* study,
                                     Performance_Evaluation_Plan_t* pe) {
    int tp = study->true_positive;
    int fp = study->false_positive;
    int tn = study->true_negative;
    int fn = study->false_negative;
    
    // 灵敏度 = TP / (TP + FN)
    pe->diagnostic_sensitivity = (float)tp / (tp + fn) * 100.0;
    
    // 特异性 = TN / (TN + FP)
    pe->diagnostic_specificity = (float)tn / (tn + fp) * 100.0;
    
    // 阳性预测值 = TP / (TP + FP)
    pe->ppv = (float)tp / (tp + fp) * 100.0;
    
    // 阴性预测值 = TN / (TN + FN)
    pe->npv = (float)tn / (tn + fn) * 100.0;
}
```

### 欧盟参考实验室（EURL）

IVDR引入了欧盟参考实验室系统，用于支持公告机构的评估。

**EURL的作用**：
- 为公告机构提供科学和技术支持
- 评估性能评价计划
- 审查性能研究数据
- 提供专家意见

**需要EURL参与的情况**：
- D类器械（强制）
- C类器械（某些情况）
- 新技术或新分析物
- 公告机构请求

```c
// EURL评估流程
typedef struct {
    char device_name[100];
    char ivdr_class[10];
    bool eurl_required;
    char eurl_name[100];
    
    // 提交材料
    bool performance_evaluation_plan;
    bool analytical_performance_data;
    bool clinical_performance_data;
    bool scientific_validity_evidence;
    
    // EURL评估
    char eurl_opinion[500];
    bool eurl_positive_opinion;
    char eurl_recommendations[500];
    
    // 时间线
    int eurl_review_days;             // EURL审查天数：60天
} EURL_Assessment_t;
```

### 合格评定程序

#### A类器械（自测试，非清单A/B）

**程序：自我声明**
- 制造商自行评估符合性
- 编制技术文档
- 签署EU符合性声明
- 加贴CE标志
- 无需公告机构参与

#### B类器械

**程序：附录IX第3部分（产品验证）**
- 公告机构审核技术文档（抽样）
- 公告机构进行产品验证
- 制造商建立QMS
- 获得CE证书

#### C类器械

**程序：附录IX第2部分（完整QMS）+ 附录IX第3部分**
- 公告机构审核完整QMS
- 公告机构审核技术文档（抽样）
- EURL参与（某些情况）
- 获得CE证书

#### D类器械

**程序：附录IX第2部分 + 附录IX第3部分 + EURL**
- 公告机构审核完整QMS
- 公告机构审核技术文档（全部）
- **EURL强制参与**
- 获得CE证书

```c
// 合格评定程序选择
typedef struct {
    char device_name[100];
    char ivdr_class[10];
    bool self_testing;
    bool list_a_analyte;
    bool list_b_analyte;
    
    // 程序选择
    char conformity_assessment[100];
    bool notified_body_required;
    bool eurl_required;
    
    // 时间估算
    int estimated_months;
} IVDR_Conformity_Assessment_t;

// 选择合格评定程序
void select_conformity_assessment(IVDR_Conformity_Assessment_t* ca) {
    if (strcmp(ca->ivdr_class, "A") == 0 && ca->self_testing && 
        !ca->list_a_analyte && !ca->list_b_analyte) {
        strcpy(ca->conformity_assessment, "自我声明");
        ca->notified_body_required = false;
        ca->eurl_required = false;
        ca->estimated_months = 3;
    } else if (strcmp(ca->ivdr_class, "B") == 0) {
        strcpy(ca->conformity_assessment, "附录IX第3部分");
        ca->notified_body_required = true;
        ca->eurl_required = false;
        ca->estimated_months = 9;
    } else if (strcmp(ca->ivdr_class, "C") == 0) {
        strcpy(ca->conformity_assessment, "附录IX第2+3部分");
        ca->notified_body_required = true;
        ca->eurl_required = true;  // 某些情况
        ca->estimated_months = 12;
    } else if (strcmp(ca->ivdr_class, "D") == 0) {
        strcpy(ca->conformity_assessment, "附录IX第2+3部分 + EURL");
        ca->notified_body_required = true;
        ca->eurl_required = true;  // 强制
        ca->estimated_months = 18;
    }
}
```

### IVD软件特殊考虑

#### 软件作为IVD

**独立软件（SaMD）**：
- 用于分析IVD数据
- 提供诊断信息
- 本身就是IVD器械

**示例**：
```c
// IVD软件类型
typedef enum {
    IVD_SW_DATA_ACQUISITION,      // 数据采集
    IVD_SW_DATA_PROCESSING,       // 数据处理
    IVD_SW_RESULT_CALCULATION,    // 结果计算
    IVD_SW_RESULT_INTERPRETATION, // 结果解释
    IVD_SW_QUALITY_CONTROL,       // 质量控制
    IVD_SW_LIMS                   // 实验室信息系统
} IVD_Software_Type_t;

// 软件分类评估
typedef struct {
    IVD_Software_Type_t software_type;
    char intended_use[200];
    bool provides_diagnostic_info;
    bool influences_clinical_decision;
    char ivdr_class[10];
} IVD_Software_Assessment_t;
```

#### 软件性能评价

**软件特定要求**：
- 算法验证
- 软件验证和确认（IEC 62304）
- 数据集验证
- 算法性能评估
- 临床性能验证

```c
// 软件性能评价
typedef struct {
    // 算法验证
    char algorithm_type[100];         // 算法类型
    bool algorithm_validated;         // 算法已验证
    int training_dataset_size;        // 训练数据集大小
    int validation_dataset_size;      // 验证数据集大小
    int test_dataset_size;            // 测试数据集大小
    
    // 性能指标
    float algorithm_accuracy;         // 算法准确度
    float algorithm_sensitivity;      // 算法灵敏度
    float algorithm_specificity;      // 算法特异性
    float auc_roc;                    // ROC曲线下面积
    
    // 软件验证
    bool software_verification;       // 软件验证完成
    bool software_validation;         // 软件确认完成
    char iec_62304_compliance[100];   // IEC 62304合规性
    
    // 临床验证
    int clinical_samples;             // 临床样本数
    float clinical_agreement;         // 临床一致性
} IVD_Software_Performance_t;
```



## 最佳实践

!!! tip "IVDR合规建议"
    1. **早期分类**：准确确定器械分类，影响整个认证策略
    2. **性能评价规划**：早期规划性能研究，特别是临床性能研究
    3. **EURL准备**：D类和某些C类器械需要EURL参与，提前准备
    4. **数据质量**：确保分析和临床性能数据的质量和完整性
    5. **软件文档**：IVD软件需要完整的IEC 62304文档
    6. **参考方法**：选择合适的参考方法或金标准
    7. **样本量计算**：正确计算临床性能研究的样本量
    8. **公告机构选择**：选择有IVD经验的公告机构

## 常见陷阱

!!! warning "注意事项"
    1. **分类错误**：错误分类导致认证路径错误
    2. **性能评价不足**：性能数据不充分或不符合要求
    3. **科学有效性缺失**：未能证明分析物与临床状况的关系
    4. **样本量不足**：临床性能研究样本量不够
    5. **参考标准不当**：参考方法或金标准选择不合适
    6. **软件验证不完整**：IVD软件缺少完整的验证文档
    7. **EURL延误**：未预留EURL审查时间（D类器械）
    8. **干扰物质测试不全**：未测试所有相关干扰物质

## 实践练习

1. **IVD分类练习**：
   - 分析一个血液分析系统
   - 确定每个分析物的分类
   - 选择合适的合格评定程序

2. **性能评价计划**：
   - 为一个新的IVD器械制定性能评价计划
   - 设计分析性能研究
   - 设计临床性能研究
   - 计算所需样本量

3. **软件性能评价**：
   - 为一个IVD分析软件设计性能评价
   - 定义算法验证方法
   - 规划临床验证研究

## 自测问题

??? question "问题1：IVDR的分类规则与MDR有什么不同？如何确定IVD器械的分类？"
    
    ??? success "答案"
        **IVDR vs MDR分类差异**：
        
        | 方面 | IVDR | MDR |
        |------|------|-----|
        | 分类数量 | 4类（A、B、C、D） | 4类（I、IIa、IIb、III） |
        | 分类依据 | 分析物风险 + 预期用途 | 侵入性 + 使用时间 + 部位 |
        | 分类规则 | 7条规则 + 清单A/B | 22条规则 |
        | 最高风险 | D类 | III类 |
        
        **IVD分类方法**：
        
        **步骤1：检查是否为自测试器械**
        - 是 → 规则1（B类或C类）
        
        **步骤2：检查分析物是否在清单A或B**
        - 清单A → D类（HIV、HBV、HCV、血型等）
        - 清单B → C类（PSA、肿瘤标志物等）
        
        **步骤3：检查是否为伴随诊断**
        - 是 → C类或D类
        
        **步骤4：检查是否用于癌症筛查/诊断**
        - 是 → C类
        
        **步骤5：其他**
        - 默认 → A类
        
        **分类示例**：
        
        ```
        示例1：血糖检测系统（自测试）
        - 规则1：自测试器械
        - 不在清单A/B
        - 分类：B类
        
        示例2：HIV检测试剂盒
        - 规则2：清单A分析物（HIV）
        - 分类：D类
        
        示例3：PSA检测（前列腺癌筛查）
        - 规则2：清单B分析物（PSA）
        - 规则6：癌症筛查
        - 分类：C类（取较高分类）
        
        示例4：HER2基因检测（伴随诊断）
        - 规则3：伴随诊断
        - 用于指导曲妥珠单抗治疗
        - 分类：C类
        
        示例5：血常规分析
        - 不属于规则1-6
        - 规则7：其他
        - 分类：A类
        ```
        
        **知识点回顾**：IVDR分类主要基于分析物的风险和预期用途，清单A/B是关键参考。

??? question "问题2：什么是性能评价？它与MDR的临床评价有什么区别？"
    
    ??? success "答案"
        **性能评价定义**：
        
        性能评价是评估和分析数据以验证IVD器械的科学有效性和性能的过程。
        
        **性能评价三要素**：
        
        ```
        性能评价 = 科学有效性 + 分析性能 + 临床性能
        
        1. 科学有效性（Scientific Validity）：
           - 分析物与临床状况的关系
           - 生物学机制
           - 文献证据
           问题：这个分析物能反映临床状况吗？
        
        2. 分析性能（Analytical Performance）：
           - 准确度、精密度
           - 灵敏度、特异性
           - 检测限、测量范围
           问题：这个检测方法准确可靠吗？
        
        3. 临床性能（Clinical Performance）：
           - 诊断灵敏度、特异性
           - 阳性/阴性预测值
           - 临床有效性
           问题：这个检测在临床上有用吗？
        ```
        
        **与MDR临床评价的区别**：
        
        | 方面 | IVDR性能评价 | MDR临床评价 |
        |------|------------|-----------|
        | 适用对象 | IVD器械 | 医疗器械 |
        | 核心内容 | 科学有效性 + 分析性能 + 临床性能 | 临床安全性和有效性 |
        | 分析性能 | 强制要求 | 不适用 |
        | 临床性能 | 诊断准确性 | 治疗效果 |
        | 参考标准 | 金标准检测方法 | 临床结局 |
        | 研究类型 | 诊断准确性研究 | 临床试验 |
        
        **实际示例**：
        
        **IVD器械（血糖仪）性能评价**：
        ```
        1. 科学有效性：
           - 血糖水平与糖尿病的关系（已确立）
           - 文献支持
        
        2. 分析性能：
           - 准确度：±15% vs 参考方法
           - 精密度：CV < 5%
           - 测量范围：20-600 mg/dL
           - 干扰：血细胞比容、维生素C等
        
        3. 临床性能：
           - 诊断灵敏度：98%
           - 诊断特异性：97%
           - 与金标准（实验室方法）比较
           - 临床样本：200例
        ```
        
        **MDR器械（胰岛素泵）临床评价**：
        ```
        1. 临床安全性：
           - 不良事件发生率
           - 低血糖事件
           - 设备故障
        
        2. 临床有效性：
           - HbA1c改善
           - 血糖控制
           - 生活质量
        
        3. 临床试验：
           - 随机对照试验
           - 长期随访
           - 临床结局评估
        ```
        
        **知识点回顾**：IVDR性能评价关注诊断准确性，MDR临床评价关注治疗效果。

??? question "问题3：什么是EURL？它在IVDR认证中的作用是什么？"
    
    ??? success "答案"
        **EURL（European Union Reference Laboratory）欧盟参考实验室**：
        
        **定义**：
        EURL是由欧盟委员会指定的专业实验室，为公告机构提供科学和技术支持。
        
        **EURL的作用**：
        
        ```
        EURL职责：
        ├── 评估性能评价计划
        ├── 审查性能研究数据
        ├── 验证制造商声称的性能
        ├── 提供科学和技术意见
        ├── 支持公告机构决策
        └── 协调不同公告机构的评估
        ```
        
        **何时需要EURL参与**：
        
        | 器械类别 | EURL参与 | 说明 |
        |---------|---------|------|
        | A类 | 不需要 | 自我声明 |
        | B类 | 不需要 | 公告机构直接评估 |
        | C类 | 可能需要 | 新技术、新分析物 |
        | D类 | **强制需要** | 所有D类器械 |
        
        **EURL评估流程**：
        
        ```
        步骤1：公告机构提交
        ├── 制造商向公告机构申请
        ├── 公告机构审查初步文档
        └── 公告机构向EURL提交评估请求
        
        步骤2：EURL审查（60天）
        ├── 审查性能评价计划
        ├── 评估科学有效性证据
        ├── 审查分析性能数据
        ├── 审查临床性能数据
        └── 可能要求补充信息
        
        步骤3：EURL意见
        ├── 正面意见：支持认证
        ├── 负面意见：不支持认证
        ├── 有条件意见：需要改进
        └── 建议和要求
        
        步骤4：公告机构决策
        ├── 考虑EURL意见
        ├── 进行自己的评估
        └── 做出最终决定
        ```
        
        **EURL评估内容**：
        
        ```c
        // EURL评估检查清单
        typedef struct {
            // 科学有效性
            bool biomarker_clinical_relevance;    // 生物标志物临床相关性
            bool literature_adequate;             // 文献充分性
            bool biological_mechanism_clear;      // 生物学机制清晰
            
            // 分析性能
            bool analytical_study_design_appropriate; // 研究设计合适
            bool analytical_data_sufficient;      // 数据充分
            bool analytical_performance_acceptable; // 性能可接受
            bool interferents_adequately_tested;  // 干扰物质测试充分
            
            // 临床性能
            bool clinical_study_design_appropriate; // 研究设计合适
            bool sample_size_adequate;            // 样本量充分
            bool reference_standard_appropriate;  // 参考标准合适
            bool clinical_performance_acceptable; // 性能可接受
            
            // 总体意见
            char eurl_opinion[500];
            bool positive_opinion;
        } EURL_Assessment_Checklist_t;
        ```
        
        **EURL对时间线的影响**：
        
        ```
        D类器械认证时间线（18-24个月）：
        
        月份 0-6：准备阶段
        ├── 性能评价计划
        ├── 分析性能研究
        ├── 临床性能研究
        └── 技术文档编制
        
        月份 6-9：公告机构初审
        ├── 提交申请
        ├── 公告机构审查
        └── 准备EURL提交
        
        月份 9-11：EURL审查（60天）⭐
        ├── EURL评估
        ├── 可能的补充信息请求
        └── EURL意见
        
        月份 11-15：公告机构最终审核
        ├── 考虑EURL意见
        ├── 完成评估
        └── 颁发证书
        
        月份 15-18：上市准备
        ├── EUDAMED注册
        ├── 标签和包装
        └── 分销准备
        ```
        
        **实际案例**：
        
        **案例：HIV检测试剂盒（D类）**
        ```
        器械：HIV抗体/抗原检测试剂盒
        分类：D类（清单A分析物）
        EURL：强制参与
        
        EURL评估重点：
        1. 科学有效性：
           - HIV抗体/抗原与HIV感染的关系
           - 窗口期考虑
        
        2. 分析性能：
           - 分析灵敏度（检测限）
           - 分析特异性（交叉反应）
           - 不同HIV亚型的检测
        
        3. 临床性能：
           - 诊断灵敏度：>99.5%
           - 诊断特异性：>99.5%
           - 与金标准（Western Blot）比较
           - 血清转换样本测试
        
        EURL审查时间：60天
        EURL意见：正面，但建议增加某些HIV亚型的测试
        ```
        
        **知识点回顾**：EURL是IVDR特有的机制，为D类器械提供独立的科学评估，确保高风险IVD的质量。

## 相关资源

- [MDR概述](mdr-overview.md) - 医疗器械法规
- [CE认证流程](ce-marking.md) - CE认证详细流程
- [IEC 62304](../iec-62304/index.md) - 软件生命周期标准
- [ISO 13485](../iso-13485/index.md) - 质量管理体系

## 参考文献

1. **Regulation (EU) 2017/746** - In Vitro Diagnostic Medical Device Regulation (IVDR)
2. **MDCG 2020-16** - Guidance on Classification Rules for in vitro Diagnostic Medical Devices
3. **MDCG 2022-2** - Guidance on Performance Evaluation of In Vitro Diagnostic Medical Devices
4. **ISO 20916:2019** - In vitro diagnostic medical devices - Clinical performance studies
5. **ISO 18113 series** - In vitro diagnostic medical devices - Information supplied by the manufacturer
6. **CLSI EP series** - Clinical and Laboratory Standards Institute Evaluation Protocols
7. **IEC 62304:2006+AMD1:2015** - Medical device software - Software life cycle processes
8. **European Commission IVDR Resources** - https://ec.europa.eu/health/md_sector/overview_en
