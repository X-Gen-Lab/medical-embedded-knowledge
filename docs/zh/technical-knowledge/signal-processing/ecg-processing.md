---
title: 心电信号处理（ECG Processing）
description: 掌握心电信号采集、滤波、QRS检测和心率计算的完整技术
difficulty: 高级
estimated_time: 120分钟
tags:
- ECG
- 心电图
- QRS检测
- 心率计算
- 信号处理
- 医疗器械
related_modules:
- zh/technical-knowledge/signal-processing
- zh/technical-knowledge/signal-processing/digital-filters
- zh/technical-knowledge/signal-processing/fft
- zh/technical-knowledge/hardware-interfaces/adc-dac
last_updated: '2026-02-09'
version: '1.0'
language: zh
---

# 心电信号处理（ECG Processing）

## 学习目标

完成本模块后，你将能够：
- 理解心电信号的生理学基础和特征
- 掌握心电信号采集的硬件和软件要求
- 实现完整的心电信号滤波链
- 实现实时QRS波检测算法
- 计算心率和心率变异性（HRV）
- 处理心电信号中的各种噪声和伪影
- 符合医疗器械标准（IEC 60601-2-27）

## 前置知识

- 心脏电生理基础
- 数字信号处理理论
- 数字滤波器设计
- ADC采样原理
- C语言编程
- 实时系统概念

## 内容

### 概念介绍

心电图（Electrocardiogram, ECG或EKG）记录心脏电活动，是最常用的心脏诊断工具之一。
心电信号处理是医疗器械开发中最具挑战性的领域之一，需要在噪声环境中准确提取微弱的生理信号。

**心电信号特征**：
- **幅度范围**：0.5-4 mV（体表）
- **频率范围**：0.05-150 Hz
- **主要波形**：P波、QRS波群、T波
- **典型心率**：60-100 bpm（成人静息）

**心电信号处理挑战**：
1. **微弱信号**：需要高增益放大（1000-2000倍）
2. **多种噪声**：工频干扰、肌电干扰、基线漂移、运动伪影
3. **实时性要求**：需要在毫秒级响应
4. **个体差异**：波形形态因人而异
5. **法规要求**：必须符合IEC 60601-2-27等标准

### 心电信号波形解析

#### 标准心电波形

```
      R
      |
      |
  P   |   T
  /\  |  /\
 /  \ | /  \
/    \|/    \___
      Q    S
```

**各波形的生理意义**：

- **P波**：心房去极化（0.08-0.12秒）
- **QRS波群**：心室去极化（0.06-0.10秒）
  - Q波：室间隔去极化
  - R波：心室主要去极化（最高峰）
  - S波：心室基底部去极化
- **T波**：心室复极化
- **PR间期**：房室传导时间（0.12-0.20秒）
- **QT间期**：心室去极化和复极化总时间（0.35-0.44秒）

#### 心电信号参数

```c
// 心电信号参数定义
typedef struct {
    float p_wave_duration;      // P波宽度（ms）
    float pr_interval;          // PR间期（ms）
    float qrs_duration;         // QRS波宽度（ms）
    float qt_interval;          // QT间期（ms）
    float rr_interval;          // RR间期（ms）
    float heart_rate;           // 心率（bpm）
    float p_amplitude;          // P波幅度（mV）
    float r_amplitude;          // R波幅度（mV）
    float t_amplitude;          // T波幅度（mV）
} ECG_Parameters_t;
```

### 心电信号采集

#### 硬件要求

```c
// ECG采集配置
typedef struct {
    float sample_rate;          // 采样率（Hz）
    uint8_t resolution;         // ADC分辨率（bits）
    float gain;                 // 放大倍数
    float input_range;          // 输入范围（mV）
    float common_mode_rejection; // 共模抑制比（dB）
} ECG_Acquisition_Config_t;

// 推荐配置
#define ECG_SAMPLE_RATE_MIN     250.0f   // 最小采样率
#define ECG_SAMPLE_RATE_TYPICAL 500.0f   // 典型采样率
#define ECG_SAMPLE_RATE_HIGH    1000.0f  // 高质量采样率
#define ECG_ADC_RESOLUTION      16       // 16位ADC
#define ECG_GAIN                1000.0f  // 1000倍增益
#define ECG_INPUT_RANGE         5.0f     // ±5mV输入范围
#define ECG_CMRR_MIN            80.0f    // 最小CMRR: 80dB
```

#### 导联配置

