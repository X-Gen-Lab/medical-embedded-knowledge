---
title: "小波变换（Wavelet Transform）"
description: "小波变换在医疗信号处理中的应用，包括理论基础、实现方法和医疗应用案例"
difficulty: "高级"
estimated_time: "3小时"
tags: ["小波变换", "信号处理", "时频分析", "医疗算法"]
related_modules:
  - zh/technical-knowledge/signal-processing/fft
  - zh/technical-knowledge/signal-processing/ecg-processing
  - zh/technical-knowledge/signal-processing/digital-filters
last_updated: 2026-02-10
version: 1.0
language: zh-CN
---

# 小波变换（Wavelet Transform）

## 📋 学习目标

完成本章学习后，您将能够：

- ✅ 理解小波变换的基本原理和优势
- ✅ 掌握常用小波基函数的特性
- ✅ 实现离散小波变换（DWT）
- ✅ 应用小波变换进行信号去噪和特征提取
- ✅ 在医疗信号处理中应用小波变换

## 前置知识

- 数字信号处理基础
- 傅里叶变换
- C/C++编程
- 基本的线性代数知识

---

## 1. 小波变换基础

### 1.1 什么是小波变换？

小波变换是一种时频分析方法，相比傅里叶变换具有更好的时间-频率局部化特性。

**与傅里叶变换的对比**：

| 特性 | 傅里叶变换 | 小波变换 |
|------|-----------|---------|
| 基函数 | 正弦/余弦波（无限长） | 小波函数（有限长） |
| 时间分辨率 | 无 | 有 |
| 频率分辨率 | 高 | 可变 |
| 适用信号 | 平稳信号 | 非平稳信号 |
| 医疗应用 | 频谱分析 | 瞬态特征检测 |

### 1.2 连续小波变换（CWT）

数学定义：

```
CWT(a,b) = (1/√a) ∫ x(t) ψ*((t-b)/a) dt
```

其中：
- `a`：尺度参数（scale），控制小波的伸缩
- `b`：平移参数（translation），控制小波的位置
- `ψ(t)`：母小波函数
- `*`：复共轭


### 1.3 离散小波变换（DWT）

DWT通过二进尺度离散化实现：

```
a = 2^j, b = k·2^j
```

**优势**：
- 计算效率高
- 适合嵌入式实现
- 完美重构
- 多分辨率分析

---

## 2. 常用小波基函数

### 2.1 Haar小波

**最简单的小波**，适合快速原型开发。

```c
// Haar小波定义
// ψ(t) = { 1,  0 ≤ t < 0.5
//        {-1,  0.5 ≤ t < 1
//        { 0,  其他

typedef struct {
    float low_pass[2];   // [1/√2, 1/√2]
    float high_pass[2];  // [1/√2, -1/√2]
} HaarWavelet;

void haar_wavelet_init(HaarWavelet* wavelet) {
    float sqrt2_inv = 0.7071067811865476f;  // 1/√2
    
    wavelet->low_pass[0] = sqrt2_inv;
    wavelet->low_pass[1] = sqrt2_inv;
    
    wavelet->high_pass[0] = sqrt2_inv;
    wavelet->high_pass[1] = -sqrt2_inv;
}
```

**特点**：
- ✅ 计算简单
- ✅ 内存占用小
- ❌ 不连续，不光滑
- ❌ 频率选择性差

### 2.2 Daubechies小波（dbN）

**最常用的小波族**，平衡了紧支撑和光滑性。

```c
// Daubechies 4 (db4) 小波系数
typedef struct {
    float low_pass[8];
    float high_pass[8];
    uint8_t length;
} Db4Wavelet;

void db4_wavelet_init(Db4Wavelet* wavelet) {
    // db4低通滤波器系数
    wavelet->low_pass[0] = 0.230377813308896f;
    wavelet->low_pass[1] = 0.714846570552915f;
    wavelet->low_pass[2] = 0.630880767929859f;
    wavelet->low_pass[3] = -0.027983769416859f;
    wavelet->low_pass[4] = -0.187034811719092f;
    wavelet->low_pass[5] = 0.030841381835561f;
    wavelet->low_pass[6] = 0.032883011666885f;
    wavelet->low_pass[7] = -0.010597401785069f;
    
    // 高通滤波器系数（QMF关系）
    for (int i = 0; i < 8; i++) {
        int sign = (i % 2 == 0) ? 1 : -1;
        wavelet->high_pass[i] = sign * wavelet->low_pass[7 - i];
    }
    
    wavelet->length = 8;
}
```

**db4特点**：
- ✅ 良好的时频局部化
- ✅ 适合ECG信号
- ✅ 4个消失矩（vanishing moments）
- ✅ 适度的计算复杂度

### 2.3 Symlet小波（symN）

**近似对称的小波**，减少相位失真。

