---
title: 集成测试
description: 集成测试策略、方法和工具，包括接口测试、集成策略和医疗器械软件集成测试最佳实践
difficulty: 中级
estimated_time: 3小时
tags:
- 集成测试
- 接口测试
- 测试策略
- IEC 62304
related_modules:
- zh/software-engineering/testing-strategy/unit-testing
- zh/software-engineering/testing-strategy/system-testing
- zh/software-engineering/architecture-design/interface-design
last_updated: '2026-02-09'
version: '1.0'
language: zh-CN
---

# 集成测试

## 学习目标

完成本模块后，你将能够：
- 理解集成测试的概念和重要性
- 掌握不同的集成测试策略（自顶向下、自底向上、三明治）
- 设计和执行接口测试
- 使用集成测试工具和框架
- 应用医疗器械软件集成测试的最佳实践
- 遵循IEC 62304标准的集成测试要求

## 前置知识

- 单元测试基础
- 软件架构设计
- 接口设计原则
- C/C++编程
- IEC 62304标准基础知识

## 内容

### 集成测试基础

**集成测试定义**：
集成测试是将已通过单元测试的软件模块组合在一起，测试模块间接口和交互的测试活动。

**集成测试的目的**：
- 验证模块间接口的正确性
- 发现模块集成时的问题
- 验证数据在模块间的正确传递
- 检测模块间的时序问题
- 验证系统架构设计

**集成测试特点**：
```
✓ 测试模块间交互
✓ 使用真实或部分真实的依赖
✓ 执行速度比单元测试慢
✓ 发现接口和集成问题
✓ 需要更复杂的测试环境
```

**集成测试 vs 单元测试**：

| 维度 | 单元测试 | 集成测试 |
|------|---------|---------|
| 测试范围 | 单个函数/模块 | 多个模块的接口 |
| 依赖处理 | 隔离（Mock/Stub） | 真实依赖 |
| 执行速度 | 非常快（毫秒） | 较慢（秒级） |
| 缺陷定位 | 精确到函数 | 定位到模块间 |
| 测试环境 | 简单 | 复杂 |
| 执行时机 | 开发阶段 | 集成阶段 |


### 集成测试策略

#### 1. 大爆炸集成（Big Bang Integration）

**定义**：将所有模块一次性集成在一起进行测试。

**优点**：
- 实施简单
- 适合小型系统

**缺点**：
- 难以定位问题
- 测试延迟到后期
- 风险高

**适用场景**：
- 小型项目（< 5个模块）
- 模块间依赖简单
- 时间紧迫的原型


#### 2. 自顶向下集成（Top-Down Integration）

**定义**：从顶层模块开始，逐步向下集成低层模块。

**工作流程**：
```
主控模块（已测试）
    ↓
集成第一层子模块
    ↓
集成第二层子模块
    ↓
...
    ↓
集成最底层模块
```

**使用桩（Stub）**：
未开发完成的低层模块用桩代替。

**示例：心电监护系统**

```c
// 顶层模块：ECG监护主控
typedef struct {
    ecg_acquisition_t* acquisition;
    ecg_processing_t* processing;
    ecg_display_t* display;
    alarm_manager_t* alarm;
} ecg_monitor_t;

// 步骤1：测试主控模块（使用桩）
void test_ecg_monitor_initialization(void) {
    ecg_monitor_t monitor;
    
    // 使用桩代替真实模块
    monitor.acquisition = &acquisition_stub;
    monitor.processing = &processing_stub;
    monitor.display = &display_stub;
    monitor.alarm = &alarm_stub;
    
    int result = ecg_monitor_init(&monitor);
    
    TEST_ASSERT_EQUAL(SUCCESS, result);
}

// 采集模块桩
ecg_acquisition_t acquisition_stub = {
    .start = acquisition_start_stub,
    .stop = acquisition_stop_stub,
    .get_data = acquisition_get_data_stub
};

int acquisition_start_stub(void) {
    return SUCCESS;  // 简单返回成功
}

int16_t* acquisition_get_data_stub(int* length) {
    static int16_t test_data[100];
    *length = 100;
    return test_data;  // 返回测试数据
}

// 步骤2：集成真实的采集模块
void test_ecg_monitor_with_real_acquisition(void) {
    ecg_monitor_t monitor;
    
    // 使用真实采集模块
    monitor.acquisition = ecg_acquisition_create();
    
    // 其他模块仍使用桩
    monitor.processing = &processing_stub;
    monitor.display = &display_stub;
    monitor.alarm = &alarm_stub;
    
    // 测试主控与采集模块的集成
    ecg_monitor_start(&monitor);
    int16_t* data = ecg_monitor_get_raw_data(&monitor);
    
    TEST_ASSERT_NOT_NULL(data);
}

// 步骤3：继续集成处理模块
void test_ecg_monitor_with_acquisition_and_processing(void) {
    ecg_monitor_t monitor;
    
    // 使用真实采集和处理模块
    monitor.acquisition = ecg_acquisition_create();
    monitor.processing = ecg_processing_create();
    
    // 显示和报警仍使用桩
    monitor.display = &display_stub;
    monitor.alarm = &alarm_stub;
    
    // 测试数据流：采集 → 处理
    ecg_monitor_start(&monitor);
    ecg_result_t result = ecg_monitor_process(&monitor);
    
    TEST_ASSERT_EQUAL(ECG_SUCCESS, result.status);
    TEST_ASSERT_TRUE(result.heart_rate > 0);
}
```

**代码说明**：
- 逐步替换桩为真实模块
- 每次集成测试一层
- 验证上层与新集成层的交互

**优点**：
- 早期验证主要控制流程
- 问题定位相对容易
- 适合需求明确的系统

**缺点**：
- 需要编写大量桩
- 底层模块测试延迟
- 可能遗漏底层问题


#### 3. 自底向上集成（Bottom-Up Integration）

**定义**：从底层模块开始，逐步向上集成高层模块。

**工作流程**：
```
底层模块（已测试）
    ↑
集成中间层模块
    ↑
集成上层模块
    ↑
集成主控模块
```

