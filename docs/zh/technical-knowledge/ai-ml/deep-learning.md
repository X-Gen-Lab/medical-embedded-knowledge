---
title: 深度学习算法
difficulty: intermediate
estimated_time: 2-3小时
---

# 深度学习算法

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

深度学习（Deep Learning）是机器学习的一个分支，使用多层神经网络来学习数据的层次化表示。在医疗器械领域，深度学习在医疗影像分析、生理信号处理、疾病预测等方面展现出卓越的性能。

## 为什么需要深度学习？

### 传统机器学习的局限

**传统ML流程**:
```
原始数据 → 手工特征工程 → 机器学习模型 → 预测结果
```

**问题**:
- 特征工程需要领域专家知识
- 难以捕捉复杂的非线性关系
- 无法处理高维原始数据（如图像）

**深度学习流程**:
```
原始数据 → 深度神经网络（自动学习特征） → 预测结果
```

**优势**:
- 自动学习特征表示
- 端到端学习
- 处理复杂模式
- 适合大规模数据

### 医疗领域的成功案例

- **影像诊断**: 皮肤癌检测达到皮肤科医生水平
- **眼底筛查**: 糖尿病视网膜病变检测超过眼科医生
- **病理分析**: 乳腺癌淋巴结转移检测
- **心电分析**: 心律失常自动分类

## 神经网络基础

### 1. 感知机和神经元

**单个神经元**:
```python
import numpy as np

def neuron(inputs, weights, bias):
    # 加权求和
    z = np.dot(inputs, weights) + bias
    # 激活函数
    output = sigmoid(z)
    return output

def sigmoid(z):
    return 1 / (1 + np.exp(-z))
```

**示例**:
```python
# 输入：患者特征 [年龄, BMI, 血压]
inputs = np.array([65, 28, 140])
weights = np.array([0.1, 0.3, 0.2])
bias = -10

output = neuron(inputs, weights, bias)
print(f"疾病风险: {output:.2%}")
```

### 2. 多层感知机（MLP）

**网络结构**:
```
输入层 → 隐藏层1 → 隐藏层2 → 输出层
```

**PyTorch实现**:
```python
import torch
import torch.nn as nn

class MLP(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(MLP, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, output_size)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)
        x = self.sigmoid(x)
        return x

# 创建模型
model = MLP(input_size=10, hidden_size=64, output_size=1)

# 训练模型
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# 训练循环
for epoch in range(100):
    # 前向传播
    outputs = model(X_train)
    loss = criterion(outputs, y_train)
    
    # 反向传播
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
```

### 3. 激活函数

**常用激活函数**:

```python
# Sigmoid: 输出0-1，用于二分类输出层
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# ReLU: 最常用，解决梯度消失
def relu(x):
    return np.maximum(0, x)

# Leaky ReLU: 避免神经元死亡
def leaky_relu(x, alpha=0.01):
    return np.where(x > 0, x, alpha * x)

# Tanh: 输出-1到1
def tanh(x):
    return np.tanh(x)

# Softmax: 多分类输出层
def softmax(x):
    exp_x = np.exp(x - np.max(x))
    return exp_x / exp_x.sum()
```

**选择建议**:
- 隐藏层: ReLU或Leaky ReLU
- 二分类输出: Sigmoid
- 多分类输出: Softmax
- 回归输出: 线性（无激活函数）

## 卷积神经网络（CNN）

### 1. CNN基础

**为什么用CNN处理医疗影像？**
- 局部连接：捕捉局部特征
- 权重共享：减少参数
- 平移不变性：位置无关的特征检测

**基本组件**:
- 卷积层（Convolution）
- 池化层（Pooling）
- 全连接层（Fully Connected）

### 2. 卷积操作

**1D卷积（心电信号）**:
```python
import torch.nn as nn

class ECG_CNN(nn.Module):
    def __init__(self):
        super(ECG_CNN, self).__init__()
        # 输入: (batch, 1, 5000) - 1通道，5000个采样点
        self.conv1 = nn.Conv1d(1, 32, kernel_size=5, stride=1, padding=2)
        self.relu = nn.ReLU()
        self.pool = nn.MaxPool1d(kernel_size=2)
        self.conv2 = nn.Conv1d(32, 64, kernel_size=5, stride=1, padding=2)
        self.fc = nn.Linear(64 * 1250, 5)  # 5类心律失常
    
    def forward(self, x):
        x = self.conv1(x)      # (batch, 32, 5000)
        x = self.relu(x)
        x = self.pool(x)       # (batch, 32, 2500)
        x = self.conv2(x)      # (batch, 64, 2500)
        x = self.relu(x)
        x = self.pool(x)       # (batch, 64, 1250)
        x = x.view(x.size(0), -1)  # 展平
        x = self.fc(x)         # (batch, 5)
        return x
```

**2D卷积（医疗影像）**:
```python
class MedicalImageCNN(nn.Module):
    def __init__(self):
        super(MedicalImageCNN, self).__init__()
        # 输入: (batch, 1, 224, 224) - 灰度医疗影像
        self.conv1 = nn.Conv2d(1, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)
        self.fc1 = nn.Linear(128 * 28 * 28, 512)
        self.fc2 = nn.Linear(512, 2)  # 二分类：正常/异常
        self.dropout = nn.Dropout(0.5)
    
    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))  # 112x112
        x = self.pool(F.relu(self.conv2(x)))  # 56x56
        x = self.pool(F.relu(self.conv3(x)))  # 28x28
        x = x.view(-1, 128 * 28 * 28)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x
```

### 3. 经典CNN架构

**LeNet（简单任务）**:
```python
# 适用于小图像，如28x28的医疗图像块
class LeNet(nn.Module):
    def __init__(self):
        super(LeNet, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16*4*4, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)
```

**VGG（深度网络）**:
```python
# VGG-16风格，适用于复杂医疗影像
class VGG_Medical(nn.Module):
    def __init__(self):
        super(VGG_Medical, self).__init__()
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(1, 64, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Block 2
            nn.Conv2d(64, 128, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            # Block 3
            nn.Conv2d(128, 256, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, 3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
        self.classifier = nn.Sequential(
            nn.Linear(256 * 28 * 28, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(4096, 2)
        )
```
