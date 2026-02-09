---
title: 中断处理
description: RTOS中的中断处理机制，包括ISR编写、中断优先级和中断嵌套
difficulty: 中级
estimated_time: 2.5小时
tags:
- RTOS
- 中断
- ISR
- 中断优先级
- 实时系统
related_modules:
- zh/technical-knowledge/rtos/task-scheduling
- zh/technical-knowledge/rtos/synchronization
last_updated: '2026-02-09'
version: '1.0'
language: zh-CN
---

# 中断处理

## 学习目标

完成本模块后，你将能够：
- 理解RTOS中断处理的基本原理
- 正确编写中断服务程序（ISR）
- 配置和管理中断优先级
- 处理中断嵌套和临界区
- 实现中断与任务的安全通信
- 避免常见的中断处理陷阱

## 前置知识

- C语言基础
- ARM Cortex-M架构基础（或其他目标架构）
- RTOS任务调度基础
- 同步机制（信号量、队列）

## 内容

### 中断基础

**中断**是硬件或软件事件，它会暂停当前执行的代码，转而执行中断服务程序（ISR）。

**中断处理流程**：

```
正常执行 → 中断发生 → 保存上下文 → 执行ISR → 恢复上下文 → 继续执行
```

**RTOS中的中断特点**：
- ISR必须尽可能短
- ISR中不能调用阻塞函数
- ISR中必须使用FromISR版本的API
- ISR可能需要触发任务切换

### 编写中断服务程序

**基本ISR结构**：

```c
#include "FreeRTOS.h"
#include "task.h"
#include "queue.h"

// 外部队列
extern QueueHandle_t xDataQueue;

// UART接收中断
void UART1_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    uint8_t received_data;
    
    // 1. 检查中断源
    if (UART1->SR & UART_SR_RXNE) {
        // 2. 读取数据（清除中断标志）
        received_data = UART1->DR;
        
        // 3. 发送到队列
        xQueueSendFromISR(xDataQueue, &received_data, &xHigherPriorityTaskWoken);
        
        // 4. 如果需要，触发任务切换
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}
```

**ISR编写规则**：

1. **保持ISR简短**
2. **不要调用阻塞函数**
3. **使用FromISR版本的API**
4. **正确处理xHigherPriorityTaskWoken**
5. **及时清除中断标志**

**完整示例：ADC中断处理**：

```c
#include "FreeRTOS.h"
#include "semphr.h"

#define ADC_BUFFER_SIZE 100

volatile uint16_t adc_buffer[ADC_BUFFER_SIZE];
volatile uint32_t adc_index = 0;
SemaphoreHandle_t xADCCompleteSemaphore;

// ADC转换完成中断
void ADC_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 读取ADC值
    adc_buffer[adc_index++] = ADC1->DR;
    
    // 缓冲区满？
    if (adc_index >= ADC_BUFFER_SIZE) {
        adc_index = 0;
        
        // 通知处理任务
        xSemaphoreGiveFromISR(xADCCompleteSemaphore, &xHigherPriorityTaskWoken);
    }
    
    // 触发任务切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// ADC处理任务
void adc_processing_task(void *param) {
    while (1) {
        // 等待ADC缓冲区满
        xSemaphoreTake(xADCCompleteSemaphore, portMAX_DELAY);
        
        // 处理ADC数据（在任务上下文中）
        process_adc_data(adc_buffer, ADC_BUFFER_SIZE);
    }
}
```

### 中断优先级

**ARM Cortex-M中断优先级**：

```c
// NVIC优先级配置
#define PRIORITY_HIGHEST    0
#define PRIORITY_HIGH       1
#define PRIORITY_MEDIUM     2
#define PRIORITY_LOW        3

// 配置中断优先级
void configure_interrupt_priorities(void) {
    // 设置优先级分组（4位抢占优先级，0位子优先级）
    NVIC_SetPriorityGrouping(0);
    
    // 关键中断：最高优先级
    NVIC_SetPriority(TIM1_IRQn, PRIORITY_HIGHEST);
    
    // UART中断：高优先级
    NVIC_SetPriority(USART1_IRQn, PRIORITY_HIGH);
    
    // ADC中断：中等优先级
    NVIC_SetPriority(ADC_IRQn, PRIORITY_MEDIUM);
    
    // 使能中断
    NVIC_EnableIRQ(TIM1_IRQn);
    NVIC_EnableIRQ(USART1_IRQn);
    NVIC_EnableIRQ(ADC_IRQn);
}
```

