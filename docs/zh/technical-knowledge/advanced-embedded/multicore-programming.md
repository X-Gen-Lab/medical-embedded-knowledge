---
title: 多核处理器编程
description: "学习多核处理器编程技术，实现医疗设备的并行处理和性能优化"
difficulty: 高级
estimated_time: 3-4小时
last_updated: "2026-02-11"
version: "1.0"
language: "zh-CN"
tags:
  - multicore
  - parallel-processing
  - performance
  - embedded-systems
---

# 多核处理器编程

## 学习目标

通过本文档的学习，你将能够：

- 理解核心概念和原理
- 掌握实际应用方法
- 了解最佳实践和注意事项

## 前置知识

在学习本文档之前，建议你已经掌握：

- 基础的嵌入式系统知识
- C/C++编程基础
- 相关领域的基本概念

## 概述

多核处理器在现代医疗设备中越来越普遍，能够实现并行处理、提高性能并降低功耗。本文档介绍医疗设备开发中的多核编程技术。

## 🎯 学习目标

- 理解SMP和AMP架构差异
- 掌握核间通信机制
- 实现负载均衡策略
- 确保多核系统的安全性和可靠性

## 多核架构类型

### 1. 对称多处理（SMP - Symmetric Multi-Processing）

**特点**:
- 所有核心共享相同的内存空间
- 运行相同的操作系统实例
- 任务可以在任意核心上运行
- 操作系统负责调度和负载均衡

**优势**:
- 编程模型简单
- 动态负载均衡
- 资源利用率高
- 易于扩展

**劣势**:
- 缓存一致性开销
- 同步复杂度高
- 实时性保证困难

**医疗设备应用场景**:
```c
// SMP架构示例 - 多核心并行处理ECG信号
typedef struct {
    uint32_t core_id;
    ecg_channel_t *channels;
    uint32_t num_channels;
} ecg_processing_task_t;

// 在SMP系统中，任务可以在任意核心上运行
void ecg_parallel_processing(void) {
    // 创建多个处理任务
    for (int i = 0; i < NUM_CORES; i++) {
        ecg_processing_task_t *task = create_task(i);
        // 操作系统自动分配到可用核心
        os_task_create(ecg_process_task, task, PRIORITY_HIGH);
    }
}

void ecg_process_task(void *param) {
    ecg_processing_task_t *task = (ecg_processing_task_t *)param;
    
    while (1) {
        // 处理分配的ECG通道
        for (uint32_t ch = 0; ch < task->num_channels; ch++) {
            process_ecg_channel(&task->channels[ch]);
        }
        
        // 同步点 - 等待所有核心完成
        barrier_wait(&processing_barrier);
    }
}
```

### 2. 非对称多处理（AMP - Asymmetric Multi-Processing）

**特点**:
- 每个核心运行独立的软件
- 可以运行不同的操作系统或裸机代码
- 明确的任务分配
- 独立的内存区域（可选共享内存）

**优势**:
- 确定性实时性能
- 隔离性好，故障不会传播
- 功耗优化灵活
- 适合混合关键级别系统

**劣势**:
- 编程复杂度高
- 需要手动负载均衡
- 核间通信需要显式设计

**医疗设备应用场景**:
```c
// AMP架构示例 - 核心0运行RTOS，核心1运行裸机实时处理
// 核心0: 主控制器（运行FreeRTOS）
void core0_main(void) {
    // 初始化RTOS
    rtos_init();
    
    // 启动核心1
    start_core1(core1_realtime_main);
    
    // 创建控制任务
    xTaskCreate(ui_task, "UI", STACK_SIZE, NULL, PRIORITY_LOW, NULL);
    xTaskCreate(communication_task, "COMM", STACK_SIZE, NULL, PRIORITY_MED, NULL);
    xTaskCreate(data_logging_task, "LOG", STACK_SIZE, NULL, PRIORITY_LOW, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
}

// 核心1: 实时信号处理（裸机）
void core1_realtime_main(void) {
    // 配置高优先级中断
    configure_adc_interrupt(PRIORITY_HIGHEST);
    
    while (1) {
        // 等待ADC数据就绪
        wait_for_adc_interrupt();
        
        // 实时处理（无OS开销）
        uint32_t sample = read_adc_sample();
        float filtered = apply_filter(sample);
        
        // 通过共享内存发送到核心0
        write_to_shared_buffer(filtered);
        notify_core0();
    }
}
```

