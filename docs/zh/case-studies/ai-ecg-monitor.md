---
title: AI心电监护系统完整案例
description: CardioAI智能心电监护系统的完整开发案例，涵盖需求分析、架构设计、AI模型开发和法规认证
difficulty: 高级
estimated_time: 3小时
tags:
  - 案例研究
  - AI心电
  - 深度学习
  - 实时监护
  - III类器械
related_modules:
  - zh/technical-knowledge/ai-ml/index
  - zh/technical-knowledge/signal-processing/ecg-processing
  - zh/regulatory-standards/iec-62304/index
  - zh/regulatory-standards/ai-ml-regulations/index
last_updated: '2026-02-10'
version: '1.0'
language: zh-CN
---

# AI心电监护系统完整案例

## 案例概述

### 产品简介
**产品名称**: CardioAI智能心电监护系统  
**分类**: III类医疗器械（高风险）  
**适用范围**: 用于心律失常的实时检测和预警，特别是房颤、室颤等危及生命的心律失常  
**目标用户**: 医院ICU、心内科、急诊科；家庭远程监护

### 系统特点
- **实时AI分析**: 使用深度学习模型实时分析ECG信号
- **多导联支持**: 支持12导联标准ECG和单导联可穿戴设备
- **云端协同**: 边缘计算+云端分析的混合架构
- **智能告警**: 基于AI的智能告警系统，减少误报
- **远程监护**: 支持远程实时监控和历史数据分析

## 技术架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    医护人员端                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Web监护台   │  │  移动应用    │  │  告警系统    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      云平台层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  AI推理服务  │  │  数据存储    │  │  告警引擎    │      │
│  │  (深度模型)  │  │  (时序DB)    │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  模型管理    │  │  报告生成    │  │  数据分析    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      边缘设备层                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  ECG采集模块 │  │  边缘AI芯片  │  │  数据预处理  │      │
│  │  (AFE芯片)   │  │  (轻量模型)  │  │  (滤波/降噪) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

#### 硬件平台
- **MCU**: STM32H7系列 (Cortex-M7, 480MHz)
- **AI加速器**: ARM Cortex-M55 + Ethos-U55 NPU
- **ECG前端**: ADS1298 (8通道24位ADC)
- **无线通信**: BLE 5.0 + WiFi 6
- **存储**: 2MB Flash + 1MB RAM + 32GB eMMC

#### 软件平台
- **嵌入式OS**: FreeRTOS
- **AI框架**: TensorFlow Lite Micro
- **云平台**: AWS (EC2, Lambda, SageMaker)
- **后端**: Python (FastAPI), Node.js
- **前端**: React, React Native
- **数据库**: InfluxDB (时序), PostgreSQL (关系), S3 (对象存储)

## AI模型设计

### 模型架构

#### 1. 边缘端轻量级模型

```python
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

def create_edge_ecg_model(input_shape=(2500, 1), num_classes=5):
    """
    边缘端ECG分类模型
    
    输入: 10秒ECG信号 (250Hz采样率)
    输出: 5类心律失常分类
        - 0: 正常窦性心律 (Normal Sinus Rhythm)
        - 1: 房颤 (Atrial Fibrillation)
        - 2: 室性早搏 (Premature Ventricular Contraction)
        - 3: 室上性早搏 (Supraventricular Premature Beat)
        - 4: 其他异常 (Other Abnormalities)
    """
    
    model = keras.Sequential([
        # 输入层
        layers.Input(shape=input_shape),
        
        # 第一卷积块 - 提取低级特征
        layers.Conv1D(32, kernel_size=5, strides=1, padding='same'),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.2),
        
        # 第二卷积块 - 提取中级特征
        layers.Conv1D(64, kernel_size=5, strides=1, padding='same'),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.2),
        
        # 第三卷积块 - 提取高级特征
        layers.Conv1D(128, kernel_size=3, strides=1, padding='same'),
        layers.BatchNormalization(),
        layers.ReLU(),
        layers.MaxPooling1D(pool_size=2),
        layers.Dropout(0.3),
        
        # 全局平均池化
        layers.GlobalAveragePooling1D(),
        
        # 全连接层
        layers.Dense(64, activation='relu'),
        layers.Dropout(0.4),
        
        # 输出层
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model

# 创建模型
edge_model = create_edge_ecg_model()

# 编译模型
edge_model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.001),
    loss='categorical_crossentropy',
    metrics=['accuracy', 'AUC']
)

# 模型摘要
edge_model.summary()

# 模型大小: ~500KB (适合嵌入式部署)
```

#### 2. 云端深度模型

```python
def create_cloud_ecg_model(input_shape=(5000, 12), num_classes=17):
    """
    云端ECG分类模型 - 更复杂的ResNet架构
    
    输入: 20秒12导联ECG信号
    输出: 17类详细心律失常分类
    """
    
    def residual_block(x, filters, kernel_size=3):
        """残差块"""
        shortcut = x
        
        # 第一卷积
        x = layers.Conv1D(filters, kernel_size, padding='same')(x)
        x = layers.BatchNormalization()(x)
        x = layers.ReLU()(x)
        
        # 第二卷积
        x = layers.Conv1D(filters, kernel_size, padding='same')(x)
        x = layers.BatchNormalization()(x)
        
        # 调整shortcut维度
        if shortcut.shape[-1] != filters:
            shortcut = layers.Conv1D(filters, 1, padding='same')(shortcut)
        
        # 残差连接
        x = layers.Add()([x, shortcut])
        x = layers.ReLU()(x)
        
        return x
    
    # 输入
    inputs = layers.Input(shape=input_shape)
    
    # 初始卷积
    x = layers.Conv1D(64, 7, strides=2, padding='same')(inputs)
    x = layers.BatchNormalization()(x)
    x = layers.ReLU()(x)
    x = layers.MaxPooling1D(3, strides=2, padding='same')(x)
    
    # 残差块组
    x = residual_block(x, 64)
    x = residual_block(x, 64)
    x = layers.MaxPooling1D(2)(x)
    
    x = residual_block(x, 128)
    x = residual_block(x, 128)
    x = layers.MaxPooling1D(2)(x)
    
    x = residual_block(x, 256)
    x = residual_block(x, 256)
    x = layers.MaxPooling1D(2)(x)
    
    x = residual_block(x, 512)
    x = residual_block(x, 512)
    
    # 全局平均池化
    x = layers.GlobalAveragePooling1D()(x)
    
    # 全连接层
    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.5)(x)
    
    # 输出层
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = keras.Model(inputs=inputs, outputs=outputs)
    
    return model

# 创建云端模型
cloud_model = create_cloud_ecg_model()

# 编译模型
cloud_model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=0.0001),
    loss='categorical_crossentropy',
    metrics=['accuracy', 'AUC', 'Precision', 'Recall']
)

# 模型大小: ~50MB
```

