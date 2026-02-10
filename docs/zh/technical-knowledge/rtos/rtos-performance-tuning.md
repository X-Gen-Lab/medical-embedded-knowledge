---
title: RTOS性能调优
description: 实时操作系统性能优化技术，包括任务优化、内存管理、中断处理和调度策略调优
difficulty: 高级
estimated_time: 4小时
tags:
- RTOS
- 性能优化
- 实时系统
- 调优
related_modules:
- zh/technical-knowledge/rtos/task-scheduling
- zh/technical-knowledge/rtos/interrupt-handling
- zh/technical-knowledge/embedded-c-cpp/compiler-optimization
last_updated: '2026-02-10'
version: '1.0'
language: zh-CN
---

# RTOS性能调优

## 前置知识

在学习本文档之前，建议你已经掌握：

- RTOS基础概念
- 嵌入式系统开发经验
- C/C++编程基础


## 学习目标

完成本模块后，你将能够：
- 识别RTOS性能瓶颈
- 优化任务调度和优先级配置
- 改善内存使用效率
- 优化中断处理性能
- 使用性能分析工具

---

## 内容

### 性能分析基础

#### 关键性能指标

**时间指标**：
- **任务切换时间**：上下文切换的开销
- **中断延迟**：从中断发生到ISR执行
- **响应时间**：从事件发生到任务响应
- **CPU利用率**：处理器忙碌时间占比

**资源指标**：
- **内存使用**：RAM和Flash占用
- **栈使用**：各任务栈的峰值使用
- **队列占用**：消息队列的使用情况

#### 性能测量方法

**GPIO翻转法**：

```c
// 测量任务切换时间
void vHighPriorityTask(void *pvParameters) {
    for(;;) {
        GPIO_SetBits(GPIOA, GPIO_Pin_0);  // 置高
        vTaskDelay(1);
        GPIO_ResetBits(GPIOA, GPIO_Pin_0); // 置低
        vTaskDelay(1);
    }
}
```

**时间戳法**：

```c
#include "FreeRTOS.h"
#include "task.h"

// 使用DWT周期计数器（Cortex-M）
static inline void enable_cycle_counter(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

static inline uint32_t get_cycle_count(void) {
    return DWT->CYCCNT;
}

// 测量函数执行时间
void measure_function_time(void) {
    uint32_t start, end, cycles;
    
    start = get_cycle_count();
    
    // 被测函数
    process_ecg_sample();
    
    end = get_cycle_count();
    cycles = end - start;
    
    // 转换为微秒（假设72MHz时钟）
    uint32_t us = cycles / 72;
    printf("Execution time: %lu us\n", us);
}
```

**RTOS统计功能**：

```c
// FreeRTOS运行时统计
#define configGENERATE_RUN_TIME_STATS 1
#define configUSE_TRACE_FACILITY 1
#define configUSE_STATS_FORMATTING_FUNCTIONS 1

void print_task_stats(void) {
    char buffer[512];
    vTaskGetRunTimeStats(buffer);
    printf("Task Statistics:\n%s\n", buffer);
}

// 输出示例：
// Task            Abs Time        % Time
// ------------------------------------------------
// IDLE            123456          50%
// ECG_Task        98765           40%
// Display_Task    24691           10%
```

---

### 任务优化

#### 优先级配置优化

**原则**：
1. 高频率、短执行时间的任务优先级高
2. 低频率、长执行时间的任务优先级低
3. 避免优先级反转

**示例：医疗监护系统**：

```c
// 优先级定义（数字越大优先级越高）
#define PRIORITY_CRITICAL_ALARM    7  // 最高：生命危险报警
#define PRIORITY_ECG_ACQUISITION   6  // 高：ECG数据采集（500Hz）
#define PRIORITY_SPO2_ACQUISITION  5  // 高：SpO2数据采集（100Hz）
#define PRIORITY_DATA_PROCESSING   4  // 中：信号处理
#define PRIORITY_DISPLAY_UPDATE    3  // 中：显示更新（30Hz）
#define PRIORITY_DATA_STORAGE      2  // 低：数据存储
#define PRIORITY_COMMUNICATION     1  // 低：网络通信

// 创建任务
xTaskCreate(vCriticalAlarmTask, "Alarm", 256, NULL, 
            PRIORITY_CRITICAL_ALARM, NULL);
xTaskCreate(vECGAcquisitionTask, "ECG", 512, NULL, 
            PRIORITY_ECG_ACQUISITION, NULL);
xTaskCreate(vSpO2AcquisitionTask, "SpO2", 512, NULL, 
            PRIORITY_SPO2_ACQUISITION, NULL);
```

