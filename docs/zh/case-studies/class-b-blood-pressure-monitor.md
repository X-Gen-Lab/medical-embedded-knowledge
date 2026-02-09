---
title: Class B案例：电子血压监测仪
description: 一个Class B医疗器械的完整开发案例，包括需求、设计、实现和验证
difficulty: 中级
estimated_time: 3小时
tags:
- 案例研究
- Class B
- 血压监测
- IEC 62304
related_modules:
- zh/regulatory-standards/iec-62304/software-classification
- zh/software-engineering/requirements-engineering
- zh/software-engineering/testing-strategy
last_updated: '2026-02-07'
version: '1.0'
language: zh-CN
---

# Class B案例：电子血压监测仪

## 案例概述

本案例描述一个家用电子血压监测仪的软件开发过程，展示如何应用IEC 62304标准开发Class B医疗器械软件。

**设备信息**：
- **设备名称**：智能电子血压监测仪
- **预期用途**：家庭环境下测量成人上臂血压
- **测量范围**：
  - 收缩压：60-260 mmHg
  - 舒张压：40-200 mmHg
  - 脉率：40-180 bpm
- **测量方法**：示波法
- **监管分类**：Class IIa（欧盟）/ Class II（美国FDA）
- **软件安全分类**：Class B

## 项目背景

### 市场需求

- 家庭血压监测需求增长
- 用户需要简单易用的设备
- 需要数据存储和趋势分析功能
- 支持多用户使用

### 技术挑战

1. **测量准确性**：确保血压测量符合临床标准
2. **用户体验**：简化操作流程，适合老年用户
3. **数据管理**：存储和管理历史测量数据
4. **电源管理**：优化电池使用时间
5. **合规性**：满足IEC 62304和相关标准

## 软件安全分类

### 风险分析

根据ISO 14971进行风险分析：

| 危害 | 危害情况 | 后果 | 严重度 | 软件贡献 |
|------|---------|------|--------|---------|
| 错误的血压读数 | 软件算法错误导致读数偏高 | 患者可能未及时就医 | 中等 | 直接原因 |
| 错误的血压读数 | 软件算法错误导致读数偏低 | 患者可能过度担心 | 轻微 | 直接原因 |
| 过度充气 | 软件控制错误导致袖带压力过高 | 用户不适，可能造成瘀伤 | 轻微 | 直接原因 |
| 数据丢失 | 存储模块故障 | 历史数据丢失 | 可忽略 | 直接原因 |

### 分类结果

**软件安全等级：Class B**

**理由**：
- 软件故障可能导致错误的血压读数
- 错误读数可能导致延误诊断或不必要的担心
- 但不太可能直接导致严重伤害或死亡
- 通常会通过多次测量或医生复查验证

## 软件需求

### 系统需求

**SR-001：血压测量**
- 系统应测量收缩压、舒张压和脉率
- 测量范围和精度应符合ISO 81060-2标准

**SR-002：用户界面**
- 系统应提供简单直观的用户界面
- 支持一键测量操作

**SR-003：数据存储**
- 系统应存储至少90次测量记录
- 支持多用户（最多4个用户）

**SR-004：电源管理**
- 系统应使用4节AA电池
- 电池寿命应支持至少300次测量

### 软件需求

**SWR-001：测量控制**
```
需求ID：SWR-001
描述：软件应控制充气泵和放气阀，实现血压测量过程
优先级：高
安全等级：Class B
验收标准：
1. 充气速率：4-8 mmHg/s
2. 目标压力：收缩压估计值 + 30 mmHg
3. 放气速率：2-4 mmHg/s
4. 测量时间：不超过60秒
追溯：SR-001
```

**SWR-002：示波法算法**
```
需求ID：SWR-002
描述：软件应使用示波法算法计算血压值
优先级：高
安全等级：Class B
验收标准：
1. 检测脉搏波动
2. 识别最大振幅点（平均压）
3. 计算收缩压和舒张压
4. 精度符合ISO 81060-2（±3 mmHg）
追溯：SR-001
```

**SWR-003：数据存储**
```
需求ID：SWR-003
描述：软件应存储测量数据到非易失性存储器
优先级：中
安全等级：Class B
验收标准：
1. 存储至少90条记录
2. 每条记录包含：日期、时间、收缩压、舒张压、脉率、用户ID
3. 数据完整性校验（CRC）
4. 存储器满时覆盖最旧记录
追溯：SR-003
```

