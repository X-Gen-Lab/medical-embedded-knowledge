---
title: 模块化设计（Modular Design）
description: 深入理解模块化设计原则、模块划分方法和医疗器械软件中的模块化实践
difficulty: 中级
estimated_time: 90分钟
tags:
- 模块化
- 软件架构
- 设计原则
- 高内聚
- 低耦合
- 医疗器械
related_modules:
- zh/software-engineering/architecture-design
- zh/software-engineering/architecture-design/layered-architecture
- zh/software-engineering/architecture-design/interface-design
last_updated: '2026-02-09'
version: '1.0'
language: zh
---

# 模块化设计（Modular Design）

## 学习目标

完成本模块后，你将能够：
- 理解模块化设计的基本原则和优势
- 掌握模块划分的方法和标准
- 应用高内聚、低耦合原则进行模块设计
- 识别和避免常见的模块化设计问题
- 在医疗器械软件中实施有效的模块化架构
- 评估和改进现有系统的模块化程度
- 使用模块化设计提高代码的可维护性和可测试性

## 前置知识

- C/C++编程基础
- 软件工程基本概念
- 函数和数据结构设计
- 编译和链接过程
- 基本的软件架构概念

## 内容

### 概念介绍

模块化设计是将复杂系统分解为独立、可管理的模块的过程。每个模块负责特定的功能，通过明确定义的接口与其他模块交互。

**模块化设计的核心原则**：
- **高内聚（High Cohesion）**：模块内部元素紧密相关，共同完成单一职责
- **低耦合（Low Coupling）**：模块之间的依赖关系最小化
- **信息隐藏（Information Hiding）**：隐藏模块内部实现细节
- **接口清晰（Clear Interfaces）**：通过明确的接口进行模块间通信

**医疗器械软件中的重要性**：
- 符合IEC 62304对软件架构的要求
- 便于风险分析和安全分类
- 提高代码可追溯性
- 简化验证和确认过程
- 支持增量开发和维护

### 模块化设计原则

#### 1. 单一职责原则（Single Responsibility Principle）

每个模块应该只有一个改变的理由。


**示例：血压监测模块**

```c
// ❌ 错误：模块职责过多
typedef struct {
    void (*measure_bp)(void);
    void (*display_result)(void);
    void (*save_to_flash)(void);
    void (*send_to_cloud)(void);
    void (*check_battery)(void);
} BPMonitor;

// ✅ 正确：职责单一的模块
typedef struct {
    void (*measure_bp)(BPResult* result);
    void (*get_status)(BPStatus* status);
} BPMeasurement;

typedef struct {
    void (*display)(const BPResult* result);
    void (*update_ui)(UIState state);
} BPDisplay;

typedef struct {
    void (*save)(const BPResult* result);
    void (*load)(BPResult* result, uint32_t id);
} BPStorage;
```

#### 2. 开闭原则（Open-Closed Principle）

模块应该对扩展开放，对修改关闭。

**示例：传感器接口**

```c
// 定义通用传感器接口
typedef struct {
    int (*init)(void);
    int (*read)(void* data, size_t size);
    int (*deinit)(void);
} SensorInterface;

// 温度传感器实现
static int temp_sensor_init(void) {
    // 初始化温度传感器
    return 0;
}

static int temp_sensor_read(void* data, size_t size) {
    float* temp = (float*)data;
    *temp = read_temperature_from_hardware();
    return 0;
}

static int temp_sensor_deinit(void) {
    // 清理资源
    return 0;
}

const SensorInterface temp_sensor = {
    .init = temp_sensor_init,
    .read = temp_sensor_read,
    .deinit = temp_sensor_deinit
};

// 添加新传感器无需修改现有代码
const SensorInterface spo2_sensor = {
    .init = spo2_sensor_init,
    .read = spo2_sensor_read,
    .deinit = spo2_sensor_deinit
};
```

#### 3. 依赖倒置原则（Dependency Inversion Principle）

高层模块不应该依赖低层模块，两者都应该依赖抽象。

**示例：数据存储抽象**

```c
// 抽象存储接口
typedef struct {
    int (*write)(const void* data, size_t size);
    int (*read)(void* data, size_t size);
    int (*erase)(void);
} StorageInterface;

// 应用层模块依赖抽象接口
typedef struct {
    const StorageInterface* storage;
} DataLogger;

void data_logger_save(DataLogger* logger, const void* data, size_t size) {
    // 不关心具体存储实现
    logger->storage->write(data, size);
}

// Flash存储实现
static int flash_write(const void* data, size_t size) {
    // Flash写入实现
    return 0;
}

static int flash_read(void* data, size_t size) {
    // Flash读取实现
    return 0;
}

static int flash_erase(void) {
    // Flash擦除实现
    return 0;
}

const StorageInterface flash_storage = {
    .write = flash_write,
    .read = flash_read,
    .erase = flash_erase
};

// EEPROM存储实现（可替换）
const StorageInterface eeprom_storage = {
    .write = eeprom_write,
    .read = eeprom_read,
    .erase = eeprom_erase
};
```

