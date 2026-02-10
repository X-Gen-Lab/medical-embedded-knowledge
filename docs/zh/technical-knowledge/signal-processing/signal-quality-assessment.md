---
title: "信号质量评估（Signal Quality Assessment）"
description: "医疗信号质量评估方法，包括质量指标、实时评估算法及临床应用"
difficulty: "高级"
estimated_time: "2小时"
tags: ["信号质量", "SQI", "ECG", "PPG", "质量评估"]

last_updated: 2026-02-10
version: 1.0
---

# 信号质量评估（Signal Quality Assessment）

## 📋 学习目标

完成本章学习后，您将能够：

- ✅ 理解信号质量评估的重要性
- ✅ 掌握常用的信号质量指标（SQI）
- ✅ 实现实时信号质量评估算法
- ✅ 应用质量评估改善医疗监护系统
- ✅ 处理低质量信号的策略

## 前置知识

- 数字信号处理基础
- 统计学基础
- 医疗信号特征（ECG、PPG等）
- C/C++编程

---

## 1. 信号质量评估基础

### 1.1 为什么需要信号质量评估？

**临床问题**：
- ❌ 运动伪影导致误报警
- ❌ 电极脱落未被检测
- ❌ 低质量信号影响诊断
- ❌ 假阳性增加医护负担

**解决方案**：
- ✅ 实时评估信号质量
- ✅ 抑制低质量信号的报警
- ✅ 提示用户改善信号采集
- ✅ 自动选择最佳导联

### 1.2 信号质量指标（SQI）分类

| 类别 | 指标 | 适用信号 |
|------|------|---------|
| 时域 | SNR、峰值检测率 | ECG、PPG |
| 频域 | 功率谱比、频带能量 | ECG、EEG |
| 统计 | 峰度、偏度 | 通用 |
| 模板匹配 | 相关系数 | ECG、PPG |
| 机器学习 | SVM、神经网络 | 通用 |


---

## 2. ECG信号质量评估

### 2.1 基于SNR的质量评估

```c
#include <stdint.h>
#include <math.h>

/**
 * @brief 计算ECG信号的信噪比（SNR）
 * @param ecg_signal ECG信号
 * @param length 信号长度
 * @param qrs_positions QRS波位置数组
 * @param qrs_count QRS波数量
 * @return SNR值（dB）
 */
float ecg_calculate_snr(const float* ecg_signal, uint16_t length,
                        const uint16_t* qrs_positions, uint8_t qrs_count) {
    
    if (qrs_count < 2) {
        return -1.0f;  // 数据不足
    }
    
    // 1. 估计信号功率（QRS波段）
    float signal_power = 0.0f;
    uint16_t signal_samples = 0;
    
    for (uint8_t i = 0; i < qrs_count; i++) {
        uint16_t qrs_pos = qrs_positions[i];
        
        // QRS波前后各50ms（假设250Hz采样率，约12个样本）
        for (int j = -12; j <= 12; j++) {
            uint16_t index = qrs_pos + j;
            if (index < length) {
                signal_power += ecg_signal[index] * ecg_signal[index];
                signal_samples++;
            }
        }
    }
    signal_power /= signal_samples;
    
    // 2. 估计噪声功率（基线段）
    float noise_power = 0.0f;
    uint16_t noise_samples = 0;
    
    for (uint8_t i = 0; i < qrs_count - 1; i++) {
        uint16_t start = qrs_positions[i] + 50;  // QRS后50个样本
        uint16_t end = qrs_positions[i + 1] - 50;  // 下一个QRS前50个样本
        
        if (end > start) {
            for (uint16_t j = start; j < end; j++) {
                noise_power += ecg_signal[j] * ecg_signal[j];
                noise_samples++;
            }
        }
    }
    
    if (noise_samples == 0) {
        return -1.0f;
    }
    
    noise_power /= noise_samples;
    
    // 3. 计算SNR（dB）
    if (noise_power < 1e-10f) {
        return 100.0f;  // 噪声极小
    }
    
    float snr_db = 10.0f * log10f(signal_power / noise_power);
    
    return snr_db;
}

/**
 * @brief 基于SNR的质量分级
 */
typedef enum {
    ECG_QUALITY_EXCELLENT = 4,  // SNR > 20dB
    ECG_QUALITY_GOOD = 3,       // 15-20dB
    ECG_QUALITY_FAIR = 2,       // 10-15dB
    ECG_QUALITY_POOR = 1,       // 5-10dB
    ECG_QUALITY_UNACCEPTABLE = 0 // < 5dB
} ECGQualityLevel;

ECGQualityLevel ecg_classify_quality(float snr_db) {
    if (snr_db >= 20.0f) return ECG_QUALITY_EXCELLENT;
    if (snr_db >= 15.0f) return ECG_QUALITY_GOOD;
    if (snr_db >= 10.0f) return ECG_QUALITY_FAIR;
    if (snr_db >= 5.0f) return ECG_QUALITY_POOR;
    return ECG_QUALITY_UNACCEPTABLE;
}
```

