---
title: 数字滤波器
description: 掌握医疗器械中常用的数字滤波技术，包括FIR和IIR滤波器的设计与实现
difficulty: 高级
estimated_time: 60分钟
tags:
- 数字滤波
- FIR滤波器
- IIR滤波器
- 信号处理
- 噪声抑制
related_modules:
- zh/technical-knowledge/signal-processing
- zh/technical-knowledge/hardware-interfaces/adc-dac
- zh/technical-knowledge/embedded-c-cpp/memory-management
last_updated: '2026-02-09'
version: '1.0'
language: zh
---

# 数字滤波器

## 学习目标

完成本模块后，你将能够：
- 理解数字滤波器的基本原理和分类
- 掌握FIR滤波器的设计和实现
- 掌握IIR滤波器的设计和实现
- 选择合适的滤波器类型和参数
- 在嵌入式系统中高效实现数字滤波器
- 在医疗器械中应用数字滤波技术

## 前置知识

- 信号处理基础
- 数字信号处理理论
- C语言编程
- 定点数运算
- ADC/DAC原理

## 内容

### 概念介绍

数字滤波器是医疗器械信号处理的核心技术，用于去除噪声、提取特征信号、抑制干扰。与模拟滤波器相比，数字滤波器具有精度高、稳定性好、易于调整等优点。

**数字滤波器的应用**：
- **心电信号处理**：去除工频干扰、基线漂移
- **血氧信号处理**：去除运动伪影、环境光干扰
- **血压信号处理**：平滑脉搏波形
- **脑电信号处理**：提取特定频段的脑电波
- **超声信号处理**：去除噪声、增强对比度


### 数字滤波器分类

#### 按脉冲响应分类

1. **FIR滤波器（Finite Impulse Response）**
   - 有限脉冲响应
   - 线性相位特性
   - 稳定性好
   - 计算量较大

2. **IIR滤波器（Infinite Impulse Response）**
   - 无限脉冲响应
   - 非线性相位
   - 计算效率高
   - 可能不稳定

#### 按频率特性分类

- **低通滤波器（LPF）**：通过低频，抑制高频
- **高通滤波器（HPF）**：通过高频，抑制低频
- **带通滤波器（BPF）**：通过特定频段
- **带阻滤波器（BSF）**：抑制特定频段

### FIR滤波器

#### FIR滤波器原理

FIR滤波器的差分方程：

```
y[n] = b₀×x[n] + b₁×x[n-1] + b₂×x[n-2] + ... + bₙ×x[n-N]
```

其中：
- y[n]：输出信号
- x[n]：输入信号
- b₀, b₁, ..., bₙ：滤波器系数
- N：滤波器阶数

#### FIR滤波器实现

```c
// FIR滤波器结构
typedef struct {
    float* coeffs;        // 滤波器系数
    float* buffer;        // 延迟线缓冲区
    uint16_t length;      // 滤波器长度（阶数+1）
    uint16_t index;       // 当前索引
} FIR_Filter_t;

// 初始化FIR滤波器
void FIR_Init(FIR_Filter_t* fir, float* coeffs, uint16_t length) {
    fir->coeffs = coeffs;
    fir->length = length;
    fir->index = 0;
    
    // 分配并清零缓冲区
    fir->buffer = (float*)malloc(length * sizeof(float));
    memset(fir->buffer, 0, length * sizeof(float));
}

// FIR滤波器处理（浮点实现）
float FIR_Process(FIR_Filter_t* fir, float input) {
    float output = 0.0f;
    
    // 将新样本存入缓冲区
    fir->buffer[fir->index] = input;
    
    // 计算输出（卷积）
    uint16_t buf_idx = fir->index;
    for (uint16_t i = 0; i < fir->length; i++) {
        output += fir->coeffs[i] * fir->buffer[buf_idx];
        
        // 循环索引
        if (buf_idx == 0) {
            buf_idx = fir->length - 1;
        } else {
            buf_idx--;
        }
    }
    
    // 更新索引
    fir->index++;
    if (fir->index >= fir->length) {
        fir->index = 0;
    }
    
    return output;
}

// 释放FIR滤波器
void FIR_Free(FIR_Filter_t* fir) {
    if (fir->buffer != NULL) {
        free(fir->buffer);
        fir->buffer = NULL;
    }
}
```

