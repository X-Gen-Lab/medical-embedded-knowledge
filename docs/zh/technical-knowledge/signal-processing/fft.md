---
title: 快速傅里叶变换（FFT）
description: 深入理解FFT算法原理及其在医疗器械信号分析中的应用
difficulty: 高级
estimated_time: 90分钟
tags:
- FFT
- 频域分析
- 信号处理
- 频谱分析
- 医疗信号
related_modules:
- zh/technical-knowledge/signal-processing
- zh/technical-knowledge/signal-processing/digital-filters
- zh/technical-knowledge/signal-processing/ecg-processing
last_updated: '2026-02-09'
version: '1.0'
language: zh
---

# 快速傅里叶变换（FFT）

## 学习目标

完成本模块后，你将能够：
- 理解傅里叶变换和FFT的基本原理
- 掌握FFT算法的实现方法
- 在嵌入式系统中高效实现FFT
- 应用FFT进行医疗信号的频域分析
- 理解FFT在心电、脑电等信号处理中的应用
- 优化FFT算法以适应资源受限的嵌入式环境

## 前置知识

- 复数运算基础
- 信号处理基础理论
- 离散傅里叶变换（DFT）概念
- C语言编程
- 定点数和浮点数运算
- 三角函数和指数函数

## 内容

### 概念介绍

快速傅里叶变换（Fast Fourier Transform, FFT）是一种高效计算离散傅里叶变换（DFT）的算法。
在医疗器械中，FFT是分析生理信号频率成分的核心工具，广泛应用于心电图、脑电图、血氧信号等的频域分析。

**为什么需要FFT？**

1. **频域分析**：将时域信号转换到频域，揭示信号的频率成分
2. **特征提取**：识别特定频率的生理信号（如心率、呼吸率）
3. **噪声识别**：区分有用信号和噪声干扰
4. **功率谱分析**：评估不同频率成分的能量分布
5. **滤波器设计**：辅助设计和验证数字滤波器

**医疗器械中的FFT应用**：

- **心电图（ECG）**：心率变异性分析、频域HRV指标
- **脑电图（EEG）**：脑波频段分析（δ、θ、α、β、γ波）
- **血氧仪（SpO2）**：脉搏波频谱分析
- **血压计**：脉搏波形态分析
- **超声设备**：多普勒频移分析

### 傅里叶变换基础

#### 离散傅里叶变换（DFT）

对于长度为N的离散信号x[n]，其DFT定义为：

```
X[k] = Σ(n=0 to N-1) x[n] × e^(-j2πkn/N)
```

其中：
- x[n]：时域输入信号
- X[k]：频域输出（复数）
- k：频率索引（0 ≤ k < N）
- j：虚数单位
- N：信号长度

**DFT的问题**：
- 计算复杂度：O(N²)
- 对于N=1024的信号，需要约100万次复数乘法
- 在嵌入式系统中实时处理困难

#### FFT算法原理

FFT通过"分治法"将DFT分解为更小的DFT，大幅降低计算复杂度：

- **计算复杂度**：O(N log N)
- **对于N=1024**：仅需约1万次复数乘法（减少100倍）
- **Cooley-Tukey算法**：最常用的FFT算法

**基-2 FFT算法**：

要求信号长度N为2的幂次（N = 2^m），通过递归分解：

```
X[k] = X_even[k] + W_N^k × X_odd[k]
```

其中：
- X_even[k]：偶数索引样本的DFT
- X_odd[k]：奇数索引样本的DFT
- W_N^k = e^(-j2πk/N)：旋转因子

### FFT算法实现

#### 基本数据结构

```c
// 复数结构
typedef struct {
    float real;    // 实部
    float imag;    // 虚部
} Complex_t;

// FFT配置结构
typedef struct {
    uint16_t fft_size;        // FFT点数（必须是2的幂）
    uint16_t log2_size;       // log2(fft_size)
    Complex_t* twiddle;       // 旋转因子表
    uint16_t* bit_reverse;    // 位反转索引表
    float sample_rate;        // 采样率（Hz）
} FFT_Config_t;

// FFT结果结构
typedef struct {
    float* magnitude;         // 幅度谱
    float* phase;            // 相位谱
    float* power;            // 功率谱
    uint16_t size;           // 频点数量
} FFT_Result_t;
```

#### 复数运算函数

