---
title: 任务调度
description: RTOS中的任务调度机制，包括优先级调度、时间片轮转和调度策略
difficulty: 中级
estimated_time: 2.5小时
tags:
- RTOS
- 任务调度
- 优先级
- 实时系统
related_modules:
- zh/technical-knowledge/rtos/synchronization
- zh/technical-knowledge/rtos/interrupt-handling
last_updated: '2026-02-07'
version: '1.0'
language: zh-CN
---

# 任务调度

## 学习目标

完成本模块后，你将能够：
- 理解RTOS任务调度的基本原理
- 掌握优先级调度和时间片轮转机制
- 配置和管理任务优先级
- 识别和解决优先级反转问题
- 应用医疗器械软件中的任务调度最佳实践

## 前置知识

- C语言基础
- 基本的操作系统概念
- 中断和上下文切换的理解

## 内容

### RTOS任务调度基础

**任务（Task）**是RTOS中的基本执行单元，也称为线程（Thread）。调度器负责决定在任何给定时刻哪个任务应该运行。

**任务状态**：

```
┌─────────┐
│  就绪   │◄──────────┐
│ (Ready) │           │
└────┬────┘           │
     │                │
     │ 调度器选择      │ 抢占/时间片到期
     ▼                │
┌─────────┐           │
│  运行   │───────────┘
│(Running)│
└────┬────┘
     │
     │ 等待事件/延时
     ▼
┌─────────┐
│  阻塞   │
│(Blocked)│
└─────────┘
```

**任务状态转换**：
1. **就绪（Ready）**：任务准备运行，等待CPU
2. **运行（Running）**：任务正在CPU上执行
3. **阻塞（Blocked）**：任务等待事件或延时
4. **挂起（Suspended）**：任务被显式挂起（某些RTOS支持）

### 优先级调度

大多数RTOS使用基于优先级的抢占式调度。

**调度规则**：
- 高优先级任务总是优先于低优先级任务运行
- 当高优先级任务就绪时，立即抢占低优先级任务
- 相同优先级的任务通常采用时间片轮转

**FreeRTOS示例**：

```c
#include "FreeRTOS.h"
#include "task.h"

// 任务优先级定义
#define PRIORITY_HIGH       3
#define PRIORITY_MEDIUM     2
#define PRIORITY_LOW        1
#define PRIORITY_IDLE       0

// 高优先级任务 - 紧急数据处理
void vHighPriorityTask(void *pvParameters) {
    for (;;) {
        // 等待紧急事件
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        
        // 处理紧急数据
        process_urgent_data();
        
        // 任务完成，进入阻塞状态
    }
}

// 中优先级任务 - 周期性测量
void vMediumPriorityTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(100);  // 100ms周期
    
    for (;;) {
        // 周期性唤醒
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
        
        // 执行测量
        perform_measurement();
    }
}

// 低优先级任务 - 后台处理
void vLowPriorityTask(void *pvParameters) {
    for (;;) {
        // 后台数据处理
        process_background_data();
        
        // 让出CPU给其他任务
        taskYIELD();
    }
}

// 创建任务
void create_tasks(void) {
    xTaskCreate(
        vHighPriorityTask,      // 任务函数
        "HighPrio",             // 任务名称
        configMINIMAL_STACK_SIZE,  // 栈大小
        NULL,                   // 参数
        PRIORITY_HIGH,          // 优先级
        NULL                    // 任务句柄
    );
    
    xTaskCreate(
        vMediumPriorityTask,
        "MediumPrio",
        configMINIMAL_STACK_SIZE,
        NULL,
        PRIORITY_MEDIUM,
        NULL
    );
    
    xTaskCreate(
        vLowPriorityTask,
        "LowPrio",
        configMINIMAL_STACK_SIZE,
        NULL,
        PRIORITY_LOW,
        NULL
    );
}
```

### 时间片轮转（Round Robin）

当多个任务具有相同优先级时，RTOS使用时间片轮转调度。

**工作原理**：
- 每个任务分配固定的时间片（tick）
- 时间片到期后，调度器切换到下一个同优先级任务
- 被抢占的任务移到就绪队列末尾

**配置示例（FreeRTOS）**：

