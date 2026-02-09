---
title: 睡眠模式
description: 掌握微控制器的各种睡眠模式，学习如何在医疗器械中实现低功耗设计，延长电池寿命
difficulty: 中级
estimated_time: 40分钟
tags:
- 低功耗
- 睡眠模式
- 功耗管理
- 电池供电
- 唤醒机制
related_modules:
- zh/technical-knowledge/low-power-design/power-optimization
- zh/technical-knowledge/rtos/task-scheduling
- zh/technical-knowledge/hardware-interfaces/gpio
last_updated: '2026-02-09'
version: '1.0'
language: zh
---

# 睡眠模式

## 学习目标

完成本模块后，你将能够：
- 理解微控制器的各种睡眠模式
- 配置和使用不同的低功耗模式
- 实现唤醒机制
- 在RTOS环境中使用睡眠模式
- 在医疗器械中实现有效的功耗管理

## 前置知识

- 微控制器架构基础
- 中断处理机制
- RTOS任务调度
- 时钟系统

## 内容

### 概念介绍

睡眠模式是微控制器降低功耗的主要手段。通过关闭不需要的外设和时钟，MCU可以在保持必要功能的同时大幅降低功耗。这对于电池供电的医疗器械尤为重要。

**功耗管理的重要性**：
- **延长电池寿命**：便携式医疗设备的关键指标
- **降低发热**：提高可靠性和舒适度
- **环保节能**：符合绿色设计理念
- **降低成本**：减少电池更换频率


### STM32睡眠模式

STM32微控制器提供三种主要的低功耗模式：

#### 1. 睡眠模式（Sleep Mode）

**特点**：
- CPU停止，所有外设继续运行
- 功耗降低最少，唤醒最快
- 典型功耗：几mA

**进入条件**：
- 执行WFI（Wait For Interrupt）或WFE（Wait For Event）指令

**唤醒方式**：
- 任何中断（WFI）
- 任何事件（WFE）

```c
// 进入睡眠模式
void Enter_SleepMode(void) {
    // 挂起SysTick中断（可选）
    HAL_SuspendTick();
    
    // 进入睡眠模式
    HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    
    // 唤醒后恢复SysTick
    HAL_ResumeTick();
}
```

#### 2. 停止模式（Stop Mode）

**特点**：
- CPU和大部分外设时钟停止
- SRAM和寄存器内容保持
- RTC、独立看门狗、唤醒单元继续运行
- 典型功耗：几十μA到几百μA

**进入条件**：
- 配置PWR寄存器
- 执行WFI或WFE指令

**唤醒方式**：
- EXTI线中断
- RTC闹钟/唤醒
- 独立看门狗复位

```c
// 进入停止模式
void Enter_StopMode(void) {
    // 挂起SysTick
    HAL_SuspendTick();
    
    // 配置停止模式
    // PWR_LOWPOWERREGULATOR_ON: 低功耗稳压器
    // PWR_SLEEPENTRY_WFI: 使用WFI指令进入
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    
    // 唤醒后重新配置系统时钟（HSI被使用）
    SystemClock_Config();
    
    // 恢复SysTick
    HAL_ResumeTick();
}
```

#### 3. 待机模式（Standby Mode）

**特点**：
- 功耗最低
- 1.8V域断电，SRAM和寄存器内容丢失
- 只有备份寄存器和RTC保持
- 典型功耗：几μA

**进入条件**：
- 配置PWR寄存器
- 执行WFI或WFE指令

**唤醒方式**：
- WKUP引脚上升沿
- RTC闹钟
- 外部复位
- 独立看门狗复位

```c
// 进入待机模式
void Enter_StandbyMode(void) {
    // 使能WKUP引脚
    HAL_PWR_EnableWakeUpPin(PWR_WAKEUP_PIN1);
    
    // 清除唤醒标志
    __HAL_PWR_CLEAR_FLAG(PWR_FLAG_WU);
    
    // 进入待机模式
    HAL_PWR_EnterSTANDBYMode();
    
    // 注意：从待机模式唤醒后，MCU会复位，程序从头开始执行
}

// 检查是否从待机模式唤醒
void CheckWakeupSource(void) {
    if (__HAL_PWR_GET_FLAG(PWR_FLAG_SB) != RESET) {
        // 从待机模式唤醒
        __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB);
        
        UART_Printf("Wakeup from Standby Mode\r\n");
        
        // 恢复应用状态（从备份寄存器或外部存储）
        RestoreApplicationState();
    }
}
```