### 模块划分方法

#### 1. 按功能划分

根据系统功能将代码组织成模块。

**示例：心电监护仪模块划分**

```c
// 信号采集模块
typedef struct {
    void (*start_acquisition)(void);
    void (*stop_acquisition)(void);
    int (*get_sample)(int16_t* sample);
} ECGAcquisition;

// 信号处理模块
typedef struct {
    void (*filter_signal)(const int16_t* input, int16_t* output, size_t len);
    void (*detect_qrs)(const int16_t* signal, size_t len, QRSResult* result);
    void (*calculate_hr)(const QRSResult* qrs, uint16_t* heart_rate);
} ECGProcessing;

// 报警模块
typedef struct {
    void (*check_thresholds)(const ECGMetrics* metrics);
    void (*trigger_alarm)(AlarmType type, AlarmLevel level);
    void (*silence_alarm)(void);
} ECGAlarm;

// 显示模块
typedef struct {
    void (*draw_waveform)(const int16_t* data, size_t len);
    void (*show_metrics)(const ECGMetrics* metrics);
    void (*update_status)(SystemStatus status);
} ECGDisplay;
```

#### 2. 按层次划分

将系统分为不同的抽象层次。

**示例：分层模块结构**

```c
// ============ 硬件抽象层（HAL） ============
typedef struct {
    void (*gpio_init)(GPIO_Pin pin, GPIO_Mode mode);
    void (*gpio_write)(GPIO_Pin pin, GPIO_State state);
    GPIO_State (*gpio_read)(GPIO_Pin pin);
} HAL_GPIO;

typedef struct {
    void (*adc_init)(ADC_Config* config);
    uint16_t (*adc_read)(ADC_Channel channel);
} HAL_ADC;

// ============ 驱动层 ============
typedef struct {
    int (*init)(void);
    int (*read_data)(uint8_t* buffer, size_t len);
    int (*write_data)(const uint8_t* buffer, size_t len);
} SensorDriver;

// ============ 中间件层 ============
typedef struct {
    void (*init)(void);
    void (*process)(void);
    int (*get_result)(MeasurementResult* result);
} MeasurementEngine;

// ============ 应用层 ============
typedef struct {
    void (*init)(void);
    void (*run)(void);
    void (*handle_event)(AppEvent event);
} Application;
```


#### 3. 按数据流划分

根据数据处理流程划分模块。

**示例：血糖仪数据流模块**

```c
// 数据采集模块
typedef struct {
    int (*acquire_sample)(RawSample* sample);
    int (*validate_sample)(const RawSample* sample);
} DataAcquisition;

// 数据处理模块
typedef struct {
    int (*calibrate)(const RawSample* raw, CalibratedSample* calibrated);
    int (*calculate_glucose)(const CalibratedSample* sample, float* glucose_mg_dl);
} DataProcessing;

// 数据存储模块
typedef struct {
    int (*save_measurement)(const GlucoseMeasurement* measurement);
    int (*get_history)(GlucoseMeasurement* buffer, size_t count);
    int (*get_statistics)(GlucoseStatistics* stats);
} DataStorage;

// 数据传输模块
typedef struct {
    int (*send_to_app)(const GlucoseMeasurement* measurement);
    int (*sync_history)(void);
} DataTransmission;
```

### 模块接口设计

#### 1. 接口最小化原则

只暴露必要的接口，隐藏内部实现。

**示例：定时器模块接口**

```c
// timer.h - 公共接口
typedef void (*TimerCallback)(void* arg);

typedef struct Timer Timer;

// 公共API（最小化）
Timer* timer_create(uint32_t period_ms, TimerCallback callback, void* arg);
int timer_start(Timer* timer);
int timer_stop(Timer* timer);
int timer_destroy(Timer* timer);

// timer.c - 内部实现（隐藏）
struct Timer {
    uint32_t period_ms;
    uint32_t remaining_ms;
    TimerCallback callback;
    void* callback_arg;
    bool is_running;
    Timer* next;  // 链表指针（内部使用）
};

// 内部函数（不暴露）
static void timer_list_add(Timer* timer);
static void timer_list_remove(Timer* timer);
static void timer_tick_handler(void);
```

