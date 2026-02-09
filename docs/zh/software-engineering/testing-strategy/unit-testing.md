---
title: 单元测试
description: 单元测试基础知识，包括测试框架、测试用例设计、覆盖率分析和最佳实践
difficulty: 中级
estimated_time: 3小时
tags:
- 单元测试
- 测试框架
- 代码覆盖率
- TDD
related_modules:
- zh/software-engineering/testing-strategy/integration-testing
- zh/software-engineering/testing-strategy/system-testing
- zh/software-engineering/coding-standards/code-review-checklist
last_updated: '2026-02-09'
version: '1.0'
language: zh-CN
---

# 单元测试

## 学习目标

完成本模块后，你将能够：
- 理解单元测试的概念和重要性
- 掌握常用的单元测试框架（Unity、CppUTest、Google Test）
- 编写高质量的单元测试用例
- 使用代码覆盖率工具分析测试完整性
- 应用测试驱动开发（TDD）方法
- 遵循医疗器械软件单元测试的最佳实践

## 前置知识

- C/C++编程基础
- 函数和模块化设计
- 基本的软件工程概念
- IEC 62304标准基础知识

## 内容

### 单元测试基础

**单元测试定义**：
单元测试是对软件中最小可测试单元（通常是函数或方法）进行验证的测试活动。

**单元测试的目的**：
- 验证代码功能正确性
- 及早发现缺陷（成本最低）
- 支持代码重构
- 作为代码文档
- 提高代码质量和可维护性

**单元测试特点**：
```
✓ 快速执行（毫秒级）
✓ 独立运行（不依赖外部资源）
✓ 可重复（每次结果一致）
✓ 自动化（无需人工干预）
✓ 自验证（明确的通过/失败）
```

**说明**: 这是单元测试的FIRST原则。Fast(快速执行)、Independent(独立运行)、Repeatable(可重复)、Self-validating(自动化)、Timely(及时编写)，这些原则确保单元测试的有效性和可维护性。



### 单元测试框架

#### Unity测试框架

Unity是专为嵌入式C语言设计的轻量级测试框架。

**特点**：
- 轻量级，适合资源受限的嵌入式系统
- 纯C语言实现
- 易于集成
- 支持多种断言

**基本示例**：

```c
#include "unity.h"
#include "temperature_sensor.h"

// 每个测试前执行
void setUp(void) {
    temperature_sensor_init();
}

// 每个测试后执行
void tearDown(void) {
    temperature_sensor_deinit();
}

// 测试用例1：正常温度读取
void test_temperature_read_normal(void) {
    float temperature = temperature_sensor_read();
    
    TEST_ASSERT_FLOAT_WITHIN(0.1, 25.0, temperature);
}

// 测试用例2：温度范围验证
void test_temperature_range_validation(void) {
    bool result = temperature_sensor_validate_range(37.5);
    
    TEST_ASSERT_TRUE(result);
}

// 测试用例3：错误处理
void test_temperature_sensor_error_handling(void) {
    // 模拟传感器故障
    temperature_sensor_simulate_fault();
    
    int error_code = temperature_sensor_read_with_error();
    
    TEST_ASSERT_EQUAL_INT(SENSOR_ERROR_FAULT, error_code);
}

// 主测试运行器
int main(void) {
    UNITY_BEGIN();
    
    RUN_TEST(test_temperature_read_normal);
    RUN_TEST(test_temperature_range_validation);
    RUN_TEST(test_temperature_sensor_error_handling);
    
    return UNITY_END();
}
```

**常用断言**：

```c
// 基本断言
TEST_ASSERT(condition)
TEST_ASSERT_TRUE(condition)
TEST_ASSERT_FALSE(condition)

// 整数断言
TEST_ASSERT_EQUAL_INT(expected, actual)
TEST_ASSERT_EQUAL_UINT(expected, actual)
TEST_ASSERT_INT_WITHIN(delta, expected, actual)

// 浮点数断言
TEST_ASSERT_EQUAL_FLOAT(expected, actual)
TEST_ASSERT_FLOAT_WITHIN(delta, expected, actual)

// 字符串断言
TEST_ASSERT_EQUAL_STRING(expected, actual)
TEST_ASSERT_EQUAL_MEMORY(expected, actual, length)

// 指针断言
TEST_ASSERT_NULL(pointer)
TEST_ASSERT_NOT_NULL(pointer)
```


#### CppUTest框架

CppUTest是为C/C++设计的单元测试框架，支持模拟对象。

**特点**：
- 支持C和C++
- 内置模拟（Mock）支持
- 内存泄漏检测
- 测试隔离

**基本示例**：

```cpp
#include "CppUTest/TestHarness.h"
#include "ecg_processor.h"

TEST_GROUP(ECGProcessor)
{
    void setup() {
        ecg_processor_init();
    }
    
    void teardown() {
        ecg_processor_cleanup();
    }
};

TEST(ECGProcessor, ProcessValidSignal)
{
    // 准备测试数据
    int16_t ecg_data[100];
    for (int i = 0; i < 100; i++) {
        ecg_data[i] = generate_test_ecg_sample(i);
    }
    
    // 执行处理
    ecg_result_t result = ecg_process_signal(ecg_data, 100);
    
    // 验证结果
    CHECK_EQUAL(ECG_SUCCESS, result.status);
    CHECK(result.heart_rate >= 40 && result.heart_rate <= 200);
}

TEST(ECGProcessor, DetectAbnormalHeartRate)
{
    // 模拟异常心率数据
    int16_t abnormal_data[100];
    generate_abnormal_ecg(abnormal_data, 100, 220);  // 220 bpm
    
    ecg_result_t result = ecg_process_signal(abnormal_data, 100);
    
    CHECK_EQUAL(ECG_ABNORMAL_RATE, result.status);
    CHECK(result.alarm_triggered);
}

TEST(ECGProcessor, HandleNoiseInSignal)
{
    int16_t noisy_data[100];
    add_noise_to_signal(noisy_data, 100, 0.3);  // 30% 噪声
    
    ecg_result_t result = ecg_process_signal(noisy_data, 100);
    
    CHECK_EQUAL(ECG_NOISY_SIGNAL, result.status);
}
```