**代码说明**：
- 待机模式唤醒后MCU复位，需要保存状态到备份寄存器或外部存储
- 备份寄存器在待机模式下保持，可用于保存关键数据

### 睡眠模式对比

| 模式 | CPU | 外设 | SRAM | 功耗 | 唤醒时间 | 唤醒方式 |
|------|-----|------|------|------|----------|----------|
| 睡眠 | 停止 | 运行 | 保持 | ~mA | <1μs | 任何中断 |
| 停止 | 停止 | 停止 | 保持 | ~μA | 几μs | EXTI, RTC |
| 待机 | 停止 | 停止 | 丢失 | <10μA | 几十μs | WKUP, RTC |


### 唤醒机制

#### GPIO唤醒（EXTI）

```c
// 配置GPIO唤醒
void Config_GPIO_Wakeup(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能时钟
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    // 配置唤醒引脚
    GPIO_InitStruct.Pin = GPIO_PIN_13;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;  // 下降沿触发
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // 配置NVIC
    HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);
}

// EXTI中断处理
void EXTI15_10_IRQHandler(void) {
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_13);
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_13) {
        // 唤醒后的处理
        UART_Printf("Wakeup by GPIO\r\n");
    }
}
```

#### RTC唤醒

```c
// RTC句柄
RTC_HandleTypeDef hrtc;

// 配置RTC
void Config_RTC(void) {
    // 使能PWR时钟
    __HAL_RCC_PWR_CLK_ENABLE();
    
    // 允许访问备份域
    HAL_PWR_EnableBkUpAccess();
    
    // 配置RTC
    hrtc.Instance = RTC;
    hrtc.Init.HourFormat = RTC_HOURFORMAT_24;
    hrtc.Init.AsynchPrediv = 127;
    hrtc.Init.SynchPrediv = 255;
    hrtc.Init.OutPut = RTC_OUTPUT_DISABLE;
    hrtc.Init.OutPutPolarity = RTC_OUTPUT_POLARITY_HIGH;
    hrtc.Init.OutPutType = RTC_OUTPUT_TYPE_OPENDRAIN;
    
    if (HAL_RTC_Init(&hrtc) != HAL_OK) {
        Error_Handler();
    }
}

// 设置RTC闹钟唤醒
void Set_RTC_Alarm_Wakeup(uint32_t seconds) {
    RTC_AlarmTypeDef sAlarm = {0};
    
    // 配置闹钟
    sAlarm.AlarmTime.Hours = 0;
    sAlarm.AlarmTime.Minutes = 0;
    sAlarm.AlarmTime.Seconds = seconds;
    sAlarm.AlarmTime.SubSeconds = 0;
    sAlarm.AlarmMask = RTC_ALARMMASK_DATEWEEKDAY | RTC_ALARMMASK_HOURS | 
                       RTC_ALARMMASK_MINUTES;
    sAlarm.AlarmSubSecondMask = RTC_ALARMSUBSECONDMASK_ALL;
    sAlarm.AlarmDateWeekDaySel = RTC_ALARMDATEWEEKDAYSEL_DATE;
    sAlarm.AlarmDateWeekDay = 1;
    sAlarm.Alarm = RTC_ALARM_A;
    
    if (HAL_RTC_SetAlarm_IT(&hrtc, &sAlarm, RTC_FORMAT_BIN) != HAL_OK) {
        Error_Handler();
    }
}

// RTC闹钟中断处理
void RTC_Alarm_IRQHandler(void) {
    HAL_RTC_AlarmIRQHandler(&hrtc);
}

void HAL_RTC_AlarmAEventCallback(RTC_HandleTypeDef *hrtc) {
    // 唤醒后的处理
    UART_Printf("Wakeup by RTC Alarm\r\n");
}
```

#### 定时唤醒

```c
// 配置RTC唤醒定时器
void Config_RTC_Wakeup_Timer(uint32_t seconds) {
    // 禁用唤醒定时器
    HAL_RTCEx_DeactivateWakeUpTimer(&hrtc);
    
    // 配置唤醒定时器
    // RTC_WAKEUPCLOCK_RTCCLK_DIV16: 时钟源
    // seconds * 2048: 计数值（32768Hz / 16 = 2048Hz）
    if (HAL_RTCEx_SetWakeUpTimer_IT(&hrtc, seconds * 2048 - 1, 
                                     RTC_WAKEUPCLOCK_RTCCLK_DIV16) != HAL_OK) {
        Error_Handler();
    }
}

// RTC唤醒中断处理
void RTC_WKUP_IRQHandler(void) {
    HAL_RTCEx_WakeUpTimerIRQHandler(&hrtc);
}

void HAL_RTCEx_WakeUpTimerEventCallback(RTC_HandleTypeDef *hrtc) {
    // 定时唤醒处理
    UART_Printf("Wakeup by RTC Timer\r\n");
}
```