**SWR-004：用户界面**
```
需求ID：SWR-004
描述：软件应提供LCD显示和按键输入
优先级：中
安全等级：Class B
验收标准：
1. 显示测量结果（大字体）
2. 显示日期时间
3. 显示电池电量
4. 支持用户切换和历史查看
追溯：SR-002
```

**SWR-005：错误处理**
```
需求ID：SWR-005
描述：软件应检测和处理测量错误
优先级：高
安全等级：Class B
验收标准：
1. 检测运动干扰
2. 检测心律不齐
3. 检测袖带松脱
4. 显示错误代码和提示
追溯：SR-001
```

**说明**: 此需求定义了测量错误检测功能，对于Class B设备至关重要。系统需要检测运动干扰、心律不齐、袖带松脱等异常情况，并显示相应的错误代码和提示，确保测量结果的可靠性和患者安全。


## 软件架构设计

### 系统架构

```
┌─────────────────────────────────────────┐
│           应用层 (Application)           │
├─────────────────────────────────────────┤
│  测量控制  │  算法处理  │  数据管理  │  UI │
├─────────────────────────────────────────┤
│         硬件抽象层 (HAL)                 │
├─────────────────────────────────────────┤
│  ADC  │  PWM  │  GPIO  │  I2C  │  RTC  │
└─────────────────────────────────────────┘
```

**说明**: 此架构图展示了血压监测设备的软件分层设计。应用层包含测量控制、算法处理、数据管理和UI模块；硬件抽象层封装了ADC(模数转换)、PWM(脉宽调制)、GPIO、I2C和RTC等硬件接口，实现了清晰的模块划分和职责分离。


### 模块设计

**1. 测量控制模块（Measurement Control）**

```c
/**
 * @module MeasurementControl
 * @trace SWR-001
 * @description 控制血压测量过程
 */

typedef enum {
    MEAS_STATE_IDLE,
    MEAS_STATE_INFLATE,
    MEAS_STATE_MEASURE,
    MEAS_STATE_DEFLATE,
    MEAS_STATE_COMPLETE,
    MEAS_STATE_ERROR
} measurement_state_t;

typedef struct {
    measurement_state_t state;
    uint16_t target_pressure;
    uint16_t current_pressure;
    uint32_t start_time;
} measurement_context_t;

// 初始化测量
void measurement_init(void);

// 开始测量
bool measurement_start(void);

// 测量状态机
void measurement_process(void);

// 停止测量
void measurement_stop(void);

// 获取测量结果
bool measurement_get_result(bp_result_t* result);
```

**2. 示波法算法模块（Oscillometric Algorithm）**

```c
/**
 * @module OscillometricAlgorithm
 * @trace SWR-002
 * @description 实现示波法血压计算算法
 */

#define MAX_SAMPLES 1000

typedef struct {
    uint16_t pressure[MAX_SAMPLES];
    int16_t oscillation[MAX_SAMPLES];
    uint16_t sample_count;
} oscillometric_data_t;

typedef struct {
    uint16_t systolic;
    uint16_t diastolic;
    uint16_t mean;
    uint16_t pulse_rate;
    bool valid;
} bp_result_t;

// 初始化算法
void algorithm_init(void);

// 添加采样数据
void algorithm_add_sample(uint16_t pressure, int16_t oscillation);

// 计算血压
bool algorithm_calculate(bp_result_t* result);

// 重置算法
void algorithm_reset(void);
```

**3. 数据管理模块（Data Management）**

```c
/**
 * @module DataManagement
 * @trace SWR-003
 * @description 管理测量数据存储
 */

#define MAX_RECORDS 90
#define MAX_USERS 4

typedef struct {
    uint32_t timestamp;
    uint8_t user_id;
    uint16_t systolic;
    uint16_t diastolic;
    uint16_t pulse_rate;
    uint16_t crc;
} measurement_record_t;

// 初始化数据管理
void data_init(void);

// 保存测量记录
bool data_save_record(uint8_t user_id, const bp_result_t* result);

// 读取记录
bool data_read_record(uint8_t user_id, uint16_t index, measurement_record_t* record);

// 获取记录数量
uint16_t data_get_record_count(uint8_t user_id);

// 清除用户数据
void data_clear_user(uint8_t user_id);
```

## 关键实现

### 示波法算法实现