**代码说明**：
- 使用循环缓冲区存储历史样本
- 通过卷积计算输出
- 浮点实现，精度高但计算量大


#### FIR滤波器定点实现

```c
// 定点FIR滤波器（Q15格式）
typedef struct {
    int16_t* coeffs;      // 滤波器系数（Q15）
    int16_t* buffer;      // 延迟线缓冲区（Q15）
    uint16_t length;      // 滤波器长度
    uint16_t index;       // 当前索引
} FIR_Filter_Q15_t;

// 初始化定点FIR滤波器
void FIR_Q15_Init(FIR_Filter_Q15_t* fir, int16_t* coeffs, uint16_t length) {
    fir->coeffs = coeffs;
    fir->length = length;
    fir->index = 0;
    
    fir->buffer = (int16_t*)malloc(length * sizeof(int16_t));
    memset(fir->buffer, 0, length * sizeof(int16_t));
}

// 定点FIR滤波器处理
int16_t FIR_Q15_Process(FIR_Filter_Q15_t* fir, int16_t input) {
    int32_t acc = 0;  // 32位累加器
    
    // 存入新样本
    fir->buffer[fir->index] = input;
    
    // 计算输出
    uint16_t buf_idx = fir->index;
    for (uint16_t i = 0; i < fir->length; i++) {
        // Q15 × Q15 = Q30，需要右移15位得到Q15
        acc += ((int32_t)fir->coeffs[i] * (int32_t)fir->buffer[buf_idx]);
        
        if (buf_idx == 0) {
            buf_idx = fir->length - 1;
        } else {
            buf_idx--;
        }
    }
    
    // 右移15位，从Q30转换为Q15
    int16_t output = (int16_t)(acc >> 15);
    
    // 更新索引
    fir->index++;
    if (fir->index >= fir->length) {
        fir->index = 0;
    }
    
    return output;
}
```

**代码说明**：
- 使用Q15定点格式（16位有符号整数）
- Q15表示范围：-1.0 到 +0.999969482421875
- 乘法结果为Q30，需要右移15位
- 定点运算速度快，适合嵌入式系统

#### 低通FIR滤波器设计示例

```c
// 50Hz低通滤波器（采样率1000Hz，31阶）
// 使用窗函数法设计
const float lpf_50hz_coeffs[31] = {
    -0.0018f, -0.0027f, -0.0025f, -0.0006f,  0.0032f,
     0.0084f,  0.0138f,  0.0176f,  0.0181f,  0.0143f,
     0.0062f, -0.0051f, -0.0171f, -0.0272f, -0.0327f,
    -0.0314f, -0.0220f, -0.0050f,  0.0171f,  0.0416f,
     0.0649f,  0.0832f,  0.0935f,  0.0935f,  0.0832f,
     0.0649f,  0.0416f,  0.0171f, -0.0050f, -0.0220f,
    -0.0314f
};

// 创建50Hz低通滤波器
FIR_Filter_t lpf_50hz;

void Init_LPF_50Hz(void) {
    FIR_Init(&lpf_50hz, (float*)lpf_50hz_coeffs, 31);
}

// 使用示例
float filtered_signal = FIR_Process(&lpf_50hz, raw_signal);
```

**代码说明**：
- 截止频率50Hz，采样率1000Hz
- 31阶滤波器，过渡带较窄
- 系数通过MATLAB或Python设计工具生成


### IIR滤波器

#### IIR滤波器原理

IIR滤波器的差分方程：

```
y[n] = b₀×x[n] + b₁×x[n-1] + ... + bₘ×x[n-M]
       - a₁×y[n-1] - a₂×y[n-2] - ... - aₙ×y[n-N]
```

其中：
- y[n]：输出信号
- x[n]：输入信号
- b₀, b₁, ..., bₘ：前向系数
- a₁, a₂, ..., aₙ：反馈系数

#### 二阶IIR滤波器（Biquad）

二阶IIR滤波器是最常用的IIR滤波器结构，多个二阶节级联可以实现高阶滤波器。