**使用驱动器（Driver）**：
未开发完成的高层模块用驱动器代替。

**示例：血压监测系统**

```c
// 步骤1：测试底层硬件接口模块
void test_adc_driver(void) {
    adc_init();
    
    int16_t value = adc_read_channel(0);
    
    TEST_ASSERT_TRUE(value >= 0 && value <= 4095);
}

// 步骤2：集成传感器接口层
void test_pressure_sensor_with_adc(void) {
    // 使用真实ADC驱动
    adc_init();
    
    // 测试传感器接口
    pressure_sensor_t sensor;
    pressure_sensor_init(&sensor);
    
    float pressure = pressure_sensor_read(&sensor);
    
    TEST_ASSERT_TRUE(pressure >= 0 && pressure <= 300);  // mmHg
}

// 驱动器：模拟上层调用
void driver_test_pressure_measurement(void) {
    pressure_sensor_t sensor;
    pressure_sensor_init(&sensor);
    
    // 模拟测量循环
    for (int i = 0; i < 10; i++) {
        float pressure = pressure_sensor_read(&sensor);
        printf("Pressure: %.1f mmHg\n", pressure);
        delay_ms(100);
    }
}

// 步骤3：集成测量算法层
void test_bp_algorithm_with_sensor(void) {
    // 使用真实传感器和ADC
    pressure_sensor_t sensor;
    pressure_sensor_init(&sensor);
    
    bp_algorithm_t algorithm;
    bp_algorithm_init(&algorithm);
    
    // 测试算法与传感器的集成
    bp_measurement_t result;
    int status = bp_measure(&algorithm, &sensor, &result);
    
    TEST_ASSERT_EQUAL(BP_SUCCESS, status);
    TEST_ASSERT_TRUE(result.systolic >= 60 && result.systolic <= 250);
    TEST_ASSERT_TRUE(result.diastolic >= 40 && result.diastolic <= 150);
}

// 步骤4：集成主控模块
void test_bp_monitor_complete_integration(void) {
    // 所有模块都使用真实实现
    bp_monitor_t monitor;
    bp_monitor_init(&monitor);
    
    // 执行完整测量
    bp_measurement_t result;
    int status = bp_monitor_measure(&monitor, &result);
    
    TEST_ASSERT_EQUAL(BP_SUCCESS, status);
    TEST_ASSERT_TRUE(result.systolic > result.diastolic);
}
```

**代码说明**：
- 从底层硬件驱动开始测试
- 逐层向上集成
- 使用驱动器模拟上层调用

**优点**：
- 底层模块充分测试
- 不需要桩
- 适合硬件相关系统

**缺点**：
- 需要编写驱动器
- 主要控制流程测试延迟
- 可能遗漏高层设计问题


#### 4. 三明治集成（Sandwich Integration）

**定义**：结合自顶向下和自底向上策略，同时从两端向中间集成。

**工作流程**：
```
顶层模块 ←→ 中间层 ←→ 底层模块
   ↓                      ↑
  桩                    驱动器
```

**示例：体温监测系统**

```c
// 顶层：从主控开始（自顶向下）
void test_temperature_monitor_top_layer(void) {
    temp_monitor_t monitor;
    
    // 使用桩代替底层
    monitor.sensor = &sensor_stub;
    monitor.display = &display_stub;
    
    temp_monitor_init(&monitor);
    temp_monitor_start(&monitor);
    
    TEST_ASSERT_TRUE(monitor.is_running);
}

// 底层：从传感器开始（自底向上）
void test_temperature_sensor_bottom_layer(void) {
    temp_sensor_t sensor;
    temp_sensor_init(&sensor);
    
    float temp = temp_sensor_read(&sensor);
    
    TEST_ASSERT_TRUE(temp >= -40.0 && temp <= 85.0);
}

// 中间层：集成两端
void test_temperature_monitor_middle_integration(void) {
    temp_monitor_t monitor;
    
    // 使用真实传感器
    monitor.sensor = temp_sensor_create();
    
    // 使用真实显示
    monitor.display = display_create();
    
    // 测试完整集成
    temp_monitor_start(&monitor);
    float displayed_temp = display_get_value(monitor.display);
    
    TEST_ASSERT_TRUE(displayed_temp >= -40.0 && displayed_temp <= 85.0);
}
```

**优点**：
- 平衡两种策略的优点
- 并行开发和测试
- 风险分散

**缺点**：
- 协调复杂
- 需要更多资源
- 管理难度大


### 接口测试

接口测试是集成测试的核心，验证模块间的数据传递和交互。

#### 接口类型

**1. 函数调用接口**

```c
// 接口定义
typedef struct {
    int (*init)(void);
    int (*read)(uint8_t* buffer, size_t length);
    int (*write)(const uint8_t* data, size_t length);
    int (*close)(void);
} uart_interface_t;

// 接口测试
void test_uart_interface(void) {
    uart_interface_t uart;
    uart_init_interface(&uart);
    
    // 测试初始化接口
    int result = uart.init();
    TEST_ASSERT_EQUAL(SUCCESS, result);
    
    // 测试写接口
    uint8_t data[] = {0x01, 0x02, 0x03};
    result = uart.write(data, 3);
    TEST_ASSERT_EQUAL(3, result);
    
    // 测试读接口
    uint8_t buffer[10];
    result = uart.read(buffer, 10);
    TEST_ASSERT_TRUE(result >= 0);
    
    // 测试关闭接口
    result = uart.close();
    TEST_ASSERT_EQUAL(SUCCESS, result);
}
```

**2. 数据结构接口**

```c
// 共享数据结构
typedef struct {
    float temperature;
    float humidity;
    uint32_t timestamp;
    bool valid;
} sensor_data_t;

// 生产者模块
void sensor_module_produce(sensor_data_t* data) {
    data->temperature = read_temperature();
    data->humidity = read_humidity();
    data->timestamp = get_timestamp();
    data->valid = true;
}

// 消费者模块
void display_module_consume(const sensor_data_t* data) {
    if (data->valid) {
        display_temperature(data->temperature);
        display_humidity(data->humidity);
    }
}

// 接口测试
void test_sensor_data_interface(void) {
    sensor_data_t data;
    
    // 测试生产者
    sensor_module_produce(&data);
    TEST_ASSERT_TRUE(data.valid);
    TEST_ASSERT_TRUE(data.temperature >= -40.0 && data.temperature <= 85.0);
    
    // 测试消费者
    display_module_consume(&data);
    // 验证显示正确
}
```


