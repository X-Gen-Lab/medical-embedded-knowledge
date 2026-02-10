---
title: 机器学习基础
difficulty: intermediate
estimated_time: 2-3小时
---

# 机器学习基础

## 学习目标

通过本文档的学习，你将能够：

- 理解核心概念和原理
- 掌握实际应用方法
- 了解最佳实践和注意事项

## 前置知识

在学习本文档之前，建议你已经掌握：

- 基础的嵌入式系统知识
- C/C++编程基础
- 相关领域的基本概念

## 概述

机器学习（Machine Learning, ML）是人工智能的核心技术，使计算机能够从数据中学习规律，而无需显式编程。在医疗器械领域，机器学习被广泛应用于诊断辅助、风险预测、信号处理等场景。

## 什么是机器学习？

### 传统编程 vs 机器学习

**传统编程**:
```
输入数据 + 规则（程序） → 输出结果
```

**机器学习**:
```
输入数据 + 输出结果 → 规则（模型）
```

### 医疗器械中的例子

**传统方法**:
```python
# 传统的心率异常检测
if heart_rate > 100:
    alert = "心动过速"
elif heart_rate < 60:
    alert = "心动过缓"
else:
    alert = "正常"
```

**机器学习方法**:
```python
# ML心率异常检测
model = train_model(historical_ecg_data, labels)
prediction = model.predict(new_ecg_data)
# 模型自动学习复杂的心律失常模式
```

## 机器学习的类型

### 1. 监督学习（Supervised Learning）

**定义**: 从标注数据中学习输入到输出的映射关系

**医疗应用**:
- **分类**: 疾病诊断（正常/异常）、病灶分类（良性/恶性）
- **回归**: 血糖预测、血压估计、生存时间预测

**常用算法**:
- 逻辑回归（Logistic Regression）
- 支持向量机（SVM）
- 决策树（Decision Tree）
- 随机森林（Random Forest）
- 神经网络（Neural Network）

**示例：心电图分类**
```python
# 训练数据
X_train = ecg_signals  # 心电信号特征
y_train = labels       # 标签：0=正常, 1=房颤, 2=室颤

# 训练模型
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# 预测新数据
new_ecg = extract_features(patient_ecg)
prediction = model.predict(new_ecg)
```

### 2. 无监督学习（Unsupervised Learning）

**定义**: 从未标注数据中发现隐藏的模式和结构

**医疗应用**:
- **聚类**: 患者分组、疾病亚型发现
- **降维**: 高维医疗数据可视化
- **异常检测**: 罕见疾病识别、设备故障检测

**常用算法**:
- K-Means聚类
- 层次聚类（Hierarchical Clustering）
- 主成分分析（PCA）
- 自编码器（Autoencoder）

**示例：患者分组**
```python
from sklearn.cluster import KMeans

# 患者特征：年龄、血压、血糖、BMI等
patient_features = [[65, 140, 6.5, 28], 
                    [45, 120, 5.2, 24], ...]

# 聚类分析
kmeans = KMeans(n_clusters=3)
patient_groups = kmeans.fit_predict(patient_features)
# 结果：将患者分为3个风险组
```

### 3. 强化学习（Reinforcement Learning）

**定义**: 通过与环境交互，学习最优决策策略

**医疗应用**:
- 治疗方案优化
- 药物剂量调整
- 手术机器人控制
- ICU患者管理

**示例：胰岛素剂量优化**
```
状态: 当前血糖、进食情况、运动量
动作: 胰岛素剂量
奖励: 血糖控制在目标范围内
目标: 学习最优的剂量调整策略
```

## 机器学习工作流程

### 1. 问题定义
- 明确医疗目标（诊断、预测、监测）
- 确定输入和输出
- 定义性能指标

### 2. 数据收集
- 临床数据采集
- 数据标注（专家标注）
- 数据质量控制

### 3. 数据预处理
```python
# 数据清洗
data = remove_outliers(raw_data)
data = handle_missing_values(data)

# 特征工程
features = extract_features(data)
features = normalize_features(features)

# 数据划分
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.2, random_state=42
)
```

### 4. 模型选择和训练
```python
# 尝试多个模型
models = {
    'Logistic Regression': LogisticRegression(),
    'Random Forest': RandomForestClassifier(),
    'SVM': SVC(),
    'Neural Network': MLPClassifier()
}

# 训练和评估
for name, model in models.items():
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f"{name}: {score:.3f}")
```

### 5. 模型评估
```python
from sklearn.metrics import classification_report, confusion_matrix

# 预测
y_pred = model.predict(X_test)

# 评估指标
print(classification_report(y_test, y_pred))
print(confusion_matrix(y_test, y_pred))
```

### 6. 模型优化
```python
from sklearn.model_selection import GridSearchCV

# 超参数调优
param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [10, 20, 30],
    'min_samples_split': [2, 5, 10]
}

grid_search = GridSearchCV(
    RandomForestClassifier(), 
    param_grid, 
    cv=5
)
grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_
```