**FreeRTOS中断优先级配置**：

```c
// FreeRTOSConfig.h

// 最低的中断优先级（数值最大）
#define configLIBRARY_LOWEST_INTERRUPT_PRIORITY         15

// 内核使用的最高优先级
#define configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY    5

// 优先级高于此值的中断不能调用FreeRTOS API
// 优先级0-4：不能调用FreeRTOS API（超高优先级，零延迟）
// 优先级5-15：可以调用FreeRTOS API

// 配置示例
void setup_interrupts(void) {
    // 紧急中断：优先级2（不能调用FreeRTOS API）
    NVIC_SetPriority(EMERGENCY_IRQn, 2);
    
    // 普通中断：优先级6（可以调用FreeRTOS API）
    NVIC_SetPriority(UART_IRQn, 6);
    
    // 低优先级中断：优先级10
    NVIC_SetPriority(TIMER_IRQn, 10);
}
```

### 中断嵌套

**中断嵌套**：高优先级中断可以打断低优先级中断。

```c
// 低优先级中断
void LOW_PRIORITY_IRQHandler(void) {
    // 开始执行
    process_low_priority_event();
    
    // 可能被高优先级中断打断
    
    // 继续执行
    finish_low_priority_processing();
}

// 高优先级中断
void HIGH_PRIORITY_IRQHandler(void) {
    // 可以打断低优先级中断
    handle_critical_event();
}
```

**嵌套深度控制**：

```c
// FreeRTOSConfig.h
#define configMAX_SYSCALL_INTERRUPT_PRIORITY    5

// 只有优先级数值 >= 5 的中断可以嵌套调用FreeRTOS API
```

### 临界区保护

**临界区**：不能被中断打断的代码段。

**方法1：禁用所有中断**：

```c
// 禁用所有中断
void critical_operation(void) {
    __disable_irq();  // 或 taskDISABLE_INTERRUPTS()
    
    // 临界区代码
    shared_variable++;
    
    __enable_irq();   // 或 taskENABLE_INTERRUPTS()
}
```

**方法2：禁用可屏蔽中断（推荐）**：

```c
void safe_critical_operation(void) {
    // 进入临界区（只禁用优先级低于configMAX_SYSCALL_INTERRUPT_PRIORITY的中断）
    taskENTER_CRITICAL();
    
    // 临界区代码
    shared_variable++;
    
    // 退出临界区
    taskEXIT_CRITICAL();
}
```

**方法3：从ISR进入临界区**：

```c
void ISR_Handler(void) {
    UBaseType_t uxSavedInterruptStatus;
    
    // 保存中断状态并进入临界区
    uxSavedInterruptStatus = taskENTER_CRITICAL_FROM_ISR();
    
    // 临界区代码
    shared_variable++;
    
    // 恢复中断状态
    taskEXIT_CRITICAL_FROM_ISR(uxSavedInterruptStatus);
}
```

### 中断与任务通信

**方法1：使用信号量**：

```c
SemaphoreHandle_t xBinarySemaphore;

void init_semaphore(void) {
    xBinarySemaphore = xSemaphoreCreateBinary();
}

// 中断通知任务
void BUTTON_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 清除中断标志
    clear_button_interrupt();
    
    // 释放信号量
    xSemaphoreGiveFromISR(xBinarySemaphore, &xHigherPriorityTaskWoken);
    
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 任务等待中断
void button_task(void *param) {
    while (1) {
        // 等待按钮中断
        if (xSemaphoreTake(xBinarySemaphore, portMAX_DELAY) == pdTRUE) {
            // 处理按钮事件
            handle_button_press();
        }
    }
}
```