**代码说明**：
- `TEST_GROUP`：定义测试组，包含setup和teardown
- `TEST`：定义单个测试用例
- `CHECK_EQUAL`：验证相等性
- `CHECK`：验证条件为真


#### Google Test框架

Google Test（gtest）是功能强大的C++测试框架。

**特点**：
- 丰富的断言
- 参数化测试
- 死亡测试（异常测试）
- 测试夹具（Fixture）

**基本示例**：

```cpp
#include <gtest/gtest.h>
#include "blood_pressure_monitor.h"

class BloodPressureTest : public ::testing::Test {
protected:
    void SetUp() override {
        bp_monitor = new BloodPressureMonitor();
        bp_monitor->initialize();
    }
    
    void TearDown() override {
        bp_monitor->shutdown();
        delete bp_monitor;
    }
    
    BloodPressureMonitor* bp_monitor;
};

TEST_F(BloodPressureTest, MeasureNormalBloodPressure) {
    // 模拟正常血压测量
    BPReading reading = bp_monitor->measure();
    
    EXPECT_GE(reading.systolic, 90);
    EXPECT_LE(reading.systolic, 140);
    EXPECT_GE(reading.diastolic, 60);
    EXPECT_LE(reading.diastolic, 90);
}

TEST_F(BloodPressureTest, DetectHypertension) {
    // 模拟高血压
    bp_monitor->simulate_reading(160, 100);
    
    BPReading reading = bp_monitor->measure();
    
    EXPECT_EQ(BP_STATUS_HYPERTENSION, reading.status);
    EXPECT_TRUE(reading.alert_triggered);
}

TEST_F(BloodPressureTest, HandleMeasurementError) {
    // 模拟测量错误
    bp_monitor->simulate_sensor_error();
    
    EXPECT_THROW({
        bp_monitor->measure();
    }, MeasurementException);
}

// 参数化测试
class BPValidationTest : public ::testing::TestWithParam<std::tuple<int, int, bool>> {
};

TEST_P(BPValidationTest, ValidateBloodPressureRange) {
    auto [systolic, diastolic, expected_valid] = GetParam();
    
    bool is_valid = validate_bp_reading(systolic, diastolic);
    
    EXPECT_EQ(expected_valid, is_valid);
}

INSTANTIATE_TEST_SUITE_P(
    BPRanges,
    BPValidationTest,
    ::testing::Values(
        std::make_tuple(120, 80, true),   // 正常
        std::make_tuple(160, 100, true),  // 高血压但有效
        std::make_tuple(50, 30, false),   // 过低
        std::make_tuple(250, 150, false)  // 过高
    )
);
```

**代码说明**：
- `TEST_F`：使用测试夹具的测试用例
- `EXPECT_*`：非致命断言（失败后继续）
- `ASSERT_*`：致命断言（失败后停止）
- `EXPECT_THROW`：验证异常抛出
- 参数化测试：用不同参数运行同一测试


### 测试用例设计

#### 等价类划分

将输入域划分为若干等价类，从每个等价类中选择代表性测试用例。

**示例：心率验证函数**

```c
// 被测函数
typedef enum {
    HR_VALID,
    HR_TOO_LOW,
    HR_TOO_HIGH,
    HR_INVALID
} heart_rate_status_t;

heart_rate_status_t validate_heart_rate(int heart_rate) {
    if (heart_rate < 0) {
        return HR_INVALID;
    } else if (heart_rate < 40) {
        return HR_TOO_LOW;
    } else if (heart_rate <= 200) {
        return HR_VALID;
    } else {
        return HR_TOO_HIGH;
    }
}

// 测试用例
void test_heart_rate_validation(void) {
    // 等价类1：无效值（< 0）
    TEST_ASSERT_EQUAL(HR_INVALID, validate_heart_rate(-1));
    
    // 等价类2：过低（0-39）
    TEST_ASSERT_EQUAL(HR_TOO_LOW, validate_heart_rate(30));
    
    // 等价类3：正常（40-200）
    TEST_ASSERT_EQUAL(HR_VALID, validate_heart_rate(75));
    TEST_ASSERT_EQUAL(HR_VALID, validate_heart_rate(120));
    
    // 等价类4：过高（> 200）
    TEST_ASSERT_EQUAL(HR_TOO_HIGH, validate_heart_rate(250));
}
```

#### 边界值分析

测试边界值和边界附近的值。

```c
void test_heart_rate_boundaries(void) {
    // 下边界测试
    TEST_ASSERT_EQUAL(HR_INVALID, validate_heart_rate(-1));
    TEST_ASSERT_EQUAL(HR_TOO_LOW, validate_heart_rate(0));
    TEST_ASSERT_EQUAL(HR_TOO_LOW, validate_heart_rate(39));
    TEST_ASSERT_EQUAL(HR_VALID, validate_heart_rate(40));
    
    // 上边界测试
    TEST_ASSERT_EQUAL(HR_VALID, validate_heart_rate(200));
    TEST_ASSERT_EQUAL(HR_TOO_HIGH, validate_heart_rate(201));
}
```

#### 错误猜测法

基于经验预测可能的错误。