```c
/**
 * @file oscillometric.c
 * @trace SWR-002
 * @description 示波法血压计算算法实现
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "oscillometric.h"

static oscillometric_data_t g_osc_data;

void algorithm_init(void) {
    memset(&g_osc_data, 0, sizeof(g_osc_data));
}

void algorithm_add_sample(uint16_t pressure, int16_t oscillation) {
    if (g_osc_data.sample_count < MAX_SAMPLES) {
        g_osc_data.pressure[g_osc_data.sample_count] = pressure;
        g_osc_data.oscillation[g_osc_data.sample_count] = oscillation;
        g_osc_data.sample_count++;
    }
}

/**
 * @brief 查找最大振幅点
 * @trace SWR-002: 识别最大振幅点（平均压）
 */
static uint16_t find_max_amplitude_index(void) {
    uint16_t max_index = 0;
    int16_t max_amplitude = 0;
    
    for (uint16_t i = 0; i < g_osc_data.sample_count; i++) {
        if (g_osc_data.oscillation[i] > max_amplitude) {
            max_amplitude = g_osc_data.oscillation[i];
            max_index = i;
        }
    }
    
    return max_index;
}

/**
 * @brief 计算收缩压
 * @trace SWR-002: 计算收缩压
 * @description 收缩压对应振幅为最大振幅的50-60%的点
 */
static uint16_t calculate_systolic(uint16_t map_index, int16_t max_amplitude) {
    int16_t threshold = max_amplitude * 55 / 100;  // 55%阈值
    
    // 从最大振幅点向高压方向搜索
    for (int i = map_index; i >= 0; i--) {
        if (g_osc_data.oscillation[i] <= threshold) {
            return g_osc_data.pressure[i];
        }
    }
    
    return 0;  // 未找到
}

/**
 * @brief 计算舒张压
 * @trace SWR-002: 计算舒张压
 * @description 舒张压对应振幅为最大振幅的70-80%的点
 */
static uint16_t calculate_diastolic(uint16_t map_index, int16_t max_amplitude) {
    int16_t threshold = max_amplitude * 75 / 100;  // 75%阈值
    
    // 从最大振幅点向低压方向搜索
    for (uint16_t i = map_index; i < g_osc_data.sample_count; i++) {
        if (g_osc_data.oscillation[i] <= threshold) {
            return g_osc_data.pressure[i];
        }
    }
    
    return 0;  // 未找到
}

/**
 * @brief 计算脉率
 * @trace SWR-002: 计算脉率
 */
static uint16_t calculate_pulse_rate(void) {
    uint16_t pulse_count = 0;
    int16_t threshold = 0;
    bool above_threshold = false;
    
    // 计算阈值（平均振幅的30%）
    int32_t sum = 0;
    for (uint16_t i = 0; i < g_osc_data.sample_count; i++) {
        sum += g_osc_data.oscillation[i];
    }
    threshold = (sum / g_osc_data.sample_count) * 30 / 100;
    
    // 计数脉搏
    for (uint16_t i = 0; i < g_osc_data.sample_count; i++) {
        if (g_osc_data.oscillation[i] > threshold) {
            if (!above_threshold) {
                pulse_count++;
                above_threshold = true;
            }
        } else {
            above_threshold = false;
        }
    }
    
    // 转换为bpm（假设采样率100Hz，测量时间约30秒）
    uint16_t pulse_rate = (pulse_count * 60 * 100) / g_osc_data.sample_count;
    
    return pulse_rate;
}

bool algorithm_calculate(bp_result_t* result) {
    if (g_osc_data.sample_count < 100) {
        return false;  // 数据不足
    }
    
    // 查找最大振幅点（平均压）
    uint16_t map_index = find_max_amplitude_index();
    int16_t max_amplitude = g_osc_data.oscillation[map_index];
    
    // 计算血压值
    result->mean = g_osc_data.pressure[map_index];
    result->systolic = calculate_systolic(map_index, max_amplitude);
    result->diastolic = calculate_diastolic(map_index, max_amplitude);
    result->pulse_rate = calculate_pulse_rate();
    
    // 验证结果有效性
    result->valid = (result->systolic >= 60 && result->systolic <= 260 &&
                    result->diastolic >= 40 && result->diastolic <= 200 &&
                    result->systolic > result->diastolic &&
                    result->pulse_rate >= 40 && result->pulse_rate <= 180);
    
    return result->valid;
}

void algorithm_reset(void) {
    g_osc_data.sample_count = 0;
}
```

### 数据存储实现

