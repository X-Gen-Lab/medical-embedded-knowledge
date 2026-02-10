---
title: 上市后监督
description: MDR/IVDR上市后监督系统详解，包括PMS、警戒、FSCA和PSUR
difficulty: 中级
estimated_time: 2.5小时
tags:
  - 上市后监督
  - PMS
  - 警戒系统
  - FSCA
  - PSUR
related_modules:
  - zh/regulatory-standards/eu-regulations/mdr-overview
  - zh/regulatory-standards/eu-regulations/clinical-evaluation
  - zh/regulatory-standards/iso-13485
last_updated: '2026-02-10'
version: '1.0'
language: zh-CN
---

# 上市后监督

## 学习目标

完成本模块后，你将能够：
- 理解MDR/IVDR上市后监督要求
- 建立PMS系统
- 实施警戒系统
- 处理不良事件报告
- 执行现场安全纠正措施（FSCA）
- 编制定期安全更新报告（PSUR）
- 整合PMCF到PMS系统

## 前置知识

- MDR/IVDR法规基础
- 质量管理体系（ISO 13485）
- 风险管理（ISO 14971）
- 临床评价基础

## 内容

### 上市后监督概述

**PMS定义（MDR第2条）**：

上市后监督（Post-Market Surveillance, PMS）是制造商为收集和审查已上市器械的经验而进行的所有活动，以识别任何需要立即采取纠正或预防措施的理由。

**PMS的目的**：

```
PMS目标：
├── 确认器械的安全性和性能
├── 识别新出现的风险
├── 确保效益-风险比持续可接受
├── 识别误用或滥用
├── 收集真实世界数据
├── 支持临床评价更新
└── 满足法规要求
```


**PMS法规要求**：

```
MDR关键条款：
├── 第83条：上市后监督
│   ├── 所有制造商必须建立PMS系统
│   ├── 与器械风险和类别相适应
│   └── 系统化收集和分析数据
├── 第84条：定期安全更新报告（PSUR）
│   ├── IIa/IIb类：每2年
│   ├── III类/植入：每年
│   └── 提交至EUDAMED
├── 第85条：趋势报告
│   ├── 识别统计显著增加
│   ├── 报告给主管当局
│   └── 采取适当措施
├── 第86-92条：警戒和上市后安全
│   ├── 严重事件报告
│   ├── 现场安全纠正措施
│   └── 安全通知
└── 附录III：PMS计划和PSUR
    ├── PMS计划要求
    └── PSUR内容要求
```

### PMS系统建立

**PMS系统组成**：

```
PMS系统架构：

1. 主动监控
   ├── 客户反馈收集
   ├── 用户调查
   ├── 文献监控
   ├── 竞争对手分析
   └── 社交媒体监控

2. 被动监控
   ├── 投诉处理
   ├── 不良事件报告
   ├── 现场反馈
   └── 退货分析

3. 数据分析
   ├── 趋势分析
   ├── 根本原因分析
   ├── 风险评估
   └── 效益-风险评估

4. 纠正预防措施
   ├── CAPA系统
   ├── 设计变更
   ├── FSCA
   └── 产品召回

5. 报告和沟通
   ├── 内部报告
   ├── 主管当局报告
   ├── 公告机构通知
   └── 客户沟通
```

**PMS计划**：

```c
// PMS计划结构
typedef struct {
    // 计划信息
    char pms_plan_version[20];
    char pms_plan_date[20];
    char responsible_person[100];
    
    // 器械信息
    char device_name[100];
    char device_model[50];
    char mdr_classification[10];
    char udi_di[50];
    
    // PMS目标
    char pms_objectives[1000];
    char specific_questions[1000];
    
    // 数据收集方法
    bool complaint_handling;
    bool adverse_event_reporting;
    bool customer_feedback;
    bool literature_monitoring;
    bool registry_participation;
    bool pmcf_activities;
    char other_methods[500];
    
    // 数据分析
    char analysis_methods[500];
    char trend_analysis_methods[500];
    int analysis_frequency_months;
    
    // 报告
    bool psur_required;
    int psur_frequency_years;
    char internal_reporting[500];
    
    // 资源
    char pms_team[500];
    char budget[100];
    char tools_systems[500];
    
    // 时间表
    char implementation_date[20];
    char review_frequency[50];
} PMS_Plan_t;
```

**PMS数据来源**：