**方法2：使用队列传递数据**：

```c
typedef struct {
    uint32_t timestamp;
    uint16_t value;
    uint8_t channel;
} adc_sample_t;

QueueHandle_t xADCQueue;

void init_adc_queue(void) {
    xADCQueue = xQueueCreate(10, sizeof(adc_sample_t));
}

// 中断发送数据
void ADC_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    adc_sample_t sample;
    
    // 读取ADC数据
    sample.timestamp = get_timestamp();
    sample.value = ADC1->DR;
    sample.channel = get_current_channel();
    
    // 发送到队列
    xQueueSendFromISR(xADCQueue, &sample, &xHigherPriorityTaskWoken);
    
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 任务接收数据
void adc_task(void *param) {
    adc_sample_t sample;
    
    while (1) {
        if (xQueueReceive(xADCQueue, &sample, portMAX_DELAY) == pdTRUE) {
            // 处理ADC样本
            process_adc_sample(&sample);
        }
    }
}
```

**方法3：使用任务通知**：

```c
TaskHandle_t xProcessingTaskHandle;

// 中断通知任务
void TIMER_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 清除中断标志
    TIM1->SR &= ~TIM_SR_UIF;
    
    // 通知任务
    vTaskNotifyGiveFromISR(xProcessingTaskHandle, &xHigherPriorityTaskWoken);
    
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 任务等待通知
void processing_task(void *param) {
    while (1) {
        // 等待定时器中断通知
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        
        // 执行周期性处理
        periodic_processing();
    }
}
```

### 延迟中断处理

**问题**：ISR中不能执行耗时操作。

**解决方案**：延迟中断处理（Deferred Interrupt Handling）。

```c
// 高优先级任务处理中断
TaskHandle_t xDeferredTaskHandle;
QueueHandle_t xDeferredQueue;

typedef struct {
    uint8_t interrupt_source;
    uint32_t data;
} deferred_work_t;

// 中断：快速记录并通知
void COMPLEX_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    deferred_work_t work;
    
    // 最小化ISR工作
    work.interrupt_source = get_interrupt_source();
    work.data = read_minimal_data();
    
    // 发送到延迟处理队列
    xQueueSendFromISR(xDeferredQueue, &work, &xHigherPriorityTaskWoken);
    
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 高优先级延迟处理任务
void deferred_interrupt_task(void *param) {
    deferred_work_t work;
    
    while (1) {
        // 等待工作
        if (xQueueReceive(xDeferredQueue, &work, portMAX_DELAY) == pdTRUE) {
            // 在任务上下文中执行复杂处理
            switch (work.interrupt_source) {
                case SOURCE_UART:
                    process_uart_data(work.data);
                    break;
                case SOURCE_SPI:
                    process_spi_data(work.data);
                    break;
                default:
                    break;
            }
        }
    }
}

void init_deferred_handling(void) {
    xDeferredQueue = xQueueCreate(10, sizeof(deferred_work_t));
    
    // 创建高优先级任务
    xTaskCreate(deferred_interrupt_task,
               "DeferredISR",
               256,
               NULL,
               configMAX_PRIORITIES - 1,  // 最高优先级
               &xDeferredTaskHandle);
}
```

## 最佳实践

### 1. 保持ISR简短

!!! tip "ISR设计原则"
    ISR应该只做必要的工作，复杂处理交给任务。

```c
// ❌ 不好：ISR中执行复杂处理
void BAD_IRQHandler(void) {
    uint8_t data = read_data();
    
    // 复杂处理（不应该在ISR中）
    float result = complex_calculation(data);
    update_display(result);
    log_to_file(result);
}

// ✅ 好：ISR只读取数据并通知
void GOOD_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    uint8_t data = read_data();
    
    // 快速发送到队列
    xQueueSendFromISR(xQueue, &data, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### 2. 正确使用FromISR API

```c
// ISR中必须使用FromISR版本
void ISR_Handler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // ✅ 正确
    xSemaphoreGiveFromISR(xSemaphore, &xHigherPriorityTaskWoken);
    xQueueSendFromISR(xQueue, &data, &xHigherPriorityTaskWoken);
    vTaskNotifyGiveFromISR(xTask, &xHigherPriorityTaskWoken);
    
    // ❌ 错误：不要在ISR中使用普通API
    // xSemaphoreGive(xSemaphore);
    // xQueueSend(xQueue, &data, 0);
    
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### 3. 合理设置中断优先级

