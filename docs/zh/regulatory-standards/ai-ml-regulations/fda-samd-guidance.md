# FDA SaMD指南

## 概述

FDA对软件作为医疗器械（Software as a Medical Device, SaMD）有一系列指南文件，特别是针对AI/ML的监管框架。本文档详细介绍FDA的SaMD监管要求和AI/ML特定考虑。

## 核心指南文件

### 1. Software as a Medical Device (SaMD): Clinical Evaluation (2017)

**定义SaMD**:
> 软件作为医疗器械是指预期用于一个或多个医疗目的的软件，无需成为硬件医疗器械的一部分即可实现其预期目的。

**不是SaMD的软件**:
- 仅用于驱动硬件的软件
- 仅用于数据存储和传输的软件
- 通用办公软件

**是SaMD的软件**:
- 诊断辅助软件
- 治疗决策支持软件
- 疾病风险预测软件
- 医疗影像分析软件

### 2. AI/ML-Based SaMD Action Plan (2021)

**五大支柱**:

**支柱1: 基于良好机器学习实践（GMLP）的监管框架**
```markdown
良好机器学习实践包括:
- 数据质量和管理
- 特征提取和选择
- 模型设计和训练
- 模型评估和验证
- 文档和可追溯性
```

**支柱2: 患者中心的方法**
- 考虑患者视角
- 透明度和可解释性
- 患者参与设计

**支柱3: 基于风险的监管方法**
- 根据风险等级调整监管强度
- 预定变更控制计划（PCCP）

**支柱4: 真实世界性能监控**
- 上市后持续监控
- 性能漂移检测
- 及时采取纠正措施

**支柱5: 监管科学进步**
- 开发新的评估方法
- 与学术界和产业界合作

### 3. Proposed Regulatory Framework for Modifications to AI/ML-Based SaMD (2019)

**预定变更控制计划（PCCP）**:

**传统方法的问题**:
```
每次算法更新 → 重新提交FDA → 等待审批（数月）
→ 创新受阻，无法及时改进
```

**PCCP解决方案**:
```
1. 预先定义变更范围（SaMD Pre-Specifications）
2. 描述变更管理流程（Algorithm Change Protocol）
3. FDA批准PCCP
4. 在批准范围内自主更新
5. 定期向FDA报告
```

**SaMD Pre-Specifications示例**:
```markdown
## 预定变更规格

### 性能改进
- 目标: 提高敏感性从90%到95%
- 约束: 特异性不低于85%
- 方法: 增加训练数据，优化模型架构

### 输入数据扩展
- 当前: 仅支持Canon CR-2眼底相机
- 计划: 支持Topcon TRC-50DX
- 验证: 在新设备上达到相同性能标准

### 适用人群扩展
- 当前: 18-80岁成人
- 计划: 扩展到12-18岁青少年
- 验证: 在青少年群体中独立验证

### 不允许的变更
- 改变预期用途（从筛查到诊断）
- 改变风险等级
- 改变核心算法类型（从CNN到其他）
```

**Algorithm Change Protocol示例**:
```markdown
## 算法变更协议

### 变更触发条件
1. 性能监控发现准确率下降>5%
2. 收集到足够新数据（>10,000例）
3. 发现特定亚组性能不足
4. 用户反馈的系统性问题

### 变更流程
1. 变更提案
   - 描述问题和解决方案
   - 风险评估
   - 预期效果

2. 数据准备
   - 收集和标注新数据
   - 数据质量检查
   - 更新数据集文档

3. 模型开发
   - 在开发集上训练
   - 在验证集上调优
   - 记录所有实验

4. 验证测试
   - 在独立测试集上评估
   - 亚组分析
   - 与旧版本对比

5. 风险分析
   - 识别新风险
   - 评估风险可接受性
   - 更新风险管理文件

6. 内部审批
   - 算法团队审查
   - 质量团队审查
   - 监管团队审查

7. 部署
   - 灰度发布（10% → 50% → 100%）
   - 实时监控
   - 准备回滚方案

8. 上市后监控
   - 持续性能监控
   - 收集用户反馈
   - 定期向FDA报告

### 回滚标准
- 准确率下降>3%
- 严重不良事件报告
- 系统稳定性问题
```

## 风险分类

### IMDRF SaMD风险框架

**两个维度**:

**维度1: 医疗决策的重要性**
- **Treat**: 直接治疗或诊断
- **Drive**: 驱动临床管理
- **Inform**: 提供信息

**维度2: 健康状况的严重性**
- **Critical**: 危及生命或不可逆损伤
- **Serious**: 严重疾病或损伤
- **Non-serious**: 非严重状况

**风险矩阵**:
```
                Critical    Serious     Non-serious
Treat           IV          III         II
Drive           III         II          I
Inform          II          I           I

I = 低风险
II = 中低风险
III = 中高风险
IV = 高风险
```