```c
void test_heart_rate_error_guessing(void) {
    // 特殊值测试
    TEST_ASSERT_EQUAL(HR_TOO_LOW, validate_heart_rate(0));
    
    // 极值测试
    TEST_ASSERT_EQUAL(HR_INVALID, validate_heart_rate(INT_MIN));
    TEST_ASSERT_EQUAL(HR_TOO_HIGH, validate_heart_rate(INT_MAX));
    
    // 典型错误值
    TEST_ASSERT_EQUAL(HR_INVALID, validate_heart_rate(-999));
}
```


### 代码覆盖率

代码覆盖率衡量测试执行了多少代码。

#### 覆盖率类型

**1. 语句覆盖率（Statement Coverage）**：
- 每条语句至少执行一次
- 最基本的覆盖率指标

**2. 分支覆盖率（Branch Coverage）**：
- 每个判断的真假分支都执行
- 比语句覆盖更严格

**3. 条件覆盖率（Condition Coverage）**：
- 每个条件的真假值都测试
- 适用于复杂条件

**4. 路径覆盖率（Path Coverage）**：
- 所有可能的执行路径都测试
- 最严格但可能不现实

#### 使用gcov进行覆盖率分析

**编译配置**：

```bash
# 编译时添加覆盖率标志
gcc -fprofile-arcs -ftest-coverage -o test_program test_program.c module.c

# 运行测试
./test_program

# 生成覆盖率报告
gcov module.c

# 查看覆盖率
cat module.c.gcov
```

**示例输出**：

```
        -:    0:Source:module.c
        -:    1:#include "module.h"
        -:    2:
        5:    3:int calculate_bmi(float weight, float height) {
        5:    4:    if (height <= 0 || weight <= 0) {
        2:    5:        return -1;  // 错误
        -:    6:    }
        3:    7:    float bmi = weight / (height * height);
        3:    8:    return (int)bmi;
        -:    9:}
```

**代码说明**：
- 第一列数字：该行执行次数
- `-`：不可执行行（注释、声明）
- `#####`：未执行的行

#### 覆盖率目标

**IEC 62304要求**：

| 软件安全分类 | 最低覆盖率要求 |
|------------|--------------|
| Class A    | 无明确要求    |
| Class B    | 语句覆盖 100% |
| Class C    | 分支覆盖 100% |

**实践建议**：
```
✓ 关键功能：100% 分支覆盖
✓ 安全相关：100% 分支覆盖
✓ 一般功能：≥ 80% 语句覆盖
✓ 工具代码：≥ 70% 语句覆盖
```

**说明**: 这是不同类型代码的覆盖率目标。关键功能和安全相关代码要求100%分支覆盖，一般功能要求≥80%语句覆盖，工具代码要求≥70%语句覆盖，根据代码重要性设定不同标准。



### 测试驱动开发（TDD）

TDD是一种先写测试、后写代码的开发方法。

#### TDD循环

```
┌─────────────┐
│  编写测试    │
│  (Red)      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  编写代码    │
│  (Green)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  重构代码    │
│  (Refactor) │
└──────┬──────┘
       │
       └──────► 重复
```

**说明**: 这是测试驱动开发(TDD)的Red-Green-Refactor循环。先编写测试(Red-失败)，然后编写代码使测试通过(Green-成功)，最后重构代码(Refactor-优化)，循环往复，确保代码质量。


#### TDD示例：血氧饱和度计算

**步骤1：编写测试（Red）**

```c
#include "unity.h"
#include "spo2_calculator.h"

void test_calculate_spo2_normal_value(void) {
    // 正常血氧值测试
    float red_ac = 0.5;
    float red_dc = 2.0;
    float ir_ac = 0.8;
    float ir_dc = 2.5;
    
    int spo2 = calculate_spo2(red_ac, red_dc, ir_ac, ir_dc);
    
    TEST_ASSERT_INT_WITHIN(2, 98, spo2);  // 98±2%
}

void test_calculate_spo2_low_value(void) {
    // 低血氧值测试
    float red_ac = 1.2;
    float red_dc = 2.0;
    float ir_ac = 0.6;
    float ir_dc = 2.5;
    
    int spo2 = calculate_spo2(red_ac, red_dc, ir_ac, ir_dc);
    
    TEST_ASSERT_INT_WITHIN(2, 85, spo2);  // 85±2%
}

void test_calculate_spo2_invalid_input(void) {
    // 无效输入测试
    int spo2 = calculate_spo2(0, 0, 0, 0);
    
    TEST_ASSERT_EQUAL_INT(-1, spo2);  // 返回错误码
}
```

**步骤2：编写代码（Green）**

```c
// spo2_calculator.c
#include "spo2_calculator.h"
#include <math.h>

int calculate_spo2(float red_ac, float red_dc, 
                   float ir_ac, float ir_dc) {
    // 输入验证
    if (red_dc <= 0 || ir_dc <= 0) {
        return -1;  // 错误
    }
    
    // 计算R值
    float r = (red_ac / red_dc) / (ir_ac / ir_dc);
    
    // 使用经验公式计算SpO2
    // SpO2 = 110 - 25 * R
    float spo2 = 110.0 - 25.0 * r;
    
    // 限制范围
    if (spo2 < 0) spo2 = 0;
    if (spo2 > 100) spo2 = 100;
    
    return (int)spo2;
}
```

**步骤3：重构（Refactor）**