## 核间通信（Inter-Core Communication）

### 1. 共享内存

**实现方式**:
```c
// 共享内存区域定义
#define SHARED_MEM_BASE 0x20000000
#define SHARED_MEM_SIZE 0x10000

typedef struct {
    volatile uint32_t write_index;
    volatile uint32_t read_index;
    volatile uint32_t data[BUFFER_SIZE];
    volatile uint32_t flags;
} shared_buffer_t;

// 放置在共享内存区域
__attribute__((section(".shared_mem")))
shared_buffer_t shared_buffer;

// 核心0: 写入数据
void core0_write_data(uint32_t value) {
    uint32_t next_write = (shared_buffer.write_index + 1) % BUFFER_SIZE;
    
    // 检查缓冲区是否已满
    if (next_write != shared_buffer.read_index) {
        shared_buffer.data[shared_buffer.write_index] = value;
        
        // 内存屏障确保写入顺序
        __DMB();
        
        shared_buffer.write_index = next_write;
        
        // 通知核心1
        trigger_core1_interrupt();
    }
}

// 核心1: 读取数据
uint32_t core1_read_data(void) {
    if (shared_buffer.read_index != shared_buffer.write_index) {
        uint32_t value = shared_buffer.data[shared_buffer.read_index];
        
        // 内存屏障
        __DMB();
        
        shared_buffer.read_index = (shared_buffer.read_index + 1) % BUFFER_SIZE;
        return value;
    }
    return 0;
}
```

### 2. 消息传递

**基于邮箱的实现**:
```c
// 硬件邮箱寄存器
#define MAILBOX_CORE0_TO_CORE1  ((volatile uint32_t *)0x40000000)
#define MAILBOX_CORE1_TO_CORE0  ((volatile uint32_t *)0x40000004)
#define MAILBOX_STATUS          ((volatile uint32_t *)0x40000008)

typedef enum {
    MSG_TYPE_DATA_READY = 1,
    MSG_TYPE_ALARM = 2,
    MSG_TYPE_COMMAND = 3,
    MSG_TYPE_ACK = 4
} message_type_t;

typedef struct {
    message_type_t type;
    uint32_t payload;
    uint32_t timestamp;
} icc_message_t;

// 发送消息
bool send_message_to_core1(icc_message_t *msg) {
    // 等待邮箱空闲
    while (*MAILBOX_STATUS & MAILBOX_FULL);
    
    // 写入消息指针
    *MAILBOX_CORE0_TO_CORE1 = (uint32_t)msg;
    
    // 触发核心1中断
    trigger_mailbox_interrupt(CORE1);
    
    return true;
}

// 接收消息（在中断处理程序中）
void mailbox_interrupt_handler(void) {
    // 读取消息指针
    icc_message_t *msg = (icc_message_t *)(*MAILBOX_CORE1_TO_CORE0);
    
    // 处理消息
    switch (msg->type) {
        case MSG_TYPE_DATA_READY:
            process_data(msg->payload);
            break;
        case MSG_TYPE_ALARM:
            handle_alarm(msg->payload);
            break;
        case MSG_TYPE_COMMAND:
            execute_command(msg->payload);
            break;
    }
    
    // 清除中断标志
    clear_mailbox_interrupt();
}
```

### 3. 信号量和互斥锁

**硬件信号量实现**:
```c
// 硬件信号量寄存器
#define HW_SEM_BASE 0x50000000
#define HW_SEM(n) ((volatile uint32_t *)(HW_SEM_BASE + (n) * 4))

// 获取硬件信号量
bool hw_semaphore_take(uint32_t sem_id, uint32_t timeout_ms) {
    uint32_t start_time = get_tick_count();
    
    while (1) {
        // 尝试获取信号量（原子操作）
        if (*HW_SEM(sem_id) == 0) {
            return true;  // 成功获取
        }
        
        // 检查超时
        if ((get_tick_count() - start_time) > timeout_ms) {
            return false;
        }
        
        // 短暂等待
        __WFE();  // Wait For Event
    }
}

// 释放硬件信号量
void hw_semaphore_give(uint32_t sem_id) {
    *HW_SEM(sem_id) = 0;
    __SEV();  // Send Event to wake up waiting cores
}

// 使用示例：保护共享资源
void access_shared_resource(void) {
    if (hw_semaphore_take(SEM_SHARED_RESOURCE, 100)) {
        // 临界区
        modify_shared_data();
        
        // 释放信号量
        hw_semaphore_give(SEM_SHARED_RESOURCE);
    } else {
        // 超时处理
        log_error("Failed to acquire semaphore");
    }
}
```