```c
// ECG导联类型
typedef enum {
    ECG_LEAD_I = 0,      // 导联I：LA - RA
    ECG_LEAD_II,         // 导联II：LL - RA
    ECG_LEAD_III,        // 导联III：LL - LA
    ECG_LEAD_aVR,        // 加压单极肢体导联aVR
    ECG_LEAD_aVL,        // 加压单极肢体导联aVL
    ECG_LEAD_aVF,        // 加压单极肢体导联aVF
    ECG_LEAD_V1,         // 胸导联V1
    ECG_LEAD_V2,         // 胸导联V2
    ECG_LEAD_V3,         // 胸导联V3
    ECG_LEAD_V4,         // 胸导联V4
    ECG_LEAD_V5,         // 胸导联V5
    ECG_LEAD_V6,         // 胸导联V6
    ECG_LEAD_COUNT
} ECG_Lead_t;

// 单导联ECG系统（最简单）
typedef struct {
    ECG_Lead_t lead_type;
    float* buffer;
    uint16_t buffer_size;
    uint16_t write_index;
} Single_Lead_ECG_t;
```


### 心电信号滤波

#### 完整的滤波链

心电信号处理需要多级滤波来去除不同类型的噪声：

```c
// ECG滤波器组
typedef struct {
    // 基线漂移去除（高通滤波器）
    Biquad_Filter_t hpf_baseline;    // 0.5Hz高通
    
    // 工频干扰去除（陷波滤波器）
    Biquad_Filter_t notch_50hz;      // 50Hz陷波
    Biquad_Filter_t notch_60hz;      // 60Hz陷波（可选）
    
    // 高频噪声去除（低通滤波器）
    Biquad_Filter_t lpf_noise;       // 40Hz低通
    
    // 肌电干扰抑制（可选）
    Biquad_Filter_t lpf_emg;         // 35Hz低通
    
    float sample_rate;
} ECG_Filter_Bank_t;

// 初始化ECG滤波器组
void ecg_filter_bank_init(ECG_Filter_Bank_t* fb, float sample_rate) {
    fb->sample_rate = sample_rate;
    
    // 1. 高通滤波器（0.5Hz）- 去除基线漂移
    float hp_freq = 0.5f;
    float hp_q = 0.707f;
    biquad_highpass_init(&fb->hpf_baseline, hp_freq, hp_q, sample_rate);
    
    // 2. 陷波滤波器（50Hz）- 去除工频干扰
    float notch_freq = 50.0f;
    float notch_q = 30.0f;  // 高Q值，窄带陷波
    biquad_notch_init(&fb->notch_50hz, notch_freq, notch_q, sample_rate);
    
    // 3. 低通滤波器（40Hz）- 去除高频噪声
    float lp_freq = 40.0f;
    float lp_q = 0.707f;
    biquad_lowpass_init(&fb->lpf_noise, lp_freq, lp_q, sample_rate);
}

// ECG信号滤波处理
float ecg_filter_process(ECG_Filter_Bank_t* fb, float raw_ecg) {
    float signal = raw_ecg;
    
    // 级联滤波
    signal = biquad_process(&fb->hpf_baseline, signal);  // 去基线漂移
    signal = biquad_process(&fb->notch_50hz, signal);    // 去工频干扰
    signal = biquad_process(&fb->lpf_noise, signal);     // 去高频噪声
    
    return signal;
}
```

#### 自适应滤波

对于运动伪影等非平稳噪声，可以使用自适应滤波：

```c
// 自适应滤波器（LMS算法）
typedef struct {
    float* weights;          // 滤波器权重
    float* buffer;           // 输入缓冲区
    uint16_t length;         // 滤波器长度
    float mu;                // 步长参数
    uint16_t index;          // 当前索引
} Adaptive_Filter_t;

// 初始化自适应滤波器
void adaptive_filter_init(Adaptive_Filter_t* af, uint16_t length, float mu) {
    af->length = length;
    af->mu = mu;
    af->index = 0;
    
    af->weights = (float*)calloc(length, sizeof(float));
    af->buffer = (float*)calloc(length, sizeof(float));
}

// LMS自适应滤波
float adaptive_filter_lms(Adaptive_Filter_t* af, float input, float desired) {
    // 更新输入缓冲区
    af->buffer[af->index] = input;
    af->index = (af->index + 1) % af->length;
    
    // 计算输出
    float output = 0.0f;
    for (uint16_t i = 0; i < af->length; i++) {
        uint16_t idx = (af->index + i) % af->length;
        output += af->weights[i] * af->buffer[idx];
    }
    
    // 计算误差
    float error = desired - output;
    
    // 更新权重
    for (uint16_t i = 0; i < af->length; i++) {
        uint16_t idx = (af->index + i) % af->length;
        af->weights[i] += 2.0f * af->mu * error * af->buffer[idx];
    }
    
    return output;
}
```