```c
// 复数加法
static inline Complex_t complex_add(Complex_t a, Complex_t b) {
    Complex_t result;
    result.real = a.real + b.real;
    result.imag = a.imag + b.imag;
    return result;
}

// 复数减法
static inline Complex_t complex_sub(Complex_t a, Complex_t b) {
    Complex_t result;
    result.real = a.real - b.real;
    result.imag = a.imag - b.imag;
    return result;
}

// 复数乘法
static inline Complex_t complex_mul(Complex_t a, Complex_t b) {
    Complex_t result;
    result.real = a.real * b.real - a.imag * b.imag;
    result.imag = a.real * b.imag + a.imag * b.real;
    return result;
}

// 复数模（幅度）
static inline float complex_magnitude(Complex_t c) {
    return sqrtf(c.real * c.real + c.imag * c.imag);
}

// 复数相位
static inline float complex_phase(Complex_t c) {
    return atan2f(c.imag, c.real);
}
```


#### 位反转排序

FFT算法需要对输入数据进行位反转排序：

```c
// 计算位反转索引
static uint16_t bit_reverse(uint16_t x, uint16_t log2_size) {
    uint16_t result = 0;
    for (uint16_t i = 0; i < log2_size; i++) {
        result = (result << 1) | (x & 1);
        x >>= 1;
    }
    return result;
}

// 生成位反转索引表
void generate_bit_reverse_table(FFT_Config_t* config) {
    uint16_t n = config->fft_size;
    config->bit_reverse = (uint16_t*)malloc(n * sizeof(uint16_t));
    
    for (uint16_t i = 0; i < n; i++) {
        config->bit_reverse[i] = bit_reverse(i, config->log2_size);
    }
}

// 应用位反转排序
void apply_bit_reverse(Complex_t* data, uint16_t* bit_reverse, uint16_t size) {
    for (uint16_t i = 0; i < size; i++) {
        uint16_t j = bit_reverse[i];
        if (i < j) {
            // 交换data[i]和data[j]
            Complex_t temp = data[i];
            data[i] = data[j];
            data[j] = temp;
        }
    }
}
```

#### 旋转因子计算

```c
// 生成旋转因子表（Twiddle Factors）
void generate_twiddle_factors(FFT_Config_t* config) {
    uint16_t n = config->fft_size;
    config->twiddle = (Complex_t*)malloc(n * sizeof(Complex_t));
    
    for (uint16_t k = 0; k < n; k++) {
        float angle = -2.0f * M_PI * k / n;
        config->twiddle[k].real = cosf(angle);
        config->twiddle[k].imag = sinf(angle);
    }
}
```

#### Cooley-Tukey FFT实现

```c
// 基-2 FFT算法（Cooley-Tukey）
void fft_cooley_tukey(Complex_t* data, FFT_Config_t* config) {
    uint16_t n = config->fft_size;
    uint16_t log2_n = config->log2_size;
    
    // 步骤1：位反转排序
    apply_bit_reverse(data, config->bit_reverse, n);
    
    // 步骤2：蝶形运算
    for (uint16_t stage = 1; stage <= log2_n; stage++) {
        uint16_t m = 1 << stage;           // 当前级的DFT大小
        uint16_t m_half = m >> 1;          // m/2
        uint16_t twiddle_step = n / m;     // 旋转因子步长
        
        // 对每个DFT组进行蝶形运算
        for (uint16_t k = 0; k < n; k += m) {
            for (uint16_t j = 0; j < m_half; j++) {
                uint16_t idx_even = k + j;
                uint16_t idx_odd = k + j + m_half;
                uint16_t twiddle_idx = j * twiddle_step;
                
                // 蝶形运算
                Complex_t t = complex_mul(config->twiddle[twiddle_idx], 
                                         data[idx_odd]);
                Complex_t u = data[idx_even];
                
                data[idx_even] = complex_add(u, t);
                data[idx_odd] = complex_sub(u, t);
            }
        }
    }
}
```

#### FFT初始化和执行