## 负载均衡策略

### 1. 静态任务分配（AMP）

**按功能分配**:
```c
// 医疗监护仪的多核任务分配
typedef enum {
    CORE_0 = 0,  // 主控制核心
    CORE_1 = 1,  // 信号处理核心
    CORE_2 = 2,  // 通信核心
    CORE_3 = 3   // 显示核心
} core_assignment_t;

// 核心0: 系统控制和协调
void core0_tasks(void) {
    // 系统初始化
    system_init();
    
    // 启动其他核心
    start_core(CORE_1, signal_processing_main);
    start_core(CORE_2, communication_main);
    start_core(CORE_3, display_main);
    
    // 主控制循环
    while (1) {
        monitor_system_health();
        handle_user_input();
        coordinate_cores();
        check_alarms();
    }
}

// 核心1: 实时信号处理
void signal_processing_main(void) {
    init_signal_processing();
    
    while (1) {
        // ECG信号处理
        process_ecg_signals();
        
        // SpO2信号处理
        process_spo2_signals();
        
        // NIBP信号处理
        process_nibp_signals();
        
        // 发送结果到核心0
        send_results_to_core0();
    }
}

// 核心2: 网络通信
void communication_main(void) {
    init_network_stack();
    
    while (1) {
        handle_network_packets();
        process_hl7_messages();
        sync_with_ehr_system();
        handle_remote_monitoring();
    }
}

// 核心3: 用户界面
void display_main(void) {
    init_graphics_engine();
    
    while (1) {
        update_waveforms();
        render_vital_signs();
        handle_touch_input();
        update_display();
    }
}
```

### 2. 动态负载均衡（SMP）

**工作窃取算法**:
```c
// 每个核心的任务队列
typedef struct {
    task_t *tasks[MAX_TASKS];
    volatile uint32_t head;
    volatile uint32_t tail;
    spinlock_t lock;
} task_queue_t;

task_queue_t core_queues[NUM_CORES];

// 添加任务到最空闲的核心
void schedule_task(task_t *task) {
    uint32_t min_load = UINT32_MAX;
    uint32_t target_core = 0;
    
    // 找到负载最小的核心
    for (uint32_t i = 0; i < NUM_CORES; i++) {
        uint32_t load = get_queue_size(&core_queues[i]);
        if (load < min_load) {
            min_load = load;
            target_core = i;
        }
    }
    
    // 添加到目标核心队列
    enqueue_task(&core_queues[target_core], task);
}

// 工作窃取：当核心空闲时从其他核心窃取任务
task_t* steal_task(uint32_t current_core) {
    // 尝试从其他核心窃取任务
    for (uint32_t i = 0; i < NUM_CORES; i++) {
        if (i == current_core) continue;
        
        task_queue_t *queue = &core_queues[i];
        
        // 如果队列有多个任务，窃取一个
        if (get_queue_size(queue) > 1) {
            spinlock_acquire(&queue->lock);
            task_t *task = dequeue_task_from_tail(queue);
            spinlock_release(&queue->lock);
            
            if (task) {
                return task;
            }
        }
    }
    
    return NULL;
}

// 核心工作循环
void core_worker_loop(uint32_t core_id) {
    while (1) {
        task_t *task = dequeue_task(&core_queues[core_id]);
        
        if (task) {
            // 执行任务
            execute_task(task);
        } else {
            // 队列为空，尝试窃取任务
            task = steal_task(core_id);
            
            if (task) {
                execute_task(task);
            } else {
                // 没有任务，进入低功耗模式
                __WFI();
            }
        }
    }
}
```