### 2.2 基于模板匹配的质量评估

```c
/**
 * @brief 计算ECG波形与模板的相关系数
 * @param ecg_segment ECG片段
 * @param template_waveform 模板波形
 * @param length 长度
 * @return 相关系数（0-1）
 */
float ecg_template_correlation(const float* ecg_segment,
                               const float* template_waveform,
                               uint16_t length) {
    
    // 计算均值
    float mean_ecg = 0.0f, mean_template = 0.0f;
    for (uint16_t i = 0; i < length; i++) {
        mean_ecg += ecg_segment[i];
        mean_template += template_waveform[i];
    }
    mean_ecg /= length;
    mean_template /= length;
    
    // 计算相关系数
    float numerator = 0.0f;
    float denom_ecg = 0.0f, denom_template = 0.0f;
    
    for (uint16_t i = 0; i < length; i++) {
        float diff_ecg = ecg_segment[i] - mean_ecg;
        float diff_template = template_waveform[i] - mean_template;
        
        numerator += diff_ecg * diff_template;
        denom_ecg += diff_ecg * diff_ecg;
        denom_template += diff_template * diff_template;
    }
    
    float denominator = sqrtf(denom_ecg * denom_template);
    
    if (denominator < 1e-10f) {
        return 0.0f;
    }
    
    float correlation = numerator / denominator;
    
    // 确保在[0, 1]范围内
    if (correlation < 0.0f) correlation = 0.0f;
    if (correlation > 1.0f) correlation = 1.0f;
    
    return correlation;
}

/**
 * @brief 构建ECG模板（平均多个心跳）
 */
void ecg_build_template(const float* ecg_signal, uint16_t length,
                        const uint16_t* qrs_positions, uint8_t qrs_count,
                        float* template_waveform, uint16_t template_length) {
    
    // 初始化模板为0
    memset(template_waveform, 0, template_length * sizeof(float));
    
    uint8_t valid_beats = 0;
    
    // 累加所有心跳
    for (uint8_t i = 0; i < qrs_count; i++) {
        uint16_t qrs_pos = qrs_positions[i];
        uint16_t start = qrs_pos - template_length / 2;
        
        // 检查边界
        if (start + template_length > length) {
            continue;
        }
        
        // 累加
        for (uint16_t j = 0; j < template_length; j++) {
            template_waveform[j] += ecg_signal[start + j];
        }
        
        valid_beats++;
    }
    
    // 平均
    if (valid_beats > 0) {
        for (uint16_t i = 0; i < template_length; i++) {
            template_waveform[i] /= valid_beats;
        }
    }
}
```

### 2.3 综合质量指标