```c
// 二阶IIR滤波器（Biquad）结构
typedef struct {
    float b0, b1, b2;     // 前向系数
    float a1, a2;         // 反馈系数（a0=1）
    float x1, x2;         // 输入历史
    float y1, y2;         // 输出历史
} Biquad_Filter_t;

// 初始化Biquad滤波器
void Biquad_Init(Biquad_Filter_t* bq, float b0, float b1, float b2, 
                 float a1, float a2) {
    bq->b0 = b0;
    bq->b1 = b1;
    bq->b2 = b2;
    bq->a1 = a1;
    bq->a2 = a2;
    
    // 清零历史
    bq->x1 = 0.0f;
    bq->x2 = 0.0f;
    bq->y1 = 0.0f;
    bq->y2 = 0.0f;
}

// Biquad滤波器处理（Direct Form I）
float Biquad_Process(Biquad_Filter_t* bq, float input) {
    // 计算输出
    float output = bq->b0 * input + bq->b1 * bq->x1 + bq->b2 * bq->x2
                   - bq->a1 * bq->y1 - bq->a2 * bq->y2;
    
    // 更新历史
    bq->x2 = bq->x1;
    bq->x1 = input;
    bq->y2 = bq->y1;
    bq->y1 = output;
    
    return output;
}

// Biquad滤波器处理（Direct Form II，更节省内存）
float Biquad_Process_DF2(Biquad_Filter_t* bq, float input) {
    // Direct Form II只需要2个状态变量
    float w = input - bq->a1 * bq->x1 - bq->a2 * bq->x2;
    float output = bq->b0 * w + bq->b1 * bq->x1 + bq->b2 * bq->x2;
    
    // 更新状态
    bq->x2 = bq->x1;
    bq->x1 = w;
    
    return output;
}
```

**代码说明**：
- Direct Form I：直观，但需要4个状态变量
- Direct Form II：节省内存，只需2个状态变量
- 二阶节稳定性好，易于实现

#### 巴特沃斯低通滤波器

```c
// 巴特沃斯低通滤波器（2阶，截止频率50Hz，采样率1000Hz）
void Init_Butterworth_LPF_50Hz(Biquad_Filter_t* bq) {
    // 系数通过设计工具计算
    float b0 = 0.0201f;
    float b1 = 0.0402f;
    float b2 = 0.0201f;
    float a1 = -1.5610f;
    float a2 = 0.6414f;
    
    Biquad_Init(bq, b0, b1, b2, a1, a2);
}

// 使用示例
Biquad_Filter_t butterworth_lpf;
Init_Butterworth_LPF_50Hz(&butterworth_lpf);

float filtered = Biquad_Process(&butterworth_lpf, raw_signal);
```

**代码说明**：
- 巴特沃斯滤波器：通带平坦，过渡带平滑
- 2阶滤波器计算量小，适合实时处理
- 系数通过MATLAB或Python计算


#### 陷波滤波器（Notch Filter）

陷波滤波器用于抑制特定频率的干扰，如50Hz/60Hz工频干扰。

```c
// 50Hz陷波滤波器（采样率1000Hz，Q=30）
void Init_Notch_50Hz(Biquad_Filter_t* bq) {
    float fs = 1000.0f;   // 采样率
    float f0 = 50.0f;     // 陷波频率
    float Q = 30.0f;      // 品质因数（Q越大，陷波越窄）
    
    // 计算中间变量
    float w0 = 2.0f * M_PI * f0 / fs;
    float alpha = sinf(w0) / (2.0f * Q);
    
    // 计算系数
    float b0 = 1.0f;
    float b1 = -2.0f * cosf(w0);
    float b2 = 1.0f;
    float a0 = 1.0f + alpha;
    float a1 = -2.0f * cosf(w0);
    float a2 = 1.0f - alpha;
    
    // 归一化
    b0 /= a0;
    b1 /= a0;
    b2 /= a0;
    a1 /= a0;
    a2 /= a0;
    
    Biquad_Init(bq, b0, b1, b2, a1, a2);
}

// 使用示例：去除心电信号中的50Hz工频干扰
Biquad_Filter_t notch_50hz;
Init_Notch_50Hz(&notch_50hz);

float ecg_filtered = Biquad_Process(&notch_50hz, ecg_raw);
```

**代码说明**：
- 陷波滤波器在特定频率处衰减最大
- Q值越大，陷波越窄，对其他频率影响越小
- 常用于去除工频干扰

### 移动平均滤波器

移动平均滤波器是最简单的低通滤波器，计算效率高。