## 同步与并发控制

### 1. 内存屏障

**确保内存访问顺序**:
```c
// ARM Cortex-M内存屏障指令
#define DMB() __asm__ volatile ("dmb" ::: "memory")  // Data Memory Barrier
#define DSB() __asm__ volatile ("dsb" ::: "memory")  // Data Synchronization Barrier
#define ISB() __asm__ volatile ("isb" ::: "memory")  // Instruction Synchronization Barrier

// 使用示例：生产者-消费者模式
typedef struct {
    volatile uint32_t data;
    volatile bool ready;
} shared_data_t;

shared_data_t shared;

// 生产者（核心0）
void producer_write(uint32_t value) {
    shared.data = value;
    
    // 确保数据写入完成后再设置标志
    DMB();
    
    shared.ready = true;
    
    // 确保标志写入对其他核心可见
    DSB();
}

// 消费者（核心1）
uint32_t consumer_read(void) {
    while (!shared.ready) {
        __WFE();
    }
    
    // 确保读取标志后再读取数据
    DMB();
    
    uint32_t value = shared.data;
    shared.ready = false;
    
    return value;
}
```

### 2. 原子操作

**无锁编程**:
```c
// ARM Cortex-M LDREX/STREX原子操作
static inline bool atomic_compare_and_swap(volatile uint32_t *ptr, 
                                           uint32_t old_val, 
                                           uint32_t new_val) {
    uint32_t result;
    uint32_t temp;
    
    __asm__ volatile (
        "1: ldrex %0, [%2]\n"        // 独占加载
        "   cmp %0, %3\n"             // 比较
        "   bne 2f\n"                 // 不相等则跳转
        "   strex %1, %4, [%2]\n"    // 独占存储
        "   cmp %1, #0\n"             // 检查是否成功
        "   bne 1b\n"                 // 失败则重试
        "2:\n"
        : "=&r" (result), "=&r" (temp)
        : "r" (ptr), "r" (old_val), "r" (new_val)
        : "cc", "memory"
    );
    
    return (result == old_val);
}

// 无锁队列实现
typedef struct {
    volatile uint32_t head;
    volatile uint32_t tail;
    uint32_t data[QUEUE_SIZE];
} lockfree_queue_t;

bool lockfree_enqueue(lockfree_queue_t *queue, uint32_t value) {
    uint32_t tail, next_tail;
    
    do {
        tail = queue->tail;
        next_tail = (tail + 1) % QUEUE_SIZE;
        
        // 检查队列是否已满
        if (next_tail == queue->head) {
            return false;
        }
        
        queue->data[tail] = value;
        
        // 原子更新tail
    } while (!atomic_compare_and_swap(&queue->tail, tail, next_tail));
    
    return true;
}

bool lockfree_dequeue(lockfree_queue_t *queue, uint32_t *value) {
    uint32_t head, next_head;
    
    do {
        head = queue->head;
        
        // 检查队列是否为空
        if (head == queue->tail) {
            return false;
        }
        
        *value = queue->data[head];
        next_head = (head + 1) % QUEUE_SIZE;
        
        // 原子更新head
    } while (!atomic_compare_and_swap(&queue->head, head, next_head));
    
    return true;
}
```

## 缓存一致性

### 1. 缓存管理

**手动缓存操作**:
```c
// 缓存控制函数
void cache_clean_range(void *addr, uint32_t size) {
    uint32_t start = (uint32_t)addr & ~(CACHE_LINE_SIZE - 1);
    uint32_t end = ((uint32_t)addr + size + CACHE_LINE_SIZE - 1) & ~(CACHE_LINE_SIZE - 1);
    
    for (uint32_t line = start; line < end; line += CACHE_LINE_SIZE) {
        // 清除缓存行（写回到内存）
        SCB_CleanDCache_by_Addr((uint32_t *)line, CACHE_LINE_SIZE);
    }
}

void cache_invalidate_range(void *addr, uint32_t size) {
    uint32_t start = (uint32_t)addr & ~(CACHE_LINE_SIZE - 1);
    uint32_t end = ((uint32_t)addr + size + CACHE_LINE_SIZE - 1) & ~(CACHE_LINE_SIZE - 1);
    
    for (uint32_t line = start; line < end; line += CACHE_LINE_SIZE) {
        // 使缓存行无效
        SCB_InvalidateDCache_by_Addr((uint32_t *)line, CACHE_LINE_SIZE);
    }
}

// DMA传输前后的缓存管理
void dma_transfer_with_cache_management(void *src, void *dst, uint32_t size) {
    // 传输前：清除源缓存（确保数据写回内存）
    cache_clean_range(src, size);
    
    // 使目标缓存无效（避免读取旧数据）
    cache_invalidate_range(dst, size);
    
    // 启动DMA传输
    start_dma_transfer(src, dst, size);
    
    // 等待传输完成
    wait_dma_complete();
    
    // 传输后：使目标缓存无效（确保读取新数据）
    cache_invalidate_range(dst, size);
}
```