**3. 消息队列接口**

```c
// 消息队列接口
typedef struct {
    uint8_t msg_id;
    uint8_t data[32];
    size_t length;
} message_t;

// 发送模块
void sender_module_send(message_t* msg) {
    msg->msg_id = MSG_SENSOR_DATA;
    msg->length = 4;
    memcpy(msg->data, sensor_data, 4);
    queue_send(msg);
}

// 接收模块
void receiver_module_receive(void) {
    message_t msg;
    if (queue_receive(&msg, 100)) {
        process_message(&msg);
    }
}

// 接口测试
void test_message_queue_interface(void) {
    message_t sent_msg, received_msg;
    
    // 发送消息
    sent_msg.msg_id = MSG_TEST;
    sent_msg.length = 4;
    memcpy(sent_msg.data, "TEST", 4);
    queue_send(&sent_msg);
    
    // 接收消息
    bool received = queue_receive(&received_msg, 1000);
    
    TEST_ASSERT_TRUE(received);
    TEST_ASSERT_EQUAL(MSG_TEST, received_msg.msg_id);
    TEST_ASSERT_EQUAL(4, received_msg.length);
    TEST_ASSERT_EQUAL_MEMORY("TEST", received_msg.data, 4);
}
```

**4. 回调接口**

```c
// 回调函数类型
typedef void (*event_callback_t)(int event_type, void* data);

// 事件生成模块
typedef struct {
    event_callback_t callback;
    void* user_data;
} event_generator_t;

void event_generator_register(event_generator_t* gen, 
                              event_callback_t callback,
                              void* user_data) {
    gen->callback = callback;
    gen->user_data = user_data;
}

void event_generator_trigger(event_generator_t* gen, int event_type) {
    if (gen->callback) {
        gen->callback(event_type, gen->user_data);
    }
}

// 事件处理模块
static int received_event = 0;

void event_handler_callback(int event_type, void* data) {
    received_event = event_type;
    // 处理事件
}

// 接口测试
void test_callback_interface(void) {
    event_generator_t generator;
    received_event = 0;
    
    // 注册回调
    event_generator_register(&generator, event_handler_callback, NULL);
    
    // 触发事件
    event_generator_trigger(&generator, EVENT_ALARM);
    
    // 验证回调被调用
    TEST_ASSERT_EQUAL(EVENT_ALARM, received_event);
}
```


### 集成测试工具

#### 1. CppUTest集成测试

CppUTest不仅支持单元测试，也适合集成测试。

```cpp
#include "CppUTest/TestHarness.h"
#include "ecg_monitor.h"
#include "ecg_acquisition.h"
#include "ecg_processing.h"

TEST_GROUP(ECGMonitorIntegration)
{
    ecg_monitor_t* monitor;
    
    void setup() {
        monitor = ecg_monitor_create();
    }
    
    void teardown() {
        ecg_monitor_destroy(monitor);
    }
};

TEST(ECGMonitorIntegration, AcquisitionToProcessingDataFlow)
{
    // 启动采集
    ecg_monitor_start_acquisition(monitor);
    
    // 等待数据采集
    delay_ms(100);
    
    // 触发处理
    ecg_result_t result = ecg_monitor_process(monitor);
    
    // 验证数据流
    CHECK_EQUAL(ECG_SUCCESS, result.status);
    CHECK(result.heart_rate >= 40 && result.heart_rate <= 200);
}

TEST(ECGMonitorIntegration, ProcessingToAlarmIntegration)
{
    // 模拟异常心率数据
    ecg_monitor_inject_test_data(monitor, abnormal_ecg_data, 100);
    
    // 处理数据
    ecg_result_t result = ecg_monitor_process(monitor);
    
    // 验证报警触发
    CHECK_EQUAL(ECG_ABNORMAL_RATE, result.status);
    CHECK_TRUE(ecg_monitor_is_alarm_active(monitor));
}
```

#### 2. Robot Framework集成测试

Robot Framework适合高层集成测试和验收测试。

```robot
*** Settings ***
Library    SerialLibrary
Library    Collections

*** Variables ***
${DEVICE_PORT}    COM3
${BAUD_RATE}      115200

*** Test Cases ***
Test Blood Pressure Measurement Integration
    [Documentation]    测试血压测量完整流程
    [Tags]    integration    blood-pressure
    
    # 连接设备
    Open Serial Port    ${DEVICE_PORT}    ${BAUD_RATE}
    
    # 发送测量命令
    Send Command    START_MEASUREMENT
    
    # 等待测量完成
    ${response}=    Wait For Response    timeout=30s
    
    # 验证结果
    Should Contain    ${response}    MEASUREMENT_COMPLETE
    ${systolic}=    Extract Systolic    ${response}
    ${diastolic}=    Extract Diastolic    ${response}
    
    Should Be True    ${systolic} >= 90
    Should Be True    ${systolic} <= 200
    Should Be True    ${diastolic} >= 60
    Should Be True    ${diastolic} <= 120
    
    # 关闭连接
    Close Serial Port

Test Sensor Data Flow Integration
    [Documentation]    测试传感器数据流集成
    
    # 初始化系统
    Initialize System
    
    # 启动传感器
    Start Sensor Acquisition
    
    # 验证数据流
    ${data}=    Get Sensor Data
    Should Not Be Empty    ${data}
    
    # 验证处理结果
    ${processed}=    Get Processed Data
    Should Be Equal    ${processed.status}    SUCCESS
```


#### 3. Python集成测试脚本

Python适合编写灵活的集成测试脚本。

