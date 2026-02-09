---
title: Class C案例：植入式心脏起搏器
description: 一个Class C医疗器械的完整开发案例，包括需求、设计、实现和验证
difficulty: 高级
estimated_time: 4小时
tags:
- 案例研究
- Class C
- 心脏起搏器
- IEC 62304
- 生命支持
related_modules:
- zh/regulatory-standards/iec-62304/software-classification
- zh/software-engineering/requirements-engineering
- zh/software-engineering/testing-strategy
- zh/regulatory-standards/iso-14971
last_updated: '2026-02-09'
version: '1.0'
language: zh-CN
---

# Class C案例：植入式心脏起搏器

## 案例概述

本案例描述一个单腔植入式心脏起搏器的软件开发过程，展示如何应用IEC 62304标准开发Class C医疗器械软件。

**设备信息**：
- **设备名称**：单腔植入式心脏起搏器
- **预期用途**：治疗心动过缓，维持患者心率
- **起搏模式**：VVI（心室按需起搏）
- **起搏频率范围**：40-120 bpm
- **起搏脉冲宽度**：0.1-1.5 ms
- **起搏输出电压**：0.5-7.5 V
- **监管分类**：Class III（欧盟）/ Class III（美国FDA）
- **软件安全分类**：Class C

## 项目背景

### 临床需求

- 治疗病态窦房结综合征
- 治疗房室传导阻滞
- 预防心动过缓引起的晕厥
- 提高患者生活质量

### 技术挑战

1. **生命支持功能**：软件故障可能直接危及生命
2. **实时性要求**：必须在严格时间约束内响应
3. **可靠性要求**：需要极高的可靠性（故障率 < 0.01%）
4. **电池寿命**：需要工作5-10年
5. **电磁兼容性**：抗干扰能力要求极高
6. **合规性**：满足IEC 62304 Class C和相关标准


## 软件安全分类

### 风险分析

根据ISO 14971进行详细风险分析：

| 危害 | 危害情况 | 后果 | 严重度 | 概率 | 风险等级 | 软件贡献 |
|------|---------|------|--------|------|---------|---------|
| 起搏失效 | 软件未检测到心动过缓 | 患者晕厥或死亡 | 灾难性 | 中等 | 不可接受 | 直接原因 |
| 过度起搏 | 软件错误导致起搏频率过高 | 心律失常、心衰 | 严重 | 低 | 不可接受 | 直接原因 |
| 感知失效 | 软件未能检测自主心跳 | 不必要的起搏、R-on-T现象 | 严重 | 中等 | 不可接受 | 直接原因 |
| 电池耗尽 | 软件未能准确监测电池 | 设备突然停止工作 | 灾难性 | 低 | 不可接受 | 直接原因 |
| 参数错误 | 软件应用错误的起搏参数 | 治疗无效或有害 | 严重 | 低 | 不可接受 | 直接原因 |

### 分类结果

**软件安全等级：Class C**

**理由**：
- 软件故障可能直接导致死亡或严重伤害
- 设备是生命支持系统
- 软件直接控制治疗功能
- 软件故障无法通过其他手段及时补救
- 需要最高级别的开发流程和文档要求

## 软件需求

### 系统需求

**SR-001：心脏感知**
- 系统应检测自主心跳
- 感知灵敏度：0.5-10 mV可调
- 感知延迟：< 50 ms
- 不应感知T波和肌电干扰

**SR-002：心室起搏**
- 系统应在需要时提供心室起搏
- 起搏频率：40-120 bpm可编程
- 起搏输出：0.5-7.5 V可编程
- 脉冲宽度：0.1-1.5 ms可编程

**SR-003：VVI模式**
- 系统应实现VVI起搏模式
- 感知到自主心跳时抑制起搏
- 未感知到心跳时按设定频率起搏

**SR-004：安全监测**
- 系统应持续监测电池电量
- 系统应检测导线故障
- 系统应检测软件异常
- 系统应在故障时进入安全模式

**SR-005：程控通信**
- 系统应支持无线程控
- 系统应验证程控命令
- 系统应记录程控历史

### 软件需求

**SWR-001：心脏信号采集**
```
需求ID：SWR-001
描述：软件应从感知放大器采集心脏电信号
优先级：关键
安全等级：Class C
验收标准：
1. 采样率：512 Hz
2. 分辨率：12位ADC
3. 采样延迟：< 2 ms
4. 连续采样，无丢失
追溯：SR-001
风险控制：R-001（起搏失效）
```

**SWR-002：心跳检测算法**
```
需求ID：SWR-002
描述：软件应检测自主心跳（R波）
优先级：关键
安全等级：Class C
验收标准：
1. 检测灵敏度：0.5-10 mV可调
2. 检测延迟：< 50 ms
3. T波抑制：不检测T波
4. 抗干扰：抑制肌电干扰
5. 检测准确率：> 99.9%
追溯：SR-001
风险控制：R-003（感知失效）
```

**SWR-003：起搏控制**
```
需求ID：SWR-003
描述：软件应控制起搏脉冲输出
优先级：关键
安全等级：Class C
验收标准：
1. 起搏频率精度：±1 bpm
2. 脉冲宽度精度：±0.01 ms
3. 输出电压精度：±0.1 V
4. 起搏延迟：< 10 ms
5. 不应在不应期内起搏
追溯：SR-002
风险控制：R-002（过度起搏）
```

**SWR-004：VVI逻辑**
```
需求ID：SWR-004
描述：软件应实现VVI起搏逻辑
优先级：关键
安全等级：Class C
验收标准：
1. 感知到R波后重置起搏定时器
2. 起搏间期到达时未感知R波则起搏
3. 起搏后进入不应期（150-400 ms可编程）
4. 不应期内不感知、不起搏
5. 逻辑执行时间：< 1 ms
追溯：SR-003
风险控制：R-001, R-002, R-003
```