```c
typedef struct {
    float snr_db;              // 信噪比
    float template_corr;       // 模板相关系数
    float baseline_wander;     // 基线漂移
    float powerline_noise;     // 工频干扰
    uint8_t qrs_detection_rate; // QRS检测率（%）
    ECGQualityLevel overall_quality; // 综合质量
} ECGQualityMetrics;

/**
 * @brief 综合评估ECG信号质量
 */
void ecg_assess_quality(const float* ecg_signal, uint16_t length,
                        uint16_t sampling_rate,
                        ECGQualityMetrics* metrics) {
    
    // 1. 检测QRS波
    uint16_t qrs_positions[100];
    uint8_t qrs_count = detect_qrs_peaks(ecg_signal, length, 
                                         sampling_rate, qrs_positions);
    
    // 2. 计算SNR
    metrics->snr_db = ecg_calculate_snr(ecg_signal, length,
                                        qrs_positions, qrs_count);
    
    // 3. 构建模板并计算相关系数
    float template[200];  // 约0.8秒的模板
    ecg_build_template(ecg_signal, length, qrs_positions, qrs_count,
                      template, 200);
    
    float total_corr = 0.0f;
    for (uint8_t i = 0; i < qrs_count; i++) {
        uint16_t start = qrs_positions[i] - 100;
        if (start + 200 <= length) {
            float corr = ecg_template_correlation(&ecg_signal[start],
                                                 template, 200);
            total_corr += corr;
        }
    }
    metrics->template_corr = (qrs_count > 0) ? (total_corr / qrs_count) : 0.0f;
    
    // 4. 评估基线漂移（低频能量）
    metrics->baseline_wander = estimate_baseline_wander(ecg_signal, length,
                                                       sampling_rate);
    
    // 5. 评估工频干扰
    metrics->powerline_noise = estimate_powerline_noise(ecg_signal, length,
                                                       sampling_rate);
    
    // 6. 计算QRS检测率
    float expected_hr = 70.0f;  // 假设心率70bpm
    float duration_sec = (float)length / sampling_rate;
    uint8_t expected_qrs = (uint8_t)(expected_hr * duration_sec / 60.0f);
    metrics->qrs_detection_rate = (expected_qrs > 0) ?
        (qrs_count * 100 / expected_qrs) : 0;
    
    // 7. 综合评分
    int score = 0;
    
    // SNR权重：40%
    if (metrics->snr_db >= 20.0f) score += 40;
    else if (metrics->snr_db >= 15.0f) score += 30;
    else if (metrics->snr_db >= 10.0f) score += 20;
    else if (metrics->snr_db >= 5.0f) score += 10;
    
    // 模板相关性权重：30%
    if (metrics->template_corr >= 0.9f) score += 30;
    else if (metrics->template_corr >= 0.8f) score += 20;
    else if (metrics->template_corr >= 0.7f) score += 10;
    
    // QRS检测率权重：20%
    if (metrics->qrs_detection_rate >= 90) score += 20;
    else if (metrics->qrs_detection_rate >= 80) score += 15;
    else if (metrics->qrs_detection_rate >= 70) score += 10;
    
    // 噪声权重：10%
    if (metrics->baseline_wander < 0.1f && metrics->powerline_noise < 0.1f) {
        score += 10;
    } else if (metrics->baseline_wander < 0.2f && metrics->powerline_noise < 0.2f) {
        score += 5;
    }
    
    // 分级
    if (score >= 80) metrics->overall_quality = ECG_QUALITY_EXCELLENT;
    else if (score >= 60) metrics->overall_quality = ECG_QUALITY_GOOD;
    else if (score >= 40) metrics->overall_quality = ECG_QUALITY_FAIR;
    else if (score >= 20) metrics->overall_quality = ECG_QUALITY_POOR;
    else metrics->overall_quality = ECG_QUALITY_UNACCEPTABLE;
}
```

---

## 3. PPG信号质量评估

### 3.1 灌注指数（Perfusion Index）