```c
// 初始化FFT配置
FFT_Config_t* fft_init(uint16_t fft_size, float sample_rate) {
    // 检查fft_size是否为2的幂
    if ((fft_size & (fft_size - 1)) != 0) {
        return NULL;  // 不是2的幂
    }
    
    FFT_Config_t* config = (FFT_Config_t*)malloc(sizeof(FFT_Config_t));
    config->fft_size = fft_size;
    config->sample_rate = sample_rate;
    
    // 计算log2(fft_size)
    config->log2_size = 0;
    uint16_t temp = fft_size;
    while (temp > 1) {
        temp >>= 1;
        config->log2_size++;
    }
    
    // 生成查找表
    generate_twiddle_factors(config);
    generate_bit_reverse_table(config);
    
    return config;
}

// 执行FFT
void fft_execute(float* input, Complex_t* output, FFT_Config_t* config) {
    uint16_t n = config->fft_size;
    
    // 将实数输入转换为复数
    for (uint16_t i = 0; i < n; i++) {
        output[i].real = input[i];
        output[i].imag = 0.0f;
    }
    
    // 执行FFT
    fft_cooley_tukey(output, config);
}

// 计算幅度谱
void fft_magnitude(Complex_t* fft_output, float* magnitude, uint16_t size) {
    for (uint16_t i = 0; i < size; i++) {
        magnitude[i] = complex_magnitude(fft_output[i]);
    }
}

// 计算功率谱
void fft_power_spectrum(Complex_t* fft_output, float* power, uint16_t size) {
    for (uint16_t i = 0; i < size; i++) {
        float mag = complex_magnitude(fft_output[i]);
        power[i] = mag * mag / size;  // 归一化功率
    }
}

// 释放FFT资源
void fft_free(FFT_Config_t* config) {
    if (config) {
        free(config->twiddle);
        free(config->bit_reverse);
        free(config);
    }
}
```


### 医疗器械中的FFT应用

#### 心率变异性（HRV）分析

```c
// HRV频域分析
typedef struct {
    float vlf_power;    // 极低频功率 (0.003-0.04 Hz)
    float lf_power;     // 低频功率 (0.04-0.15 Hz)
    float hf_power;     // 高频功率 (0.15-0.4 Hz)
    float lf_hf_ratio;  // LF/HF比值
    float total_power;  // 总功率
} HRV_Frequency_t;

// 计算HRV频域指标
void calculate_hrv_frequency(float* rr_intervals, uint16_t count, 
                             float sample_rate, HRV_Frequency_t* result) {
    // 初始化FFT
    uint16_t fft_size = 512;  // 使用512点FFT
    FFT_Config_t* fft_config = fft_init(fft_size, sample_rate);
    
    // 准备输入数据（插值到均匀采样）
    float* uniform_data = (float*)malloc(fft_size * sizeof(float));
    interpolate_rr_intervals(rr_intervals, count, uniform_data, fft_size);
    
    // 应用汉宁窗减少频谱泄漏
    apply_hanning_window(uniform_data, fft_size);
    
    // 执行FFT
    Complex_t* fft_output = (Complex_t*)malloc(fft_size * sizeof(Complex_t));
    fft_execute(uniform_data, fft_output, fft_config);
    
    // 计算功率谱
    float* power_spectrum = (float*)malloc(fft_size * sizeof(float));
    fft_power_spectrum(fft_output, power_spectrum, fft_size);
    
    // 计算频段功率
    float freq_resolution = sample_rate / fft_size;
    
    result->vlf_power = 0.0f;
    result->lf_power = 0.0f;
    result->hf_power = 0.0f;
    result->total_power = 0.0f;
    
    for (uint16_t i = 0; i < fft_size / 2; i++) {
        float freq = i * freq_resolution;
        float power = power_spectrum[i];
        
        if (freq >= 0.003f && freq < 0.04f) {
            result->vlf_power += power;
        } else if (freq >= 0.04f && freq < 0.15f) {
            result->lf_power += power;
        } else if (freq >= 0.15f && freq < 0.4f) {
            result->hf_power += power;
        }
        
        if (freq < 0.4f) {
            result->total_power += power;
        }
    }
    
    // 计算LF/HF比值
    result->lf_hf_ratio = result->lf_power / result->hf_power;
    
    // 清理资源
    free(uniform_data);
    free(fft_output);
    free(power_spectrum);
    fft_free(fft_config);
}

// 汉宁窗函数
void apply_hanning_window(float* data, uint16_t size) {
    for (uint16_t i = 0; i < size; i++) {
        float window = 0.5f * (1.0f - cosf(2.0f * M_PI * i / (size - 1)));
        data[i] *= window;
    }
}
```

#### 脑电图（EEG）频段分析