#### 2. 接口稳定性

设计稳定的接口，减少变更影响。

**示例：版本化接口**

```c
// 版本1接口
typedef struct {
    int version;  // 接口版本号
    int (*init)(void);
    int (*read)(void* data, size_t size);
} SensorAPI_V1;

// 版本2接口（向后兼容）
typedef struct {
    int version;
    int (*init)(void);
    int (*read)(void* data, size_t size);
    int (*configure)(const SensorConfig* config);  // 新增功能
    int (*get_status)(SensorStatus* status);       // 新增功能
} SensorAPI_V2;

// 使用时检查版本
int use_sensor(void* api) {
    SensorAPI_V1* v1 = (SensorAPI_V1*)api;
    
    if (v1->version >= 2) {
        SensorAPI_V2* v2 = (SensorAPI_V2*)api;
        // 使用V2功能
        v2->configure(&config);
    }
    
    // 使用V1功能（所有版本都支持）
    return v1->read(buffer, size);
}
```

### 模块间通信

#### 1. 直接调用

最简单的通信方式，适用于紧密相关的模块。

```c
// 模块A
int module_a_process(const Data* input, Result* output) {
    // 直接调用模块B
    int status = module_b_transform(input, &temp_data);
    if (status != 0) {
        return status;
    }
    
    // 继续处理
    return finalize_result(&temp_data, output);
}
```

#### 2. 回调函数

实现模块间的松耦合通信。

```c
// 事件回调机制
typedef void (*EventCallback)(EventType type, const void* data, void* user_data);

typedef struct {
    void (*register_callback)(EventType type, EventCallback callback, void* user_data);
    void (*unregister_callback)(EventType type, EventCallback callback);
    void (*trigger_event)(EventType type, const void* data);
} EventManager;

// 使用示例
void alarm_handler(EventType type, const void* data, void* user_data) {
    if (type == EVENT_THRESHOLD_EXCEEDED) {
        const ThresholdData* threshold = (const ThresholdData*)data;
        trigger_alarm(threshold->level);
    }
}

void init_monitoring(EventManager* events) {
    // 注册回调
    events->register_callback(EVENT_THRESHOLD_EXCEEDED, alarm_handler, NULL);
}
```

#### 3. 消息队列

适用于异步通信和解耦。

```c
// 消息队列接口
typedef struct {
    int (*send)(const Message* msg, uint32_t timeout_ms);
    int (*receive)(Message* msg, uint32_t timeout_ms);
    int (*peek)(Message* msg);
    size_t (*get_count)(void);
} MessageQueue;

// 生产者模块
void sensor_task(MessageQueue* queue) {
    Message msg;
    msg.type = MSG_SENSOR_DATA;
    msg.data.sensor_value = read_sensor();
    
    queue->send(&msg, 100);  // 发送消息
}

// 消费者模块
void processing_task(MessageQueue* queue) {
    Message msg;
    
    if (queue->receive(&msg, 1000) == 0) {
        if (msg.type == MSG_SENSOR_DATA) {
            process_sensor_data(msg.data.sensor_value);
        }
    }
}
```

### 模块化设计模式

#### 1. 工厂模式

创建对象的统一接口。

```c
// 传感器工厂
typedef struct {
    SensorInterface* (*create)(SensorType type);
    void (*destroy)(SensorInterface* sensor);
} SensorFactory;

SensorInterface* sensor_factory_create(SensorType type) {
    switch (type) {
        case SENSOR_TEMPERATURE:
            return create_temperature_sensor();
        case SENSOR_PRESSURE:
            return create_pressure_sensor();
        case SENSOR_SPO2:
            return create_spo2_sensor();
        default:
            return NULL;
    }
}

// 使用工厂
SensorInterface* sensor = sensor_factory_create(SENSOR_TEMPERATURE);
if (sensor != NULL) {
    sensor->init();
    sensor->read(&data, sizeof(data));
    sensor->deinit();
    sensor_factory_destroy(sensor);
}
```

#### 2. 观察者模式

实现一对多的依赖关系。