```c
// 移动平均滤波器
typedef struct {
    int16_t* buffer;
    uint16_t length;
    uint16_t index;
    int32_t sum;
} MovingAverage_t;

// 初始化移动平均滤波器
void MovingAverage_Init(MovingAverage_t* ma, uint16_t length) {
    ma->length = length;
    ma->index = 0;
    ma->sum = 0;
    
    ma->buffer = (int16_t*)malloc(length * sizeof(int16_t));
    memset(ma->buffer, 0, length * sizeof(int16_t));
}

// 移动平均滤波器处理
int16_t MovingAverage_Process(MovingAverage_t* ma, int16_t input) {
    // 减去最旧的样本
    ma->sum -= ma->buffer[ma->index];
    
    // 加上新样本
    ma->buffer[ma->index] = input;
    ma->sum += input;
    
    // 更新索引
    ma->index++;
    if (ma->index >= ma->length) {
        ma->index = 0;
    }
    
    // 返回平均值
    return (int16_t)(ma->sum / ma->length);
}

// 优化版本：长度为2的幂次，使用位移代替除法
int16_t MovingAverage_Process_Fast(MovingAverage_t* ma, int16_t input) {
    // 假设length = 16 (2^4)
    ma->sum -= ma->buffer[ma->index];
    ma->buffer[ma->index] = input;
    ma->sum += input;
    
    ma->index = (ma->index + 1) & 0x0F;  // 等价于 % 16
    
    return (int16_t)(ma->sum >> 4);  // 等价于 / 16
}
```

**代码说明**：
- 移动平均滤波器计算简单，适合实时处理
- 使用累加和，避免重复计算
- 长度为2的幂次时，可以使用位运算优化


### 医疗器械滤波应用

#### 心电信号滤波

```c
// 心电信号滤波器组
typedef struct {
    Biquad_Filter_t notch_50hz;    // 50Hz陷波（工频干扰）
    Biquad_Filter_t hpf_05hz;      // 0.5Hz高通（基线漂移）
    Biquad_Filter_t lpf_40hz;      // 40Hz低通（高频噪声）
} ECG_FilterBank_t;

ECG_FilterBank_t ecg_filters;

// 初始化心电滤波器组
void ECG_FilterBank_Init(ECG_FilterBank_t* fb) {
    // 50Hz陷波滤波器
    Init_Notch_50Hz(&fb->notch_50hz);
    
    // 0.5Hz高通滤波器（去除基线漂移）
    float b0_hp = 0.9899f;
    float b1_hp = -1.9799f;
    float b2_hp = 0.9899f;
    float a1_hp = -1.9798f;
    float a2_hp = 0.9798f;
    Biquad_Init(&fb->hpf_05hz, b0_hp, b1_hp, b2_hp, a1_hp, a2_hp);
    
    // 40Hz低通滤波器（去除高频噪声）
    float b0_lp = 0.0675f;
    float b1_lp = 0.1349f;
    float b2_lp = 0.0675f;
    float a1_lp = -1.1430f;
    float a2_lp = 0.4128f;
    Biquad_Init(&fb->lpf_40hz, b0_lp, b1_lp, b2_lp, a1_lp, a2_lp);
}

// 心电信号滤波处理
float ECG_Filter_Process(ECG_FilterBank_t* fb, float ecg_raw) {
    float signal = ecg_raw;
    
    // 级联滤波
    signal = Biquad_Process(&fb->hpf_05hz, signal);   // 去基线漂移
    signal = Biquad_Process(&fb->notch_50hz, signal); // 去工频干扰
    signal = Biquad_Process(&fb->lpf_40hz, signal);   // 去高频噪声
    
    return signal;
}

// 使用示例
void ECG_Processing_Task(void) {
    // 从ADC读取原始心电信号
    float ecg_raw = ADC_ReadECG();
    
    // 滤波处理
    float ecg_filtered = ECG_Filter_Process(&ecg_filters, ecg_raw);
    
    // 后续处理（QRS检测等）
    ECG_QRS_Detection(ecg_filtered);
}
```

**代码说明**：
- 级联多个滤波器，分别处理不同类型的干扰
- 高通滤波器去除基线漂移
- 陷波滤波器去除工频干扰
- 低通滤波器去除高频噪声

#### 血氧信号滤波