```c
// EEG频段定义
typedef enum {
    EEG_DELTA = 0,    // δ波: 0.5-4 Hz（深度睡眠）
    EEG_THETA,        // θ波: 4-8 Hz（浅睡眠、冥想）
    EEG_ALPHA,        // α波: 8-13 Hz（放松、闭眼）
    EEG_BETA,         // β波: 13-30 Hz（清醒、思考）
    EEG_GAMMA,        // γ波: 30-100 Hz（高度集中）
    EEG_BAND_COUNT
} EEG_Band_t;

// EEG频段功率结构
typedef struct {
    float band_power[EEG_BAND_COUNT];
    float total_power;
    float relative_power[EEG_BAND_COUNT];  // 相对功率（%）
} EEG_Spectrum_t;

// 分析EEG频谱
void analyze_eeg_spectrum(float* eeg_data, uint16_t size, 
                          float sample_rate, EEG_Spectrum_t* result) {
    // 初始化FFT
    FFT_Config_t* fft_config = fft_init(size, sample_rate);
    
    // 应用汉宁窗
    float* windowed_data = (float*)malloc(size * sizeof(float));
    memcpy(windowed_data, eeg_data, size * sizeof(float));
    apply_hanning_window(windowed_data, size);
    
    // 执行FFT
    Complex_t* fft_output = (Complex_t*)malloc(size * sizeof(Complex_t));
    fft_execute(windowed_data, fft_output, fft_config);
    
    // 计算功率谱
    float* power_spectrum = (float*)malloc(size * sizeof(float));
    fft_power_spectrum(fft_output, power_spectrum, size);
    
    // 初始化频段功率
    for (int i = 0; i < EEG_BAND_COUNT; i++) {
        result->band_power[i] = 0.0f;
    }
    result->total_power = 0.0f;
    
    // 计算各频段功率
    float freq_resolution = sample_rate / size;
    
    for (uint16_t i = 0; i < size / 2; i++) {
        float freq = i * freq_resolution;
        float power = power_spectrum[i];
        
        if (freq >= 0.5f && freq < 4.0f) {
            result->band_power[EEG_DELTA] += power;
        } else if (freq >= 4.0f && freq < 8.0f) {
            result->band_power[EEG_THETA] += power;
        } else if (freq >= 8.0f && freq < 13.0f) {
            result->band_power[EEG_ALPHA] += power;
        } else if (freq >= 13.0f && freq < 30.0f) {
            result->band_power[EEG_BETA] += power;
        } else if (freq >= 30.0f && freq < 100.0f) {
            result->band_power[EEG_GAMMA] += power;
        }
        
        if (freq < 100.0f) {
            result->total_power += power;
        }
    }
    
    // 计算相对功率
    for (int i = 0; i < EEG_BAND_COUNT; i++) {
        result->relative_power[i] = 
            (result->band_power[i] / result->total_power) * 100.0f;
    }
    
    // 清理资源
    free(windowed_data);
    free(fft_output);
    free(power_spectrum);
    fft_free(fft_config);
}
```


### 嵌入式优化技术

#### 定点FFT实现

对于没有FPU的MCU，使用定点数可以显著提高性能：

```c
// 定点复数（Q15格式）
typedef struct {
    int16_t real;    // Q15: -1.0 ~ 0.9999
    int16_t imag;
} Complex_Q15_t;

// Q15乘法
static inline int16_t q15_mul(int16_t a, int16_t b) {
    return (int16_t)(((int32_t)a * b) >> 15);
}

// 定点复数乘法
static inline Complex_Q15_t complex_mul_q15(Complex_Q15_t a, Complex_Q15_t b) {
    Complex_Q15_t result;
    result.real = q15_mul(a.real, b.real) - q15_mul(a.imag, b.imag);
    result.imag = q15_mul(a.real, b.imag) + q15_mul(a.imag, b.real);
    return result;
}

// 定点FFT（基-2）
void fft_q15(Complex_Q15_t* data, uint16_t fft_size, 
             const Complex_Q15_t* twiddle, const uint16_t* bit_reverse) {
    uint16_t log2_n = 0;
    uint16_t temp = fft_size;
    while (temp > 1) {
        temp >>= 1;
        log2_n++;
    }
    
    // 位反转
    for (uint16_t i = 0; i < fft_size; i++) {
        uint16_t j = bit_reverse[i];
        if (i < j) {
            Complex_Q15_t temp = data[i];
            data[i] = data[j];
            data[j] = temp;
        }
    }
    
    // 蝶形运算
    for (uint16_t stage = 1; stage <= log2_n; stage++) {
        uint16_t m = 1 << stage;
        uint16_t m_half = m >> 1;
        uint16_t twiddle_step = fft_size / m;
        
        for (uint16_t k = 0; k < fft_size; k += m) {
            for (uint16_t j = 0; j < m_half; j++) {
                uint16_t idx_even = k + j;
                uint16_t idx_odd = k + j + m_half;
                uint16_t twiddle_idx = j * twiddle_step;
                
                Complex_Q15_t t = complex_mul_q15(twiddle[twiddle_idx], 
                                                  data[idx_odd]);
                Complex_Q15_t u = data[idx_even];
                
                data[idx_even].real = u.real + t.real;
                data[idx_even].imag = u.imag + t.imag;
                data[idx_odd].real = u.real - t.real;
                data[idx_odd].imag = u.imag - t.imag;
            }
        }
    }
}
```