```c
// 观察者接口
typedef void (*Observer)(const void* subject, const void* data);

typedef struct {
    void (*attach)(Observer observer);
    void (*detach)(Observer observer);
    void (*notify)(const void* data);
} Subject;

// 具体主题：心率监测
typedef struct {
    Subject base;
    uint16_t heart_rate;
    Observer observers[MAX_OBSERVERS];
    size_t observer_count;
} HeartRateMonitor;

void heart_rate_attach(Observer observer) {
    // 添加观察者
}

void heart_rate_notify(const void* data) {
    for (size_t i = 0; i < monitor.observer_count; i++) {
        monitor.observers[i](&monitor, data);
    }
}

// 观察者：显示模块
void display_observer(const void* subject, const void* data) {
    const HeartRateMonitor* monitor = (const HeartRateMonitor*)subject;
    update_display(monitor->heart_rate);
}

// 观察者：报警模块
void alarm_observer(const void* subject, const void* data) {
    const HeartRateMonitor* monitor = (const HeartRateMonitor*)subject;
    if (monitor->heart_rate > THRESHOLD_HIGH || monitor->heart_rate < THRESHOLD_LOW) {
        trigger_alarm();
    }
}
```


### 医疗器械软件中的模块化实践

#### 1. 按IEC 62304安全分类划分模块

```c
// Class C模块（高风险）- 严格验证
typedef struct {
    int (*calculate_insulin_dose)(const PatientData* data, float* dose);
    int (*verify_dose)(float dose, bool* is_safe);
} InsulinDosageModule;  // 需要完整的单元测试和集成测试

// Class B模块（中风险）
typedef struct {
    int (*log_measurement)(const Measurement* data);
    int (*get_history)(Measurement* buffer, size_t count);
} DataLoggingModule;

// Class A模块（低风险）
typedef struct {
    void (*update_display)(const DisplayData* data);
    void (*show_message)(const char* message);
} DisplayModule;
```

#### 2. 可追溯性设计

每个模块应该能够追溯到需求。

```c
/**
 * @module: ECG_Signal_Processing
 * @requirement: REQ-ECG-001, REQ-ECG-002
 * @safety_class: Class B
 * @description: ECG信号处理模块，负责滤波和QRS检测
 */
typedef struct {
    /**
     * @function: filter_ecg_signal
     * @requirement: REQ-ECG-001
     * @description: 对ECG信号进行带通滤波
     */
    int (*filter_signal)(const int16_t* input, int16_t* output, size_t len);
    
    /**
     * @function: detect_qrs_complex
     * @requirement: REQ-ECG-002
     * @description: 检测QRS波群
     */
    int (*detect_qrs)(const int16_t* signal, size_t len, QRSResult* result);
} ECGProcessingModule;
```

#### 3. 模块化测试策略

```c
// 模块测试接口
typedef struct {
    int (*self_test)(void);
    int (*get_test_coverage)(float* coverage);
    int (*inject_fault)(FaultType type);  // 用于故障注入测试
} ModuleTestInterface;

// 示例：传感器模块测试
int sensor_module_self_test(void) {
    int result = 0;
    
    // 测试初始化
    if (sensor_init() != 0) {
        result |= TEST_INIT_FAILED;
    }
    
    // 测试读取功能
    SensorData data;
    if (sensor_read(&data) != 0) {
        result |= TEST_READ_FAILED;
    }
    
    // 测试数据有效性
    if (!is_data_valid(&data)) {
        result |= TEST_DATA_INVALID;
    }
    
    // 测试清理
    if (sensor_deinit() != 0) {
        result |= TEST_DEINIT_FAILED;
    }
    
    return result;
}
```

### 模块化度量

#### 1. 内聚性度量

```c
// 高内聚示例：所有函数都操作相同的数据结构
typedef struct {
    float temperature;
    float humidity;
    uint32_t timestamp;
} EnvironmentData;

typedef struct {
    int (*read_temperature)(float* temp);
    int (*read_humidity)(float* humidity);
    int (*get_data)(EnvironmentData* data);
    int (*is_data_valid)(const EnvironmentData* data);
} EnvironmentSensor;  // 高内聚：所有函数都与环境数据相关

// 低内聚示例（应避免）
typedef struct {
    int (*read_sensor)(void);
    int (*save_to_flash)(void);
    int (*send_to_cloud)(void);
    int (*check_battery)(void);
    int (*update_display)(void);
} MixedModule;  // 低内聚：函数职责不相关
```

#### 2. 耦合性度量

```c
// 低耦合示例：通过接口通信
typedef struct {
    const StorageInterface* storage;  // 依赖抽象接口
} DataLogger;

void data_logger_save(DataLogger* logger, const void* data) {
    logger->storage->write(data, sizeof(data));  // 不依赖具体实现
}

// 高耦合示例（应避免）
void bad_data_logger_save(const void* data) {
    // 直接依赖具体实现
    flash_write(FLASH_ADDRESS, data, sizeof(data));
    eeprom_backup(EEPROM_ADDRESS, data, sizeof(data));
    // 难以测试和替换
}
```

#### 3. 模块复杂度