### RTOS中的睡眠模式

#### FreeRTOS Tickless Idle

FreeRTOS提供Tickless Idle模式，在空闲时自动进入低功耗模式。

```c
// FreeRTOSConfig.h 配置
#define configUSE_TICKLESS_IDLE  1

// 实现低功耗回调
void vApplicationSleep(TickType_t xExpectedIdleTime) {
    // 计算睡眠时间（毫秒）
    uint32_t sleepTimeMs = xExpectedIdleTime * portTICK_PERIOD_MS;
    
    // 配置RTC唤醒定时器
    Config_RTC_Wakeup_Timer(sleepTimeMs / 1000);
    
    // 进入停止模式
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_SLEEPENTRY_WFI);
    
    // 唤醒后重新配置时钟
    SystemClock_Config();
}

// 低功耗任务示例
void LowPowerTask(void *pvParameters) {
    while(1) {
        // 执行任务
        ProcessSensorData();
        
        // 进入阻塞状态，允许系统进入低功耗模式
        vTaskDelay(pdMS_TO_TICKS(1000));  // 1秒
    }
}
```

**代码说明**：
- Tickless Idle在所有任务阻塞时自动进入低功耗模式
- 需要实现`vApplicationSleep`回调函数
- 唤醒后需要补偿系统时钟

### 实际应用示例

#### 便携式血压计

```c
// 血压计低功耗状态机
typedef enum {
    STATE_IDLE,           // 空闲状态（待机模式）
    STATE_MEASURING,      // 测量状态（正常运行）
    STATE_DISPLAYING,     // 显示结果（正常运行）
    STATE_TRANSMITTING    // 数据传输（正常运行）
} DeviceState_t;

DeviceState_t deviceState = STATE_IDLE;

void BloodPressureMonitor_Task(void *pvParameters) {
    while(1) {
        switch (deviceState) {
            case STATE_IDLE:
                // 显示"按键开始测量"
                Display_ShowMessage("Press to start");
                
                // 保存状态到备份寄存器
                SaveStateToBackupRegister(STATE_IDLE);
                
                // 进入待机模式，等待按键唤醒
                Enter_StandbyMode();
                break;
                
            case STATE_MEASURING:
                // 执行血压测量
                MeasureBloodPressure();
                
                // 测量完成，进入显示状态
                deviceState = STATE_DISPLAYING;
                break;
                
            case STATE_DISPLAYING:
                // 显示测量结果
                Display_ShowResults();
                
                // 显示30秒后进入空闲
                vTaskDelay(pdMS_TO_TICKS(30000));
                deviceState = STATE_IDLE;
                break;
                
            case STATE_TRANSMITTING:
                // 通过蓝牙传输数据
                TransmitData();
                
                // 传输完成，进入空闲
                deviceState = STATE_IDLE;
                break;
        }
    }
}

// 从待机模式唤醒后的初始化
void main(void) {
    HAL_Init();
    SystemClock_Config();
    
    // 检查唤醒源
    if (__HAL_PWR_GET_FLAG(PWR_FLAG_SB) != RESET) {
        // 从待机模式唤醒
        __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB);
        
        // 恢复状态
        deviceState = RestoreStateFromBackupRegister();
        
        // 按键唤醒，开始测量
        if (deviceState == STATE_IDLE) {
            deviceState = STATE_MEASURING;
        }
    }
    
    // 初始化外设
    Init_Peripherals();
    
    // 创建任务
    xTaskCreate(BloodPressureMonitor_Task, "BPM", 512, NULL, 1, NULL);
    
    // 启动调度器
    vTaskStartScheduler();
}
```

**代码说明**：
- 空闲时进入待机模式，功耗<10μA
- 按键唤醒后开始测量
- 使用备份寄存器保存状态
- 测量和显示时正常运行


### 最佳实践

!!! tip "睡眠模式使用最佳实践"
    - **选择合适的模式**：根据功耗要求和唤醒时间选择
    - **外设管理**：进入睡眠前关闭不需要的外设
    - **时钟配置**：停止模式唤醒后需要重新配置时钟
    - **状态保存**：待机模式前保存关键数据到备份寄存器或外部存储
    - **唤醒源配置**：确保至少有一个唤醒源
    - **测试验证**：实际测量功耗，验证低功耗效果
    - **RTOS集成**：使用Tickless Idle自动管理低功耗
    - **电池监控**：实时监控电池电量，低电量时进入超低功耗模式