```c
// PMS数据来源
typedef enum {
    DATA_SOURCE_COMPLAINTS,           // 投诉
    DATA_SOURCE_ADVERSE_EVENTS,       // 不良事件
    DATA_SOURCE_CUSTOMER_FEEDBACK,    // 客户反馈
    DATA_SOURCE_LITERATURE,           // 文献
    DATA_SOURCE_CLINICAL_DATA,        // 临床数据
    DATA_SOURCE_PMCF,                 // PMCF
    DATA_SOURCE_REGISTRY,             // 注册研究
    DATA_SOURCE_RETURNS,              // 退货
    DATA_SOURCE_FIELD_REPORTS,        // 现场报告
    DATA_SOURCE_SOCIAL_MEDIA,         // 社交媒体
    DATA_SOURCE_COMPETITOR_INFO       // 竞争对手信息
} PMS_Data_Source_t;

// PMS数据记录
typedef struct {
    int record_id;
    char record_date[20];
    PMS_Data_Source_t source;
    
    // 数据内容
    char description[1000];
    char device_model[50];
    char lot_serial[50];
    
    // 分类
    bool safety_related;
    bool performance_related;
    char severity[20];                // 轻微、中等、严重
    
    // 分析
    char root_cause[500];
    char risk_assessment[500];
    bool trend_identified;
    
    // 措施
    char corrective_action[500];
    char preventive_action[500];
    bool fsca_required;
    
    // 状态
    char status[20];                  // 开放、调查中、已关闭
    char closure_date[20];
} PMS_Data_Record_t;
```

### 投诉处理

**投诉处理流程**：

```
投诉处理流程：

步骤1：接收和记录（24小时内）
├── 接收投诉
├── 分配投诉编号
├── 记录投诉信息
│   ├── 投诉人信息
│   ├── 器械信息
│   ├── 投诉描述
│   └── 接收日期
└── 确认收到

步骤2：初步评估（3个工作日内）
├── 评估严重性
├── 确定是否为不良事件
├── 评估是否需要立即措施
└── 分配调查责任人

步骤3：调查（根据严重性）
├── 收集信息
│   ├── 器械检查
│   ├── 记录审查
│   ├── 访谈
│   └── 测试
├── 根本原因分析
│   ├── 5 Why分析
│   ├── 鱼骨图
│   └── 故障树分析
└── 风险评估

步骤4：纠正预防措施
├── 确定CAPA
├── 实施CAPA
├── 验证有效性
└── 文档化

步骤5：回复和关闭
├── 回复投诉人
├── 更新记录
├── 趋势分析
└── 关闭投诉
```

**投诉分类**：

```c
// 投诉分类
typedef struct {
    int complaint_id;
    char complaint_date[20];
    char complainant[100];
    
    // 器械信息
    char device_model[50];
    char lot_number[50];
    char serial_number[50];
    char manufacturing_date[20];
    
    // 投诉描述
    char complaint_description[1000];
    char event_date[20];
    char event_location[200];
    
    // 分类
    char complaint_category[50];      // 性能、安全、标签等
    char severity[20];                // 轻微、中等、严重
    bool reportable_event;            // 是否需要报告
    bool device_returned;             // 器械是否退回
    
    // 调查
    char investigation_findings[1000];
    char root_cause[500];
    char risk_assessment[500];
    
    // CAPA
    char corrective_action[500];
    char preventive_action[500];
    char capa_reference[50];
    
    // 状态
    char status[20];
    char assigned_to[100];
    char target_closure_date[20];
    char actual_closure_date[20];
} Complaint_Record_t;
```

### 警戒系统

**警戒系统定义**：

警戒（Vigilance）是指收集、记录、评估和报告与医疗器械使用相关的严重事件和现场安全纠正措施的系统。

**严重事件定义（MDR第2条）**：

```
严重事件是指直接或间接导致、可能导致或可能已导致以下任何情况的事件：
├── 患者、使用者或其他人员死亡
├── 患者、使用者或其他人员健康状况暂时或永久严重恶化
├── 对公共健康的严重威胁
└── 器械特征或性能的严重恶化
```

**严重事件报告时限**：

```
报告时限：
├── 死亡或不可预见的严重健康恶化
│   └── 立即报告（知晓后2天内）
├── 其他严重事件
│   └── 10天内报告
└── 趋势报告
    └── 识别后立即报告
```

**严重事件报告流程**：

