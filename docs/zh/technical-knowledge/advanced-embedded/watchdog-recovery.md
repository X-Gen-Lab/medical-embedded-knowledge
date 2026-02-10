---
title: 看门狗与故障恢复
difficulty: advanced
estimated_time: 3-4小时
---

# 看门狗与故障恢复

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

看门狗（Watchdog）是医疗设备中确保系统可靠性的关键机制。当系统出现故障或死锁时，看门狗能够检测并自动恢复系统，保证设备持续运行和患者安全。

## 🎯 学习目标

- 理解硬件和软件看门狗原理
- 实现可靠的看门狗喂狗策略
- 设计故障检测机制
- 实现安全状态转换
- 满足医疗设备安全要求

## 看门狗基础

### 1. 硬件看门狗

**工作原理**:
```c
// 硬件看门狗基本概念
// - 独立的硬件定时器
// - 需要定期"喂狗"（重置计数器）
// - 超时后自动复位系统
// - 不受软件故障影响

// STM32独立看门狗（IWDG）配置
void init_hardware_watchdog(uint32_t timeout_ms) {
    // 使能LSI时钟（32kHz）
    RCC->CSR |= RCC_CSR_LSION;
    while (!(RCC->CSR & RCC_CSR_LSIRDY));
    
    // 解锁IWDG寄存器
    IWDG->KR = 0x5555;
    
    // 配置预分频器（/32）
    IWDG->PR = IWDG_PR_PR_2;
    
    // 计算重载值
    // timeout_ms = (4 * 2^PR * RLR) / LSI_freq
    // RLR = (timeout_ms * LSI_freq) / (4 * 2^PR)
    uint32_t reload = (timeout_ms * 32) / (4 * 32);
    IWDG->RLR = reload & 0xFFF;
    
    // 等待更新完成
    while (IWDG->SR);
    
    // 启动看门狗
    IWDG->KR = 0xCCCC;
}
```

// 喂狗函数
void feed_watchdog(void) {
    IWDG->KR = 0xAAAA;  // 重载计数器
}

// 医疗设备看门狗配置示例
void configure_medical_device_watchdog(void) {
    // 配置2秒超时
    // 医疗设备通常使用较长的超时时间
    // 以避免误触发，但要足够短以快速检测故障
    init_hardware_watchdog(2000);
    
    // 记录看门狗启动
    log_system_event("Hardware watchdog enabled: 2s timeout");
}
```

### 2. 软件看门狗

**实现原理**:
```c
// 软件看门狗 - 基于定时器实现
typedef struct {
    uint32_t timeout_ms;
    uint32_t last_feed_time;
    bool enabled;
    void (*timeout_callback)(void);
} software_watchdog_t;

software_watchdog_t sw_watchdogs[MAX_SW_WATCHDOGS];

// 初始化软件看门狗
void sw_watchdog_init(uint8_t id, uint32_t timeout_ms, 
                     void (*callback)(void)) {
    sw_watchdogs[id].timeout_ms = timeout_ms;
    sw_watchdogs[id].last_feed_time = get_tick_count();
    sw_watchdogs[id].enabled = true;
    sw_watchdogs[id].timeout_callback = callback;
}

// 喂软件看门狗
void sw_watchdog_feed(uint8_t id) {
    if (id < MAX_SW_WATCHDOGS) {
        sw_watchdogs[id].last_feed_time = get_tick_count();
    }
}