### QRS波检测算法

QRS波检测是心电信号处理的核心，有多种算法可选。

#### Pan-Tompkins算法

Pan-Tompkins是最经典和广泛使用的QRS检测算法：

```c
// Pan-Tompkins QRS检测器
typedef struct {
    // 带通滤波器（5-15Hz）
    Biquad_Filter_t bpf_low;
    Biquad_Filter_t bpf_high;
    
    // 微分器
    float diff_buffer[5];
    uint8_t diff_index;
    
    // 积分器
    float* int_buffer;
    uint16_t int_window_size;
    uint16_t int_index;
    float int_sum;
    
    // 阈值检测
    float threshold_i1;      // 积分阈值
    float threshold_i2;      // 备用阈值
    float spki;              // 信号峰值
    float npki;              // 噪声峰值
    
    // RR间期
    float* rr_buffer;
    uint8_t rr_count;
    float rr_average;
    float rr_low_limit;
    float rr_high_limit;
    
    // 检测状态
    uint32_t last_qrs_time;
    float sample_rate;
    bool qrs_detected;
    
} PanTompkins_Detector_t;

// 初始化Pan-Tompkins检测器
void pan_tompkins_init(PanTompkins_Detector_t* pt, float sample_rate) {
    pt->sample_rate = sample_rate;
    pt->diff_index = 0;
    pt->int_index = 0;
    pt->int_sum = 0.0f;
    pt->rr_count = 0;
    pt->last_qrs_time = 0;
    pt->qrs_detected = false;
    
    // 带通滤波器（5-15Hz）
    biquad_highpass_init(&pt->bpf_low, 5.0f, 0.707f, sample_rate);
    biquad_lowpass_init(&pt->bpf_high, 15.0f, 0.707f, sample_rate);
    
    // 积分窗口（150ms）
    pt->int_window_size = (uint16_t)(0.150f * sample_rate);
    pt->int_buffer = (float*)calloc(pt->int_window_size, sizeof(float));
    
    // RR间期缓冲区（最近8个）
    pt->rr_buffer = (float*)calloc(8, sizeof(float));
    
    // 初始阈值
    pt->spki = 0.0f;
    pt->npki = 0.0f;
    pt->threshold_i1 = 0.0f;
    pt->threshold_i2 = 0.0f;
}

// Pan-Tompkins处理单个样本
bool pan_tompkins_process(PanTompkins_Detector_t* pt, float ecg_sample, 
                          uint32_t sample_time) {
    // 步骤1：带通滤波（5-15Hz）
    float filtered = biquad_process(&pt->bpf_low, ecg_sample);
    filtered = biquad_process(&pt->bpf_high, filtered);
    
    // 步骤2：微分（突出QRS斜率）
    pt->diff_buffer[pt->diff_index] = filtered;
    pt->diff_index = (pt->diff_index + 1) % 5;
    
    // 五点微分：y[n] = (2x[n] + x[n-1] - x[n-3] - 2x[n-4]) / 8
    float diff_output = (
        2.0f * pt->diff_buffer[(pt->diff_index + 4) % 5] +
        pt->diff_buffer[(pt->diff_index + 3) % 5] -
        pt->diff_buffer[(pt->diff_index + 1) % 5] -
        2.0f * pt->diff_buffer[pt->diff_index]
    ) / 8.0f;
    
    // 步骤3：平方（放大高频成分）
    float squared = diff_output * diff_output;
    
    // 步骤4：移动窗口积分（150ms）
    pt->int_sum -= pt->int_buffer[pt->int_index];
    pt->int_buffer[pt->int_index] = squared;
    pt->int_sum += squared;
    pt->int_index = (pt->int_index + 1) % pt->int_window_size;
    
    float integrated = pt->int_sum / pt->int_window_size;
    
    // 步骤5：自适应阈值检测
    bool qrs_found = false;
    
    if (integrated > pt->threshold_i1) {
        // 检查RR间期合理性
        uint32_t rr_interval = sample_time - pt->last_qrs_time;
        float rr_ms = (rr_interval * 1000.0f) / pt->sample_rate;
        
        // RR间期应在200ms-2000ms之间（30-300 bpm）
        if (rr_ms > 200.0f && rr_ms < 2000.0f) {
            qrs_found = true;
            pt->last_qrs_time = sample_time;
            
            // 更新信号峰值
            pt->spki = 0.125f * integrated + 0.875f * pt->spki;
            
            // 更新RR间期
            if (pt->rr_count < 8) {
                pt->rr_buffer[pt->rr_count++] = rr_ms;
            } else {
                // 移动RR缓冲区
                for (uint8_t i = 0; i < 7; i++) {
                    pt->rr_buffer[i] = pt->rr_buffer[i + 1];
                }
                pt->rr_buffer[7] = rr_ms;
            }
            
            // 计算平均RR间期
            pt->rr_average = 0.0f;
            for (uint8_t i = 0; i < pt->rr_count; i++) {
                pt->rr_average += pt->rr_buffer[i];
            }
            pt->rr_average /= pt->rr_count;
            
            // 更新RR间期限制
            pt->rr_low_limit = 0.92f * pt->rr_average;
            pt->rr_high_limit = 1.16f * pt->rr_average;
        }
    } else {
        // 更新噪声峰值
        if (integrated > pt->npki) {
            pt->npki = 0.125f * integrated + 0.875f * pt->npki;
        }
    }
    
    // 更新阈值
    pt->threshold_i1 = pt->npki + 0.25f * (pt->spki - pt->npki);
    pt->threshold_i2 = 0.5f * pt->threshold_i1;
    
    pt->qrs_detected = qrs_found;
    return qrs_found;
}
```