```c
// Symlet 4 (sym4) 小波系数
typedef struct {
    float low_pass[8];
    float high_pass[8];
    uint8_t length;
} Sym4Wavelet;

void sym4_wavelet_init(Sym4Wavelet* wavelet) {
    // sym4低通滤波器系数
    wavelet->low_pass[0] = -0.075765714789273f;
    wavelet->low_pass[1] = -0.029635527645999f;
    wavelet->low_pass[2] = 0.497618667632563f;
    wavelet->low_pass[3] = 0.803738751805386f;
    wavelet->low_pass[4] = 0.297857795605605f;
    wavelet->low_pass[5] = -0.099219543576935f;
    wavelet->low_pass[6] = -0.012603967262037f;
    wavelet->low_pass[7] = 0.032223100604071f;
    
    // 高通滤波器系数
    for (int i = 0; i < 8; i++) {
        int sign = (i % 2 == 0) ? 1 : -1;
        wavelet->high_pass[i] = sign * wavelet->low_pass[7 - i];
    }
    
    wavelet->length = 8;
}
```

**应用场景**：
- 心电信号QRS波检测
- 血压波形分析
- 需要保持波形形状的场合

### 2.4 Coiflet小波（coifN）

**尺度函数和小波函数都近似对称**。

```c
// Coiflet 1 (coif1) 小波系数
typedef struct {
    float low_pass[6];
    float high_pass[6];
    uint8_t length;
} Coif1Wavelet;

void coif1_wavelet_init(Coif1Wavelet* wavelet) {
    wavelet->low_pass[0] = -0.051429728471390f;
    wavelet->low_pass[1] = 0.238929728471390f;
    wavelet->low_pass[2] = 0.602859456942779f;
    wavelet->low_pass[3] = 0.272140543057221f;
    wavelet->low_pass[4] = -0.051429728471390f;
    wavelet->low_pass[5] = -0.011070271528610f;
    
    for (int i = 0; i < 6; i++) {
        int sign = (i % 2 == 0) ? 1 : -1;
        wavelet->high_pass[i] = sign * wavelet->low_pass[5 - i];
    }
    
    wavelet->length = 6;
}
```

---

## 3. 离散小波变换实现

### 3.1 单层DWT分解

使用Mallat算法（快速小波变换）：

```c
#include <stdint.h>
#include <string.h>

// DWT分解结果
typedef struct {
    float* approximation;  // 低频系数（近似）
    float* detail;         // 高频系数（细节）
    uint16_t length;       // 系数长度
} DWTResult;

/**
 * @brief 单层离散小波变换分解
 * @param signal 输入信号
 * @param length 信号长度（必须是2的幂）
 * @param wavelet 小波滤波器
 * @param result 输出结果
 * @return 0成功，-1失败
 */
int dwt_decompose(const float* signal, uint16_t length,
                  const Db4Wavelet* wavelet, DWTResult* result) {
    
    // 参数检查
    if (signal == NULL || wavelet == NULL || result == NULL) {
        return -1;
    }
    
    // 检查长度是否为2的幂
    if ((length & (length - 1)) != 0) {
        return -1;
    }
    
    uint16_t output_length = length / 2;
    result->length = output_length;
    
    // 分配输出缓冲区
    result->approximation = (float*)malloc(output_length * sizeof(float));
    result->detail = (float*)malloc(output_length * sizeof(float));
    
    if (result->approximation == NULL || result->detail == NULL) {
        return -1;
    }
    
    // 卷积和下采样
    for (uint16_t i = 0; i < output_length; i++) {
        float approx_sum = 0.0f;
        float detail_sum = 0.0f;
        
        // 卷积
        for (uint8_t j = 0; j < wavelet->length; j++) {
            uint16_t index = (2 * i + j) % length;  // 循环边界
            approx_sum += signal[index] * wavelet->low_pass[j];
            detail_sum += signal[index] * wavelet->high_pass[j];
        }
        
        result->approximation[i] = approx_sum;
        result->detail[i] = detail_sum;
    }
    
    return 0;
}
```

### 3.2 多层DWT分解