### 2. 非缓存内存区域

**配置MPU（内存保护单元）**:
```c
// 配置共享内存为非缓存区域
void configure_shared_memory_region(void) {
    // 禁用MPU
    MPU->CTRL = 0;
    
    // 配置区域0：共享内存（非缓存，可共享）
    MPU->RBAR = SHARED_MEM_BASE | MPU_REGION_VALID | 0;
    MPU->RASR = MPU_REGION_SIZE_64KB |
                MPU_REGION_FULL_ACCESS |
                MPU_SHAREABLE |
                MPU_NON_CACHEABLE |
                MPU_REGION_ENABLE;
    
    // 启用MPU
    MPU->CTRL = MPU_CTRL_ENABLE | MPU_CTRL_PRIVDEFENA;
    
    // 内存屏障
    DSB();
    ISB();
}

// 使用非缓存内存的共享数据结构
__attribute__((section(".shared_noncache")))
volatile shared_data_t shared_data;
```

## 医疗设备实例：多参数监护仪

### 系统架构

```c
// 四核处理器架构设计
typedef struct {
    // 核心0: 主控制器（Cortex-A53, 运行Linux）
    struct {
        void (*system_manager)(void);
        void (*alarm_handler)(void);
        void (*data_logger)(void);
        void (*network_manager)(void);
    } core0;
    
    // 核心1: 实时信号处理（Cortex-R5, 运行FreeRTOS）
    struct {
        void (*ecg_processor)(void);
        void (*spo2_processor)(void);
        void (*resp_processor)(void);
        void (*temp_processor)(void);
    } core1;
    
    // 核心2: 通信处理（Cortex-M7, 运行FreeRTOS）
    struct {
        void (*hl7_handler)(void);
        void (*dicom_handler)(void);
        void (*modbus_handler)(void);
        void (*mqtt_handler)(void);
    } core2;
    
    // 核心3: 显示引擎（Cortex-M7, 裸机）
    struct {
        void (*waveform_renderer)(void);
        void (*gui_updater)(void);
        void (*touch_handler)(void);
    } core3;
} multicore_system_t;
```

### 核间通信实现

```c
// 共享内存布局
typedef struct {
    // ECG数据缓冲区（核心1 -> 核心0）
    struct {
        ecg_sample_t samples[ECG_BUFFER_SIZE];
        volatile uint32_t write_idx;
        volatile uint32_t read_idx;
    } ecg_buffer;
    
    // 报警消息队列（核心1 -> 核心0）
    struct {
        alarm_message_t messages[ALARM_QUEUE_SIZE];
        volatile uint32_t head;
        volatile uint32_t tail;
    } alarm_queue;
    
    // 显示命令队列（核心0 -> 核心3）
    struct {
        display_command_t commands[CMD_QUEUE_SIZE];
        volatile uint32_t head;
        volatile uint32_t tail;
    } display_queue;
    
    // 同步标志
    volatile uint32_t sync_flags;
    
} shared_memory_layout_t;

__attribute__((section(".shared_mem")))
shared_memory_layout_t shared_mem;

// 核心1: 发送ECG数据到核心0
void core1_send_ecg_data(ecg_sample_t *sample) {
    uint32_t next_write = (shared_mem.ecg_buffer.write_idx + 1) % ECG_BUFFER_SIZE;
    
    if (next_write != shared_mem.ecg_buffer.read_idx) {
        shared_mem.ecg_buffer.samples[shared_mem.ecg_buffer.write_idx] = *sample;
        
        DMB();
        shared_mem.ecg_buffer.write_idx = next_write;
        
        // 通知核心0
        send_ipi_to_core(0, IPI_ECG_DATA_READY);
    }
}

// 核心0: 接收ECG数据
void core0_receive_ecg_data(void) {
    while (shared_mem.ecg_buffer.read_idx != shared_mem.ecg_buffer.write_idx) {
        ecg_sample_t sample = shared_mem.ecg_buffer.samples[shared_mem.ecg_buffer.read_idx];
        
        DMB();
        shared_mem.ecg_buffer.read_idx = (shared_mem.ecg_buffer.read_idx + 1) % ECG_BUFFER_SIZE;
        
        // 处理ECG数据
        process_ecg_sample(&sample);
        
        // 发送到显示核心
        send_to_display_core(&sample);
    }
}
```

