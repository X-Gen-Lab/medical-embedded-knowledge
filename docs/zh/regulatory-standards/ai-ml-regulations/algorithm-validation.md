# 算法验证方法

## 概述

算法验证是确保AI/ML医疗器械安全有效的关键步骤。本文档介绍验证和确认（V&V）的方法、最佳实践和监管要求。

## 验证 vs 确认

### 定义

**验证（Verification）**: "我们是否正确地构建了产品？"
- 软件是否符合规格要求？
- 代码是否正确实现了设计？
- 单元测试、集成测试

**确认（Validation）**: "我们是否构建了正确的产品？"
- 软件是否满足用户需求？
- 是否达到预期的临床效果？
- 临床验证、用户测试

### 医疗器械中的应用

```
需求 → 设计 → 实现 → 验证 → 确认
  ↑                              ↓
  └──────────── 反馈 ────────────┘
```

## 验证方法

### 1. 单元测试

**测试模型组件**:
```python
import pytest
import numpy as np

class TestECGPreprocessing:
    """
    测试ECG预处理模块
    """
    def test_bandpass_filter(self):
        """测试带通滤波器"""
        # 生成测试信号
        fs = 250  # 采样率
        t = np.linspace(0, 10, fs * 10)
        signal = np.sin(2 * np.pi * 1 * t)  # 1Hz正弦波
        
        # 应用滤波器（0.5-40Hz）
        filtered = bandpass_filter(signal, lowcut=0.5, highcut=40, fs=fs)
        
        # 验证
        assert len(filtered) == len(signal), "输出长度应与输入相同"
        assert not np.any(np.isnan(filtered)), "不应包含NaN"
        assert not np.any(np.isinf(filtered)), "不应包含Inf"
    
    def test_normalize(self):
        """测试归一化"""
        signal = np.array([1, 2, 3, 4, 5])
        normalized = normalize(signal)
        
        assert np.isclose(np.mean(normalized), 0, atol=1e-6), "均值应为0"
        assert np.isclose(np.std(normalized), 1, atol=1e-6), "标准差应为1"
    
    def test_r_peak_detection(self):
        """测试R峰检测"""
        # 加载标准测试信号
        signal, true_peaks = load_test_ecg()
        
        # 检测R峰
        detected_peaks = detect_r_peaks(signal)
        
        # 计算检测率
        tp, fp, fn = compare_peaks(detected_peaks, true_peaks, tolerance=10)
        sensitivity = tp / (tp + fn)
        ppv = tp / (tp + fp)
        
        assert sensitivity > 0.95, f"敏感性{sensitivity:.2%}低于95%"
        assert ppv > 0.95, f"PPV {ppv:.2%}低于95%"

class TestModelInference:
    """
    测试模型推理
    """
    def test_model_output_shape(self):
        """测试输出形状"""
        model = load_model()
        input_data = np.random.randn(1, 5000, 1)
        output = model.predict(input_data)
        
        assert output.shape == (1, 5), "输出应为(batch_size, num_classes)"
    
    def test_model_output_range(self):
        """测试输出范围"""
        model = load_model()
        input_data = np.random.randn(10, 5000, 1)
        output = model.predict(input_data)
        
        assert np.all(output >= 0) and np.all(output <= 1), "输出应在[0,1]"
        assert np.allclose(np.sum(output, axis=1), 1.0), "概率和应为1"
    
    def test_model_determinism(self):
        """测试确定性"""
        model = load_model()
        input_data = np.random.randn(1, 5000, 1)
        
        output1 = model.predict(input_data)
        output2 = model.predict(input_data)
        
        assert np.allclose(output1, output2), "相同输入应产生相同输出"
    
    def test_model_robustness(self):
        """测试鲁棒性"""
        model = load_model()
        input_data = np.random.randn(1, 5000, 1)
        
        # 添加小噪声
        noise = np.random.randn(*input_data.shape) * 0.01
        noisy_input = input_data + noise
        
        output_clean = model.predict(input_data)
        output_noisy = model.predict(noisy_input)
        
        # 预测应该相似
        diff = np.abs(output_clean - output_noisy)
        assert np.max(diff) < 0.1, "小噪声不应显著改变预测"
```