```c
/**
 * @brief 计算PPG灌注指数
 * @param ppg_signal PPG信号
 * @param length 信号长度
 * @return 灌注指数（%）
 */
float ppg_calculate_perfusion_index(const float* ppg_signal, uint16_t length) {
    
    // 找到最大值和最小值
    float max_val = -1e6f, min_val = 1e6f;
    float sum = 0.0f;
    
    for (uint16_t i = 0; i < length; i++) {
        if (ppg_signal[i] > max_val) max_val = ppg_signal[i];
        if (ppg_signal[i] < min_val) min_val = ppg_signal[i];
        sum += ppg_signal[i];
    }
    
    float mean_val = sum / length;
    
    // AC分量（脉动）
    float ac_component = (max_val - min_val) / 2.0f;
    
    // DC分量（基线）
    float dc_component = mean_val;
    
    // 灌注指数 = (AC / DC) * 100%
    if (dc_component < 1e-6f) {
        return 0.0f;
    }
    
    float perfusion_index = (ac_component / dc_component) * 100.0f;
    
    return perfusion_index;
}

/**
 * @brief 基于灌注指数的质量评估
 */
typedef enum {
    PPG_QUALITY_EXCELLENT = 4,  // PI > 1.0%
    PPG_QUALITY_GOOD = 3,       // 0.5-1.0%
    PPG_QUALITY_FAIR = 2,       // 0.2-0.5%
    PPG_QUALITY_POOR = 1,       // 0.1-0.2%
    PPG_QUALITY_UNACCEPTABLE = 0 // < 0.1%
} PPGQualityLevel;

PPGQualityLevel ppg_classify_quality_by_pi(float perfusion_index) {
    if (perfusion_index >= 1.0f) return PPG_QUALITY_EXCELLENT;
    if (perfusion_index >= 0.5f) return PPG_QUALITY_GOOD;
    if (perfusion_index >= 0.2f) return PPG_QUALITY_FAIR;
    if (perfusion_index >= 0.1f) return PPG_QUALITY_POOR;
    return PPG_QUALITY_UNACCEPTABLE;
}
```

### 3.2 峰值检测质量

```c
/**
 * @brief 评估PPG峰值检测质量
 */
float ppg_assess_peak_quality(const float* ppg_signal, uint16_t length,
                              const uint16_t* peak_positions,
                              uint8_t peak_count) {
    
    if (peak_count < 3) {
        return 0.0f;  // 峰值太少
    }
    
    // 1. 计算峰间间隔（IBI）
    float ibi[99];
    for (uint8_t i = 0; i < peak_count - 1; i++) {
        ibi[i] = (float)(peak_positions[i + 1] - peak_positions[i]);
    }
    
    // 2. 计算IBI的变异系数（CV）
    float mean_ibi = 0.0f;
    for (uint8_t i = 0; i < peak_count - 1; i++) {
        mean_ibi += ibi[i];
    }
    mean_ibi /= (peak_count - 1);
    
    float std_ibi = 0.0f;
    for (uint8_t i = 0; i < peak_count - 1; i++) {
        float diff = ibi[i] - mean_ibi;
        std_ibi += diff * diff;
    }
    std_ibi = sqrtf(std_ibi / (peak_count - 1));
    
    float cv = std_ibi / mean_ibi;
    
    // 3. 质量评分（CV越小越好）
    float quality_score;
    if (cv < 0.1f) quality_score = 1.0f;       // 优秀
    else if (cv < 0.2f) quality_score = 0.8f;  // 良好
    else if (cv < 0.3f) quality_score = 0.6f;  // 一般
    else if (cv < 0.5f) quality_score = 0.4f;  // 较差
    else quality_score = 0.2f;                 // 很差
    
    return quality_score;
}
```

---

## 4. 实时质量监控

### 4.1 滑动窗口质量评估

```c
#define QUALITY_WINDOW_SIZE 250  // 1秒窗口（250Hz采样）

typedef struct {
    float signal_buffer[QUALITY_WINDOW_SIZE];
    uint16_t buffer_index;
    uint16_t sample_count;
    
    float current_quality;
    float quality_history[10];  // 最近10秒的质量
    uint8_t history_index;
    
    uint8_t low_quality_count;  // 连续低质量计数
} RealTimeQualityMonitor;

void quality_monitor_init(RealTimeQualityMonitor* monitor) {
    memset(monitor, 0, sizeof(RealTimeQualityMonitor));
    monitor->current_quality = 1.0f;  // 初始假设质量良好
}

/**
 * @brief 添加新样本并更新质量评估
 */
void quality_monitor_update(RealTimeQualityMonitor* monitor, float new_sample) {
    
    // 添加到缓冲区
    monitor->signal_buffer[monitor->buffer_index] = new_sample;
    monitor->buffer_index = (monitor->buffer_index + 1) % QUALITY_WINDOW_SIZE;
    
    if (monitor->sample_count < QUALITY_WINDOW_SIZE) {
        monitor->sample_count++;
        return;  // 数据不足
    }
    
    // 每秒评估一次质量
    if (monitor->buffer_index == 0) {
        // 计算当前窗口的质量指标
        float snr = calculate_window_snr(monitor->signal_buffer, QUALITY_WINDOW_SIZE);
        float stability = calculate_signal_stability(monitor->signal_buffer,
                                                     QUALITY_WINDOW_SIZE);
        
        // 综合质量评分
        monitor->current_quality = (snr * 0.6f + stability * 0.4f);
        
        // 更新历史
        monitor->quality_history[monitor->history_index] = monitor->current_quality;
        monitor->history_index = (monitor->history_index + 1) % 10;
        
        // 检测连续低质量
        if (monitor->current_quality < 0.5f) {
            monitor->low_quality_count++;
        } else {
            monitor->low_quality_count = 0;
        }
        
        // 触发报警
        if (monitor->low_quality_count >= 5) {
            // 连续5秒低质量，触发报警
            trigger_low_quality_alarm();
        }
    }
}

/**
 * @brief 获取平均质量（最近10秒）
 */
float quality_monitor_get_average(const RealTimeQualityMonitor* monitor) {
    float sum = 0.0f;
    uint8_t count = 0;
    
    for (uint8_t i = 0; i < 10; i++) {
        if (monitor->quality_history[i] > 0.0f) {
            sum += monitor->quality_history[i];
            count++;
        }
    }
    
    return (count > 0) ? (sum / count) : 0.0f;
}
```