#### 任务栈大小优化

**栈使用分析**：

```c
// 启用栈溢出检测
#define configCHECK_FOR_STACK_OVERFLOW 2

// 栈溢出钩子函数
void vApplicationStackOverflowHook(TaskHandle_t xTask, char *pcTaskName) {
    // 记录错误
    log_error("Stack overflow in task: %s", pcTaskName);
    
    // 进入安全状态
    enter_safe_state();
}

// 检查栈使用情况
void check_stack_usage(void) {
    TaskHandle_t xHandle = xTaskGetHandle("ECG");
    UBaseType_t uxHighWaterMark = uxTaskGetStackHighWaterMark(xHandle);
    
    printf("ECG task stack remaining: %u words\n", uxHighWaterMark);
    
    // 如果剩余空间<20%，增加栈大小
    if (uxHighWaterMark < (STACK_SIZE * 0.2)) {
        printf("WARNING: Stack usage too high!\n");
    }
}
```

**栈大小配置建议**：

```c
// 根据任务复杂度配置栈大小
#define STACK_SIZE_SIMPLE    128   // 简单任务（LED闪烁）
#define STACK_SIZE_NORMAL    256   // 普通任务（数据采集）
#define STACK_SIZE_COMPLEX   512   // 复杂任务（信号处理）
#define STACK_SIZE_HEAVY     1024  // 重型任务（FFT计算）

// 考虑中断嵌套深度
// 栈大小 = 任务使用 + 中断使用 + 安全余量(20%)
```

#### 任务执行时间优化

**避免长时间阻塞**：

```c
// ❌ 不好的做法：长时间阻塞
void vBadTask(void *pvParameters) {
    for(;;) {
        // 处理1000个样本，可能需要100ms
        for(int i = 0; i < 1000; i++) {
            process_sample(i);
        }
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// ✅ 好的做法：分批处理
void vGoodTask(void *pvParameters) {
    static int index = 0;
    
    for(;;) {
        // 每次只处理10个样本，约1ms
        for(int i = 0; i < 10; i++) {
            process_sample(index++);
            if(index >= 1000) index = 0;
        }
        vTaskDelay(pdMS_TO_TICKS(1));
    }
}
```

**使用零拷贝技术**：

```c
// ❌ 不好的做法：数据拷贝
void vDataProcessTask(void *pvParameters) {
    uint8_t buffer[512];
    
    for(;;) {
        // 从队列接收数据（拷贝）
        xQueueReceive(xDataQueue, buffer, portMAX_DELAY);
        
        // 处理数据
        process_data(buffer, 512);
    }
}

// ✅ 好的做法：传递指针
void vDataProcessTask(void *pvParameters) {
    uint8_t *pBuffer;
    
    for(;;) {
        // 从队列接收指针（无拷贝）
        xQueueReceive(xDataQueue, &pBuffer, portMAX_DELAY);
        
        // 处理数据
        process_data(pBuffer, 512);
        
        // 释放缓冲区
        release_buffer(pBuffer);
    }
}
```

---

### 调度器优化

#### 时间片配置

```c
// FreeRTOSConfig.h

// 启用时间片轮转
#define configUSE_TIME_SLICING 1

// 配置时钟节拍频率
// 更高的频率 = 更好的响应性，但更高的开销
#define configTICK_RATE_HZ 1000  // 1ms节拍（推荐）

// 对于低功耗应用，可以降低频率
// #define configTICK_RATE_HZ 100  // 10ms节拍
```

#### 空闲任务优化

```c
// 空闲任务钩子函数
void vApplicationIdleHook(void) {
    // 在空闲时进入低功耗模式
    __WFI();  // Wait For Interrupt
    
    // 或执行后台任务
    // background_task();
}

// 配置空闲任务栈大小
#define configMINIMAL_STACK_SIZE 128

// 如果空闲任务钩子函数复杂，增加栈大小
// #define configMINIMAL_STACK_SIZE 256
```