```c
// 计算模块复杂度的指标
typedef struct {
    size_t function_count;      // 函数数量
    size_t line_count;          // 代码行数
    size_t dependency_count;    // 依赖模块数量
    size_t interface_count;     // 接口数量
    float cyclomatic_complexity; // 圈复杂度
} ModuleMetrics;

// 理想的模块特征
// - 函数数量：5-15个
// - 代码行数：200-500行
// - 依赖数量：<5个
// - 圈复杂度：<10
```

### 模块化重构

#### 1. 识别重构机会

```c
// 重构前：大型单体函数
void process_patient_data(PatientData* data) {
    // 100+ 行代码
    // 数据验证
    // 数据处理
    // 结果计算
    // 存储
    // 显示
    // 报警检查
}

// 重构后：模块化函数
int validate_patient_data(const PatientData* data) {
    // 专注于验证
    return is_valid(data) ? 0 : -1;
}

int process_measurements(const PatientData* data, ProcessedData* result) {
    // 专注于处理
    return calculate_results(data, result);
}

int store_results(const ProcessedData* result) {
    // 专注于存储
    return storage->save(result);
}

void update_display_with_results(const ProcessedData* result) {
    // 专注于显示
    display->show(result);
}

int check_alarm_conditions(const ProcessedData* result) {
    // 专注于报警
    return alarm->check(result);
}

// 主流程变得清晰
int process_patient_data_modular(PatientData* data) {
    ProcessedData result;
    
    if (validate_patient_data(data) != 0) {
        return ERROR_INVALID_DATA;
    }
    
    if (process_measurements(data, &result) != 0) {
        return ERROR_PROCESSING;
    }
    
    store_results(&result);
    update_display_with_results(&result);
    check_alarm_conditions(&result);
    
    return SUCCESS;
}
```

#### 2. 提取公共模块

```c
// 识别重复代码并提取为公共模块

// 重构前：重复的CRC计算
uint16_t calculate_crc_in_module_a(const uint8_t* data, size_t len) {
    uint16_t crc = 0xFFFF;
    // CRC计算逻辑
    return crc;
}

uint16_t calculate_crc_in_module_b(const uint8_t* data, size_t len) {
    uint16_t crc = 0xFFFF;
    // 相同的CRC计算逻辑
    return crc;
}

// 重构后：提取为公共工具模块
// utils/crc.h
typedef struct {
    uint16_t (*calculate)(const uint8_t* data, size_t len);
    bool (*verify)(const uint8_t* data, size_t len, uint16_t expected_crc);
} CRCUtils;

extern const CRCUtils crc_utils;

// 各模块使用公共工具
uint16_t crc = crc_utils.calculate(data, len);
```

### 最佳实践

#### 1. 模块命名规范

```c
// 使用清晰的命名约定
// 格式：<subsystem>_<module>_<function>

// 好的命名
int ecg_filter_apply_bandpass(const int16_t* input, int16_t* output);
int ecg_qrs_detect_complex(const int16_t* signal, QRSResult* result);
int storage_flash_write_block(uint32_t address, const void* data, size_t size);

// 避免的命名
int process(void);  // 太模糊
int do_it(void);    // 无意义
int func1(void);    // 无描述性
```

#### 2. 模块文档化

```c
/**
 * @file ecg_processing.h
 * @brief ECG信号处理模块
 * @author Medical Device Team
 * @date 2026-02-09
 * @version 1.0
 * 
 * @requirements REQ-ECG-001, REQ-ECG-002, REQ-ECG-003
 * @safety_class Class B
 * 
 * @description
 * 本模块负责ECG信号的实时处理，包括：
 * - 信号滤波（带通滤波器）
 * - QRS波群检测
 * - 心率计算
 * 
 * @dependencies
 * - math_utils: 数学运算工具
 * - signal_buffer: 信号缓冲管理
 * 
 * @testing
 * - 单元测试覆盖率：95%
 * - 集成测试：已完成
 * - 验证状态：已验证
 */
```

#### 3. 模块版本管理

```c
// 模块版本信息
typedef struct {
    uint8_t major;
    uint8_t minor;
    uint8_t patch;
    const char* build_date;
    const char* build_time;
} ModuleVersion;

#define ECG_MODULE_VERSION { \
    .major = 1, \
    .minor = 2, \
    .patch = 3, \
    .build_date = __DATE__, \
    .build_time = __TIME__ \
}

// 版本兼容性检查
bool is_module_compatible(const ModuleVersion* required, 
                         const ModuleVersion* actual) {
    // 主版本号必须匹配
    if (required->major != actual->major) {
        return false;
    }
    
    // 次版本号必须大于等于要求
    if (actual->minor < required->minor) {
        return false;
    }
    
    return true;
}
```