### 模型训练

```python
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau

class ECGDataGenerator(keras.utils.Sequence):
    """ECG数据生成器"""
    
    def __init__(self, ecg_data, labels, batch_size=32, shuffle=True, augment=False):
        self.ecg_data = ecg_data
        self.labels = labels
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.augment = augment
        self.indexes = np.arange(len(self.ecg_data))
        self.on_epoch_end()
    
    def __len__(self):
        return int(np.floor(len(self.ecg_data) / self.batch_size))
    
    def __getitem__(self, index):
        indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]
        
        X = np.array([self.ecg_data[i] for i in indexes])
        y = np.array([self.labels[i] for i in indexes])
        
        if self.augment:
            X = self._augment_data(X)
        
        return X, y
    
    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.indexes)
    
    def _augment_data(self, X):
        """数据增强"""
        # 添加高斯噪声
        noise = np.random.normal(0, 0.01, X.shape)
        X_aug = X + noise
        
        # 随机缩放
        scale = np.random.uniform(0.9, 1.1, (X.shape[0], 1, 1))
        X_aug = X_aug * scale
        
        # 随机时间偏移
        shift = np.random.randint(-50, 50, X.shape[0])
        for i in range(X.shape[0]):
            X_aug[i] = np.roll(X_aug[i], shift[i], axis=0)
        
        return X_aug

# 加载数据 (示例)
# 实际应用中从MIT-BIH、PTB-XL等数据集加载
X_train = np.random.randn(10000, 2500, 1)  # 示例数据
y_train = keras.utils.to_categorical(np.random.randint(0, 5, 10000), 5)

X_val = np.random.randn(2000, 2500, 1)
y_val = keras.utils.to_categorical(np.random.randint(0, 5, 2000), 5)

# 创建数据生成器
train_generator = ECGDataGenerator(X_train, y_train, batch_size=32, augment=True)
val_generator = ECGDataGenerator(X_val, y_val, batch_size=32, augment=False)

# 回调函数
callbacks = [
    ModelCheckpoint(
        'best_ecg_model.h5',
        monitor='val_accuracy',
        save_best_only=True,
        mode='max',
        verbose=1
    ),
    EarlyStopping(
        monitor='val_loss',
        patience=10,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    )
]

# 训练模型
history = edge_model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=100,
    callbacks=callbacks,
    verbose=1
)
```


### 模型优化与量化

```python
import tensorflow as tf

def quantize_model_for_edge(model, representative_dataset):
    """
    模型量化 - 转换为TensorFlow Lite格式
    """
    
    # 创建转换器
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    
    # 启用优化
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    
    # 设置代表性数据集用于量化
    def representative_data_gen():
        for data in representative_dataset:
            yield [data.astype(np.float32)]
    
    converter.representative_dataset = representative_data_gen
    
    # 全整数量化
    converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
    converter.inference_input_type = tf.int8
    converter.inference_output_type = tf.int8
    
    # 转换模型
    tflite_model = converter.convert()
    
    # 保存模型
    with open('ecg_model_quantized.tflite', 'wb') as f:
        f.write(tflite_model)
    
    print(f"原始模型大小: {model.count_params() * 4 / 1024:.2f} KB")
    print(f"量化模型大小: {len(tflite_model) / 1024:.2f} KB")
    
    return tflite_model

# 准备代表性数据集
representative_dataset = X_train[:1000]

# 量化模型
tflite_model = quantize_model_for_edge(edge_model, representative_dataset)

# 验证量化模型
def evaluate_tflite_model(tflite_model, test_data, test_labels):
    """评估TFLite模型"""
    
    # 加载模型
    interpreter = tf.lite.Interpreter(model_content=tflite_model)
    interpreter.allocate_tensors()
    
    # 获取输入输出详情
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    
    # 推理
    predictions = []
    for data in test_data:
        # 量化输入
        input_scale, input_zero_point = input_details[0]['quantization']
        data_quantized = (data / input_scale + input_zero_point).astype(np.int8)
        
        # 设置输入
        interpreter.set_tensor(input_details[0]['index'], [data_quantized])
        
        # 运行推理
        interpreter.invoke()
        
        # 获取输出
        output = interpreter.get_tensor(output_details[0]['index'])
        
        # 反量化输出
        output_scale, output_zero_point = output_details[0]['quantization']
        output_dequantized = (output.astype(np.float32) - output_zero_point) * output_scale
        
        predictions.append(output_dequantized[0])
    
    predictions = np.array(predictions)
    accuracy = np.mean(np.argmax(predictions, axis=1) == np.argmax(test_labels, axis=1))
    
    print(f"量化模型准确率: {accuracy * 100:.2f}%")
    
    return accuracy

# 评估
evaluate_tflite_model(tflite_model, X_val[:100], y_val[:100])
```

## 嵌入式实现

### ECG信号采集

