---
title: 技术文档要求
description: MDR/IVDR技术文档编制详细指南，包括附录II/III要求和文档结构
difficulty: 中级
estimated_time: 2.5小时
tags:
  - 技术文档
  - MDR附录II
  - MDR附录III
  - 文档编制
related_modules:
  - zh/regulatory-standards/eu-regulations/mdr-overview
  - zh/regulatory-standards/eu-regulations/ce-marking
  - zh/regulatory-standards/iec-62304
last_updated: '2026-02-10'
version: '1.0'
language: zh-CN
---

# 技术文档要求

## 学习目标

完成本模块后，你将能够：
- 理解MDR/IVDR技术文档的结构和要求
- 掌握附录II和附录III的区别
- 编制符合要求的技术文档
- 建立文档追溯系统
- 管理技术文档的变更和维护
- 准备公告机构审核所需文档

## 前置知识

- MDR/IVDR法规基础
- 医疗器械设计开发流程
- 风险管理基础（ISO 14971）
- 质量管理体系（ISO 13485）

## 内容

### 技术文档概述

**技术文档的目的**：

技术文档是证明医疗器械符合MDR/IVDR要求的核心证据包，用于：
- 证明符合通用安全和性能要求（GSPR）
- 支持器械分类决策
- 提供设计和制造信息
- 证明效益-风险比可接受
- 支持公告机构评估

**技术文档类型**：

```
MDR技术文档：
├── 附录II：完整技术文档
│   ├── 适用于：所有器械类别
│   ├── 内容：完整的设计、制造、验证信息
│   └── 用于：公告机构全面评估
└── 附录III：技术文档摘要
    ├── 适用于：I类器械（某些情况）
    ├── 内容：简化的技术信息
    └── 用于：EUDAMED公开信息
```


### MDR附录II技术文档结构

**完整技术文档目录（8个主要部分）**：

```
附录II技术文档结构：

1. 器械描述和规格
   ├── 1.1 器械标识和通用描述
   ├── 1.2 预期用途和适应症
   ├── 1.3 器械描述
   ├── 1.4 参考器械
   ├── 1.5 变体和配置
   └── 1.6 附件、配件和其他器械

2. 标签和使用说明书
   ├── 2.1 标签
   ├── 2.2 使用说明书
   └── 2.3 患者植入卡（如适用）

3. 设计和制造信息
   ├── 3.1 设计和开发
   ├── 3.2 制造和包装
   ├── 3.3 材料和物质
   └── 3.4 灭菌和微生物控制

4. 通用安全和性能要求（GSPR）
   ├── 4.1 GSPR检查清单
   ├── 4.2 符合性证明
   └── 4.3 协调标准应用

5. 效益-风险分析和风险管理
   ├── 5.1 风险管理计划
   ├── 5.2 风险分析
   ├── 5.3 风险评估
   ├── 5.4 风险控制
   └── 5.5 风险管理报告

6. 产品验证和确认
   ├── 6.1 验证计划
   ├── 6.2 性能测试
   ├── 6.3 软件验证
   └── 6.4 临床前评价

7. 临床评价和上市后临床随访
   ├── 7.1 临床评价计划
   ├── 7.2 临床评价报告
   ├── 7.3 临床调查
   └── 7.4 PMCF计划

8. 其他信息
   ├── 8.1 符合其他法规
   ├── 8.2 上市后监督计划
   └── 8.3 定期安全更新报告
```

#### 第1部分：器械描述和规格

**1.1 器械标识和通用描述**：

```c
// 器械标识信息
typedef struct {
    // 基本标识
    char device_name[100];            // 商品名
    char device_model[50];            // 型号
    char basic_udi_di[50];            // 基本UDI-DI
    char device_version[20];          // 版本号
    
    // 制造商信息
    char manufacturer_name[100];
    char manufacturer_address[200];
    char manufacturer_srn[50];        // EUDAMED SRN
    
    // 授权代表（如适用）
    char authorized_rep_name[100];
    char authorized_rep_address[200];
    
    // 分类信息
    char mdr_classification[10];      // I, IIa, IIb, III
    char classification_rule[50];     // 适用规则
    bool custom_made;                 // 定制器械
    bool investigational;             // 研究用器械
    
    // 器械类型
    bool active_device;               // 有源器械
    bool implantable;                 // 植入器械
    bool invasive;                    // 侵入性器械
    bool software;                    // 软件器械
} Device_Identification_t;
```

**1.2 预期用途和适应症**：