```c
// 医疗设备中断优先级示例
void configure_medical_device_interrupts(void) {
    // 安全关键：最高优先级（不调用RTOS API）
    NVIC_SetPriority(SAFETY_MONITOR_IRQn, 0);
    
    // 实时采样：高优先级
    NVIC_SetPriority(ECG_ADC_IRQn, 5);
    
    // 通信：中等优先级
    NVIC_SetPriority(UART_IRQn, 8);
    
    // 用户界面：低优先级
    NVIC_SetPriority(BUTTON_IRQn, 12);
}
```

### 4. 避免在ISR中使用浮点运算

```c
// ❌ 不好：ISR中使用浮点
void BAD_ADC_IRQHandler(void) {
    float voltage = (float)ADC1->DR * 3.3f / 4096.0f;
    // 浮点运算可能触发上下文保存
}

// ✅ 好：在任务中进行浮点运算
void GOOD_ADC_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    uint16_t raw_value = ADC1->DR;
    
    xQueueSendFromISR(xADCQueue, &raw_value, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

void adc_task(void *param) {
    uint16_t raw_value;
    while (1) {
        if (xQueueReceive(xADCQueue, &raw_value, portMAX_DELAY) == pdTRUE) {
            // 在任务中进行浮点运算
            float voltage = (float)raw_value * 3.3f / 4096.0f;
            process_voltage(voltage);
        }
    }
}
```

### 5. 使用中断计数器监控

```c
// 中断统计
typedef struct {
    uint32_t count;
    uint32_t max_duration;
    uint32_t total_duration;
} interrupt_stats_t;

volatile interrupt_stats_t uart_stats = {0};

void UART_IRQHandler(void) {
    uint32_t start_time = get_cycle_count();
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 处理中断
    uint8_t data = UART1->DR;
    xQueueSendFromISR(xQueue, &data, &xHigherPriorityTaskWoken);
    
    // 更新统计
    uint32_t duration = get_cycle_count() - start_time;
    uart_stats.count++;
    uart_stats.total_duration += duration;
    if (duration > uart_stats.max_duration) {
        uart_stats.max_duration = duration;
    }
    
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 监控任务
void monitor_task(void *param) {
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
        
        printf("UART IRQ: count=%lu, max=%lu cycles, avg=%lu cycles\n",
               uart_stats.count,
               uart_stats.max_duration,
               uart_stats.total_duration / uart_stats.count);
    }
}
```

## 常见陷阱

### 1. 忘记清除中断标志

```c
// ❌ 错误：忘记清除标志，导致中断重复触发
void BAD_IRQHandler(void) {
    uint8_t data = UART1->DR;
    process_data(data);
    // 忘记清除中断标志！
}

// ✅ 正确：及时清除中断标志
void GOOD_IRQHandler(void) {
    // 读取数据通常会自动清除标志
    uint8_t data = UART1->DR;
    
    // 或显式清除
    UART1->SR &= ~UART_SR_RXNE;
    
    process_data(data);
}
```

### 2. ISR中调用阻塞函数

```c
// ❌ 错误：ISR中调用阻塞函数
void BAD_IRQHandler(void) {
    xSemaphoreTake(xMutex, portMAX_DELAY);  // 阻塞！
    shared_data++;
    xSemaphoreGive(xMutex);
}

// ✅ 正确：使用临界区或原子操作
void GOOD_IRQHandler(void) {
    UBaseType_t uxSavedInterruptStatus;
    uxSavedInterruptStatus = taskENTER_CRITICAL_FROM_ISR();
    
    shared_data++;
    
    taskEXIT_CRITICAL_FROM_ISR(uxSavedInterruptStatus);
}
```