**SWR-005：电池监测**
```
需求ID：SWR-005
描述：软件应监测电池电量和阻抗
优先级：关键
安全等级：Class C
验收标准：
1. 每小时测量电池电压
2. 电压精度：±10 mV
3. 电量指示器（ERI）阈值：2.4 V
4. 更换指示器（EOL）阈值：2.2 V
5. 达到EOL时进入安全模式
追溯：SR-004
风险控制：R-004（电池耗尽）
```

**SWR-006：导线监测**
```
需求ID：SWR-006
描述：软件应监测导线完整性
优先级：关键
安全等级：Class C
验收标准：
1. 每次起搏后测量导线阻抗
2. 检测导线断裂（阻抗 > 2000 Ω）
3. 检测导线短路（阻抗 < 200 Ω）
4. 检测到故障时记录并告警
追溯：SR-004
风险控制：R-001（起搏失效）
```

**SWR-007：看门狗和自检**
```
需求ID：SWR-007
描述：软件应实现看门狗和自检功能
优先级：关键
安全等级：Class C
验收标准：
1. 硬件看门狗超时：100 ms
2. 软件看门狗超时：50 ms
3. 每小时执行RAM测试
4. 每小时执行ROM CRC校验
5. 检测到故障时进入安全模式
追溯：SR-004
风险控制：所有风险
```

**SWR-008：安全模式**
```
需求ID：SWR-008
描述：软件应在检测到故障时进入安全模式
优先级：关键
安全等级：Class C
验收标准：
1. 使用固定安全参数起搏（VVI 60 bpm）
2. 禁用程控功能
3. 记录故障信息
4. 持续监测，尝试恢复
追溯：SR-004
风险控制：所有风险
```

**说明**: 此需求定义了安全模式功能，这是Class C设备的关键安全特性。当检测到故障时，系统进入安全模式，使用固定的安全参数起搏(VVI 60 bpm)，禁用程控功能，记录故障信息并持续监测，确保患者生命安全。



## 软件架构设计

### 系统架构

```
┌─────────────────────────────────────────────────────┐
│              应用层 (Application)                    │
├─────────────────────────────────────────────────────┤
│  起搏控制  │  感知检测  │  安全监测  │  程控通信  │
├─────────────────────────────────────────────────────┤
│         实时操作系统 (RTOS)                          │
├─────────────────────────────────────────────────────┤
│  任务调度  │  中断管理  │  定时器  │  同步机制  │
├─────────────────────────────────────────────────────┤
│         硬件抽象层 (HAL)                             │
├─────────────────────────────────────────────────────┤
│  ADC  │  DAC  │  Timer  │  Watchdog  │  Telemetry │
└─────────────────────────────────────────────────────┘
```

**说明**: 此架构图展示了心脏起搏器的复杂软件架构。应用层包含起搏控制、感知检测、安全监测和程控通信；中间层使用实时操作系统(RTOS)进行任务调度、中断管理和同步；硬件抽象层封装了各种硬件接口。这种多层架构确保了系统的实时性、可靠性和安全性。


### 安全架构设计

**双重冗余设计**：
- 主处理器 + 安全监督处理器
- 主处理器执行正常功能
- 监督处理器监测主处理器，检测故障

**故障检测机制**：
- 硬件看门狗（独立时钟源）
- 软件看门狗（RTOS任务监测）
- 内存完整性检查（RAM测试、ROM CRC）
- 参数范围检查
- 时序约束检查

### 模块设计

**1. 心跳检测模块（Sensing Module）**

```c
/**
 * @module SensingModule
 * @trace SWR-001, SWR-002
 * @safety_class Class C
 * @description 检测自主心跳
 */

typedef struct {
    uint16_t threshold_mv;      // 感知阈值（mV）
    uint16_t blanking_ms;       // 消隐期（ms）
    uint16_t refractory_ms;     // 不应期（ms）
    bool auto_adjust;           // 自动调整灵敏度
} sensing_config_t;

typedef enum {
    SENSE_EVENT_NONE,
    SENSE_EVENT_R_WAVE,         // 检测到R波
    SENSE_EVENT_NOISE,          // 检测到噪声
    SENSE_EVENT_FAULT           // 感知故障
} sense_event_t;

// 初始化感知模块
void sensing_init(const sensing_config_t* config);

// 处理ADC采样数据
void sensing_process_sample(uint16_t sample);

// 获取感知事件
sense_event_t sensing_get_event(void);

// 更新感知配置
bool sensing_update_config(const sensing_config_t* config);

// 获取感知统计
void sensing_get_statistics(sensing_stats_t* stats);
```

**2. 起搏控制模块（Pacing Module）**

```c
/**
 * @module PacingModule
 * @trace SWR-003, SWR-004
 * @safety_class Class C
 * @description 控制心室起搏
 */

typedef struct {
    uint16_t rate_bpm;          // 起搏频率（bpm）
    uint16_t amplitude_mv;      // 起搏幅度（mV）
    uint16_t pulse_width_us;    // 脉冲宽度（μs）
    uint16_t refractory_ms;     // 不应期（ms）
} pacing_config_t;

typedef enum {
    PACE_STATE_IDLE,
    PACE_STATE_WAITING,         // 等待起搏间期
    PACE_STATE_PACING,          // 正在起搏
    PACE_STATE_REFRACTORY,      // 不应期
    PACE_STATE_INHIBITED        // 被抑制
} pace_state_t;

// 初始化起搏模块
void pacing_init(const pacing_config_t* config);

// VVI逻辑处理
void pacing_vvi_process(sense_event_t sense_event);

// 执行起搏脉冲
void pacing_deliver_pulse(void);

// 获取起搏状态
pace_state_t pacing_get_state(void);

// 更新起搏配置
bool pacing_update_config(const pacing_config_t* config);
```