#### 使用CMSIS-DSP库

ARM Cortex-M处理器可以使用高度优化的CMSIS-DSP库：

```c
#include "arm_math.h"

// 使用CMSIS-DSP的FFT
void fft_cmsis_example(float32_t* input, uint16_t fft_size) {
    // 初始化FFT实例
    arm_rfft_fast_instance_f32 fft_instance;
    arm_rfft_fast_init_f32(&fft_instance, fft_size);
    
    // 分配输出缓冲区
    float32_t* fft_output = (float32_t*)malloc(fft_size * sizeof(float32_t));
    
    // 执行实数FFT
    arm_rfft_fast_f32(&fft_instance, input, fft_output, 0);
    
    // 计算幅度
    float32_t* magnitude = (float32_t*)malloc((fft_size/2) * sizeof(float32_t));
    arm_cmplx_mag_f32(fft_output, magnitude, fft_size/2);
    
    // 使用magnitude数据...
    
    free(fft_output);
    free(magnitude);
}

// Q15定点FFT（CMSIS-DSP）
void fft_cmsis_q15_example(int16_t* input, uint16_t fft_size) {
    // 初始化Q15 FFT实例
    arm_rfft_instance_q15 fft_instance;
    arm_rfft_init_q15(&fft_instance, fft_size, 0, 1);
    
    // 分配输出缓冲区
    q15_t* fft_output = (q15_t*)malloc(fft_size * sizeof(q15_t));
    
    // 执行FFT
    arm_rfft_q15(&fft_instance, input, fft_output);
    
    // 计算幅度
    q15_t* magnitude = (q15_t*)malloc((fft_size/2) * sizeof(q15_t));
    arm_cmplx_mag_q15(fft_output, magnitude, fft_size/2);
    
    free(fft_output);
    free(magnitude);
}
```

#### 内存优化

```c
// 原地FFT（节省内存）
void fft_in_place(Complex_t* data, FFT_Config_t* config) {
    // 直接在输入数组上进行FFT运算
    // 不需要额外的输出缓冲区
    fft_cooley_tukey(data, config);
}

// 使用静态缓冲区（避免动态分配）
#define MAX_FFT_SIZE 1024
static Complex_t fft_buffer[MAX_FFT_SIZE];
static float magnitude_buffer[MAX_FFT_SIZE/2];

void fft_static_buffers(float* input, uint16_t size, FFT_Config_t* config) {
    // 使用静态缓冲区
    for (uint16_t i = 0; i < size; i++) {
        fft_buffer[i].real = input[i];
        fft_buffer[i].imag = 0.0f;
    }
    
    fft_cooley_tukey(fft_buffer, config);
    
    for (uint16_t i = 0; i < size/2; i++) {
        magnitude_buffer[i] = complex_magnitude(fft_buffer[i]);
    }
}
```

### 实际应用示例

#### 完整的心电信号频谱分析

