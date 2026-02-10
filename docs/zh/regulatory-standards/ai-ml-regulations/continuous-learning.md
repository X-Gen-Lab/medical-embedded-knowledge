# 持续学习系统

## 概述

持续学习（Continuous Learning）或自适应AI系统能够在部署后从新数据中学习和更新。这为医疗器械带来了巨大潜力，但也带来了独特的监管挑战。本文档介绍持续学习系统的类型、监管考虑和实施策略。

## 什么是持续学习？

### 传统AI vs 持续学习AI

**传统（锁定）AI**:
```
训练 → 验证 → 锁定 → 部署 → 不变
```

**持续学习AI**:
```
训练 → 验证 → 部署 → 收集数据 → 重新训练 → 更新 → 循环
```

### 为什么需要持续学习？

**1. 数据漂移（Data Drift）**:
```python
# 示例：患者人群变化
训练数据（2020年）:
- 平均年龄: 55岁
- 男性: 60%
- 疾病分布: A型70%, B型30%

实际使用（2024年）:
- 平均年龄: 62岁（老龄化）
- 男性: 55%（性别比例变化）
- 疾病分布: A型60%, B型40%（流行病学变化）

结果: 模型性能下降
```

**2. 概念漂移（Concept Drift）**:
```
疾病定义变化:
- 诊断标准更新
- 新的疾病亚型发现
- 治疗指南改变

设备变化:
- 新型号传感器
- 不同厂商设备
- 技术升级
```

**3. 性能改进**:
- 收集更多数据
- 发现新模式
- 修正错误

## 持续学习的类型

### 1. 离线更新（Offline Update）

**特点**:
- 定期批量更新
- 在受控环境中重新训练
- 更新前完整验证

**流程**:
```python
class OfflineUpdateSystem:
    """
    离线更新系统
    """
    def __init__(self, update_frequency='quarterly'):
        self.update_frequency = update_frequency
        self.data_buffer = []
        self.current_model_version = "1.0.0"
    
    def collect_data(self, input_data, prediction, ground_truth=None):
        """
        收集新数据
        """
        record = {
            'timestamp': datetime.now(),
            'input': input_data,
            'prediction': prediction,
            'ground_truth': ground_truth,
            'model_version': self.current_model_version
        }
        self.data_buffer.append(record)
    
    def trigger_update(self):
        """
        触发更新流程
        """
        # 1. 数据准备
        new_data = self.prepare_training_data(self.data_buffer)
        
        # 2. 数据质量检查
        if not self.validate_data_quality(new_data):
            raise ValueError("数据质量不合格")
        
        # 3. 重新训练
        new_model = self.retrain_model(new_data)
        
        # 4. 验证新模型
        validation_results = self.validate_model(new_model)
        
        # 5. 性能对比
        if validation_results['accuracy'] < self.current_model_performance:
            raise ValueError("新模型性能下降")
        
        # 6. 风险评估
        risk_assessment = self.assess_risks(new_model)
        if not risk_assessment['acceptable']:
            raise ValueError("风险不可接受")
        
        # 7. 批准流程
        approval = self.get_approval(new_model, validation_results, risk_assessment)
        if not approval:
            raise ValueError("未获批准")
        
        # 8. 部署
        self.deploy_model(new_model)
        self.current_model_version = self.increment_version()
        
        # 9. 清空缓冲区
        self.data_buffer = []
    
    def retrain_model(self, new_data):
        """
        重新训练模型
        """
        # 合并历史数据和新数据
        combined_data = self.combine_datasets(self.historical_data, new_data)
        
        # 训练
        model = create_model()
        model.fit(combined_data['X'], combined_data['y'], epochs=50)
        
        return model
```

**优点**:
- 完全控制更新过程
- 充分验证
- 符合传统监管框架

**缺点**:
- 更新频率低
- 无法快速响应变化
- 需要人工干预

### 2. 在线学习（Online Learning）

**特点**:
- 实时或近实时更新
- 增量学习
- 自动化程度高