```c
// 预期用途定义
typedef struct {
    // 预期用途
    char intended_purpose[500];       // 详细描述
    char medical_indication[300];     // 医学适应症
    char target_population[200];      // 目标人群
    char target_body_part[100];       // 目标身体部位
    
    // 使用环境
    char intended_user[100];          // 预期使用者
    char use_environment[100];        // 使用环境
    bool professional_use;            // 专业使用
    bool lay_user;                    // 非专业使用
    bool home_use;                    // 家用
    
    // 禁忌症
    char contraindications[500];      // 禁忌症
    char warnings[500];               // 警告
    char precautions[500];            // 注意事项
    
    // 预期效益
    char intended_benefits[500];      // 预期效益
    char clinical_outcomes[300];      // 临床结局
} Intended_Use_t;

// 示例：血糖监测系统
Intended_Use_t glucose_meter_intended_use = {
    .intended_purpose = "用于糖尿病患者的毛细血管全血葡萄糖浓度的体外定量测定，"
                       "用于自我监测血糖水平，辅助糖尿病管理",
    .medical_indication = "糖尿病（1型和2型）",
    .target_population = "18岁及以上的糖尿病患者",
    .target_body_part = "不适用（体外诊断）",
    .intended_user = "患者（自我检测）和医护人员",
    .use_environment = "家庭、医院、诊所",
    .professional_use = true,
    .lay_user = true,
    .home_use = true,
    .contraindications = "新生儿；严重脱水、休克或高渗状态的患者",
    .warnings = "不用于糖尿病诊断；不用于低血糖或高血糖昏迷的诊断",
    .precautions = "极端血细胞比容值可能影响结果；某些药物可能干扰测量",
    .intended_benefits = "准确监测血糖水平，帮助患者和医生优化糖尿病管理，"
                        "减少并发症风险",
    .clinical_outcomes = "改善血糖控制（HbA1c降低），减少低血糖事件"
};
```


**1.3 器械描述**：

```c
// 器械详细描述
typedef struct {
    // 物理描述
    char physical_description[500];   // 外观、尺寸、重量
    char materials[300];              // 材料清单
    char components[500];             // 组件清单
    
    // 技术规格
    char technical_specifications[1000]; // 技术参数
    char performance_characteristics[500]; // 性能特征
    
    // 工作原理
    char principle_of_operation[500]; // 工作原理
    char mechanism_of_action[500];    // 作用机制
    
    // 软件（如适用）
    bool contains_software;
    char software_version[20];
    char software_description[500];
    char software_safety_class[10];   // IEC 62304 A/B/C
    
    // 附件和配件
    int num_accessories;
    char accessories[10][100];
} Device_Description_t;
```

**1.4 参考器械**：

```c
// 参考器械（用于临床评价）
typedef struct {
    char reference_device_name[100];
    char manufacturer[100];
    char model[50];
    
    // 等效性分析
    bool technical_equivalent;        // 技术等效
    bool biological_equivalent;       // 生物学等效
    bool clinical_equivalent;         // 临床等效
    
    // 相似性
    char similarities[500];           // 相似之处
    char differences[500];            // 差异之处
    
    // 临床数据
    char clinical_data_available[500]; // 可用临床数据
    bool sufficient_for_equivalence;   // 足以证明等效性
} Reference_Device_t;
```

#### 第2部分：标签和使用说明书

**标签要求**：

```c
// 标签信息检查清单
typedef struct {
    // 强制标签信息
    bool manufacturer_name_address;
    bool device_name_model;
    bool lot_batch_number;
    bool serial_number;
    bool udi_carrier;
    bool manufacturing_date;
    bool expiry_date;                 // 如适用
    bool sterile_indication;          // 如适用
    bool single_use_indication;       // 如适用
    bool ce_marking;
    bool notified_body_number;        // 如需要
    
    // 警告和符号
    bool warnings_present;
    bool symbols_correct;             // ISO 15223-1
    bool instructions_reference;
    
    // 特殊要求
    bool implant_card_reference;      // 植入器械
    bool prescription_only;           // 处方器械
    bool reprocessing_instructions;   // 可重复使用
    
    // 语言要求
    bool local_language;              // 目标市场语言
    bool multilingual;                // 多语言
} Label_Requirements_t;
```

**使用说明书（IFU）结构**：

```
使用说明书内容：

1. 器械标识
   ├── 名称、型号、版本
   ├── 制造商信息
   └── UDI

2. 预期用途
   ├── 适应症
   ├── 目标人群
   └── 预期效益

3. 禁忌症、警告和注意事项
   ├── 禁忌症
   ├── 警告
   ├── 注意事项
   └── 副作用

4. 使用说明
   ├── 安装和设置
   ├── 操作步骤
   ├── 维护和清洁
   └── 故障排除

5. 技术规格
   ├── 性能参数
   ├── 环境条件
   └── 兼容性

6. 符号说明
   ├── 符号图例
   └── 符号含义

7. 其他信息
   ├── 储存条件
   ├── 运输条件
   ├── 处置说明
   └── 联系信息
```

#### 第3部分：设计和制造信息

**3.1 设计和开发**：

```c
// 设计和开发文档
typedef struct {
    // 设计计划
    char design_plan[200];            // 设计计划文档
    char design_team[500];            // 设计团队
    char design_phases[500];          // 设计阶段
    
    // 设计输入
    char user_needs[500];             // 用户需求
    char design_requirements[1000];   // 设计需求
    char regulatory_requirements[500]; // 法规要求
    char standards_applied[500];      // 应用标准
    
    // 设计输出
    char design_specifications[1000]; // 设计规格
    char drawings[200];               // 图纸
    char schematics[200];             // 原理图
    char software_design[200];        // 软件设计文档
    
    // 设计验证
    char verification_plan[200];      // 验证计划
    char verification_report[200];    // 验证报告
    bool all_requirements_verified;   // 所有需求已验证
    
    // 设计确认
    char validation_plan[200];        // 确认计划
    char validation_report[200];      // 确认报告
    bool intended_use_validated;      // 预期用途已确认
    
    // 设计变更
    char change_control_procedure[200]; // 变更控制程序
    int num_design_changes;           // 设计变更数量
    char design_history_file[200];    // 设计历史文件
} Design_Development_t;
```