```c
// 严重事件报告
typedef struct {
    // 事件信息
    char event_id[50];
    char event_date[20];
    char report_date[20];
    char reporter[100];
    
    // 器械信息
    char device_name[100];
    char device_model[50];
    char udi_di[50];
    char lot_serial[50];
    
    // 事件描述
    char event_description[2000];
    char event_location[200];
    char event_circumstances[1000];
    
    // 严重性
    bool death;
    bool serious_deterioration;
    bool public_health_threat;
    bool device_malfunction;
    char severity_justification[500];
    
    // 患者信息（匿名化）
    int patient_age;
    char patient_gender[10];
    char medical_condition[500];
    
    // 初步评估
    char preliminary_assessment[1000];
    bool device_related;
    char causality_assessment[500];
    
    // 报告
    bool reported_to_authority;
    char authority_report_number[50];
    char report_date_to_authority[20];
    bool reported_to_notified_body;
    
    // 调查
    char investigation_status[50];
    char investigation_findings[2000];
    char root_cause[1000];
    
    // 措施
    char immediate_actions[1000];
    bool fsca_required;
    char fsca_reference[50];
} Serious_Incident_Report_t;
```

**事件评估流程**：

```
事件评估步骤：

步骤1：事件识别（立即）
├── 接收事件信息
├── 初步评估严重性
└── 确定是否为严重事件

步骤2：初步报告（2-10天）
├── 收集初步信息
├── 评估因果关系
├── 报告给主管当局
└── 通知公告机构

步骤3：调查（持续）
├── 详细调查
├── 根本原因分析
├── 风险评估
└── 确定纠正措施

步骤4：最终报告（调查完成后）
├── 编制最终报告
├── 提交给主管当局
├── 更新风险管理文件
└── 更新临床评价

步骤5：跟进措施
├── 实施CAPA
├── FSCA（如需要）
├── 监控有效性
└── 文档化
```


### 现场安全纠正措施（FSCA）

**FSCA定义**：

现场安全纠正措施（Field Safety Corrective Action, FSCA）是制造商为降低与已上市器械相关的死亡或严重健康恶化风险而采取的纠正措施。

**FSCA类型**：

```
FSCA类型：
├── 召回（Recall）
│   ├── 完全召回：所有器械
│   ├── 部分召回：特定批次/型号
│   └── 自愿召回 vs 强制召回
├── 修改（Modification）
│   ├── 硬件修改
│   ├── 软件更新
│   └── 标签变更
├── 退货（Return）
│   ├── 退回制造商
│   └── 销毁
└── 建议（Advisory）
    ├── 使用限制
    ├── 额外监控
    └── 培训要求
```

**FSCA决策流程**：

```c
// FSCA决策
typedef struct {
    // 触发因素
    char trigger_event[500];
    char risk_assessment[1000];
    int risk_level;                   // 1-5
    
    // FSCA评估
    bool fsca_required;
    char fsca_justification[1000];
    char fsca_type[50];               // 召回、修改、建议
    char fsca_scope[500];             // 影响范围
    
    // 受影响器械
    char affected_models[500];
    char affected_lots[500];
    int num_devices_affected;
    int num_devices_in_field;
    
    // 措施描述
    char corrective_action[1000];
    char implementation_method[500];
    char timeline[500];
    
    // 沟通计划
    char communication_plan[1000];
    bool customer_notification;
    bool authority_notification;
    bool public_notification;
    
    // 有效性监控
    char effectiveness_criteria[500];
    char monitoring_plan[500];
} FSCA_Decision_t;
```

**FSCA实施流程**：

```
FSCA实施步骤：

步骤1：FSCA决策（立即）
├── 风险评估
├── 确定FSCA类型
├── 定义受影响器械
└── 制定行动计划

步骤2：通知主管当局（立即）
├── 提交FSCA通知
├── 包含初步信息
├── 说明计划措施
└── 提供时间表

步骤3：通知客户（立即）
├── 编制现场安全通知（FSN）
├── 发送给所有受影响客户
├── 说明风险和措施
└── 提供联系方式

步骤4：实施纠正措施（按计划）
├── 执行纠正措施
│   ├── 召回器械
│   ├── 修改器械
│   └── 提供培训
├── 记录实施过程
└── 跟踪完成情况

步骤5：监控有效性（持续）
├── 跟踪响应率
├── 验证措施有效性
├── 监控残余风险
└── 定期报告进展

步骤6：最终报告（完成后）
├── 编制FSCA最终报告
├── 提交给主管当局
├── 更新技术文档
└── 关闭FSCA
```

