---
title: 模型优化技术
description: "学习AI模型优化技术，实现医疗设备上的高效推理"
difficulty: 中级
estimated_time: 2-3小时
last_updated: "2026-02-11"
version: "1.0"
language: "zh-CN"
tags:
  - model-optimization
  - quantization
  - pruning
  - edge-ai
---

# 模型优化技术

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

模型优化是将大型深度学习模型转换为适合嵌入式设备运行的小型、高效模型的过程。在医疗器械中，优化后的模型需要在保持诊断准确性的同时，满足实时性、低功耗和小尺寸的要求。

## 为什么需要模型优化？

### 典型场景对比

**云端模型**:
```
ResNet-50:
- 参数量: 25M
- 模型大小: 100MB
- 推理时间: 50ms (GPU)
- 内存占用: 200MB
```

**嵌入式需求**:
```
可穿戴心电监护:
- 可用Flash: 1MB
- 可用RAM: 100KB
- 推理时间: <10ms
- 功耗: <50mW
```

**优化目标**:
- 模型大小: 100MB → 100KB (1000x压缩)
- 推理时间: 50ms → 5ms (10x加速)
- 内存占用: 200MB → 50KB (4000x减少)
- 准确率损失: <2%

## 主要优化技术

### 1. 量化（Quantization）

**原理**: 降低数值精度，减少存储和计算

**精度对比**:
```
FP32 (浮点32位):
- 范围: ±3.4×10^38
- 精度: 7位小数
- 大小: 4字节/参数

INT8 (整数8位):
- 范围: -128 to 127
- 精度: 整数
- 大小: 1字节/参数
- 压缩比: 4x
```

**量化方法**:

**训练后量化（Post-Training Quantization）**:
```python
import tensorflow as tf

# 1. 加载训练好的模型
model = tf.keras.models.load_model('ecg_model.h5')

# 2. 转换为TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# 3. 启用量化
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# 4. 提供代表性数据集（用于校准）
def representative_dataset():
    for i in range(100):
        yield [ecg_samples[i:i+1].astype(np.float32)]

converter.representative_dataset = representative_dataset

# 5. 设置为INT8量化
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8

# 6. 转换
tflite_model = converter.convert()

# 7. 保存
with open('ecg_model_quantized.tflite', 'wb') as f:
    f.write(tflite_model)

# 结果：模型大小从2MB减少到500KB
```

**量化感知训练（Quantization-Aware Training）**:
```python
import tensorflow_model_optimization as tfmot

# 1. 定义模型
model = create_ecg_model()

# 2. 应用量化感知训练
quantize_model = tfmot.quantization.keras.quantize_model

q_aware_model = quantize_model(model)

# 3. 训练（模拟量化效果）
q_aware_model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

q_aware_model.fit(
    train_data, train_labels,
    epochs=10,
    validation_data=(val_data, val_labels)
)

# 4. 转换为量化模型
converter = tf.lite.TFLiteConverter.from_keras_model(q_aware_model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# 结果：准确率损失更小（<1%）
```

**混合精度量化**:
```python
# 关键层保持FP32，其他层INT8
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# 设置操作白名单（保持FP32）
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS,  # FP32
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8  # INT8
]

# 最后一层保持FP32（提高准确性）
converter.inference_output_type = tf.float32
```

### 2. 剪枝（Pruning）

**原理**: 移除不重要的权重，减少参数量

**剪枝类型**:

**非结构化剪枝**（移除单个权重）:
```python
import tensorflow_model_optimization as tfmot

# 1. 定义剪枝参数
pruning_params = {
    'pruning_schedule': tfmot.sparsity.keras.PolynomialDecay(
        initial_sparsity=0.0,    # 初始稀疏度
        final_sparsity=0.75,     # 最终稀疏度（75%权重为0）
        begin_step=0,
        end_step=1000
    )
}

# 2. 应用剪枝
model = create_model()
pruned_model = tfmot.sparsity.keras.prune_low_magnitude(
    model, 
    **pruning_params
)

# 3. 训练
pruned_model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 添加剪枝回调
callbacks = [
    tfmot.sparsity.keras.UpdatePruningStep()
]

pruned_model.fit(
    train_data, train_labels,
    epochs=10,
    callbacks=callbacks
)

# 4. 移除剪枝包装器
final_model = tfmot.sparsity.keras.strip_pruning(pruned_model)

# 结果：75%参数为0，可进一步压缩
```

**结构化剪枝**（移除整个通道/神经元）:
```python
# 手动实现通道剪枝
def prune_channels(model, layer_name, channels_to_keep):
    """
    移除卷积层中不重要的通道
    """
    layer = model.get_layer(layer_name)
    weights = layer.get_weights()
    
    # 计算每个通道的重要性（L1范数）
    channel_importance = np.sum(np.abs(weights[0]), axis=(0, 1, 2))
    
    # 选择最重要的通道
    important_channels = np.argsort(channel_importance)[-channels_to_keep:]
    
    # 剪枝权重
    new_weights = weights[0][:, :, :, important_channels]
    new_bias = weights[1][important_channels]
    
    return new_weights, new_bias

# 示例：将64通道减少到32通道
pruned_weights = prune_channels(model, 'conv1', channels_to_keep=32)
```

### 3. 知识蒸馏（Knowledge Distillation）

**原理**: 训练小模型（学生）模仿大模型（教师）

**实现**:
```python
import tensorflow as tf

# 1. 教师模型（大模型，已训练好）
teacher_model = tf.keras.models.load_model('teacher_resnet50.h5')

# 2. 学生模型（小模型）
def create_student_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Conv2D(32, 3, activation='relu', input_shape=(224, 224, 1)),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(64, 3, activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(10)  # 10类
    ])
    return model

student_model = create_student_model()

# 3. 蒸馏损失函数
class DistillationLoss(tf.keras.losses.Loss):
    def __init__(self, teacher_model, temperature=3.0, alpha=0.5):
        super().__init__()
        self.teacher_model = teacher_model
        self.temperature = temperature
        self.alpha = alpha
        self.student_loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    
    def call(self, y_true, y_pred_student):
        # 教师预测（软标签）
        y_pred_teacher = self.teacher_model(y_true, training=False)
        
        # 蒸馏损失（KL散度）
        distillation_loss = tf.keras.losses.KLDivergence()(
            tf.nn.softmax(y_pred_teacher / self.temperature),
            tf.nn.softmax(y_pred_student / self.temperature)
        ) * (self.temperature ** 2)
        
        # 学生损失（硬标签）
        student_loss = self.student_loss(y_true, y_pred_student)
        
        # 组合损失
        return self.alpha * distillation_loss + (1 - self.alpha) * student_loss

# 4. 训练学生模型
student_model.compile(
    optimizer='adam',
    loss=DistillationLoss(teacher_model),
    metrics=['accuracy']
)

student_model.fit(train_data, train_labels, epochs=20)

# 结果：学生模型小10倍，准确率接近教师模型
```