```c
// 重构后的代码
#include "spo2_calculator.h"
#include <math.h>

#define SPO2_MIN 0
#define SPO2_MAX 100
#define SPO2_COEFFICIENT_A 110.0
#define SPO2_COEFFICIENT_B 25.0

static float calculate_r_value(float red_ac, float red_dc,
                               float ir_ac, float ir_dc) {
    return (red_ac / red_dc) / (ir_ac / ir_dc);
}

static int clamp_spo2(float spo2) {
    if (spo2 < SPO2_MIN) return SPO2_MIN;
    if (spo2 > SPO2_MAX) return SPO2_MAX;
    return (int)spo2;
}

int calculate_spo2(float red_ac, float red_dc,
                   float ir_ac, float ir_dc) {
    // 输入验证
    if (red_dc <= 0 || ir_dc <= 0 || ir_ac <= 0) {
        return -1;
    }
    
    // 计算R值
    float r = calculate_r_value(red_ac, red_dc, ir_ac, ir_dc);
    
    // 计算SpO2
    float spo2 = SPO2_COEFFICIENT_A - SPO2_COEFFICIENT_B * r;
    
    // 限制范围
    return clamp_spo2(spo2);
}
```

**代码说明**：
- 重构提取了辅助函数
- 使用常量替代魔法数字
- 提高了代码可读性和可维护性
- 测试仍然通过


### 模拟对象（Mock）和桩（Stub）

在单元测试中，需要隔离被测单元，使用Mock和Stub替代依赖。

#### 桩（Stub）

桩提供预定义的返回值。

```c
// 原始函数（依赖外部硬件）
int adc_read_channel(int channel) {
    // 读取ADC硬件
    return read_hardware_adc(channel);
}

// 测试桩
int adc_read_channel_stub(int channel) {
    // 返回预定义的测试值
    if (channel == 0) {
        return 2048;  // 模拟中间值
    } else if (channel == 1) {
        return 4095;  // 模拟最大值
    }
    return 0;
}

// 使用桩进行测试
void test_sensor_reading_with_stub(void) {
    // 替换真实函数为桩
    adc_read_channel = adc_read_channel_stub;
    
    // 测试传感器读取
    float voltage = sensor_read_voltage(0);
    
    TEST_ASSERT_FLOAT_WITHIN(0.01, 1.65, voltage);  // 2048/4096 * 3.3V
}
```

#### 模拟对象（Mock）

Mock不仅提供返回值，还验证调用行为。

```c
// 使用CMock生成的Mock
#include "mock_uart.h"

void test_send_data_via_uart(void) {
    uint8_t data[] = {0x01, 0x02, 0x03};
    
    // 设置期望：uart_send应该被调用一次
    uart_send_ExpectWithArray(data, 3, 3);
    
    // 执行被测函数
    send_packet(data, 3);
    
    // CMock自动验证uart_send是否按预期被调用
}

void test_retry_on_uart_failure(void) {
    uint8_t data[] = {0xAA};
    
    // 第一次调用失败
    uart_send_ExpectAndReturn(data, 1, UART_ERROR);
    
    // 第二次调用成功
    uart_send_ExpectAndReturn(data, 1, UART_SUCCESS);
    
    // 执行被测函数（应该重试）
    int result = send_packet_with_retry(data, 1);
    
    TEST_ASSERT_EQUAL_INT(UART_SUCCESS, result);
}
```

#### 依赖注入

通过依赖注入使代码更易测试。

```c
// 不易测试的代码
void process_sensor_data(void) {
    int raw_value = adc_read_channel(0);  // 硬编码依赖
    float voltage = raw_value * 3.3 / 4096.0;
    // 处理数据...
}

// 易测试的代码（依赖注入）
typedef int (*adc_read_func_t)(int channel);

void process_sensor_data_injectable(adc_read_func_t adc_read) {
    int raw_value = adc_read(0);  // 使用注入的函数
    float voltage = raw_value * 3.3 / 4096.0;
    // 处理数据...
}

// 测试
int test_adc_read(int channel) {
    return 2048;  // 测试值
}

void test_process_sensor_data(void) {
    // 注入测试函数
    process_sensor_data_injectable(test_adc_read);
    
    // 验证结果...
}
```


### 医疗器械软件单元测试最佳实践

#### 1. 遵循IEC 62304要求

```c
// 为每个软件单元编写测试
// Class B/C软件：确保100%语句/分支覆盖

// 测试文档化
/**
 * @test_id: UT_TEMP_001
 * @requirement: REQ_TEMP_001
 * @description: 验证温度传感器读取功能
 * @safety_class: B
 */
void test_temperature_sensor_read(void) {
    float temp = temperature_sensor_read();
    TEST_ASSERT_FLOAT_WITHIN(0.5, 36.5, temp);
}
```

#### 2. 测试命名规范

```c
// 好的命名：描述性强
void test_blood_pressure_measurement_returns_valid_range(void)
void test_alarm_triggers_when_heart_rate_exceeds_threshold(void)
void test_sensor_returns_error_on_hardware_fault(void)

// 不好的命名：不清晰
void test1(void)
void test_bp(void)
void test_function(void)
```

#### 3. 一个测试一个断言原则

```c
// 好的做法：每个测试关注一个方面
void test_heart_rate_upper_limit(void) {
    TEST_ASSERT_EQUAL(HR_TOO_HIGH, validate_heart_rate(201));
}

void test_heart_rate_lower_limit(void) {
    TEST_ASSERT_EQUAL(HR_TOO_LOW, validate_heart_rate(39));
}

// 不好的做法：一个测试多个断言
void test_heart_rate_all(void) {
    TEST_ASSERT_EQUAL(HR_TOO_HIGH, validate_heart_rate(201));
    TEST_ASSERT_EQUAL(HR_TOO_LOW, validate_heart_rate(39));
    TEST_ASSERT_EQUAL(HR_VALID, validate_heart_rate(75));
    // 如果第一个失败，后面的不会执行
}
```

#### 4. 测试独立性

```c
// 好的做法：每个测试独立
static int test_counter = 0;

void setUp(void) {
    test_counter = 0;  // 每次重置
    sensor_init();
}

void test_first(void) {
    test_counter++;
    TEST_ASSERT_EQUAL(1, test_counter);
}

void test_second(void) {
    test_counter++;
    TEST_ASSERT_EQUAL(1, test_counter);  // 仍然是1，因为setUp重置了
}
```