**现场安全通知（FSN）**：

```c
// 现场安全通知
typedef struct {
    // FSN信息
    char fsn_number[50];
    char fsn_date[20];
    char fsn_type[50];                // 紧急、重要、通知
    
    // 器械信息
    char device_name[100];
    char device_model[50];
    char udi_di[50];
    char affected_lots[500];
    
    // 问题描述
    char problem_description[1000];
    char risk_description[1000];
    char incidents_reported[500];
    
    // 措施
    char action_required[1000];
    char action_timeline[200];
    char action_instructions[1000];
    
    // 联系信息
    char contact_person[100];
    char contact_phone[50];
    char contact_email[100];
    
    // 回执
    bool acknowledgment_required;
    char acknowledgment_deadline[20];
} Field_Safety_Notice_t;
```

### 趋势报告

**趋势定义**：

趋势是指与器械相关的类似事件或观察结果的统计显著增加。

**趋势分析方法**：

```c
// 趋势分析
typedef struct {
    // 数据收集
    char data_period[50];             // 分析周期
    int total_devices_sold;
    int total_devices_in_use;
    
    // 事件统计
    int num_complaints;
    int num_adverse_events;
    int num_serious_incidents;
    int num_returns;
    
    // 事件分类
    char event_categories[10][100];
    int events_per_category[10];
    
    // 趋势检测
    char statistical_method[100];     // 控制图、卡方检验等
    float baseline_rate;
    float current_rate;
    float rate_increase;              // 百分比
    bool statistically_significant;
    
    // 趋势评估
    bool trend_identified;
    char trend_description[500];
    char potential_causes[1000];
    char risk_assessment[1000];
    
    // 措施
    bool action_required;
    char planned_actions[1000];
    bool reportable_to_authority;
} Trend_Analysis_t;

// 趋势检测算法示例
bool detect_trend(Trend_Analysis_t* analysis) {
    // 简化的趋势检测逻辑
    float threshold = 1.5;  // 50%增加阈值
    
    if (analysis->current_rate > analysis->baseline_rate * threshold) {
        analysis->trend_identified = true;
        analysis->rate_increase = 
            (analysis->current_rate - analysis->baseline_rate) / 
            analysis->baseline_rate * 100.0;
        return true;
    }
    return false;
}
```

**趋势报告触发条件**：

```
趋势报告触发：
├── 统计显著增加
│   ├── 事件发生率增加>50%
│   ├── 统计检验p<0.05
│   └── 持续多个周期
├── 新类型事件
│   ├── 以前未观察到的事件
│   ├── 新的失效模式
│   └── 新的风险识别
└── 严重性增加
    ├── 事件严重程度升级
    ├── 后果更严重
    └── 风险水平提高
```

### 定期安全更新报告（PSUR）

**PSUR目的和要求**：

```
PSUR目的：
├── 总结PMS数据
├── 评估效益-风险比
├── 确认安全性和性能
├── 识别新风险
└── 支持临床评价更新

PSUR频率：
├── I类：不需要
├── IIa类：每2年
├── IIb类：每2年
├── III类：每年
└── 植入器械：每年
```

**PSUR结构**：

```
PSUR内容（MDR附录III）：

1. 执行摘要
   ├── 报告期间
   ├── 主要发现
   └── 结论

2. 器械标识和描述
   ├── 器械名称和型号
   ├── UDI-DI
   ├── 预期用途
   └── 分类

3. 销售和使用数据
   ├── 销售数量
   ├── 使用中器械数量
   ├── 地理分布
   └── 使用人群

4. PMS数据汇总
   ├── 投诉数据
   ├── 不良事件数据
   ├── FSCA数据
   └── 其他PMS数据

5. 安全性分析
   ├── 不良事件分析
   ├── 严重事件分析
   ├── 趋势分析
   └── 新风险识别

6. 性能分析
   ├── 性能投诉
   ├── 性能问题
   └── 性能趋势

7. 效益-风险评估
   ├── 效益评估
   ├── 风险评估
   ├── 效益-风险比
   └── 可接受性判断

8. 临床评价更新
   ├── 新临床数据
   ├── 文献更新
   ├── PMCF数据
   └── CER更新需求

9. 结论和措施
   ├── 总体结论
   ├── 已采取措施
   ├── 计划措施
   └── CER更新计划

10. 附录
    ├── 数据表格
    ├── 统计分析
    └── 支持文档
```