#### 简化的QRS检测算法

对于资源受限的嵌入式系统，可以使用更简单的算法：

```c
// 简化的QRS检测器（基于阈值和斜率）
typedef struct {
    float threshold;
    float last_peak;
    uint32_t last_peak_time;
    uint16_t refractory_samples;  // 不应期（200ms）
    uint32_t samples_since_peak;
    float sample_rate;
} Simple_QRS_Detector_t;

// 初始化简单QRS检测器
void simple_qrs_init(Simple_QRS_Detector_t* det, float sample_rate) {
    det->sample_rate = sample_rate;
    det->threshold = 0.5f;  // 初始阈值
    det->last_peak = 0.0f;
    det->last_peak_time = 0;
    det->samples_since_peak = 0;
    det->refractory_samples = (uint16_t)(0.2f * sample_rate);  // 200ms
}

// 简单QRS检测
bool simple_qrs_detect(Simple_QRS_Detector_t* det, float ecg_sample) {
    det->samples_since_peak++;
    
    // 在不应期内不检测
    if (det->samples_since_peak < det->refractory_samples) {
        return false;
    }
    
    // 检测峰值
    if (ecg_sample > det->threshold && ecg_sample > det->last_peak) {
        det->last_peak = ecg_sample;
        det->last_peak_time = det->samples_since_peak;
        det->samples_since_peak = 0;
        
        // 自适应阈值（80%的峰值）
        det->threshold = 0.8f * ecg_sample;
        
        return true;
    }
    
    // 阈值衰减（避免漏检）
    det->threshold *= 0.9999f;
    
    return false;
}
```

### 心率计算

#### 实时心率计算

```c
// 心率计算器
typedef struct {
    float* rr_intervals;     // RR间期缓冲区（ms）
    uint16_t buffer_size;
    uint16_t count;
    uint16_t write_index;
    float current_hr;        // 当前心率（bpm）
    float average_hr;        // 平均心率（bpm）
    float min_hr;            // 最小心率
    float max_hr;            // 最大心率
} Heart_Rate_Calculator_t;

// 初始化心率计算器
void heart_rate_init(Heart_Rate_Calculator_t* hrc, uint16_t buffer_size) {
    hrc->buffer_size = buffer_size;
    hrc->count = 0;
    hrc->write_index = 0;
    hrc->current_hr = 0.0f;
    hrc->average_hr = 0.0f;
    hrc->min_hr = 300.0f;
    hrc->max_hr = 0.0f;
    
    hrc->rr_intervals = (float*)calloc(buffer_size, sizeof(float));
}

// 添加RR间期并计算心率
void heart_rate_add_rr(Heart_Rate_Calculator_t* hrc, float rr_ms) {
    // 验证RR间期合理性（200-2000ms，对应30-300 bpm）
    if (rr_ms < 200.0f || rr_ms > 2000.0f) {
        return;  // 忽略异常值
    }
    
    // 添加到缓冲区
    hrc->rr_intervals[hrc->write_index] = rr_ms;
    hrc->write_index = (hrc->write_index + 1) % hrc->buffer_size;
    
    if (hrc->count < hrc->buffer_size) {
        hrc->count++;
    }
    
    // 计算当前心率（基于最新RR间期）
    hrc->current_hr = 60000.0f / rr_ms;  // bpm = 60000 / RR(ms)
    
    // 计算平均心率
    float sum = 0.0f;
    for (uint16_t i = 0; i < hrc->count; i++) {
        sum += hrc->rr_intervals[i];
    }
    float avg_rr = sum / hrc->count;
    hrc->average_hr = 60000.0f / avg_rr;
    
    // 更新最小/最大心率
    if (hrc->current_hr < hrc->min_hr) {
        hrc->min_hr = hrc->current_hr;
    }
    if (hrc->current_hr > hrc->max_hr) {
        hrc->max_hr = hrc->current_hr;
    }
}

// 获取心率统计
void heart_rate_get_stats(Heart_Rate_Calculator_t* hrc, 
                          float* current, float* average, 
                          float* min, float* max) {
    if (current) *current = hrc->current_hr;
    if (average) *average = hrc->average_hr;
    if (min) *min = hrc->min_hr;
    if (max) *max = hrc->max_hr;
}
```