```c
// ecg_acquisition.c
#include "stm32h7xx_hal.h"
#include "ads1298.h"

#define ECG_SAMPLE_RATE 250  // 250 Hz
#define ECG_BUFFER_SIZE 2500 // 10秒数据

typedef struct {
    int32_t data[ECG_BUFFER_SIZE];
    uint16_t write_index;
    uint8_t is_full;
} ECGBuffer;

static ECGBuffer ecg_buffer = {0};
static SPI_HandleTypeDef hspi1;

/**
 * @brief 初始化ADS1298 ECG前端芯片
 */
void ECG_Init(void) {
    // 配置SPI
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;
    hspi1.Init.Direction = SPI_DIRECTION_2LINES;
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;
    hspi1.Init.CLKPhase = SPI_PHASE_2EDGE;
    hspi1.Init.NSS = SPI_NSS_SOFT;
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_16;
    HAL_SPI_Init(&hspi1);
    
    // 复位ADS1298
    ADS1298_Reset();
    HAL_Delay(100);
    
    // 配置ADS1298寄存器
    ADS1298_WriteReg(CONFIG1, 0x96);  // 250 SPS
    ADS1298_WriteReg(CONFIG2, 0xE0);  // 内部参考
    ADS1298_WriteReg(CONFIG3, 0xEC);  // 使能内部参考缓冲
    
    // 配置通道1 (导联II)
    ADS1298_WriteReg(CH1SET, 0x00);   // 正常输入，增益6
    
    // 启动连续转换
    ADS1298_StartConversion();
}

/**
 * @brief ECG数据采集中断处理
 */
void ECG_DataReadyCallback(void) {
    int32_t ecg_sample;
    
    // 读取ECG样本
    ecg_sample = ADS1298_ReadData(1);  // 读取通道1
    
    // 存储到缓冲区
    ecg_buffer.data[ecg_buffer.write_index++] = ecg_sample;
    
    // 检查缓冲区是否已满
    if (ecg_buffer.write_index >= ECG_BUFFER_SIZE) {
        ecg_buffer.write_index = 0;
        ecg_buffer.is_full = 1;
        
        // 触发AI推理
        xTaskNotifyGive(ai_inference_task_handle);
    }
}

/**
 * @brief 获取ECG缓冲区数据
 */
void ECG_GetBuffer(int32_t *buffer, uint16_t size) {
    memcpy(buffer, ecg_buffer.data, size * sizeof(int32_t));
    ecg_buffer.is_full = 0;
}
```

### 信号预处理

```c
// ecg_preprocessing.c
#include "arm_math.h"

#define FILTER_ORDER 4
#define NOTCH_FREQ 50.0f  // 50Hz工频干扰

// 带通滤波器系数 (0.5-40Hz)
static float32_t bpf_coeffs[5] = {0.0201, 0.0000, -0.0402, 0.0000, 0.0201};
static float32_t bpf_state[4] = {0};

// 陷波滤波器系数 (50Hz)
static float32_t notch_coeffs[5] = {0.9780, -1.8999, 0.9780, -1.8999, 0.9561};
static float32_t notch_state[4] = {0};

/**
 * @brief ECG信号预处理
 * @param input 输入ECG信号
 * @param output 输出处理后的信号
 * @param length 信号长度
 */
void ECG_Preprocess(int32_t *input, float32_t *output, uint16_t length) {
    float32_t temp[ECG_BUFFER_SIZE];
    
    // 1. 转换为浮点数并归一化
    for (uint16_t i = 0; i < length; i++) {
        temp[i] = (float32_t)input[i] / 8388608.0f;  // 24位ADC
    }
    
    // 2. 去除基线漂移 (高通滤波)
    arm_biquad_cascade_df2T_f32(
        &bpf_instance,
        temp,
        output,
        length
    );
    
    // 3. 去除工频干扰 (陷波滤波)
    arm_biquad_cascade_df2T_f32(
        &notch_instance,
        output,
        output,
        length
    );
    
    // 4. 归一化到[-1, 1]
    float32_t max_val = 0.0f;
    arm_max_f32(output, length, &max_val, NULL);
    
    float32_t min_val = 0.0f;
    arm_min_f32(output, length, &min_val, NULL);
    
    float32_t range = max_val - min_val;
    if (range > 0.0f) {
        for (uint16_t i = 0; i < length; i++) {
            output[i] = 2.0f * (output[i] - min_val) / range - 1.0f;
        }
    }
}

/**
 * @brief R波检测 (Pan-Tompkins算法)
 */
typedef struct {
    uint16_t position;
    float32_t amplitude;
} RPeak;

uint16_t ECG_DetectRPeaks(float32_t *ecg, uint16_t length, RPeak *peaks, uint16_t max_peaks) {
    float32_t derivative[ECG_BUFFER_SIZE];
    float32_t squared[ECG_BUFFER_SIZE];
    float32_t integrated[ECG_BUFFER_SIZE];
    
    // 1. 带通滤波 (已在预处理中完成)
    
    // 2. 求导
    for (uint16_t i = 1; i < length; i++) {
        derivative[i] = ecg[i] - ecg[i-1];
    }
    derivative[0] = 0;
    
    // 3. 平方
    arm_mult_f32(derivative, derivative, squared, length);
    
    // 4. 移动窗口积分
    uint16_t window_size = 30;  // 120ms @ 250Hz
    for (uint16_t i = 0; i < length; i++) {
        float32_t sum = 0.0f;
        uint16_t start = (i >= window_size) ? (i - window_size) : 0;
        for (uint16_t j = start; j <= i; j++) {
            sum += squared[j];
        }
        integrated[i] = sum / window_size;
    }
    
    // 5. 自适应阈值检测
    float32_t threshold = 0.0f;
    arm_mean_f32(integrated, length, &threshold);
    threshold *= 0.6f;
    
    uint16_t peak_count = 0;
    uint16_t refractory_period = 50;  // 200ms @ 250Hz
    uint16_t last_peak = 0;
    
    for (uint16_t i = 1; i < length - 1; i++) {
        if (integrated[i] > threshold &&
            integrated[i] > integrated[i-1] &&
            integrated[i] > integrated[i+1] &&
            (i - last_peak) > refractory_period) {
            
            if (peak_count < max_peaks) {
                peaks[peak_count].position = i;
                peaks[peak_count].amplitude = ecg[i];
                peak_count++;
                last_peak = i;
            }
        }
    }
    
    return peak_count;
}
```

### AI推理引擎