### 2. 集成测试

**测试完整流程**:
```python
class TestEndToEndPipeline:
    """
    端到端测试
    """
    def test_complete_workflow(self):
        """测试完整工作流"""
        # 1. 加载原始数据
        raw_ecg = load_raw_ecg("test_data/patient_001.dat")
        
        # 2. 预处理
        preprocessed = preprocess_pipeline(raw_ecg)
        assert preprocessed.shape == (5000, 1), "预处理后形状错误"
        
        # 3. 模型推理
        prediction = model.predict(preprocessed[np.newaxis, ...])
        assert prediction.shape == (1, 5), "预测形状错误"
        
        # 4. 后处理
        result = postprocess_prediction(prediction)
        assert 'class' in result, "结果应包含类别"
        assert 'confidence' in result, "结果应包含置信度"
        assert result['class'] in [0, 1, 2, 3, 4], "类别应在有效范围"
        assert 0 <= result['confidence'] <= 1, "置信度应在[0,1]"
    
    def test_batch_processing(self):
        """测试批量处理"""
        # 加载多个样本
        ecg_files = glob.glob("test_data/*.dat")
        
        results = []
        for ecg_file in ecg_files:
            raw_ecg = load_raw_ecg(ecg_file)
            preprocessed = preprocess_pipeline(raw_ecg)
            prediction = model.predict(preprocessed[np.newaxis, ...])
            result = postprocess_prediction(prediction)
            results.append(result)
        
        assert len(results) == len(ecg_files), "应处理所有文件"
        assert all('class' in r for r in results), "所有结果应包含类别"
    
    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效输入
        with pytest.raises(ValueError):
            preprocess_pipeline(np.array([]))  # 空数组
        
        with pytest.raises(ValueError):
            preprocess_pipeline(np.random.randn(100, 1))  # 太短
        
        # 测试低质量信号
        noisy_signal = np.random.randn(5000, 1) * 100
        result = process_with_quality_check(noisy_signal)
        assert result['quality'] == 'poor', "应检测到低质量"
        assert result['warning'] is not None, "应有警告信息"
```

### 3. 性能测试

**测试计算性能**:
```python
import time

class TestPerformance:
    """
    性能测试
    """
    def test_inference_time(self):
        """测试推理时间"""
        model = load_model()
        input_data = np.random.randn(1, 5000, 1)
        
        # 预热
        for _ in range(10):
            model.predict(input_data)
        
        # 测试
        times = []
        for _ in range(100):
            start = time.time()
            model.predict(input_data)
            end = time.time()
            times.append(end - start)
        
        avg_time = np.mean(times)
        max_time = np.max(times)
        
        assert avg_time < 0.1, f"平均推理时间{avg_time:.3f}s超过100ms"
        assert max_time < 0.2, f"最大推理时间{max_time:.3f}s超过200ms"
    
    def test_memory_usage(self):
        """测试内存使用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # 初始内存
        mem_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # 加载模型
        model = load_model()
        
        # 运行推理
        for _ in range(100):
            input_data = np.random.randn(1, 5000, 1)
            model.predict(input_data)
        
        # 最终内存
        mem_after = process.memory_info().rss / 1024 / 1024  # MB
        mem_increase = mem_after - mem_before
        
        assert mem_increase < 100, f"内存增加{mem_increase:.1f}MB超过100MB"
    
    def test_throughput(self):
        """测试吞吐量"""
        model = load_model()
        num_samples = 1000
        
        start = time.time()
        for _ in range(num_samples):
            input_data = np.random.randn(1, 5000, 1)
            model.predict(input_data)
        end = time.time()
        
        throughput = num_samples / (end - start)
        assert throughput > 10, f"吞吐量{throughput:.1f}样本/秒低于10"
```