**流程**:
```python
class OnlineLearningSystem:
    """
    在线学习系统
    """
    def __init__(self, learning_rate=0.001, update_threshold=100):
        self.model = load_model()
        self.learning_rate = learning_rate
        self.update_threshold = update_threshold
        self.samples_since_update = 0
        self.performance_monitor = PerformanceMonitor()
    
    def predict_and_learn(self, input_data, ground_truth=None):
        """
        预测并学习
        """
        # 1. 预测
        prediction = self.model.predict(input_data)
        
        # 2. 如果有标签，进行增量学习
        if ground_truth is not None:
            self.incremental_update(input_data, ground_truth)
            self.samples_since_update += 1
        
        # 3. 定期验证
        if self.samples_since_update >= self.update_threshold:
            self.validate_and_checkpoint()
            self.samples_since_update = 0
        
        return prediction
    
    def incremental_update(self, input_data, ground_truth):
        """
        增量更新
        """
        # 计算损失
        with tf.GradientTape() as tape:
            prediction = self.model(input_data, training=True)
            loss = self.loss_function(ground_truth, prediction)
        
        # 计算梯度
        gradients = tape.gradient(loss, self.model.trainable_variables)
        
        # 应用梯度（小学习率）
        self.optimizer.apply_gradients(
            zip(gradients, self.model.trainable_variables)
        )
        
        # 监控性能
        self.performance_monitor.log(ground_truth, prediction)
    
    def validate_and_checkpoint(self):
        """
        验证并保存检查点
        """
        # 在验证集上评估
        val_performance = self.evaluate_on_validation_set()
        
        # 检查性能
        if val_performance < self.performance_threshold:
            # 性能下降，回滚到上一个检查点
            self.rollback_to_checkpoint()
            self.trigger_alert("性能下降，已回滚")
        else:
            # 性能良好，保存检查点
            self.save_checkpoint()
```

**优点**:
- 快速适应变化
- 自动化
- 持续改进

**缺点**:
- 监管挑战大
- 风险控制难
- 可能不稳定

### 3. 混合方法

**特点**:
- 结合离线和在线学习
- 在线微调 + 定期重训练

**流程**:
```python
class HybridLearningSystem:
    """
    混合学习系统
    """
    def __init__(self):
        self.base_model = load_base_model()  # 离线训练的基础模型
        self.adaptation_layer = create_adaptation_layer()  # 在线学习层
        self.data_buffer = []
    
    def predict(self, input_data):
        """
        预测
        """
        # 基础模型提取特征
        features = self.base_model.extract_features(input_data)
        
        # 自适应层进行预测
        prediction = self.adaptation_layer(features)
        
        return prediction
    
    def online_adapt(self, input_data, ground_truth):
        """
        在线自适应（仅更新自适应层）
        """
        features = self.base_model.extract_features(input_data)
        
        # 仅更新自适应层
        self.adaptation_layer.fit(features, ground_truth, epochs=1)
        
        # 收集数据用于离线更新
        self.data_buffer.append((input_data, ground_truth))
    
    def offline_retrain(self):
        """
        离线重训练（更新基础模型）
        """
        if len(self.data_buffer) >= 10000:
            # 重新训练基础模型
            new_base_model = retrain_base_model(self.data_buffer)
            
            # 验证
            if validate_model(new_base_model):
                self.base_model = new_base_model
                self.adaptation_layer = create_adaptation_layer()  # 重置
                self.data_buffer = []
```

## 监管考虑

### 1. FDA预定变更控制计划（PCCP）