**设计追溯矩阵**：

```c
// 追溯矩阵条目
typedef struct {
    int requirement_id;
    char requirement_description[200];
    char design_specification[200];
    char verification_method[100];
    char verification_reference[100];
    char validation_reference[100];
    char risk_analysis_reference[100];
    bool traced;
} Traceability_Matrix_Entry_t;

// 示例追溯矩阵
Traceability_Matrix_Entry_t traceability_example[] = {
    {
        .requirement_id = 1,
        .requirement_description = "测量范围：20-600 mg/dL",
        .design_specification = "DS-001: 传感器规格",
        .verification_method = "性能测试",
        .verification_reference = "VR-001",
        .validation_reference = "VAL-001",
        .risk_analysis_reference = "RA-001",
        .traced = true
    },
    {
        .requirement_id = 2,
        .requirement_description = "测量准确度：±15% vs 参考方法",
        .design_specification = "DS-002: 算法规格",
        .verification_method = "准确度测试",
        .verification_reference = "VR-002",
        .validation_reference = "VAL-002",
        .risk_analysis_reference = "RA-002",
        .traced = true
    }
    // ... 更多条目
};
```

**3.2 制造和包装**：

```c
// 制造信息
typedef struct {
    // 制造场所
    char manufacturing_site[200];
    char site_address[200];
    bool iso_13485_certified;
    char certificate_number[50];
    
    // 制造流程
    char manufacturing_process[1000]; // 制造流程描述
    char process_flow_diagram[200];   // 流程图
    char critical_processes[500];     // 关键工序
    
    // 过程验证
    bool process_validated;
    char validation_protocol[200];
    char validation_report[200];
    
    // 包装
    char packaging_description[500];
    char packaging_materials[300];
    bool packaging_validated;
    char packaging_validation[200];
    
    // 灭菌（如适用）
    bool sterile_device;
    char sterilization_method[100];
    char sterilization_validation[200];
} Manufacturing_Info_t;
```

#### 第4部分：GSPR符合性

**GSPR检查清单**：

```c
// GSPR检查清单条目
typedef struct {
    char gspr_number[20];             // GSPR编号（如23.1）
    char gspr_requirement[500];       // 要求描述
    bool applicable;                  // 是否适用
    char compliance_method[200];      // 符合方法
    char evidence[500];               // 证据
    char standards_applied[200];      // 应用标准
    bool compliant;                   // 是否符合
} GSPR_Checklist_Entry_t;

// GSPR示例条目
GSPR_Checklist_Entry_t gspr_examples[] = {
    {
        .gspr_number = "1",
        .gspr_requirement = "器械应达到制造商规定的性能，并设计和制造成在正常使用条件下适合其预期用途",
        .applicable = true,
        .compliance_method = "设计验证和确认",
        .evidence = "验证报告VR-001-010；确认报告VAL-001",
        .standards_applied = "ISO 13485:2016",
        .compliant = true
    },
    {
        .gspr_number = "17.1",
        .gspr_requirement = "含有电子可编程系统（包括软件）的器械应设计成确保这些系统的重复性、可靠性和性能",
        .applicable = true,
        .compliance_method = "软件生命周期过程",
        .evidence = "IEC 62304文档；软件验证报告",
        .standards_applied = "IEC 62304:2006+AMD1:2015",
        .compliant = true
    },
    {
        .gspr_number = "17.4",
        .gspr_requirement = "含有软件或本身为软件的器械应根据最新技术考虑网络安全",
        .applicable = true,
        .compliance_method = "网络安全风险管理",
        .evidence = "威胁建模报告；渗透测试报告",
        .standards_applied = "IEC 81001-5-1:2021",
        .compliant = true
    }
    // ... 所有适用的GSPR
};
```


#### 第5部分：效益-风险分析和风险管理

**风险管理文件结构（ISO 14971）**：

```c
// 风险管理文件
typedef struct {
    // 风险管理计划
    char risk_management_plan[200];
    char risk_acceptance_criteria[500];
    char risk_analysis_methods[200];  // FMEA, FTA等
    
    // 风险分析
    int num_hazards_identified;
    char hazard_list[200];
    char hazardous_situations[200];
    
    // 风险评估
    char risk_matrix[200];            // 风险矩阵
    int num_unacceptable_risks;
    int num_acceptable_risks;
    
    // 风险控制
    char risk_control_measures[200];
    bool all_risks_controlled;
    
    // 残余风险
    char residual_risk_analysis[200];
    bool residual_risks_acceptable;
    
    // 效益-风险分析
    char benefit_risk_analysis[200];
    bool benefits_outweigh_risks;
    
    // 风险管理报告
    char risk_management_report[200];
    char risk_management_review_date[20];
} Risk_Management_File_t;
```