```python
import serial
import time
import unittest

class BloodPressureMonitorIntegrationTest(unittest.TestCase):
    """血压监测系统集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.device = serial.Serial('COM3', 115200, timeout=5)
        time.sleep(1)  # 等待设备初始化
    
    def tearDown(self):
        """测试后清理"""
        self.device.close()
    
    def test_measurement_flow(self):
        """测试完整测量流程"""
        # 发送开始测量命令
        self.device.write(b'START_MEASUREMENT\n')
        
        # 等待测量完成
        response = self.device.readline().decode('utf-8')
        
        # 验证响应
        self.assertIn('MEASUREMENT_COMPLETE', response)
        
        # 解析结果
        systolic, diastolic = self.parse_bp_result(response)
        
        # 验证范围
        self.assertGreaterEqual(systolic, 90)
        self.assertLessEqual(systolic, 200)
        self.assertGreaterEqual(diastolic, 60)
        self.assertLessEqual(diastolic, 120)
    
    def test_error_handling_integration(self):
        """测试错误处理集成"""
        # 模拟传感器故障
        self.device.write(b'SIMULATE_SENSOR_FAULT\n')
        
        # 尝试测量
        self.device.write(b'START_MEASUREMENT\n')
        
        # 验证错误响应
        response = self.device.readline().decode('utf-8')
        self.assertIn('ERROR_SENSOR_FAULT', response)
    
    def parse_bp_result(self, response):
        """解析血压结果"""
        # 格式: "MEASUREMENT_COMPLETE:SYS=120,DIA=80"
        parts = response.split(':')[1].split(',')
        systolic = int(parts[0].split('=')[1])
        diastolic = int(parts[1].split('=')[1])
        return systolic, diastolic

if __name__ == '__main__':
    unittest.main()
```


### 医疗器械软件集成测试最佳实践

#### 1. 遵循IEC 62304要求

**IEC 62304集成测试要求**：

```c
/**
 * @test_id: IT_ECG_001
 * @requirement: REQ_ECG_INT_001
 * @description: 验证ECG采集与处理模块集成
 * @safety_class: C
 * @integration_level: 模块间接口
 * @test_type: 接口测试
 */
void test_ecg_acquisition_processing_integration(void) {
    // 初始化模块
    ecg_acquisition_init();
    ecg_processing_init();
    
    // 启动采集
    ecg_acquisition_start();
    
    // 获取数据
    int16_t* raw_data;
    size_t length;
    ecg_acquisition_get_data(&raw_data, &length);
    
    // 处理数据
    ecg_result_t result;
    int status = ecg_processing_analyze(raw_data, length, &result);
    
    // 验证集成
    TEST_ASSERT_EQUAL(ECG_SUCCESS, status);
    TEST_ASSERT_NOT_NULL(raw_data);
    TEST_ASSERT_TRUE(length > 0);
    TEST_ASSERT_TRUE(result.heart_rate >= 40 && result.heart_rate <= 200);
}
```

#### 2. 测试可追溯性

建立需求到集成测试的追溯矩阵：

```
需求ID          | 设计ID        | 集成测试ID
----------------|--------------|------------------
REQ_BP_001      | DES_BP_001   | IT_BP_001, IT_BP_002
REQ_BP_002      | DES_BP_002   | IT_BP_003
REQ_ALARM_001   | DES_ALARM_001| IT_ALARM_001
```

**说明**: 这是需求到集成测试的追溯矩阵示例。展示了需求ID、设计ID和集成测试ID之间的对应关系，确保每个需求都有对应的集成测试，实现完整的可追溯性。


#### 3. 接口文档化

```c
/**
 * @interface: ECG_Processing_Interface
 * @description: ECG处理模块接口
 * @provider: ecg_processing.c
 * @consumer: ecg_monitor.c
 * 
 * @input_data:
 *   - raw_ecg_data: int16_t数组，采样数据
 *   - length: 数据长度，范围[100, 1000]
 * 
 * @output_data:
 *   - result: ecg_result_t结构体
 *   - status: 处理状态码
 * 
 * @preconditions:
 *   - ECG采集模块已初始化
 *   - 数据有效且长度足够
 * 
 * @postconditions:
 *   - 返回有效的心率值
 *   - 状态码指示处理结果
 */
int ecg_processing_analyze(const int16_t* raw_ecg_data,
                           size_t length,
                           ecg_result_t* result);
```


#### 4. 数据流测试

验证数据在模块间的正确传递。

```c
void test_sensor_to_display_data_flow(void) {
    // 1. 传感器采集数据
    sensor_data_t sensor_data;
    sensor_read(&sensor_data);
    TEST_ASSERT_TRUE(sensor_data.valid);
    
    // 2. 数据处理
    processed_data_t processed;
    process_sensor_data(&sensor_data, &processed);
    TEST_ASSERT_EQUAL(PROCESS_SUCCESS, processed.status);
    
    // 3. 数据显示
    display_update(&processed);
    
    // 4. 验证端到端数据一致性
    float displayed_value = display_get_current_value();
    TEST_ASSERT_FLOAT_WITHIN(0.1, sensor_data.raw_value, displayed_value);
}
```

#### 5. 时序测试

验证模块间的时序关系。

```c
void test_alarm_response_timing(void) {
    uint32_t start_time, alarm_time;
    
    // 记录开始时间
    start_time = get_timestamp_ms();
    
    // 触发异常条件
    inject_critical_heart_rate(250);
    
    // 等待报警
    while (!is_alarm_triggered() && 
           (get_timestamp_ms() - start_time) < 1000) {
        delay_ms(10);
    }
    
    alarm_time = get_timestamp_ms();
    
    // 验证响应时间 < 500ms（IEC 60601-1-8要求）
    uint32_t response_time = alarm_time - start_time;
    TEST_ASSERT_TRUE(response_time < 500);
}
```

#### 6. 错误传播测试

验证错误在模块间的正确传播。

```c
void test_error_propagation(void) {
    // 1. 底层模块产生错误
    sensor_simulate_fault();
    
    // 2. 中间层检测错误
    int status = data_acquisition_read();
    TEST_ASSERT_EQUAL(ERROR_SENSOR_FAULT, status);
    
    // 3. 顶层处理错误
    system_status_t sys_status = system_get_status();
    TEST_ASSERT_EQUAL(SYSTEM_ERROR, sys_status.state);
    TEST_ASSERT_TRUE(sys_status.error_logged);
    
    // 4. 验证用户通知
    TEST_ASSERT_TRUE(is_error_displayed());
}
```