**PCCP for持续学习**:
```markdown
## 预定变更控制计划

### 1. SaMD Pre-Specifications（变更规格）

#### 性能边界
- 最低准确率: 90%
- 最低敏感性: 88%
- 最低特异性: 92%
- 如果低于阈值，自动回滚

#### 数据要求
- 每次更新最少新数据: 1,000例
- 数据质量标准: SNR>10dB, 标注一致性>95%
- 数据分布: 各类别至少100例

#### 更新频率
- 最频繁: 每月一次
- 触发条件:
  - 收集足够新数据
  - 性能下降>5%
  - 发现系统性问题

#### 不允许的变更
- 改变预期用途
- 改变核心算法架构
- 改变输入/输出格式
- 扩展到新的患者群体

### 2. Algorithm Change Protocol（变更协议）

#### 数据收集
- 自动收集预测结果
- 定期收集金标准标签
- 数据去标识化
- 安全存储

#### 模型更新
- 增量学习或重新训练
- 在开发集上训练
- 在验证集上调优
- 在测试集上评估

#### 验证测试
- 独立测试集（固定）
- 性能指标计算
- 亚组分析
- 与基线对比

#### 风险评估
- 识别新风险
- 评估风险可接受性
- 更新风险管理文件
- 如果风险不可接受，不部署

#### 自动化决策
- 如果满足所有标准，自动部署
- 否则，人工审查
- 记录所有决策

#### 监控
- 部署后持续监控
- 实时性能跟踪
- 异常检测
- 自动回滚机制

#### 报告
- 每次更新向FDA报告
- 季度性能报告
- 年度总结报告
```

### 2. 欧盟MDR考虑

**持续学习作为重大变更**:
```markdown
## MDR Article 120: 重大变更

持续学习可能构成重大变更，如果:
- 改变预期用途或性能
- 影响安全性或有效性
- 改变风险/收益比

### 应对策略
1. 在技术文档中描述持续学习机制
2. 定义变更边界
3. 建立变更管理流程
4. 上市后监督计划包含持续学习监控
5. 定期向公告机构报告
```

## 实施最佳实践

### 1. 性能监控

**实时监控系统**:
```python
class ContinuousMonitoring:
    """
    持续监控系统
    """
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            'accuracy': 0.90,
            'sensitivity': 0.88,
            'specificity': 0.92
        }
    
    def monitor_prediction(self, prediction, ground_truth=None):
        """
        监控单次预测
        """
        record = {
            'timestamp': datetime.now(),
            'prediction': prediction,
            'confidence': np.max(prediction),
            'ground_truth': ground_truth
        }
        
        # 检查置信度
        if record['confidence'] < 0.6:
            self.log_warning("低置信度预测", record)
        
        # 如果有标签，计算准确性
        if ground_truth is not None:
            is_correct = (np.argmax(prediction) == ground_truth)
            record['correct'] = is_correct
            
            # 更新滑动窗口统计
            self.update_rolling_metrics(is_correct)
    
    def update_rolling_metrics(self, is_correct):
        """
        更新滑动窗口指标
        """
        self.metrics_history.append(is_correct)
        
        # 保持最近1000个预测
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)
        
        # 计算当前性能
        current_accuracy = np.mean(self.metrics_history)
        
        # 检查是否低于阈值
        if current_accuracy < self.alert_thresholds['accuracy']:
            self.trigger_alert("准确率下降", current_accuracy)
    
    def detect_drift(self):
        """
        检测数据漂移
        """
        # 比较最近和历史分布
        recent_data = self.get_recent_data(n=1000)
        historical_data = self.get_historical_data()
        
        # KS检验
        from scipy.stats import ks_2samp
        statistic, p_value = ks_2samp(recent_data, historical_data)
        
        if p_value < 0.05:
            self.trigger_alert("检测到数据漂移", p_value)
            return True
        return False
```

### 2. 自动回滚机制