### 常见陷阱

!!! warning "注意事项"
    - **忘记配置唤醒源**：导致无法唤醒，系统"死机"
    - **外设未关闭**：外设继续运行，功耗降低不明显
    - **时钟未恢复**：停止模式唤醒后使用HSI，性能下降
    - **调试困难**：睡眠模式下调试器断开，难以调试
    - **SRAM丢失**：待机模式下SRAM内容丢失，未保存状态
    - **RTC未配置**：定时唤醒失败
    - **中断优先级**：唤醒中断优先级过低，可能被抢占
    - **功耗测量不准**：未断开调试器、LED等额外负载

## 实践练习

1. **基础睡眠**：实现睡眠模式和唤醒
2. **定时唤醒**：使用RTC定时唤醒
3. **功耗测量**：测量不同模式下的实际功耗
4. **状态保存**：实现待机模式的状态保存和恢复
5. **RTOS集成**：在FreeRTOS中实现Tickless Idle

## 自测问题

??? question "睡眠、停止和待机模式有什么区别？如何选择？"
    三种模式在功耗、唤醒时间和状态保持上有不同的权衡。
    
    ??? success "答案"
        **主要区别**：
        
        | 特性 | 睡眠模式 | 停止模式 | 待机模式 |
        |------|----------|----------|----------|
        | CPU | 停止 | 停止 | 停止 |
        | 外设 | 运行 | 停止 | 停止 |
        | SRAM | 保持 | 保持 | 丢失 |
        | 功耗 | ~mA | ~μA | <10μA |
        | 唤醒时间 | <1μs | 几μs | 几十μs |
        | 唤醒后 | 继续执行 | 继续执行 | 复位 |
        
        **选择建议**：
        
        1. **睡眠模式**：
           - 短时间空闲（<1ms）
           - 需要快速响应
           - 外设需要继续运行
           - 例：等待UART接收
        
        2. **停止模式**：
           - 中等时间空闲（几ms到几秒）
           - 需要保持SRAM内容
           - 可以接受几μs的唤醒延迟
           - 例：传感器定时采样
        
        3. **待机模式**：
           - 长时间空闲（几秒到几小时）
           - 功耗要求极低
           - 可以接受复位和状态丢失
           - 例：便携设备待机
        
        **医疗器械应用**：
        - 连续监测设备：停止模式
        - 按需测量设备：待机模式
        - 实时报警设备：睡眠模式

??? question "从停止模式唤醒后为什么需要重新配置时钟？"
    停止模式会改变系统时钟源。
    
    ??? success "答案"
        **原因**：
        
        1. **时钟切换**：
           - 进入停止模式时，HSE和PLL被关闭
           - 唤醒时使用HSI（内部RC振荡器）
           - HSI频率较低（通常16MHz）
        
        2. **性能影响**：
           - HSI精度较低（±1%）
           - 频率低于正常工作频率
           - 外设时钟也受影响
        
        3. **需要恢复**：
           - 重新启动HSE
           - 重新配置PLL
           - 切换系统时钟到PLL
        
        **恢复代码**：
        ```c
        void SystemClock_Config(void) {
            RCC_OscInitTypeDef RCC_OscInitStruct = {0};
            RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};
            
            // 配置HSE
            RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
            RCC_OscInitStruct.HSEState = RCC_HSE_ON;
            RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
            RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
            RCC_OscInitStruct.PLL.PLLM = 8;
            RCC_OscInitStruct.PLL.PLLN = 336;
            RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
            HAL_RCC_OscConfig(&RCC_OscInitStruct);
            
            // 配置系统时钟
            RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_SYSCLK;
            RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
            HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5);
        }
        ```
        
        **注意**：睡眠模式不需要重新配置时钟。