### 心率变异性（HRV）分析

#### 时域HRV指标

```c
// HRV时域指标
typedef struct {
    float sdnn;          // RR间期标准差（ms）
    float rmssd;         // 相邻RR间期差值的均方根（ms）
    float nn50;          // 相邻RR间期差值>50ms的个数
    float pnn50;         // NN50占总RR间期的百分比（%）
    float mean_rr;       // 平均RR间期（ms）
    float mean_hr;       // 平均心率（bpm）
} HRV_Time_Domain_t;

// 计算时域HRV指标
void calculate_hrv_time_domain(float* rr_intervals, uint16_t count, 
                               HRV_Time_Domain_t* result) {
    if (count < 2) {
        memset(result, 0, sizeof(HRV_Time_Domain_t));
        return;
    }
    
    // 计算平均RR间期
    float sum_rr = 0.0f;
    for (uint16_t i = 0; i < count; i++) {
        sum_rr += rr_intervals[i];
    }
    result->mean_rr = sum_rr / count;
    result->mean_hr = 60000.0f / result->mean_rr;
    
    // 计算SDNN（标准差）
    float sum_squared_diff = 0.0f;
    for (uint16_t i = 0; i < count; i++) {
        float diff = rr_intervals[i] - result->mean_rr;
        sum_squared_diff += diff * diff;
    }
    result->sdnn = sqrtf(sum_squared_diff / count);
    
    // 计算RMSSD和NN50
    float sum_successive_diff_squared = 0.0f;
    uint16_t nn50_count = 0;
    
    for (uint16_t i = 1; i < count; i++) {
        float diff = rr_intervals[i] - rr_intervals[i-1];
        sum_successive_diff_squared += diff * diff;
        
        if (fabsf(diff) > 50.0f) {
            nn50_count++;
        }
    }
    
    result->rmssd = sqrtf(sum_successive_diff_squared / (count - 1));
    result->nn50 = (float)nn50_count;
    result->pnn50 = (nn50_count * 100.0f) / (count - 1);
}
```

#### 频域HRV指标（使用FFT）

```c
// HRV频域指标
typedef struct {
    float vlf_power;     // 极低频功率（0.003-0.04 Hz）
    float lf_power;      // 低频功率（0.04-0.15 Hz）
    float hf_power;      // 高频功率（0.15-0.4 Hz）
    float total_power;   // 总功率
    float lf_hf_ratio;   // LF/HF比值
    float lf_nu;         // LF归一化单位
    float hf_nu;         // HF归一化单位
} HRV_Frequency_Domain_t;

// 计算频域HRV指标（需要FFT支持）
void calculate_hrv_frequency_domain(float* rr_intervals, uint16_t count,
                                    float sample_rate,
                                    HRV_Frequency_Domain_t* result) {
    // 参见FFT模块中的实现
    // 这里省略详细代码，参考fft.md中的HRV频域分析
}
```

### 完整的ECG处理系统

#### 集成系统架构