**PSUR编制代码示例**：

```c
// PSUR数据结构
typedef struct {
    // 报告信息
    char psur_version[20];
    char reporting_period_start[20];
    char reporting_period_end[20];
    char psur_date[20];
    
    // 器械信息
    char device_name[100];
    char device_models[500];
    char udi_di[50];
    char mdr_classification[10];
    
    // 销售和使用
    int devices_sold_period;
    int cumulative_devices_sold;
    int estimated_devices_in_use;
    char geographic_distribution[500];
    
    // PMS数据汇总
    int num_complaints;
    int num_adverse_events;
    int num_serious_incidents;
    int num_deaths;
    int num_fsca;
    
    // 事件率
    float complaint_rate;             // 每1000台器械
    float adverse_event_rate;
    float serious_incident_rate;
    
    // 安全性分析
    char safety_analysis[2000];
    int num_new_risks_identified;
    char new_risks[1000];
    bool trend_identified;
    char trend_description[500];
    
    // 性能分析
    char performance_analysis[1000];
    bool performance_issues;
    char performance_issues_desc[500];
    
    // 效益-风险评估
    char benefit_assessment[1000];
    char risk_assessment[1000];
    char benefit_risk_ratio[500];
    bool benefit_risk_acceptable;
    
    // 临床评价
    bool cer_update_required;
    char cer_update_rationale[500];
    char pmcf_data_summary[1000];
    
    // 结论
    char overall_conclusion[1000];
    char actions_taken[1000];
    char planned_actions[1000];
    
    // 提交
    bool submitted_to_eudamed;
    char submission_date[20];
} PSUR_t;
```

### PMS系统整合

**PMS与其他系统的整合**：

```
PMS系统整合：

├── 质量管理系统（ISO 13485）
│   ├── CAPA系统
│   ├── 不合格品控制
│   ├── 内部审核
│   └── 管理评审
│
├── 风险管理系统（ISO 14971）
│   ├── 上市后风险识别
│   ├── 风险评估更新
│   ├── 风险控制措施
│   └── 风险管理报告更新
│
├── 临床评价系统
│   ├── PMCF数据
│   ├── CER更新
│   ├── 文献监控
│   └── 效益-风险分析
│
├── 设计控制系统
│   ├── 设计变更
│   ├── 验证确认
│   ├── 设计输入更新
│   └── 设计历史文件
│
└── 法规事务系统
    ├── 主管当局报告
    ├── 公告机构通知
    ├── EUDAMED更新
    └── 证书维护
```


## 最佳实践

!!! tip "PMS系统成功要素"
    1. **系统化方法**：建立系统化的PMS流程和程序
    2. **主动监控**：不要只依赖被动投诉，主动收集数据
    3. **及时响应**：快速响应严重事件和趋势
    4. **数据质量**：确保PMS数据的准确性和完整性
    5. **跨部门协作**：PMS需要质量、法规、研发等部门协作
    6. **持续改进**：利用PMS数据持续改进产品
    7. **文档化**：详细记录所有PMS活动
    8. **培训**：培训员工识别和报告安全问题

## 常见陷阱

!!! warning "注意事项"
    1. **报告延迟**：未在规定时限内报告严重事件
    2. **趋势未识别**：未能识别统计显著的趋势
    3. **FSCA延误**：延迟实施必要的FSCA
    4. **数据分析不足**：收集数据但未充分分析
    5. **PSUR质量低**：PSUR过于简单，缺乏深度分析
    6. **系统未整合**：PMS与其他系统脱节
    7. **资源不足**：PMS资源和人员不足
    8. **培训不足**：员工不了解PMS要求

## 实践练习

1. **建立PMS系统**：
   - 为一个医疗器械设计PMS系统
   - 编制PMS计划
   - 定义数据收集方法

2. **投诉处理**：
   - 处理一个投诉案例
   - 进行根本原因分析
   - 确定CAPA

3. **严重事件报告**：
   - 评估一个事件是否为严重事件
   - 编制严重事件报告
   - 确定报告时限

4. **PSUR编制**：
   - 收集和分析PMS数据
   - 进行效益-风险评估
   - 编制PSUR

## 自测问题