```python
class AutoRollback:
    """
    自动回滚系统
    """
    def __init__(self):
        self.model_checkpoints = []
        self.performance_history = []
    
    def deploy_new_version(self, new_model):
        """
        部署新版本
        """
        # 保存当前模型作为检查点
        checkpoint = {
            'model': self.current_model,
            'version': self.current_version,
            'performance': self.current_performance,
            'timestamp': datetime.now()
        }
        self.model_checkpoints.append(checkpoint)
        
        # 部署新模型
        self.current_model = new_model
        self.current_version = self.increment_version()
        
        # 开始监控
        self.start_monitoring()
    
    def check_rollback_conditions(self):
        """
        检查是否需要回滚
        """
        # 条件1: 性能下降
        if self.current_performance < self.rollback_threshold:
            self.rollback("性能下降")
            return True
        
        # 条件2: 错误率激增
        if self.error_rate > self.max_error_rate:
            self.rollback("错误率过高")
            return True
        
        # 条件3: 系统不稳定
        if self.is_unstable():
            self.rollback("系统不稳定")
            return True
        
        return False
    
    def rollback(self, reason):
        """
        回滚到上一个版本
        """
        if not self.model_checkpoints:
            raise ValueError("没有可回滚的检查点")
        
        # 恢复上一个检查点
        last_checkpoint = self.model_checkpoints[-1]
        self.current_model = last_checkpoint['model']
        self.current_version = last_checkpoint['version']
        
        # 记录回滚事件
        self.log_rollback(reason, last_checkpoint)
        
        # 通知相关人员
        self.notify_stakeholders(reason)
```

### 3. 数据管理

```python
class DataManagement:
    """
    持续学习数据管理
    """
    def __init__(self):
        self.data_buffer = []
        self.data_quality_checker = DataQualityChecker()
    
    def collect_data(self, input_data, prediction, ground_truth=None):
        """
        收集数据
        """
        # 数据质量检查
        quality_score = self.data_quality_checker.assess(input_data)
        
        if quality_score < 0.7:
            return  # 丢弃低质量数据
        
        # 去标识化
        anonymized_data = self.anonymize(input_data)
        
        # 存储
        record = {
            'data': anonymized_data,
            'prediction': prediction,
            'ground_truth': ground_truth,
            'quality_score': quality_score,
            'timestamp': datetime.now(),
            'model_version': self.current_version
        }
        
        self.data_buffer.append(record)
        
        # 定期归档
        if len(self.data_buffer) >= 10000:
            self.archive_data()
    
    def prepare_training_data(self):
        """
        准备训练数据
        """
        # 过滤有标签的数据
        labeled_data = [r for r in self.data_buffer if r['ground_truth'] is not None]
        
        # 平衡数据集
        balanced_data = self.balance_dataset(labeled_data)
        
        # 数据增强
        augmented_data = self.augment_data(balanced_data)
        
        return augmented_data
    
    def balance_dataset(self, data):
        """
        平衡数据集
        """
        from collections import Counter
        
        # 统计各类别数量
        labels = [r['ground_truth'] for r in data]
        class_counts = Counter(labels)
        
        # 找到最少的类别
        min_count = min(class_counts.values())
        
        # 欠采样到相同数量
        balanced_data = []
        for class_label in class_counts.keys():
            class_data = [r for r in data if r['ground_truth'] == class_label]
            sampled = random.sample(class_data, min_count)
            balanced_data.extend(sampled)
        
        return balanced_data
```

## 挑战和解决方案

### 1. 灾难性遗忘

**问题**: 学习新数据时忘记旧知识

**解决方案**:
```python
# 1. 经验回放（Experience Replay）
class ExperienceReplay:
    def __init__(self, buffer_size=10000):
        self.buffer = []
        self.buffer_size = buffer_size
    
    def add(self, data, label):
        self.buffer.append((data, label))
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)
    
    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)
    
    def train_with_replay(self, new_data, new_labels):
        # 混合新数据和历史数据
        replay_data = self.sample(len(new_data) // 2)
        combined_data = new_data + [d[0] for d in replay_data]
        combined_labels = new_labels + [d[1] for d in replay_data]
        
        # 训练
        model.fit(combined_data, combined_labels)

# 2. 弹性权重巩固（Elastic Weight Consolidation）
class EWC:
    def __init__(self, model, lambda_=1000):
        self.model = model
        self.lambda_ = lambda_
        self.fisher_matrix = self.compute_fisher()
        self.optimal_params = model.get_weights()
    
    def compute_fisher(self):
        # 计算Fisher信息矩阵
        # 衡量参数对旧任务的重要性
        pass
    
    def ewc_loss(self, current_loss):
        # 添加正则化项，惩罚重要参数的变化
        ewc_penalty = 0
        current_params = self.model.get_weights()
        
        for i, (curr, opt) in enumerate(zip(current_params, self.optimal_params)):
            ewc_penalty += tf.reduce_sum(
                self.fisher_matrix[i] * (curr - opt) ** 2
            )
        
        return current_loss + (self.lambda_ / 2) * ewc_penalty
```