**风险分析示例**：

```c
// 风险分析条目
typedef struct {
    int hazard_id;
    char hazard[200];
    char hazardous_situation[200];
    char harm[200];
    int severity;                     // 1-5
    int probability;                  // 1-5
    int initial_risk;                 // severity * probability
    char risk_control[300];
    int residual_severity;
    int residual_probability;
    int residual_risk;
    bool acceptable;
} Risk_Analysis_Entry_t;

// 示例：血糖仪风险分析
Risk_Analysis_Entry_t risk_examples[] = {
    {
        .hazard_id = 1,
        .hazard = "测量不准确",
        .hazardous_situation = "血糖仪显示错误的血糖值",
        .harm = "患者基于错误数据调整胰岛素剂量，导致低血糖或高血糖",
        .severity = 4,                // 严重
        .probability = 3,             // 偶尔
        .initial_risk = 12,           // 不可接受
        .risk_control = "1) 严格的设计验证和确认\n"
                       "2) 符合ISO 15197:2013准确度要求\n"
                       "3) 质量控制测试\n"
                       "4) 用户培训",
        .residual_severity = 4,
        .residual_probability = 1,    // 罕见
        .residual_risk = 4,           // 可接受
        .acceptable = true
    },
    {
        .hazard_id = 2,
        .hazard = "软件故障",
        .hazardous_situation = "软件崩溃或计算错误",
        .harm = "无法测量血糖或显示错误结果",
        .severity = 3,
        .probability = 2,
        .initial_risk = 6,
        .risk_control = "1) IEC 62304 Class B软件开发\n"
                       "2) 100%单元测试覆盖率\n"
                       "3) 软件验证和确认\n"
                       "4) 错误处理机制",
        .residual_severity = 3,
        .residual_probability = 1,
        .residual_risk = 3,
        .acceptable = true
    },
    {
        .hazard_id = 3,
        .hazard = "网络安全漏洞",
        .hazardous_situation = "未授权访问患者数据",
        .harm = "隐私泄露，数据篡改",
        .severity = 4,
        .probability = 3,
        .initial_risk = 12,
        .risk_control = "1) 数据加密（AES-256）\n"
                       "2) 安全认证机制\n"
                       "3) 渗透测试\n"
                       "4) 安全更新机制",
        .residual_severity = 4,
        .residual_probability = 1,
        .residual_risk = 4,
        .acceptable = true
    }
    // ... 更多风险
};
```

#### 第6部分：产品验证和确认

**验证计划**：

```c
// 验证活动
typedef struct {
    int verification_id;
    char requirement_reference[50];
    char verification_method[100];    // 测试、检查、分析
    char test_protocol[200];
    char acceptance_criteria[200];
    char test_report[200];
    bool passed;
} Verification_Activity_t;

// 验证类型
typedef enum {
    VERIFICATION_PERFORMANCE,         // 性能验证
    VERIFICATION_SAFETY,              // 安全验证
    VERIFICATION_EMC,                 // 电磁兼容性
    VERIFICATION_BIOCOMPATIBILITY,    // 生物相容性
    VERIFICATION_SOFTWARE,            // 软件验证
    VERIFICATION_USABILITY,           // 可用性验证
    VERIFICATION_PACKAGING,           // 包装验证
    VERIFICATION_STERILIZATION,       // 灭菌验证
    VERIFICATION_STABILITY            // 稳定性验证
} Verification_Type_t;
```

**性能测试示例**：

```c
// 性能测试结果
typedef struct {
    char test_name[100];
    char test_standard[50];
    char test_method[200];
    int sample_size;
    char acceptance_criteria[200];
    char test_results[500];
    bool passed;
    char test_report_reference[100];
} Performance_Test_t;

// 示例：血糖仪性能测试
Performance_Test_t performance_tests[] = {
    {
        .test_name = "系统准确度",
        .test_standard = "ISO 15197:2013",
        .test_method = "与YSI参考方法比较，100个样本",
        .sample_size = 100,
        .acceptance_criteria = "95%结果在±15 mg/dL（<100）或±15%（≥100）",
        .test_results = "98%结果符合要求（98/100）",
        .passed = true,
        .test_report_reference = "TR-001"
    },
    {
        .test_name = "重复性",
        .test_standard = "ISO 15197:2013",
        .test_method = "3个浓度水平，各10次重复测量",
        .sample_size = 30,
        .acceptance_criteria = "CV ≤ 5%",
        .test_results = "低浓度CV=3.2%, 中浓度CV=2.8%, 高浓度CV=3.5%",
        .passed = true,
        .test_report_reference = "TR-002"
    },
    {
        .test_name = "干扰物质",
        .test_standard = "ISO 15197:2013",
        .test_method = "测试常见干扰物质的影响",
        .sample_size = 50,
        .acceptance_criteria = "偏差 < 10%",
        .test_results = "所有测试干扰物质偏差 < 8%",
        .passed = true,
        .test_report_reference = "TR-003"
    }
};
```

**软件验证**：