```c
// FreeRTOSConfig.h
#define configUSE_PREEMPTION            1
#define configUSE_TIME_SLICING          1
#define configTICK_RATE_HZ              1000  // 1ms tick

// 相同优先级的任务
void vTask1(void *pvParameters) {
    for (;;) {
        // 执行工作
        do_work_1();
        // 不调用阻塞函数，依赖时间片切换
    }
}

void vTask2(void *pvParameters) {
    for (;;) {
        // 执行工作
        do_work_2();
        // 不调用阻塞函数，依赖时间片切换
    }
}

// 创建相同优先级的任务
void create_equal_priority_tasks(void) {
    xTaskCreate(vTask1, "Task1", 128, NULL, 2, NULL);
    xTaskCreate(vTask2, "Task2", 128, NULL, 2, NULL);
    // Task1和Task2将轮流执行
}
```

### 任务延时

任务可以主动放弃CPU，进入阻塞状态。

**相对延时**：

```c
void vPeriodicTask(void *pvParameters) {
    for (;;) {
        // 执行工作
        perform_operation();
        
        // 延时100ms（相对延时）
        vTaskDelay(pdMS_TO_TICKS(100));
        // 注意：实际周期会有累积误差
    }
}
```

**绝对延时（精确周期）**：

```c
void vPrecisePeriodicTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xPeriod = pdMS_TO_TICKS(100);
    
    for (;;) {
        // 精确的周期性唤醒
        vTaskDelayUntil(&xLastWakeTime, xPeriod);
        
        // 执行工作
        perform_operation();
        // 即使perform_operation()耗时变化，周期仍然精确
    }
}
```

!!! tip "医疗器械中的周期性任务"
    对于需要精确采样率的医疗设备（如ECG、血氧仪），必须使用`vTaskDelayUntil()`确保精确的采样周期。

### 优先级反转问题

**优先级反转**：高优先级任务被低优先级任务阻塞的现象。

**经典场景**：

```
时间线：
T1(高优先级) ────────────┐等待互斥锁┌────────────
T2(中优先级) ──────┌运行中┐──────────────────────
T3(低优先级) ┌持有锁┐└────┘释放锁└────────────────
```

**说明**: 这是优先级反转的时序图示例。高优先级任务T1等待低优先级任务T3持有的互斥锁，而中优先级任务T2抢占了T3的执行，导致T1被T2间接阻塞。这违反了优先级调度原则，需要使用优先级继承或优先级天花板协议解决。


1. T3（低优先级）获得互斥锁
2. T1（高优先级）尝试获取同一互斥锁，被阻塞
3. T2（中优先级）就绪，抢占T3
4. T1被T2间接阻塞，尽管T1优先级更高

**解决方案：优先级继承**

```c
#include "FreeRTOS.h"
#include "semphr.h"

SemaphoreHandle_t xMutex;

void create_mutex_with_priority_inheritance(void) {
    // 创建支持优先级继承的互斥锁
    xMutex = xSemaphoreCreateMutex();
}

void vHighPriorityTask(void *pvParameters) {
    for (;;) {
        // 获取互斥锁
        if (xSemaphoreTake(xMutex, portMAX_DELAY) == pdTRUE) {
            // 如果低优先级任务持有锁，它会临时继承高优先级
            access_shared_resource();
            
            // 释放互斥锁
            xSemaphoreGive(xMutex);
        }
    }
}

void vLowPriorityTask(void *pvParameters) {
    for (;;) {
        // 获取互斥锁
        if (xSemaphoreTake(xMutex, portMAX_DELAY) == pdTRUE) {
            // 持有锁期间，如果高优先级任务等待，
            // 此任务优先级临时提升
            access_shared_resource();
            
            // 释放锁后，优先级恢复
            xSemaphoreGive(xMutex);
        }
    }
}
```

### 调度器配置

**FreeRTOS配置选项**：

```c
// FreeRTOSConfig.h

// 使能抢占式调度
#define configUSE_PREEMPTION            1

// 使能时间片轮转
#define configUSE_TIME_SLICING          1

// Tick频率（Hz）
#define configTICK_RATE_HZ              1000

// 最大优先级数（0到configMAX_PRIORITIES-1）
#define configMAX_PRIORITIES            5

// 空闲任务栈大小
#define configMINIMAL_STACK_SIZE        128

// 使能任务通知
#define configUSE_TASK_NOTIFICATIONS    1

// 使能互斥锁
#define configUSE_MUTEXES               1

// 使能递归互斥锁
#define configUSE_RECURSIVE_MUTEXES     1
```

### 任务优先级分配策略

**Rate Monotonic Scheduling (RMS)**：
- 周期越短的任务，优先级越高
- 适用于周期性任务
- 可证明的调度性分析

**示例**：