```c
// 心电信号频谱分析系统
typedef struct {
    FFT_Config_t* fft_config;
    float* input_buffer;
    Complex_t* fft_output;
    float* magnitude;
    float* power_spectrum;
    uint16_t buffer_size;
    float sample_rate;
} ECG_Spectrum_Analyzer_t;

// 初始化频谱分析器
ECG_Spectrum_Analyzer_t* ecg_spectrum_init(uint16_t fft_size, float sample_rate) {
    ECG_Spectrum_Analyzer_t* analyzer = 
        (ECG_Spectrum_Analyzer_t*)malloc(sizeof(ECG_Spectrum_Analyzer_t));
    
    analyzer->buffer_size = fft_size;
    analyzer->sample_rate = sample_rate;
    
    // 初始化FFT
    analyzer->fft_config = fft_init(fft_size, sample_rate);
    
    // 分配缓冲区
    analyzer->input_buffer = (float*)malloc(fft_size * sizeof(float));
    analyzer->fft_output = (Complex_t*)malloc(fft_size * sizeof(Complex_t));
    analyzer->magnitude = (float*)malloc(fft_size * sizeof(float));
    analyzer->power_spectrum = (float*)malloc(fft_size * sizeof(float));
    
    return analyzer;
}

// 分析心电信号
void ecg_spectrum_analyze(ECG_Spectrum_Analyzer_t* analyzer, 
                          float* ecg_data, uint16_t size) {
    // 复制数据到输入缓冲区
    memcpy(analyzer->input_buffer, ecg_data, size * sizeof(float));
    
    // 应用窗函数
    apply_hanning_window(analyzer->input_buffer, size);
    
    // 执行FFT
    fft_execute(analyzer->input_buffer, analyzer->fft_output, 
                analyzer->fft_config);
    
    // 计算幅度谱和功率谱
    fft_magnitude(analyzer->fft_output, analyzer->magnitude, size);
    fft_power_spectrum(analyzer->fft_output, analyzer->power_spectrum, size);
}

// 查找主频率
float ecg_find_dominant_frequency(ECG_Spectrum_Analyzer_t* analyzer) {
    uint16_t max_idx = 0;
    float max_magnitude = 0.0f;
    
    // 只搜索0.5Hz到5Hz范围（心率范围）
    float freq_resolution = analyzer->sample_rate / analyzer->buffer_size;
    uint16_t start_idx = (uint16_t)(0.5f / freq_resolution);
    uint16_t end_idx = (uint16_t)(5.0f / freq_resolution);
    
    for (uint16_t i = start_idx; i < end_idx; i++) {
        if (analyzer->magnitude[i] > max_magnitude) {
            max_magnitude = analyzer->magnitude[i];
            max_idx = i;
        }
    }
    
    return max_idx * freq_resolution;
}

// 释放资源
void ecg_spectrum_free(ECG_Spectrum_Analyzer_t* analyzer) {
    if (analyzer) {
        fft_free(analyzer->fft_config);
        free(analyzer->input_buffer);
        free(analyzer->fft_output);
        free(analyzer->magnitude);
        free(analyzer->power_spectrum);
        free(analyzer);
    }
}
```


## 最佳实践

### 1. 选择合适的FFT大小

!!! tip "FFT大小选择"
    - **必须是2的幂**：128, 256, 512, 1024, 2048等
    - **权衡频率分辨率和时间分辨率**：
        - 更大的FFT：更好的频率分辨率，但更慢
        - 更小的FFT：更快，但频率分辨率较低
    - **医疗器械常用大小**：
        - ECG分析：512或1024点
        - EEG分析：256或512点
        - 实时应用：128或256点

### 2. 使用窗函数

!!! tip "窗函数的重要性"
    - **减少频谱泄漏**：避免频率成分扩散
    - **常用窗函数**：
        - 汉宁窗（Hanning）：通用，平衡性能
        - 汉明窗（Hamming）：更好的旁瓣抑制
        - 布莱克曼窗（Blackman）：最佳旁瓣抑制，但主瓣较宽
    - **医疗信号推荐**：汉宁窗或汉明窗

### 3. 预处理信号

```c
// 信号预处理流程
void preprocess_for_fft(float* signal, uint16_t size) {
    // 1. 去除直流分量
    float mean = 0.0f;
    for (uint16_t i = 0; i < size; i++) {
        mean += signal[i];
    }
    mean /= size;
    
    for (uint16_t i = 0; i < size; i++) {
        signal[i] -= mean;
    }
    
    // 2. 归一化（可选）
    float max_val = 0.0f;
    for (uint16_t i = 0; i < size; i++) {
        float abs_val = fabsf(signal[i]);
        if (abs_val > max_val) {
            max_val = abs_val;
        }
    }
    
    if (max_val > 0.0f) {
        for (uint16_t i = 0; i < size; i++) {
            signal[i] /= max_val;
        }
    }
}
```

### 4. 频率分辨率计算

```c
// 计算频率分辨率
float calculate_frequency_resolution(float sample_rate, uint16_t fft_size) {
    return sample_rate / fft_size;
}

// 示例：
// 采样率 = 250 Hz
// FFT大小 = 512
// 频率分辨率 = 250 / 512 = 0.488 Hz
```

### 5. 避免混叠

!!! warning "奈奎斯特定理"
    - **采样率必须 ≥ 2倍最高频率**
    - **医疗信号采样率建议**：
        - ECG：250-500 Hz（信号带宽0-150 Hz）
        - EEG：250-1000 Hz（信号带宽0-100 Hz）
        - SpO2：100-200 Hz（脉搏波0-20 Hz）
    - **使用抗混叠滤波器**：在ADC前进行模拟滤波