??? question "问题1：什么是严重事件？报告时限是多少？"
    
    ??? success "答案"
        **严重事件定义（MDR第2条第65款）**：
        
        严重事件是指直接或间接导致、可能导致或可能已导致以下任何情况的事件：
        
        **1. 死亡**
        - 患者死亡
        - 使用者死亡
        - 其他人员死亡
        
        **2. 健康状况严重恶化**
        - 危及生命的疾病或伤害
        - 身体或精神功能永久损害
        - 身体结构或功能永久损害
        - 需要医疗或手术干预以防止上述情况
        
        **3. 对公共健康的严重威胁**
        - 可能影响大量人群
        - 需要公共卫生措施
        
        **4. 器械特征或性能的严重恶化**
        - 可能导致上述情况的器械问题
        
        **报告时限**：
        
        ```
        报告时限（MDR第87条）：
        
        1. 死亡或不可预见的严重健康恶化：
           └── 立即报告，最迟知晓后2天内
        
        2. 其他严重事件：
           └── 知晓后10天内报告
        
        3. 后续报告：
           ├── 调查进展报告：30天内
           ├── 最终报告：调查完成后
           └── 更新：有新信息时
        
        4. 趋势报告：
           └── 识别后立即报告
        ```
        
        **报告流程**：
        
        ```
        Day 0：事件发生/知晓
        ├── 立即评估严重性
        └── 确定是否为严重事件
        
        Day 1-2：初步报告（如为死亡或不可预见）
        ├── 通过EUDAMED报告
        ├── 提供初步信息
        └── 说明计划调查
        
        Day 1-10：初步报告（其他严重事件）
        ├── 收集初步信息
        ├── 评估因果关系
        └── 提交报告
        
        Day 30：进展报告
        ├── 调查进展
        ├── 初步发现
        └── 计划措施
        
        调查完成：最终报告
        ├── 调查结论
        ├── 根本原因
        ├── 纠正措施
        └── 预防措施
        ```
        
        **判断示例**：
        
        | 事件 | 是否严重 | 报告时限 | 理由 |
        |------|---------|---------|------|
        | 患者使用血糖仪后死亡 | 是 | 2天 | 死亡 |
        | 血糖仪显示错误导致低血糖昏迷 | 是 | 10天 | 严重健康恶化 |
        | 血糖仪屏幕破裂但无伤害 | 否 | 不报告 | 无健康影响 |
        | 多个血糖仪同一批次失效 | 是 | 10天 | 公共健康威胁 |
        
        **知识点回顾**：严重事件报告是法律要求，延迟报告可能导致处罚。