```c
// 软件验证文档（IEC 62304）
typedef struct {
    // 软件单元测试
    char unit_test_plan[200];
    char unit_test_report[200];
    float unit_test_coverage;         // 目标：100%
    int num_unit_tests;
    int num_passed;
    
    // 软件集成测试
    char integration_test_plan[200];
    char integration_test_report[200];
    int num_integration_tests;
    int num_integration_passed;
    
    // 软件系统测试
    char system_test_plan[200];
    char system_test_report[200];
    int num_system_tests;
    int num_system_passed;
    
    // 追溯
    char requirements_trace_matrix[200];
    bool all_requirements_tested;
    
    // 已知异常
    int num_known_anomalies;
    char anomaly_list[200];
    bool all_anomalies_evaluated;
} Software_Verification_t;
```

**确认（Validation）**：

```c
// 确认活动
typedef struct {
    char validation_protocol[200];
    char validation_environment[200]; // 实际使用环境
    int num_users;                    // 用户数量
    int num_use_scenarios;            // 使用场景数
    
    // 确认结果
    char validation_report[200];
    bool intended_use_confirmed;
    bool user_needs_met;
    bool safe_and_effective;
    
    // 可用性验证
    char usability_validation[200];
    int num_use_errors;
    bool use_errors_acceptable;
} Validation_t;
```

#### 第7部分：临床评价

**临床评价计划**：

```c
// 临床评价计划
typedef struct {
    // 计划信息
    char clinical_evaluation_plan[200];
    char evaluation_team[500];
    char evaluation_scope[500];
    
    // 评价策略
    bool literature_review;
    bool clinical_investigation;
    bool equivalent_device_data;
    bool pmcf_data;
    
    // 文献综述
    char literature_search_strategy[500];
    char databases_searched[200];
    char search_terms[500];
    char inclusion_criteria[500];
    char exclusion_criteria[500];
    int num_studies_identified;
    int num_studies_included;
    
    // 等效器械
    int num_equivalent_devices;
    char equivalent_device_analysis[200];
    
    // 临床数据
    bool clinical_data_available;
    char clinical_data_sources[500];
    int num_patients;
    
    // 临床评价报告
    char clinical_evaluation_report[200];
    char cer_conclusion[500];
    bool benefit_risk_acceptable;
} Clinical_Evaluation_Plan_t;
```

**临床评价报告（CER）结构**：

```
临床评价报告内容：

1. 执行摘要
   ├── 器械描述
   ├── 评价范围
   └── 结论

2. 器械描述
   ├── 技术特征
   ├── 预期用途
   └── 分类

3. 临床背景
   ├── 疾病/状况描述
   ├── 当前治疗方法
   └── 目标人群

4. 评价方法
   ├── 文献检索策略
   ├── 数据来源
   └── 评价标准

5. 文献综述
   ├── 文献筛选流程
   ├── 纳入研究列表
   └── 证据综合

6. 等效器械分析
   ├── 等效器械识别
   ├── 技术等效性
   └── 临床等效性

7. 临床数据分析
   ├── 安全性数据
   ├── 性能数据
   └── 效益数据

8. 效益-风险分析
   ├── 效益评估
   ├── 风险评估
   └── 效益-风险比

9. 结论
   ├── 临床安全性
   ├── 临床性能
   └── 符合性声明

10. PMCF计划
    ├── PMCF目标
    ├── 数据收集方法
    └── 时间表
```


#### 第8部分：其他信息

**上市后监督计划**：

```c
// PMS计划
typedef struct {
    char pms_plan[200];
    
    // 主动监控
    bool customer_feedback_system;
    bool complaint_handling;
    bool trend_analysis;
    bool literature_monitoring;
    
    // 被动监控
    bool vigilance_system;
    bool adverse_event_reporting;
    bool fsca_procedure;
    
    // PMCF
    char pmcf_plan[200];
    bool pmcf_required;
    char pmcf_methods[500];
    
    // PSUR
    bool psur_required;
    int psur_frequency_years;
    char psur_template[200];
} PMS_Plan_t;
```

### 文档管理和维护

**文档控制系统**：

```c
// 文档控制
typedef struct {
    char document_id[50];
    char document_title[200];
    char document_type[50];
    char version[20];
    char revision_date[20];
    char author[100];
    char reviewer[100];
    char approver[100];
    
    // 状态
    char status[20];                  // 草稿、审查中、批准、废弃
    bool controlled_document;
    
    // 变更
    int revision_number;
    char change_description[500];
    char change_reason[500];
    
    // 分发
    char distribution_list[500];
    bool obsolete_copies_retrieved;
} Document_Control_t;
```

**文档版本控制**：

```
版本编号规则：
├── 主版本号.次版本号.修订号
├── 例如：2.1.3
│   ├── 2 = 主版本（重大变更）
│   ├── 1 = 次版本（中等变更）
│   └── 3 = 修订号（小变更）
└── 变更类型：
    ├── 主版本：设计变更、新功能
    ├── 次版本：改进、增强
    └── 修订：错误修正、澄清
```

**变更管理**：