```c
// ai_inference.c
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/micro/micro_mutable_op_resolver.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include "ecg_model_data.h"  // 量化模型数据

#define TENSOR_ARENA_SIZE (100 * 1024)  // 100KB

// 全局变量
static uint8_t tensor_arena[TENSOR_ARENA_SIZE] __attribute__((aligned(16)));
static tflite::MicroInterpreter *interpreter = nullptr;
static TfLiteTensor *input_tensor = nullptr;
static TfLiteTensor *output_tensor = nullptr;

/**
 * @brief 初始化AI推理引擎
 */
int AI_Init(void) {
    // 加载模型
    const tflite::Model *model = tflite::GetModel(ecg_model_data);
    
    if (model->version() != TFLITE_SCHEMA_VERSION) {
        printf("Model schema version mismatch!\n");
        return -1;
    }
    
    // 创建操作解析器
    static tflite::MicroMutableOpResolver<6> micro_op_resolver;
    micro_op_resolver.AddConv2D();
    micro_op_resolver.AddMaxPool2D();
    micro_op_resolver.AddReshape();
    micro_op_resolver.AddFullyConnected();
    micro_op_resolver.AddSoftmax();
    micro_op_resolver.AddQuantize();
    
    // 创建解释器
    static tflite::MicroInterpreter static_interpreter(
        model,
        micro_op_resolver,
        tensor_arena,
        TENSOR_ARENA_SIZE
    );
    interpreter = &static_interpreter;
    
    // 分配张量
    TfLiteStatus allocate_status = interpreter->AllocateTensors();
    if (allocate_status != kTfLiteOk) {
        printf("AllocateTensors() failed\n");
        return -1;
    }
    
    // 获取输入输出张量
    input_tensor = interpreter->input(0);
    output_tensor = interpreter->output(0);
    
    printf("AI Engine initialized successfully\n");
    printf("Input shape: [%d, %d, %d]\n",
           input_tensor->dims->data[0],
           input_tensor->dims->data[1],
           input_tensor->dims->data[2]);
    printf("Output shape: [%d, %d]\n",
           output_tensor->dims->data[0],
           output_tensor->dims->data[1]);
    
    return 0;
}

/**
 * @brief 执行AI推理
 */
typedef enum {
    RHYTHM_NORMAL = 0,
    RHYTHM_AFIB = 1,
    RHYTHM_PVC = 2,
    RHYTHM_SVPB = 3,
    RHYTHM_OTHER = 4
} RhythmType;

typedef struct {
    RhythmType type;
    float confidence;
    uint32_t timestamp;
} InferenceResult;

int AI_Inference(float32_t *ecg_data, uint16_t length, InferenceResult *result) {
    // 1. 量化输入数据
    int8_t *input_data = input_tensor->data.int8;
    float input_scale = input_tensor->params.scale;
    int input_zero_point = input_tensor->params.zero_point;
    
    for (uint16_t i = 0; i < length; i++) {
        int32_t quantized = (int32_t)(ecg_data[i] / input_scale) + input_zero_point;
        quantized = (quantized < -128) ? -128 : (quantized > 127) ? 127 : quantized;
        input_data[i] = (int8_t)quantized;
    }
    
    // 2. 执行推理
    uint32_t start_time = HAL_GetTick();
    TfLiteStatus invoke_status = interpreter->Invoke();
    uint32_t inference_time = HAL_GetTick() - start_time;
    
    if (invoke_status != kTfLiteOk) {
        printf("Invoke failed\n");
        return -1;
    }
    
    // 3. 反量化输出
    int8_t *output_data = output_tensor->data.int8;
    float output_scale = output_tensor->params.scale;
    int output_zero_point = output_tensor->params.zero_point;
    
    float probabilities[5];
    for (int i = 0; i < 5; i++) {
        probabilities[i] = (output_data[i] - output_zero_point) * output_scale;
    }
    
    // 4. 找到最大概率的类别
    float max_prob = probabilities[0];
    int max_index = 0;
    for (int i = 1; i < 5; i++) {
        if (probabilities[i] > max_prob) {
            max_prob = probabilities[i];
            max_index = i;
        }
    }
    
    // 5. 填充结果
    result->type = (RhythmType)max_index;
    result->confidence = max_prob;
    result->timestamp = HAL_GetTick();
    
    printf("Inference: Type=%d, Confidence=%.2f%%, Time=%lums\n",
           result->type, result->confidence * 100, inference_time);
    
    return 0;
}
```


## 云端服务实现

### AI推理服务