```c
// 血氧信号滤波器
typedef struct {
    Biquad_Filter_t lpf_5hz;       // 5Hz低通（平滑脉搏波）
    MovingAverage_t ma_dc;         // DC分量提取
} SpO2_Filter_t;

SpO2_Filter_t spo2_filter;

// 初始化血氧滤波器
void SpO2_Filter_Init(SpO2_Filter_t* sf) {
    // 5Hz低通滤波器
    float b0 = 0.0013f;
    float b1 = 0.0025f;
    float b2 = 0.0013f;
    float a1 = -1.8226f;
    float a2 = 0.8278f;
    Biquad_Init(&sf->lpf_5hz, b0, b1, b2, a1, a2);
    
    // 移动平均滤波器（提取DC分量）
    MovingAverage_Init(&sf->ma_dc, 64);
}

// 血氧信号处理
void SpO2_Process(SpO2_Filter_t* sf, float red_raw, float ir_raw) {
    // 低通滤波
    float red_ac = Biquad_Process(&sf->lpf_5hz, red_raw);
    float ir_ac = Biquad_Process(&sf->lpf_5hz, ir_raw);
    
    // 提取DC分量
    float red_dc = MovingAverage_Process(&sf->ma_dc, (int16_t)red_raw);
    float ir_dc = MovingAverage_Process(&sf->ma_dc, (int16_t)ir_raw);
    
    // 计算AC/DC比值
    float ratio = (red_ac / red_dc) / (ir_ac / ir_dc);
    
    // 根据比值计算SpO2
    float spo2 = 110.0f - 25.0f * ratio;
    
    // 限制范围
    if (spo2 > 100.0f) spo2 = 100.0f;
    if (spo2 < 0.0f) spo2 = 0.0f;
}
```

**代码说明**：
- 低通滤波器提取AC分量（脉搏波动）
- 移动平均滤波器提取DC分量（平均光强）
- AC/DC比值用于计算血氧饱和度


### 滤波器设计工具

#### 使用Python设计滤波器

```python
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# 设计FIR低通滤波器
def design_fir_lpf(cutoff_hz, fs_hz, numtaps=31):
    """
    设计FIR低通滤波器
    cutoff_hz: 截止频率（Hz）
    fs_hz: 采样率（Hz）
    numtaps: 滤波器阶数+1
    """
    # 归一化截止频率
    nyquist = fs_hz / 2.0
    cutoff_norm = cutoff_hz / nyquist
    
    # 使用窗函数法设计
    coeffs = signal.firwin(numtaps, cutoff_norm, window='hamming')
    
    return coeffs

# 设计IIR巴特沃斯低通滤波器
def design_butterworth_lpf(cutoff_hz, fs_hz, order=2):
    """
    设计IIR巴特沃斯低通滤波器
    cutoff_hz: 截止频率（Hz）
    fs_hz: 采样率（Hz）
    order: 滤波器阶数
    """
    # 归一化截止频率
    nyquist = fs_hz / 2.0
    cutoff_norm = cutoff_hz / nyquist
    
    # 设计滤波器
    b, a = signal.butter(order, cutoff_norm, btype='low')
    
    # 转换为二阶节（SOS）形式
    sos = signal.butter(order, cutoff_norm, btype='low', output='sos')
    
    return b, a, sos

# 设计陷波滤波器
def design_notch_filter(f0_hz, fs_hz, Q=30):
    """
    设计陷波滤波器
    f0_hz: 陷波频率（Hz）
    fs_hz: 采样率（Hz）
    Q: 品质因数
    """
    # 归一化频率
    w0 = f0_hz / (fs_hz / 2.0)
    
    # 设计陷波滤波器
    b, a = signal.iirnotch(w0, Q)
    
    return b, a

# 生成C代码
def generate_c_code(coeffs, name):
    """生成C语言数组定义"""
    print(f"const float {name}[{len(coeffs)}] = {{")
    for i in range(0, len(coeffs), 5):
        line = "    "
        for j in range(5):
            if i + j < len(coeffs):
                line += f"{coeffs[i+j]:8.4f}f, "
        print(line)
    print("};")

# 示例：设计50Hz低通滤波器
fs = 1000  # 采样率1000Hz
cutoff = 50  # 截止频率50Hz

# FIR滤波器
fir_coeffs = design_fir_lpf(cutoff, fs, numtaps=31)
print("FIR Low-Pass Filter Coefficients:")
generate_c_code(fir_coeffs, "lpf_50hz_coeffs")

# IIR滤波器
b, a, sos = design_butterworth_lpf(cutoff, fs, order=2)
print("\nIIR Butterworth Filter Coefficients:")
print(f"b0={b[0]:.4f}, b1={b[1]:.4f}, b2={b[2]:.4f}")
print(f"a0={a[0]:.4f}, a1={a[1]:.4f}, a2={a[2]:.4f}")
```