#### 5. 测试边界条件和错误情况

```c
void test_buffer_overflow_protection(void) {
    char buffer[10];
    
    // 测试边界
    int result = safe_copy(buffer, "123456789", 10);
    TEST_ASSERT_EQUAL(SUCCESS, result);
    
    // 测试溢出保护
    result = safe_copy(buffer, "12345678901", 10);
    TEST_ASSERT_EQUAL(BUFFER_OVERFLOW, result);
}

void test_null_pointer_handling(void) {
    // 测试NULL指针
    int result = process_data(NULL);
    TEST_ASSERT_EQUAL(ERROR_NULL_POINTER, result);
}

void test_division_by_zero(void) {
    // 测试除零
    float result = calculate_ratio(10.0, 0.0);
    TEST_ASSERT_EQUAL(ERROR_DIVISION_BY_ZERO, result);
}
```


#### 6. 持续集成中的单元测试

```bash
# Makefile示例
.PHONY: test coverage

# 编译测试
test:
	gcc -Wall -Wextra -o test_runner \
	    -fprofile-arcs -ftest-coverage \
	    test_*.c src/*.c -lunity
	./test_runner

# 生成覆盖率报告
coverage: test
	gcov src/*.c
	lcov --capture --directory . --output-file coverage.info
	genhtml coverage.info --output-directory coverage_html
	@echo "Coverage report generated in coverage_html/index.html"

# 清理
clean:
	rm -f *.gcda *.gcno *.gcov test_runner
	rm -rf coverage_html coverage.info
```

**CI配置示例（GitHub Actions）**：

```yaml
name: Unit Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y lcov
    
    - name: Run unit tests
      run: make test
    
    - name: Generate coverage report
      run: make coverage
    
    - name: Check coverage threshold
      run: |
        coverage=$(lcov --summary coverage.info | grep lines | awk '{print $2}' | sed 's/%//')
        if (( $(echo "$coverage < 80" | bc -l) )); then
          echo "Coverage $coverage% is below 80% threshold"
          exit 1
        fi
    
    - name: Upload coverage report
      uses: codecov/codecov-action@v2
      with:
        files: ./coverage.info
```

### 常见陷阱