```c
#define MAX_DWT_LEVELS 8

typedef struct {
    float* approximation;              // 最终近似系数
    float* details[MAX_DWT_LEVELS];    // 各层细节系数
    uint16_t detail_lengths[MAX_DWT_LEVELS];
    uint8_t num_levels;                // 分解层数
} MultiLevelDWT;

/**
 * @brief 多层离散小波变换分解
 * @param signal 输入信号
 * @param length 信号长度
 * @param wavelet 小波滤波器
 * @param num_levels 分解层数
 * @param result 输出结果
 * @return 0成功，-1失败
 */
int dwt_multilevel_decompose(const float* signal, uint16_t length,
                              const Db4Wavelet* wavelet, uint8_t num_levels,
                              MultiLevelDWT* result) {
    
    if (num_levels > MAX_DWT_LEVELS) {
        return -1;
    }
    
    result->num_levels = num_levels;
    
    // 临时缓冲区
    float* temp_signal = (float*)malloc(length * sizeof(float));
    memcpy(temp_signal, signal, length * sizeof(float));
    
    uint16_t current_length = length;
    
    // 逐层分解
    for (uint8_t level = 0; level < num_levels; level++) {
        DWTResult level_result;
        
        if (dwt_decompose(temp_signal, current_length, wavelet, &level_result) != 0) {
            free(temp_signal);
            return -1;
        }
        
        // 保存细节系数
        result->details[level] = level_result.detail;
        result->detail_lengths[level] = level_result.length;
        
        // 使用近似系数作为下一层输入
        free(temp_signal);
        temp_signal = level_result.approximation;
        current_length = level_result.length;
    }
    
    // 保存最终近似系数
    result->approximation = temp_signal;
    
    return 0;
}
```


### 3.3 小波重构（IDWT）

```c
/**
 * @brief 单层离散小波逆变换（重构）
 * @param approximation 近似系数
 * @param detail 细节系数
 * @param length 系数长度
 * @param wavelet 小波滤波器
 * @param output 输出信号（长度为2*length）
 * @return 0成功，-1失败
 */
int dwt_reconstruct(const float* approximation, const float* detail,
                    uint16_t length, const Db4Wavelet* wavelet,
                    float* output) {
    
    if (approximation == NULL || detail == NULL || output == NULL) {
        return -1;
    }
    
    uint16_t output_length = length * 2;
    
    // 初始化输出
    memset(output, 0, output_length * sizeof(float));
    
    // 上采样和卷积
    for (uint16_t i = 0; i < length; i++) {
        for (uint8_t j = 0; j < wavelet->length; j++) {
            uint16_t index = (2 * i + j) % output_length;
            
            // 低通重构
            output[index] += approximation[i] * wavelet->low_pass[j];
            
            // 高通重构
            output[index] += detail[i] * wavelet->high_pass[j];
        }
    }
    
    return 0;
}
```

---

## 4. 医疗信号应用

### 4.1 ECG信号去噪

```c
/**
 * @brief 使用小波变换对ECG信号去噪
 * @param ecg_signal 输入ECG信号
 * @param length 信号长度
 * @param threshold 阈值
 * @param denoised_signal 输出去噪信号
 * @return 0成功，-1失败
 */
int ecg_wavelet_denoise(const float* ecg_signal, uint16_t length,
                        float threshold, float* denoised_signal) {
    
    Db4Wavelet wavelet;
    db4_wavelet_init(&wavelet);
    
    // 3层小波分解
    MultiLevelDWT dwt_result;
    if (dwt_multilevel_decompose(ecg_signal, length, &wavelet, 3, &dwt_result) != 0) {
        return -1;
    }
    
    // 软阈值处理细节系数（去除噪声）
    for (uint8_t level = 0; level < dwt_result.num_levels; level++) {
        uint16_t detail_length = dwt_result.detail_lengths[level];
        
        for (uint16_t i = 0; i < detail_length; i++) {
            float coeff = dwt_result.details[level][i];
            
            // 软阈值函数
            if (fabs(coeff) < threshold) {
                dwt_result.details[level][i] = 0.0f;
            } else {
                float sign = (coeff > 0) ? 1.0f : -1.0f;
                dwt_result.details[level][i] = sign * (fabs(coeff) - threshold);
            }
        }
    }
    
    // 重构信号
    // （简化版本，实际需要多层重构）
    float* temp_signal = dwt_result.approximation;
    uint16_t temp_length = dwt_result.detail_lengths[dwt_result.num_levels - 1];
    
    for (int level = dwt_result.num_levels - 1; level >= 0; level--) {
        float* reconstructed = (float*)malloc(temp_length * 2 * sizeof(float));
        
        dwt_reconstruct(temp_signal, dwt_result.details[level],
                       temp_length, &wavelet, reconstructed);
        
        if (level > 0) {
            free(temp_signal);
        }
        temp_signal = reconstructed;
        temp_length *= 2;
    }
    
    memcpy(denoised_signal, temp_signal, length * sizeof(float));
    
    // 清理
    free(temp_signal);
    for (uint8_t i = 0; i < dwt_result.num_levels; i++) {
        free(dwt_result.details[i]);
    }
    
    return 0;
}
```

**阈值选择方法**：