**3. 安全监测模块（Safety Monitor）**

```c
/**
 * @module SafetyMonitor
 * @trace SWR-005, SWR-006, SWR-007, SWR-008
 * @safety_class Class C
 * @description 监测系统安全状态
 */

typedef enum {
    SAFETY_OK,
    SAFETY_WARNING,             // 警告状态
    SAFETY_ERROR,               // 错误状态
    SAFETY_CRITICAL             // 严重故障
} safety_status_t;

typedef struct {
    uint16_t battery_voltage_mv;
    uint16_t lead_impedance_ohm;
    uint32_t ram_test_result;
    uint32_t rom_crc;
    bool watchdog_ok;
} safety_diagnostics_t;

// 初始化安全监测
void safety_init(void);

// 执行周期性安全检查
void safety_periodic_check(void);

// 获取安全状态
safety_status_t safety_get_status(void);

// 获取诊断信息
void safety_get_diagnostics(safety_diagnostics_t* diag);

// 进入安全模式
void safety_enter_safe_mode(void);

// 喂狗
void safety_feed_watchdog(void);
```


## 关键实现

### 心跳检测算法实现

```c
/**
 * @file sensing.c
 * @trace SWR-002
 * @safety_class Class C
 * @description 心跳检测算法实现
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "sensing.h"

#define SAMPLE_BUFFER_SIZE 256
#define BASELINE_WINDOW 128

static sensing_config_t g_config;
static uint16_t g_sample_buffer[SAMPLE_BUFFER_SIZE];
static uint16_t g_buffer_index = 0;
static int32_t g_baseline = 0;
static uint32_t g_last_sense_time = 0;
static sense_event_t g_current_event = SENSE_EVENT_NONE;

void sensing_init(const sensing_config_t* config) {
    memcpy(&g_config, config, sizeof(sensing_config_t));
    g_buffer_index = 0;
    g_baseline = 0;
    g_last_sense_time = 0;
    g_current_event = SENSE_EVENT_NONE;
}

/**
 * @brief 更新基线
 * @trace SWR-002: 抗干扰
 * @description 使用滑动窗口计算基线，抑制低频漂移
 */
static void update_baseline(uint16_t sample) {
    static int32_t baseline_sum = 0;
    static uint16_t baseline_buffer[BASELINE_WINDOW];
    static uint16_t baseline_index = 0;
    
    // 移除最旧的样本
    baseline_sum -= baseline_buffer[baseline_index];
    
    // 添加新样本
    baseline_buffer[baseline_index] = sample;
    baseline_sum += sample;
    
    // 更新索引
    baseline_index = (baseline_index + 1) % BASELINE_WINDOW;
    
    // 计算平均值
    g_baseline = baseline_sum / BASELINE_WINDOW;
}

/**
 * @brief 检测R波
 * @trace SWR-002: 检测自主心跳
 * @description 使用阈值法检测R波，包含消隐期和不应期
 */
static bool detect_r_wave(int32_t signal) {
    uint32_t current_time = system_get_tick_ms();
    
    // 检查消隐期（起搏后的短暂时间）
    if (current_time - g_last_sense_time < g_config.blanking_ms) {
        return false;
    }
    
    // 检查不应期
    if (current_time - g_last_sense_time < g_config.refractory_ms) {
        return false;
    }
    
    // 计算信号幅度（绝对值）
    int32_t amplitude = (signal > 0) ? signal : -signal;
    
    // 阈值检测
    if (amplitude > g_config.threshold_mv) {
        g_last_sense_time = current_time;
        return true;
    }
    
    return false;
}

/**
 * @brief 噪声检测
 * @trace SWR-002: 抗干扰
 * @description 检测高频噪声和肌电干扰
 */
static bool detect_noise(void) {
    // 计算最近样本的方差
    int32_t mean = 0;
    for (uint16_t i = 0; i < 32; i++) {
        uint16_t idx = (g_buffer_index - i - 1) % SAMPLE_BUFFER_SIZE;
        mean += g_sample_buffer[idx];
    }
    mean /= 32;
    
    int32_t variance = 0;
    for (uint16_t i = 0; i < 32; i++) {
        uint16_t idx = (g_buffer_index - i - 1) % SAMPLE_BUFFER_SIZE;
        int32_t diff = g_sample_buffer[idx] - mean;
        variance += diff * diff;
    }
    variance /= 32;
    
    // 高方差表示噪声
    const int32_t NOISE_THRESHOLD = 100;  // 根据实际情况调整
    return (variance > NOISE_THRESHOLD);
}

void sensing_process_sample(uint16_t sample) {
    // 存储样本
    g_sample_buffer[g_buffer_index] = sample;
    g_buffer_index = (g_buffer_index + 1) % SAMPLE_BUFFER_SIZE;
    
    // 更新基线
    update_baseline(sample);
    
    // 计算去基线信号
    int32_t signal = (int32_t)sample - g_baseline;
    
    // 检测噪声
    if (detect_noise()) {
        g_current_event = SENSE_EVENT_NOISE;
        return;
    }
    
    // 检测R波
    if (detect_r_wave(signal)) {
        g_current_event = SENSE_EVENT_R_WAVE;
        
        // 自动调整灵敏度
        if (g_config.auto_adjust) {
            // 根据检测到的R波幅度调整阈值
            int32_t amplitude = (signal > 0) ? signal : -signal;
            g_config.threshold_mv = (uint16_t)(amplitude * 0.5f);  // 50%阈值
        }
    } else {
        g_current_event = SENSE_EVENT_NONE;
    }
}

sense_event_t sensing_get_event(void) {
    sense_event_t event = g_current_event;
    g_current_event = SENSE_EVENT_NONE;  // 清除事件
    return event;
}

bool sensing_update_config(const sensing_config_t* config) {
    // 参数范围检查
    if (config->threshold_mv < 500 || config->threshold_mv > 10000) {
        return false;  // 阈值超出范围
    }
    
    if (config->refractory_ms < 150 || config->refractory_ms > 400) {
        return false;  // 不应期超出范围
    }
    
    memcpy(&g_config, config, sizeof(sensing_config_t));
    return true;
}
```