```c
/**
 * @file data_management.c
 * @trace SWR-003
 * @description 测量数据存储管理
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "data_management.h"
#include "eeprom.h"
#include "rtc.h"

#define EEPROM_BASE_ADDR 0x0000
#define RECORD_SIZE sizeof(measurement_record_t)

static uint16_t g_record_indices[MAX_USERS];

void data_init(void) {
    // 读取每个用户的记录索引
    for (uint8_t user = 0; user < MAX_USERS; user++) {
        uint16_t addr = EEPROM_BASE_ADDR + user * 2;
        eeprom_read(addr, (uint8_t*)&g_record_indices[user], 2);
        
        // 验证索引有效性
        if (g_record_indices[user] >= MAX_RECORDS) {
            g_record_indices[user] = 0;
        }
    }
}

/**
 * @brief 计算CRC校验
 * @trace SWR-003: 数据完整性校验
 */
static uint16_t calculate_crc(const measurement_record_t* record) {
    uint16_t crc = 0xFFFF;
    const uint8_t* data = (const uint8_t*)record;
    size_t len = sizeof(measurement_record_t) - sizeof(uint16_t);  // 不包括CRC字段
    
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x0001) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc = crc >> 1;
            }
        }
    }
    
    return crc;
}

bool data_save_record(uint8_t user_id, const bp_result_t* result) {
    if (user_id >= MAX_USERS || !result->valid) {
        return false;
    }
    
    // 准备记录
    measurement_record_t record;
    record.timestamp = rtc_get_timestamp();
    record.user_id = user_id;
    record.systolic = result->systolic;
    record.diastolic = result->diastolic;
    record.pulse_rate = result->pulse_rate;
    record.crc = calculate_crc(&record);
    
    // 计算存储地址
    uint16_t index = g_record_indices[user_id];
    uint16_t addr = EEPROM_BASE_ADDR + (MAX_USERS * 2) + 
                   (user_id * MAX_RECORDS + index) * RECORD_SIZE;
    
    // 写入EEPROM
    if (!eeprom_write(addr, (const uint8_t*)&record, RECORD_SIZE)) {
        return false;
    }
    
    // 更新索引（循环覆盖）
    g_record_indices[user_id] = (index + 1) % MAX_RECORDS;
    uint16_t index_addr = EEPROM_BASE_ADDR + user_id * 2;
    eeprom_write(index_addr, (const uint8_t*)&g_record_indices[user_id], 2);
    
    return true;
}

bool data_read_record(uint8_t user_id, uint16_t index, measurement_record_t* record) {
    if (user_id >= MAX_USERS || index >= MAX_RECORDS) {
        return false;
    }
    
    // 计算地址
    uint16_t addr = EEPROM_BASE_ADDR + (MAX_USERS * 2) + 
                   (user_id * MAX_RECORDS + index) * RECORD_SIZE;
    
    // 读取记录
    if (!eeprom_read(addr, (uint8_t*)record, RECORD_SIZE)) {
        return false;
    }
    
    // 验证CRC
    uint16_t calculated_crc = calculate_crc(record);
    if (calculated_crc != record->crc) {
        return false;  // 数据损坏
    }
    
    return true;
}

uint16_t data_get_record_count(uint8_t user_id) {
    if (user_id >= MAX_USERS) {
        return 0;
    }
    
    // 简化实现：返回当前索引值
    // 实际应该检查所有记录的有效性
    return g_record_indices[user_id];
}

void data_clear_user(uint8_t user_id) {
    if (user_id >= MAX_USERS) {
        return;
    }
    
    // 重置索引
    g_record_indices[user_id] = 0;
    uint16_t addr = EEPROM_BASE_ADDR + user_id * 2;
    eeprom_write(addr, (const uint8_t*)&g_record_indices[user_id], 2);
}
```

## 测试策略

### 单元测试

**测试用例TC-001：示波法算法测试**

```c
/**
 * @test TC-001
 * @trace SWR-002
 * @description 测试示波法算法的准确性
 */
void test_oscillometric_algorithm(void) {
    bp_result_t result;
    
    // 准备测试数据（模拟真实测量数据）
    algorithm_init();
    
    // 添加模拟的压力和振幅数据
    // 收缩压120, 舒张压80, 平均压93
    for (uint16_t i = 0; i < 300; i++) {
        uint16_t pressure = 150 - i / 2;  // 从150降到0
        int16_t oscillation = simulate_oscillation(pressure, 120, 80);
        algorithm_add_sample(pressure, oscillation);
    }
    
    // 计算血压
    bool success = algorithm_calculate(&result);
    
    // 验证结果
    assert(success == true);
    assert(result.valid == true);
    assert(abs(result.systolic - 120) <= 3);  // ±3 mmHg精度
    assert(abs(result.diastolic - 80) <= 3);
    assert(result.pulse_rate >= 60 && result.pulse_rate <= 80);
}
```