```c
/**
 * @brief 计算通用阈值（Universal Threshold）
 * @param detail_coeffs 细节系数
 * @param length 系数长度
 * @return 阈值
 */
float calculate_universal_threshold(const float* detail_coeffs, uint16_t length) {
    // 估计噪声标准差（使用中位数绝对偏差）
    float* abs_coeffs = (float*)malloc(length * sizeof(float));
    
    for (uint16_t i = 0; i < length; i++) {
        abs_coeffs[i] = fabs(detail_coeffs[i]);
    }
    
    // 计算中位数
    qsort(abs_coeffs, length, sizeof(float), float_compare);
    float median = abs_coeffs[length / 2];
    
    free(abs_coeffs);
    
    // MAD估计
    float sigma = median / 0.6745f;
    
    // 通用阈值
    float threshold = sigma * sqrtf(2.0f * logf((float)length));
    
    return threshold;
}
```

### 4.2 QRS波检测

```c
typedef struct {
    uint16_t* positions;  // QRS波位置
    uint8_t count;        // 检测到的QRS波数量
} QRSDetectionResult;

/**
 * @brief 使用小波变换检测ECG中的QRS波
 * @param ecg_signal 输入ECG信号
 * @param length 信号长度
 * @param sampling_rate 采样率（Hz）
 * @param result 检测结果
 * @return 0成功，-1失败
 */
int detect_qrs_wavelet(const float* ecg_signal, uint16_t length,
                       uint16_t sampling_rate, QRSDetectionResult* result) {
    
    Sym4Wavelet wavelet;
    sym4_wavelet_init(&wavelet);
    
    // 4层小波分解
    MultiLevelDWT dwt_result;
    if (dwt_multilevel_decompose(ecg_signal, length, &wavelet, 4, &dwt_result) != 0) {
        return -1;
    }
    
    // QRS波主要在尺度2^3和2^4（对应8-32Hz）
    float* qrs_feature = dwt_result.details[2];  // 第3层细节
    uint16_t feature_length = dwt_result.detail_lengths[2];
    
    // 计算特征信号的平方
    float* squared_feature = (float*)malloc(feature_length * sizeof(float));
    for (uint16_t i = 0; i < feature_length; i++) {
        squared_feature[i] = qrs_feature[i] * qrs_feature[i];
    }
    
    // 移动平均平滑
    uint16_t window_size = sampling_rate / 40;  // 约25ms窗口
    float* smoothed = (float*)malloc(feature_length * sizeof(float));
    
    for (uint16_t i = 0; i < feature_length; i++) {
        float sum = 0.0f;
        uint16_t count = 0;
        
        for (int j = -window_size/2; j <= window_size/2; j++) {
            int index = i + j;
            if (index >= 0 && index < feature_length) {
                sum += squared_feature[index];
                count++;
            }
        }
        smoothed[i] = sum / count;
    }
    
    // 自适应阈值检测峰值
    float threshold = 0.0f;
    for (uint16_t i = 0; i < feature_length; i++) {
        threshold += smoothed[i];
    }
    threshold = (threshold / feature_length) * 3.0f;  // 3倍平均值
    
    // 峰值检测
    result->positions = (uint16_t*)malloc(100 * sizeof(uint16_t));
    result->count = 0;
    
    uint16_t refractory_period = sampling_rate / 5;  // 200ms不应期
    uint16_t last_detection = 0;
    
    for (uint16_t i = 1; i < feature_length - 1; i++) {
        // 检查是否为局部最大值且超过阈值
        if (smoothed[i] > smoothed[i-1] && 
            smoothed[i] > smoothed[i+1] &&
            smoothed[i] > threshold &&
            (i - last_detection) > refractory_period) {
            
            // 映射回原始信号位置
            result->positions[result->count] = i * 8;  // 2^3下采样
            result->count++;
            last_detection = i;
            
            if (result->count >= 100) break;
        }
    }
    
    // 清理
    free(squared_feature);
    free(smoothed);
    for (uint8_t i = 0; i < dwt_result.num_levels; i++) {
        free(dwt_result.details[i]);
    }
    free(dwt_result.approximation);
    
    return 0;
}
```

### 4.3 血压波形特征提取