```c
// 变更请求
typedef struct {
    int change_request_id;
    char change_date[20];
    char requestor[100];
    
    // 变更描述
    char change_description[500];
    char change_reason[500];
    char affected_documents[500];
    
    // 影响评估
    bool affects_safety;
    bool affects_performance;
    bool requires_revalidation;
    bool requires_nb_notification;
    
    // 批准
    char approval_status[20];
    char approver[100];
    char approval_date[20];
    
    // 实施
    char implementation_date[20];
    bool implemented;
} Change_Request_t;
```

### 公告机构审核准备

**文档完整性检查清单**：

```c
// 技术文档完整性检查
typedef struct {
    // 第1部分：器械描述
    bool device_identification;
    bool intended_use;
    bool device_description;
    bool reference_devices;
    
    // 第2部分：标签和IFU
    bool labeling;
    bool instructions_for_use;
    bool patient_implant_card;        // 如适用
    
    // 第3部分：设计和制造
    bool design_development_plan;
    bool design_inputs;
    bool design_outputs;
    bool design_verification;
    bool design_validation;
    bool traceability_matrix;
    bool manufacturing_information;
    bool process_validation;
    
    // 第4部分：GSPR
    bool gspr_checklist;
    bool gspr_compliance_evidence;
    bool standards_list;
    
    // 第5部分：风险管理
    bool risk_management_plan;
    bool risk_analysis;
    bool risk_evaluation;
    bool risk_control;
    bool residual_risk_analysis;
    bool benefit_risk_analysis;
    bool risk_management_report;
    
    // 第6部分：验证确认
    bool verification_plan;
    bool performance_testing;
    bool safety_testing;
    bool emc_testing;
    bool biocompatibility;            // 如适用
    bool software_verification;       // 如适用
    bool usability_validation;
    bool validation_report;
    
    // 第7部分：临床评价
    bool clinical_evaluation_plan;
    bool literature_review;
    bool equivalent_device_analysis;
    bool clinical_data;
    bool clinical_evaluation_report;
    bool pmcf_plan;
    
    // 第8部分：其他
    bool pms_plan;
    bool psur_template;               // 如适用
    bool other_regulations;
    
    // 软件特定（如适用）
    bool iec_62304_documentation;
    bool soup_list;
    bool cybersecurity_documentation;
    
    // 完整性评分
    int total_items;
    int completed_items;
    float completeness_percentage;
} Technical_Documentation_Completeness_t;

// 计算完整性
void calculate_completeness(Technical_Documentation_Completeness_t* doc) {
    doc->total_items = 35;  // 根据实际检查项调整
    doc->completed_items = 0;
    
    // 统计完成项
    if (doc->device_identification) doc->completed_items++;
    if (doc->intended_use) doc->completed_items++;
    // ... 其他项
    
    doc->completeness_percentage = 
        (float)doc->completed_items / doc->total_items * 100.0;
}
```

**审核准备检查清单**：

```
审核前准备：

1. 文档组织（2周前）
   ├── 按附录II结构组织
   ├── 创建文档索引
   ├── 检查版本一致性
   └── 准备电子版和纸质版

2. 追溯性检查（1周前）
   ├── 需求追溯矩阵完整
   ├── 风险追溯完整
   ├── 测试追溯完整
   └── 标准符合性追溯

3. 内部审核（1周前）
   ├── 技术审核
   ├── 质量审核
   ├── 法规审核
   └── 纠正不符合项

4. 问题准备（3天前）
   ├── 预期问题列表
   ├── 准备答案
   ├── 准备支持证据
   └── 团队培训

5. 最终检查（1天前）
   ├── 文档完整性
   ├── 文档可访问性
   ├── 团队准备就绪
   └── 场地准备
```

## 最佳实践

!!! tip "技术文档编制建议"
    1. **早期开始**：从设计阶段就开始文档化
    2. **使用模板**：建立标准化模板和检查清单
    3. **持续更新**：随设计变更及时更新文档
    4. **追溯性**：建立完整的追溯矩阵
    5. **内部审核**：提交前进行彻底的内部审核
    6. **版本控制**：使用严格的版本控制系统
    7. **团队协作**：多部门协作编制文档
    8. **质量优先**：宁可延迟也要确保质量

## 常见陷阱

!!! warning "注意事项"
    1. **文档不完整**：缺少关键信息或证据
    2. **追溯性缺失**：需求、设计、测试之间无法追溯
    3. **版本不一致**：不同文档引用的版本不一致
    4. **GSPR证据不足**：未充分证明符合GSPR
    5. **风险分析不充分**：风险识别不全面
    6. **临床证据薄弱**：临床评价报告过于简单
    7. **软件文档缺失**：软件器械缺少IEC 62304文档
    8. **变更未文档化**：设计变更未及时更新文档

## 实践练习

1. **文档结构设计**：
   - 为一个医疗器械设计技术文档结构
   - 创建文档索引
   - 识别所需文档清单

2. **追溯矩阵建立**：
   - 创建需求追溯矩阵
   - 建立需求-设计-测试追溯
   - 验证追溯完整性

3. **GSPR检查清单**：
   - 为一个器械填写GSPR检查清单
   - 识别适用的GSPR
   - 准备符合性证据

4. **文档审核**：
   - 审核一份技术文档
   - 识别缺失信息
   - 提出改进建议

## 自测问题