### 7. 部署和监控
- 模型集成到医疗器械
- 性能持续监控
- 定期更新和维护

## 医疗器械中的关键概念

### 1. 特征工程

**时域特征**（心电信号）:
```python
def extract_time_features(ecg_signal):
    features = {
        'mean_rr': np.mean(rr_intervals),
        'std_rr': np.std(rr_intervals),
        'rmssd': np.sqrt(np.mean(np.diff(rr_intervals)**2)),
        'pnn50': np.sum(np.abs(np.diff(rr_intervals)) > 50) / len(rr_intervals)
    }
    return features
```

**频域特征**:
```python
def extract_frequency_features(signal, fs=250):
    # 傅里叶变换
    fft = np.fft.fft(signal)
    freqs = np.fft.fftfreq(len(signal), 1/fs)
    
    # 功率谱密度
    psd = np.abs(fft)**2
    
    # 频段能量
    lf_power = np.sum(psd[(freqs >= 0.04) & (freqs < 0.15)])
    hf_power = np.sum(psd[(freqs >= 0.15) & (freqs < 0.4)])
    
    return {'lf_power': lf_power, 'hf_power': hf_power}
```

### 2. 交叉验证

**K折交叉验证**:
```python
from sklearn.model_selection import cross_val_score

# 5折交叉验证
scores = cross_val_score(model, X, y, cv=5)
print(f"准确率: {scores.mean():.3f} (+/- {scores.std():.3f})")
```

**留一法交叉验证**（小数据集）:
```python
from sklearn.model_selection import LeaveOneOut

loo = LeaveOneOut()
scores = cross_val_score(model, X, y, cv=loo)
```

### 3. 性能指标

**分类指标**:
```python
from sklearn.metrics import (
    accuracy_score,      # 准确率
    precision_score,     # 精确率
    recall_score,        # 召回率（敏感性）
    f1_score,           # F1分数
    roc_auc_score       # AUC
)

# 计算指标
accuracy = accuracy_score(y_true, y_pred)
precision = precision_score(y_true, y_pred)
recall = recall_score(y_true, y_pred)  # 敏感性
f1 = f1_score(y_true, y_pred)
auc = roc_auc_score(y_true, y_pred_proba)
```

**医疗器械关注的指标**:
- **敏感性（Sensitivity）**: 正确识别阳性的比例（不漏诊）
- **特异性（Specificity）**: 正确识别阴性的比例（不误诊）
- **阳性预测值（PPV）**: 预测为阳性中真正阳性的比例
- **阴性预测值（NPV）**: 预测为阴性中真正阴性的比例

```python
from sklearn.metrics import confusion_matrix

tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

sensitivity = tp / (tp + fn)  # 敏感性
specificity = tn / (tn + fp)  # 特异性
ppv = tp / (tp + fp)          # 阳性预测值
npv = tn / (tn + fn)          # 阴性预测值
```

### 4. 过拟合和欠拟合

**过拟合**（Overfitting）:
- 模型在训练集上表现很好，但在测试集上表现差
- 原因：模型过于复杂，记住了训练数据的噪声

**欠拟合**（Underfitting）:
- 模型在训练集和测试集上都表现差
- 原因：模型过于简单，无法捕捉数据的规律

**解决方法**:
```python
# 1. 正则化
from sklearn.linear_model import Ridge, Lasso

# L2正则化
ridge = Ridge(alpha=1.0)

# L1正则化
lasso = Lasso(alpha=1.0)

# 2. Dropout（神经网络）
from tensorflow.keras.layers import Dropout

model.add(Dense(128, activation='relu'))
model.add(Dropout(0.5))  # 随机丢弃50%的神经元

# 3. 早停（Early Stopping）
from tensorflow.keras.callbacks import EarlyStopping

early_stop = EarlyStopping(
    monitor='val_loss', 
    patience=10, 
    restore_best_weights=True
)
model.fit(X_train, y_train, validation_split=0.2, callbacks=[early_stop])

# 4. 数据增强
from scipy.ndimage import rotate, shift

def augment_ecg(signal):
    # 时间平移
    shifted = shift(signal, shift=np.random.randint(-10, 10))
    # 幅度缩放
    scaled = signal * np.random.uniform(0.9, 1.1)
    return shifted, scaled
```

## 常用算法详解

### 1. 逻辑回归

**适用场景**: 二分类问题（疾病有/无）

**优点**:
- 简单、快速
- 可解释性强
- 输出概率值

**示例：糖尿病风险预测**
```python
from sklearn.linear_model import LogisticRegression

# 特征：年龄、BMI、血压、家族史
X = patient_data[['age', 'bmi', 'blood_pressure', 'family_history']]
y = patient_data['diabetes']  # 0=无, 1=有

# 训练模型
lr = LogisticRegression()
lr.fit(X, y)

# 预测概率
risk_prob = lr.predict_proba(new_patient)[:, 1]
print(f"糖尿病风险: {risk_prob[0]:.1%}")

# 查看特征重要性
for feature, coef in zip(X.columns, lr.coef_[0]):
    print(f"{feature}: {coef:.3f}")
```