```python
# cloud_inference_service.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import numpy as np
import tensorflow as tf
from typing import List, Dict
import asyncio
from datetime import datetime

app = FastAPI(title="CardioAI Cloud Inference Service")

# 加载云端模型
cloud_model = tf.keras.models.load_model('cloud_ecg_model.h5')

class ECGData(BaseModel):
    device_id: str
    patient_id: str
    timestamp: str
    ecg_signal: List[List[float]]  # 12导联数据
    sampling_rate: int
    duration: float

class InferenceResult(BaseModel):
    patient_id: str
    device_id: str
    timestamp: str
    predictions: Dict[str, float]
    primary_diagnosis: str
    confidence: float
    risk_level: str
    recommendations: List[str]

# 心律失常类别定义
ARRHYTHMIA_CLASSES = {
    0: "正常窦性心律",
    1: "窦性心动过速",
    2: "窦性心动过缓",
    3: "房颤",
    4: "房扑",
    5: "室上性心动过速",
    6: "室性心动过速",
    7: "室颤",
    8: "房性早搏",
    9: "室性早搏",
    10: "一度房室传导阻滞",
    11: "二度I型房室传导阻滞",
    12: "二度II型房室传导阻滞",
    13: "三度房室传导阻滞",
    14: "左束支传导阻滞",
    15: "右束支传导阻滞",
    16: "其他异常"
}

@app.post("/api/v1/inference", response_model=InferenceResult)
async def perform_inference(ecg_data: ECGData, background_tasks: BackgroundTasks):
    """
    执行ECG AI推理
    """
    try:
        # 1. 数据验证
        if len(ecg_data.ecg_signal) != 12:
            raise HTTPException(status_code=400, detail="需要12导联ECG数据")
        
        # 2. 数据预处理
        ecg_array = np.array(ecg_data.ecg_signal)
        ecg_preprocessed = preprocess_ecg(ecg_array, ecg_data.sampling_rate)
        
        # 3. 执行推理
        predictions = cloud_model.predict(np.expand_dims(ecg_preprocessed, axis=0))
        predictions = predictions[0]
        
        # 4. 解析结果
        primary_class = np.argmax(predictions)
        confidence = float(predictions[primary_class])
        
        # 5. 风险评估
        risk_level = assess_risk_level(primary_class, confidence)
        
        # 6. 生成建议
        recommendations = generate_recommendations(primary_class, risk_level)
        
        # 7. 构建结果
        result = InferenceResult(
            patient_id=ecg_data.patient_id,
            device_id=ecg_data.device_id,
            timestamp=ecg_data.timestamp,
            predictions={
                ARRHYTHMIA_CLASSES[i]: float(predictions[i])
                for i in range(len(predictions))
            },
            primary_diagnosis=ARRHYTHMIA_CLASSES[primary_class],
            confidence=confidence,
            risk_level=risk_level,
            recommendations=recommendations
        )
        
        # 8. 异步保存结果和触发告警
        background_tasks.add_task(save_inference_result, result)
        if risk_level in ["high", "critical"]:
            background_tasks.add_task(trigger_alert, result)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def preprocess_ecg(ecg_signal: np.ndarray, sampling_rate: int) -> np.ndarray:
    """
    ECG信号预处理
    """
    from scipy import signal
    
    # 1. 重采样到500Hz
    if sampling_rate != 500:
        num_samples = int(ecg_signal.shape[1] * 500 / sampling_rate)
        ecg_resampled = signal.resample(ecg_signal, num_samples, axis=1)
    else:
        ecg_resampled = ecg_signal
    
    # 2. 带通滤波 (0.5-40Hz)
    sos = signal.butter(4, [0.5, 40], btype='band', fs=500, output='sos')
    ecg_filtered = signal.sosfilt(sos, ecg_resampled, axis=1)
    
    # 3. 陷波滤波 (50Hz)
    b_notch, a_notch = signal.iirnotch(50, 30, 500)
    ecg_filtered = signal.filtfilt(b_notch, a_notch, ecg_filtered, axis=1)
    
    # 4. 归一化
    ecg_normalized = (ecg_filtered - np.mean(ecg_filtered, axis=1, keepdims=True)) / \
                     (np.std(ecg_filtered, axis=1, keepdims=True) + 1e-8)
    
    # 5. 截取或填充到固定长度 (5000样本 = 10秒)
    target_length = 5000
    if ecg_normalized.shape[1] > target_length:
        ecg_normalized = ecg_normalized[:, :target_length]
    elif ecg_normalized.shape[1] < target_length:
        padding = target_length - ecg_normalized.shape[1]
        ecg_normalized = np.pad(ecg_normalized, ((0, 0), (0, padding)), mode='edge')
    
    # 转置为 (time_steps, channels)
    return ecg_normalized.T

def assess_risk_level(arrhythmia_class: int, confidence: float) -> str:
    """
    评估风险等级
    """
    # 危及生命的心律失常
    critical_arrhythmias = [7]  # 室颤
    high_risk_arrhythmias = [3, 6, 13]  # 房颤、室速、三度AVB
    medium_risk_arrhythmias = [4, 5, 11, 12, 14, 15]  # 房扑、室上速等
    
    if arrhythmia_class in critical_arrhythmias and confidence > 0.7:
        return "critical"
    elif arrhythmia_class in high_risk_arrhythmias and confidence > 0.7:
        return "high"
    elif arrhythmia_class in medium_risk_arrhythmias and confidence > 0.6:
        return "medium"
    else:
        return "low"

def generate_recommendations(arrhythmia_class: int, risk_level: str) -> List[str]:
    """
    生成临床建议
    """
    recommendations = []
    
    if risk_level == "critical":
        recommendations.append("立即启动急救程序")
        recommendations.append("准备除颤器")
        recommendations.append("通知心内科医生")
    elif risk_level == "high":
        recommendations.append("密切监护患者")
        recommendations.append("准备抗心律失常药物")
        recommendations.append("考虑转入ICU")
    elif risk_level == "medium":
        recommendations.append("持续心电监护")
        recommendations.append("评估患者症状")
        recommendations.append("必要时咨询心内科")
    else:
        recommendations.append("继续常规监护")
    
    # 针对特定心律失常的建议
    if arrhythmia_class == 3:  # 房颤
        recommendations.append("评估卒中风险 (CHA2DS2-VASc评分)")
        recommendations.append("考虑抗凝治疗")
    elif arrhythmia_class == 6:  # 室速
        recommendations.append("检查电解质")
        recommendations.append("评估心肌缺血")
    
    return recommendations

async def save_inference_result(result: InferenceResult):
    """
    保存推理结果到数据库
    """
    from database import get_db_connection
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO inference_results 
        (patient_id, device_id, timestamp, primary_diagnosis, confidence, risk_level)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        result.patient_id,
        result.device_id,
        result.timestamp,
        result.primary_diagnosis,
        result.confidence,
        result.risk_level
    ))
    
    conn.commit()
    cursor.close()
    conn.close()

async def trigger_alert(result: InferenceResult):
    """
    触发告警
    """
    from alert_service import send_alert
    
    alert_data = {
        "patient_id": result.patient_id,
        "diagnosis": result.primary_diagnosis,
        "confidence": result.confidence,
        "risk_level": result.risk_level,
        "timestamp": result.timestamp,
        "recommendations": result.recommendations
    }
    
    await send_alert(alert_data)

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "model_loaded": cloud_model is not None,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 实时监护服务

```python
# realtime_monitoring_service.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import asyncio
import json
from datetime import datetime

app = FastAPI()

class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 存储活跃连接: {patient_id: Set[WebSocket]}
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, patient_id: str):
        """建立连接"""
        await websocket.accept()
        
        if patient_id not in self.active_connections:
            self.active_connections[patient_id] = set()
        
        self.active_connections[patient_id].add(websocket)
        print(f"Client connected for patient {patient_id}")
    
    def disconnect(self, websocket: WebSocket, patient_id: str):
        """断开连接"""
        if patient_id in self.active_connections:
            self.active_connections[patient_id].discard(websocket)
            
            if not self.active_connections[patient_id]:
                del self.active_connections[patient_id]
        
        print(f"Client disconnected for patient {patient_id}")
    
    async def broadcast_to_patient(self, patient_id: str, message: dict):
        """向特定患者的所有连接广播消息"""
        if patient_id in self.active_connections:
            disconnected = set()
            
            for connection in self.active_connections[patient_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)
            
            # 清理断开的连接
            for connection in disconnected:
                self.active_connections[patient_id].discard(connection)

manager = ConnectionManager()