#### 调度策略选择

```c
// 抢占式调度（推荐用于医疗设备）
#define configUSE_PREEMPTION 1

// 协作式调度（仅用于简单应用）
// #define configUSE_PREEMPTION 0

// 时间片轮转（相同优先级任务）
#define configUSE_TIME_SLICING 1
```

---

### 内存优化

#### 动态内存管理

**FreeRTOS内存方案选择**：

```c
// heap_1.c - 最简单，只分配不释放
// 优点：快速、确定性
// 缺点：无法释放内存
// 适用：静态任务创建

// heap_2.c - 可分配和释放，但不合并碎片
// 优点：快速
// 缺点：可能产生碎片
// 适用：固定大小分配

// heap_3.c - 使用标准库malloc/free
// 优点：功能完整
// 缺点：非确定性，可能不适合实时系统
// 适用：非关键应用

// heap_4.c - 可合并相邻空闲块（推荐）
// 优点：减少碎片，确定性
// 缺点：稍慢
// 适用：大多数医疗设备

// heap_5.c - 支持多个不连续内存区域
// 优点：灵活
// 缺点：配置复杂
// 适用：复杂内存布局
```

**配置heap_4**：

```c
// FreeRTOSConfig.h
#define configTOTAL_HEAP_SIZE ((size_t)(20 * 1024))  // 20KB堆

// 监控堆使用
void monitor_heap_usage(void) {
    size_t free_heap = xPortGetFreeHeapSize();
    size_t min_free_heap = xPortGetMinimumEverFreeHeapSize();
    
    printf("Current free heap: %u bytes\n", free_heap);
    printf("Minimum free heap: %u bytes\n", min_free_heap);
    
    // 如果最小剩余堆<20%，需要增加堆大小
    if (min_free_heap < (configTOTAL_HEAP_SIZE * 0.2)) {
        printf("WARNING: Heap usage too high!\n");
    }
}
```

#### 静态内存分配

**静态任务创建**（推荐用于医疗设备）：

```c
// 启用静态分配
#define configSUPPORT_STATIC_ALLOCATION 1

// 静态任务缓冲区
static StaticTask_t xECGTaskBuffer;
static StackType_t xECGStack[512];

// 静态创建任务
TaskHandle_t xECGHandle = xTaskCreateStatic(
    vECGTask,           // 任务函数
    "ECG",              // 任务名称
    512,                // 栈大小
    NULL,               // 参数
    5,                  // 优先级
    xECGStack,          // 栈缓冲区
    &xECGTaskBuffer     // 任务缓冲区
);

// 静态队列
static StaticQueue_t xQueueBuffer;
static uint8_t ucQueueStorage[10 * sizeof(uint32_t)];

QueueHandle_t xQueue = xQueueCreateStatic(
    10,                 // 队列长度
    sizeof(uint32_t),   // 项目大小
    ucQueueStorage,     // 存储区
    &xQueueBuffer       // 队列缓冲区
);
```

**优势**：
- ✅ 编译时确定内存使用
- ✅ 无内存碎片风险
- ✅ 符合MISRA C规则
- ✅ 更容易通过认证

#### 内存池技术

```c
// 固定大小内存池
#define POOL_BLOCK_SIZE 128
#define POOL_BLOCK_COUNT 10

typedef struct {
    uint8_t data[POOL_BLOCK_SIZE];
    bool in_use;
} MemoryBlock_t;

static MemoryBlock_t memory_pool[POOL_BLOCK_COUNT];
static SemaphoreHandle_t xPoolMutex;

// 初始化内存池
void init_memory_pool(void) {
    xPoolMutex = xSemaphoreCreateMutex();
    
    for(int i = 0; i < POOL_BLOCK_COUNT; i++) {
        memory_pool[i].in_use = false;
    }
}

// 分配块
void* allocate_block(void) {
    void* ptr = NULL;
    
    xSemaphoreTake(xPoolMutex, portMAX_DELAY);
    
    for(int i = 0; i < POOL_BLOCK_COUNT; i++) {
        if(!memory_pool[i].in_use) {
            memory_pool[i].in_use = true;
            ptr = memory_pool[i].data;
            break;
        }
    }
    
    xSemaphoreGive(xPoolMutex);
    
    return ptr;
}

// 释放块
void free_block(void* ptr) {
    xSemaphoreTake(xPoolMutex, portMAX_DELAY);
    
    for(int i = 0; i < POOL_BLOCK_COUNT; i++) {
        if(memory_pool[i].data == ptr) {
            memory_pool[i].in_use = false;
            break;
        }
    }
    
    xSemaphoreGive(xPoolMutex);
}
```