??? question "问题2：什么是FSCA？何时需要实施FSCA？"
    
    ??? success "答案"
        **FSCA定义**：
        
        现场安全纠正措施（Field Safety Corrective Action, FSCA）是制造商为降低与已上市器械相关的死亡或严重健康恶化风险而采取的纠正措施。
        
        **FSCA触发条件**：
        
        ```
        需要FSCA的情况：
        
        1. 安全风险识别
           ├── 器械缺陷可能导致严重伤害或死亡
           ├── 设计或制造问题
           ├── 标签或使用说明不充分
           └── 新风险识别
        
        2. 严重事件调查结果
           ├── 根本原因与器械相关
           ├── 风险评估显示不可接受
           ├── 需要纠正措施降低风险
           └── 影响已上市器械
        
        3. 趋势识别
           ├── 事件发生率显著增加
           ├── 新失效模式出现
           ├── 风险水平升高
           └── 需要系统性纠正
        
        4. 主管当局要求
           └── 基于监管检查或评估
        ```
        
        **FSCA类型和示例**：
        
        **1. 召回（Recall）**
        ```
        示例：血糖仪电池缺陷
        - 问题：电池可能过热起火
        - 风险：烧伤、火灾
        - 措施：召回所有受影响批次
        - 范围：全球召回
        - 时间：立即
        ```
        
        **2. 修改（Modification）**
        ```
        示例：血糖仪软件错误
        - 问题：软件计算错误
        - 风险：错误治疗决策
        - 措施：软件更新
        - 范围：所有在用器械
        - 时间：30天内完成
        ```
        
        **3. 建议（Advisory）**
        ```
        示例：血糖仪干扰问题
        - 问题：某些药物干扰测量
        - 风险：测量不准确
        - 措施：更新使用说明，用户培训
        - 范围：所有用户
        - 时间：立即通知
        ```
        
        **FSCA决策流程**：
        
        ```
        步骤1：风险评估
        ├── 识别危害
        ├── 评估严重性
        ├── 评估发生概率
        └── 计算风险水平
        
        步骤2：FSCA必要性判断
        ├── 风险是否不可接受？
        ├── 是否影响已上市器械？
        ├── 是否需要客户行动？
        └── 是否有其他控制措施？
        
        步骤3：FSCA类型选择
        ├── 召回：风险极高，无法现场修复
        ├── 修改：可现场修复或更新
        ├── 建议：需要用户注意但无需修改
        └── 组合：多种措施结合
        
        步骤4：FSCA范围确定
        ├── 受影响型号
        ├── 受影响批次
        ├── 地理范围
        └── 客户范围
        
        步骤5：实施计划
        ├── 时间表
        ├── 沟通计划
        ├── 实施方法
        └── 有效性监控
        ```
        
        **FSCA通知要求**：
        
        ```
        通知对象和时限：
        
        1. 主管当局（立即）
           ├── 提交FSCA通知
           ├── 说明问题和风险
           ├── 描述计划措施
           └── 提供时间表
        
        2. 公告机构（立即）
           ├── 通知FSCA决定
           ├── 提供相关文档
           └── 更新技术文档
        
        3. 客户（立即）
           ├── 发送现场安全通知（FSN）
           ├── 说明风险和措施
           ├── 提供明确指示
           └── 要求确认收到
        
        4. EUDAMED（立即）
           └── 上传FSCA信息
        ```
        
        **FSCA有效性监控**：
        
        ```
        监控指标：
        ├── 响应率：客户确认收到FSN的比例
        ├── 完成率：完成纠正措施的比例
        ├── 时间：完成措施所需时间
        ├── 残余风险：措施后的风险水平
        └── 新事件：措施后的事件发生率
        
        目标：
        ├── 响应率：>95%
        ├── 完成率：>90%
        ├── 时间：按计划完成
        └── 残余风险：可接受水平
        ```
        
        **知识点回顾**：FSCA是降低已上市器械风险的重要措施，必须及时实施并监控有效性。