??? question "问题1：MDR附录II技术文档的8个主要部分是什么？每部分的核心内容是什么？"
    
    ??? success "答案"
        **MDR附录II技术文档的8个主要部分**：
        
        **1. 器械描述和规格**
        - 核心内容：器械标识、预期用途、技术规格、参考器械
        - 目的：清晰定义器械是什么、用于什么
        
        **2. 标签和使用说明书**
        - 核心内容：标签信息、使用说明书、患者植入卡
        - 目的：确保用户正确使用器械
        
        **3. 设计和制造信息**
        - 核心内容：设计开发过程、制造流程、材料、灭菌
        - 目的：证明器械按照规范设计和制造
        
        **4. 通用安全和性能要求（GSPR）**
        - 核心内容：GSPR检查清单、符合性证明、应用标准
        - 目的：证明符合MDR附录I的所有适用要求
        
        **5. 效益-风险分析和风险管理**
        - 核心内容：风险管理文件（ISO 14971）、效益-风险分析
        - 目的：证明风险可接受且效益大于风险
        
        **6. 产品验证和确认**
        - 核心内容：验证计划和报告、性能测试、软件验证、确认报告
        - 目的：证明器械满足规格要求和预期用途
        
        **7. 临床评价和PMCF**
        - 核心内容：临床评价计划、文献综述、临床数据、CER、PMCF计划
        - 目的：证明临床安全性和有效性
        
        **8. 其他信息**
        - 核心内容：PMS计划、PSUR、其他法规符合性
        - 目的：证明上市后持续监督和合规
        
        **文档关系图**：
        ```
        技术文档结构：
        ├── 第1部分：定义器械（是什么）
        ├── 第2部分：如何使用
        ├── 第3部分：如何制造
        ├── 第4部分：符合法规要求
        ├── 第5部分：风险可接受
        ├── 第6部分：性能符合规格
        ├── 第7部分：临床安全有效
        └── 第8部分：上市后监督
        ```
        
        **知识点回顾**：技术文档是系统性证明器械安全有效的证据包，8个部分相互关联，缺一不可。

??? question "问题2：什么是追溯矩阵？为什么它在技术文档中很重要？"
    
    ??? success "答案"
        **追溯矩阵定义**：
        
        追溯矩阵是一个表格或数据库，用于建立和维护产品开发各阶段之间的双向追溯关系。
        
        **追溯类型**：
        
        ```
        1. 需求追溯：
           用户需求 ↔ 设计需求 ↔ 设计规格 ↔ 测试用例
        
        2. 风险追溯：
           危害 ↔ 风险 ↔ 风险控制措施 ↔ 验证
        
        3. 标准追溯：
           标准要求 ↔ 设计规格 ↔ 测试 ↔ 证据
        
        4. GSPR追溯：
           GSPR要求 ↔ 设计特征 ↔ 验证 ↔ 标准
        ```
        
        **追溯矩阵示例**：
        
        | 需求ID | 需求描述 | 设计规格 | 风险分析 | 验证方法 | 测试报告 | 状态 |
        |--------|---------|---------|---------|---------|---------|------|
        | REQ-001 | 测量范围20-600 mg/dL | DS-001 | RA-001 | 性能测试 | TR-001 | ✓ |
        | REQ-002 | 准确度±15% | DS-002 | RA-002 | 准确度测试 | TR-002 | ✓ |
        | REQ-003 | 5秒测量时间 | DS-003 | RA-003 | 性能测试 | TR-003 | ✓ |
        
        **重要性**：
        
        **1. 证明完整性**
        - 确保所有需求都有对应的设计
        - 确保所有设计都经过验证
        - 确保没有遗漏
        
        **2. 支持变更管理**
        - 快速识别变更影响范围
        - 确定需要重新测试的项目
        - 评估变更风险
        
        **3. 简化审核**
        - 公告机构可快速验证符合性
        - 清晰展示设计逻辑
        - 减少审核问题
        
        **4. 质量保证**
        - 确保设计过程系统化
        - 防止需求遗漏
        - 支持根本原因分析
        
        **5. 法规要求**
        - MDR要求证明符合GSPR
        - ISO 13485要求设计控制
        - IEC 62304要求软件追溯
        
        **建立追溯矩阵的最佳实践**：
        
        ```
        1. 工具选择：
           ├── 简单项目：Excel
           ├── 中等项目：专用工具（如Jama, Polarion）
           └── 复杂项目：PLM系统集成
        
        2. 持续维护：
           ├── 随设计变更实时更新
           ├── 定期审查完整性
           └── 版本控制
        
        3. 双向追溯：
           ├── 向前追溯：需求→设计→测试
           └── 向后追溯：测试→设计→需求
        
        4. 自动化：
           ├── 使用工具自动生成
           ├── 自动检查完整性
           └── 自动生成报告
        ```
        
        **知识点回顾**：追溯矩阵是技术文档的"骨架"，确保设计过程的系统性和完整性，是公告机构审核的重点。