---

### 中断优化

#### 中断优先级配置

```c
// ARM Cortex-M中断优先级配置
// 数字越小优先级越高

// 定义中断优先级
#define IRQ_PRIORITY_CRITICAL  0  // 最高：关键传感器
#define IRQ_PRIORITY_HIGH      1  // 高：数据采集
#define IRQ_PRIORITY_MEDIUM    2  // 中：通信
#define IRQ_PRIORITY_LOW       3  // 低：非关键外设

// FreeRTOS中断优先级配置
// 优先级 >= configMAX_SYSCALL_INTERRUPT_PRIORITY 的中断
// 不能调用FreeRTOS API
#define configMAX_SYSCALL_INTERRUPT_PRIORITY 5

// 配置中断优先级
void configure_interrupts(void) {
    // ADC中断（ECG采集）- 高优先级
    NVIC_SetPriority(ADC_IRQn, IRQ_PRIORITY_HIGH);
    
    // UART中断 - 中优先级
    NVIC_SetPriority(USART1_IRQn, IRQ_PRIORITY_MEDIUM);
    
    // 定时器中断 - 低优先级
    NVIC_SetPriority(TIM2_IRQn, IRQ_PRIORITY_LOW);
}
```

#### 中断服务程序优化

**最小化ISR执行时间**：

```c
// ❌ 不好的做法：在ISR中处理数据
void ADC_IRQHandler(void) {
    uint16_t adc_value = ADC1->DR;
    
    // 复杂处理（不应在ISR中）
    float voltage = adc_value * 3.3 / 4096.0;
    float filtered = apply_filter(voltage);
    update_display(filtered);
    
    ADC_ClearITPendingBit(ADC1, ADC_IT_EOC);
}

// ✅ 好的做法：ISR只读取数据，延迟处理
static QueueHandle_t xADCQueue;

void ADC_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    
    // 快速读取数据
    uint16_t adc_value = ADC1->DR;
    
    // 发送到队列（从ISR）
    xQueueSendFromISR(xADCQueue, &adc_value, &xHigherPriorityTaskWoken);
    
    // 清除中断标志
    ADC_ClearITPendingBit(ADC1, ADC_IT_EOC);
    
    // 如果需要，触发任务切换
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 在任务中处理数据
void vADCProcessTask(void *pvParameters) {
    uint16_t adc_value;
    
    for(;;) {
        if(xQueueReceive(xADCQueue, &adc_value, portMAX_DELAY)) {
            // 在任务上下文中处理
            float voltage = adc_value * 3.3 / 4096.0;
            float filtered = apply_filter(voltage);
            update_display(filtered);
        }
    }
}
```

#### 使用DMA减少中断负担

```c
// 配置DMA进行ADC数据传输
#define ADC_BUFFER_SIZE 100
static uint16_t adc_buffer[ADC_BUFFER_SIZE];

void configure_adc_dma(void) {
    // 配置DMA
    DMA_InitTypeDef DMA_InitStructure;
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)&ADC1->DR;
    DMA_InitStructure.DMA_MemoryBaseAddr = (uint32_t)adc_buffer;
    DMA_InitStructure.DMA_DIR = DMA_DIR_PeripheralSRC;
    DMA_InitStructure.DMA_BufferSize = ADC_BUFFER_SIZE;
    DMA_InitStructure.DMA_PeripheralInc = DMA_PeripheralInc_Disable;
    DMA_InitStructure.DMA_MemoryInc = DMA_MemoryInc_Enable;
    DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_HalfWord;
    DMA_InitStructure.DMA_MemoryDataSize = DMA_MemoryDataSize_HalfWord;
    DMA_InitStructure.DMA_Mode = DMA_Mode_Circular;
    DMA_InitStructure.DMA_Priority = DMA_Priority_High;
    DMA_Init(DMA1_Channel1, &DMA_InitStructure);
    
    // 启用DMA传输完成中断
    DMA_ITConfig(DMA1_Channel1, DMA_IT_TC, ENABLE);
    
    // 启动DMA
    DMA_Cmd(DMA1_Channel1, ENABLE);
}

// DMA传输完成中断（频率降低100倍）
void DMA1_Channel1_IRQHandler(void) {
    if(DMA_GetITStatus(DMA1_IT_TC1)) {
        // 通知任务处理缓冲区
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xTaskNotifyFromISR(xProcessTaskHandle, 0, eNoAction, 
                          &xHigherPriorityTaskWoken);
        
        DMA_ClearITPendingBit(DMA1_IT_TC1);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}
```