**代码说明**：
- `update_baseline()`: 使用滑动窗口计算基线，抑制低频漂移和呼吸干扰
- `detect_r_wave()`: 阈值法检测R波，包含消隐期和不应期逻辑
- `detect_noise()`: 通过方差检测高频噪声和肌电干扰
- `sensing_process_sample()`: 主处理函数，每个ADC采样调用一次
- 自动灵敏度调整：根据检测到的R波幅度动态调整阈值


### VVI起搏逻辑实现

```c
/**
 * @file pacing_vvi.c
 * @trace SWR-004
 * @safety_class Class C
 * @description VVI起搏逻辑实现
 */

#include <stdint.h>
#include <stdbool.h>
#include "pacing.h"
#include "sensing.h"
#include "safety.h"

static pacing_config_t g_config;
static pace_state_t g_state = PACE_STATE_IDLE;
static uint32_t g_state_start_time = 0;
static uint32_t g_pacing_interval_ms = 0;

void pacing_init(const pacing_config_t* config) {
    memcpy(&g_config, config, sizeof(pacing_config_t));
    
    // 计算起搏间期（ms）
    g_pacing_interval_ms = 60000 / g_config.rate_bpm;
    
    g_state = PACE_STATE_WAITING;
    g_state_start_time = system_get_tick_ms();
}

/**
 * @brief VVI状态机
 * @trace SWR-004: VVI起搏逻辑
 * @description 实现VVI模式的状态机
 */
void pacing_vvi_process(sense_event_t sense_event) {
    uint32_t current_time = system_get_tick_ms();
    uint32_t elapsed = current_time - g_state_start_time;
    
    // 喂狗
    safety_feed_watchdog();
    
    switch (g_state) {
        case PACE_STATE_IDLE:
            // 初始化后进入等待状态
            g_state = PACE_STATE_WAITING;
            g_state_start_time = current_time;
            break;
            
        case PACE_STATE_WAITING:
            // 等待起搏间期或感知事件
            
            if (sense_event == SENSE_EVENT_R_WAVE) {
                // 感知到R波，重置定时器
                g_state_start_time = current_time;
                g_state = PACE_STATE_INHIBITED;
            } else if (elapsed >= g_pacing_interval_ms) {
                // 起搏间期到达，执行起搏
                pacing_deliver_pulse();
                g_state = PACE_STATE_PACING;
                g_state_start_time = current_time;
            }
            break;
            
        case PACE_STATE_INHIBITED:
            // 感知后的短暂抑制期
            if (elapsed >= 10) {  // 10ms抑制期
                g_state = PACE_STATE_WAITING;
                g_state_start_time = current_time;
            }
            break;
            
        case PACE_STATE_PACING:
            // 起搏脉冲输出中
            if (elapsed >= (g_config.pulse_width_us / 1000)) {
                // 脉冲结束，进入不应期
                g_state = PACE_STATE_REFRACTORY;
                g_state_start_time = current_time;
            }
            break;
            
        case PACE_STATE_REFRACTORY:
            // 不应期，不感知、不起搏
            if (elapsed >= g_config.refractory_ms) {
                // 不应期结束，返回等待状态
                g_state = PACE_STATE_WAITING;
                g_state_start_time = current_time;
            }
            break;
    }
}

/**
 * @brief 执行起搏脉冲
 * @trace SWR-003: 起搏控制
 * @description 输出起搏脉冲，包含安全检查
 */
void pacing_deliver_pulse(void) {
    // 安全检查
    safety_status_t safety_status = safety_get_status();
    if (safety_status >= SAFETY_ERROR) {
        // 安全状态异常，不起搏
        return;
    }
    
    // 参数范围检查
    if (g_config.amplitude_mv < 500 || g_config.amplitude_mv > 7500) {
        safety_enter_safe_mode();
        return;
    }
    
    if (g_config.pulse_width_us < 100 || g_config.pulse_width_us > 1500) {
        safety_enter_safe_mode();
        return;
    }
    
    // 配置DAC输出
    dac_set_voltage(g_config.amplitude_mv);
    
    // 启动脉冲定时器
    timer_start_pulse(g_config.pulse_width_us);
    
    // 记录起搏事件
    telemetry_log_pace_event(g_config.amplitude_mv, g_config.pulse_width_us);
    
    // 测量导线阻抗
    uint16_t impedance = measure_lead_impedance();
    safety_update_lead_impedance(impedance);
}

pace_state_t pacing_get_state(void) {
    return g_state;
}

bool pacing_update_config(const pacing_config_t* config) {
    // 参数范围检查
    if (config->rate_bpm < 40 || config->rate_bpm > 120) {
        return false;
    }
    
    if (config->amplitude_mv < 500 || config->amplitude_mv > 7500) {
        return false;
    }
    
    if (config->pulse_width_us < 100 || config->pulse_width_us > 1500) {
        return false;
    }
    
    if (config->refractory_ms < 150 || config->refractory_ms > 400) {
        return false;
    }
    
    // 更新配置
    memcpy(&g_config, config, sizeof(pacing_config_t));
    
    // 重新计算起搏间期
    g_pacing_interval_ms = 60000 / g_config.rate_bpm;
    
    return true;
}
```