```c
typedef struct {
    float systolic_peak;      // 收缩压峰值
    float diastolic_notch;    // 舒张切迹
    float dicrotic_notch;     // 重搏切迹
    uint16_t peak_position;   // 峰值位置
} BPWaveformFeatures;

/**
 * @brief 使用小波变换提取血压波形特征
 * @param bp_signal 血压信号
 * @param length 信号长度
 * @param features 输出特征
 * @return 0成功，-1失败
 */
int extract_bp_features_wavelet(const float* bp_signal, uint16_t length,
                                BPWaveformFeatures* features) {
    
    Coif1Wavelet wavelet;
    coif1_wavelet_init(&wavelet);
    
    // 3层小波分解
    MultiLevelDWT dwt_result;
    if (dwt_multilevel_decompose(bp_signal, length, &wavelet, 3, &dwt_result) != 0) {
        return -1;
    }
    
    // 使用第2层细节系数检测特征点
    float* detail2 = dwt_result.details[1];
    uint16_t detail2_length = dwt_result.detail_lengths[1];
    
    // 查找收缩压峰值（最大正峰）
    float max_value = -1e6f;
    uint16_t max_index = 0;
    
    for (uint16_t i = 0; i < detail2_length; i++) {
        if (detail2[i] > max_value) {
            max_value = detail2[i];
            max_index = i;
        }
    }
    
    features->peak_position = max_index * 4;  // 映射回原始信号
    features->systolic_peak = bp_signal[features->peak_position];
    
    // 在峰值后查找重搏切迹（负峰）
    float min_value = 1e6f;
    uint16_t notch_index = 0;
    
    for (uint16_t i = max_index + 5; i < detail2_length && i < max_index + 30; i++) {
        if (detail2[i] < min_value) {
            min_value = detail2[i];
            notch_index = i;
        }
    }
    
    features->dicrotic_notch = bp_signal[notch_index * 4];
    
    // 清理
    for (uint8_t i = 0; i < dwt_result.num_levels; i++) {
        free(dwt_result.details[i]);
    }
    free(dwt_result.approximation);
    
    return 0;
}
```


---

## 5. 嵌入式优化技术

### 5.1 定点运算实现

```c
// 使用Q15定点格式（1符号位 + 15小数位）
typedef int16_t q15_t;

#define Q15_ONE 32767
#define FLOAT_TO_Q15(x) ((q15_t)((x) * 32768.0f))
#define Q15_TO_FLOAT(x) (((float)(x)) / 32768.0f)

// Q15乘法
static inline q15_t q15_mul(q15_t a, q15_t b) {
    return (q15_t)(((int32_t)a * (int32_t)b) >> 15);
}

// 定点小波变换
typedef struct {
    q15_t low_pass[8];
    q15_t high_pass[8];
    uint8_t length;
} Db4WaveletQ15;

void db4_wavelet_init_q15(Db4WaveletQ15* wavelet) {
    // 将浮点系数转换为Q15
    float low_pass_float[8] = {
        0.230377813308896f, 0.714846570552915f, 0.630880767929859f,
        -0.027983769416859f, -0.187034811719092f, 0.030841381835561f,
        0.032883011666885f, -0.010597401785069f
    };
    
    for (int i = 0; i < 8; i++) {
        wavelet->low_pass[i] = FLOAT_TO_Q15(low_pass_float[i]);
        
        int sign = (i % 2 == 0) ? 1 : -1;
        wavelet->high_pass[i] = sign * wavelet->low_pass[7 - i];
    }
    
    wavelet->length = 8;
}

/**
 * @brief 定点DWT分解
 */
int dwt_decompose_q15(const q15_t* signal, uint16_t length,
                      const Db4WaveletQ15* wavelet,
                      q15_t* approximation, q15_t* detail) {
    
    uint16_t output_length = length / 2;
    
    for (uint16_t i = 0; i < output_length; i++) {
        int32_t approx_sum = 0;
        int32_t detail_sum = 0;
        
        for (uint8_t j = 0; j < wavelet->length; j++) {
            uint16_t index = (2 * i + j) % length;
            
            // Q15乘法累加
            approx_sum += ((int32_t)signal[index] * (int32_t)wavelet->low_pass[j]);
            detail_sum += ((int32_t)signal[index] * (int32_t)wavelet->high_pass[j]);
        }
        
        // 右移15位（Q15乘法结果）
        approximation[i] = (q15_t)(approx_sum >> 15);
        detail[i] = (q15_t)(detail_sum >> 15);
    }
    
    return 0;
}
```

### 5.2 内存优化

```c
/**
 * @brief 原地DWT（节省内存）
 * @note 输入信号会被覆盖
 */
int dwt_decompose_inplace(float* signal, uint16_t length,
                          const Db4Wavelet* wavelet) {
    
    // 使用临时缓冲区（只需要滤波器长度）
    float temp_buffer[8];
    uint16_t output_length = length / 2;
    
    // 分两次处理：先计算近似系数，再计算细节系数
    for (uint16_t i = 0; i < output_length; i++) {
        float approx_sum = 0.0f;
        
        for (uint8_t j = 0; j < wavelet->length; j++) {
            uint16_t index = (2 * i + j) % length;
            approx_sum += signal[index] * wavelet->low_pass[j];
        }
        
        signal[i] = approx_sum;  // 存储在前半部分
    }
    
    // 计算细节系数
    for (uint16_t i = 0; i < output_length; i++) {
        float detail_sum = 0.0f;
        
        for (uint8_t j = 0; j < wavelet->length; j++) {
            uint16_t index = (2 * i + j) % length;
            // 注意：这里需要使用原始信号，但已被覆盖
            // 实际实现需要更复杂的策略
            detail_sum += signal[index] * wavelet->high_pass[j];
        }
        
        signal[output_length + i] = detail_sum;  // 存储在后半部分
    }
    
    return 0;
}
```