## 确认方法

### 1. 数据集验证

**独立测试集**:
```python
def validate_on_test_set():
    """
    在独立测试集上验证
    """
    # 加载测试数据
    X_test, y_test = load_test_dataset()
    
    # 确保测试集独立
    assert not data_leakage_check(X_test, X_train), "测试集泄露！"
    
    # 预测
    y_pred = model.predict(X_test)
    y_pred_class = np.argmax(y_pred, axis=1)
    
    # 计算指标
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, 
        f1_score, confusion_matrix, classification_report
    )
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred_class),
        'precision': precision_score(y_test, y_pred_class, average='weighted'),
        'recall': recall_score(y_test, y_pred_class, average='weighted'),
        'f1': f1_score(y_test, y_pred_class, average='weighted')
    }
    
    # 混淆矩阵
    cm = confusion_matrix(y_test, y_pred_class)
    
    # 分类报告
    report = classification_report(y_test, y_pred_class, 
                                   target_names=['Normal', 'AFib', 'PVC', 'VT', 'VF'])
    
    return metrics, cm, report
```

**交叉验证**:
```python
from sklearn.model_selection import StratifiedKFold

def cross_validation(X, y, n_folds=5):
    """
    K折交叉验证
    """
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    
    fold_metrics = []
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        print(f"Fold {fold + 1}/{n_folds}")
        
        # 划分数据
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        # 训练模型
        model = create_model()
        model.fit(X_train, y_train, epochs=50, verbose=0)
        
        # 评估
        y_pred = model.predict(X_val)
        y_pred_class = np.argmax(y_pred, axis=1)
        
        metrics = {
            'accuracy': accuracy_score(y_val, y_pred_class),
            'precision': precision_score(y_val, y_pred_class, average='weighted'),
            'recall': recall_score(y_val, y_pred_class, average='weighted')
        }
        
        fold_metrics.append(metrics)
    
    # 汇总结果
    avg_metrics = {
        metric: np.mean([fold[metric] for fold in fold_metrics])
        for metric in fold_metrics[0].keys()
    }
    
    std_metrics = {
        metric: np.std([fold[metric] for fold in fold_metrics])
        for metric in fold_metrics[0].keys()
    }
    
    return avg_metrics, std_metrics
```

### 2. 亚组分析

**人口统计学亚组**:
```python
def subgroup_analysis(X_test, y_test, demographics):
    """
    亚组性能分析
    """
    results = {}
    
    # 年龄组
    age_groups = {
        '18-40': (demographics['age'] >= 18) & (demographics['age'] < 40),
        '40-60': (demographics['age'] >= 40) & (demographics['age'] < 60),
        '60+': demographics['age'] >= 60
    }
    
    for group_name, mask in age_groups.items():
        X_group = X_test[mask]
        y_group = y_test[mask]
        
        y_pred = model.predict(X_group)
        y_pred_class = np.argmax(y_pred, axis=1)
        
        results[f'age_{group_name}'] = {
            'n': len(y_group),
            'accuracy': accuracy_score(y_group, y_pred_class),
            'sensitivity': recall_score(y_group, y_pred_class, average='weighted'),
            'specificity': calculate_specificity(y_group, y_pred_class)
        }
    
    # 性别
    for gender in ['male', 'female']:
        mask = demographics['gender'] == gender
        X_group = X_test[mask]
        y_group = y_test[mask]
        
        y_pred = model.predict(X_group)
        y_pred_class = np.argmax(y_pred, axis=1)
        
        results[f'gender_{gender}'] = {
            'n': len(y_group),
            'accuracy': accuracy_score(y_group, y_pred_class)
        }
    
    # 种族
    for race in demographics['race'].unique():
        mask = demographics['race'] == race
        X_group = X_test[mask]
        y_group = y_test[mask]
        
        if len(y_group) > 30:  # 足够样本量
            y_pred = model.predict(X_group)
            y_pred_class = np.argmax(y_pred, axis=1)
            
            results[f'race_{race}'] = {
                'n': len(y_group),
                'accuracy': accuracy_score(y_group, y_pred_class)
            }
    
    return results
```