## 性能优化

### 1. 减少核间通信开销

**批量传输**:
```c
// 批量传输减少通信次数
#define BATCH_SIZE 32

typedef struct {
    uint32_t count;
    ecg_sample_t samples[BATCH_SIZE];
} ecg_batch_t;

void send_ecg_batch(void) {
    static ecg_batch_t batch;
    static uint32_t batch_count = 0;
    
    // 收集样本
    batch.samples[batch_count++] = current_sample;
    
    // 达到批量大小时发送
    if (batch_count >= BATCH_SIZE) {
        batch.count = batch_count;
        send_batch_to_core0(&batch);
        batch_count = 0;
    }
}
```

### 2. 亲和性优化

**绑定任务到特定核心**:
```c
// 设置任务CPU亲和性（Linux）
void set_task_affinity(pthread_t thread, int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    
    pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
}

// 创建高优先级实时任务并绑定到核心
void create_realtime_task(void) {
    pthread_t thread;
    pthread_attr_t attr;
    struct sched_param param;
    
    pthread_attr_init(&attr);
    pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
    param.sched_priority = 99;
    pthread_attr_setschedparam(&attr, &param);
    
    pthread_create(&thread, &attr, signal_processing_task, NULL);
    
    // 绑定到核心1
    set_task_affinity(thread, 1);
}
```

### 3. 缓存优化

**数据结构对齐**:
```c
// 缓存行对齐避免伪共享
#define CACHE_LINE_SIZE 64

typedef struct {
    volatile uint32_t counter;
    uint8_t padding[CACHE_LINE_SIZE - sizeof(uint32_t)];
} __attribute__((aligned(CACHE_LINE_SIZE))) aligned_counter_t;

// 每个核心独立的计数器，避免缓存行竞争
aligned_counter_t core_counters[NUM_CORES];

void increment_core_counter(uint32_t core_id) {
    core_counters[core_id].counter++;
}
```

## 调试与测试

### 1. 多核调试技术

**JTAG多核调试配置**:
```gdb
# GDB多核调试脚本
# 连接到所有核心
target extended-remote :3333

# 附加到核心0
inferior 1
attach 1

# 附加到核心1
add-inferior
inferior 2
attach 2

# 附加到核心2
add-inferior
inferior 3
attach 3

# 设置断点
break core0_main
break core1_signal_processing
break shared_memory_write

# 查看所有核心状态
info inferiors

# 切换到特定核心
inferior 2
backtrace
```

**日志系统**:
```c
// 多核安全的日志系统
typedef struct {
    uint32_t core_id;
    uint32_t timestamp;
    log_level_t level;
    char message[LOG_MSG_SIZE];
} log_entry_t;

typedef struct {
    log_entry_t entries[LOG_BUFFER_SIZE];
    volatile uint32_t write_idx;
    spinlock_t lock;
} multicore_log_t;

multicore_log_t system_log;

void log_message(log_level_t level, const char *format, ...) {
    uint32_t core_id = get_current_core_id();
    
    spinlock_acquire(&system_log.lock);
    
    uint32_t idx = system_log.write_idx % LOG_BUFFER_SIZE;
    log_entry_t *entry = &system_log.entries[idx];
    
    entry->core_id = core_id;
    entry->timestamp = get_timestamp();
    entry->level = level;
    
    va_list args;
    va_start(args, format);
    vsnprintf(entry->message, LOG_MSG_SIZE, format, args);
    va_end(args);
    
    system_log.write_idx++;
    
    spinlock_release(&system_log.lock);
}
```