### 常见陷阱

#### 1. 过度模块化

**问题**：创建过多的小模块，增加系统复杂度。

```c
// ❌ 过度模块化
typedef struct {
    int (*add)(int a, int b);
} AddModule;

typedef struct {
    int (*subtract)(int a, int b);
} SubtractModule;

typedef struct {
    int (*multiply)(int a, int b);
} MultiplyModule;

// ✅ 合理的模块化
typedef struct {
    int (*add)(int a, int b);
    int (*subtract)(int a, int b);
    int (*multiply)(int a, int b);
    int (*divide)(int a, int b);
} MathOperations;
```

#### 2. 循环依赖

**问题**：模块A依赖模块B，模块B又依赖模块A。

```c
// ❌ 循环依赖
// module_a.h
#include "module_b.h"
void module_a_function(void) {
    module_b_function();
}

// module_b.h
#include "module_a.h"
void module_b_function(void) {
    module_a_function();  // 循环依赖！
}

// ✅ 解决方案：引入中间层或使用回调
// module_a.h
typedef void (*CallbackFunction)(void);
void module_a_set_callback(CallbackFunction callback);

// module_b.c
void module_b_function(void) {
    // 通过回调调用module_a的功能
}
```

#### 3. 上帝模块（God Module）

**问题**：单个模块承担过多职责。

```c
// ❌ 上帝模块
typedef struct {
    int (*init_hardware)(void);
    int (*read_sensor)(void);
    int (*process_data)(void);
    int (*save_to_flash)(void);
    int (*send_to_cloud)(void);
    int (*update_display)(void);
    int (*check_battery)(void);
    int (*manage_power)(void);
    int (*handle_alarms)(void);
    int (*log_events)(void);
} SystemManager;  // 职责过多！

// ✅ 拆分为多个专注的模块
typedef struct {
    int (*init)(void);
    int (*read)(SensorData* data);
} SensorModule;

typedef struct {
    int (*process)(const SensorData* input, ProcessedData* output);
} ProcessingModule;

typedef struct {
    int (*save)(const ProcessedData* data);
    int (*load)(ProcessedData* data);
} StorageModule;
```

#### 4. 接口污染

**问题**：接口包含不必要的函数。

```c
// ❌ 接口污染
typedef struct {
    int (*read)(void* data);
    int (*write)(const void* data);
    int (*internal_helper_1)(void);  // 不应该暴露
    int (*internal_helper_2)(void);  // 不应该暴露
    int (*debug_function)(void);     // 调试函数不应该在发布接口中
} SensorInterface;

// ✅ 清晰的接口
typedef struct {
    int (*read)(void* data);
    int (*write)(const void* data);
} SensorInterface;

// 内部辅助函数保持私有
static int internal_helper_1(void);
static int internal_helper_2(void);
```

#### 5. 隐式依赖

**问题**：模块依赖全局状态或隐藏的依赖。

```c
// ❌ 隐式依赖全局变量
static int global_sensor_state;  // 全局状态

int sensor_read(void* data) {
    if (global_sensor_state != INITIALIZED) {  // 隐式依赖
        return ERROR;
    }
    // 读取数据
}

// ✅ 显式依赖
typedef struct {
    int state;
    // 其他状态
} SensorContext;

int sensor_read(SensorContext* ctx, void* data) {
    if (ctx->state != INITIALIZED) {  // 显式依赖
        return ERROR;
    }
    // 读取数据
}
```

### 实践练习

#### 练习1：模块划分

**任务**：为一个血氧仪设计模块结构。

**要求**：
- 识别主要功能模块
- 定义模块接口
- 确保高内聚、低耦合
- 考虑IEC 62304安全分类

**提示**：考虑以下功能：
- PPG信号采集
- 信号处理和SpO2计算
- 显示
- 数据存储
- 报警管理

#### 练习2：重构单体代码

**任务**：将以下单体函数重构为模块化设计。

```c
void monitor_patient(void) {
    // 初始化传感器
    init_ecg_sensor();
    init_bp_sensor();
    init_temp_sensor();
    
    while (1) {
        // 读取ECG
        int16_t ecg_data[100];
        read_ecg(ecg_data, 100);
        
        // 处理ECG
        filter_ecg(ecg_data, 100);
        detect_qrs(ecg_data, 100);
        
        // 读取血压
        uint16_t systolic, diastolic;
        read_bp(&systolic, &diastolic);
        
        // 读取体温
        float temperature;
        read_temp(&temperature);
        
        // 显示所有数据
        display_ecg(ecg_data, 100);
        display_bp(systolic, diastolic);
        display_temp(temperature);
        
        // 检查报警
        if (systolic > 140 || diastolic > 90) {
            trigger_alarm(ALARM_BP_HIGH);
        }
        if (temperature > 38.0) {
            trigger_alarm(ALARM_FEVER);
        }
        
        // 保存数据
        save_to_flash(ecg_data, systolic, diastolic, temperature);
        
        delay(1000);
    }
}
```