!!! warning "注意事项"
    
    **1. 测试依赖外部状态**
    ```c
    // 错误：依赖文件系统
    void test_bad(void) {
        FILE* f = fopen("config.txt", "r");  // 依赖外部文件
        // ...
    }
    
    // 正确：使用Mock或内存数据
    void test_good(void) {
        const char* config = "setting=value";
        parse_config(config);
        // ...
    }
    ```
    
    **2. 测试顺序依赖**
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
    ```
    
    **3. 过度使用Mock**
    ```c
    // 错误：Mock了所有依赖，测试变得无意义
    void test_over_mocked(void) {
        mock_function1_return(10);
        mock_function2_return(20);
        mock_function3_return(30);
        
        int result = my_function();  // 只是调用Mock
        TEST_ASSERT_EQUAL(60, result);  // 没有测试真实逻辑
    }
    ```
    
    **4. 忽略错误路径**
    ```c
    // 错误：只测试正常路径
    void test_incomplete(void) {
        int result = divide(10, 2);
        TEST_ASSERT_EQUAL(5, result);
        // 没有测试除零情况
    }
    
    // 正确：测试错误路径
    void test_complete(void) {
        TEST_ASSERT_EQUAL(5, divide(10, 2));
        TEST_ASSERT_EQUAL(ERROR, divide(10, 0));  // 测试错误情况
    }
    ```
    
    **5. 测试实现而非行为**
    ```c
    // 错误：测试内部实现
    void test_implementation(void) {
        // 测试内部变量
        TEST_ASSERT_EQUAL(5, obj->internal_counter);
    }
    
    // 正确：测试外部行为
    void test_behavior(void) {
        // 测试公共接口
        TEST_ASSERT_EQUAL(EXPECTED_RESULT, obj->get_result());
    }
    ```


## 实践练习

1. **基础练习**：为一个简单的温度转换函数（摄氏度↔华氏度）编写完整的单元测试，包括边界值测试。

2. **中级练习**：使用TDD方法开发一个心率计算模块，要求：
   - 先编写测试用例
   - 实现功能代码
   - 重构优化
   - 达到100%分支覆盖率

3. **高级练习**：为一个包含硬件依赖的血压测量模块编写单元测试：
   - 使用Mock隔离硬件依赖
   - 测试正常测量流程
   - 测试错误处理（传感器故障、超时等）
   - 生成覆盖率报告

4. **综合练习**：建立一个完整的单元测试CI/CD流程：
   - 配置自动化测试
   - 集成覆盖率检查
   - 设置覆盖率阈值
   - 生成测试报告

## 相关资源

### 相关知识模块

- [集成测试](integration-testing.md) - 模块间接口测试
- [系统测试](system-testing.md) - 完整系统验证
- [代码审查检查清单](../coding-standards/code-review-checklist.md) - 代码质量保证

### 深入学习

- [测试策略概述](index.md) - 测试策略整体框架
- [静态分析](../static-analysis/index.md) - 静态代码分析工具

### 工具和框架

- [Unity测试框架](https://github.com/ThrowTheSwitch/Unity) - 轻量级C测试框架
- [CppUTest](https://cpputest.github.io/) - C/C++测试框架
- [Google Test](https://github.com/google/googletest) - Google C++测试框架
- [CMock](https://github.com/ThrowTheSwitch/CMock) - C语言Mock生成器
- [gcov/lcov](https://gcc.gnu.org/onlinedocs/gcc/Gcov.html) - 代码覆盖率工具

## 参考文献

1. IEC 62304:2006+AMD1:2015 - Medical device software - Software life cycle processes, Section 5.5 (Software Unit Implementation and Verification)
2. "Test Driven Development for Embedded C" by James W. Grenning
3. "Embedded Software Development for Safety-Critical Systems" by Chris Hobbs
4. FDA Guidance for the Content of Premarket Submissions for Software Contained in Medical Devices (2005)
5. "xUnit Test Patterns: Refactoring Test Code" by Gerard Meszaros


## 自测问题

??? question "问题1：什么是单元测试？它与集成测试有什么区别？"
    **问题**：解释单元测试的定义，并说明它与集成测试的主要区别。
    
    ??? success "答案"
        **单元测试定义**：
        单元测试是对软件中最小可测试单元（通常是函数或方法）进行独立验证的测试活动。
        
        **单元测试特点**：
        - 测试范围：单个函数或方法
        - 执行速度：快速（毫秒级）
        - 依赖隔离：使用Mock/Stub隔离外部依赖
        - 执行频率：每次代码修改后
        - 自动化程度：完全自动化
        
        **与集成测试的区别**：
        
        | 维度 | 单元测试 | 集成测试 |
        |------|---------|---------|
        | 测试范围 | 单个函数/模块 | 多个模块的接口 |
        | 依赖处理 | 隔离依赖（Mock） | 使用真实依赖 |
        | 执行速度 | 非常快 | 较慢 |
        | 缺陷定位 | 精确到函数 | 定位到模块间 |
        | 执行时机 | 开发阶段 | 集成阶段 |
        
        **示例对比**：
        ```c
        // 单元测试：测试单个函数
        void test_calculate_bmi(void) {
            float bmi = calculate_bmi(70.0, 1.75);
            TEST_ASSERT_FLOAT_WITHIN(0.1, 22.9, bmi);
        }
        
        // 集成测试：测试模块间交互
        void test_patient_data_flow(void) {
            // 测试从传感器读取 → 处理 → 存储的完整流程
            sensor_read();
            process_data();
            store_to_database();
            // 验证数据库中的数据
        }
        ```
        
        **知识点回顾**：单元测试关注单个单元的正确性，集成测试关注模块间的协作。

??? question "问题2：什么是代码覆盖率？IEC 62304对不同安全等级的覆盖率要求是什么？"
    **问题**：解释代码覆盖率的概念，并说明医疗器械软件的覆盖率要求。
    
    ??? success "答案"
        **代码覆盖率定义**：
        代码覆盖率是衡量测试执行了多少代码的指标，用百分比表示。
        
        **主要覆盖率类型**：
        
        **1. 语句覆盖率（Statement Coverage）**：
        ```c
        int abs_value(int x) {
            if (x < 0) {        // 语句1
                return -x;      // 语句2
            }
            return x;           // 语句3
        }
        
        // 测试用例1：abs_value(-5) → 覆盖语句1, 2
        // 测试用例2：abs_value(5)  → 覆盖语句1, 3
        // 语句覆盖率：100%
        ```
        
        **2. 分支覆盖率（Branch Coverage）**：
        ```c
        int classify(int x) {
            if (x < 0) {        // 分支1：真/假
                return -1;
            } else if (x > 0) { // 分支2：真/假
                return 1;
            }
            return 0;
        }
        
        // 需要测试所有分支的真假情况
        // 测试：-5, 5, 0 → 100%分支覆盖
        ```
        
        **IEC 62304覆盖率要求**：
        
        | 软件安全分类 | 最低覆盖率要求 | 说明 |
        |------------|--------------|------|
        | Class A | 无明确要求 | 建议≥70%语句覆盖 |
        | Class B | 100%语句覆盖 | 必须覆盖所有语句 |
        | Class C | 100%分支覆盖 | 必须覆盖所有分支 |
        
        **实践建议**：
        ```
        ✓ 安全关键代码：100%分支覆盖（无论分类）
        ✓ Class C软件：100%分支覆盖（强制）
        ✓ Class B软件：100%语句覆盖（强制）
        ✓ Class A软件：≥80%语句覆盖（建议）
        ```
        
        **覆盖率工具**：
        ```bash
        # 使用gcov生成覆盖率报告
        gcc -fprofile-arcs -ftest-coverage -o test test.c
        ./test
        gcov test.c
        # 查看test.c.gcov文件
        ```
        
        **重要提示**：
        - 高覆盖率不等于高质量测试
        - 覆盖率是必要条件，不是充分条件
        - 还需要测试边界值、错误情况等
        
        **知识点回顾**：覆盖率是测试完整性的重要指标，但不是唯一指标。

??? question "问题3：什么是测试驱动开发（TDD）？它的优势是什么？"
    **问题**：解释TDD的概念、工作流程和主要优势。
    
    ??? success "答案"
        **TDD定义**：
        测试驱动开发（Test-Driven Development）是一种先写测试、后写代码的开发方法。
        
        **TDD工作流程（Red-Green-Refactor）**：
        
        ```
        1. Red（红灯）：
           - 编写一个失败的测试
           - 测试描述期望的行为
           - 运行测试，确认失败
        
        2. Green（绿灯）：
           - 编写最少的代码使测试通过
           - 不关注代码质量，只求通过
           - 运行测试，确认通过
        
        3. Refactor（重构）：
           - 改进代码质量
           - 消除重复
           - 提高可读性
           - 运行测试，确保仍然通过
        
        4. 重复循环
        ```
        
        **TDD示例**：
        ```c
        // 步骤1：编写测试（Red）
        void test_is_valid_heart_rate(void) {
            TEST_ASSERT_TRUE(is_valid_heart_rate(75));
            TEST_ASSERT_FALSE(is_valid_heart_rate(300));
        }
        // 运行：失败（函数不存在）
        
        // 步骤2：编写代码（Green）
        bool is_valid_heart_rate(int hr) {
            return hr >= 40 && hr <= 200;
        }
        // 运行：通过
        
        // 步骤3：重构（Refactor）
        #define HR_MIN 40
        #define HR_MAX 200
        
        bool is_valid_heart_rate(int hr) {
            return hr >= HR_MIN && hr <= HR_MAX;
        }
        // 运行：仍然通过
        ```
        
        **TDD的优势**：
        
        **1. 更少的缺陷**：
        - 在编写代码前就考虑测试
        - 及早发现设计问题
        - 减少返工成本
        
        **2. 更好的设计**：
        - 强制模块化设计
        - 降低耦合度
        - 提高可测试性
        
        **3. 更高的信心**：
        - 完整的测试覆盖
        - 安全重构
        - 快速反馈
        
        **4. 活文档**：
        - 测试即文档
        - 展示使用方法
        - 始终保持更新
        
        **5. 更快的开发**：
        - 减少调试时间
        - 减少集成问题
        - 提高开发效率
        
        **TDD在医疗器械中的应用**：
        ```c
        // 先写测试定义安全需求
        void test_alarm_triggers_on_critical_value(void) {
            set_heart_rate(250);  // 危险值
            TEST_ASSERT_TRUE(is_alarm_triggered());
        }
        
        // 然后实现功能
        bool is_alarm_triggered(void) {
            int hr = get_heart_rate();
            return hr > CRITICAL_HR_THRESHOLD;
        }
        ```
        
        **常见误解**：
        - ❌ TDD会降低开发速度
        - ✅ TDD初期慢，长期更快
        - ❌ TDD只适合简单项目
        - ✅ TDD特别适合复杂、安全关键项目
        
        **知识点回顾**：TDD通过先写测试来驱动设计，提高代码质量和可维护性。

??? question "问题4：什么是Mock和Stub？它们有什么区别？"
    **问题**：解释Mock和Stub的概念，并说明它们的区别和使用场景。
    
    ??? success "答案"
        **基本概念**：
        Mock和Stub都是测试替身（Test Double），用于在单元测试中隔离依赖。
        
        **Stub（桩）**：
        
        **定义**：提供预定义返回值的简单替代品。
        
        **特点**：
        - 只返回固定值
        - 不验证调用行为
        - 实现简单
        
        **示例**：
        ```c
        // 真实函数（依赖硬件）
        int read_adc(int channel) {
            return hardware_adc_read(channel);
        }
        
        // Stub实现
        int read_adc_stub(int channel) {
            // 返回预定义的测试值
            if (channel == 0) return 2048;
            if (channel == 1) return 4095;
            return 0;
        }
        
        // 使用Stub测试
        void test_voltage_calculation(void) {
            // 使用Stub替代真实ADC
            int raw = read_adc_stub(0);
            float voltage = raw * 3.3 / 4096.0;
            TEST_ASSERT_FLOAT_WITHIN(0.01, 1.65, voltage);
        }
        ```
        
        **Mock（模拟对象）**：
        
        **定义**：不仅提供返回值，还验证调用行为的智能替代品。
        
        **特点**：
        - 验证函数是否被调用
        - 验证调用次数
        - 验证调用参数
        - 可以设置期望
        
        **示例**：
        ```c
        // 使用CMock生成的Mock
        #include "mock_uart.h"
        
        void test_send_command(void) {
            uint8_t cmd[] = {0x01, 0x02};
            
            // 设置期望：uart_send应该被调用一次，参数为cmd
            uart_send_ExpectWithArray(cmd, 2, 2);
            uart_send_IgnoreAndReturn(SUCCESS);
            
            // 执行被测函数
            send_command(cmd, 2);
            
            // Mock自动验证期望是否满足
        }
        
        void test_retry_mechanism(void) {
            uint8_t data[] = {0xAA};
            
            // 期望：第一次失败，第二次成功
            uart_send_ExpectAndReturn(data, 1, ERROR);
            uart_send_ExpectAndReturn(data, 1, SUCCESS);
            
            // 执行（应该重试）
            int result = send_with_retry(data, 1);
            
            TEST_ASSERT_EQUAL(SUCCESS, result);
            // Mock验证uart_send被调用了2次
        }
        ```
        
        **Mock vs Stub对比**：
        
        | 特性 | Stub | Mock |
        |------|------|------|
        | 返回值 | ✓ 提供 | ✓ 提供 |
        | 验证调用 | ✗ 不验证 | ✓ 验证 |
        | 验证参数 | ✗ 不验证 | ✓ 验证 |
        | 验证次数 | ✗ 不验证 | ✓ 验证 |
        | 实现复杂度 | 简单 | 复杂 |
        | 使用场景 | 提供数据 | 验证交互 |
        
        **使用场景**：
        
        **使用Stub**：
        ```c
        // 场景：需要特定输入数据
        void test_data_processing(void) {
            // Stub提供测试数据
            sensor_data_t data = sensor_read_stub();
            process_data(data);
            // 验证处理结果
        }
        ```
        
        **使用Mock**：
        ```c
        // 场景：需要验证函数调用
        void test_logging_behavior(void) {
            // Mock验证log_error被调用
            log_error_Expect("Sensor fault");
            
            handle_sensor_fault();
            
            // Mock自动验证log_error是否被正确调用
        }
        ```
        
        **选择建议**：
        - 只需要返回值 → 使用Stub
        - 需要验证交互 → 使用Mock
        - 简单场景 → 使用Stub
        - 复杂交互 → 使用Mock
        
        **注意事项**：
        - 不要过度使用Mock
        - Mock过多可能导致测试脆弱
        - 优先测试行为而非实现
        
        **知识点回顾**：Stub提供数据，Mock验证行为，根据需求选择合适的测试替身。

??? question "问题5：如何为医疗器械软件编写高质量的单元测试？"
    **问题**：列举医疗器械软件单元测试的最佳实践和注意事项。
    
    ??? success "答案"
        **医疗器械软件单元测试最佳实践**：
        
        **1. 遵循IEC 62304要求**：
        ```c
        /**
         * @test_id: UT_BP_001
         * @requirement: REQ_BP_001
         * @description: 验证血压测量范围
         * @safety_class: C
         * @coverage: 分支覆盖100%
         */
        void test_blood_pressure_range_validation(void) {
            // 正常范围
            TEST_ASSERT_TRUE(is_valid_bp(120, 80));
            
            // 边界值
            TEST_ASSERT_TRUE(is_valid_bp(90, 60));
            TEST_ASSERT_TRUE(is_valid_bp(140, 90));
            
            // 异常值
            TEST_ASSERT_FALSE(is_valid_bp(50, 30));
            TEST_ASSERT_FALSE(is_valid_bp(200, 120));
        }
        ```
        
        **2. 测试可追溯性**：
        ```
        需求 → 设计 → 代码 → 测试
        
        REQ_ALARM_001: 心率超过阈值时触发报警
        ↓
        DESIGN_ALARM_001: alarm_check()函数实现
        ↓
        CODE: alarm.c中的alarm_check()
        ↓
        TEST: test_alarm_triggers_on_high_heart_rate()
        ```
        
        **3. 全面的测试覆盖**：
        ```c
        // 正常路径
        void test_normal_operation(void) {
            int result = process_data(valid_data);
            TEST_ASSERT_EQUAL(SUCCESS, result);
        }
        
        // 边界条件
        void test_boundary_conditions(void) {
            TEST_ASSERT_EQUAL(SUCCESS, process_data(min_valid));
            TEST_ASSERT_EQUAL(SUCCESS, process_data(max_valid));
            TEST_ASSERT_EQUAL(ERROR, process_data(below_min));
            TEST_ASSERT_EQUAL(ERROR, process_data(above_max));
        }
        
        // 错误处理
        void test_error_handling(void) {
            TEST_ASSERT_EQUAL(ERROR_NULL, process_data(NULL));
            TEST_ASSERT_EQUAL(ERROR_INVALID, process_data(invalid_data));
        }
        
        // 安全关键路径
        void test_safety_critical_path(void) {
            // 测试所有可能导致危险的情况
            simulate_sensor_fault();
            TEST_ASSERT_TRUE(is_safe_state());
        }
        ```
        
        **4. 测试独立性和可重复性**：
        ```c
        // 每个测试独立
        void setUp(void) {
            // 初始化到已知状态
            system_reset();
            clear_all_flags();
            init_test_environment();
        }
        
        void tearDown(void) {
            // 清理资源
            cleanup_test_environment();
        }
        
        void test_independent_1(void) {
            // 不依赖其他测试
            // 可以单独运行
        }
        ```
        
        **5. 清晰的测试命名**：
        ```c
        // 好的命名
        void test_alarm_triggers_when_heart_rate_exceeds_200_bpm(void)
        void test_sensor_returns_error_on_hardware_fault(void)
        void test_data_validation_rejects_negative_values(void)
        
        // 不好的命名
        void test1(void)
        void test_function(void)
        void test_alarm(void)
        ```
        
        **6. 使用断言验证结果**：
        ```c
        void test_calculation_accuracy(void) {
            float result = calculate_bmi(70.0, 1.75);
            
            // 使用合适的断言
            TEST_ASSERT_FLOAT_WITHIN(0.1, 22.9, result);
            
            // 不要使用
            // if (result != 22.9) { /* fail */ }  // 错误！
        }
        ```
        
        **7. 文档化测试**：
        ```c
        /**
         * 测试目的：验证温度传感器在正常范围内的读取
         * 前置条件：传感器已初始化
         * 测试步骤：
         *   1. 读取温度值
         *   2. 验证值在35-40°C范围内
         * 预期结果：温度值有效且在范围内
         * 需求追溯：REQ_TEMP_001
         */
        void test_temperature_sensor_normal_range(void) {
            float temp = read_temperature();
            TEST_ASSERT_TRUE(temp >= 35.0 && temp <= 40.0);
        }
        ```
        
        **8. 持续集成**：
        ```bash
        # 每次提交自动运行测试
        git commit → CI触发 → 编译 → 运行测试 → 检查覆盖率
        
        # 覆盖率门槛
        if coverage < 80%:
            构建失败
        ```
        
        **9. 定期审查测试**：
        ```
        ✓ 测试是否仍然有效？
        ✓ 测试是否覆盖新需求？
        ✓ 测试是否需要更新？
        ✓ 是否有冗余测试？
        ```
        
        **10. 性能考虑**：
        ```c
        // 单元测试应该快速
        void test_fast(void) {
            // 避免：
            // - 文件I/O
            // - 网络访问
            // - 长时间延迟
            // - 复杂计算
            
            // 使用：
            // - 内存数据
            // - Mock/Stub
            // - 简单验证
        }
        ```
        
        **检查清单**：
        ```
        ☐ 测试可追溯到需求
        ☐ 达到要求的覆盖率
        ☐ 测试独立且可重复
        ☐ 测试命名清晰
        ☐ 包含边界值测试
        ☐ 包含错误处理测试
        ☐ 测试执行快速
        ☐ 测试文档完整
        ☐ 集成到CI/CD
        ☐ 定期审查更新
        ```
        
        **知识点回顾**：高质量的单元测试需要遵循标准、全面覆盖、独立可重复、文档完整。