### 2. 性能分析

**核心利用率监控**:
```c
// 性能计数器
typedef struct {
    uint32_t idle_cycles;
    uint32_t busy_cycles;
    uint32_t ipc_cycles;  // 核间通信周期
    uint32_t cache_misses;
} core_perf_counters_t;

core_perf_counters_t perf_counters[NUM_CORES];

void update_performance_stats(uint32_t core_id) {
    // 读取硬件性能计数器
    uint32_t cycle_count = read_cycle_counter();
    uint32_t cache_miss_count = read_cache_miss_counter();
    
    perf_counters[core_id].busy_cycles += cycle_count;
    perf_counters[core_id].cache_misses += cache_miss_count;
}

void print_performance_report(void) {
    printf("Core Performance Report:\n");
    for (uint32_t i = 0; i < NUM_CORES; i++) {
        uint32_t total = perf_counters[i].idle_cycles + 
                        perf_counters[i].busy_cycles;
        float utilization = (float)perf_counters[i].busy_cycles / total * 100.0f;
        
        printf("Core %u: Utilization=%.2f%%, Cache Misses=%u\n",
               i, utilization, perf_counters[i].cache_misses);
    }
}
```

## 安全性考虑

### 1. 内存隔离

**MPU配置实现隔离**:
```c
// 为每个核心配置独立的内存区域
void configure_core_memory_protection(uint32_t core_id) {
    // 核心私有内存区域
    uint32_t private_base = PRIVATE_MEM_BASE + (core_id * PRIVATE_MEM_SIZE);
    
    // 配置MPU区域
    mpu_region_config_t config = {
        .base_address = private_base,
        .size = PRIVATE_MEM_SIZE,
        .access_permission = MPU_ACCESS_FULL,
        .executable = true,
        .cacheable = true,
        .shareable = false
    };
    
    configure_mpu_region(core_id, &config);
    
    // 共享内存区域（只读或读写）
    config.base_address = SHARED_MEM_BASE;
    config.size = SHARED_MEM_SIZE;
    config.shareable = true;
    
    configure_mpu_region(core_id + NUM_CORES, &config);
}
```

### 2. 故障隔离

**核心故障检测与恢复**:
```c
// 核心健康监控
typedef struct {
    volatile uint32_t heartbeat;
    volatile uint32_t error_count;
    volatile bool is_alive;
} core_health_t;

core_health_t core_health[NUM_CORES];

// 每个核心定期更新心跳
void update_heartbeat(uint32_t core_id) {
    core_health[core_id].heartbeat++;
    core_health[core_id].is_alive = true;
}

// 监控核心（在核心0上运行）
void monitor_cores(void) {
    static uint32_t last_heartbeat[NUM_CORES] = {0};
    
    for (uint32_t i = 1; i < NUM_CORES; i++) {
        if (core_health[i].heartbeat == last_heartbeat[i]) {
            // 核心无响应
            core_health[i].is_alive = false;
            handle_core_failure(i);
        }
        last_heartbeat[i] = core_health[i].heartbeat;
    }
}

void handle_core_failure(uint32_t core_id) {
    log_error("Core %u failure detected", core_id);
    
    // 尝试重启核心
    if (restart_core(core_id)) {
        log_info("Core %u restarted successfully", core_id);
    } else {
        // 进入安全状态
        enter_safe_state();
        trigger_system_alarm(ALARM_CORE_FAILURE);
    }
}
```

## 最佳实践

### 1. 设计原则

- **最小化核间通信**: 减少同步开销，提高性能
- **明确的所有权**: 每个数据结构应有明确的所有者核心
- **避免伪共享**: 使用缓存行对齐
- **使用硬件特性**: 充分利用硬件信号量、邮箱等
- **故障隔离**: 设计时考虑核心故障场景

### 2. 常见陷阱