@app.websocket("/ws/monitor/{patient_id}")
async def websocket_endpoint(websocket: WebSocket, patient_id: str):
    """
    实时监护WebSocket端点
    """
    await manager.connect(websocket, patient_id)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理不同类型的消息
            if message.get("type") == "heartbeat":
                await websocket.send_json({
                    "type": "heartbeat_ack",
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            elif message.get("type") == "ecg_data":
                # 处理ECG数据
                await process_ecg_data(patient_id, message.get("data"))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, patient_id)

async def process_ecg_data(patient_id: str, ecg_data: dict):
    """
    处理实时ECG数据
    """
    # 1. 执行AI推理
    inference_result = await perform_realtime_inference(ecg_data)
    
    # 2. 广播结果
    await manager.broadcast_to_patient(patient_id, {
        "type": "inference_result",
        "data": inference_result,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # 3. 检查是否需要告警
    if inference_result.get("risk_level") in ["high", "critical"]:
        await manager.broadcast_to_patient(patient_id, {
            "type": "alert",
            "severity": inference_result.get("risk_level"),
            "diagnosis": inference_result.get("primary_diagnosis"),
            "recommendations": inference_result.get("recommendations"),
            "timestamp": datetime.utcnow().isoformat()
        })

async def perform_realtime_inference(ecg_data: dict):
    """
    执行实时推理（简化版）
    """
    # 实际实现中调用推理服务
    return {
        "primary_diagnosis": "正常窦性心律",
        "confidence": 0.95,
        "risk_level": "low"
    }
```

## 法规合规

### IEC 62304 软件生命周期

#### 软件安全分类
- **分类**: Class C (可能导致死亡或严重伤害)
- **理由**: AI算法错误可能导致漏诊或误诊危及生命的心律失常

#### 软件开发计划

```markdown
# CardioAI软件开发计划

## 1. 软件开发过程

### 1.1 需求分析
- 功能需求
  - ECG信号采集 (250Hz, 12导联)
  - 实时AI推理 (<2秒延迟)
  - 17类心律失常识别
  - 智能告警系统
  - 远程监护功能

- 性能需求
  - 推理准确率 >95%
  - 灵敏度 >98% (危及生命的心律失常)
  - 特异性 >90%
  - 推理延迟 <2秒

- 安全需求
  - 数据加密传输 (TLS 1.3)
  - 用户认证和授权
  - 审计日志
  - 故障安全机制

### 1.2 架构设计
- 分层架构
  - 硬件抽象层 (HAL)
  - 信号处理层
  - AI推理层
  - 通信层
  - 应用层

- 关键设计决策
  - 边缘+云端混合架构
  - 模型量化优化
  - 故障检测和恢复机制

### 1.3 详细设计
- 模块设计文档
- 接口规范
- 数据流图
- 状态机图

### 1.4 编码
- 编码标准: MISRA C 2012
- 代码审查流程
- 单元测试覆盖率 >90%

### 1.5 集成测试
- 模块集成测试
- 系统集成测试
- 硬件-软件集成测试

### 1.6 系统测试
- 功能测试
- 性能测试
- 安全测试
- 可用性测试

## 2. 风险管理

### 2.1 风险识别
| 风险ID | 风险描述 | 严重性 | 概率 | 风险等级 |
|--------|----------|--------|------|----------|
| R-001 | AI模型漏诊室颤 | 致命 | 低 | 高 |
| R-002 | AI模型误诊正常为异常 | 中等 | 中 | 中 |
| R-003 | 通信中断导致数据丢失 | 严重 | 低 | 中 |
| R-004 | 电池耗尽导致监护中断 | 严重 | 中 | 高 |

### 2.2 风险控制措施
- R-001: 
  - 多模型集成
  - 人工审核机制
  - 定期模型验证
  
- R-002:
  - 调整决策阈值
  - 提供置信度信息
  - 医生最终判断

- R-003:
  - 本地数据缓存
  - 自动重连机制
  - 离线模式支持

- R-004:
  - 低电量告警
  - 省电模式
  - 充电提醒

## 3. 验证与确认

### 3.1 模型验证
- 数据集: MIT-BIH, PTB-XL, CPSC2018
- 验证指标:
  - 准确率 >95%
  - 灵敏度 >98% (VF, VT)
  - 特异性 >90%
  - F1分数 >0.93

### 3.2 临床验证
- 临床试验设计
- 样本量计算
- 统计分析计划
- 临床终点定义

### 3.3 软件确认
- 需求追溯矩阵
- 测试用例覆盖
- 用户验收测试
```

### FDA软件验证指南

#### 算法验证文档

```markdown
# AI算法验证报告

## 1. 算法描述

### 1.1 算法类型
- 深度学习卷积神经网络 (CNN)
- 架构: ResNet-34变体
- 输入: 12导联ECG信号 (10秒, 500Hz)
- 输出: 17类心律失常概率分布

### 1.2 训练数据
- 数据来源:
  - MIT-BIH Arrhythmia Database: 48例患者
  - PTB-XL Database: 21,837例患者
  - CPSC2018 Database: 6,877例患者
  - 自有数据集: 50,000例患者

- 数据标注:
  - 3名心内科医生独立标注
  - 不一致时由资深专家裁决
  - 标注质量控制流程

- 数据分布:
  - 训练集: 70% (54,000例)
  - 验证集: 15% (11,500例)
  - 测试集: 15% (11,500例)

### 1.3 性能指标

| 心律失常类型 | 灵敏度 | 特异性 | PPV | NPV | F1分数 |
|-------------|--------|--------|-----|-----|--------|
| 正常窦性心律 | 96.2% | 94.8% | 95.1% | 96.0% | 0.956 |
| 房颤 | 97.8% | 96.5% | 94.2% | 98.5% | 0.960 |
| 室颤 | 99.1% | 99.8% | 98.5% | 99.9% | 0.988 |
| 室速 | 98.3% | 97.9% | 95.7% | 99.0% | 0.970 |
| 室性早搏 | 94.5% | 93.2% | 91.8% | 95.3% | 0.931 |
| **平均** | **96.8%** | **96.1%** | **94.9%** | **97.3%** | **0.958** |

## 2. 验证方法

### 2.1 独立测试集验证
- 测试集与训练集完全独立
- 包含不同医院、不同设备的数据
- 覆盖不同年龄、性别、种族

### 2.2 交叉验证
- 5折交叉验证
- 每折包含不同患者
- 确保患者级别的独立性

### 2.3 临床验证
- 前瞻性临床研究
- 300例患者
- 与金标准(心内科医生诊断)对比

## 3. 性能限制

### 3.1 已知限制
- 对于罕见心律失常(发生率<0.1%)性能下降
- 信号质量差时准确率降低
- 起搏器信号可能影响识别

### 3.2 不适用场景
- 严重伪迹干扰
- 电极脱落
- 设备故障

## 4. 持续监控

### 4.1 上市后监控
- 收集真实世界数据
- 定期性能评估
- 模型漂移检测

### 4.2 模型更新
- 更新触发条件
- 重新验证流程
- 监管申报要求
```


## 测试策略

### 单元测试

```python
# test_ecg_preprocessing.py
import unittest
import numpy as np
from ecg_preprocessing import preprocess_ecg, detect_r_peaks

class TestECGPreprocessing(unittest.TestCase):
    
    def setUp(self):
        """测试前准备"""
        # 生成模拟ECG信号
        self.sampling_rate = 250
        self.duration = 10  # 秒
        self.num_samples = self.sampling_rate * self.duration
        
        # 生成正弦波模拟ECG
        t = np.linspace(0, self.duration, self.num_samples)
        self.ecg_signal = np.sin(2 * np.pi * 1.2 * t)  # 72 bpm
    
    def test_preprocess_ecg_output_shape(self):
        """测试预处理输出形状"""
        processed = preprocess_ecg(self.ecg_signal, self.sampling_rate)
        self.assertEqual(processed.shape, (self.num_samples,))
    
    def test_preprocess_ecg_normalization(self):
        """测试归一化"""
        processed = preprocess_ecg(self.ecg_signal, self.sampling_rate)
        self.assertAlmostEqual(np.mean(processed), 0.0, places=1)
        self.assertAlmostEqual(np.std(processed), 1.0, places=1)
    
    def test_detect_r_peaks(self):
        """测试R波检测"""
        # 生成带有明显R波的信号
        t = np.linspace(0, 10, 2500)
        ecg = np.zeros(2500)
        
        # 添加R波 (每秒1.2次 = 72 bpm)
        for i in range(12):
            peak_pos = int(i * 2500 / 12)
            if peak_pos < 2500:
                ecg[peak_pos] = 1.0
        
        peaks = detect_r_peaks(ecg)
        
        # 应该检测到约12个R波
        self.assertGreater(len(peaks), 10)
        self.assertLess(len(peaks), 14)
    
    def test_preprocess_with_noise(self):
        """测试带噪声信号的预处理"""
        # 添加高斯噪声
        noisy_signal = self.ecg_signal + np.random.normal(0, 0.1, self.num_samples)
        
        processed = preprocess_ecg(noisy_signal, self.sampling_rate)
        
        # 预处理后信号应该更平滑
        self.assertLess(np.std(np.diff(processed)), np.std(np.diff(noisy_signal)))

if __name__ == '__main__':
    unittest.main()
```

### 集成测试

```python
# test_ai_inference_integration.py
import unittest
import numpy as np
from ai_inference import AIInferenceEngine
from ecg_preprocessing import preprocess_ecg

class TestAIInferenceIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.inference_engine = AIInferenceEngine('models/ecg_model_quantized.tflite')
    
    def test_end_to_end_inference(self):
        """测试端到端推理流程"""
        # 1. 生成模拟ECG数据
        ecg_signal = self._generate_normal_ecg()
        
        # 2. 预处理
        processed = preprocess_ecg(ecg_signal, 250)
        
        # 3. 推理
        result = self.inference_engine.predict(processed)
        
        # 4. 验证结果
        self.assertIn('rhythm_type', result)
        self.assertIn('confidence', result)
        self.assertGreater(result['confidence'], 0.0)
        self.assertLess(result['confidence'], 1.0)
    
    def test_inference_performance(self):
        """测试推理性能"""
        import time
        
        ecg_signal = self._generate_normal_ecg()
        processed = preprocess_ecg(ecg_signal, 250)
        
        # 测试推理时间
        start_time = time.time()
        for _ in range(100):
            self.inference_engine.predict(processed)
        end_time = time.time()
        
        avg_time = (end_time - start_time) / 100
        
        # 推理时间应小于2秒
        self.assertLess(avg_time, 2.0)
        print(f"Average inference time: {avg_time*1000:.2f}ms")
    
    def test_batch_inference(self):
        """测试批量推理"""
        batch_size = 10
        ecg_batch = [self._generate_normal_ecg() for _ in range(batch_size)]
        
        results = self.inference_engine.predict_batch(ecg_batch)
        
        self.assertEqual(len(results), batch_size)
        for result in results:
            self.assertIn('rhythm_type', result)
    
    def _generate_normal_ecg(self):
        """生成正常ECG信号"""
        t = np.linspace(0, 10, 2500)
        ecg = 0.5 * np.sin(2 * np.pi * 1.2 * t)  # 基础心率
        
        # 添加P波、QRS波群、T波
        for i in range(12):
            beat_time = i / 1.2
            if beat_time < 10:
                # P波
                p_wave = 0.1 * np.exp(-((t - beat_time + 0.15)**2) / 0.001)
                # QRS波群
                qrs_wave = 1.0 * np.exp(-((t - beat_time)**2) / 0.0001)
                # T波
                t_wave = 0.3 * np.exp(-((t - beat_time - 0.2)**2) / 0.002)
                
                ecg += p_wave + qrs_wave + t_wave
        
        return ecg

if __name__ == '__main__':
    unittest.main()
```

### 系统测试

```python
# test_system.py
import unittest
import requests
import websocket
import json
import time

class TestSystemIntegration(unittest.TestCase):
    
    BASE_URL = "http://localhost:8000"
    WS_URL = "ws://localhost:8000"
    
    def test_health_check(self):
        """测试健康检查端点"""
        response = requests.get(f"{self.BASE_URL}/api/v1/health")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
        self.assertTrue(data['model_loaded'])
    
    def test_inference_api(self):
        """测试推理API"""
        # 准备测试数据
        ecg_data = {
            "device_id": "TEST-001",
            "patient_id": "P12345",
            "timestamp": "2024-01-01T00:00:00Z",
            "ecg_signal": [[0.0] * 5000 for _ in range(12)],
            "sampling_rate": 500,
            "duration": 10.0
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/v1/inference",
            json=ecg_data
        )
        
        self.assertEqual(response.status_code, 200)
        
        result = response.json()
        self.assertIn('primary_diagnosis', result)
        self.assertIn('confidence', result)
        self.assertIn('risk_level', result)
    
    def test_websocket_connection(self):
        """测试WebSocket连接"""
        ws = websocket.create_connection(f"{self.WS_URL}/ws/monitor/P12345")
        
        # 发送心跳
        ws.send(json.dumps({"type": "heartbeat"}))
        
        # 接收响应
        response = json.loads(ws.recv())
        self.assertEqual(response['type'], 'heartbeat_ack')
        
        ws.close()
    
    def test_alert_system(self):
        """测试告警系统"""
        # 发送高风险ECG数据
        ecg_data = {
            "device_id": "TEST-001",
            "patient_id": "P12345",
            "timestamp": "2024-01-01T00:00:00Z",
            "ecg_signal": self._generate_vfib_signal(),
            "sampling_rate": 500,
            "duration": 10.0
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/v1/inference",
            json=ecg_data
        )
        
        result = response.json()
        
        # 应该触发高风险告警
        self.assertIn(result['risk_level'], ['high', 'critical'])
    
    def _generate_vfib_signal(self):
        """生成室颤信号"""
        import numpy as np
        
        # 生成随机高频信号模拟室颤
        signal = []
        for _ in range(12):
            lead_signal = np.random.randn(5000) * 0.5
            signal.append(lead_signal.tolist())
        
        return signal

if __name__ == '__main__':
    unittest.main()
```

## 部署与运维

### Docker部署

```dockerfile
# Dockerfile - 云端推理服务
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 下载模型
RUN python download_models.py

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:8000/api/v1/health || exit 1

# 启动应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 推理服务
  inference-service:
    build: ./inference-service
    ports:
      - "8000:8000"
    environment:
      - MODEL_PATH=/models
      - DATABASE_URL=postgresql://user:pass@db:5432/cardioai
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./models:/models
    depends_on:
      - db
      - redis
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
  
  # 实时监护服务
  monitoring-service:
    build: ./monitoring-service
    ports:
      - "8001:8001"
    environment:
      - INFERENCE_SERVICE_URL=http://inference-service:8000
    depends_on:
      - inference-service
  
  # PostgreSQL数据库
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=cardioai
    volumes:
      - postgres-data:/var/lib/postgresql/data
  
  # Redis缓存
  redis:
    image: redis:7-alpine
  
  # Prometheus监控
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
  
  # Grafana可视化
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana
    depends_on:
      - prometheus

volumes:
  postgres-data:
  prometheus-data:
  grafana-data:
```

### Kubernetes部署

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cardioai-inference
  namespace: medical-ai
spec:
  replicas: 5
  selector:
    matchLabels:
      app: cardioai-inference
  template:
    metadata:
      labels:
        app: cardioai-inference
    spec:
      containers:
      - name: inference
        image: cardioai/inference-service:v1.0.0
        ports:
        - containerPort: 8000
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        env:
        - name: MODEL_PATH
          value: "/models"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        volumeMounts:
        - name: models
          mountPath: /models
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: models-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: cardioai-inference-service
  namespace: medical-ai
spec:
  selector:
    app: cardioai-inference
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: cardioai-inference-hpa
  namespace: medical-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: cardioai-inference
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 项目总结

### 关键成果

1. **技术创新**
   - 边缘+云端混合AI架构
   - 模型量化优化，边缘推理<100ms
   - 17类心律失常高精度识别

2. **性能指标**
   - 整体准确率: 96.8%
   - 危及生命心律失常灵敏度: >98%
   - 端到端延迟: <2秒
   - 系统可用性: 99.9%

3. **法规合规**
   - 符合IEC 62304 Class C要求
   - 通过FDA 510(k)审批
   - 符合HIPAA隐私要求
   - 获得CE认证

4. **商业价值**
   - 降低医护人员工作负担60%
   - 提高危急事件响应速度3倍
   - 减少误报率40%
   - 支持远程监护，扩大服务范围

### 经验教训

1. **数据质量至关重要**
   - 高质量标注数据是模型性能的基础
   - 需要多中心、多设备的数据覆盖
   - 持续收集真实世界数据改进模型

2. **边缘计算的价值**
   - 降低延迟，提高响应速度
   - 减少云端成本
   - 提高隐私保护
   - 支持离线场景

3. **可解释性很重要**
   - 医生需要理解AI的决策依据
   - 提供注意力热图等可视化
   - 保留人工审核机制

4. **持续监控和改进**
   - 上市后性能监控
   - 模型漂移检测
   - 定期重新训练和验证

### 未来展望

1. **技术演进**
   - 多模态融合（ECG + 临床数据）
   - 联邦学习保护隐私
   - 持续学习适应新场景
   - 更轻量级的模型架构

2. **功能扩展**
   - 心肌梗死检测
   - 心衰风险预测
   - 个性化治疗建议
   - 药物疗效评估

3. **市场拓展**
   - 家庭远程监护
   - 可穿戴设备集成
   - 基层医疗机构
   - 国际市场

## 参考资源

### 学术论文
1. Hannun, A. Y., et al. (2019). "Cardiologist-level arrhythmia detection and classification in ambulatory electrocardiograms using a deep neural network." Nature Medicine.
2. Ribeiro, A. H., et al. (2020). "Automatic diagnosis of the 12-lead ECG using a deep neural network." Nature Communications.

### 数据集
- MIT-BIH Arrhythmia Database
- PTB-XL ECG Database
- CPSC2018 Challenge Database
- PhysioNet Databases

### 工具和框架
- TensorFlow / PyTorch
- TensorFlow Lite Micro
- CMSIS-NN
- FastAPI
- Docker / Kubernetes

### 法规指南
- IEC 62304: Medical device software lifecycle processes
- FDA Software Validation Guidance
- FDA AI/ML-Based Software as a Medical Device Action Plan
- ISO 13485: Medical devices quality management systems

---

**案例完成日期**: 2026年2月10日  
**文档版本**: v1.0  
**作者**: Medical AI Development Team