#### 7. 资源竞争测试

测试多模块访问共享资源的情况。

```c
void test_shared_resource_access(void) {
    // 初始化共享资源
    shared_buffer_t buffer;
    shared_buffer_init(&buffer);
    
    // 模块A写入
    uint8_t data_a[] = {0x01, 0x02, 0x03};
    int result_a = module_a_write(&buffer, data_a, 3);
    TEST_ASSERT_EQUAL(SUCCESS, result_a);
    
    // 模块B读取
    uint8_t read_buffer[10];
    int result_b = module_b_read(&buffer, read_buffer, 10);
    TEST_ASSERT_EQUAL(3, result_b);
    TEST_ASSERT_EQUAL_MEMORY(data_a, read_buffer, 3);
    
    // 验证互斥访问
    TEST_ASSERT_FALSE(buffer.is_locked);
}
```

#### 8. 持续集成中的集成测试

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on: [push, pull_request]

jobs:
  integration-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Build system
      run: |
        mkdir build
        cd build
        cmake ..
        make
    
    - name: Run integration tests
      run: |
        cd build
        ./integration_tests
    
    - name: Check test results
      run: |
        if [ $? -ne 0 ]; then
          echo "Integration tests failed"
          exit 1
        fi
    
    - name: Generate test report
      run: |
        cd build
        ./integration_tests --gtest_output=xml:integration_test_results.xml
    
    - name: Upload test results
      uses: actions/upload-artifact@v2
      with:
        name: integration-test-results
        path: build/integration_test_results.xml
```


### 常见陷阱

!!! warning "注意事项"
    
    **1. 过早集成**
    ```c
    // 错误：单元测试未完成就集成
    void test_premature_integration(void) {
        // 模块A和B都未充分单元测试
        module_a_init();  // 可能有bug
        module_b_init();  // 可能有bug
        
        // 集成测试失败，难以定位问题
        int result = integrate_a_and_b();
        // 是A的问题？B的问题？还是接口问题？
    }
    
    // 正确：确保单元测试通过后再集成
    void test_proper_integration(void) {
        // 前提：module_a和module_b已通过所有单元测试
        module_a_init();
        module_b_init();
        
        // 现在集成测试失败，可以确定是接口问题
        int result = integrate_a_and_b();
    }
    ```
    
    **2. 忽略接口边界条件**
    ```c
    // 错误：只测试正常情况
    void test_incomplete_interface(void) {
        uint8_t data[] = {0x01, 0x02};
        int result = send_data(data, 2);
        TEST_ASSERT_EQUAL(SUCCESS, result);
        // 没有测试边界条件
    }
    
    // 正确：测试边界和异常情况
    void test_complete_interface(void) {
        // 正常情况
        uint8_t data[] = {0x01, 0x02};
        TEST_ASSERT_EQUAL(SUCCESS, send_data(data, 2));
        
        // 边界：空数据
        TEST_ASSERT_EQUAL(ERROR_INVALID, send_data(NULL, 0));
        
        // 边界：最大长度
        uint8_t max_data[MAX_SIZE];
        TEST_ASSERT_EQUAL(SUCCESS, send_data(max_data, MAX_SIZE));
        
        // 边界：超过最大长度
        TEST_ASSERT_EQUAL(ERROR_TOO_LARGE, send_data(max_data, MAX_SIZE + 1));
    }
    ```
    
    **3. 测试环境不真实**
    ```c
    // 错误：使用过度简化的桩
    int sensor_read_stub(void) {
        return 100;  // 总是返回固定值
    }
    
    // 正确：使用更真实的模拟
    int sensor_read_realistic_stub(void) {
        static int count = 0;
        // 模拟真实传感器的变化
        return 95 + (count++ % 10);  // 95-104之间变化
    }
    ```
    
    **4. 忽略时序问题**
    ```c
    // 错误：假设立即完成
    void test_ignoring_timing(void) {
        start_async_operation();
        int result = get_result();  // 可能还未完成
        TEST_ASSERT_EQUAL(EXPECTED, result);  // 不稳定
    }
    
    // 正确：考虑异步操作
    void test_with_timing(void) {
        start_async_operation();
        
        // 等待完成或超时
        int timeout = 1000;  // ms
        while (!is_operation_complete() && timeout > 0) {
            delay_ms(10);
            timeout -= 10;
        }
        
        TEST_ASSERT_TRUE(is_operation_complete());
        int result = get_result();
        TEST_ASSERT_EQUAL(EXPECTED, result);
    }
    ```
    
    **5. 测试依赖顺序**
    ```c
    // 错误：测试之间有依赖
    static int global_state = 0;
    
    void test_first(void) {
        global_state = 5;
        TEST_ASSERT_EQUAL(5, global_state);
    }
    
    void test_second(void) {
        // 依赖test_first的结果
        TEST_ASSERT_EQUAL(5, global_state);  // 错误！
    }
    
    // 正确：每个测试独立
    void setUp(void) {
        global_state = 0;  // 每次重置
    }
    
    void test_independent_1(void) {
        global_state = 5;
        TEST_ASSERT_EQUAL(5, global_state);
    }
    
    void test_independent_2(void) {
        // 不依赖其他测试
        global_state = 10;
        TEST_ASSERT_EQUAL(10, global_state);
    }
    ```


## 最佳实践

### 集成测试策略选择

**选择指南**：

| 项目特点 | 推荐策略 | 理由 |
|---------|---------|------|
| 需求明确，控制流程清晰 | 自顶向下 | 早期验证主要流程 |
| 硬件相关，底层复杂 | 自底向上 | 充分测试硬件接口 |
| 大型系统，多团队 | 三明治 | 并行开发，风险分散 |
| 小型系统，时间紧 | 大爆炸 | 快速集成 |

### 测试数据管理

```c
// 使用测试数据生成器
typedef struct {
    int16_t* data;
    size_t length;
} test_ecg_data_t;