**代码说明**：
- 使用scipy.signal库设计滤波器
- 自动生成C语言代码
- 支持FIR和IIR滤波器设计

### 性能优化

#### 使用CMSIS-DSP库

```c
#include "arm_math.h"

// 使用CMSIS-DSP的FIR滤波器
arm_fir_instance_f32 fir_instance;
float fir_state[31 + 1 - 1];  // 状态缓冲区
float fir_coeffs[31];          // 滤波器系数

// 初始化
void Init_CMSIS_FIR(void) {
    arm_fir_init_f32(&fir_instance, 31, fir_coeffs, fir_state, 1);
}

// 处理
void Process_CMSIS_FIR(float* input, float* output, uint32_t blockSize) {
    arm_fir_f32(&fir_instance, input, output, blockSize);
}

// 使用CMSIS-DSP的Biquad滤波器
arm_biquad_casd_df1_inst_f32 biquad_instance;
float biquad_state[4];  // 2阶滤波器需要4个状态
float biquad_coeffs[5]; // b0, b1, b2, a1, a2

// 初始化
void Init_CMSIS_Biquad(void) {
    arm_biquad_cascade_df1_init_f32(&biquad_instance, 1, 
                                     biquad_coeffs, biquad_state);
}

// 处理
void Process_CMSIS_Biquad(float* input, float* output, uint32_t blockSize) {
    arm_biquad_cascade_df1_f32(&biquad_instance, input, output, blockSize);
}
```

**代码说明**：
- CMSIS-DSP库提供优化的DSP函数
- 利用ARM Cortex-M的DSP指令
- 性能比普通C代码快2-10倍


### 最佳实践

!!! tip "数字滤波器设计最佳实践"
    - **选择合适的滤波器类型**：FIR线性相位，IIR计算效率高
    - **合理设计参数**：截止频率、阶数、采样率等
    - **使用设计工具**：MATLAB、Python等工具辅助设计
    - **定点实现**：嵌入式系统优先使用定点运算
    - **使用优化库**：CMSIS-DSP等优化库提高性能
    - **级联设计**：复杂滤波器可以级联多个简单滤波器
    - **测试验证**：使用实际信号测试滤波效果
    - **考虑延迟**：FIR滤波器有固定延迟，需要考虑实时性
    - **稳定性检查**：IIR滤波器需要检查极点位置，确保稳定
    - **量化误差**：定点实现需要考虑量化误差和溢出

### 常见陷阱

!!! warning "注意事项"
    - **系数精度不足**：定点实现时系数量化误差大
    - **溢出问题**：累加器溢出导致结果错误
    - **不稳定的IIR**：极点在单位圆外，滤波器不稳定
    - **过高的阶数**：计算量大，实时性差
    - **采样率不足**：违反奈奎斯特定理，产生混叠
    - **初始化错误**：历史状态未清零，产生瞬态响应
    - **相位失真**：IIR滤波器非线性相位，可能影响波形
    - **边界效应**：滤波器启动时的瞬态响应
    - **数值精度**：浮点运算精度问题
    - **内存泄漏**：动态分配的缓冲区未释放

## 实践练习

1. **FIR滤波器设计**：设计并实现一个50Hz低通FIR滤波器
2. **IIR滤波器设计**：设计并实现一个50Hz陷波IIR滤波器
3. **心电信号滤波**：实现完整的心电信号滤波器组
4. **性能优化**：使用CMSIS-DSP库优化滤波器性能
5. **定点实现**：将浮点滤波器转换为定点实现

## 自测问题