### 5.3 SIMD加速（ARM NEON）

```c
#ifdef __ARM_NEON
#include <arm_neon.h>

/**
 * @brief 使用NEON加速的DWT卷积
 */
void dwt_convolve_neon(const float* signal, uint16_t length,
                       const float* filter, uint8_t filter_length,
                       float* output) {
    
    uint16_t output_length = length / 2;
    
    for (uint16_t i = 0; i < output_length; i += 4) {
        // 一次处理4个输出样本
        float32x4_t sum = vdupq_n_f32(0.0f);
        
        for (uint8_t j = 0; j < filter_length; j++) {
            // 加载4个连续的信号样本
            uint16_t index = 2 * i + j;
            float32x4_t sig = vld1q_f32(&signal[index]);
            
            // 广播滤波器系数
            float32x4_t filt = vdupq_n_f32(filter[j]);
            
            // 乘加
            sum = vmlaq_f32(sum, sig, filt);
        }
        
        // 存储结果
        vst1q_f32(&output[i], sum);
    }
}
#endif
```

---

## 6. 实时性能考虑

### 6.1 计算复杂度分析

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| 单层DWT | O(N) | N为信号长度 |
| L层DWT | O(2N) | 总计算量约为2N |
| FFT | O(N log N) | 对比参考 |
| 内存占用 | 2N | 近似+细节系数 |

**示例计算**（1000点ECG信号，250Hz采样）：

```c
// 性能基准测试
typedef struct {
    uint32_t decompose_cycles;
    uint32_t reconstruct_cycles;
    uint32_t denoise_cycles;
} WaveletPerformance;

void benchmark_wavelet_performance(void) {
    const uint16_t signal_length = 1024;
    float test_signal[signal_length];
    
    // 生成测试信号
    for (uint16_t i = 0; i < signal_length; i++) {
        test_signal[i] = sinf(2.0f * M_PI * 10.0f * i / 250.0f);
    }
    
    Db4Wavelet wavelet;
    db4_wavelet_init(&wavelet);
    
    WaveletPerformance perf;
    
    // 测试分解
    uint32_t start = get_cycle_count();
    
    DWTResult result;
    dwt_decompose(test_signal, signal_length, &wavelet, &result);
    
    perf.decompose_cycles = get_cycle_count() - start;
    
    // 测试重构
    start = get_cycle_count();
    
    float reconstructed[signal_length];
    dwt_reconstruct(result.approximation, result.detail,
                   result.length, &wavelet, reconstructed);
    
    perf.reconstruct_cycles = get_cycle_count() - start;
    
    // 测试去噪
    start = get_cycle_count();
    
    float denoised[signal_length];
    ecg_wavelet_denoise(test_signal, signal_length, 0.1f, denoised);
    
    perf.denoise_cycles = get_cycle_count() - start;
    
    // 打印结果
    printf("DWT Performance (1024 points):\n");
    printf("  Decompose: %lu cycles (%.2f ms @ 100MHz)\n",
           perf.decompose_cycles, perf.decompose_cycles / 100000.0f);
    printf("  Reconstruct: %lu cycles (%.2f ms @ 100MHz)\n",
           perf.reconstruct_cycles, perf.reconstruct_cycles / 100000.0f);
    printf("  Denoise: %lu cycles (%.2f ms @ 100MHz)\n",
           perf.denoise_cycles, perf.denoise_cycles / 100000.0f);
    
    // 清理
    free(result.approximation);
    free(result.detail);
}
```

### 6.2 实时处理策略

```c
/**
 * @brief 流式小波变换（适合实时处理）
 */
typedef struct {
    float buffer[16];         // 滑动窗口
    uint8_t buffer_index;     // 当前索引
    Db4Wavelet wavelet;       // 小波滤波器
    float last_approx;        // 上一个近似系数
    float last_detail;        // 上一个细节系数
} StreamingDWT;

void streaming_dwt_init(StreamingDWT* sdwt) {
    memset(sdwt->buffer, 0, sizeof(sdwt->buffer));
    sdwt->buffer_index = 0;
    db4_wavelet_init(&sdwt->wavelet);
    sdwt->last_approx = 0.0f;
    sdwt->last_detail = 0.0f;
}

/**
 * @brief 处理单个新样本
 * @param sdwt 流式DWT状态
 * @param new_sample 新输入样本
 * @param approx 输出近似系数（每2个样本输出一次）
 * @param detail 输出细节系数（每2个样本输出一次）
 * @return 1有新输出，0无输出
 */
int streaming_dwt_process(StreamingDWT* sdwt, float new_sample,
                          float* approx, float* detail) {
    
    // 添加新样本到缓冲区
    sdwt->buffer[sdwt->buffer_index] = new_sample;
    sdwt->buffer_index = (sdwt->buffer_index + 1) % 16;
    
    // 每2个样本计算一次
    if (sdwt->buffer_index % 2 == 0) {
        float approx_sum = 0.0f;
        float detail_sum = 0.0f;
        
        // 卷积
        for (uint8_t i = 0; i < sdwt->wavelet.length; i++) {
            uint8_t index = (sdwt->buffer_index + i) % 16;
            approx_sum += sdwt->buffer[index] * sdwt->wavelet.low_pass[i];
            detail_sum += sdwt->buffer[index] * sdwt->wavelet.high_pass[i];
        }
        
        *approx = approx_sum;
        *detail = detail_sum;
        
        sdwt->last_approx = approx_sum;
        sdwt->last_detail = detail_sum;
        
        return 1;  // 有新输出
    }
    
    return 0;  // 无输出
}
```

