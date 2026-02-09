---
title: 同步机制
description: RTOS中的同步机制，包括互斥锁、信号量、消息队列和事件组
difficulty: 中级
estimated_time: 3小时
tags:
- RTOS
- 同步
- 互斥锁
- 信号量
- 消息队列
related_modules:
- zh/technical-knowledge/rtos/task-scheduling
- zh/technical-knowledge/rtos/interrupt-handling
last_updated: '2026-02-09'
version: '1.0'
language: zh-CN
---

# 同步机制

## 学习目标

完成本模块后，你将能够：
- 理解RTOS中各种同步机制的原理和用途
- 正确使用互斥锁保护共享资源
- 掌握信号量的使用场景和最佳实践
- 使用消息队列实现任务间通信
- 应用事件组进行多事件同步
- 避免常见的同步问题（死锁、优先级反转等）

## 前置知识

- C语言基础
- RTOS任务调度基础
- 临界区和原子操作概念
- 中断和上下文切换的理解

## 内容

### 为什么需要同步机制

在多任务系统中，多个任务可能需要访问共享资源（如全局变量、硬件外设、数据结构等）。如果没有适当的同步机制，会导致：

**竞态条件（Race Condition）**：

```c
// 共享变量
volatile uint32_t shared_counter = 0;

// 任务1
void task1(void *param) {
    while (1) {
        shared_counter++;  // 非原子操作！
        vTaskDelay(10);
    }
}

// 任务2
void task2(void *param) {
    while (1) {
        shared_counter++;  // 非原子操作！
        vTaskDelay(10);
    }
}
```

**问题分析**：
```
shared_counter++ 实际上是三个操作：
1. 读取 shared_counter 的值
2. 加1
3. 写回 shared_counter

如果任务1在步骤2时被任务2抢占：
任务1: 读取(0) → 加1(1) → [被抢占]
任务2: 读取(0) → 加1(1) → 写回(1)
任务1: [恢复] → 写回(1)

结果：两次递增，但值只增加了1！
```

**说明**: 这是竞态条件的示例。shared_counter++不是原子操作，包含读取、加1、写回三个步骤。如果任务1在加1后被任务2抢占，两个任务都读到相同的值，最终结果会丢失一次增量，导致数据不一致。


### 互斥锁（Mutex）

**互斥锁**用于保护共享资源，确保同一时间只有一个任务可以访问。

**特点**：
- 支持优先级继承（防止优先级反转）
- 必须由获取锁的任务释放
- 不能在中断中使用
- 支持递归锁定（可选）

**FreeRTOS互斥锁示例**：

```c
#include "FreeRTOS.h"
#include "semphr.h"

// 创建互斥锁
SemaphoreHandle_t xMutex;

void init_mutex(void) {
    xMutex = xSemaphoreCreateMutex();
    if (xMutex == NULL) {
        // 创建失败，处理错误
        error_handler();
    }
}

// 任务1：安全地访问共享资源
void task1(void *param) {
    while (1) {
        // 获取互斥锁（最多等待100ms）
        if (xSemaphoreTake(xMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            // 临界区：访问共享资源
            shared_counter++;
            process_shared_data();
            
            // 释放互斥锁
            xSemaphoreGive(xMutex);
        } else {
            // 获取锁超时，处理错误
            log_error("Failed to acquire mutex");
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

// 任务2：同样安全地访问共享资源
void task2(void *param) {
    while (1) {
        if (xSemaphoreTake(xMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            // 临界区
            shared_counter++;
            process_shared_data();
            
            xSemaphoreGive(xMutex);
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
```

**递归互斥锁**：

```c
// 创建递归互斥锁
SemaphoreHandle_t xRecursiveMutex;

void init_recursive_mutex(void) {
    xRecursiveMutex = xSemaphoreCreateRecursiveMutex();
}

// 递归函数可以多次获取同一个锁
void recursive_function(int depth) {
    if (xSemaphoreTakeRecursive(xRecursiveMutex, portMAX_DELAY) == pdTRUE) {
        // 访问共享资源
        process_data(depth);
        
        if (depth > 0) {
            // 递归调用，再次获取锁
            recursive_function(depth - 1);
        }
        
        // 释放锁
        xSemaphoreGiveRecursive(xRecursiveMutex);
    }
}
```

### 二值信号量（Binary Semaphore）

**二值信号量**类似于互斥锁，但更轻量，常用于任务同步。

**特点**：
- 值只能是0或1
- 可以在中断中使用
- 不支持优先级继承
- 可以由不同任务获取和释放

**用途**：
- 任务与中断同步
- 任务间事件通知
- 资源可用性信号

**示例：中断与任务同步**：

```c
#include "FreeRTOS.h"
#include "semphr.h"

SemaphoreHandle_t xBinarySemaphore;
TaskHandle_t xProcessingTask;

void init_binary_semaphore(void) {
    // 创建二值信号量（初始值为0）
    xBinarySemaphore = xSemaphoreCreateBinary();
}

// 中断服务程序
void UART_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 读取数据
    uint8_t data = UART_ReadData();
    
    // 释放信号量，通知任务
    xSemaphoreGiveFromISR(xBinarySemaphore, &xHigherPriorityTaskWoken);
    
    // 如果需要，进行上下文切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 处理任务
void processing_task(void *param) {
    while (1) {
        // 等待信号量（阻塞直到中断发生）
        if (xSemaphoreTake(xBinarySemaphore, portMAX_DELAY) == pdTRUE) {
            // 处理接收到的数据
            process_uart_data();
        }
    }
}
```