**示例**:
```markdown
1. ICU患者脓毒症预警系统
   - 决策: Drive（驱动治疗决策）
   - 状况: Critical（危及生命）
   - 风险: III级（中高风险）
   - 监管: Class II (510k)

2. 糖尿病视网膜病变筛查
   - 决策: Drive（驱动转诊决策）
   - 状况: Serious（可能失明）
   - 风险: II级（中低风险）
   - 监管: Class II (510k)

3. 健康生活方式建议App
   - 决策: Inform（提供信息）
   - 状况: Non-serious
   - 风险: I级（低风险）
   - 监管: Class I或豁免
```

## 提交要求

### 510(k)申请内容

**1. 设备描述**:
```markdown
## 设备描述

### 产品名称
AI-ECG心律失常检测系统 v1.0

### 预期用途
本设备用于分析成人（18岁以上）的单导联心电图信号，
自动检测和分类常见心律失常，辅助医生诊断。

### 适应症
- 房颤检测
- 室性早搏检测
- 室性心动过速检测
- 正常窦性心律识别

### 使用环境
- 医院心电监护室
- 门诊心电检查室
- 由持证医生或护士操作

### 技术特征
- 算法类型: 1D卷积神经网络
- 输入: 10秒单导联ECG（250Hz采样）
- 输出: 4类心律概率分布
- 处理时间: <1秒
- 准确率: >95%（在验证集上）
```

**2. 实质等同性声明**:
```markdown
## 实质等同性对比

### 对比设备
Predicate Device: XYZ ECG Analysis System (K123456)

### 相同点
- 预期用途: 心律失常检测
- 技术原理: 基于软件的ECG分析
- 输入数据: 单导联ECG
- 使用环境: 医疗机构
- 用户: 医疗专业人员

### 不同点
| 特征 | 本设备 | 对比设备 | 影响 |
|------|--------|----------|------|
| 算法 | 深度学习 | 规则基础 | 提高准确性 |
| 处理速度 | <1秒 | 2-3秒 | 改善用户体验 |
| 心律类型 | 4类 | 3类 | 扩展功能 |

### 等同性结论
不同点不影响安全性和有效性，本设备实质等同于对比设备。
```

**3. 性能测试**:
```markdown
## 性能测试报告

### 测试数据集
- 来源: MIT-BIH心律失常数据库 + 内部收集
- 样本量: 10,000例（独立测试集）
- 分布:
  - 正常窦律: 5,000例
  - 房颤: 2,500例
  - 室早: 1,500例
  - 室速: 1,000例

### 性能指标
| 心律类型 | 敏感性 | 特异性 | PPV | NPV | F1分数 |
|---------|--------|--------|-----|-----|--------|
| 正常窦律 | 97.2% | 96.8% | 96.5% | 97.5% | 0.968 |
| 房颤 | 95.6% | 98.2% | 96.8% | 97.8% | 0.962 |
| 室早 | 93.8% | 97.5% | 94.2% | 97.3% | 0.940 |
| 室速 | 94.5% | 99.1% | 97.8% | 98.2% | 0.961 |
| **总体** | **95.3%** | **97.9%** | **96.3%** | **97.7%** | **0.958** |

### 亚组分析
- 年龄: 18-40岁、41-60岁、>60岁（性能无显著差异）
- 性别: 男性、女性（性能无显著差异）
- 信号质量: 高、中、低（低质量准确率下降5%）

### 与医生对比
- 3名心脏科医生独立诊断相同测试集
- AI准确率: 95.3%
- 医生平均准确率: 93.7%
- 结论: AI非劣效于医生（p=0.03）
```

**4. 软件文档**:
```markdown
## 软件文档清单

### Level of Concern: Moderate

### 提交文档
1. 软件描述文档（SDD）
   - 系统架构
   - 数据流图
   - 接口规格

2. 软件需求规格（SRS）
   - 功能需求
   - 性能需求
   - 安全需求

3. 风险分析
   - 危害识别
   - 风险评估
   - 风险控制措施

4. 验证和确认
   - 测试计划
   - 测试用例
   - 测试报告
   - 可追溯性矩阵

5. 版本控制
   - 版本历史
   - 变更日志
   - 配置管理

6. 网络安全
   - 威胁模型
   - 安全控制
   - 漏洞管理
```

**5. AI/ML特定文档**:
```markdown
## AI/ML透明度文档

### 训练数据
- 数据来源: 详见附录A
- 样本量: 100,000例
- 标注方法: 3名专家独立标注
- 数据质量: 一致性>95%
- 数据偏差分析: 详见附录B

### 算法开发
- 模型架构: ResNet-18变体
- 训练过程: 详见附录C
- 超参数: 详见附录D
- 交叉验证: 5折交叉验证

### 性能评估
- 独立测试集: 10,000例
- 评估指标: 敏感性、特异性、AUC
- 亚组分析: 年龄、性别、种族
- 失败案例分析: 详见附录E

### 可解释性
- 方法: Grad-CAM热力图
- 示例: 详见附录F
- 临床验证: 心脏科医生确认关注区域合理

### 限制和警告
- 仅适用于单导联ECG
- 信号质量要求: SNR>10dB
- 不适用于起搏器患者
- 不能替代医生诊断
```