---

### 同步机制优化

#### 选择合适的同步原语

```c
// 互斥锁 vs 二值信号量

// ✅ 使用互斥锁保护共享资源（支持优先级继承）
SemaphoreHandle_t xResourceMutex = xSemaphoreCreateMutex();

void access_shared_resource(void) {
    xSemaphoreTake(xResourceMutex, portMAX_DELAY);
    // 访问共享资源
    shared_resource++;
    xSemaphoreGive(xResourceMutex);
}

// ✅ 使用二值信号量进行任务同步
SemaphoreHandle_t xSyncSemaphore = xSemaphoreCreateBinary();

// ISR中释放信号量
void SENSOR_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(xSyncSemaphore, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// 任务中等待信号量
void vSensorTask(void *pvParameters) {
    for(;;) {
        xSemaphoreTake(xSyncSemaphore, portMAX_DELAY);
        process_sensor_data();
    }
}
```

#### 使用任务通知替代信号量

```c
// 任务通知比信号量更快、更节省内存

// ❌ 使用信号量（较慢）
SemaphoreHandle_t xSemaphore = xSemaphoreCreateBinary();

void ISR_Handler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    xSemaphoreGiveFromISR(xSemaphore, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

// ✅ 使用任务通知（更快）
TaskHandle_t xTaskToNotify;

void ISR_Handler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    vTaskNotifyGiveFromISR(xTaskToNotify, &xHigherPriorityTaskWoken);
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

void vTask(void *pvParameters) {
    for(;;) {
        // 等待通知
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        process_data();
    }
}
```

---

### 性能分析工具

#### FreeRTOS+Trace

**配置**：

```c
// FreeRTOSConfig.h
#define configUSE_TRACE_FACILITY 1
#define INCLUDE_xTaskGetIdleTaskHandle 1

// 使用Percepio Tracealyzer
#include "trcRecorder.h"

void main(void) {
    // 初始化跟踪
    vTraceEnable(TRC_START);
    
    // 创建任务...
    
    vTaskStartScheduler();
}
```

**分析内容**：
- 任务执行时间线
- CPU利用率
- 任务切换频率
- 阻塞时间分析
- 中断活动

#### SystemView (SEGGER)

```c
#include "SEGGER_SYSVIEW.h"

void main(void) {
    // 初始化SystemView
    SEGGER_SYSVIEW_Conf();
    SEGGER_SYSVIEW_Start();
    
    // 应用代码...
}

// 自定义事件标记
void process_ecg_data(void) {
    SEGGER_SYSVIEW_RecordEnterISR();
    
    // ECG处理代码
    
    SEGGER_SYSVIEW_RecordExitISR();
}
```

#### 自定义性能监控