### 3. 忘记portYIELD_FROM_ISR

```c
// ❌ 错误：忘记触发任务切换
void BAD_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(xSemaphore, &xHigherPriorityTaskWoken);
    // 忘记调用portYIELD_FROM_ISR！
}

// ✅ 正确：总是检查并触发任务切换
void GOOD_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(xSemaphore, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

### 4. 中断优先级配置错误

```c
// ❌ 错误：高优先级中断调用RTOS API
void configure_wrong(void) {
    // 优先级2 < configMAX_SYSCALL_INTERRUPT_PRIORITY (5)
    NVIC_SetPriority(UART_IRQn, 2);
}

void UART_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    // 错误！此优先级不能调用RTOS API
    xQueueSendFromISR(xQueue, &data, &xHigherPriorityTaskWoken);
}

// ✅ 正确：确保优先级允许调用RTOS API
void configure_correct(void) {
    // 优先级6 >= configMAX_SYSCALL_INTERRUPT_PRIORITY (5)
    NVIC_SetPriority(UART_IRQn, 6);
}
```

### 5. 共享变量未使用volatile

```c
// ❌ 错误：编译器可能优化掉读取
uint32_t interrupt_flag = 0;

void ISR_Handler(void) {
    interrupt_flag = 1;
}

void task(void *param) {
    while (interrupt_flag == 0) {
        // 可能永远循环！
    }
}

// ✅ 正确：使用volatile
volatile uint32_t interrupt_flag = 0;

void ISR_Handler(void) {
    interrupt_flag = 1;
}