#### 练习3：设计可扩展模块

**任务**：设计一个传感器管理模块，支持动态添加新类型的传感器。

**要求**：
- 使用工厂模式或策略模式
- 支持运行时注册新传感器
- 提供统一的传感器接口
- 考虑错误处理

#### 练习4：模块测试

**任务**：为数据处理模块编写自测试函数。

**要求**：
- 测试所有公共接口
- 包含边界条件测试
- 返回详细的测试结果
- 不依赖外部硬件

## 自测问题

### 问题1：模块化设计的核心原则

**问题**：什么是高内聚、低耦合？请举例说明。

<details>
<summary>点击查看答案</summary>

**答案**：

**高内聚（High Cohesion）**：
- 定义：模块内部的元素紧密相关，共同完成单一、明确的职责
- 特征：模块内的函数和数据都围绕同一个目标
- 优点：易于理解、维护和测试

示例：
```c
// 高内聚：所有函数都与ECG信号处理相关
typedef struct {
    int (*filter_signal)(const int16_t* input, int16_t* output, size_t len);
    int (*detect_qrs)(const int16_t* signal, size_t len, QRSResult* result);
    int (*calculate_hr)(const QRSResult* qrs, uint16_t* heart_rate);
} ECGProcessing;
```

**低耦合（Low Coupling）**：
- 定义：模块之间的依赖关系最小化
- 特征：模块通过明确的接口通信，不直接访问其他模块的内部实现
- 优点：模块可以独立修改、测试和替换

示例：
```c
// 低耦合：通过抽象接口依赖
typedef struct {
    const StorageInterface* storage;  // 依赖抽象，不依赖具体实现
} DataLogger;

void data_logger_save(DataLogger* logger, const void* data) {
    logger->storage->write(data, sizeof(data));  // 不关心具体是Flash还是EEPROM
}
```

</details>

### 问题2：模块划分方法

**问题**：列举至少三种模块划分方法，并说明各自的适用场景。

<details>
<summary>点击查看答案</summary>

**答案**：

1. **按功能划分**：
   - 方法：根据系统功能将代码组织成模块
   - 适用场景：功能明确、相对独立的系统
   - 示例：信号采集模块、信号处理模块、显示模块、报警模块

2. **按层次划分**：
   - 方法：将系统分为不同的抽象层次
   - 适用场景：需要硬件抽象、支持多平台的系统
   - 示例：硬件抽象层（HAL）、驱动层、中间件层、应用层

3. **按数据流划分**：
   - 方法：根据数据处理流程划分模块
   - 适用场景：数据处理管道明确的系统
   - 示例：数据采集→数据处理→数据存储→数据传输

4. **按安全等级划分**（医疗器械特有）：
   - 方法：根据IEC 62304安全分类划分模块
   - 适用场景：医疗器械软件开发
   - 示例：Class C模块（高风险）、Class B模块（中风险）、Class A模块（低风险）

</details>

### 问题3：模块接口设计

**问题**：设计模块接口时应该遵循哪些原则？为什么？

<details>
<summary>点击查看答案</summary>

**答案**：

1. **接口最小化原则**：
   - 只暴露必要的接口，隐藏内部实现
   - 原因：减少模块间耦合，降低使用复杂度，提高安全性

2. **接口稳定性原则**：
   - 设计稳定的接口，减少变更影响
   - 原因：避免频繁修改导致的连锁反应，提高系统稳定性

3. **接口清晰性原则**：
   - 接口语义明确，参数含义清楚
   - 原因：降低使用难度，减少误用风险

4. **接口一致性原则**：
   - 相似功能的接口应该保持一致的风格
   - 原因：提高可学习性，减少认知负担

5. **错误处理明确**：
   - 明确定义错误返回值和异常情况
   - 原因：提高系统可靠性，便于调试

示例：
```c
// 好的接口设计
typedef struct {
    // 清晰的函数名
    int (*init)(const Config* config);
    // 明确的参数和返回值
    int (*read)(void* buffer, size_t size, size_t* bytes_read);
    // 一致的错误处理
    int (*deinit)(void);
} SensorInterface;
```

</details>

### 问题4：识别设计问题