// 软件看门狗监控任务
void sw_watchdog_monitor_task(void *param) {
    while (1) {
        uint32_t current_time = get_tick_count();
        
        for (uint8_t i = 0; i < MAX_SW_WATCHDOGS; i++) {
            if (sw_watchdogs[i].enabled) {
                uint32_t elapsed = current_time - sw_watchdogs[i].last_feed_time;
                
                if (elapsed > sw_watchdogs[i].timeout_ms) {
                    // 超时处理
                    log_error("Software watchdog %u timeout", i);
                    
                    if (sw_watchdogs[i].timeout_callback) {
                        sw_watchdogs[i].timeout_callback();
                    }
                    
                    // 重置计时器
                    sw_watchdogs[i].last_feed_time = current_time;
                }
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
```

### 3. 硬件 vs 软件看门狗

**对比分析**:

| 特性 | 硬件看门狗 | 软件看门狗 |
|------|-----------|-----------|
| 独立性 | 完全独立 | 依赖软件运行 |
| 可靠性 | 非常高 | 中等 |
| 灵活性 | 低 | 高 |
| 复位方式 | 硬件复位 | 软件处理 |
| 适用场景 | 系统级故障 | 任务级监控 |
| 成本 | 硬件资源 | CPU时间 |

**组合使用策略**:
```c
// 医疗设备看门狗架构
typedef struct {
    // 硬件看门狗 - 最后防线
    struct {
        uint32_t timeout_ms;
        uint32_t feed_count;
        uint32_t reset_count;
    } hardware_wdt;
    
    // 软件看门狗 - 任务监控
    struct {
        software_watchdog_t task_watchdogs[10];
        uint32_t timeout_count;
    } software_wdt;
    
    // 看门狗管理器
    struct {
        bool system_healthy;
        uint32_t last_health_check;
    } manager;
} watchdog_system_t;

watchdog_system_t wdt_system;

// 初始化看门狗系统
void init_watchdog_system(void) {
    // 1. 初始化硬件看门狗（5秒超时）
    init_hardware_watchdog(5000);
    wdt_system.hardware_wdt.timeout_ms = 5000;
    
    // 2. 初始化关键任务的软件看门狗
    sw_watchdog_init(0, 1000, handle_ecg_task_timeout);    // ECG任务
    sw_watchdog_init(1, 2000, handle_alarm_task_timeout);  // 报警任务
    sw_watchdog_init(2, 500, handle_display_task_timeout); // 显示任务
    
    // 3. 启动看门狗管理器任务
    xTaskCreate(watchdog_manager_task, "WDT_MGR", 
                STACK_SIZE, NULL, PRIORITY_HIGH, NULL);
}
```

## 喂狗策略

### 1. 集中式喂狗

**看门狗管理器模式**:
```c
// 任务健康状态
typedef struct {
    const char *task_name;
    uint32_t last_heartbeat;
    uint32_t timeout_ms;
    bool is_healthy;
    uint32_t timeout_count;
} task_health_t;

task_health_t task_health_table[] = {
    {"ECG_Task",     0, 1000, true, 0},
    {"Alarm_Task",   0, 2000, true, 0},
    {"Display_Task", 0, 500,  true, 0},
    {"Network_Task", 0, 3000, true, 0},
    {"Storage_Task", 0, 5000, true, 0},
};

#define NUM_MONITORED_TASKS (sizeof(task_health_table) / sizeof(task_health_t))

// 任务报告心跳
void task_report_heartbeat(const char *task_name) {
    for (uint32_t i = 0; i < NUM_MONITORED_TASKS; i++) {
        if (strcmp(task_health_table[i].task_name, task_name) == 0) {
            task_health_table[i].last_heartbeat = get_tick_count();
            task_health_table[i].is_healthy = true;
            break;
        }
    }
}

// 看门狗管理器任务
void watchdog_manager_task(void *param) {
    while (1) {
        uint32_t current_time = get_tick_count();
        bool all_tasks_healthy = true;
        
        // 检查所有任务健康状态
        for (uint32_t i = 0; i < NUM_MONITORED_TASKS; i++) {
            uint32_t elapsed = current_time - task_health_table[i].last_heartbeat;
            
            if (elapsed > task_health_table[i].timeout_ms) {
                task_health_table[i].is_healthy = false;
                task_health_table[i].timeout_count++;
                all_tasks_healthy = false;
                
                log_error("Task %s timeout (elapsed: %u ms)",
                         task_health_table[i].task_name, elapsed);
                
                // 尝试恢复任务
                attempt_task_recovery(i);
            }
        }
        
        // 只有所有任务健康时才喂硬件看门狗
        if (all_tasks_healthy) {
            feed_watchdog();
            wdt_system.hardware_wdt.feed_count++;
        } else {
            log_warning("System unhealthy, not feeding watchdog");
            // 如果持续不健康，硬件看门狗将触发系统复位
        }
        
        // 每100ms检查一次
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}

// 任务使用示例
void ecg_processing_task(void *param) {
    while (1) {
        // 执行ECG处理
        process_ecg_data();
        
        // 报告心跳
        task_report_heartbeat("ECG_Task");
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}
```

### 2. 分布式喂狗

**多级看门狗架构**:
```c
// 分层看门狗系统
typedef enum {
    WDT_LEVEL_TASK = 0,      // 任务级
    WDT_LEVEL_SUBSYSTEM,     // 子系统级
    WDT_LEVEL_SYSTEM         // 系统级
} watchdog_level_t;

typedef struct {
    watchdog_level_t level;
    uint32_t timeout_ms;
    uint32_t last_feed;
    bool enabled;
    void (*recovery_handler)(void);
} hierarchical_watchdog_t;

// 三级看门狗配置
hierarchical_watchdog_t wdt_hierarchy[] = {
    // 任务级看门狗（最快响应）
    {WDT_LEVEL_TASK, 500, 0, true, recover_task},
    
    // 子系统级看门狗（中等响应）
    {WDT_LEVEL_SUBSYSTEM, 2000, 0, true, recover_subsystem},
    
    // 系统级看门狗（最后防线）
    {WDT_LEVEL_SYSTEM, 5000, 0, true, system_reset}
};

// 分层喂狗
void feed_hierarchical_watchdog(watchdog_level_t level) {
    uint32_t current_time = get_tick_count();
    
    // 喂当前级别及以下的看门狗
    for (uint32_t i = 0; i <= level; i++) {
        wdt_hierarchy[i].last_feed = current_time;
    }
}

// 分层监控
void hierarchical_watchdog_monitor(void) {
    uint32_t current_time = get_tick_count();
    
    for (uint32_t i = 0; i < 3; i++) {
        if (wdt_hierarchy[i].enabled) {
            uint32_t elapsed = current_time - wdt_hierarchy[i].last_feed;
            
            if (elapsed > wdt_hierarchy[i].timeout_ms) {
                log_error("Level %u watchdog timeout", i);
                
                if (wdt_hierarchy[i].recovery_handler) {
                    wdt_hierarchy[i].recovery_handler();
                }
            }
        }
    }
}
```

## 故障检测策略

### 1. 主动健康检查

**系统健康监控**:
```c
// 健康检查项
typedef enum {
    HEALTH_CHECK_CPU_USAGE = 0,
    HEALTH_CHECK_MEMORY,
    HEALTH_CHECK_STACK,
    HEALTH_CHECK_TASKS,
    HEALTH_CHECK_PERIPHERALS,
    HEALTH_CHECK_COMMUNICATION,
    HEALTH_CHECK_SENSORS,
    HEALTH_CHECK_COUNT
} health_check_type_t;

typedef struct {
    health_check_type_t type;
    bool (*check_function)(void);
    const char *name;
    bool last_result;
    uint32_t fail_count;
} health_check_t;

// 健康检查函数
bool check_cpu_usage(void) {
    uint32_t cpu_usage = get_cpu_usage_percent();
    return cpu_usage < 95;  // CPU使用率低于95%
}

bool check_memory(void) {
    uint32_t free_heap = xPortGetFreeHeapSize();
    uint32_t min_heap = configTOTAL_HEAP_SIZE * 0.1;  // 至少10%空闲
    return free_heap > min_heap;
}

bool check_stack_overflow(void) {
    // 检查所有任务栈
    TaskHandle_t task_handles[10];
    UBaseType_t num_tasks = uxTaskGetNumberOfTasks();
    
    if (num_tasks > 10) num_tasks = 10;
    
    uxTaskGetSystemState((TaskStatus_t *)task_handles, num_tasks, NULL);
    
    for (uint32_t i = 0; i < num_tasks; i++) {
        UBaseType_t stack_remaining = uxTaskGetStackHighWaterMark(task_handles[i]);
        if (stack_remaining < 100) {  // 少于100字节
            log_error("Task stack low: %u bytes", stack_remaining);
            return false;
        }
    }
    
    return true;
}

bool check_peripherals(void) {
    // 检查关键外设状态
    bool adc_ok = check_adc_status();
    bool uart_ok = check_uart_status();
    bool spi_ok = check_spi_status();
    
    return adc_ok && uart_ok && spi_ok;
}

bool check_sensors(void) {
    // 检查传感器数据有效性
    bool ecg_ok = is_ecg_data_valid();
    bool spo2_ok = is_spo2_data_valid();
    bool temp_ok = is_temp_data_valid();
    
    return ecg_ok && spo2_ok && temp_ok;
}

// 健康检查表
health_check_t health_checks[] = {
    {HEALTH_CHECK_CPU_USAGE, check_cpu_usage, "CPU Usage", true, 0},
    {HEALTH_CHECK_MEMORY, check_memory, "Memory", true, 0},
    {HEALTH_CHECK_STACK, check_stack_overflow, "Stack", true, 0},
    {HEALTH_CHECK_PERIPHERALS, check_peripherals, "Peripherals", true, 0},
    {HEALTH_CHECK_SENSORS, check_sensors, "Sensors", true, 0},
};

// 执行健康检查
bool perform_health_checks(void) {
    bool all_healthy = true;
    
    for (uint32_t i = 0; i < HEALTH_CHECK_COUNT; i++) {
        bool result = health_checks[i].check_function();
        health_checks[i].last_result = result;
        
        if (!result) {
            health_checks[i].fail_count++;
            all_healthy = false;
            
            log_warning("Health check failed: %s (count: %u)",
                       health_checks[i].name,
                       health_checks[i].fail_count);
        }
    }
    
    return all_healthy;
}

// 健康监控任务
void health_monitor_task(void *param) {
    while (1) {
        bool system_healthy = perform_health_checks();
        
        if (!system_healthy) {
            // 记录不健康状态
            log_system_health_status();
            
            // 触发恢复措施
            initiate_recovery_procedure();
        }
        
        // 每秒检查一次
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
```

### 2. 被动故障检测

**异常捕获和处理**:
```c
// 故障类型
typedef enum {
    FAULT_HARD_FAULT = 0,
    FAULT_MEM_MANAGE,
    FAULT_BUS_FAULT,
    FAULT_USAGE_FAULT,
    FAULT_STACK_OVERFLOW,
    FAULT_ASSERT,
    FAULT_WATCHDOG
} fault_type_t;

// 故障记录
typedef struct {
    fault_type_t type;
    uint32_t timestamp;
    uint32_t pc;          // 程序计数器
    uint32_t lr;          // 链接寄存器
    uint32_t psr;         // 程序状态寄存器
    uint32_t fault_addr;  // 故障地址
    char task_name[16];
} fault_record_t;

#define MAX_FAULT_RECORDS 10
fault_record_t fault_history[MAX_FAULT_RECORDS];
uint32_t fault_index = 0;

// 记录故障
void record_fault(fault_type_t type, uint32_t *stack_frame) {
    fault_record_t *record = &fault_history[fault_index];
    
    record->type = type;
    record->timestamp = get_tick_count();
    record->pc = stack_frame[6];   // R15 (PC)
    record->lr = stack_frame[5];   // R14 (LR)
    record->psr = stack_frame[7];  // xPSR
    
    // 获取当前任务名
    TaskHandle_t task = xTaskGetCurrentTaskHandle();
    if (task) {
        pcTaskGetName(task, record->task_name, sizeof(record->task_name));
    }
    
    // 获取故障地址（如果适用）
    if (type == FAULT_MEM_MANAGE || type == FAULT_BUS_FAULT) {
        record->fault_addr = SCB->MMFAR;  // 或 SCB->BFAR
    }
    
    fault_index = (fault_index + 1) % MAX_FAULT_RECORDS;
    
    // 保存到非易失性存储
    save_fault_record_to_flash(record);
}
```

// Hard Fault处理程序
void HardFault_Handler(void) {
    __asm volatile (
        "tst lr, #4\n"
        "ite eq\n"
        "mrseq r0, msp\n"
        "mrsne r0, psp\n"
        "b hard_fault_handler_c\n"
    );
}

void hard_fault_handler_c(uint32_t *stack_frame) {
    // 记录故障
    record_fault(FAULT_HARD_FAULT, stack_frame);
    
    // 打印故障信息
    log_error("Hard Fault at PC=0x%08X, LR=0x%08X", 
             stack_frame[6], stack_frame[5]);
    
    // 进入安全状态
    enter_safe_state();
    
    // 等待看门狗复位
    while (1);
}
```

## 安全状态设计

### 1. 安全状态定义

**医疗设备安全状态**:
```c
typedef enum {
    STATE_NORMAL_OPERATION = 0,
    STATE_DEGRADED_MODE,
    STATE_SAFE_STATE,
    STATE_EMERGENCY_STOP
} system_state_t;

typedef struct {
    system_state_t current_state;
    system_state_t previous_state;
    uint32_t state_entry_time;
    uint32_t transition_count;
} state_machine_t;

state_machine_t system_state_machine;

// 进入安全状态
void enter_safe_state(void) {
    log_critical("Entering safe state");
    
    // 1. 停止所有治疗输出
    disable_therapy_outputs();
    
    // 2. 保存关键数据
    save_critical_data_to_nvram();
    
    // 3. 激活报警
    activate_critical_alarm(ALARM_SYSTEM_FAULT);
    
    // 4. 显示错误信息
    display_error_message("SYSTEM FAULT - SAFE STATE");
    
    // 5. 记录状态转换
    system_state_machine.previous_state = system_state_machine.current_state;
    system_state_machine.current_state = STATE_SAFE_STATE;
    system_state_machine.state_entry_time = get_tick_count();
    system_state_machine.transition_count++;
    
    // 6. 通知外部系统
    notify_external_systems(EVENT_SAFE_STATE_ENTERED);
}

// 安全状态下的最小功能
void safe_state_operation(void) {
    while (system_state_machine.current_state == STATE_SAFE_STATE) {
        // 保持基本监控
        monitor_vital_signs();
        
        // 保持报警功能
        process_alarms();
        
        // 保持显示更新
        update_display();
        
        // 保持通信（用于远程诊断）
        process_communication();
        
        // 等待用户干预或自动恢复
        if (check_recovery_conditions()) {
            attempt_system_recovery();
        }
        
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
```

### 2. 故障恢复策略

**分级恢复机制**:
```c
typedef enum {
    RECOVERY_LEVEL_TASK_RESTART = 0,
    RECOVERY_LEVEL_SUBSYSTEM_RESET,
    RECOVERY_LEVEL_SOFT_RESET,
    RECOVERY_LEVEL_HARD_RESET
} recovery_level_t;

// 尝试恢复
bool attempt_recovery(recovery_level_t level) {
    log_info("Attempting recovery level %u", level);
    
    switch (level) {
        case RECOVERY_LEVEL_TASK_RESTART:
            return restart_failed_tasks();
            
        case RECOVERY_LEVEL_SUBSYSTEM_RESET:
            return reset_failed_subsystem();
            
        case RECOVERY_LEVEL_SOFT_RESET:
            return perform_soft_reset();
            
        case RECOVERY_LEVEL_HARD_RESET:
            perform_hard_reset();
            return false;  // 不会返回
    }
    
    return false;
}

// 任务重启
bool restart_failed_tasks(void) {
    for (uint32_t i = 0; i < NUM_MONITORED_TASKS; i++) {
        if (!task_health_table[i].is_healthy) {
            log_info("Restarting task: %s", task_health_table[i].task_name);
            
            // 删除旧任务
            vTaskDelete(task_handles[i]);
            
            // 创建新任务
            task_handles[i] = recreate_task(i);
            
            if (task_handles[i] == NULL) {
                log_error("Failed to restart task %s", 
                         task_health_table[i].task_name);
                return false;
            }
            
            // 重置健康状态
            task_health_table[i].is_healthy = true;
            task_health_table[i].last_heartbeat = get_tick_count();
        }
    }
    
    return true;
}

// 软复位
bool perform_soft_reset(void) {
    log_info("Performing soft reset");
    
    // 1. 保存状态
    save_system_state();
    
    // 2. 停止所有任务
    vTaskSuspendAll();
    
    // 3. 重新初始化子系统
    reinit_peripherals();
    reinit_communication();
    reinit_data_processing();
    
    // 4. 重新创建任务
    recreate_all_tasks();
    
    // 5. 恢复状态
    restore_system_state();
    
    // 6. 恢复调度器
    xTaskResumeAll();
    
    log_info("Soft reset completed");
    return true;
}

// 硬复位
void perform_hard_reset(void) {
    log_critical("Performing hard reset");
    
    // 保存复位原因
    save_reset_reason(RESET_REASON_WATCHDOG);
    
    // 触发系统复位
    NVIC_SystemReset();
}
```

## 复位原因分析

**启动时检查复位原因**:
```c
typedef enum {
    RESET_REASON_POWER_ON = 0,
    RESET_REASON_WATCHDOG,
    RESET_REASON_SOFTWARE,
    RESET_REASON_EXTERNAL,
    RESET_REASON_BROWNOUT,
    RESET_REASON_UNKNOWN
} reset_reason_t;

// 获取复位原因
reset_reason_t get_reset_reason(void) {
    uint32_t rcc_csr = RCC->CSR;
    reset_reason_t reason = RESET_REASON_UNKNOWN;
    
    if (rcc_csr & RCC_CSR_PORRSTF) {
        reason = RESET_REASON_POWER_ON;
    } else if (rcc_csr & RCC_CSR_IWDGRSTF) {
        reason = RESET_REASON_WATCHDOG;
    } else if (rcc_csr & RCC_CSR_SFTRSTF) {
        reason = RESET_REASON_SOFTWARE;
    } else if (rcc_csr & RCC_CSR_PINRSTF) {
        reason = RESET_REASON_EXTERNAL;
    } else if (rcc_csr & RCC_CSR_BORRSTF) {
        reason = RESET_REASON_BROWNOUT;
    }
    
    // 清除复位标志
    RCC->CSR |= RCC_CSR_RMVF;
    
    return reason;
}

// 启动时处理
void handle_reset_on_startup(void) {
    reset_reason_t reason = get_reset_reason();
    
    log_info("Reset reason: %u", reason);
    
    switch (reason) {
        case RESET_REASON_POWER_ON:
            // 正常启动
            perform_full_initialization();
            break;
            
        case RESET_REASON_WATCHDOG:
            // 看门狗复位 - 可能有故障
            log_error("Watchdog reset detected");
            load_fault_records();
            analyze_fault_history();
            
            // 尝试恢复
            if (can_recover_from_fault()) {
                perform_recovery_initialization();
            } else {
                enter_safe_state();
            }
            break;
            
        case RESET_REASON_SOFTWARE:
            // 软件复位 - 可能是固件更新
            perform_quick_initialization();
            break;
            
        default:
            // 未知原因 - 谨慎处理
            log_warning("Unknown reset reason");
            perform_full_initialization();
            break;
    }
}
```

## 最佳实践

### 设计原则
- 硬件看门狗作为最后防线
- 软件看门狗监控关键任务
- 集中式喂狗策略
- 分级故障恢复
- 完整的故障记录
- 明确的安全状态

### 医疗设备特殊考虑
- 患者安全优先
- 快速故障检测
- 可靠的恢复机制
- 完整的审计日志
- 符合IEC 62304要求

## 合规性要求

### IEC 62304
- 故障检测机制文档
- 安全状态设计
- 恢复策略验证
- 风险分析

### FDA指南
- 网络安全考虑
- 故障日志记录
- 远程监控能力

## 总结

看门狗和故障恢复是医疗设备可靠性的关键。通过硬件和软件看门狗的组合、完善的故障检测机制、分级恢复策略和明确的安全状态设计，可以确保设备在故障情况下仍能保护患者安全。

---

**相关文档**:
- [多核处理器编程](multicore-programming.md)
- [DMA技术](dma.md)
- [引导加载程序](bootloader.md)

**标签**: #看门狗 #故障恢复 #安全状态 #可靠性 #医疗设备