---

## 5. 质量驱动的报警管理

```c
/**
 * @brief 质量感知的报警决策
 */
typedef struct {
    float alarm_threshold;      // 报警阈值
    float quality_threshold;    // 质量阈值
    uint8_t confirmation_count; // 确认计数
    uint8_t required_confirms;  // 需要的确认次数
} QualityAwareAlarm;

/**
 * @brief 处理报警（考虑信号质量）
 * @return 1触发报警，0抑制报警
 */
int process_alarm_with_quality(QualityAwareAlarm* alarm,
                               float measured_value,
                               float signal_quality) {
    
    // 如果信号质量太低，抑制报警
    if (signal_quality < alarm->quality_threshold) {
        alarm->confirmation_count = 0;
        return 0;  // 抑制报警
    }
    
    // 检查是否超过阈值
    if (measured_value > alarm->alarm_threshold) {
        alarm->confirmation_count++;
        
        // 根据质量调整确认次数
        uint8_t required = alarm->required_confirms;
        if (signal_quality >= 0.9f) {
            required = alarm->required_confirms / 2;  // 高质量，快速报警
        }
        
        if (alarm->confirmation_count >= required) {
            return 1;  // 触发报警
        }
    } else {
        alarm->confirmation_count = 0;
    }
    
    return 0;  // 未触发
}
```

---

## 6. 最佳实践

### 6.1 质量评估策略

| 应用场景 | 推荐方法 | 更新频率 |
|---------|---------|---------|
| 实时监护 | 滑动窗口SNR | 1秒 |
| 诊断ECG | 综合质量指标 | 每次记录 |
| 可穿戴设备 | 灌注指数 | 实时 |
| 远程监护 | 质量驱动报警 | 实时 |

### 6.2 常见陷阱

❌ **错误1：忽略信号质量直接报警**
```c
// 错误
if (heart_rate > 120) {
    trigger_alarm();  // 可能是伪影！
}

// 正确
if (heart_rate > 120 && signal_quality > 0.7f) {
    trigger_alarm();
}
```

❌ **错误2：质量阈值设置不当**
```c
// 错误：阈值太高，丢失有用数据
if (quality < 0.95f) {
    discard_data();
}

// 正确：根据应用场景设置
if (quality < 0.5f) {  // 诊断级
    discard_data();
}
```

---

## 7. 参考资料

### 论文
1. **"Signal Quality Indices for the Electrocardiogram and Photoplethysmogram" (2015)**
2. **"A Review of Signal Quality Assessment Methods for Physiological Signals" (2019)**

### 标准
1. **IEC 60601-2-27**: ECG监护设备
2. **ISO 80601-2-61**: 脉搏血氧仪

---

## 相关模块

- [数字滤波器](digital-filters.md)
- [心电信号处理](ecg-processing.md)
- [SpO2计算](spo2-calculation.md)

---

**下一步**: 综合应用所学的信号处理技术，构建完整的医疗监护系统。