??? question "如何在待机模式下保存和恢复应用状态？"
    待机模式会丢失SRAM内容，需要特殊方法保存状态。
    
    ??? success "答案"
        **保存方法**：
        
        1. **备份寄存器**：
           - STM32提供20个32位备份寄存器
           - 在待机模式下保持
           - 访问需要使能PWR时钟和备份域
           
           ```c
           // 保存状态
           void SaveState(uint32_t state) {
               HAL_PWR_EnableBkUpAccess();
               HAL_RTCEx_BKUPWrite(&hrtc, RTC_BKP_DR0, state);
           }
           
           // 恢复状态
           uint32_t RestoreState(void) {
               HAL_PWR_EnableBkUpAccess();
               return HAL_RTCEx_BKUPRead(&hrtc, RTC_BKP_DR0);
           }
           ```
        
        2. **外部EEPROM/Flash**：
           - 容量大，可保存更多数据
           - 需要I2C/SPI通信
           - 写入速度较慢
        
        3. **RTC备份SRAM**（部分型号）：
           - 4KB备份SRAM
           - 在待机模式下保持
           - 访问速度快
        
        **保存内容建议**：
        - 设备状态（空闲/测量/显示等）
        - 测量数据（最近的测量结果）
        - 配置参数
        - 时间戳
        - CRC校验值（验证数据完整性）
        
        **恢复流程**：
        ```c
        void main(void) {
            HAL_Init();
            
            if (__HAL_PWR_GET_FLAG(PWR_FLAG_SB)) {
                // 从待机唤醒
                __HAL_PWR_CLEAR_FLAG(PWR_FLAG_SB);
                
                // 恢复状态
                uint32_t savedState = RestoreState();
                
                // 验证CRC
                if (ValidateCRC(savedState)) {
                    // 恢复应用状态
                    RestoreApplicationState(savedState);
                } else {
                    // CRC错误，使用默认状态
                    UseDefaultState();
                }
            }
            
            // 正常初始化
            Init_Application();
        }
        ```

??? question "FreeRTOS的Tickless Idle是如何工作的？"
    Tickless Idle是FreeRTOS的低功耗特性。
    
    ??? success "答案"
        **工作原理**：
        
        1. **检测空闲**：
           - 所有任务都处于阻塞状态
           - 没有就绪任务需要运行
        
        2. **计算睡眠时间**：
           - 找到最近的任务唤醒时间
           - 计算可以睡眠的tick数
        
        3. **进入低功耗**：
           - 停止SysTick
           - 配置RTC唤醒定时器
           - 进入停止模式
        
        4. **唤醒和补偿**：
           - RTC或其他中断唤醒
           - 计算实际睡眠时间
           - 补偿系统tick计数
        
        **配置**：
        ```c
        // FreeRTOSConfig.h
        #define configUSE_TICKLESS_IDLE  1
        #define configEXPECTED_IDLE_TIME_BEFORE_SLEEP  2  // 最小空闲tick数
        
        // 实现低功耗回调
        void vApplicationSleep(TickType_t xExpectedIdleTime) {
            // 进入低功耗模式
            // 配置唤醒定时器
            // 唤醒后补偿tick
        }
        ```
        
        **优势**：
        - 自动管理，无需手动控制
        - 与任务调度无缝集成
        - 显著降低功耗
        
        **注意事项**：
        - 需要精确的RTC
        - 唤醒时间补偿要准确
        - 短时间睡眠可能不值得（开销大于收益）

??? question "在医疗器械中使用睡眠模式需要注意什么？"
    医疗器械对可靠性和响应时间有严格要求。
    
    ??? success "答案"
        **医疗器械低功耗设计要点**：
        
        1. **安全优先**：
           - 关键监测功能不能因低功耗而失效
           - 报警功能必须可靠唤醒
           - 实现看门狗监控
        
        2. **响应时间**：
           - 紧急情况下的唤醒时间要求
           - 选择合适的睡眠模式
           - 测试最坏情况下的响应时间
        
        3. **数据完整性**：
           - 进入低功耗前保存关键数据
           - 使用CRC验证数据
           - 记录低功耗事件日志
        
        4. **电池管理**：
           - 实时监控电池电量
           - 低电量时进入超低功耗模式
           - 提供低电量警告
        
        5. **用户体验**：
           - 唤醒后快速响应
           - 显示设备状态
           - 提供电池电量指示
        
        6. **测试验证**：
           - 长期功耗测试
           - 唤醒可靠性测试
           - 极端温度下的测试
           - 符合IEC 60601-1要求
        
        7. **文档化**：
           - 记录功耗预算
           - 说明低功耗策略
           - 提供电池寿命估算

## 相关资源

- [功耗优化](power-optimizationn.md)
- [任务调度](../rtos/task-scheduling.md)
- [GPIO操作](../hardware-interfaces/gpio.md)

## 参考文献

1. STM32F4xx Reference Manual - STMicroelectronics
2. AN4365: Using STM32F4 MCU power modes with best dynamic efficiency - STMicroelectronics
3. FreeRTOS Low Power Support - FreeRTOS.org
4. IEC 60601-1:2005+AMD1:2012 - Medical electrical equipment
5. "Embedded Systems Architecture" - Tammy Noergaard