??? question "FIR和IIR滤波器有什么区别？如何选择？"
    FIR和IIR滤波器各有优缺点，需要根据应用场景选择。
    
    ??? success "答案"
        **主要区别**：
        
        | 特性 | FIR滤波器 | IIR滤波器 |
        |------|-----------|-----------|
        | 脉冲响应 | 有限 | 无限 |
        | 相位特性 | 线性相位 | 非线性相位 |
        | 稳定性 | 总是稳定 | 可能不稳定 |
        | 计算量 | 较大 | 较小 |
        | 延迟 | 固定延迟 | 延迟较小 |
        | 设计难度 | 简单 | 较复杂 |
        
        **选择建议**：
        
        1. **选择FIR的场景**：
           - 需要线性相位（如音频处理）
           - 稳定性要求高
           - 计算资源充足
           - 可以接受较大延迟
        
        2. **选择IIR的场景**：
           - 计算资源有限
           - 需要陡峭的过渡带
           - 实时性要求高
           - 不关心相位失真
        
        3. **医疗器械应用**：
           - 心电信号：IIR（实时性要求高）
           - 音频信号：FIR（需要线性相位）
           - 血氧信号：IIR（计算简单）
           - 脑电信号：根据具体需求选择

??? question "如何设计一个50Hz陷波滤波器去除工频干扰？"
    陷波滤波器用于抑制特定频率的干扰。
    
    ??? success "答案"
        **设计步骤**：
        
        1. **确定参数**：
           - 陷波频率：f0 = 50Hz（或60Hz）
           - 采样率：fs = 1000Hz
           - 品质因数：Q = 30（Q越大，陷波越窄）
        
        2. **计算系数**：
           ```
           w0 = 2π × f0 / fs
           α = sin(w0) / (2Q)
           
           b0 = 1
           b1 = -2 × cos(w0)
           b2 = 1
           a0 = 1 + α
           a1 = -2 × cos(w0)
           a2 = 1 - α
           
           归一化：除以a0
           ```
        
        3. **实现代码**：
           ```c
           void Init_Notch_50Hz(Biquad_Filter_t* bq) {
               float fs = 1000.0f;
               float f0 = 50.0f;
               float Q = 30.0f;
               
               float w0 = 2.0f * M_PI * f0 / fs;
               float alpha = sinf(w0) / (2.0f * Q);
               
               float b0 = 1.0f;
               float b1 = -2.0f * cosf(w0);
               float b2 = 1.0f;
               float a0 = 1.0f + alpha;
               float a1 = -2.0f * cosf(w0);
               float a2 = 1.0f - alpha;
               
               b0 /= a0; b1 /= a0; b2 /= a0;
               a1 /= a0; a2 /= a0;
               
               Biquad_Init(bq, b0, b1, b2, a1, a2);
           }
           ```
        
        4. **验证效果**：
           - 在50Hz处衰减应>40dB
           - 其他频率影响应<1dB
           - 使用频谱分析验证
        
        **注意事项**：
        - Q值不宜过大（>50），可能导致不稳定
        - 需要精确的采样率
        - 可以级联多个陷波滤波器（50Hz和100Hz）

??? question "在嵌入式系统中如何优化滤波器性能？"
    嵌入式系统资源有限，需要优化滤波器实现。
    
    ??? success "答案"
        **优化方法**：
        
        1. **使用定点运算**：
           - 浮点运算慢，定点运算快
           - 使用Q15或Q31格式
           - 注意溢出和精度
           
           ```c
           // Q15定点乘法
           int16_t q15_mult(int16_t a, int16_t b) {
               return (int16_t)(((int32_t)a * b) >> 15);
           }
           ```
        
        2. **使用CMSIS-DSP库**：
           - ARM官方优化的DSP库
           - 利用SIMD指令
           - 性能提升2-10倍
           
           ```c
           #include "arm_math.h"
           arm_fir_f32(&fir_instance, input, output, blockSize);
           ```
        
        3. **降低滤波器阶数**：
           - 使用IIR代替高阶FIR
           - 级联多个低阶滤波器
           - 权衡性能和精度
        
        4. **批量处理**：
           - 一次处理多个样本
           - 减少函数调用开销
           - 提高缓存命中率
        
        5. **使用DMA**：
           - DMA传输ADC数据
           - CPU可以处理其他任务
           - 降低CPU负载
        
        6. **优化数据结构**：
           - 使用循环缓冲区
           - 避免数据搬移
           - 内存对齐
        
        7. **编译器优化**：
           - 使用-O2或-O3优化级别
           - 使用inline函数
           - 循环展开
        
        **性能对比**：
        - 浮点FIR（31阶）：~1000 cycles
        - 定点FIR（31阶）：~500 cycles
        - CMSIS FIR（31阶）：~200 cycles
        - IIR（2阶）：~50 cycles