**陷阱1: 忘记内存屏障**
```c
// 错误：可能导致数据竞争
shared_data.value = 42;
shared_data.ready = true;  // 可能在value写入前执行

// 正确：使用内存屏障
shared_data.value = 42;
__DMB();
shared_data.ready = true;
```

**陷阱2: 缓存一致性问题**
```c
// 错误：DMA传输后直接读取可能读到旧数据
start_dma_transfer(src, dst, size);
wait_dma_complete();
uint32_t value = dst[0];  // 可能读取缓存中的旧数据

// 正确：使缓存无效
start_dma_transfer(src, dst, size);
wait_dma_complete();
cache_invalidate_range(dst, size);
uint32_t value = dst[0];
```

**陷阱3: 死锁**
```c
// 错误：可能导致死锁
void core0_function() {
    lock_acquire(&lock_a);
    lock_acquire(&lock_b);  // 顺序: A -> B
    // ...
    lock_release(&lock_b);
    lock_release(&lock_a);
}

void core1_function() {
    lock_acquire(&lock_b);
    lock_acquire(&lock_a);  // 顺序: B -> A (死锁!)
    // ...
}

// 正确：统一锁获取顺序
void core0_function() {
    lock_acquire(&lock_a);
    lock_acquire(&lock_b);
    // ...
}

void core1_function() {
    lock_acquire(&lock_a);  // 相同顺序: A -> B
    lock_acquire(&lock_b);
    // ...
}
```

### 3. 性能优化清单

- [ ] 使用硬件信号量而非软件自旋锁
- [ ] 批量传输数据减少通信次数
- [ ] 数据结构缓存行对齐
- [ ] 使用无锁算法（适当场景）
- [ ] 配置非缓存共享内存区域
- [ ] 绑定关键任务到特定核心
- [ ] 监控核心利用率和负载均衡
- [ ] 优化中断分配

## 合规性要求

### IEC 62304要求

**软件架构文档**:
- 多核系统架构图
- 核间通信协议
- 任务分配策略
- 同步机制说明

**风险分析**:
- 核间通信失败
- 核心故障影响
- 数据竞争风险
- 死锁可能性

**验证测试**:
- 核间通信功能测试
- 负载均衡验证
- 故障恢复测试
- 性能基准测试

### FDA指南

**网络安全考虑**:
- 核心隔离机制
- 安全启动验证
- 故障检测与恢复
- 审计日志

## 工具与资源

### 开发工具

**调试器**:
- Lauterbach TRACE32（多核JTAG调试）
- Segger J-Link（多核支持）
- OpenOCD（开源调试器）

**性能分析**:
- ARM DS-5 Streamline
- Percepio Tracealyzer
- 自定义性能计数器

**静态分析**:
- Polyspace（多线程分析）
- Coverity（并发缺陷检测）
- LDRA（合规性验证）

### 参考资料

**技术文档**:
- ARM Cortex-A/R/M多核编程指南
- RTOS多核支持文档（FreeRTOS-SMP, Zephyr等）
- 处理器技术参考手册

**标准规范**:
- IEC 62304: 医疗设备软件生命周期
- ISO 26262: 功能安全（汽车，可参考）
- MISRA C: 嵌入式C编码标准

## 总结

多核处理器编程为医疗设备提供了强大的并行处理能力，但也带来了复杂性。关键要点：

1. **选择合适的架构**: SMP适合通用处理，AMP适合实时确定性
2. **设计高效的核间通信**: 最小化开销，确保数据一致性
3. **实现可靠的同步机制**: 使用硬件特性，避免常见陷阱
4. **优化性能**: 减少通信、优化缓存、平衡负载
5. **确保安全性**: 隔离故障、监控健康、快速恢复
6. **满足合规要求**: 文档化设计、风险分析、充分测试

通过遵循最佳实践和深入理解硬件特性，可以构建高性能、高可靠性的多核医疗设备系统。

---

**相关文档**:
- [DMA技术](dma.md)
- [看门狗与故障恢复](watchdog-recovery.md)
- [实时操作系统](../rtos/index.md)
- [RTOS任务调度](../rtos/task-scheduling.md)

**标签**: #多核处理 #SMP #AMP #核间通信 #并发控制 #性能优化 #医疗设备