### 3. 临床验证

**与医生对比**:
```python
def clinical_validation_study():
    """
    临床验证研究
    """
    # 加载临床测试集
    test_cases = load_clinical_test_set(n=500)
    
    # 专家标注
    expert1_labels = get_expert_annotations(test_cases, expert_id=1)
    expert2_labels = get_expert_annotations(test_cases, expert_id=2)
    expert3_labels = get_expert_annotations(test_cases, expert_id=3)
    
    # 专家一致性
    inter_rater_agreement = calculate_cohens_kappa([
        expert1_labels, expert2_labels, expert3_labels
    ])
    print(f"专家间一致性 (Kappa): {inter_rater_agreement:.3f}")
    
    # 金标准（多数投票或仲裁）
    gold_standard = majority_vote([expert1_labels, expert2_labels, expert3_labels])
    
    # AI预测
    ai_predictions = model.predict(test_cases)
    ai_labels = np.argmax(ai_predictions, axis=1)
    
    # 性能对比
    results = {
        'AI': {
            'accuracy': accuracy_score(gold_standard, ai_labels),
            'sensitivity': recall_score(gold_standard, ai_labels, average='weighted'),
            'specificity': calculate_specificity(gold_standard, ai_labels)
        },
        'Expert1': {
            'accuracy': accuracy_score(gold_standard, expert1_labels),
            'sensitivity': recall_score(gold_standard, expert1_labels, average='weighted')
        },
        'Expert2': {
            'accuracy': accuracy_score(gold_standard, expert2_labels),
            'sensitivity': recall_score(gold_standard, expert2_labels, average='weighted')
        },
        'Expert3': {
            'accuracy': accuracy_score(gold_standard, expert3_labels),
            'sensitivity': recall_score(gold_standard, expert3_labels, average='weighted')
        }
    }
    
    # 统计检验（非劣效性）
    from statsmodels.stats.proportion import proportions_ztest
    
    ai_correct = np.sum(ai_labels == gold_standard)
    expert_avg_correct = np.mean([
        np.sum(expert1_labels == gold_standard),
        np.sum(expert2_labels == gold_standard),
        np.sum(expert3_labels == gold_standard)
    ])
    
    z_stat, p_value = proportions_ztest(
        [ai_correct, expert_avg_correct],
        [len(gold_standard), len(gold_standard)]
    )
    
    results['statistical_test'] = {
        'z_statistic': z_stat,
        'p_value': p_value,
        'non_inferior': p_value < 0.05 and ai_correct >= expert_avg_correct
    }
    
    return results
```

## 特殊验证场景

### 1. 边界情况测试

```python
def test_edge_cases():
    """
    测试边界情况
    """
    test_cases = {
        'all_zeros': np.zeros((1, 5000, 1)),
        'all_ones': np.ones((1, 5000, 1)),
        'very_large': np.ones((1, 5000, 1)) * 1e6,
        'very_small': np.ones((1, 5000, 1)) * 1e-6,
        'nan_values': np.full((1, 5000, 1), np.nan),
        'inf_values': np.full((1, 5000, 1), np.inf)
    }
    
    for case_name, input_data in test_cases.items():
        try:
            result = safe_predict(input_data)
            print(f"{case_name}: {result}")
        except Exception as e:
            print(f"{case_name}: 错误 - {e}")

def safe_predict(input_data):
    """
    安全预测（带错误处理）
    """
    # 输入验证
    if np.any(np.isnan(input_data)):
        return {'error': 'Input contains NaN'}
    if np.any(np.isinf(input_data)):
        return {'error': 'Input contains Inf'}
    if np.all(input_data == 0):
        return {'error': 'Input is all zeros'}
    
    # 预测
    prediction = model.predict(input_data)
    
    return {
        'class': np.argmax(prediction),
        'confidence': np.max(prediction)
    }
```