## 上市后要求

### 1. 不良事件报告

**MDR（Medical Device Reporting）**:
```markdown
## 报告时限

### 立即报告（5个工作日）
- 导致死亡
- 严重伤害且需要立即纠正

### 30天报告
- 可能导致严重伤害或死亡的故障

### 年度报告
- 其他故障和投诉汇总
```

**AI/ML特定考虑**:
```python
class AdverseEventMonitoring:
    """
    AI/ML不良事件监控
    """
    def __init__(self):
        self.events = []
    
    def log_prediction_error(self, case_id, true_label, predicted_label, 
                            patient_outcome, severity):
        """
        记录预测错误
        """
        event = {
            'timestamp': datetime.now(),
            'case_id': case_id,
            'error_type': 'false_negative' if predicted_label == 0 else 'false_positive',
            'true_label': true_label,
            'predicted_label': predicted_label,
            'patient_outcome': patient_outcome,
            'severity': severity  # minor, moderate, serious, death
        }
        
        self.events.append(event)
        
        # 严重事件立即报告
        if severity in ['serious', 'death']:
            self.trigger_mdr_report(event)
    
    def analyze_patterns(self):
        """
        分析错误模式
        """
        # 是否有系统性问题？
        recent_errors = self.events[-100:]
        error_rate = len(recent_errors) / 100
        
        if error_rate > 0.10:  # 错误率>10%
            self.trigger_investigation()
```

### 2. 性能监控

**持续监控计划**:
```markdown
## 上市后监控计划

### 监控指标
1. 准确性指标
   - 总体准确率
   - 各类别敏感性/特异性
   - AUC

2. 使用指标
   - 日均使用量
   - 用户分布
   - 使用场景

3. 质量指标
   - 输入数据质量
   - 预测置信度分布
   - 低置信度预测比例

4. 安全指标
   - 假阴性率（漏诊）
   - 假阳性率（误诊）
   - 不良事件数量

### 监控频率
- 实时: 每次预测记录
- 日报: 使用量和质量指标
- 周报: 准确性指标
- 月报: 综合分析和趋势
- 季报: 向FDA报告

### 警报阈值
- 准确率下降>5%: 黄色警报
- 准确率下降>10%: 红色警报
- 严重不良事件: 立即警报

### 响应措施
- 黄色警报: 增加监控频率，分析原因
- 红色警报: 暂停使用，启动调查
- 立即警报: MDR报告，通知用户
```

## 最佳实践

### 1. 早期与FDA沟通

**Pre-Submission (Q-Submission)**:
```markdown
## Q-Submission建议

### 时机
- 开发早期（确定监管路径）
- 临床研究前（确认研究设计）
- 提交前（确认文档充分性）

### 内容
- 设备描述和预期用途
- 监管路径建议（510k vs PMA）
- 临床研究设计
- 性能评估方法
- 特殊考虑（AI/ML）

### 好处
- 减少审批风险
- 节省时间和成本
- 明确FDA期望
```

### 2. 建立质量体系

**QSR (Quality System Regulation) 21 CFR Part 820**:
- 设计控制
- 文档控制
- 变更控制
- CAPA（纠正和预防措施）

### 3. 保持文档更新

```python
# 自动化文档生成
class DocumentationSystem:
    def generate_algorithm_card(self, model):
        """
        生成算法卡片（类似Model Card）
        """
        card = {
            'model_details': {
                'version': model.version,
                'date': model.training_date,
                'architecture': model.architecture,
                'parameters': model.num_parameters
            },
            'intended_use': {
                'primary_use': model.intended_use,
                'out_of_scope': model.out_of_scope_uses
            },
            'training_data': {
                'source': model.data_source,
                'size': model.training_size,
                'demographics': model.data_demographics
            },
            'performance': {
                'metrics': model.performance_metrics,
                'subgroup_analysis': model.subgroup_performance
            },
            'limitations': model.known_limitations,
            'ethical_considerations': model.ethical_considerations
        }
        return card
```

## 下一步

- 学习[算法验证方法](algorithm-validation.md)
- 了解[持续学习系统](continuous-learning.md)监管
- 查看[案例研究](../../case-studies/ai-ecg-monitor.md)

---

**相关主题**:
- [AI/ML监管概述](index.md)
- [算法验证方法](algorithm-validation.md)
- [IEC 62304标准](../iec-62304/index.md)