### 计数信号量（Counting Semaphore）

**计数信号量**可以有多个计数值，用于管理多个相同资源。

**特点**：
- 计数值可以大于1
- 适合管理资源池
- 可以在中断中使用

**用途**：
- 管理有限数量的资源
- 事件计数
- 生产者-消费者模式

**示例：资源池管理**：

```c
#include "FreeRTOS.h"
#include "semphr.h"

#define MAX_BUFFERS 5

SemaphoreHandle_t xBufferSemaphore;
uint8_t buffer_pool[MAX_BUFFERS][256];

void init_buffer_pool(void) {
    // 创建计数信号量（初始值为5，最大值为5）
    xBufferSemaphore = xSemaphoreCreateCounting(MAX_BUFFERS, MAX_BUFFERS);
}

// 获取缓冲区
uint8_t* acquire_buffer(void) {
    if (xSemaphoreTake(xBufferSemaphore, pdMS_TO_TICKS(100)) == pdTRUE) {
        // 找到可用缓冲区
        for (int i = 0; i < MAX_BUFFERS; i++) {
            if (is_buffer_free(i)) {
                mark_buffer_used(i);
                return buffer_pool[i];
            }
        }
    }
    return NULL;  // 无可用缓冲区
}

// 释放缓冲区
void release_buffer(uint8_t* buffer) {
    // 标记缓冲区为空闲
    int index = get_buffer_index(buffer);
    mark_buffer_free(index);
    
    // 释放信号量
    xSemaphoreGive(xBufferSemaphore);
}

// 生产者任务
void producer_task(void *param) {
    while (1) {
        uint8_t* buffer = acquire_buffer();
        if (buffer != NULL) {
            // 填充数据
            fill_buffer(buffer);
            
            // 发送到消费者
            send_to_consumer(buffer);
        }
        
        vTaskDelay(pdMS_TO_TICKS(50));
    }
}

// 消费者任务
void consumer_task(void *param) {
    while (1) {
        uint8_t* buffer = receive_from_producer();
        if (buffer != NULL) {
            // 处理数据
            process_buffer(buffer);
            
            // 释放缓冲区
            release_buffer(buffer);
        }
    }
}
```

### 消息队列（Message Queue）

**消息队列**用于任务间传递数据，是最常用的通信机制。

**特点**：
- FIFO（先进先出）顺序
- 可以传递任意类型的数据
- 支持阻塞和非阻塞操作
- 可以在中断中使用

**用途**：
- 任务间数据传递
- 事件通知（携带数据）
- 解耦生产者和消费者

**示例：传感器数据采集**：

```c
#include "FreeRTOS.h"
#include "queue.h"

// 定义消息结构
typedef struct {
    uint32_t timestamp;
    float temperature;
    float humidity;
    uint8_t sensor_id;
} sensor_data_t;

#define QUEUE_LENGTH 10
QueueHandle_t xSensorQueue;

void init_sensor_queue(void) {
    // 创建队列（10个元素，每个元素大小为sensor_data_t）
    xSensorQueue = xQueueCreate(QUEUE_LENGTH, sizeof(sensor_data_t));
    if (xSensorQueue == NULL) {
        error_handler();
    }
}

// 传感器采集任务
void sensor_task(void *param) {
    sensor_data_t data;
    
    while (1) {
        // 读取传感器数据
        data.timestamp = xTaskGetTickCount();
        data.temperature = read_temperature();
        data.humidity = read_humidity();
        data.sensor_id = 1;
        
        // 发送到队列（最多等待10ms）
        if (xQueueSend(xSensorQueue, &data, pdMS_TO_TICKS(10)) != pdTRUE) {
            // 队列满，数据丢失
            log_warning("Queue full, data dropped");
        }
        
        vTaskDelay(pdMS_TO_TICKS(1000));  // 1秒采样一次
    }
}

// 数据处理任务
void processing_task(void *param) {
    sensor_data_t data;
    
    while (1) {
        // 从队列接收数据（阻塞等待）
        if (xQueueReceive(xSensorQueue, &data, portMAX_DELAY) == pdTRUE) {
            // 处理数据
            printf("Sensor %d: Temp=%.1f°C, Humidity=%.1f%%\n",
                   data.sensor_id, data.temperature, data.humidity);
            
            // 存储到数据库
            store_sensor_data(&data);
            
            // 检查阈值
            if (data.temperature > 40.0f) {
                trigger_alarm();
            }
        }
    }
}

// 中断中发送数据
void ADC_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    sensor_data_t data;
    
    // 读取ADC值
    data.timestamp = xTaskGetTickCount();
    data.temperature = read_adc_temperature();
    data.sensor_id = 2;
    
    // 从中断发送到队列
    xQueueSendFromISR(xSensorQueue, &data, &xHigherPriorityTaskWoken);
    
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

**队列操作API**：

```c
// 发送到队列尾部
xQueueSend(xQueue, &data, xTicksToWait);

// 发送到队列头部（高优先级）
xQueueSendToFront(xQueue, &data, xTicksToWait);

// 从队列接收
xQueueReceive(xQueue, &buffer, xTicksToWait);