```c
// 任务周期和优先级分配
#define TASK_ECG_PERIOD_MS      10   // ECG采样：10ms周期
#define TASK_SPO2_PERIOD_MS     50   // 血氧采样：50ms周期
#define TASK_DISPLAY_PERIOD_MS  100  // 显示更新：100ms周期

#define PRIORITY_ECG            3    // 最高优先级
#define PRIORITY_SPO2           2    // 中等优先级
#define PRIORITY_DISPLAY        1    // 较低优先级

void vECGTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xPeriod = pdMS_TO_TICKS(TASK_ECG_PERIOD_MS);
    
    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xPeriod);
        sample_ecg_data();
    }
}

void vSpO2Task(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xPeriod = pdMS_TO_TICKS(TASK_SPO2_PERIOD_MS);
    
    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xPeriod);
        sample_spo2_data();
    }
}

void vDisplayTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xPeriod = pdMS_TO_TICKS(TASK_DISPLAY_PERIOD_MS);
    
    for (;;) {
        vTaskDelayUntil(&xLastWakeTime, xPeriod);
        update_display();
    }
}
```

### 调度性分析

**CPU利用率计算**：

```
U = Σ(Ci / Ti)

其中：
Ci = 任务i的最坏执行时间
Ti = 任务i的周期
```

**RMS可调度条件**：

```
U ≤ n(2^(1/n) - 1)

其中n是任务数量
n=3时，U ≤ 0.78 (78%)
```

**示例计算**：

```c
// 任务参数
// ECG: WCET=2ms, Period=10ms
// SpO2: WCET=5ms, Period=50ms
// Display: WCET=8ms, Period=100ms

// CPU利用率
// U = 2/10 + 5/50 + 8/100
//   = 0.2 + 0.1 + 0.08
//   = 0.38 (38%)

// RMS界限（n=3）
// U_bound = 3(2^(1/3) - 1) ≈ 0.78

// 38% < 78%，系统可调度
```

### 医疗器械软件调度最佳实践

1. **明确定义任务优先级**
   ```c
   // 使用枚举定义优先级
   typedef enum {
       PRIORITY_IDLE = 0,
       PRIORITY_BACKGROUND = 1,
       PRIORITY_NORMAL = 2,
       PRIORITY_HIGH = 3,
       PRIORITY_CRITICAL = 4
   } task_priority_t;
   ```

2. **避免优先级反转**
   - 使用互斥锁而非二值信号量保护共享资源
   - 使能优先级继承
   - 最小化临界区

3. **监控任务执行时间**
   ```c
   void vMonitoredTask(void *pvParameters) {
       for (;;) {
           uint32_t start_time = xTaskGetTickCount();
           
           perform_operation();
           
           uint32_t execution_time = xTaskGetTickCount() - start_time;
           if (execution_time > MAX_EXECUTION_TIME) {
               log_warning("Task exceeded time budget");
           }
       }
   }
   ```

4. **实施看门狗监控**
   ```c
   void vWatchdogTask(void *pvParameters) {
       const TickType_t xPeriod = pdMS_TO_TICKS(1000);
       
       for (;;) {
           vTaskDelay(xPeriod);
           
           // 检查关键任务是否响应
           if (!check_task_alive(critical_task_handle)) {
               // 任务无响应，采取措施
               handle_task_failure();
           }
           
           // 喂狗
           feed_hardware_watchdog();
       }
   }
   ```

5. **使用任务通知优化性能**
   ```c
   // 任务通知比信号量更快
   void vISR_Handler(void) {
       BaseType_t xHigherPriorityTaskWoken = pdFALSE;
       
       // 通知任务
       vTaskNotifyGiveFromISR(task_handle, &xHigherPriorityTaskWoken);
       
       portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
   }
   
   void vTask(void *pvParameters) {
       for (;;) {
           // 等待通知
           ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
           
           // 处理事件
           handle_event();
       }
   }
   ```

### 调试和分析工具

**任务统计信息**：