---

## 7. 最佳实践

### 7.1 小波选择指南

| 应用场景 | 推荐小波 | 理由 |
|---------|---------|------|
| ECG去噪 | db4, db6 | 良好的时频局部化 |
| QRS检测 | sym4, sym5 | 近似对称，减少相位失真 |
| 血压波形 | coif1, coif2 | 尺度函数对称 |
| 快速原型 | haar | 计算简单 |
| 高精度 | db8, db10 | 更多消失矩 |

### 7.2 常见陷阱

❌ **错误1：边界处理不当**

```c
// 错误：未处理边界
for (uint16_t i = 0; i < output_length; i++) {
    for (uint8_t j = 0; j < filter_length; j++) {
        uint16_t index = 2 * i + j;  // 可能越界！
        sum += signal[index] * filter[j];
    }
}

// 正确：循环边界或零填充
for (uint16_t i = 0; i < output_length; i++) {
    for (uint8_t j = 0; j < filter_length; j++) {
        uint16_t index = (2 * i + j) % length;  // 循环
        sum += signal[index] * filter[j];
    }
}
```

❌ **错误2：阈值选择不当**

```c
// 错误：固定阈值
float threshold = 0.1f;  // 对所有信号都用同一阈值

// 正确：自适应阈值
float threshold = calculate_universal_threshold(detail_coeffs, length);
```

❌ **错误3：忽略信号长度要求**

```c
// 错误：未检查长度
dwt_decompose(signal, 1000, &wavelet, &result);  // 1000不是2的幂！

// 正确：检查或填充
if ((length & (length - 1)) != 0) {
    // 填充到最近的2的幂
    uint16_t padded_length = next_power_of_2(length);
    // ...
}
```

### 7.3 调试技巧

```c
/**
 * @brief 验证完美重构特性
 */
void verify_perfect_reconstruction(void) {
    const uint16_t length = 256;
    float original[length];
    float reconstructed[length];
    
    // 生成测试信号
    for (uint16_t i = 0; i < length; i++) {
        original[i] = sinf(2.0f * M_PI * 5.0f * i / length);
    }
    
    Db4Wavelet wavelet;
    db4_wavelet_init(&wavelet);
    
    // 分解
    DWTResult result;
    dwt_decompose(original, length, &wavelet, &result);
    
    // 重构
    dwt_reconstruct(result.approximation, result.detail,
                   result.length, &wavelet, reconstructed);
    
    // 计算重构误差
    float max_error = 0.0f;
    float mse = 0.0f;
    
    for (uint16_t i = 0; i < length; i++) {
        float error = fabsf(original[i] - reconstructed[i]);
        if (error > max_error) {
            max_error = error;
        }
        mse += error * error;
    }
    mse /= length;
    
    printf("Perfect Reconstruction Test:\n");
    printf("  Max Error: %.6f\n", max_error);
    printf("  MSE: %.6f\n", mse);
    printf("  Status: %s\n", (max_error < 1e-5f) ? "PASS" : "FAIL");
    
    // 清理
    free(result.approximation);
    free(result.detail);
}
```

---

## 8. 自测问题

### 基础理解
1. **小波变换与傅里叶变换的主要区别是什么？**
   <details>
   <summary>答案</summary>
   
   - 傅里叶变换使用无限长的正弦/余弦波作为基函数，只提供频率信息，无时间定位
   - 小波变换使用有限长的小波函数，同时提供时间和频率信息
   - 小波变换更适合分析非平稳信号和瞬态特征
   </details>

2. **什么是消失矩（vanishing moments）？为什么重要？**
   <details>
   <summary>答案</summary>
   
   - 消失矩是小波函数的一个性质，表示小波与多项式正交的阶数
   - N阶消失矩意味着小波与0到N-1阶多项式的内积为0
   - 更多消失矩意味着更好的平滑信号压缩能力
   - db4有4个消失矩，适合ECG等相对平滑的信号
   </details>