??? question "如何处理滤波器的初始瞬态响应？"
    滤波器启动时会有瞬态响应，可能影响结果。
    
    ??? success "答案"
        **瞬态响应问题**：
        
        1. **产生原因**：
           - 滤波器历史状态为零
           - 输入信号突变
           - 初始条件不匹配
        
        2. **影响**：
           - 输出信号初期失真
           - 可能触发误报警
           - 影响测量精度
        
        **处理方法**：
        
        1. **预填充历史**：
           ```c
           void FIR_Prefill(FIR_Filter_t* fir, float initial_value) {
               for (int i = 0; i < fir->length; i++) {
                   fir->buffer[i] = initial_value;
               }
           }
           ```
        
        2. **丢弃初始样本**：
           ```c
           // 丢弃前N个样本
           for (int i = 0; i < fir->length; i++) {
               FIR_Process(fir, input[i]);  // 不使用输出
           }
           
           // 之后的样本才有效
           for (int i = fir->length; i < total_samples; i++) {
               output[i] = FIR_Process(fir, input[i]);
           }
           ```
        
        3. **使用稳态初始化**：
           ```c
           // 使用输入信号的平均值初始化
           float avg = CalculateAverage(input, 100);
           FIR_Prefill(fir, avg);
           ```
        
        4. **渐进启动**：
           ```c
           // 逐渐增加滤波器权重
           float weight = 0.0f;
           for (int i = 0; i < fir->length; i++) {
               weight = (float)i / fir->length;
               output[i] = weight * FIR_Process(fir, input[i]) + 
                          (1.0f - weight) * input[i];
           }
           ```
        
        **医疗器械应用**：
        - 心电监护：丢弃前2秒数据
        - 血氧测量：预填充平均值
        - 血压测量：使用渐进启动

??? question "如何验证滤波器的正确性和性能？"
    滤波器设计完成后需要充分验证。
    
    ??? success "答案"
        **验证方法**：
        
        1. **频率响应测试**：
           - 输入不同频率的正弦波
           - 测量输出幅度和相位
           - 绘制频率响应曲线
           
           ```c
           // 测试频率响应
           for (float freq = 1.0f; freq <= 500.0f; freq += 1.0f) {
               float amplitude = TestFrequencyResponse(filter, freq, fs);
               printf("%.1f Hz: %.2f dB\n", freq, 20*log10(amplitude));
           }
           ```
        
        2. **脉冲响应测试**：
           - 输入单位脉冲
           - 观察输出波形
           - 验证FIR长度和IIR衰减
        
        3. **阶跃响应测试**：
           - 输入阶跃信号
           - 测量上升时间和超调
           - 验证瞬态特性
        
        4. **实际信号测试**：
           - 使用真实的医疗信号
           - 对比滤波前后的效果
           - 验证噪声抑制能力
        
        5. **性能测试**：
           - 测量执行时间
           - 测量内存占用
           - 验证实时性
           
           ```c
           uint32_t start = DWT->CYCCNT;
           float output = FIR_Process(&fir, input);
           uint32_t cycles = DWT->CYCCNT - start;
           ```
        
        6. **稳定性测试**：
           - 长时间运行
           - 极端输入测试
           - 验证无溢出和发散
        
        7. **精度测试**：
           - 对比浮点和定点实现
           - 测量量化误差
           - 验证满足精度要求
        
        **验证工具**：
        - MATLAB/Python：离线分析
        - 示波器：实时波形观察
        - 频谱分析仪：频域分析
        - 逻辑分析仪：时序分析

## 相关资源

- [信号处理基础](index.md)
- [ADC/DAC](../hardware-interfaces/adc-dac.md)
- [内存管理](../embedded-c-cpp/memory-management.md)

## 参考文献

1. "Digital Signal Processing" - John G. Proakis, Dimitris G. Manolakis
2. "The Scientist and Engineer's Guide to Digital Signal Processing" - Steven W. Smith
3. CMSIS-DSP Software Library - ARM
4. IEC 60601-2-27:2011 - Particular requirements for electrocardiographic monitoring equipment
5. "Embedded Signal Processing with the Micro Signal Architecture" - Woon-Seng Gan, Sen M. Kuo