**测试用例TC-002：数据存储测试**

```c
/**
 * @test TC-002
 * @trace SWR-003
 * @description 测试数据存储和读取
 */
void test_data_storage(void) {
    // 初始化
    data_init();
    
    // 准备测试数据
    bp_result_t test_result = {
        .systolic = 120,
        .diastolic = 80,
        .mean = 93,
        .pulse_rate = 72,
        .valid = true
    };
    
    // 保存记录
    bool save_success = data_save_record(0, &test_result);
    assert(save_success == true);
    
    // 读取记录
    measurement_record_t record;
    bool read_success = data_read_record(0, 0, &record);
    assert(read_success == true);
    
    // 验证数据
    assert(record.systolic == 120);
    assert(record.diastolic == 80);
    assert(record.pulse_rate == 72);
}
```

### 集成测试

**测试用例TC-010：完整测量流程**

```c
/**
 * @test TC-010
 * @trace SWR-001, SWR-002, SWR-003
 * @description 测试完整的测量流程
 */
void test_complete_measurement(void) {
    // 1. 初始化系统
    system_init();
    
    // 2. 开始测量
    bool start_success = measurement_start();
    assert(start_success == true);
    
    // 3. 模拟测量过程
    while (measurement_get_state() != MEAS_STATE_COMPLETE) {
        measurement_process();
        simulate_hardware();
        delay_ms(10);
    }
    
    // 4. 获取结果
    bp_result_t result;
    bool result_success = measurement_get_result(&result);
    assert(result_success == true);
    assert(result.valid == true);
    
    // 5. 验证数据已保存
    uint16_t count = data_get_record_count(0);
    assert(count > 0);
}
```

### 系统测试

**测试用例TC-020：临床精度验证**

根据ISO 81060-2标准进行临床验证：

1. **测试对象**：85名受试者
2. **测试方法**：与水银血压计对比
3. **验收标准**：
   - 平均误差 ≤ 5 mmHg
   - 标准差 ≤ 8 mmHg
   - 至少65%的测量误差 ≤ 5 mmHg
   - 至少85%的测量误差 ≤ 10 mmHg
   - 至少95%的测量误差 ≤ 15 mmHg

## 验证和确认

### 软件验证

- ✓ 所有单元测试通过
- ✓ 所有集成测试通过
- ✓ 代码审查完成
- ✓ 静态分析无严重缺陷
- ✓ 需求追溯完整

### 软件确认

- ✓ 系统测试通过
- ✓ 临床精度验证通过
- ✓ 用户可用性测试通过
- ✓ 电磁兼容性测试通过
- ✓ 环境测试通过

## 经验教训

### 成功经验

1. **早期原型验证**
   - 在完整开发前验证算法可行性
   - 使用真实数据测试算法

2. **模块化设计**
   - 清晰的模块边界便于测试和维护
   - 硬件抽象层简化了移植

3. **持续集成**
   - 自动化测试及早发现问题
   - 代码质量工具保证代码标准

### 遇到的挑战

1. **算法调优**
   - **问题**：初始算法在某些情况下精度不足
   - **解决**：收集更多临床数据，优化阈值参数

2. **电源管理**
   - **问题**：电池寿命未达到目标
   - **解决**：优化测量流程，减少不必要的操作

3. **用户体验**
   - **问题**：老年用户反馈操作复杂
   - **解决**：简化UI，增加语音提示

### 改进建议

1. **增加自检功能**
   - 定期校准检查
   - 传感器故障检测

2. **数据分析功能**
   - 血压趋势图
   - 异常值提醒

3. **连接功能**
   - 蓝牙数据传输
   - 移动应用集成

## 总结

本案例展示了Class B医疗器械软件的完整开发过程，包括：

- 基于风险的软件安全分类
- 结构化的需求分析
- 模块化的架构设计
- 关键算法的实现
- 全面的测试策略
- 符合IEC 62304的文档

通过遵循标准化的开发流程和最佳实践，成功开发了一个安全、有效、易用的医疗器械软件系统。

## 参考资料

1. IEC 62304:2006+AMD1:2015 - Medical device software
2. ISO 81060-2:2018 - Non-invasive sphygmomanometers - Part 2: Clinical investigation of intermittent automated measurement type
3. ISO 14971:2019 - Medical devices - Application of risk management
4. "Oscillometric Blood Pressure Measurement: Progress and Problems" - IEEE Engineering in Medicine and Biology Magazine
5. FDA Guidance - Content of Premarket Submissions for Software Contained in Medical Devices