```c
// 完整的ECG处理系统
typedef struct {
    // 采集配置
    ECG_Acquisition_Config_t acq_config;
    
    // 滤波器组
    ECG_Filter_Bank_t filter_bank;
    
    // QRS检测器
    PanTompkins_Detector_t qrs_detector;
    
    // 心率计算器
    Heart_Rate_Calculator_t hr_calculator;
    
    // 数据缓冲区
    float* raw_buffer;
    float* filtered_buffer;
    uint16_t buffer_size;
    uint16_t write_index;
    
    // 状态
    bool is_running;
    uint32_t sample_count;
    
} ECG_Processing_System_t;

// 初始化ECG处理系统
ECG_Processing_System_t* ecg_system_init(float sample_rate, uint16_t buffer_size) {
    ECG_Processing_System_t* sys = 
        (ECG_Processing_System_t*)malloc(sizeof(ECG_Processing_System_t));
    
    // 配置采集参数
    sys->acq_config.sample_rate = sample_rate;
    sys->acq_config.resolution = ECG_ADC_RESOLUTION;
    sys->acq_config.gain = ECG_GAIN;
    
    // 初始化滤波器
    ecg_filter_bank_init(&sys->filter_bank, sample_rate);
    
    // 初始化QRS检测器
    pan_tompkins_init(&sys->qrs_detector, sample_rate);
    
    // 初始化心率计算器
    heart_rate_init(&sys->hr_calculator, 8);  // 保存最近8个RR间期
    
    // 分配缓冲区
    sys->buffer_size = buffer_size;
    sys->raw_buffer = (float*)calloc(buffer_size, sizeof(float));
    sys->filtered_buffer = (float*)calloc(buffer_size, sizeof(float));
    sys->write_index = 0;
    sys->sample_count = 0;
    sys->is_running = false;
    
    return sys;
}

// 处理单个ECG样本
void ecg_system_process_sample(ECG_Processing_System_t* sys, float raw_sample) {
    // 1. 存储原始数据
    sys->raw_buffer[sys->write_index] = raw_sample;
    
    // 2. 滤波
    float filtered = ecg_filter_process(&sys->filter_bank, raw_sample);
    sys->filtered_buffer[sys->write_index] = filtered;
    
    // 3. QRS检测
    bool qrs_detected = pan_tompkins_process(&sys->qrs_detector, filtered, 
                                             sys->sample_count);
    
    // 4. 如果检测到QRS，计算心率
    if (qrs_detected && sys->qrs_detector.rr_count > 0) {
        float latest_rr = sys->qrs_detector.rr_buffer[
            sys->qrs_detector.rr_count - 1];
        heart_rate_add_rr(&sys->hr_calculator, latest_rr);
    }
    
    // 5. 更新索引
    sys->write_index = (sys->write_index + 1) % sys->buffer_size;
    sys->sample_count++;
}

// 获取当前心率
float ecg_system_get_heart_rate(ECG_Processing_System_t* sys) {
    return sys->hr_calculator.current_hr;
}

// 获取心率统计
void ecg_system_get_hr_stats(ECG_Processing_System_t* sys,
                             float* current, float* average,
                             float* min, float* max) {
    heart_rate_get_stats(&sys->hr_calculator, current, average, min, max);
}

// 释放系统资源
void ecg_system_free(ECG_Processing_System_t* sys) {
    if (sys) {
        free(sys->raw_buffer);
        free(sys->filtered_buffer);
        free(sys->hr_calculator.rr_intervals);
        free(sys->qrs_detector.int_buffer);
        free(sys->qrs_detector.rr_buffer);
        free(sys);
    }
}
```


### RTOS集成示例

```c
// FreeRTOS任务示例
void vECGProcessingTask(void *pvParameters) {
    ECG_Processing_System_t* ecg_sys = (ECG_Processing_System_t*)pvParameters;
    
    const TickType_t xPeriod = pdMS_TO_TICKS(2);  // 2ms周期（500Hz采样）
    TickType_t xLastWakeTime = xTaskGetTickCount();
    
    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xPeriod);
        
        // 从ADC读取ECG样本
        float raw_ecg = adc_read_ecg_channel();
        
        // 处理样本
        ecg_system_process_sample(ecg_sys, raw_ecg);
        
        // 每秒更新一次显示
        if (ecg_sys->sample_count % 500 == 0) {
            float hr = ecg_system_get_heart_rate(ecg_sys);
            update_display_heart_rate(hr);
        }
    }
}
```

## 最佳实践

### 1. 采样率选择

!!! tip "采样率建议"
    - **诊断级ECG**：500-1000 Hz（符合IEC 60601-2-27）
    - **监护级ECG**：250-500 Hz
    - **可穿戴设备**：125-250 Hz（权衡功耗）
    - **最小要求**：≥250 Hz（奈奎斯特定理，信号带宽0-150Hz）

### 2. 滤波器设计

!!! tip "滤波器配置"
    - **高通滤波器**：0.5Hz（去基线漂移）
    - **低通滤波器**：40Hz（去高频噪声）
    - **陷波滤波器**：50/60Hz（去工频干扰）
    - **使用级联二阶滤波器**：更好的稳定性
    - **避免过度滤波**：保留QRS波形特征

### 3. QRS检测优化

!!! tip "提高检测准确性"
    - **自适应阈值**：根据信号幅度动态调整
    - **不应期设置**：200ms（避免T波误检）
    - **RR间期验证**：检查生理合理性（200-2000ms）
    - **回溯搜索**：在漏检时回溯查找
    - **多导联融合**：使用多个导联提高可靠性