**代码说明**：
- `pacing_vvi_process()`: VVI模式状态机，处理感知事件和定时器
- 状态转换：WAITING → PACING → REFRACTORY → WAITING
- 感知到R波时：WAITING → INHIBITED → WAITING（重置定时器）
- `pacing_deliver_pulse()`: 执行起搏脉冲，包含多重安全检查
- 每次起搏后测量导线阻抗，检测导线故障


### 安全监测实现

```c
/**
 * @file safety_monitor.c
 * @trace SWR-007, SWR-008
 * @safety_class Class C
 * @description 安全监测和故障处理
 */

#include <stdint.h>
#include <stdbool.h>
#include "safety.h"

static safety_status_t g_safety_status = SAFETY_OK;
static safety_diagnostics_t g_diagnostics;
static bool g_safe_mode = false;
static uint32_t g_last_watchdog_feed = 0;

// 安全模式参数（固定）
static const pacing_config_t SAFE_MODE_CONFIG = {
    .rate_bpm = 60,
    .amplitude_mv = 3500,
    .pulse_width_us = 500,
    .refractory_ms = 250
};

void safety_init(void) {
    g_safety_status = SAFETY_OK;
    g_safe_mode = false;
    g_last_watchdog_feed = system_get_tick_ms();
    
    // 初始化硬件看门狗
    watchdog_init(100);  // 100ms超时
    
    // 执行初始自检
    safety_periodic_check();
}

/**
 * @brief RAM测试
 * @trace SWR-007: RAM测试
 * @description 使用March算法测试RAM
 */
static bool test_ram(void) {
    // 简化的RAM测试（实际应使用March C-算法）
    volatile uint32_t* ram_start = (uint32_t*)0x20000000;
    volatile uint32_t* ram_end = (uint32_t*)0x20001000;
    
    // 保存原始数据
    uint32_t backup[256];
    for (uint32_t i = 0; i < 256; i++) {
        backup[i] = ram_start[i];
    }
    
    // 写入测试模式
    for (uint32_t i = 0; i < 256; i++) {
        ram_start[i] = 0xAAAAAAAA;
    }
    
    // 验证
    for (uint32_t i = 0; i < 256; i++) {
        if (ram_start[i] != 0xAAAAAAAA) {
            return false;
        }
    }
    
    // 写入反向模式
    for (uint32_t i = 0; i < 256; i++) {
        ram_start[i] = 0x55555555;
    }
    
    // 验证
    for (uint32_t i = 0; i < 256; i++) {
        if (ram_start[i] != 0x55555555) {
            return false;
        }
    }
    
    // 恢复原始数据
    for (uint32_t i = 0; i < 256; i++) {
        ram_start[i] = backup[i];
    }
    
    return true;
}

/**
 * @brief ROM CRC校验
 * @trace SWR-007: ROM CRC校验
 * @description 验证程序代码完整性
 */
static bool test_rom(void) {
    const uint32_t* rom_start = (uint32_t*)0x08000000;
    const uint32_t rom_size = 0x10000;  // 64KB
    
    // 计算CRC32
    uint32_t crc = crc32_calculate(rom_start, rom_size);
    
    // 与存储的CRC比较
    const uint32_t EXPECTED_CRC = 0x12345678;  // 编译时计算
    
    return (crc == EXPECTED_CRC);
}

/**
 * @brief 电池监测
 * @trace SWR-005: 电池监测
 */
static void check_battery(void) {
    uint16_t voltage_mv = adc_read_battery_voltage();
    g_diagnostics.battery_voltage_mv = voltage_mv;
    
    if (voltage_mv < 2200) {
        // EOL - 更换指示器
        g_safety_status = SAFETY_CRITICAL;
        safety_enter_safe_mode();
    } else if (voltage_mv < 2400) {
        // ERI - 电量指示器
        if (g_safety_status < SAFETY_WARNING) {
            g_safety_status = SAFETY_WARNING;
        }
    }
}

/**
 * @brief 导线监测
 * @trace SWR-006: 导线监测
 */
static void check_lead(void) {
    uint16_t impedance = g_diagnostics.lead_impedance_ohm;
    
    if (impedance > 2000) {
        // 导线断裂
        g_safety_status = SAFETY_ERROR;
        telemetry_log_fault(FAULT_LEAD_OPEN);
    } else if (impedance < 200) {
        // 导线短路
        g_safety_status = SAFETY_ERROR;
        telemetry_log_fault(FAULT_LEAD_SHORT);
    }
}

/**
 * @brief 看门狗检查
 * @trace SWR-007: 看门狗
 */
static void check_watchdog(void) {
    uint32_t current_time = system_get_tick_ms();
    uint32_t elapsed = current_time - g_last_watchdog_feed;
    
    if (elapsed > 50) {
        // 软件看门狗超时
        g_diagnostics.watchdog_ok = false;
        g_safety_status = SAFETY_CRITICAL;
        safety_enter_safe_mode();
    } else {
        g_diagnostics.watchdog_ok = true;
    }
}

void safety_periodic_check(void) {
    // 每小时执行一次完整检查
    static uint32_t last_full_check = 0;
    uint32_t current_time = system_get_tick_ms();
    
    if (current_time - last_full_check >= 3600000) {  // 1小时
        // RAM测试
        if (!test_ram()) {
            g_diagnostics.ram_test_result = 0xFFFFFFFF;
            g_safety_status = SAFETY_CRITICAL;
            safety_enter_safe_mode();
        } else {
            g_diagnostics.ram_test_result = 0;
        }
        
        // ROM CRC校验
        if (!test_rom()) {
            g_diagnostics.rom_crc = 0xFFFFFFFF;
            g_safety_status = SAFETY_CRITICAL;
            safety_enter_safe_mode();
        } else {
            g_diagnostics.rom_crc = 0;
        }
        
        last_full_check = current_time;
    }
    
    // 每次调用都执行的检查
    check_battery();
    check_lead();
    check_watchdog();
}

safety_status_t safety_get_status(void) {
    return g_safety_status;
}

void safety_get_diagnostics(safety_diagnostics_t* diag) {
    memcpy(diag, &g_diagnostics, sizeof(safety_diagnostics_t));
}

/**
 * @brief 进入安全模式
 * @trace SWR-008: 安全模式
 * @description 使用固定安全参数继续起搏
 */
void safety_enter_safe_mode(void) {
    if (g_safe_mode) {
        return;  // 已经在安全模式
    }
    
    g_safe_mode = true;
    
    // 记录故障
    telemetry_log_fault(FAULT_SAFE_MODE_ENTRY);
    
    // 应用安全模式参数
    pacing_update_config(&SAFE_MODE_CONFIG);
    
    // 禁用程控
    telemetry_disable_programming();
    
    // 持续监测，尝试恢复
    // （实际实现中会有更复杂的恢复逻辑）
}

void safety_feed_watchdog(void) {
    g_last_watchdog_feed = system_get_tick_ms();
    watchdog_feed();  // 喂硬件看门狗
}

void safety_update_lead_impedance(uint16_t impedance) {
    g_diagnostics.lead_impedance_ohm = impedance;
}
```