```c
// 简单的性能监控系统
typedef struct {
    const char* name;
    uint32_t count;
    uint32_t total_time;
    uint32_t max_time;
    uint32_t min_time;
} PerfCounter_t;

#define MAX_COUNTERS 10
static PerfCounter_t perf_counters[MAX_COUNTERS];
static int counter_index = 0;

// 注册性能计数器
int register_perf_counter(const char* name) {
    if(counter_index >= MAX_COUNTERS) return -1;
    
    perf_counters[counter_index].name = name;
    perf_counters[counter_index].count = 0;
    perf_counters[counter_index].total_time = 0;
    perf_counters[counter_index].max_time = 0;
    perf_counters[counter_index].min_time = UINT32_MAX;
    
    return counter_index++;
}

// 测量函数执行时间
void measure_function(int counter_id, void (*func)(void)) {
    uint32_t start = get_cycle_count();
    
    func();
    
    uint32_t end = get_cycle_count();
    uint32_t elapsed = end - start;
    
    perf_counters[counter_id].count++;
    perf_counters[counter_id].total_time += elapsed;
    
    if(elapsed > perf_counters[counter_id].max_time) {
        perf_counters[counter_id].max_time = elapsed;
    }
    if(elapsed < perf_counters[counter_id].min_time) {
        perf_counters[counter_id].min_time = elapsed;
    }
}

// 打印性能报告
void print_perf_report(void) {
    printf("\nPerformance Report:\n");
    printf("%-20s %10s %10s %10s %10s\n", 
           "Function", "Count", "Avg(us)", "Max(us)", "Min(us)");
    printf("------------------------------------------------------------\n");
    
    for(int i = 0; i < counter_index; i++) {
        uint32_t avg = perf_counters[i].total_time / perf_counters[i].count;
        printf("%-20s %10lu %10lu %10lu %10lu\n",
               perf_counters[i].name,
               perf_counters[i].count,
               avg / 72,  // 转换为微秒（72MHz）
               perf_counters[i].max_time / 72,
               perf_counters[i].min_time / 72);
    }
}
```

---

### 实际优化案例

#### 案例1：ECG监护系统优化

**问题**：ECG数据采集任务偶尔丢失样本

**分析**：
```c
// 原始实现
void vECGTask(void *pvParameters) {
    for(;;) {
        uint16_t sample = read_adc();
        
        // 复杂的滤波处理（耗时5ms）
        float filtered = apply_bandpass_filter(sample);
        filtered = apply_notch_filter(filtered);
        filtered = apply_baseline_correction(filtered);
        
        store_sample(filtered);
        
        vTaskDelay(pdMS_TO_TICKS(2)); // 500Hz采样
    }
}
```

**问题**：处理时间(5ms) > 采样周期(2ms)，导致丢失样本

**优化方案**：

```c
// 优化后：分离采集和处理

// 高优先级采集任务
void vECGAcquisitionTask(void *pvParameters) {
    for(;;) {
        uint16_t sample = read_adc();
        
        // 快速存入队列
        xQueueSend(xECGQueue, &sample, 0);
        
        vTaskDelay(pdMS_TO_TICKS(2)); // 500Hz采样
    }
}

// 低优先级处理任务
void vECGProcessTask(void *pvParameters) {
    uint16_t sample;
    
    for(;;) {
        if(xQueueReceive(xECGQueue, &sample, portMAX_DELAY)) {
            // 批量处理多个样本
            float filtered = apply_bandpass_filter(sample);
            filtered = apply_notch_filter(filtered);
            filtered = apply_baseline_correction(filtered);
            
            store_sample(filtered);
        }
    }
}
```

**结果**：
- ✅ 采集任务执行时间 < 100μs
- ✅ 无样本丢失
- ✅ CPU利用率从95%降至60%

#### 案例2：内存碎片问题

**问题**：系统运行数小时后内存分配失败

**分析**：
```c
// 原始实现：频繁分配/释放不同大小的内存
void process_data(void) {
    uint8_t *buffer = pvPortMalloc(data_size);  // 大小可变
    
    // 处理数据
    
    vPortFree(buffer);
}
```

**优化方案**：

```c
// 使用固定大小内存池
#define BUFFER_SIZE 512
#define POOL_SIZE 10

static uint8_t buffer_pool[POOL_SIZE][BUFFER_SIZE];
static bool buffer_used[POOL_SIZE];
static SemaphoreHandle_t xPoolMutex;

void init_buffer_pool(void) {
    xPoolMutex = xSemaphoreCreateMutex();
    memset(buffer_used, 0, sizeof(buffer_used));
}

uint8_t* allocate_buffer(void) {
    uint8_t* ptr = NULL;
    
    xSemaphoreTake(xPoolMutex, portMAX_DELAY);
    
    for(int i = 0; i < POOL_SIZE; i++) {
        if(!buffer_used[i]) {
            buffer_used[i] = true;
            ptr = buffer_pool[i];
            break;
        }
    }
    
    xSemaphoreGive(xPoolMutex);
    
    return ptr;
}

void free_buffer(uint8_t* ptr) {
    xSemaphoreTake(xPoolMutex, portMAX_DELAY);
    
    for(int i = 0; i < POOL_SIZE; i++) {
        if(buffer_pool[i] == ptr) {
            buffer_used[i] = false;
            break;
        }
    }
    
    xSemaphoreGive(xPoolMutex);
}
```