### 4. 噪声处理

```c
// 信号质量评估
typedef enum {
    ECG_QUALITY_GOOD = 0,      // 信号质量好
    ECG_QUALITY_ACCEPTABLE,    // 可接受
    ECG_QUALITY_POOR,          // 质量差
    ECG_QUALITY_UNUSABLE       // 不可用
} ECG_Quality_t;

// 评估ECG信号质量
ECG_Quality_t assess_ecg_quality(float* ecg_data, uint16_t size) {
    // 计算信噪比
    float signal_power = 0.0f;
    float noise_power = 0.0f;
    
    // 简化的SNR计算
    for (uint16_t i = 0; i < size; i++) {
        signal_power += ecg_data[i] * ecg_data[i];
    }
    signal_power /= size;
    
    // 计算高频噪声（简化）
    for (uint16_t i = 1; i < size; i++) {
        float diff = ecg_data[i] - ecg_data[i-1];
        noise_power += diff * diff;
    }
    noise_power /= (size - 1);
    
    float snr = 10.0f * log10f(signal_power / noise_power);
    
    // 根据SNR分类
    if (snr > 20.0f) return ECG_QUALITY_GOOD;
    if (snr > 15.0f) return ECG_QUALITY_ACCEPTABLE;
    if (snr > 10.0f) return ECG_QUALITY_POOR;
    return ECG_QUALITY_UNUSABLE;
}
```

### 5. 电极脱落检测

```c
// 电极脱落检测
bool detect_lead_off(float* ecg_data, uint16_t size, float threshold) {
    // 方法1：检查信号幅度
    float max_amplitude = 0.0f;
    for (uint16_t i = 0; i < size; i++) {
        float abs_val = fabsf(ecg_data[i]);
        if (abs_val > max_amplitude) {
            max_amplitude = abs_val;
        }
    }
    
    // 如果幅度过小或过大，可能是电极脱落
    if (max_amplitude < 0.05f || max_amplitude > 5.0f) {
        return true;  // 电极脱落
    }
    
    // 方法2：检查信号方差
    float mean = 0.0f;
    for (uint16_t i = 0; i < size; i++) {
        mean += ecg_data[i];
    }
    mean /= size;
    
    float variance = 0.0f;
    for (uint16_t i = 0; i < size; i++) {
        float diff = ecg_data[i] - mean;
        variance += diff * diff;
    }
    variance /= size;
    
    // 方差过小表示信号平坦（可能脱落）
    if (variance < threshold) {
        return true;
    }
    
    return false;
}
```

### 6. 功耗优化

!!! tip "降低功耗"
    - **动态采样率**：静息时降低采样率
    - **按需处理**：只在需要时执行复杂算法
    - **使用定点运算**：避免浮点运算
    - **DMA传输**：减少CPU干预
    - **睡眠模式**：在采样间隙进入低功耗模式

## 常见陷阱

### 1. 忽略基线漂移

!!! danger "错误示例"
    ```c
    // 错误：直接检测QRS，没有去除基线漂移
    bool detect_qrs_wrong(float ecg_sample) {
        return ecg_sample > FIXED_THRESHOLD;  // 固定阈值会失败！
    }
    ```

**正确做法**：使用高通滤波器去除基线漂移，使用自适应阈值。

### 2. 固定阈值检测

!!! danger "常见错误"
    固定阈值无法适应不同患者和不同时间的信号变化。

**正确做法**：使用自适应阈值，根据信号幅度动态调整。

### 3. 忽略不应期

!!! warning "T波误检"
    T波可能被误检为QRS波，导致心率计算错误。

**解决方案**：设置200ms不应期，在检测到QRS后的200ms内不再检测。

### 4. 缓冲区溢出

!!! danger "内存安全"
    ```c
    // 危险：没有检查缓冲区边界
    void unsafe_buffer_write(float* buffer, uint16_t index, float value) {
        buffer[index] = value;  // 可能溢出！
    }
    
    // 安全：使用循环缓冲区
    void safe_buffer_write(float* buffer, uint16_t* index, 
                          uint16_t size, float value) {
        buffer[*index] = value;
        *index = (*index + 1) % size;  // 循环索引
    }
    ```

### 5. 浮点精度问题

!!! warning "累积误差"
    长时间运行时，浮点累加可能产生误差。

**解决方案**：
- 使用双精度（double）进行累加
- 定期重置累加器
- 使用Kahan求和算法

```c
// Kahan求和算法（减少浮点误差）
float kahan_sum(float* data, uint16_t size) {
    float sum = 0.0f;
    float c = 0.0f;  // 补偿值
    
    for (uint16_t i = 0; i < size; i++) {
        float y = data[i] - c;
        float t = sum + y;
        c = (t - sum) - y;
        sum = t;
    }
    
    return sum;
}
```