**代码说明**：
- `test_ram()`: 使用March算法测试RAM完整性
- `test_rom()`: 使用CRC32验证程序代码完整性
- `check_battery()`: 监测电池电压，检测ERI和EOL
- `check_lead()`: 监测导线阻抗，检测断裂和短路
- `safety_enter_safe_mode()`: 进入安全模式，使用固定参数继续起搏
- 双重看门狗：硬件看门狗（100ms）+ 软件看门狗（50ms）


## 测试策略

### 单元测试

**测试用例TC-001：心跳检测测试**

```c
/**
 * @test TC-001
 * @trace SWR-002
 * @description 测试心跳检测算法
 */
void test_r_wave_detection(void) {
    sensing_config_t config = {
        .threshold_mv = 2000,
        .blanking_ms = 50,
        .refractory_ms = 250,
        .auto_adjust = false
    };
    
    sensing_init(&config);
    
    // 模拟正常心跳信号
    uint16_t normal_signal[] = {
        2048, 2048, 2048, 2048,  // 基线
        2048, 2100, 2200, 2500,  // R波上升
        3000, 3500, 3800, 3500,  // R波峰值
        3000, 2500, 2200, 2100,  // R波下降
        2048, 2048, 2048, 2048   // 返回基线
    };
    
    sense_event_t event = SENSE_EVENT_NONE;
    
    for (uint16_t i = 0; i < sizeof(normal_signal)/sizeof(uint16_t); i++) {
        sensing_process_sample(normal_signal[i]);
        sense_event_t e = sensing_get_event();
        if (e == SENSE_EVENT_R_WAVE) {
            event = e;
        }
    }
    
    // 验证检测到R波
    assert(event == SENSE_EVENT_R_WAVE);
}
```

**测试用例TC-002：VVI逻辑测试**

```c
/**
 * @test TC-002
 * @trace SWR-004
 * @description 测试VVI起搏逻辑
 */
void test_vvi_logic(void) {
    pacing_config_t config = {
        .rate_bpm = 60,
        .amplitude_mv = 3500,
        .pulse_width_us = 500,
        .refractory_ms = 250
    };
    
    pacing_init(&config);
    
    // 测试场景1：无感知事件，应该起搏
    for (uint32_t i = 0; i < 1000; i++) {
        pacing_vvi_process(SENSE_EVENT_NONE);
        system_delay_ms(1);
    }
    
    // 验证起搏发生
    assert(pacing_get_state() == PACE_STATE_REFRACTORY ||
           pacing_get_state() == PACE_STATE_WAITING);
    
    // 测试场景2：感知到R波，应该抑制起搏
    pacing_init(&config);
    
    for (uint32_t i = 0; i < 500; i++) {
        // 每500ms模拟一次R波（120 bpm）
        sense_event_t event = (i % 500 == 0) ? SENSE_EVENT_R_WAVE : SENSE_EVENT_NONE;
        pacing_vvi_process(event);
        system_delay_ms(1);
    }
    
    // 验证起搏被抑制
    assert(pacing_get_state() == PACE_STATE_INHIBITED ||
           pacing_get_state() == PACE_STATE_WAITING);
}
```

**测试用例TC-003：安全监测测试**

```c
/**
 * @test TC-003
 * @trace SWR-007
 * @description 测试安全监测功能
 */
void test_safety_monitoring(void) {
    safety_init();
    
    // 测试RAM
    bool ram_ok = test_ram();
    assert(ram_ok == true);
    
    // 测试ROM
    bool rom_ok = test_rom();
    assert(rom_ok == true);
    
    // 测试看门狗
    safety_feed_watchdog();
    system_delay_ms(40);
    safety_periodic_check();
    assert(safety_get_status() == SAFETY_OK);
    
    // 模拟看门狗超时
    system_delay_ms(60);
    safety_periodic_check();
    assert(safety_get_status() == SAFETY_CRITICAL);
}
```