3. **为什么DWT要求信号长度为2的幂？**
   <details>
   <summary>答案</summary>
   
   - DWT使用二进尺度分解（每层下采样2倍）
   - 2的幂长度确保每层都能整除
   - 如果长度不是2的幂，需要填充（zero-padding或对称扩展）
   </details>

### 实现细节
4. **软阈值和硬阈值去噪有什么区别？**
   <details>
   <summary>答案</summary>
   
   - 硬阈值：|x| < T → 0, |x| ≥ T → x（保持原值）
   - 软阈值：|x| < T → 0, |x| ≥ T → sign(x)(|x|-T)（减去阈值）
   - 软阈值产生更平滑的结果，但可能过度平滑
   - 硬阈值保留更多细节，但可能产生伪影
   </details>

5. **如何选择小波分解的层数？**
   <details>
   <summary>答案</summary>
   
   - 取决于信号的采样率和感兴趣的频率范围
   - 每层分解将频率范围减半
   - 例如：250Hz采样的ECG，3-4层分解可覆盖0.5-30Hz（主要ECG频段）
   - 过多层数会丢失时间分辨率
   </details>

### 医疗应用
6. **为什么小波变换适合ECG的QRS波检测？**
   <details>
   <summary>答案</summary>
   
   - QRS波是瞬态、高频特征（10-30Hz）
   - 小波变换能同时提供时间和频率信息
   - 特定尺度的细节系数对应QRS频段
   - 相比带通滤波，小波变换相位失真更小
   </details>

7. **如何使用小波变换区分ECG中的不同成分（P波、QRS波、T波）？**
   <details>
   <summary>答案</summary>
   
   - P波：低频（0.5-5Hz），出现在较粗尺度（高层近似系数）
   - QRS波：高频（10-30Hz），出现在较细尺度（低层细节系数）
   - T波：中频（1-7Hz），出现在中间尺度
   - 通过分析不同层的系数可分离各成分
   </details>

### 优化与实践
8. **定点运算相比浮点运算有什么优缺点？**
   <details>
   <summary>答案</summary>
   
   优点：
   - 计算速度快（无需浮点单元）
   - 功耗低
   - 代码体积小
   
   缺点：
   - 动态范围有限
   - 需要仔细处理溢出
   - 精度损失
   - 开发和调试更复杂
   </details>

9. **如何在嵌入式系统中实现实时小波去噪？**
   <details>
   <summary>答案</summary>
   
   - 使用流式处理（逐样本或小块处理）
   - 采用原地算法减少内存占用
   - 使用定点运算或SIMD加速
   - 预计算和缓存小波系数
   - 限制分解层数
   - 使用简单的小波（如Haar）进行快速原型
   </details>

10. **如何验证小波变换实现的正确性？**
    <details>
    <summary>答案</summary>
    
    - 完美重构测试：分解后重构，误差应接近0
    - 与参考实现对比（如MATLAB、Python）
    - 能量守恒：Parseval定理
    - 边界情况测试：全零、全一、脉冲信号
    - 已知信号测试：正弦波、方波等
    </details>

---

## 9. 参考资料

### 书籍
1. **"Wavelets and Filter Banks" by Gilbert Strang and Truong Nguyen**
   - 小波理论经典教材
   - 包含详细的数学推导

2. **"Ripples in Mathematics: The Discrete Wavelet Transform" by A. Jensen and A. la Cour-Harbo**
   - 适合工程师的实用指南
   - 大量代码示例

3. **"Biomedical Signal Processing and Signal Modeling" by Eugene N. Bruce**
   - 医疗信号处理专著
   - 包含ECG、EEG等应用

### 论文
1. **"The Wavelet Transform, Time-Frequency Localization and Signal Analysis" by Ingrid Daubechies (1990)**
   - 小波变换奠基性论文

2. **"ECG Signal Denoising and Baseline Wander Correction Based on CEEMDAN and Wavelet Threshold" (2017)**
   - ECG去噪最新方法

### 在线资源
1. **PyWavelets Documentation**: https://pywavelets.readthedocs.io/
   - Python小波库，可用于算法验证

2. **MATLAB Wavelet Toolbox**: https://www.mathworks.com/products/wavelet.html
   - 工业标准参考实现

3. **ARM CMSIS-DSP Library**: https://arm-software.github.io/CMSIS_5/DSP/html/index.html
   - 包含优化的信号处理函数

### 标准与指南
1. **IEC 60601-2-27**: ECG监护设备特殊要求
2. **ANSI/AAMI EC57**: ECG信号处理标准

---

## 相关模块

- [数字滤波器](digital-filters.md) - 小波变换的滤波器组实现
- [FFT](fft.md) - 频域分析对比
- [心电信号处理](ecg-processing.md) - 小波在ECG中的应用
- [SpO2计算](spo2-calculation.md) - 脉搏波形分析

---

**下一步**: 学习[自适应滤波器](adaptive-filters.md)，了解如何根据信号特性动态调整滤波参数。