??? question "问题3：PSUR的目的是什么？应包含哪些内容？"
    
    ??? success "答案"
        **PSUR目的**：
        
        定期安全更新报告（Periodic Safety Update Report, PSUR）是制造商定期编制的报告，用于：
        
        **1. 总结PMS数据**
        - 汇总报告期间的所有PMS数据
        - 包括投诉、不良事件、FSCA等
        - 提供统计分析
        
        **2. 评估效益-风险比**
        - 评估器械的临床效益
        - 评估器械的风险
        - 判断效益-风险比是否持续可接受
        
        **3. 确认安全性和性能**
        - 确认器械持续安全
        - 确认器械性能符合预期
        - 识别任何恶化
        
        **4. 识别新风险**
        - 识别新出现的风险
        - 识别风险变化
        - 评估风险控制措施有效性
        
        **5. 支持临床评价更新**
        - 提供上市后数据
        - 支持CER更新
        - 整合PMCF数据
        
        **PSUR内容（MDR附录III）**：
        
        ```
        PSUR结构（10个主要部分）：
        
        1. 执行摘要
           ├── 报告期间
           ├── 器械概述
           ├── 主要发现
           └── 总体结论
        
        2. 器械标识和描述
           ├── 器械名称、型号
           ├── UDI-DI
           ├── 预期用途
           ├── 分类
           └── 变体
        
        3. 销售和使用数据
           ├── 报告期间销售数量
           ├── 累计销售数量
           ├── 估计使用中器械数量
           ├── 地理分布
           └── 目标人群
        
        4. PMS数据汇总
           ├── 投诉数据
           │   ├── 总数
           │   ├── 分类
           │   └── 趋势
           ├── 不良事件数据
           │   ├── 总数
           │   ├── 严重事件数
           │   ├── 死亡数
           │   └── 分类
           ├── FSCA数据
           │   ├── FSCA数量
           │   ├── FSCA类型
           │   └── 有效性
           └── 其他PMS数据
               ├── 文献数据
               ├── PMCF数据
               └── 注册研究数据
        
        5. 安全性分析
           ├── 不良事件分析
           │   ├── 事件类型
           │   ├── 严重性分布
           │   ├── 因果关系评估
           │   └── 事件率计算
           ├── 趋势分析
           │   ├── 统计分析
           │   ├── 趋势识别
           │   └── 趋势评估
           ├── 新风险识别
           │   ├── 新危害
           │   ├── 新风险
           │   └── 风险评估
           └── 风险控制措施评估
               ├── 措施有效性
               ├── 残余风险
               └── 需要的新措施
        
        6. 性能分析
           ├── 性能投诉
           ├── 性能问题
           ├── 性能趋势
           └── 性能符合性
        
        7. 效益-风险评估
           ├── 效益评估
           │   ├── 临床效益数据
           │   ├── 真实世界证据
           │   └── 效益量化
           ├── 风险评估
           │   ├── 已知风险
           │   ├── 新识别风险
           │   └── 风险量化
           ├── 效益-风险比
           │   ├── 定性评估
           │   ├── 定量评估（如可能）
           │   └── 比较分析
           └── 可接受性判断
               ├── 效益是否大于风险
               ├── 与替代方法比较
               └── 结论
        
        8. 临床评价更新
           ├── 新临床数据
           │   ├── 新文献
           │   ├── 新临床研究
           │   └── PMCF数据
           ├── CER更新需求
           │   ├── 是否需要更新
           │   ├── 更新范围
           │   └── 更新时间表
           └── PMCF计划评估
               ├── PMCF进展
               ├── PMCF发现
               └── PMCF计划调整
        
        9. 结论和措施
           ├── 总体结论
           │   ├── 安全性结论
           │   ├── 性能结论
           │   ├── 效益-风险结论
           │   └── 符合性声明
           ├── 已采取措施
           │   ├── CAPA
           │   ├── FSCA
           │   ├── 设计变更
           │   └── 标签更新
           ├── 计划措施
           │   ├── 未来CAPA
           │   ├── 计划FSCA
           │   ├── 计划变更
           │   └── 时间表
           └── CER更新计划
               ├── 更新范围
               ├── 更新时间
               └── 资源分配
        
        10. 附录
            ├── 数据表格
            ├── 统计分析详情
            ├── 文献清单
            └── 其他支持文档
        ```
        
        **PSUR编制时间表**：
        
        | 器械类别 | PSUR频率 | 提交时间 |
        |---------|---------|---------|
        | I类 | 不需要 | - |
        | IIa类 | 每2年 | 证书周年日后60天内 |
        | IIb类 | 每2年 | 证书周年日后60天内 |
        | III类 | 每年 | 证书周年日后60天内 |
        | 植入器械 | 每年 | 证书周年日后60天内 |
        
        **PSUR质量标准**：
        
        ```
        高质量PSUR特征：
        ├── 数据完整
        │   ├── 所有PMS数据源
        │   ├── 完整的报告期间
        │   └── 准确的统计
        ├── 分析深入
        │   ├── 趋势分析
        │   ├── 根本原因分析
        │   └── 风险评估
        ├── 结论有据
        │   ├── 基于数据
        │   ├── 逻辑清晰
        │   └── 结论明确
        ├── 措施具体
        │   ├── 明确的行动
        │   ├── 时间表
        │   └── 责任人
        └── 格式规范
            ├── 遵循MDR附录III
            ├── 结构清晰
            └── 易于审查
        ```
        
        **知识点回顾**：PSUR是证明器械持续安全有效的重要文档，必须定期编制并提交至EUDAMED。

## 相关资源

- [MDR概述](mdr-overview.md) - MDR法规详解
- [临床评价](clinical-evaluation.md) - 临床评价和PMCF
- [技术文档要求](technical-documentation.md) - 技术文档编制
- [ISO 13485](../iso-13485/index.md) - 质量管理体系

## 参考文献

1. **Regulation (EU) 2017/745** - Medical Device Regulation, Articles 83-92, Annex III
2. **MDCG 2020-10/11** - Post-Market Surveillance Plan and PSUR Template
3. **MDCG 2021-25** - Serious Incident Reporting
4. **MDCG 2019-9** - Summary of Safety and Clinical Performance
5. **MDCG 2020-8** - Post-Market Clinical Follow-up
6. **ISO 13485:2016** - Medical devices - Quality management systems
7. **ISO 14971:2019** - Application of risk management to medical devices
8. **MEDDEV 2.12/1 Rev 8** - Guidelines on Medical Device Vigilance System (legacy)