??? question "问题3：如何准备技术文档以应对公告机构审核？有哪些关键检查点？"
    
    ??? success "答案"
        **技术文档审核准备策略**：
        
        **阶段1：文档完整性检查（提交前4周）**
        
        ```
        完整性检查清单：
        ├── 所有必需文档都已编制
        ├── 文档版本一致
        ├── 文档间引用正确
        ├── 追溯矩阵完整
        ├── 所有附件齐全
        └── 文档索引准确
        ```
        
        **阶段2：内容质量审查（提交前3周）**
        
        ```
        质量审查要点：
        
        1. GSPR符合性：
           ├── 所有适用GSPR已识别
           ├── 符合性证据充分
           ├── 标准应用正确
           └── 不适用项有合理说明
        
        2. 风险管理：
           ├── 危害识别全面
           ├── 风险评估合理
           ├── 风险控制有效
           ├── 残余风险可接受
           └── 效益-风险比正面
        
        3. 验证确认：
           ├── 所有需求已验证
           ├── 测试方法适当
           ├── 接受标准明确
           ├── 测试结果符合要求
           └── 预期用途已确认
        
        4. 临床评价：
           ├── 文献检索系统
           ├── 证据质量高
           ├── 等效性分析充分
           ├── 临床数据足够
           └── 结论有支持
        
        5. 软件文档（如适用）：
           ├── IEC 62304合规
           ├── 软件分类正确
           ├── 测试覆盖率充分
           ├── SOUP管理完整
           └── 网络安全文档齐全
        ```
        
        **阶段3：内部审核（提交前2周）**
        
        ```
        内部审核流程：
        
        1. 技术审核：
           ├── 技术专家审查
           ├── 检查技术准确性
           ├── 验证数据一致性
           └── 识别技术问题
        
        2. 质量审核：
           ├── 质量团队审查
           ├── 检查文档控制
           ├── 验证程序符合性
           └── 识别质量问题
        
        3. 法规审核：
           ├── 法规专家审查
           ├── 检查法规符合性
           ├── 验证GSPR覆盖
           └── 识别合规问题
        
        4. 模拟审核：
           ├── 模拟公告机构审核
           ├── 提出可能的问题
           ├── 测试团队准备
           └── 改进应对策略
        ```
        
        **阶段4：问题预测和准备（提交前1周）**
        
        ```
        常见审核问题类别：
        
        1. 分类相关：
           Q: "为什么选择这个分类？"
           准备：分类依据文档，规则应用说明
        
        2. 风险管理：
           Q: "如何确保识别了所有危害？"
           准备：危害识别方法，团队专业性证明
        
        3. 临床证据：
           Q: "临床数据是否充分？"
           准备：文献质量评估，样本量计算
        
        4. 软件验证：
           Q: "测试覆盖率如何？"
           准备：覆盖率报告，测试策略说明
        
        5. 网络安全：
           Q: "如何应对网络威胁？"
           准备：威胁模型，安全控制措施
        ```
        
        **关键检查点总结**：
        
        | 检查点 | 重要性 | 常见问题 | 准备建议 |
        |--------|--------|---------|---------|
        | 文档完整性 | ⭐⭐⭐⭐⭐ | 缺少文档 | 使用检查清单 |
        | 追溯性 | ⭐⭐⭐⭐⭐ | 追溯断裂 | 追溯矩阵工具 |
        | GSPR符合性 | ⭐⭐⭐⭐⭐ | 证据不足 | 逐条准备证据 |
        | 风险管理 | ⭐⭐⭐⭐⭐ | 风险遗漏 | 多方法识别 |
        | 临床评价 | ⭐⭐⭐⭐ | 证据薄弱 | 系统文献综述 |
        | 软件文档 | ⭐⭐⭐⭐ | IEC 62304不符 | 早期遵循标准 |
        | 版本一致性 | ⭐⭐⭐ | 版本混乱 | 严格版本控制 |
        
        **最终检查清单（提交前1天）**：
        
        ```
        □ 所有文档已审查批准
        □ 文档索引准确
        □ 电子版和纸质版一致
        □ 追溯矩阵完整
        □ 内部审核不符合项已关闭
        □ 团队已培训
        □ 预期问题已准备答案
        □ 支持证据易于访问
        □ 备份文档已准备
        □ 联系人信息已确认
        ```
        
        **知识点回顾**：技术文档审核准备需要系统方法，关键是完整性、追溯性和证据充分性。

## 相关资源

- [MDR概述](mdr-overview.md) - MDR法规详解
- [CE认证流程](ce-marking.md) - CE认证详细流程
- [临床评价](clinical-evaluation.md) - 临床评价报告编制
- [IEC 62304](../iec-62304/index.md) - 软件生命周期标准

## 参考文献

1. **Regulation (EU) 2017/745** - Medical Device Regulation (MDR), Annex II and III
2. **ISO 13485:2016** - Medical devices - Quality management systems
3. **ISO 14971:2019** - Application of risk management to medical devices
4. **IEC 62304:2006+AMD1:2015** - Medical device software
5. **MDCG 2019-9** - Summary of Safety and Clinical Performance
6. **MDCG 2020-5** - Clinical Evaluation
7. **MDCG 2021-24** - Guidance on classification of medical devices
8. **MEDDEV 2.7/1 Rev 4** - Clinical Evaluation (legacy guidance)