### 集成测试

**测试用例TC-010：完整起搏流程**

```c
/**
 * @test TC-010
 * @trace SWR-001, SWR-002, SWR-003, SWR-004
 * @description 测试完整的感知-起搏流程
 */
void test_complete_pacing_cycle(void) {
    // 初始化系统
    system_init();
    
    // 配置参数
    pacing_config_t pace_config = {
        .rate_bpm = 60,
        .amplitude_mv = 3500,
        .pulse_width_us = 500,
        .refractory_ms = 250
    };
    pacing_init(&pace_config);
    
    sensing_config_t sense_config = {
        .threshold_mv = 2000,
        .blanking_ms = 50,
        .refractory_ms = 250,
        .auto_adjust = true
    };
    sensing_init(&sense_config);
    
    // 运行10秒
    for (uint32_t i = 0; i < 10000; i++) {
        // 采集心电信号
        uint16_t sample = adc_read_ecg();
        sensing_process_sample(sample);
        
        // 获取感知事件
        sense_event_t event = sensing_get_event();
        
        // VVI逻辑处理
        pacing_vvi_process(event);
        
        // 安全监测
        if (i % 1000 == 0) {
            safety_periodic_check();
        }
        
        // 喂狗
        safety_feed_watchdog();
        
        system_delay_ms(1);
    }
    
    // 验证系统正常运行
    assert(safety_get_status() <= SAFETY_WARNING);
}
```

### 系统测试

**测试用例TC-020：临床验证**

根据ISO 14708-2标准进行临床验证：

1. **感知性能测试**
   - 测试对象：20名患者
   - 测试条件：不同心率、不同R波幅度
   - 验收标准：感知准确率 > 99.9%

2. **起搏性能测试**
   - 测试对象：20名患者
   - 测试条件：不同起搏参数
   - 验收标准：起搏捕获率 > 99.5%

3. **VVI模式验证**
   - 验证感知后抑制起搏
   - 验证起搏间期准确性
   - 验证不应期功能

**测试用例TC-021：可靠性测试**

- 连续运行测试：7天 × 24小时
- 加速老化测试：模拟5年使用
- 故障注入测试：验证故障检测和安全模式
- 电磁兼容性测试：IEC 60601-1-2

**测试用例TC-022：安全功能测试**

| 测试项 | 测试方法 | 预期结果 |
|-------|---------|---------|
| 电池耗尽 | 降低电池电压至EOL | 进入安全模式，60 bpm起搏 |
| 导线断裂 | 模拟高阻抗 | 检测故障，记录事件 |
| RAM故障 | 注入RAM错误 | 检测故障，进入安全模式 |
| ROM损坏 | 修改ROM数据 | CRC校验失败，进入安全模式 |
| 看门狗超时 | 阻塞主循环 | 硬件复位，恢复运行 |


## 验证和确认

### 软件验证

- ✓ 所有单元测试通过（覆盖率 > 95%）
- ✓ 所有集成测试通过
- ✓ 代码审查完成（无严重缺陷）
- ✓ 静态分析通过（MISRA C强制规则100%合规）
- ✓ 动态分析通过（无内存泄漏、无死锁）
- ✓ 需求追溯完整（100%双向追溯）
- ✓ 设计追溯完整（100%双向追溯）

### 软件确认

- ✓ 系统测试通过
- ✓ 临床验证通过（ISO 14708-2）
- ✓ 可靠性测试通过（MTBF > 10年）
- ✓ 安全功能测试通过
- ✓ 电磁兼容性测试通过（IEC 60601-1-2）
- ✓ 环境测试通过（温度、湿度、振动）

### 风险管理

**风险控制措施验证**：

| 风险 | 控制措施 | 验证方法 | 验证结果 |
|------|---------|---------|---------|
| R-001: 起搏失效 | 双重冗余、看门狗、安全模式 | 故障注入测试 | 通过 |
| R-002: 过度起搏 | 参数范围检查、频率限制 | 边界值测试 | 通过 |
| R-003: 感知失效 | 自动灵敏度调整、噪声检测 | 临床验证 | 通过 |
| R-004: 电池耗尽 | 电池监测、ERI/EOL警告 | 电池寿命测试 | 通过 |
| R-005: 导线故障 | 阻抗监测、故障检测 | 导线故障模拟 | 通过 |

**剩余风险评估**：

所有剩余风险均降低至ALARP（As Low As Reasonably Practicable）水平，符合ISO 14971要求。

## 文档模板

### Class C软件开发计划（SDP）模板

```markdown
# 软件开发计划

## 1. 项目概述
### 1.1 项目背景
### 1.2 软件安全分类：Class C
### 1.3 适用标准

## 2. 组织和职责
### 2.1 项目组织结构
### 2.2 角色和职责
### 2.3 培训要求

## 3. 开发流程
### 3.1 生命周期模型（V模型）
### 3.2 开发阶段
### 3.3 里程碑和交付物

## 4. 需求管理
### 4.1 需求收集
### 4.2 需求分析
### 4.3 需求追溯

## 5. 设计和实现
### 5.1 架构设计
### 5.2 详细设计
### 5.3 编码标准（MISRA C）
### 5.4 代码审查

## 6. 验证和确认
### 6.1 单元测试
### 6.2 集成测试
### 6.3 系统测试
### 6.4 临床验证

## 7. 风险管理
### 7.1 风险分析
### 7.2 风险控制
### 7.3 剩余风险评估

## 8. 配置管理
### 8.1 版本控制
### 8.2 变更控制
### 8.3 基线管理

## 9. 问题解决
### 9.1 问题报告
### 9.2 问题分析
### 9.3 问题解决

## 10. 文档管理
### 10.1 文档清单
### 10.2 文档审查
### 10.3 文档归档
```