**问题**：以下代码存在什么模块化设计问题？如何改进？

```c
typedef struct {
    int (*read_sensor)(void);
    int (*process_data)(void);
    int (*save_to_flash)(void);
    int (*send_to_cloud)(void);
    int (*update_display)(void);
    int (*check_battery)(void);
} SystemModule;
```

<details>
<summary>点击查看答案</summary>

**答案**：

**存在的问题**：
1. **低内聚**：模块包含多个不相关的职责（传感器、处理、存储、通信、显示、电源）
2. **违反单一职责原则**：一个模块承担过多职责
3. **难以测试**：无法独立测试各个功能
4. **难以维护**：修改一个功能可能影响其他功能
5. **难以复用**：无法在其他项目中复用单个功能

**改进方案**：

```c
// 拆分为多个专注的模块

// 传感器模块
typedef struct {
    int (*init)(void);
    int (*read)(SensorData* data);
    int (*deinit)(void);
} SensorModule;

// 数据处理模块
typedef struct {
    int (*process)(const SensorData* input, ProcessedData* output);
    int (*validate)(const ProcessedData* data);
} ProcessingModule;

// 存储模块
typedef struct {
    int (*save)(const ProcessedData* data);
    int (*load)(ProcessedData* data, uint32_t id);
} StorageModule;

// 通信模块
typedef struct {
    int (*connect)(void);
    int (*send)(const ProcessedData* data);
    int (*disconnect)(void);
} CommunicationModule;

// 显示模块
typedef struct {
    void (*update)(const ProcessedData* data);
    void (*show_message)(const char* message);
} DisplayModule;

// 电源管理模块
typedef struct {
    int (*get_battery_level)(uint8_t* level);
    int (*enter_low_power)(void);
} PowerModule;
```

**改进效果**：
- 每个模块职责单一、内聚性高
- 模块间耦合度低
- 易于测试、维护和复用
- 符合SOLID原则

</details>

### 问题5：医疗器械模块化

**问题**：在医疗器械软件开发中，模块化设计如何支持IEC 62304合规性？

<details>
<summary>点击查看答案</summary>

**答案**：

模块化设计支持IEC 62304合规性的方式：

1. **安全分类管理**：
   - 按安全等级划分模块（Class A/B/C）
   - 对高风险模块应用更严格的开发和测试要求
   - 示例：胰岛素剂量计算模块（Class C）需要完整的单元测试和集成测试

2. **需求追溯性**：
   - 每个模块明确关联到具体需求
   - 通过模块文档建立需求到实现的追溯链
   - 便于验证所有需求都已实现

3. **风险管理**：
   - 模块化便于识别和隔离风险
   - 可以针对高风险模块实施额外的控制措施
   - 降低风险传播范围

4. **验证和确认**：
   - 模块化支持增量验证
   - 每个模块可以独立测试
   - 简化集成测试和系统测试

5. **变更管理**：
   - 模块化限制变更影响范围
   - 便于评估变更的风险和影响
   - 支持部分模块的独立更新

6. **文档化**：
   - 每个模块有清晰的文档
   - 包括接口规范、设计决策、测试结果
   - 满足IEC 62304的文档要求

示例：
```c
/**
 * @module: Insulin_Dosage_Calculator
 * @safety_class: Class C
 * @requirements: REQ-DOSE-001, REQ-DOSE-002, REQ-DOSE-003
 * @risk_controls: RC-001, RC-002
 * @verification: 单元测试覆盖率100%，已通过所有测试用例
 * @validation: 已通过临床验证
 */
typedef struct {
    int (*calculate_dose)(const PatientData* data, float* dose);
    int (*verify_dose)(float dose, bool* is_safe);
} InsulinDosageModule;
```

</details>

## 相关资源

- [软件架构设计](index.md)
- [分层架构设计](layered-architecture.md)
- [接口设计](interface-design.md)
- [IEC 62304软件生命周期](../../regulatory-standards/iec-62304/index.md)

## 参考文献

1. Martin, R. C. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.
2. Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.
3. IEC 62304:2006+AMD1:2015. *Medical device software – Software life cycle processes*.
4. Parnas, D. L. (1972). "On the Criteria To Be Used in Decomposing Systems into Modules". *Communications of the ACM*, 15(12), 1053-1058.
5. Stevens, W. P., Myers, G. J., & Constantine, L. L. (1974). "Structured Design". *IBM Systems Journal*, 13(2), 115-139.
6. ISO/IEC/IEEE 42010:2011. *Systems and software engineering — Architecture description*.

---

**最后更新**: 2026-02-09  
**版本**: 1.0  
**作者**: 医疗器械软件工程团队