### 2. 标签获取

**问题**: 实时获取金标准标签困难

**解决方案**:
```python
# 1. 主动学习（Active Learning）
class ActiveLearning:
    def select_samples_for_labeling(self, unlabeled_data, n=100):
        """
        选择最有价值的样本进行标注
        """
        # 不确定性采样
        predictions = model.predict(unlabeled_data)
        uncertainties = 1 - np.max(predictions, axis=1)
        
        # 选择最不确定的样本
        top_indices = np.argsort(uncertainties)[-n:]
        
        return unlabeled_data[top_indices]

# 2. 半监督学习
class SemiSupervisedLearning:
    def train_with_unlabeled(self, labeled_data, unlabeled_data):
        """
        利用无标签数据
        """
        # 伪标签（Pseudo-labeling）
        pseudo_labels = model.predict(unlabeled_data)
        confident_mask = np.max(pseudo_labels, axis=1) > 0.9
        
        # 使用高置信度预测作为伪标签
        pseudo_labeled_data = unlabeled_data[confident_mask]
        pseudo_labels = pseudo_labels[confident_mask]
        
        # 混合训练
        combined_data = np.concatenate([labeled_data, pseudo_labeled_data])
        combined_labels = np.concatenate([true_labels, pseudo_labels])
        
        model.fit(combined_data, combined_labels)
```

## 文档要求

### 持续学习计划文档

```markdown
# 持续学习计划

## 1. 概述
- 产品: AI-ECG心律失常检测系统
- 版本: 1.0.0
- 持续学习类型: 混合（在线微调 + 定期重训练）

## 2. 学习策略

### 2.1 在线学习
- 频率: 实时
- 范围: 仅自适应层
- 学习率: 0.0001
- 批量大小: 32

### 2.2 离线更新
- 频率: 季度
- 范围: 完整模型
- 触发条件:
  - 收集>10,000新样本
  - 性能下降>5%
  - 发现系统性问题

## 3. 数据管理
- 收集: 自动收集所有预测
- 标注: 定期从临床系统获取诊断结果
- 质量控制: SNR>10dB, 专家审核
- 存储: 加密存储，保留5年

## 4. 验证流程
- 独立测试集: 固定10,000例
- 性能阈值: 准确率>90%, 敏感性>88%
- 亚组分析: 年龄、性别、种族
- 对比基线: 与初始版本对比

## 5. 风险管理
- 风险识别: 每次更新前
- 风险评估: 使用ISO 14971框架
- 风险控制: 自动回滚、人工审查
- 残余风险: 文档化并监控

## 6. 监控和报警
- 实时监控: 准确率、置信度、错误率
- 警报阈值: 准确率<90%, 错误率>10%
- 响应措施: 自动回滚、通知团队
- 报告: 每次更新向FDA报告

## 7. 回滚机制
- 触发条件: 性能下降、错误激增、系统不稳定
- 回滚流程: 自动恢复上一版本
- 通知: 立即通知相关方
- 调查: 根本原因分析

## 8. 文档和可追溯性
- 版本控制: Git + 模型注册表
- 变更日志: 每次更新记录
- 审计追踪: 所有决策可追溯
- 定期审查: 季度质量审查
```

## 下一步

- 回顾[AI/ML监管概述](index.md)
- 学习[算法验证方法](algorithm-validation.md)
- 查看[FDA SaMD指南](fda-samd-guidance.md)

---

**相关主题**:
- [AI/ML监管概述](index.md)
- [FDA SaMD指南](fda-samd-guidance.md)
- [算法验证方法](algorithm-validation.md)