// 查看队列头部（不移除）
xQueuePeek(xQueue, &buffer, xTicksToWait);

// 获取队列中的消息数量
uxQueueMessagesWaiting(xQueue);

// 获取队列可用空间
uxQueueSpacesAvailable(xQueue);

// 重置队列
xQueueReset(xQueue);
```

### 事件组（Event Group）

**事件组**用于同步多个事件，一个任务可以等待多个事件的组合。

**特点**：
- 每个事件组有24位（FreeRTOS）或32位事件标志
- 支持等待任意事件或所有事件
- 可以在中断中设置事件
- 适合复杂的同步场景

**用途**：
- 等待多个条件满足
- 多任务协调
- 状态机实现

**示例：医疗设备启动同步**：

```c
#include "FreeRTOS.h"
#include "event_groups.h"

// 定义事件位
#define EVENT_SENSOR_READY      (1 << 0)  // 传感器就绪
#define EVENT_CALIBRATION_DONE  (1 << 1)  // 校准完成
#define EVENT_SELFTEST_PASSED   (1 << 2)  // 自检通过
#define EVENT_NETWORK_CONNECTED (1 << 3)  // 网络连接

#define ALL_STARTUP_EVENTS (EVENT_SENSOR_READY | \
                           EVENT_CALIBRATION_DONE | \
                           EVENT_SELFTEST_PASSED | \
                           EVENT_NETWORK_CONNECTED)

EventGroupHandle_t xStartupEvents;

void init_event_group(void) {
    xStartupEvents = xEventGroupCreate();
}

// 传感器初始化任务
void sensor_init_task(void *param) {
    // 初始化传感器
    init_sensors();
    
    // 设置事件标志
    xEventGroupSetBits(xStartupEvents, EVENT_SENSOR_READY);
    
    vTaskDelete(NULL);  // 任务完成，删除自己
}

// 校准任务
void calibration_task(void *param) {
    // 等待传感器就绪
    xEventGroupWaitBits(xStartupEvents,
                       EVENT_SENSOR_READY,
                       pdFALSE,  // 不清除位
                       pdTRUE,   // 等待所有位
                       portMAX_DELAY);
    
    // 执行校准
    perform_calibration();
    
    // 设置校准完成标志
    xEventGroupSetBits(xStartupEvents, EVENT_CALIBRATION_DONE);
    
    vTaskDelete(NULL);
}

// 自检任务
void selftest_task(void *param) {
    // 等待传感器和校准完成
    xEventGroupWaitBits(xStartupEvents,
                       EVENT_SENSOR_READY | EVENT_CALIBRATION_DONE,
                       pdFALSE,
                       pdTRUE,  // 等待所有位
                       portMAX_DELAY);
    
    // 执行自检
    if (perform_selftest()) {
        xEventGroupSetBits(xStartupEvents, EVENT_SELFTEST_PASSED);
    } else {
        // 自检失败，进入错误状态
        enter_error_state();
    }
    
    vTaskDelete(NULL);
}

// 主任务
void main_task(void *param) {
    // 等待所有启动事件完成
    EventBits_t uxBits = xEventGroupWaitBits(
        xStartupEvents,
        ALL_STARTUP_EVENTS,
        pdFALSE,  // 不清除位
        pdTRUE,   // 等待所有位
        pdMS_TO_TICKS(30000)  // 最多等待30秒
    );
    
    if ((uxBits & ALL_STARTUP_EVENTS) == ALL_STARTUP_EVENTS) {
        // 所有启动条件满足，开始正常运行
        printf("System ready!\n");
        start_normal_operation();
    } else {
        // 启动超时
        printf("Startup timeout!\n");
        handle_startup_failure();
    }
}

// 中断中设置事件
void NETWORK_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    if (network_connected()) {
        xEventGroupSetBitsFromISR(xStartupEvents,
                                 EVENT_NETWORK_CONNECTED,
                                 &xHigherPriorityTaskWoken);
    }
    
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```

**事件组API**：

```c
// 设置事件位
xEventGroupSetBits(xEventGroup, uxBitsToSet);

// 清除事件位
xEventGroupClearBits(xEventGroup, uxBitsToClear);

// 等待事件位
xEventGroupWaitBits(xEventGroup,
                   uxBitsToWaitFor,
                   xClearOnExit,
                   xWaitForAllBits,
                   xTicksToWait);

// 获取当前事件位
xEventGroupGetBits(xEventGroup);

// 从中断设置事件位
xEventGroupSetBitsFromISR(xEventGroup, uxBitsToSet, pxHigherPriorityTaskWoken);
```

### 任务通知（Task Notification）

**任务通知**是FreeRTOS的轻量级同步机制，比信号量和队列更快。

**特点**：
- 每个任务有一个32位通知值
- 速度快，RAM占用少
- 只能通知特定任务
- 不能广播

**用途**：
- 简单的任务间通知
- 替代二值信号量
- 替代计数信号量
- 替代事件组（有限）

**示例：任务通知替代信号量**：

```c
#include "FreeRTOS.h"
#include "task.h"

TaskHandle_t xProcessingTaskHandle;