void task(void *param) {
    while (interrupt_flag == 0) {
        // 正确读取
    }
}
```

## 实践练习

1. **基本ISR**：编写一个UART接收中断，将数据发送到队列
2. **中断优先级**：配置多个中断的优先级，观察嵌套行为
3. **延迟处理**：实现一个延迟中断处理系统
4. **性能测试**：测量ISR执行时间，确保满足实时要求
5. **错误注入**：故意制造常见错误，学习调试方法

## 相关资源

### 相关知识模块

- [任务调度](task-scheduling.md) - RTOS任务调度和优先级管理
- [同步机制](synchronizationn.md) - 信号量、队列和事件组
- [资源管理](resource-management.md) - 内存管理和资源池

### 深入学习

- [RTOS概述](index.md) - RTOS基础知识和选型指南
- [嵌入式C/C++编程](../embedded-c-cpp/index.md) - C语言基础和嵌入式编程技巧

## 参考文献

1. "Mastering the FreeRTOS Real Time Kernel" - Richard Barry
2. "The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors" - Joseph Yiu
3. IEC 62304:2006+AMD1:2015 - Medical device software
4. "Embedded Systems Architecture" by Daniele Lacamera
5. ARM Cortex-M Programming Guide to Memory Barrier Instructions

## 自测问题

??? question "问题1：为什么ISR必须尽可能短？"
    **问题**：解释ISR应该保持简短的原因。
    
    ??? success "答案"
        **原因**：
        
        **1. 影响系统响应性**：
        - ISR执行期间，其他中断可能被阻塞
        - 长时间的ISR会延迟其他中断的响应
        
        **2. 影响任务调度**：
        - ISR执行期间，任务调度器无法运行
        - 高优先级任务可能无法及时响应
        
        **3. 增加中断延迟**：
        - 中断延迟 = 中断响应时间 + ISR执行时间
        - 长ISR导致不可预测的延迟
        
        **4. 可能导致数据丢失**：
        - 如果新中断在ISR执行期间到达
        - 可能丢失数据或事件
        
        **示例**：
        ```c
        // ❌ 不好：ISR太长
        void BAD_UART_IRQHandler(void) {
            uint8_t data = UART1->DR;
            
            // 复杂处理（100us）
            process_data(data);
            
            // 更新显示（1ms）
            update_display();
            
            // 写入Flash（10ms）
            write_to_flash(data);
        }
        
        // ✅ 好：ISR只读取数据
        void GOOD_UART_IRQHandler(void) {
            BaseType_t xHigherPriorityTaskWoken = pdFALSE;
            uint8_t data = UART1->DR;  // <1us
            
            xQueueSendFromISR(xQueue, &data, &xHigherPriorityTaskWoken);
            portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
        }
        ```
        
        **最佳实践**：
        - ISR只做必要的硬件操作
        - 复杂处理交给高优先级任务
        - 目标：ISR执行时间 < 10us

??? question "问题2：什么是中断优先级反转？"
    **问题**：解释中断优先级反转的概念和影响。
    
    ??? success "答案"
        **中断优先级反转**：
        低优先级中断的ISR执行时间过长，导致高优先级中断响应延迟。
        
        **场景**：
        ```
        时间线：
        低优先级ISR ────────────[执行中]────────────
        高优先级中断 ──────────────┐等待┌──────────
        ```
        
        **示例**：
        ```c
        // 低优先级中断（优先级10）
        void LOW_PRIORITY_IRQHandler(void) {
            // 长时间处理（1ms）
            for (int i = 0; i < 1000; i++) {
                process_data(i);
            }
        }
        
        // 高优先级中断（优先级5）
        void HIGH_PRIORITY_IRQHandler(void) {
            // 关键处理
            handle_critical_event();
        }
        
        // 如果低优先级ISR正在执行，
        // 高优先级中断必须等待低优先级ISR完成
        ```
        
        **影响**：
        - 高优先级中断响应延迟
        - 实时性能下降
        - 可能导致数据丢失
        
        **解决方案**：
        
        **1. 缩短所有ISR**：
        ```c
        void LOW_PRIORITY_IRQHandler(void) {
            BaseType_t xHigherPriorityTaskWoken = pdFALSE;
            
            // 只读取数据
            uint8_t data = read_data();
            
            // 发送到任务处理
            xQueueSendFromISR(xQueue, &data, &xHigherPriorityTaskWoken);
            portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
        }
        ```
        
        **2. 使用中断嵌套**：
        ```c
        // 允许高优先级中断打断低优先级ISR
        // ARM Cortex-M自动支持
        ```
        
        **3. 合理分配优先级**：
        ```c
        // 关键中断：最高优先级
        NVIC_SetPriority(CRITICAL_IRQn, 0);
        
        // 普通中断：中等优先级
        NVIC_SetPriority(NORMAL_IRQn, 5);
        
        // 低优先级中断：最低优先级
        NVIC_SetPriority(LOW_IRQn, 15);
        ```

??? question "问题3：FromISR API和普通API有什么区别？"
    **问题**：解释FromISR版本API的特殊之处。
    
    ??? success "答案"
        **主要区别**：
        
        **1. 上下文**：
        - 普通API：在任务上下文中调用
        - FromISR API：在中断上下文中调用
        
        **2. 阻塞行为**：
        - 普通API：可以阻塞等待
        - FromISR API：永不阻塞
        
        **3. 任务切换**：
        - 普通API：自动触发任务切换
        - FromISR API：需要手动调用portYIELD_FROM_ISR
        
        **4. 参数**：
        - 普通API：使用TickType_t超时参数
        - FromISR API：使用BaseType_t *pxHigherPriorityTaskWoken
        
        **对比示例**：
        ```c
        // 任务中使用普通API
        void task_function(void *param) {
            uint8_t data;
            
            // 可以阻塞等待
            if (xQueueReceive(xQueue, &data, pdMS_TO_TICKS(100)) == pdTRUE) {
                process_data(data);
            }
            // 自动触发任务切换（如果需要）
        }
        
        // ISR中使用FromISR API
        void ISR_Handler(void) {
            BaseType_t xHigherPriorityTaskWoken = pdFALSE;
            uint8_t data = read_hardware();
            
            // 不能阻塞，立即返回
            xQueueSendFromISR(xQueue, &data, &xHigherPriorityTaskWoken);
            
            // 手动触发任务切换
            portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
        }
        ```
        
        **常用API对比**：
        
        | 任务API | ISR API |
        |---------|---------|
        | xSemaphoreGive() | xSemaphoreGiveFromISR() |
        | xSemaphoreTake() | xSemaphoreTakeFromISR() |
        | xQueueSend() | xQueueSendFromISR() |
        | xQueueReceive() | xQueueReceiveFromISR() |
        | xTaskNotifyGive() | vTaskNotifyGiveFromISR() |
        | xEventGroupSetBits() | xEventGroupSetBitsFromISR() |
        
        **错误示例**：
        ```c
        // ❌ 错误：在ISR中使用普通API
        void BAD_IRQHandler(void) {
            xQueueSend(xQueue, &data, 0);  // 错误！
        }
        
        // ✅ 正确：使用FromISR版本
        void GOOD_IRQHandler(void) {
            BaseType_t xHigherPriorityTaskWoken = pdFALSE;
            xQueueSendFromISR(xQueue, &data, &xHigherPriorityTaskWoken);
            portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
        }
        ```

??? question "问题4：如何调试中断问题？"
    **问题**：介绍调试中断相关问题的方法和工具。
    
    ??? success "答案"
        **调试方法**：
        
        **1. 使用LED指示**：
        ```c
        void DEBUG_IRQHandler(void) {
            LED_ON();  // 进入ISR
            
            // 处理中断
            process_interrupt();
            
            LED_OFF();  // 退出ISR
        }
        ```
        
        **2. 使用GPIO切换**：
        ```c
        void DEBUG_IRQHandler(void) {
            DEBUG_PIN_HIGH();  // 用示波器测量
            
            process_interrupt();
            
            DEBUG_PIN_LOW();
        }
        ```
        
        **3. 中断计数器**：
        ```c
        volatile uint32_t irq_count = 0;
        volatile uint32_t irq_errors = 0;
        
        void IRQHandler(void) {
            irq_count++;
            
            if (error_condition()) {
                irq_errors++;
            }
            
            // 处理中断
        }
        
        // 监控任务
        void monitor_task(void *param) {
            while (1) {
                printf("IRQ: count=%lu, errors=%lu\n", 
                       irq_count, irq_errors);
                vTaskDelay(pdMS_TO_TICKS(1000));
            }
        }
        ```
        
        **4. 断言检查**：
        ```c
        void IRQHandler(void) {
            // 检查中断标志
            configASSERT(UART1->SR & UART_SR_RXNE);
            
            uint8_t data = UART1->DR;
            
            // 检查队列未满
            configASSERT(uxQueueSpacesAvailable(xQueue) > 0);
            
            xQueueSendFromISR(xQueue, &data, NULL);
        }
        ```
        
        **5. 使用调试器**：
        ```c
        // 设置断点
        void IRQHandler(void) {
            __BKPT(0);  // 触发断点
            
            // 或使用条件断点
            if (error_condition()) {
                __BKPT(1);
            }
        }
        ```
        
        **6. 记录中断历史**：
        ```c
        #define IRQ_LOG_SIZE 100
        
        typedef struct {
            uint32_t timestamp;
            uint8_t irq_number;
            uint32_t data;
        } irq_log_entry_t;
        
        volatile irq_log_entry_t irq_log[IRQ_LOG_SIZE];
        volatile uint32_t irq_log_index = 0;
        
        void IRQHandler(void) {
            // 记录中断
            irq_log[irq_log_index].timestamp = get_timestamp();
            irq_log[irq_log_index].irq_number = get_irq_number();
            irq_log[irq_log_index].data = read_data();
            
            irq_log_index = (irq_log_index + 1) % IRQ_LOG_SIZE;
            
            // 处理中断
        }
        ```
        
        **7. 使用RTOS跟踪工具**：
        ```c
        // FreeRTOS+Trace
        #include "trcRecorder.h"
        
        void IRQHandler(void) {
            traceISR_ENTER();
            
            // 处理中断
            
            traceISR_EXIT();
        }
        ```
        
        **常见问题排查**：
        
        | 问题 | 可能原因 | 排查方法 |
        |------|----------|----------|
        | 中断不触发 | 未使能中断 | 检查NVIC配置 |
        | 中断频繁触发 | 未清除标志 | 检查标志清除代码 |
        | 系统崩溃 | 栈溢出 | 增加栈大小 |
        | 数据丢失 | 队列满 | 增加队列大小或加快处理 |
        | 响应慢 | ISR太长 | 使用延迟处理 |

??? question "问题5：什么是中断延迟？如何测量？"
    **问题**：解释中断延迟的概念和测量方法。
    
    ??? success "答案"
        **中断延迟定义**：
        从中断请求发生到ISR开始执行的时间。
        
        **延迟组成**：
        ```
        总延迟 = 硬件延迟 + 软件延迟 + ISR执行时间
        
        硬件延迟：中断信号传播时间
        软件延迟：中断响应时间（保存上下文等）
        ISR执行时间：ISR代码执行时间
        ```
        
        **影响因素**：
        
        **1. 中断优先级**：
        - 低优先级中断可能被高优先级中断打断
        - 相同优先级中断不能嵌套
        
        **2. 临界区**：
        - 临界区期间中断被禁用
        - 延迟 = 最长临界区时间
        
        **3. 其他ISR**：
        - 如果其他ISR正在执行
        - 必须等待其完成
        
        **测量方法1：GPIO切换**：
        ```c
        // 硬件触发GPIO
        void hardware_trigger(void) {
            TRIGGER_PIN_HIGH();  // 触发中断
        }
        
        // ISR中切换GPIO
        void IRQHandler(void) {
            MEASURE_PIN_HIGH();  // 测量点
            
            // 处理中断
            process_interrupt();
            
            MEASURE_PIN_LOW();
        }
        
        // 使用示波器测量：
        // 延迟 = MEASURE_PIN上升沿 - TRIGGER_PIN上升沿
        // ISR时间 = MEASURE_PIN高电平持续时间
        ```
        
        **测量方法2：时间戳**：
        ```c
        volatile uint32_t interrupt_latency_us = 0;
        
        // 触发中断时记录时间
        void trigger_interrupt(void) {
            uint32_t trigger_time = get_microseconds();
            
            // 触发中断
            trigger_hardware_interrupt();
        }
        
        // ISR中计算延迟
        void IRQHandler(void) {
            uint32_t isr_start_time = get_microseconds();
            
            // 计算延迟
            interrupt_latency_us = isr_start_time - trigger_time;
            
            // 处理中断
        }
        ```
        
        **测量方法3：使用DWT（ARM Cortex-M）**：
        ```c
        // 初始化DWT
        void init_dwt(void) {
            CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
            DWT->CYCCNT = 0;
            DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
        }
        
        // 测量中断延迟
        volatile uint32_t irq_start_cycle = 0;
        volatile uint32_t irq_latency_cycles = 0;
        
        void trigger_interrupt(void) {
            irq_start_cycle = DWT->CYCCNT;
            trigger_hardware_interrupt();
        }
        
        void IRQHandler(void) {
            uint32_t isr_cycle = DWT->CYCCNT;
            irq_latency_cycles = isr_cycle - irq_start_cycle;
            
            // 处理中断
        }
        ```
        
        **典型延迟值（ARM Cortex-M4 @ 168MHz）**：
        - 硬件延迟：~12个时钟周期（~70ns）
        - 上下文保存：~12个时钟周期（~70ns）
        - 总延迟：~24个时钟周期（~140ns）
        
        **优化延迟**：
        ```c
        // 1. 提高中断优先级
        NVIC_SetPriority(CRITICAL_IRQn, 0);
        
        // 2. 缩短临界区
        taskENTER_CRITICAL();
        // 最小化临界区代码
        taskEXIT_CRITICAL();
        
        // 3. 缩短其他ISR
        void OTHER_IRQHandler(void) {
            // 保持简短
            quick_operation();
        }
        
        // 4. 使用中断嵌套
        // ARM Cortex-M自动支持
        ```