### 6. 实时处理策略

```c
// 滑动窗口FFT
typedef struct {
    float* circular_buffer;
    uint16_t buffer_size;
    uint16_t write_index;
    uint16_t samples_count;
    FFT_Config_t* fft_config;
} Sliding_FFT_t;

// 添加新样本并执行FFT
void sliding_fft_add_sample(Sliding_FFT_t* sfft, float new_sample) {
    // 添加样本到循环缓冲区
    sfft->circular_buffer[sfft->write_index] = new_sample;
    sfft->write_index = (sfft->write_index + 1) % sfft->buffer_size;
    sfft->samples_count++;
    
    // 当缓冲区满时执行FFT
    if (sfft->samples_count >= sfft->buffer_size) {
        // 重排数据（从最旧的样本开始）
        float* ordered_data = (float*)malloc(sfft->buffer_size * sizeof(float));
        for (uint16_t i = 0; i < sfft->buffer_size; i++) {
            uint16_t idx = (sfft->write_index + i) % sfft->buffer_size;
            ordered_data[i] = sfft->circular_buffer[idx];
        }
        
        // 执行FFT
        Complex_t* fft_output = (Complex_t*)malloc(
            sfft->buffer_size * sizeof(Complex_t));
        fft_execute(ordered_data, fft_output, sfft->fft_config);
        
        // 处理FFT结果...
        
        free(ordered_data);
        free(fft_output);
        
        // 重置计数（可选：使用重叠窗口）
        sfft->samples_count = sfft->buffer_size / 2;  // 50%重叠
    }
}
```

## 常见陷阱

### 1. 忘记位反转排序

!!! danger "错误示例"
    ```c
    // 错误：直接进行蝶形运算，没有位反转
    void fft_wrong(Complex_t* data, uint16_t size) {
        // 缺少位反转步骤！
        for (uint16_t stage = 1; stage <= log2_size; stage++) {
            // 蝶形运算...
        }
    }
    ```

**正确做法**：始终先进行位反转排序

### 2. 频率索引错误

!!! danger "常见错误"
    ```c
    // 错误：使用错误的频率计算
    float freq = k;  // 错误！
    
    // 正确：
    float freq = k * (sample_rate / fft_size);
    ```

### 3. 忽略奈奎斯特频率

!!! warning "频谱对称性"
    - FFT输出的后半部分是前半部分的镜像（共轭对称）
    - 只需要使用前N/2个点
    - 频率范围：0 到 sample_rate/2

```c
// 正确：只使用前半部分
for (uint16_t i = 0; i < fft_size / 2; i++) {
    float freq = i * (sample_rate / fft_size);
    float magnitude = complex_magnitude(fft_output[i]);
    // 处理...
}
```

### 4. 内存泄漏

!!! danger "资源管理"
    ```c
    // 错误：忘记释放资源
    void bad_fft_usage() {
        FFT_Config_t* config = fft_init(512, 250.0f);
        // 使用FFT...
        // 忘记调用fft_free(config)！内存泄漏！
    }
    
    // 正确：
    void good_fft_usage() {
        FFT_Config_t* config = fft_init(512, 250.0f);
        // 使用FFT...
        fft_free(config);  // 释放资源
    }
    ```

### 5. 定点溢出

!!! warning "定点运算注意事项"
    - Q15格式范围：-1.0 到 0.9999
    - 中间结果可能溢出
    - 需要适当的缩放和饱和处理

```c
// 带饱和的Q15加法
static inline int16_t q15_add_sat(int16_t a, int16_t b) {
    int32_t result = (int32_t)a + (int32_t)b;
    if (result > 32767) return 32767;
    if (result < -32768) return -32768;
    return (int16_t)result;
}
```

## 实践练习

### 练习1：实现简单的频谱分析器

编写一个程序，读取心电信号数据，执行FFT，并显示频谱：