### 2. 对抗样本测试

```python
def adversarial_robustness_test():
    """
    对抗鲁棒性测试
    """
    from art.attacks.evasion import FastGradientMethod
    from art.estimators.classification import KerasClassifier
    
    # 包装模型
    classifier = KerasClassifier(model=model, clip_values=(0, 1))
    
    # 创建对抗攻击
    attack = FastGradientMethod(estimator=classifier, eps=0.1)
    
    # 生成对抗样本
    X_test, y_test = load_test_dataset()
    X_adv = attack.generate(x=X_test)
    
    # 评估
    y_pred_clean = model.predict(X_test)
    y_pred_adv = model.predict(X_adv)
    
    acc_clean = accuracy_score(y_test, np.argmax(y_pred_clean, axis=1))
    acc_adv = accuracy_score(y_test, np.argmax(y_pred_adv, axis=1))
    
    print(f"Clean accuracy: {acc_clean:.2%}")
    print(f"Adversarial accuracy: {acc_adv:.2%}")
    print(f"Robustness: {acc_adv/acc_clean:.2%}")
```

## 验证文档

### 验证报告模板

```markdown
# 算法验证报告

## 1. 概述
- 产品名称: AI-ECG心律失常检测系统
- 版本: 1.0.0
- 验证日期: 2024-01-15
- 验证负责人: 张三

## 2. 验证目标
验证AI-ECG系统能够准确检测和分类心律失常，满足设计规格要求。

## 3. 验证方法

### 3.1 单元测试
- 测试用例数: 150
- 通过率: 100%
- 详见: 附录A

### 3.2 集成测试
- 测试场景数: 50
- 通过率: 100%
- 详见: 附录B

### 3.3 性能测试
- 推理时间: 平均45ms（要求<100ms）✓
- 内存使用: 峰值85MB（要求<100MB）✓
- 吞吐量: 22样本/秒（要求>10）✓

## 4. 确认结果

### 4.1 测试集性能
- 数据集: 独立测试集，10,000例
- 总体准确率: 95.3%（要求>90%）✓
- 敏感性: 95.1%（要求>90%）✓
- 特异性: 97.9%（要求>85%）✓

### 4.2 亚组分析
| 亚组 | 样本量 | 准确率 | 敏感性 | 特异性 |
|------|--------|--------|--------|--------|
| 18-40岁 | 2,000 | 95.5% | 95.2% | 98.1% |
| 40-60岁 | 4,000 | 95.3% | 95.0% | 97.8% |
| 60+岁 | 4,000 | 95.1% | 95.0% | 97.7% |
| 男性 | 6,000 | 95.4% | 95.3% | 97.9% |
| 女性 | 4,000 | 95.2% | 94.8% | 98.0% |

### 4.3 临床验证
- 与3名心脏科医生对比
- AI准确率: 95.3%
- 医生平均准确率: 93.7%
- 统计检验: 非劣效性成立（p=0.03）

## 5. 失败案例分析
- 总失败案例: 470/10,000 (4.7%)
- 主要原因:
  - 信号质量差: 45%
  - 罕见心律: 30%
  - 边界情况: 25%

## 6. 结论
AI-ECG系统通过所有验证测试，满足设计规格和监管要求，
可以进入下一阶段（临床试验/上市申请）。

## 7. 批准
- 算法负责人: 张三 __________ 日期: 2024-01-15
- 质量负责人: 李四 __________ 日期: 2024-01-15
- 监管负责人: 王五 __________ 日期: 2024-01-15
```

## 下一步

- 了解[持续学习系统](continuous-learning.md)的验证挑战
- 查看[FDA SaMD指南](fda-samd-guidance.md)的验证要求
- 参考[案例研究](../../case-studies/ai-ecg-monitor.md)

---

**相关主题**:
- [AI/ML监管概述](index.md)
- [FDA SaMD指南](fda-samd-guidance.md)
- [持续学习系统](continuous-learning.md)