test_ecg_data_t* generate_test_ecg_data(int heart_rate, int duration_sec) {
    test_ecg_data_t* test_data = malloc(sizeof(test_ecg_data_t));
    test_data->length = duration_sec * SAMPLE_RATE;
    test_data->data = malloc(test_data->length * sizeof(int16_t));
    
    // 生成模拟ECG数据
    for (size_t i = 0; i < test_data->length; i++) {
        test_data->data[i] = generate_ecg_sample(i, heart_rate);
    }
    
    return test_data;
}

// 使用
void test_with_generated_data(void) {
    test_ecg_data_t* data = generate_test_ecg_data(75, 10);  // 75bpm, 10秒
    
    ecg_result_t result = ecg_process(data->data, data->length);
    
    TEST_ASSERT_INT_WITHIN(5, 75, result.heart_rate);
    
    free_test_data(data);
}
```

### 测试覆盖率

**集成测试覆盖目标**：
- 接口覆盖：100%（所有接口都测试）
- 数据流覆盖：100%（所有数据路径）
- 控制流覆盖：≥90%（主要控制路径）
- 错误路径覆盖：100%（所有错误处理）


## 实践练习

1. **基础练习**：为一个包含传感器读取和数据处理两个模块的系统设计集成测试计划，选择合适的集成策略。

2. **中级练习**：实现一个血压监测系统的集成测试：
   - 测试传感器与ADC接口
   - 测试数据采集与处理模块集成
   - 测试处理与显示模块集成
   - 验证完整数据流

3. **高级练习**：为一个多模块ECG监护系统编写完整的集成测试套件：
   - 使用自顶向下策略
   - 编写必要的桩
   - 测试所有模块间接口
   - 测试错误传播
   - 测试时序要求
   - 生成测试报告

4. **综合练习**：建立集成测试CI/CD流程：
   - 配置自动化集成测试
   - 集成硬件在环测试（如果可用）
   - 生成接口覆盖率报告
   - 设置测试通过标准

## 相关资源

### 相关知识模块

- [单元测试](unit-testing.md) - 模块内部测试
- [系统测试](system-testing.md) - 完整系统验证
- [接口设计](../architecture-design/interface-design.md) - 接口设计原则

### 深入学习

- [测试策略概述](index.md) - 测试策略整体框架
- [架构设计](../architecture-design/index.md) - 软件架构设计

### 工具和框架

- [CppUTest](https://cpputest.github.io/) - C/C++测试框架
- [Robot Framework](https://robotframework.org/) - 验收测试框架
- [pytest](https://pytest.org/) - Python测试框架
- [Jenkins](https://www.jenkins.io/) - 持续集成工具


## 参考文献

1. IEC 62304:2006+AMD1:2015 - Medical device software - Software life cycle processes, Section 5.6 (Software Integration and Integration Testing)
2. "Software Testing: A Craftsman's Approach" by Paul C. Jorgensen
3. "Embedded Software Development for Safety-Critical Systems" by Chris Hobbs, Chapter 8 (Integration Testing)
4. IEEE 829-2008 - IEEE Standard for Software and System Test Documentation
5. "Continuous Integration: Improving Software Quality and Reducing Risk" by Paul M. Duvall

## 自测问题

??? question "问题1：什么是集成测试？它与单元测试有什么区别？"
    **问题**：解释集成测试的定义，并说明它与单元测试的主要区别。
    
    ??? success "答案"
        **集成测试定义**：
        集成测试是将已通过单元测试的软件模块组合在一起，测试模块间接口和交互的测试活动。
        
        **主要区别**：
        
        | 维度 | 单元测试 | 集成测试 |
        |------|---------|---------|
        | 测试范围 | 单个函数/模块 | 多个模块的接口 |
        | 测试目标 | 验证单元功能 | 验证模块间交互 |
        | 依赖处理 | 隔离（Mock/Stub） | 使用真实依赖 |
        | 执行速度 | 非常快（毫秒） | 较慢（秒级） |
        | 缺陷定位 | 精确到函数 | 定位到模块间 |
        | 测试环境 | 简单 | 复杂 |
        | 执行时机 | 开发阶段 | 集成阶段 |
        
        **示例对比**：
        ```c
        // 单元测试：测试单个函数
        void test_calculate_heart_rate(void) {
            int16_t ecg_data[100];
            // 使用测试数据
            int hr = calculate_heart_rate(ecg_data, 100);
            TEST_ASSERT_INT_WITHIN(5, 75, hr);
        }
        
        // 集成测试：测试模块间交互
        void test_ecg_acquisition_to_processing(void) {
            // 启动采集模块
            ecg_acquisition_start();
            
            // 获取数据
            int16_t* data = ecg_acquisition_get_data();
            
            // 传递给处理模块
            ecg_result_t result = ecg_processing_analyze(data);
            
            // 验证集成
            TEST_ASSERT_EQUAL(ECG_SUCCESS, result.status);
        }
        ```
        
        **知识点回顾**：单元测试关注单个单元的正确性，集成测试关注模块间的协作和接口。


??? question "问题2：什么是自顶向下集成策略？它的优缺点是什么？"
    **问题**：解释自顶向下集成策略的概念、工作流程和优缺点。
    
    ??? success "答案"
        **自顶向下集成定义**：
        从顶层模块开始，逐步向下集成低层模块的集成策略。未完成的低层模块用桩（Stub）代替。
        
        **工作流程**：
        ```
        1. 测试顶层主控模块（使用桩）
        2. 集成第一层子模块（替换桩）
        3. 测试顶层与第一层的集成
        4. 集成第二层子模块（替换桩）
        5. 测试到第二层的集成
        6. 重复直到所有模块集成完成
        ```
        
        **示例**：
        ```c
        // 步骤1：测试主控（使用桩）
        void test_monitor_with_stubs(void) {
            monitor_t monitor;
            monitor.sensor = &sensor_stub;      // 桩
            monitor.processor = &processor_stub; // 桩
            
            monitor_init(&monitor);
            TEST_ASSERT_TRUE(monitor.initialized);
        }
        
        // 步骤2：集成真实传感器模块
        void test_monitor_with_real_sensor(void) {
            monitor_t monitor;
            monitor.sensor = sensor_create();    // 真实模块
            monitor.processor = &processor_stub; // 仍用桩
            
            monitor_start(&monitor);
            // 测试主控与传感器的集成
        }
        
        // 步骤3：集成真实处理模块
        void test_monitor_with_all_real_modules(void) {
            monitor_t monitor;
            monitor.sensor = sensor_create();    // 真实模块
            monitor.processor = processor_create(); // 真实模块
            
            // 测试完整集成
        }
        ```
        
        **优点**：
        - ✓ 早期验证主要控制流程
        - ✓ 早期发现设计问题
        - ✓ 问题定位相对容易
        - ✓ 适合需求明确的系统
        - ✓ 可以并行开发底层模块
        
        **缺点**：
        - ✗ 需要编写大量桩
        - ✗ 桩的质量影响测试效果
        - ✗ 底层模块测试延迟
        - ✗ 可能遗漏底层问题
        - ✗ 桩维护成本高
        
        **适用场景**：
        - 需求明确，控制流程清晰
        - 顶层设计是关键
        - 底层模块相对简单
        - 需要早期演示系统功能
        
        **知识点回顾**：自顶向下策略从主控开始，逐层向下集成，适合控制流程明确的系统。

??? question "问题3：什么是自底向上集成策略？它与自顶向下有什么区别？"
    **问题**：解释自底向上集成策略，并与自顶向下策略对比。
    
    ??? success "答案"
        **自底向上集成定义**：
        从底层模块开始，逐步向上集成高层模块的集成策略。未完成的高层模块用驱动器（Driver）代替。
        
        **工作流程**：
        ```
        1. 测试底层模块（使用驱动器）
        2. 集成中间层模块
        3. 测试底层与中间层的集成
        4. 集成上层模块
        5. 测试到上层的集成
        6. 重复直到主控模块集成完成
        ```
        
        **示例**：
        ```c
        // 步骤1：测试底层ADC驱动
        void test_adc_driver(void) {
            adc_init();
            int16_t value = adc_read(0);
            TEST_ASSERT_TRUE(value >= 0 && value <= 4095);
        }
        
        // 驱动器：模拟上层调用
        void driver_test_adc(void) {
            adc_init();
            for (int i = 0; i < 10; i++) {
                int16_t value = adc_read(0);
                printf("ADC: %d\n", value);
            }
        }
        
        // 步骤2：集成传感器接口层
        void test_sensor_with_adc(void) {
            sensor_t sensor;
            sensor_init(&sensor);  // 内部使用ADC
            
            float value = sensor_read(&sensor);
            TEST_ASSERT_TRUE(value >= 0);
        }
        
        // 步骤3：集成主控
        void test_complete_system(void) {
            system_t system;
            system_init(&system);  // 使用所有底层模块
            
            system_start(&system);
            // 测试完整系统
        }
        ```
        
        **与自顶向下对比**：
        
        | 特性 | 自顶向下 | 自底向上 |
        |------|---------|---------|
        | 起点 | 顶层主控 | 底层模块 |
        | 方向 | 向下集成 | 向上集成 |
        | 替代品 | 桩（Stub） | 驱动器（Driver） |
        | 早期验证 | 控制流程 | 底层功能 |
        | 适用场景 | 需求明确 | 硬件相关 |
        
        **优点**：
        - ✓ 底层模块充分测试
        - ✓ 不需要桩
        - ✓ 适合硬件相关系统
        - ✓ 底层问题早期发现
        - ✓ 可以并行开发上层模块
        
        **缺点**：
        - ✗ 需要编写驱动器
        - ✗ 主要控制流程测试延迟
        - ✗ 可能遗漏高层设计问题
        - ✗ 系统功能演示延迟
        
        **适用场景**：
        - 硬件接口复杂
        - 底层功能是关键
        - 硬件依赖性强
        - 底层模块先完成
        
        **知识点回顾**：自底向上策略从底层开始，逐层向上集成，适合硬件相关的系统。


??? question "问题4：接口测试应该测试哪些方面？"
    **问题**：列举接口测试的主要测试点和注意事项。
    
    ??? success "答案"
        **接口测试主要测试点**：
        
        **1. 数据传递正确性**
        ```c
        void test_data_transfer(void) {
            // 发送数据
            sensor_data_t sent_data = {
                .temperature = 36.5,
                .humidity = 60.0,
                .valid = true
            };
            
            module_a_send(&sent_data);
            
            // 接收数据
            sensor_data_t received_data;
            module_b_receive(&received_data);
            
            // 验证数据完整性
            TEST_ASSERT_FLOAT_WITHIN(0.01, sent_data.temperature, 
                                    received_data.temperature);
            TEST_ASSERT_FLOAT_WITHIN(0.01, sent_data.humidity, 
                                    received_data.humidity);
            TEST_ASSERT_EQUAL(sent_data.valid, received_data.valid);
        }
        ```
        
        **2. 参数有效性验证**
        ```c
        void test_parameter_validation(void) {
            // 正常参数
            TEST_ASSERT_EQUAL(SUCCESS, interface_call(valid_param));
            
            // NULL指针
            TEST_ASSERT_EQUAL(ERROR_NULL, interface_call(NULL));
            
            // 无效值
            TEST_ASSERT_EQUAL(ERROR_INVALID, interface_call(invalid_param));
            
            // 边界值
            TEST_ASSERT_EQUAL(SUCCESS, interface_call(min_valid));
            TEST_ASSERT_EQUAL(SUCCESS, interface_call(max_valid));
            TEST_ASSERT_EQUAL(ERROR_RANGE, interface_call(below_min));
            TEST_ASSERT_EQUAL(ERROR_RANGE, interface_call(above_max));
        }
        ```
        
        **3. 返回值验证**
        ```c
        void test_return_values(void) {
            // 成功情况
            int result = operation_success();
            TEST_ASSERT_EQUAL(SUCCESS, result);
            
            // 失败情况
            result = operation_failure();
            TEST_ASSERT_EQUAL(ERROR_CODE, result);
            
            // 返回数据有效性
            data_t* data = get_data();
            TEST_ASSERT_NOT_NULL(data);
            TEST_ASSERT_TRUE(data->valid);
        }
        ```
        
        **4. 错误处理**
        ```c
        void test_error_handling(void) {
            // 模拟错误条件
            simulate_error_condition();
            
            // 调用接口
            int result = interface_call();
            
            // 验证错误处理
            TEST_ASSERT_EQUAL(ERROR_EXPECTED, result);
            TEST_ASSERT_TRUE(error_logged());
            TEST_ASSERT_TRUE(system_in_safe_state());
        }
        ```
        
        **5. 时序要求**
        ```c
        void test_timing_requirements(void) {
            uint32_t start = get_timestamp_ms();
            
            // 调用接口
            interface_call();
            
            uint32_t end = get_timestamp_ms();
            uint32_t duration = end - start;
            
            // 验证响应时间
            TEST_ASSERT_TRUE(duration < MAX_RESPONSE_TIME_MS);
        }
        ```
        
        **6. 并发访问**
        ```c
        void test_concurrent_access(void) {
            // 模拟并发调用
            thread_1_call_interface();
            thread_2_call_interface();
            
            // 验证数据一致性
            TEST_ASSERT_TRUE(data_consistent());
            
            // 验证无死锁
            TEST_ASSERT_FALSE(deadlock_detected());
        }
        ```
        
        **7. 资源管理**
        ```c
        void test_resource_management(void) {
            // 分配资源
            resource_t* res = interface_allocate();
            TEST_ASSERT_NOT_NULL(res);
            
            // 使用资源
            interface_use(res);
            
            // 释放资源
            interface_free(res);
            
            // 验证资源已释放
            TEST_ASSERT_TRUE(resource_freed(res));
        }
        ```
        
        **测试检查清单**：
        ```
        ☐ 数据传递完整性
        ☐ 参数有效性验证
        ☐ 返回值正确性
        ☐ 错误处理机制
        ☐ 时序要求满足
        ☐ 并发访问安全
        ☐ 资源正确管理
        ☐ 边界条件处理
        ☐ 异常情况处理
        ☐ 接口文档一致性
        ```
        
        **知识点回顾**：接口测试需要全面验证数据传递、参数验证、错误处理、时序和资源管理等多个方面。

??? question "问题5：如何为医疗器械软件设计有效的集成测试？"
    **问题**：列举医疗器械软件集成测试的最佳实践。
    
    ??? success "答案"
        **医疗器械软件集成测试最佳实践**：
        
        **1. 遵循IEC 62304要求**
        ```c
        /**
         * @test_id: IT_ALARM_001
         * @requirement: REQ_ALARM_INT_001
         * @description: 验证报警模块与监测模块集成
         * @safety_class: C
         * @integration_level: 模块间接口
         * @preconditions: 监测模块和报警模块已通过单元测试
         * @test_steps:
         *   1. 初始化监测和报警模块
         *   2. 触发异常条件
         *   3. 验证报警触发
         *   4. 验证报警内容正确
         */
        void test_monitoring_alarm_integration(void) {
            // 实现测试...
        }
        ```
        
        **2. 建立追溯矩阵**
        ```
        需求 → 设计 → 接口规范 → 集成测试
        
        REQ_001 → DES_001 → IF_001 → IT_001, IT_002
        REQ_002 → DES_002 → IF_002 → IT_003
        ```
        
        **3. 测试安全关键路径**
        ```c
        void test_safety_critical_integration(void) {
            // 测试报警路径
            inject_critical_condition();
            TEST_ASSERT_TRUE(alarm_triggered_within_time(500));
            
            // 测试故障安全
            simulate_sensor_fault();
            TEST_ASSERT_TRUE(system_in_safe_state());
            
            // 测试错误恢复
            clear_fault();
            TEST_ASSERT_TRUE(system_recovers());
        }
        ```
        
        **4. 验证数据完整性**
        ```c
        void test_data_integrity(void) {
            // 端到端数据验证
            sensor_data_t input = generate_test_data();
            
            // 数据流经多个模块
            processed_data_t output = complete_data_flow(input);
            
            // 验证数据未损坏
            TEST_ASSERT_TRUE(data_integrity_check(input, output));
        }
        ```
        
        **5. 测试错误传播**
        ```c
        void test_error_propagation(void) {
            // 底层错误
            inject_low_level_error();
            
            // 验证错误向上传播
            TEST_ASSERT_EQUAL(ERROR_STATE, mid_level_status());
            TEST_ASSERT_EQUAL(ERROR_STATE, top_level_status());
            
            // 验证用户通知
            TEST_ASSERT_TRUE(error_displayed_to_user());
        }
        ```
        
        **6. 性能和时序测试**
        ```c
        void test_performance_requirements(void) {
            // 测试响应时间
            uint32_t response_time = measure_response_time();
            TEST_ASSERT_TRUE(response_time < MAX_ALLOWED_MS);
            
            // 测试吞吐量
            int throughput = measure_throughput();
            TEST_ASSERT_TRUE(throughput >= MIN_REQUIRED);
        }
        ```
        
        **7. 持续集成**
        ```bash
        # 每次提交自动运行集成测试
        git push → CI触发 → 构建 → 单元测试 → 集成测试 → 报告
        ```
        
        **8. 测试文档化**
        ```
        - 测试计划文档
        - 接口规范文档
        - 测试用例文档
        - 测试结果报告
        - 缺陷跟踪记录
        ```
        
        **9. 风险驱动测试**
        ```
        高风险接口 → 更多测试用例
        安全关键路径 → 100%覆盖
        复杂集成点 → 额外验证
        ```
        
        **10. 定期审查**
        ```
        ☐ 测试是否覆盖所有接口？
        ☐ 测试是否反映最新设计？
        ☐ 是否有新的集成风险？
        ☐ 测试结果是否可追溯？
        ```
        
        **知识点回顾**：医疗器械软件集成测试需要遵循标准、关注安全、全面覆盖、持续集成和完整文档化。