### 2. 随机森林

**适用场景**: 分类和回归，处理复杂非线性关系

**优点**:
- 准确率高
- 抗过拟合
- 可处理缺失值
- 提供特征重要性

**示例：心脏病诊断**
```python
from sklearn.ensemble import RandomForestClassifier

# 训练随机森林
rf = RandomForestClassifier(
    n_estimators=100,      # 树的数量
    max_depth=10,          # 树的最大深度
    min_samples_split=5,   # 分裂所需最小样本数
    random_state=42
)
rf.fit(X_train, y_train)

# 特征重要性
importances = rf.feature_importances_
for feature, importance in sorted(
    zip(feature_names, importances), 
    key=lambda x: x[1], 
    reverse=True
):
    print(f"{feature}: {importance:.3f}")
```

### 3. 支持向量机（SVM）

**适用场景**: 小样本、高维数据分类

**优点**:
- 泛化能力强
- 适合高维空间
- 核函数处理非线性

**示例：癌症分类**
```python
from sklearn.svm import SVC

# 训练SVM
svm = SVC(
    kernel='rbf',      # 径向基核函数
    C=1.0,            # 正则化参数
    gamma='scale'     # 核系数
)
svm.fit(X_train, y_train)

# 预测
prediction = svm.predict(X_test)
```

### 4. K近邻（KNN）

**适用场景**: 简单分类、异常检测

**优点**:
- 简单直观
- 无需训练
- 适合多分类

**示例：心律失常分类**
```python
from sklearn.neighbors import KNeighborsClassifier

# 训练KNN
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)

# 预测并返回概率
proba = knn.predict_proba(X_test)
```

## 医疗数据的特殊考虑

### 1. 不平衡数据

**问题**: 疾病样本远少于正常样本

**解决方法**:
```python
# 方法1: 重采样
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

# 过采样（SMOTE）
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# 欠采样
rus = RandomUnderSampler(random_state=42)
X_resampled, y_resampled = rus.fit_resample(X_train, y_train)

# 方法2: 类权重
model = RandomForestClassifier(class_weight='balanced')

# 方法3: 调整决策阈值
y_pred_proba = model.predict_proba(X_test)[:, 1]
y_pred = (y_pred_proba > 0.3).astype(int)  # 降低阈值提高敏感性
```

### 2. 小样本学习

**策略**:
- 使用简单模型（避免过拟合）
- 交叉验证
- 迁移学习
- 数据增强

```python
# 留一法交叉验证（小数据集）
from sklearn.model_selection import LeaveOneOut

loo = LeaveOneOut()
scores = []
for train_idx, test_idx in loo.split(X):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    scores.append(score)

print(f"平均准确率: {np.mean(scores):.3f}")
```

### 3. 多模态数据融合

**场景**: 结合影像、生理信号、临床数据

```python
# 特征级融合
image_features = extract_image_features(ct_scan)
signal_features = extract_ecg_features(ecg_data)
clinical_features = [age, gender, bmi, blood_pressure]

# 合并特征
combined_features = np.concatenate([
    image_features,
    signal_features,
    clinical_features
])

# 训练模型
model.fit(combined_features, labels)
```

## 实践建议

### 1. 数据质量优先
- 确保数据标注准确
- 多专家标注一致性检查
- 数据来源多样性

### 2. 从简单开始
- 先尝试简单模型（逻辑回归、决策树）
- 建立基线性能
- 逐步增加复杂度

### 3. 关注临床意义
- 性能指标符合临床需求
- 敏感性 vs 特异性权衡
- 假阳性/假阴性的临床后果

### 4. 可解释性
- 提供预测依据
- 特征重要性分析
- 可视化决策过程

### 5. 鲁棒性测试
- 不同患者群体
- 不同设备和环境
- 边界情况和异常输入

## 工具和库

### Python机器学习生态
```python
# 基础库
import numpy as np           # 数值计算
import pandas as pd          # 数据处理
import matplotlib.pyplot as plt  # 可视化

# 机器学习
from sklearn import *        # scikit-learn
import xgboost as xgb       # XGBoost
import lightgbm as lgb      # LightGBM

# 医疗专用
import wfdb                 # 生理信号处理
import pydicom              # DICOM影像处理
import nibabel              # 神经影像处理
```

### 开发环境
- Jupyter Notebook: 交互式开发
- Google Colab: 免费GPU
- Kaggle Kernels: 数据集和竞赛

## 下一步

- 学习[深度学习算法](deep-learning.md)了解更强大的模型
- 查看[医疗应用场景](medical-applications.md)了解实际应用
- 阅读[算法验证](../../regulatory-standards/ai-ml-regulations/algorithm-validation.md)了解监管要求

---

**相关主题**:
- [深度学习算法](deep-learning.md)
- [嵌入式AI实现](embedded-ai.md)
- [算法验证方法](../../regulatory-standards/ai-ml-regulations/algorithm-validation.md)