## 实践练习

### 练习1：实现基本ECG采集和显示

编写程序从ADC采集ECG信号，应用滤波，并在串口输出波形数据。

### 练习2：实现QRS检测

实现Pan-Tompkins算法，检测QRS波并计算心率。

### 练习3：HRV分析

收集5分钟的ECG数据，计算时域和频域HRV指标。

### 练习4：信号质量评估

实现信号质量评估算法，自动检测电极脱落和噪声干扰。

## 自测问题

??? question "1. 为什么ECG信号需要多级滤波？"
    
    ??? success "答案"
        ECG信号面临多种噪声：
        1. **基线漂移**（<0.5Hz）：呼吸、体动引起，需要高通滤波
        2. **工频干扰**（50/60Hz）：电源干扰，需要陷波滤波
        3. **高频噪声**（>40Hz）：肌电干扰、电磁干扰，需要低通滤波
        4. **运动伪影**：非平稳噪声，需要自适应滤波
        
        单一滤波器无法同时处理所有噪声，因此需要级联多个滤波器。

??? question "2. Pan-Tompkins算法的核心步骤是什么？"
    
    ??? success "答案"
        Pan-Tompkins算法包含5个步骤：
        1. **带通滤波**（5-15Hz）：保留QRS主要频率成分
        2. **微分**：突出QRS波的陡峭斜率
        3. **平方**：放大高频成分，使所有值为正
        4. **移动窗口积分**（150ms）：平滑信号
        5. **自适应阈值检测**：动态调整检测阈值
        
        这些步骤协同工作，实现鲁棒的QRS检测。

??? question "3. 如何区分QRS波和T波？"
    
    ??? success "答案"
        区分方法：
        1. **不应期**：QRS后200ms内不检测（T波通常在此期间）
        2. **幅度差异**：QRS波幅度通常大于T波
        3. **斜率差异**：QRS波斜率更陡峭
        4. **频率成分**：QRS波含更多高频成分
        5. **RR间期验证**：检查心率的生理合理性

??? question "4. 什么是心率变异性（HRV）？为什么重要？"
    
    ??? success "答案"
        HRV是连续心跳间期的变化程度，反映自主神经系统的调节能力。
        
        **临床意义**：
        - 高HRV：良好的心血管健康
        - 低HRV：心血管疾病风险增加
        - LF/HF比值：交感/副交感神经平衡
        
        **应用**：
        - 心血管疾病风险评估
        - 压力和疲劳监测
        - 运动训练优化
        - 睡眠质量评估

??? question "5. 如何处理电极脱落？"
    
    ??? success "答案"
        检测方法：
        1. **幅度检测**：信号过小或过大
        2. **方差检测**：信号过于平坦
        3. **阻抗测量**：电极-皮肤接触阻抗
        4. **QRS缺失**：长时间无QRS检测
        
        处理策略：
        1. **报警提示**：通知用户重新贴电极
        2. **停止分析**：避免错误诊断
        3. **标记数据**：记录信号质量差的时段
        4. **自动恢复**：电极恢复后自动继续

## 参考文献

1. Pan, J., & Tompkins, W. J. (1985). "A Real-Time QRS Detection Algorithm". IEEE Transactions on Biomedical Engineering, BME-32(3), 230-236.

2. IEC 60601-2-27:2011. "Medical electrical equipment - Part 2-27: Particular requirements for the basic safety and essential performance of electrocardiographic monitoring equipment".

3. Task Force of the European Society of Cardiology. (1996). "Heart rate variability: standards of measurement, physiological interpretation and clinical use". Circulation, 93(5), 1043-1065.

4. Hamilton, P. S., & Tompkins, W. J. (1986). "Quantitative Investigation of QRS Detection Rules Using the MIT/BIH Arrhythmia Database". IEEE Transactions on Biomedical Engineering, BME-33(12), 1157-1165.

5. Clifford, G. D., Azuaje, F., & McSharry, P. E. (2006). "Advanced Methods and Tools for ECG Data Analysis". Artech House.

6. Webster, J. G. (Ed.). (2009). "Medical Instrumentation: Application and Design" (4th ed.). Wiley.

## 相关资源

- [数字滤波器](digital-filters.md) - 滤波器设计详解
- [FFT](fft.md) - 频域分析方法
- [ADC/DAC](../hardware-interfaces/adc-dac.md) - 信号采集硬件
- [RTOS任务调度](../rtos/task-scheduling.md) - 实时处理架构