```c
#include "FreeRTOS.h"
#include "task.h"

void print_task_stats(void) {
    TaskStatus_t *pxTaskStatusArray;
    volatile UBaseType_t uxArraySize, x;
    uint32_t ulTotalRunTime, ulStatsAsPercentage;
    
    // 获取任务数量
    uxArraySize = uxTaskGetNumberOfTasks();
    
    // 分配数组
    pxTaskStatusArray = pvPortMalloc(uxArraySize * sizeof(TaskStatus_t));
    
    if (pxTaskStatusArray != NULL) {
        // 获取任务状态
        uxArraySize = uxTaskGetSystemState(pxTaskStatusArray, 
                                           uxArraySize, 
                                           &ulTotalRunTime);
        
        // 打印任务信息
        printf("Task Name\tStatus\tPrio\tStack\tCPU%%\n");
        
        for (x = 0; x < uxArraySize; x++) {
            // 计算CPU使用率
            ulStatsAsPercentage = pxTaskStatusArray[x].ulRunTimeCounter / 
                                 (ulTotalRunTime / 100);
            
            printf("%s\t\t%d\t%d\t%d\t%d%%\n",
                   pxTaskStatusArray[x].pcTaskName,
                   pxTaskStatusArray[x].eCurrentState,
                   pxTaskStatusArray[x].uxCurrentPriority,
                   pxTaskStatusArray[x].usStackHighWaterMark,
                   ulStatsAsPercentage);
        }
        
        vPortFree(pxTaskStatusArray);
    }
}
```

## 实践练习

1. 创建一个包含3个不同优先级任务的RTOS应用
2. 实现一个周期性数据采集系统，确保精确的采样率
3. 模拟优先级反转场景，并使用优先级继承解决
4. 分析一个多任务系统的CPU利用率和可调度性

## 相关资源

### 相关知识模块

- [同步机制](synchronization.md) - RTOS中的互斥锁、信号量和事件组
- [中断处理](interrupt-handling.md) - 中断服务程序和中断优先级管理

### 深入学习

- [RTOS概述](index.md) - RTOS基础知识和选型指南
- [嵌入式C/C++编程](../embedded-c-cpp/index.md) - C语言基础和嵌入式编程技巧

## 参考文献

1. "FreeRTOS Reference Manual" - Real Time Engineers Ltd.
2. "Real-Time Systems" by Jane W. S. Liu
3. IEC 62304:2006+AMD1:2015 - Medical device software
4. "Rate Monotonic Analysis for Real-Time Systems" by Klein et al.
5. "The Art of Designing Embedded Systems" by Jack Ganssle


## 自测问题

??? question "问题1：什么是任务调度？RTOS中有哪些常见的调度算法？"
    **问题**：解释任务调度的概念，并列举RTOS中常用的调度算法。
    
    ??? success "答案"
        **任务调度定义**：
        决定在某个时刻哪个任务应该运行的过程。
        
        **常见调度算法**：
        
        **1. 优先级调度（Priority-based）**：
        - 最常用的RTOS调度算法
        - 高优先级任务优先运行
        - 可抢占式或协作式
        
        **2. 时间片轮转（Round-Robin）**：
        - 相同优先级任务轮流执行
        - 每个任务分配固定时间片
        - 适合多个同等重要的任务
        
        **3. 速率单调调度（Rate Monotonic）**：
        - 周期任务调度
        - 周期越短，优先级越高
        - 可证明的最优静态调度
        
        **4. 最早截止期优先（EDF）**：
        - 动态优先级调度
        - 截止期越近，优先级越高
        - 理论上最优的动态调度
        
        **FreeRTOS示例**：
        ```c
        // 创建不同优先级的任务
        xTaskCreate(high_priority_task, "High", 128, NULL, 3, NULL);
        xTaskCreate(medium_priority_task, "Med", 128, NULL, 2, NULL);
        xTaskCreate(low_priority_task, "Low", 128, NULL, 1, NULL);
        
        // 启动调度器
        vTaskStartScheduler();
        ```
        
        **知识点回顾**：选择合适的调度算法对系统性能和实时性至关重要。