// 中断服务程序
void UART_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 读取数据
    uint8_t data = UART_ReadData();
    
    // 通知任务（替代xSemaphoreGiveFromISR）
    vTaskNotifyGiveFromISR(xProcessingTaskHandle, &xHigherPriorityTaskWoken);
    
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 处理任务
void processing_task(void *param) {
    while (1) {
        // 等待通知（替代xSemaphoreTake）
        ulTaskNotifyTake(pdTRUE,  // 清除计数
                        portMAX_DELAY);
        
        // 处理数据
        process_uart_data();
    }
}

void create_tasks(void) {
    xTaskCreate(processing_task,
               "Processing",
               256,
               NULL,
               2,
               &xProcessingTaskHandle);  // 保存任务句柄
}
```

**任务通知作为事件标志**：

```c
// 定义事件位
#define EVENT_DATA_READY    (1 << 0)
#define EVENT_ERROR         (1 << 1)
#define EVENT_TIMEOUT       (1 << 2)

TaskHandle_t xTaskHandle;

// 发送任务
void sender_task(void *param) {
    while (1) {
        // 设置事件位
        xTaskNotify(xTaskHandle,
                   EVENT_DATA_READY,
                   eSetBits);  // 设置位
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// 接收任务
void receiver_task(void *param) {
    uint32_t ulNotificationValue;
    
    while (1) {
        // 等待任何事件
        xTaskNotifyWait(0,  // 进入时不清除位
                       0xFFFFFFFF,  // 退出时清除所有位
                       &ulNotificationValue,
                       portMAX_DELAY);
        
        // 检查事件
        if (ulNotificationValue & EVENT_DATA_READY) {
            handle_data_ready();
        }
        if (ulNotificationValue & EVENT_ERROR) {
            handle_error();
        }
        if (ulNotificationValue & EVENT_TIMEOUT) {
            handle_timeout();
        }
    }
}
```

### 同步机制选择指南

| 机制 | 用途 | 优点 | 缺点 | 适用场景 |
|------|------|------|------|----------|
| **互斥锁** | 保护共享资源 | 支持优先级继承 | 不能在中断中使用 | 保护临界区 |
| **二值信号量** | 任务同步 | 可在中断中使用 | 无优先级继承 | 中断与任务同步 |
| **计数信号量** | 资源计数 | 管理多个资源 | 无优先级继承 | 资源池管理 |
| **消息队列** | 数据传递 | 传递任意数据 | 占用内存较多 | 任务间通信 |
| **事件组** | 多事件同步 | 等待多个事件 | 有位数限制 | 复杂同步场景 |
| **任务通知** | 简单通知 | 速度快，占用少 | 只能通知一个任务 | 简单的1对1通知 |

**选择流程图**：

```
需要传递数据？
├─ 是 → 使用消息队列
└─ 否 → 需要等待多个事件？
    ├─ 是 → 使用事件组
    └─ 否 → 需要保护共享资源？
        ├─ 是 → 使用互斥锁
        └─ 否 → 需要在中断中使用？
            ├─ 是 → 使用二值信号量或任务通知
            └─ 否 → 需要管理多个资源？
                ├─ 是 → 使用计数信号量
                └─ 否 → 使用任务通知（最快）
```

**说明**: 这是同步机制选择的决策树。根据是否需要传递数据、是否需要等待多个事件、是否需要保护共享资源、是否在中断中使用、是否管理多个资源等条件，选择合适的同步机制(消息队列、事件组、互斥锁、信号量、任务通知等)。


## 最佳实践

### 1. 最小化临界区

!!! tip "临界区优化"
    临界区应该尽可能短，只保护必要的代码。

```c
// ❌ 不好：临界区太长
void bad_example(void) {
    xSemaphoreTake(xMutex, portMAX_DELAY);
    
    // 长时间计算（不需要保护）
    complex_calculation();
    
    // 访问共享资源
    shared_data++;
    
    // 更多计算（不需要保护）
    more_calculations();
    
    xSemaphoreGive(xMutex);
}

// ✅ 好：临界区最小化
void good_example(void) {
    // 先做不需要保护的计算
    complex_calculation();
    
    // 只在访问共享资源时加锁
    xSemaphoreTake(xMutex, portMAX_DELAY);
    shared_data++;
    xSemaphoreGive(xMutex);
    
    // 后续计算
    more_calculations();
}
```

### 2. 避免死锁

**死锁条件**：
1. 互斥访问
2. 持有并等待
3. 不可抢占
4. 循环等待

**避免策略**：

```c
// ❌ 可能死锁：不同顺序获取锁
void task1(void *param) {
    xSemaphoreTake(xMutexA, portMAX_DELAY);
    xSemaphoreTake(xMutexB, portMAX_DELAY);
    // ...
    xSemaphoreGive(xMutexB);
    xSemaphoreGive(xMutexA);
}

void task2(void *param) {
    xSemaphoreTake(xMutexB, portMAX_DELAY);  // 顺序相反！
    xSemaphoreTake(xMutexA, portMAX_DELAY);
    // ...
    xSemaphoreGive(xMutexA);
    xSemaphoreGive(xMutexB);
}

// ✅ 避免死锁：统一获取顺序
void task1_safe(void *param) {
    xSemaphoreTake(xMutexA, portMAX_DELAY);
    xSemaphoreTake(xMutexB, portMAX_DELAY);
    // ...
    xSemaphoreGive(xMutexB);
    xSemaphoreGive(xMutexA);
}

void task2_safe(void *param) {
    xSemaphoreTake(xMutexA, portMAX_DELAY);  // 相同顺序
    xSemaphoreTake(xMutexB, portMAX_DELAY);
    // ...
    xSemaphoreGive(xMutexB);
    xSemaphoreGive(xMutexA);
}

// ✅ 更好：使用超时避免永久阻塞
void task_with_timeout(void *param) {
    if (xSemaphoreTake(xMutexA, pdMS_TO_TICKS(100)) == pdTRUE) {
        if (xSemaphoreTake(xMutexB, pdMS_TO_TICKS(100)) == pdTRUE) {
            // 成功获取两个锁
            // ...
            xSemaphoreGive(xMutexB);
        }
        xSemaphoreGive(xMutexA);
    } else {
        // 获取锁超时，记录错误
        log_error("Lock acquisition timeout");
    }
}
```

### 3. 正确使用互斥锁和信号量

!!! warning "互斥锁 vs 信号量"
    - 互斥锁：用于保护共享资源（必须由获取者释放）
    - 信号量：用于同步和信号通知（可以由不同任务释放）

```c
// ✅ 正确：使用互斥锁保护共享资源
SemaphoreHandle_t xMutex = xSemaphoreCreateMutex();

void access_shared_resource(void) {
    xSemaphoreTake(xMutex, portMAX_DELAY);
    // 访问共享资源
    shared_resource++;
    xSemaphoreGive(xMutex);  // 同一任务释放
}

// ✅ 正确：使用信号量进行同步
SemaphoreHandle_t xSemaphore = xSemaphoreCreateBinary();

void producer(void) {
    // 生产数据
    produce_data();
    // 通知消费者
    xSemaphoreGive(xSemaphore);  // 不同任务释放
}

void consumer(void) {
    // 等待数据
    xSemaphoreTake(xSemaphore, portMAX_DELAY);
    // 消费数据
    consume_data();
}
```

### 4. 队列大小设计

```c
// 考虑因素：
// 1. 生产速率 vs 消费速率
// 2. 突发流量
// 3. 内存限制
// 4. 数据丢失容忍度

// 示例：传感器数据队列
#define SENSOR_SAMPLE_RATE_HZ   100  // 采样率
#define PROCESSING_TIME_MS      5    // 处理时间
#define BURST_FACTOR            2    // 突发因子

// 队列大小计算
#define QUEUE_SIZE ((SENSOR_SAMPLE_RATE_HZ * PROCESSING_TIME_MS / 1000) * BURST_FACTOR)

QueueHandle_t xSensorQueue = xQueueCreate(QUEUE_SIZE, sizeof(sensor_data_t));
```

### 5. 中断安全

!!! danger "中断中的限制"
    - 不能使用互斥锁
    - 不能使用阻塞调用
    - 必须使用FromISR版本的API
    - 保持ISR尽可能短

```c
// ✅ 正确的中断处理
void UART_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    uint8_t data;
    
    // 快速读取数据
    data = UART_ReadData();
    
    // 发送到队列（FromISR版本）
    xQueueSendFromISR(xDataQueue, &data, &xHigherPriorityTaskWoken);
    
    // 必要时进行上下文切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// ❌ 错误：在中断中使用互斥锁
void BAD_IRQHandler(void) {
    xSemaphoreTake(xMutex, portMAX_DELAY);  // 错误！
    // ...
    xSemaphoreGive(xMutex);
}
```

## 常见陷阱

### 1. 忘记释放锁

```c
// ❌ 危险：可能忘记释放锁
void risky_function(void) {
    xSemaphoreTake(xMutex, portMAX_DELAY);
    
    if (error_condition) {
        return;  // 忘记释放锁！
    }
    
    process_data();
    xSemaphoreGive(xMutex);
}

// ✅ 安全：使用goto或确保所有路径释放锁
void safe_function(void) {
    xSemaphoreTake(xMutex, portMAX_DELAY);
    
    if (error_condition) {
        goto cleanup;
    }
    
    process_data();
    
cleanup:
    xSemaphoreGive(xMutex);
}
```

### 2. 优先级反转

```c
// 问题：低优先级任务持有锁，高优先级任务等待
// 解决：使用互斥锁（自动优先级继承）

// ✅ 使用互斥锁
SemaphoreHandle_t xMutex = xSemaphoreCreateMutex();

// ❌ 不要用二值信号量保护共享资源
SemaphoreHandle_t xSemaphore = xSemaphoreCreateBinary();
```

### 3. 队列溢出

```c
// ❌ 不检查返回值
void bad_sender(void) {
    xQueueSend(xQueue, &data, 0);  // 可能失败
}

// ✅ 检查返回值并处理
void good_sender(void) {
    if (xQueueSend(xQueue, &data, pdMS_TO_TICKS(10)) != pdTRUE) {
        // 队列满，记录错误
        log_error("Queue full, data dropped");
        dropped_messages++;
    }
}
```

### 4. 在中断中使用错误的API

```c
// ❌ 错误：在中断中使用普通API
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

## 实践练习

1. **互斥锁练习**：创建两个任务共享一个计数器，使用互斥锁保护，验证计数正确性
2. **生产者-消费者**：实现一个生产者-消费者系统，使用队列传递数据
3. **多事件同步**：使用事件组实现一个需要多个条件满足才能启动的系统
4. **死锁检测**：故意创建一个死锁场景，然后修复它
5. **性能对比**：对比信号量和任务通知的性能差异

## 相关资源

### 相关知识模块

- [任务调度](task-scheduling.md) - RTOS任务调度和优先级管理
- [中断处理](interrupt-handling.md) - 中断服务程序和中断优先级
- [资源管理](resource-management.md) - 内存管理和资源池

### 深入学习

- [RTOS概述](index.md) - RTOS基础知识和选型指南
- [嵌入式C/C++编程](../embedded-c-cpp/index.md) - C语言基础和嵌入式编程技巧

## 参考文献

1. "Mastering the FreeRTOS Real Time Kernel" - Richard Barry
2. "Real-Time Systems" by Jane W. S. Liu
3. "The Art of Concurrency" by Clay Breshears
4. IEC 62304:2006+AMD1:2015 - Medical device software
5. "Operating System Concepts" by Silberschatz, Galvin, and Gagne

## 自测问题

??? question "问题1：互斥锁和二值信号量有什么区别？"
    **问题**：解释互斥锁和二值信号量的区别，以及各自的适用场景。
    
    ??? success "答案"
        **主要区别**：
        
        **1. 所有权**：
        - 互斥锁：有所有权概念，必须由获取锁的任务释放
        - 二值信号量：无所有权，可以由不同任务释放
        
        **2. 优先级继承**：
        - 互斥锁：支持优先级继承，防止优先级反转
        - 二值信号量：不支持优先级继承
        
        **3. 递归锁定**：
        - 互斥锁：支持递归锁定（递归互斥锁）
        - 二值信号量：不支持递归
        
        **4. 使用场景**：
        - 互斥锁：保护共享资源（临界区）
        - 二值信号量：任务同步、事件通知
        
        **代码示例**：
        ```c
        // 互斥锁：保护共享资源
        SemaphoreHandle_t xMutex = xSemaphoreCreateMutex();
        
        void task_a(void *param) {
            xSemaphoreTake(xMutex, portMAX_DELAY);
            shared_data++;  // 临界区
            xSemaphoreGive(xMutex);  // 必须由task_a释放
        }
        
        // 二值信号量：任务同步
        SemaphoreHandle_t xSemaphore = xSemaphoreCreateBinary();
        
        void producer(void *param) {
            produce_data();
            xSemaphoreGive(xSemaphore);  // 生产者释放
        }
        
        void consumer(void *param) {
            xSemaphoreTake(xSemaphore, portMAX_DELAY);  // 消费者获取
            consume_data();
        }
        ```
        
        **选择建议**：
        - 保护共享资源 → 使用互斥锁
        - 任务间同步 → 使用二值信号量或任务通知
        - 中断与任务同步 → 使用二值信号量（互斥锁不能在中断中使用）

??? question "问题2：什么是死锁？如何避免？"
    **问题**：解释死锁的概念、产生条件和避免方法。
    
    ??? success "答案"
        **死锁定义**：
        两个或多个任务互相等待对方持有的资源，导致所有任务都无法继续执行。
        
        **死锁的四个必要条件**：
        1. **互斥**：资源不能被共享
        2. **持有并等待**：任务持有资源的同时等待其他资源
        3. **不可抢占**：资源不能被强制释放
        4. **循环等待**：存在任务等待环路
        
        **经典死锁场景**：
        ```c
        // 任务1
        xSemaphoreTake(xMutexA, portMAX_DELAY);
        vTaskDelay(10);  // 模拟处理
        xSemaphoreTake(xMutexB, portMAX_DELAY);  // 等待B
        // ...
        xSemaphoreGive(xMutexB);
        xSemaphoreGive(xMutexA);
        
        // 任务2
        xSemaphoreTake(xMutexB, portMAX_DELAY);
        vTaskDelay(10);  // 模拟处理
        xSemaphoreTake(xMutexA, portMAX_DELAY);  // 等待A
        // ...
        xSemaphoreGive(xMutexA);
        xSemaphoreGive(xMutexB);
        ```
        
        **避免方法**：
        
        **1. 统一锁获取顺序**：
        ```c
        // 所有任务按相同顺序获取锁
        void task1(void *param) {
            xSemaphoreTake(xMutexA, portMAX_DELAY);
            xSemaphoreTake(xMutexB, portMAX_DELAY);
            // ...
            xSemaphoreGive(xMutexB);
            xSemaphoreGive(xMutexA);
        }
        
        void task2(void *param) {
            xSemaphoreTake(xMutexA, portMAX_DELAY);  // 相同顺序
            xSemaphoreTake(xMutexB, portMAX_DELAY);
            // ...
            xSemaphoreGive(xMutexB);
            xSemaphoreGive(xMutexA);
        }
        ```
        
        **2. 使用超时**：
        ```c
        void task_with_timeout(void *param) {
            if (xSemaphoreTake(xMutexA, pdMS_TO_TICKS(100)) == pdTRUE) {
                if (xSemaphoreTake(xMutexB, pdMS_TO_TICKS(100)) == pdTRUE) {
                    // 成功获取两个锁
                    // ...
                    xSemaphoreGive(xMutexB);
                } else {
                    // 获取B超时，释放A
                    xSemaphoreGive(xMutexA);
                }
            }
        }
        ```
        
        **3. 一次性获取所有资源**：
        ```c
        SemaphoreHandle_t xMasterLock;
        
        void task(void *param) {
            xSemaphoreTake(xMasterLock, portMAX_DELAY);
            // 现在可以安全地获取其他锁
            xSemaphoreTake(xMutexA, portMAX_DELAY);
            xSemaphoreTake(xMutexB, portMAX_DELAY);
            // ...
            xSemaphoreGive(xMutexB);
            xSemaphoreGive(xMutexA);
            xSemaphoreGive(xMasterLock);
        }
        ```
        
        **4. 避免嵌套锁**：
        ```c
        // 重新设计，避免需要多个锁
        void task(void *param) {
            xSemaphoreTake(xSingleMutex, portMAX_DELAY);
            // 访问所有共享资源
            xSemaphoreGive(xSingleMutex);
        }
        ```

??? question "问题3：消息队列满了怎么办？"
    **问题**：当消息队列满时，有哪些处理策略？
    
    ??? success "答案"
        **处理策略**：
        
        **1. 阻塞等待**：
        ```c
        // 等待直到队列有空间
        xQueueSend(xQueue, &data, portMAX_DELAY);
        ```
        - 优点：不丢失数据
        - 缺点：可能阻塞发送任务
        
        **2. 超时等待**：
        ```c
        // 等待一段时间
        if (xQueueSend(xQueue, &data, pdMS_TO_TICKS(100)) != pdTRUE) {
            // 超时，处理错误
            log_error("Queue send timeout");
        }
        ```
        - 优点：不会永久阻塞
        - 缺点：可能丢失数据
        
        **3. 立即返回**：
        ```c
        // 不等待
        if (xQueueSend(xQueue, &data, 0) != pdTRUE) {
            // 队列满，丢弃数据
            dropped_count++;
        }
        ```
        - 优点：不阻塞
        - 缺点：丢失数据
        
        **4. 覆盖旧数据**：
        ```c
        // 使用xQueueOverwrite（仅适用于长度为1的队列）
        xQueueOverwrite(xQueue, &data);
        ```
        - 优点：总是保存最新数据
        - 缺点：丢失旧数据
        
        **5. 优先级队列**：
        ```c
        // 高优先级数据发送到队列头部
        if (is_high_priority(data)) {
            xQueueSendToFront(xQueue, &data, 0);
        } else {
            xQueueSend(xQueue, &data, 0);
        }
        ```
        
        **6. 动态调整队列大小**：
        ```c
        // 监控队列使用率
        void monitor_queue(void) {
            UBaseType_t uxMessagesWaiting = uxQueueMessagesWaiting(xQueue);
            UBaseType_t uxSpacesAvailable = uxQueueSpacesAvailable(xQueue);
            
            float usage = (float)uxMessagesWaiting / 
                         (uxMessagesWaiting + uxSpacesAvailable);
            
            if (usage > 0.9f) {
                log_warning("Queue almost full: %.0f%%", usage * 100);
                // 考虑增加队列大小或优化处理速度
            }
        }
        ```
        
        **7. 背压机制**：
        ```c
        // 通知生产者减慢速度
        void producer(void *param) {
            while (1) {
                if (uxQueueSpacesAvailable(xQueue) < 2) {
                    // 队列快满了，减慢生产速度
                    vTaskDelay(pdMS_TO_TICKS(50));
                }
                
                produce_data(&data);
                xQueueSend(xQueue, &data, pdMS_TO_TICKS(100));
            }
        }
        ```
        
        **选择建议**：
        - 关键数据：使用阻塞等待或超时等待
        - 实时数据：使用覆盖或丢弃旧数据
        - 监控系统：记录丢失数据的统计信息
        - 设计阶段：合理设计队列大小

??? question "问题4：什么时候使用事件组？"
    **问题**：事件组的适用场景和使用注意事项。
    
    ??? success "答案"
        **适用场景**：
        
        **1. 等待多个条件**：
        ```c
        // 等待所有初始化完成
        EventBits_t uxBits = xEventGroupWaitBits(
            xEventGroup,
            INIT_SENSOR | INIT_NETWORK | INIT_STORAGE,
            pdFALSE,  // 不清除
            pdTRUE,   // 等待所有位
            portMAX_DELAY
        );
        ```
        
        **2. 等待任意条件**：
        ```c
        // 等待任意输入源
        EventBits_t uxBits = xEventGroupWaitBits(
            xEventGroup,
            INPUT_UART | INPUT_USB | INPUT_NETWORK,
            pdTRUE,   // 清除触发的位
            pdFALSE,  // 等待任意位
            portMAX_DELAY
        );
        
        // 检查哪个输入源触发
        if (uxBits & INPUT_UART) {
            handle_uart_input();
        }
        ```
        
        **3. 状态机实现**：
        ```c
        #define STATE_IDLE      (1 << 0)
        #define STATE_RUNNING   (1 << 1)
        #define STATE_PAUSED    (1 << 2)
        #define STATE_ERROR     (1 << 3)
        
        void set_state(EventBits_t new_state) {
            xEventGroupClearBits(xStateGroup, 0xFFFFFF);
            xEventGroupSetBits(xStateGroup, new_state);
        }
        
        EventBits_t get_state(void) {
            return xEventGroupGetBits(xStateGroup);
        }
        ```
        
        **4. 多任务协调**：
        ```c
        // 任务A完成工作
        xEventGroupSetBits(xEventGroup, TASK_A_DONE);
        
        // 任务B完成工作
        xEventGroupSetBits(xEventGroup, TASK_B_DONE);
        
        // 主任务等待所有任务完成
        xEventGroupWaitBits(xEventGroup,
                           TASK_A_DONE | TASK_B_DONE,
                           pdTRUE,
                           pdTRUE,
                           portMAX_DELAY);
        ```
        
        **使用注意事项**：
        
        **1. 位数限制**：
        - FreeRTOS：24位可用（8位保留）
        - 其他RTOS可能不同
        
        **2. 不传递数据**：
        ```c
        // ❌ 事件组不能传递数据
        // 如果需要传递数据，使用消息队列
        
        // ✅ 事件组通知，队列传递数据
        xEventGroupSetBits(xEventGroup, DATA_READY);
        xQueueSend(xDataQueue, &data, 0);
        ```
        
        **3. 性能考虑**：
        ```c
        // 事件组比多个信号量更高效
        // ❌ 使用多个信号量
        xSemaphoreTake(xSem1, portMAX_DELAY);
        xSemaphoreTake(xSem2, portMAX_DELAY);
        xSemaphoreTake(xSem3, portMAX_DELAY);
        
        // ✅ 使用事件组
        xEventGroupWaitBits(xEventGroup,
                           BIT1 | BIT2 | BIT3,
                           pdTRUE, pdTRUE,
                           portMAX_DELAY);
        ```
        
        **4. 中断安全**：
        ```c
        // 在中断中只能设置位，不能等待
        void ISR_Handler(void) {
            BaseType_t xHigherPriorityTaskWoken = pdFALSE;
            xEventGroupSetBitsFromISR(xEventGroup,
                                     EVENT_BIT,
                                     &xHigherPriorityTaskWoken);
            portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
        }
        ```
        
        **不适用场景**：
        - 需要传递数据 → 使用队列
        - 简单的1对1通知 → 使用任务通知
        - 需要计数 → 使用计数信号量
        - 需要超过24个标志 → 使用其他机制

??? question "问题5：任务通知相比信号量有什么优势？"
    **问题**：解释任务通知的优势和限制。
    
    ??? success "答案"
        **任务通知的优势**：
        
        **1. 速度更快**：
        ```c
        // 任务通知比信号量快约45%
        // 基准测试（FreeRTOS）：
        // 信号量：~100个CPU周期
        // 任务通知：~55个CPU周期
        ```
        
        **2. RAM占用更少**：
        ```c
        // 信号量：需要额外的内核对象（约80字节）
        // 任务通知：使用任务控制块中的现有字段（0额外字节）
        ```
        
        **3. 使用简单**：
        ```c
        // 信号量方式
        SemaphoreHandle_t xSemaphore = xSemaphoreCreateBinary();
        xSemaphoreGive(xSemaphore);
        xSemaphoreTake(xSemaphore, portMAX_DELAY);
        
        // 任务通知方式
        xTaskNotifyGive(xTaskHandle);
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        ```
        
        **4. 功能丰富**：
        ```c
        // 可以作为多种机制使用
        
        // 作为二值信号量
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        
        // 作为计数信号量
        ulTaskNotifyTake(pdFALSE, portMAX_DELAY);
        
        // 作为事件组
        xTaskNotifyWait(0, 0xFFFFFFFF, &value, portMAX_DELAY);
        
        // 作为轻量级队列（传递32位值）
        xTaskNotify(xTaskHandle, value, eSetValueWithOverwrite);
        ```
        
        **任务通知的限制**：
        
        **1. 只能通知一个任务**：
        ```c
        // ❌ 不能广播
        // 信号量可以被多个任务等待
        // 任务通知只能通知特定任务
        
        // 如果需要广播，使用信号量或事件组
        ```
        
        **2. 每个任务只有一个通知值**：
        ```c
        // 如果需要多个独立的通知，使用多个信号量
        ```
        
        **3. 不能在任务创建前使用**：
        ```c
        // 必须先创建任务，获得任务句柄
        TaskHandle_t xTaskHandle;
        xTaskCreate(task_function, "Task", 128, NULL, 1, &xTaskHandle);
        
        // 然后才能通知
        xTaskNotifyGive(xTaskHandle);
        ```
        
        **性能对比示例**：
        ```c
        // 测试代码
        void performance_test(void) {
            uint32_t start, end;
            
            // 测试信号量
            start = get_cycle_count();
            xSemaphoreGive(xSemaphore);
            xSemaphoreTake(xSemaphore, 0);
            end = get_cycle_count();
            printf("Semaphore: %lu cycles\n", end - start);
            
            // 测试任务通知
            start = get_cycle_count();
            xTaskNotifyGive(xTaskHandle);
            ulTaskNotifyTake(pdTRUE, 0);
            end = get_cycle_count();
            printf("Task notification: %lu cycles\n", end - start);
        }
        ```
        
        **选择建议**：
        - 简单的1对1通知 → 使用任务通知（最快）
        - 需要广播 → 使用信号量或事件组
        - 需要多个等待者 → 使用信号量
        - 需要传递复杂数据 → 使用队列
        - 性能关键场景 → 优先考虑任务通知