### 软件风险管理文件（SRMF）模板

```markdown
# 软件风险管理文件

## 1. 风险分析
### 1.1 危害识别
### 1.2 危害情况分析
### 1.3 风险评估

## 2. 风险控制
### 2.1 风险控制措施
### 2.2 控制措施实现
### 2.3 控制措施验证

## 3. 剩余风险评估
### 3.1 剩余风险分析
### 3.2 风险可接受性评估
### 3.3 风险效益分析

## 4. 风险追溯矩阵
| 风险ID | 危害 | 控制措施 | 软件需求 | 验证方法 | 状态 |
|--------|------|---------|---------|---------|------|
```

### 软件验证报告（SVR）模板

```markdown
# 软件验证报告

## 1. 验证概述
### 1.1 验证范围
### 1.2 验证方法
### 1.3 验证环境

## 2. 单元测试结果
### 2.1 测试覆盖率
### 2.2 测试用例执行结果
### 2.3 缺陷统计

## 3. 集成测试结果
### 3.1 接口测试
### 3.2 功能测试
### 3.3 缺陷统计

## 4. 系统测试结果
### 4.1 功能测试
### 4.2 性能测试
### 4.3 安全测试
### 4.4 可靠性测试

## 5. 追溯验证
### 5.1 需求覆盖率
### 5.2 设计覆盖率
### 5.3 追溯矩阵

## 6. 验证结论
### 6.1 验证完整性
### 6.2 未解决问题
### 6.3 验证批准
```

## 经验教训

### 成功经验

1. **严格的流程管理**
   - 遵循IEC 62304 Class C要求
   - 完整的文档和追溯
   - 多层次的审查和批准

2. **安全优先设计**
   - 双重冗余架构
   - 多重故障检测机制
   - 安全模式保证基本功能

3. **全面的测试策略**
   - 单元测试覆盖率 > 95%
   - 集成测试覆盖所有接口
   - 系统测试包含临床验证
   - 故障注入测试验证安全功能

4. **持续的风险管理**
   - 贯穿整个生命周期
   - 及时识别和控制新风险
   - 验证所有控制措施有效性

### 遇到的挑战

1. **实时性要求**
   - **问题**：严格的时间约束（感知延迟 < 50ms）
   - **解决**：使用RTOS，优化中断处理，减少任务切换开销

2. **电磁干扰**
   - **问题**：MRI和除颤器干扰
   - **解决**：增强滤波算法，实现噪声检测和抑制

3. **电池寿命**
   - **问题**：需要工作5-10年
   - **解决**：优化功耗，使用低功耗硬件，实现智能电源管理

4. **软件复杂度**
   - **问题**：Class C要求导致代码和文档量大
   - **解决**：模块化设计，自动化测试和文档生成

### Class C开发特点

1. **最高级别要求**
   - 完整的软件开发计划
   - 详细的架构和设计文档
   - 全面的验证和确认
   - 完整的追溯矩阵

2. **严格的质量控制**
   - 代码审查（100%覆盖）
   - 静态分析（MISRA C强制规则）
   - 动态分析（内存、性能）
   - 独立验证和确认

3. **持续的风险管理**
   - 详细的风险分析
   - 多层次的风险控制
   - 验证所有控制措施
   - 剩余风险评估

4. **长期维护**
   - 问题报告和追踪系统
   - 变更控制流程
   - 定期安全更新
   - 上市后监测

### 改进建议

1. **技术改进**
   - 实现自适应算法（根据患者特征调整参数）
   - 增加远程监测功能
   - 支持多腔起搏（DDD模式）
   - 集成心律失常检测

2. **流程改进**
   - 增加自动化测试覆盖率
   - 实现持续集成/持续部署
   - 优化文档生成流程
   - 加强供应商管理

3. **质量改进**
   - 实施形式化验证方法
   - 增加模型检查
   - 加强网络安全防护
   - 提高软件可维护性

## 总结

本案例展示了Class C医疗器械软件的完整开发过程，包括：

- 基于风险的软件安全分类（Class C - 最高级别）
- 详细的需求分析和追溯
- 安全优先的架构设计（双重冗余、故障检测）
- 关键算法的实现（心跳检测、VVI逻辑、安全监测）
- 全面的测试策略（单元、集成、系统、临床）
- 完整的验证和确认
- 符合IEC 62304 Class C的所有文档要求

**Class C软件的关键特点**：
- 软件故障可能直接导致死亡或严重伤害
- 需要最高级别的开发流程和质量控制
- 完整的文档和追溯要求
- 严格的验证和确认
- 持续的风险管理
- 独立的安全评估

通过遵循IEC 62304标准的Class C要求，并实施严格的质量管理和风险控制，成功开发了一个安全、可靠、有效的生命支持医疗器械软件系统。

## 参考资料

1. IEC 62304:2006+AMD1:2015 - Medical device software - Software life cycle processes
2. ISO 14708-2:2019 - Implants for surgery - Active implantable medical devices - Part 2: Cardiac pacemakers
3. ISO 14971:2019 - Medical devices - Application of risk management to medical devices
4. IEC 60601-1:2005+AMD1:2012 - Medical electrical equipment - Part 1: General requirements for basic safety and essential performance
5. IEC 60601-1-2:2014 - Medical electrical equipment - Part 1-2: General requirements for basic safety and essential performance - Collateral standard: Electromagnetic disturbances
6. FDA Guidance - Content of Premarket Submissions for Software Contained in Medical Devices
7. AAMI TIR45:2012 - Guidance on the use of AGILE practices in the development of medical device software