??? question "问题2：什么是优先级反转？如何解决？"
    **问题**：解释优先级反转问题，并描述解决方法。
    
    ??? success "答案"
        **优先级反转定义**：
        高优先级任务被低优先级任务阻塞，导致高优先级任务无法及时运行。
        
        **典型场景**：
        ```
        任务H（高优先级）需要资源R
        任务M（中优先级）正在运行
        任务L（低优先级）持有资源R
        
        结果：任务H被任务L阻塞，但任务M可以抢占任务L
              导致任务H等待时间不确定
        ```
        
        **解决方法1：优先级继承（Priority Inheritance）**：
        ```c
        // FreeRTOS自动支持优先级继承
        SemaphoreHandle_t mutex = xSemaphoreCreateMutex();
        
        // 任务L获取互斥量
        xSemaphoreTake(mutex, portMAX_DELAY);
        // 如果任务H也请求此互斥量，任务L的优先级临时提升到任务H的优先级
        
        // 任务L释放互斥量
        xSemaphoreGive(mutex);
        // 任务L的优先级恢复
        ```
        
        **解决方法2：优先级天花板（Priority Ceiling）**：
        ```c
        // 互斥量的优先级设置为所有可能使用它的任务的最高优先级
        // 任何获取此互斥量的任务都临时提升到这个优先级
        ```
        
        **解决方法3：避免共享资源**：
        ```c
        // 使用消息队列代替共享资源
        QueueHandle_t queue = xQueueCreate(10, sizeof(data_t));
        
        // 任务L发送数据
        xQueueSend(queue, &data, portMAX_DELAY);
        
        // 任务H接收数据
        xQueueReceive(queue, &data, portMAX_DELAY);
        ```
        
        **火星探路者案例**：
        1997年火星探路者因优先级反转导致系统重启，后通过启用优先级继承解决。
        
        **知识点回顾**：优先级反转是实时系统中必须避免的严重问题。

??? question "问题3：抢占式调度和协作式调度有什么区别？"
    **问题**：比较抢占式调度和协作式调度的特点、优缺点和适用场景。
    
    ??? success "答案"
        **抢占式调度（Preemptive Scheduling）**：
        
        **特点**：
        - 高优先级任务可以随时打断低优先级任务
        - 调度器自动切换任务
        - 需要保存和恢复任务上下文
        
        **优点**：
        - 响应时间短
        - 实时性好
        - 任务编写简单
        
        **缺点**：
        - 需要保护共享资源
        - 上下文切换开销
        - 可能出现优先级反转
        
        **示例**：
        ```c
        void high_priority_task(void* param) {
            while (1) {
                // 高优先级工作
                process_urgent_data();
                vTaskDelay(10);  // 可以被更高优先级抢占
            }
        }
        
        void low_priority_task(void* param) {
            while (1) {
                // 低优先级工作
                process_background_data();
                vTaskDelay(100);  // 会被高优先级抢占
            }
        }
        ```
        
        **协作式调度（Cooperative Scheduling）**：
        
        **特点**：
        - 任务主动放弃CPU
        - 任务运行到完成或主动让出
        - 不需要复杂的同步机制
        
        **优点**：
        - 不需要互斥保护
        - 上下文切换开销小
        - 实现简单
        
        **缺点**：
        - 响应时间不确定
        - 一个任务可能阻塞整个系统
        - 任务编写需要注意
        
        **示例**：
        ```c
        void cooperative_task(void* param) {
            while (1) {
                // 做一小部分工作
                process_one_item();
                
                // 主动让出CPU
                taskYIELD();
            }
        }
        ```
        
        **选择建议**：
        - 医疗器械：通常使用抢占式（实时性要求高）
        - 简单系统：可以使用协作式（降低复杂度）
        - 混合模式：相同优先级协作，不同优先级抢占
        
        **知识点回顾**：大多数RTOS使用抢占式调度以保证实时性。

??? question "问题4：如何确定任务的优先级？"
    **问题**：在设计RTOS系统时，如何合理分配任务优先级？
    
    ??? success "答案"
        **优先级分配原则**：
        
        **1. 基于截止期**：
        - 截止期越短，优先级越高
        - 适用于周期性任务
        
        **2. 基于重要性**：
        - 安全关键任务优先级最高
        - 用户交互次之
        - 后台任务最低
        
        **3. 速率单调分配**：
        ```c
        // 任务周期越短，优先级越高
        任务A: 周期10ms  → 优先级5
        任务B: 周期50ms  → 优先级4
        任务C: 周期100ms → 优先级3
        ```
        
        **医疗器械示例**：
        ```c
        // 优先级分配（数字越大优先级越高）
        #define PRIORITY_SAFETY_MONITOR    7  // 安全监控（最高）
        #define PRIORITY_ALARM_HANDLER     6  // 报警处理
        #define PRIORITY_SENSOR_READ       5  // 传感器读取
        #define PRIORITY_CONTROL_LOOP      4  // 控制循环
        #define PRIORITY_DATA_LOGGING      3  // 数据记录
        #define PRIORITY_UI_UPDATE         2  // UI更新
        #define PRIORITY_BACKGROUND        1  // 后台任务（最低）
        
        // 创建任务
        xTaskCreate(safety_monitor_task, "Safety", 256, NULL, 
                   PRIORITY_SAFETY_MONITOR, NULL);
        xTaskCreate(alarm_handler_task, "Alarm", 256, NULL,
                   PRIORITY_ALARM_HANDLER, NULL);
        xTaskCreate(sensor_read_task, "Sensor", 256, NULL,
                   PRIORITY_SENSOR_READ, NULL);
        ```
        
        **优先级分配检查清单**：
        - ☐ 安全关键任务优先级最高
        - ☐ 实时任务优先级高于非实时任务
        - ☐ 避免过多的优先级层次（建议≤7层）
        - ☐ 预留最高优先级给紧急处理
        - ☐ 考虑任务间的依赖关系
        - ☐ 进行可调度性分析
        
        **可调度性分析**：
        ```
        对于速率单调调度：
        CPU利用率 ≤ n(2^(1/n) - 1)
        
        例如3个任务：
        U ≤ 3(2^(1/3) - 1) ≈ 0.78 (78%)
        ```
        
        **知识点回顾**：合理的优先级分配是系统稳定运行的基础。