**结果**：
- ✅ 无内存碎片
- ✅ 分配/释放时间确定
- ✅ 系统可长期稳定运行

---

## 性能优化清单

### 任务优化
- [ ] 合理配置任务优先级
- [ ] 优化任务栈大小（使用uxTaskGetStackHighWaterMark）
- [ ] 避免长时间阻塞任务
- [ ] 使用零拷贝技术减少数据拷贝
- [ ] 分离时间关键和非关键任务

### 调度器优化
- [ ] 选择合适的时钟节拍频率
- [ ] 配置空闲任务钩子函数
- [ ] 启用时间片轮转（如需要）
- [ ] 使用抢占式调度

### 内存优化
- [ ] 选择合适的堆管理方案
- [ ] 监控堆使用情况
- [ ] 优先使用静态内存分配
- [ ] 实现内存池减少碎片
- [ ] 检查栈溢出

### 中断优化
- [ ] 合理配置中断优先级
- [ ] 最小化ISR执行时间
- [ ] 使用DMA减少中断频率
- [ ] 使用FromISR版本的API
- [ ] 正确处理portYIELD_FROM_ISR

### 同步优化
- [ ] 选择合适的同步原语
- [ ] 使用任务通知替代信号量（如可能）
- [ ] 避免优先级反转
- [ ] 减少临界区时间
- [ ] 使用消息队列解耦任务

### 性能监控
- [ ] 启用运行时统计
- [ ] 使用性能分析工具
- [ ] 定期检查CPU利用率
- [ ] 监控任务执行时间
- [ ] 记录性能基准

---

## 实践练习

1. **性能测量**：
   - 测量你的RTOS应用的任务切换时间
   - 分析各任务的CPU占用率
   - 识别性能瓶颈

2. **内存优化**：
   - 实现一个内存池系统
   - 对比动态分配和内存池的性能
   - 监控内存碎片情况

3. **中断优化**：
   - 配置DMA进行数据传输
   - 测量中断响应延迟
   - 优化ISR执行时间

4. **综合优化**：
   - 选择一个现有项目
   - 应用本模块的优化技术
   - 测量优化前后的性能差异

---

## 相关知识模块

### 深入学习

- [任务调度](task-scheduling.md) - RTOS调度机制
- [中断处理](interrupt-handling.md) - 中断管理
- [编译器优化](../embedded-c-cpp/compiler-optimization.md) - 代码级优化

### 相关主题

- [RTOS选型指南](rtos-selection-guide.md) - 选择合适的RTOS
- [低功耗设计](../low-power-design/index.md) - 功耗优化
- [静态分析](../../software-engineering/static-analysis/index.md) - 代码质量

---

## 参考文献

1. "Mastering the FreeRTOS Real Time Kernel" - Richard Barry
2. "Real-Time Systems Design and Analysis" - Phillip A. Laplante
3. "The Definitive Guide to ARM Cortex-M3 and Cortex-M4 Processors" - Joseph Yiu
4. FreeRTOS官方文档 - https://www.freertos.org/
5. "Embedded Systems Architecture" - Daniele Lacamera
6. ARM Cortex-M Programming Guide - ARM Ltd.

---

## 总结

RTOS性能优化是一个系统工程，需要从任务、调度、内存、中断等多个维度进行。关键是：

1. **测量先于优化**：使用工具量化性能问题
2. **优化关键路径**：专注于影响最大的部分
3. **保持确定性**：医疗设备需要可预测的行为
4. **持续监控**：建立性能基准和监控机制

记住：过早优化是万恶之源，但医疗设备的实时性和可靠性要求我们必须重视性能。