```c
void exercise1_spectrum_analyzer() {
    // 1. 生成测试信号（1Hz + 5Hz正弦波）
    uint16_t size = 512;
    float sample_rate = 100.0f;
    float* signal = (float*)malloc(size * sizeof(float));
    
    for (uint16_t i = 0; i < size; i++) {
        float t = i / sample_rate;
        signal[i] = sinf(2.0f * M_PI * 1.0f * t) +  // 1Hz
                   0.5f * sinf(2.0f * M_PI * 5.0f * t);  // 5Hz
    }
    
    // 2. 执行FFT
    FFT_Config_t* config = fft_init(size, sample_rate);
    Complex_t* fft_output = (Complex_t*)malloc(size * sizeof(Complex_t));
    fft_execute(signal, fft_output, config);
    
    // 3. 计算并打印幅度谱
    float* magnitude = (float*)malloc(size * sizeof(float));
    fft_magnitude(fft_output, magnitude, size);
    
    printf("Frequency\tMagnitude\n");
    for (uint16_t i = 0; i < size / 2; i++) {
        float freq = i * (sample_rate / size);
        printf("%.2f Hz\t%.4f\n", freq, magnitude[i]);
    }
    
    // 4. 清理
    free(signal);
    free(fft_output);
    free(magnitude);
    fft_free(config);
}
```

### 练习2：实现HRV分析

基于FFT实现完整的心率变异性频域分析。

### 练习3：优化FFT性能

比较浮点FFT和定点FFT的性能差异，测量执行时间和内存使用。

## 自测问题

??? question "1. 为什么FFT比DFT快？"
    FFT通过分治法将N点DFT分解为多个小规模DFT，将计算复杂度从O(N²)降低到O(N log N)。
    对于N=1024的信号，DFT需要约100万次复数乘法，而FFT只需约1万次，速度提升约100倍。
    
    ??? success "答案"
        FFT利用了DFT计算中的对称性和周期性，通过蝶形运算重复利用中间结果，避免了大量重复计算。

??? question "2. 什么是频率分辨率？如何提高？"
    频率分辨率 = 采样率 / FFT点数。它决定了能够区分的最小频率间隔。
    
    ??? success "答案"
        提高频率分辨率的方法：
        1. 增加FFT点数（需要更多样本）
        2. 降低采样率（但会降低最高可分析频率）
        3. 使用零填充（zero-padding）技术
        4. 使用更长的数据窗口

??? question "3. 为什么需要窗函数？"
    窗函数用于减少频谱泄漏。当信号长度不是周期的整数倍时，FFT会将信号视为周期性的，导致不连续性，
    产生频谱泄漏。
    
    ??? success "答案"        窗函数通过平滑信号边界，减少不连续性，从而减少频谱泄漏。常用的汉宁窗可以将旁瓣抑制到-31dB。

??? question "4. FFT输出的物理意义是什么？"
    FFT输出是复数，包含幅度和相位信息。
    
    ??? success "答案"
        - 幅度：表示该频率成分的强度
        - 相位：表示该频率成分的初始相位
        - 功率谱：幅度的平方，表示能量分布
        - 只需要前N/2个点（奈奎斯特频率以下）

??? question "5. 如何在嵌入式系统中优化FFT？"
    
    ??? success "答案"
        优化策略：
        1. 使用定点运算（Q15格式）代替浮点
        2. 使用CMSIS-DSP等优化库
        3. 预计算旋转因子和位反转表
        4. 使用原地FFT节省内存
        5. 利用硬件加速器（如果可用）
        6. 选择合适的FFT大小（权衡精度和速度）

## 参考文献

1. Cooley, J. W., & Tukey, J. W. (1965). "An algorithm for the machine calculation of complex Fourier series". Mathematics of Computation, 19(90), 297-301.

2. Oppenheim, A. V., & Schafer, R. W. (2009). "Discrete-Time Signal Processing" (3rd ed.). Prentice Hall.

3. ARM Limited. "CMSIS-DSP Software Library". [https://www.keil.com/pack/doc/CMSIS/DSP/html/index.html](https://www.keil.com/pack/doc/CMSIS/DSP/html/index.html)

4. Task Force of the European Society of Cardiology. (1996). "Heart rate variability: standards of measurement, physiological interpretation and clinical use". Circulation, 93(5), 1043-1065.

5. Niedermeyer, E., & da Silva, F. L. (2005). "Electroencephalography: Basic Principles, Clinical Applications, and Related Fields" (5th ed.). Lippincott Williams & Wilkins.

6. Smith, S. W. (1997). "The Scientist and Engineer's Guide to Digital Signal Processing". California Technical Publishing.

## 相关资源

- [数字滤波器](digital-filters.md) - 了解滤波器设计
- [ECG信号处理](ecg-processing.md) - FFT在心电分析中的应用
- [SpO2计算](spo2-calculation.md) - FFT在血氧分析中的应用
- [ADC/DAC](../hardware-interfaces/adc-dac.md) - 信号采集基础