??? question "问题5：什么是任务饥饿？如何避免？"
    **问题**：解释任务饥饿现象，并提供避免方法。
    
    ??? success "答案"
        **任务饥饿定义**：
        低优先级任务长时间得不到CPU时间，无法执行。
        
        **产生原因**：
        1. 高优先级任务占用CPU时间过长
        2. 中等优先级任务过多
        3. 优先级分配不合理
        
        **示例场景**：
        ```c
        // 高优先级任务循环过快
        void high_priority_task(void* param) {
            while (1) {
                process_data();
                vTaskDelay(1);  // 延迟太短
            }
        }
        
        // 低优先级任务可能饥饿
        void low_priority_task(void* param) {
            while (1) {
                // 很少有机会运行
                background_work();
            }
        }
        ```
        
        **避免方法1：时间片轮转**：
        ```c
        // 为相同优先级任务启用时间片
        #define configUSE_TIME_SLICING 1
        
        // 创建相同优先级的任务
        xTaskCreate(task1, "Task1", 128, NULL, 2, NULL);
        xTaskCreate(task2, "Task2", 128, NULL, 2, NULL);
        // 两个任务轮流执行
        ```
        
        **避免方法2：适当的任务延迟**：
        ```c
        void high_priority_task(void* param) {
            while (1) {
                process_data();
                vTaskDelay(pdMS_TO_TICKS(10));  // 给其他任务机会
            }
        }
        ```
        
        **避免方法3：优先级动态调整**：
        ```c
        void monitor_task(void* param) {
            while (1) {
                // 检测低优先级任务是否饥饿
                if (is_task_starving(low_priority_task)) {
                    // 临时提升优先级
                    vTaskPrioritySet(low_priority_task, HIGH_PRIORITY);
                    vTaskDelay(pdMS_TO_TICKS(100));
                    // 恢复优先级
                    vTaskPrioritySet(low_priority_task, LOW_PRIORITY);
                }
                vTaskDelay(pdMS_TO_TICKS(1000));
            }
        }
        ```
        
        **避免方法4：使用空闲任务钩子**：
        ```c
        void vApplicationIdleHook(void) {
            // 在空闲时执行低优先级工作
            if (has_background_work()) {
                do_background_work();
            }
        }
        ```
        
        **监控任务运行时间**：
        ```c
        // 启用运行时统计
        #define configGENERATE_RUN_TIME_STATS 1
        
        void print_task_stats(void) {
            TaskStatus_t* pxTaskStatusArray;
            UBaseType_t uxArraySize = uxTaskGetNumberOfTasks();
            
            pxTaskStatusArray = pvPortMalloc(uxArraySize * sizeof(TaskStatus_t));
            if (pxTaskStatusArray != NULL) {
                uxArraySize = uxTaskGetSystemState(pxTaskStatusArray, 
                                                   uxArraySize, NULL);
                
                for (UBaseType_t i = 0; i < uxArraySize; i++) {
                    printf("Task: %s, Runtime: %lu\n",
                           pxTaskStatusArray[i].pcTaskName,
                           pxTaskStatusArray[i].ulRunTimeCounter);
                }
                
                vPortFree(pxTaskStatusArray);
            }
        }
        ```
        
        **设计建议**：
        - 限制高优先级任务的CPU使用率
        - 确保所有任务都有运行机会
        - 监控任务运行时间统计
        - 进行负载测试
        
        **知识点回顾**：避免任务饥饿需要合理的系统设计和监控机制。
