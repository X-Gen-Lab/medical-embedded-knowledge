---
title: GPIO操作
description: 掌握GPIO（通用输入输出）的配置和使用，学习如何控制LED、读取按键、配置中断等基本硬件接口操作
difficulty: 基础
estimated_time: 30分钟
tags:
- GPIO
- 数字IO
- 中断
- 硬件接口
- 嵌入式
related_modules:
- zh/technical-knowledge/rtos/interrupt-handling
- zh/technical-knowledge/hardware-interfaces/spi
- zh/technical-knowledge/hardware-interfaces/i2c
last_updated: '2026-02-09'
version: '1.0'
language: zh
---

# GPIO操作

## 学习目标

完成本模块后，你将能够：
- 理解GPIO的工作模式和配置选项
- 配置GPIO为输入或输出模式
- 读取数字输入信号
- 控制数字输出信号
- 配置和使用GPIO中断
- 在医疗器械中安全可靠地使用GPIO

## 前置知识

- 数字电路基础
- C语言编程
- 微控制器基础知识

## 内容

### 概念介绍

GPIO（General Purpose Input/Output，通用输入输出）是微控制器最基本的外设接口。每个GPIO引脚可以配置为输入或输出模式，用于与外部设备交互。

**GPIO的主要用途**：
- **输出**：控制LED、继电器、电机驱动等
- **输入**：读取按键、开关、传感器数字信号
- **中断**：响应外部事件（按键按下、传感器触发等）
- **复用功能**：作为其他外设的信号线（UART、SPI、I2C等）


### GPIO工作模式

#### 输出模式

- **推挽输出（Push-Pull）**：可以输出强高电平和强低电平
- **开漏输出（Open-Drain）**：只能输出低电平，高电平需要外部上拉
- **复用推挽输出**：用于外设功能（如UART TX）
- **复用开漏输出**：用于外设功能（如I2C）

#### 输入模式

- **浮空输入（Floating）**：高阻态，易受干扰
- **上拉输入（Pull-Up）**：内部上拉电阻，默认高电平
- **下拉输入（Pull-Down）**：内部下拉电阻，默认低电平
- **模拟输入（Analog）**：用于ADC

#### 输出速度

- **低速（Low）**：2MHz，功耗低，EMI小
- **中速（Medium）**：25MHz
- **高速（High）**：50MHz
- **超高速（Very High）**：100MHz

### GPIO配置

#### STM32 HAL库配置示例

```c
#include "stm32f4xx_hal.h"

// GPIO初始化
void GPIO_Init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能GPIO时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    // 配置LED输出 (PA5)
    GPIO_InitStruct.Pin = GPIO_PIN_5;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;      // 推挽输出
    GPIO_InitStruct.Pull = GPIO_NOPULL;              // 无上下拉
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;     // 低速
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // 配置按键输入 (PC13)
    GPIO_InitStruct.Pin = GPIO_PIN_13;
    GPIO_InitStruct.Mode = GPIO_MODE_INPUT;          // 输入模式
    GPIO_InitStruct.Pull = GPIO_PULLUP;              // 上拉
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // 配置开漏输出 (PB0)
    GPIO_InitStruct.Pin = GPIO_PIN_0;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_OD;      // 开漏输出
    GPIO_InitStruct.Pull = GPIO_PULLUP;              // 外部或内部上拉
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
}
```

**代码说明**：
- 使用前必须使能GPIO端口时钟
- 推挽输出适用于大多数输出场景
- 按键输入通常配置为上拉模式
- 开漏输出需要上拉电阻

### GPIO输出操作

#### 基本输出控制

```c
// 设置引脚为高电平
void LED_On(void) {
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);
}

// 设置引脚为低电平
void LED_Off(void) {
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
}

// 翻转引脚状态
void LED_Toggle(void) {
    HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
}

// 读取输出引脚当前状态
GPIO_PinState LED_GetState(void) {
    return HAL_GPIO_ReadPin(GPIOA, GPIO_PIN_5);
}
```

#### 多引脚同时操作

```c
// 同时设置多个引脚
void GPIO_SetMultiplePins(void) {
    // 设置PA5和PA6为高电平
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5 | GPIO_PIN_6, GPIO_PIN_SET);
}

// 使用寄存器直接操作（更快）
void GPIO_FastWrite(uint16_t pins, GPIO_PinState state) {
    if (state == GPIO_PIN_SET) {
        GPIOA->BSRR = pins;  // 设置位
    } else {
        GPIOA->BSRR = (uint32_t)pins << 16;  // 复位位
    }
}

// 读取整个端口
uint16_t GPIO_ReadPort(void) {
    return (uint16_t)GPIOA->IDR;
}

// 写入整个端口
void GPIO_WritePort(uint16_t value) {
    GPIOA->ODR = value;
}
```

**代码说明**：
- HAL函数易用但速度较慢
- 直接操作寄存器速度更快，适用于时序要求严格的场景
- BSRR寄存器可以原子操作，避免读-改-写问题


### GPIO输入操作

#### 读取数字输入

```c
// 读取按键状态
GPIO_PinState Button_Read(void) {
    return HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13);
}

// 检查按键是否按下（低电平有效，上拉配置）
bool Button_IsPressed(void) {
    return (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET);
}

// 等待按键按下
void Button_WaitPress(void) {
    while (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_SET) {
        // 等待按键按下
    }
}

// 等待按键释放
void Button_WaitRelease(void) {
    while (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET) {
        // 等待按键释放
    }
}
```

#### 按键消抖

```c
// 软件消抖（延时法）
#define DEBOUNCE_DELAY_MS 50

bool Button_ReadDebounced(void) {
    if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET) {
        HAL_Delay(DEBOUNCE_DELAY_MS);  // 延时消抖
        if (HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13) == GPIO_PIN_RESET) {
            return true;  // 确认按下
        }
    }
    return false;
}

// 状态机消抖
typedef enum {
    BUTTON_IDLE,
    BUTTON_PRESSED,
    BUTTON_DEBOUNCING
} ButtonState_t;

ButtonState_t buttonState = BUTTON_IDLE;
uint32_t debounceTimer = 0;

bool Button_StateMachine(void) {
    bool buttonPressed = false;
    GPIO_PinState pinState = HAL_GPIO_ReadPin(GPIOC, GPIO_PIN_13);
    uint32_t currentTime = HAL_GetTick();
    
    switch (buttonState) {
        case BUTTON_IDLE:
            if (pinState == GPIO_PIN_RESET) {
                buttonState = BUTTON_DEBOUNCING;
                debounceTimer = currentTime;
            }
            break;
            
        case BUTTON_DEBOUNCING:
            if (currentTime - debounceTimer >= DEBOUNCE_DELAY_MS) {
                if (pinState == GPIO_PIN_RESET) {
                    buttonState = BUTTON_PRESSED;
                    buttonPressed = true;
                } else {
                    buttonState = BUTTON_IDLE;
                }
            }
            break;
            
        case BUTTON_PRESSED:
            if (pinState == GPIO_PIN_SET) {
                buttonState = BUTTON_IDLE;
            }
            break;
    }
    
    return buttonPressed;
}
```

**代码说明**：
- 机械按键存在抖动，需要消抖处理
- 延时法简单但会阻塞程序
- 状态机法不阻塞，适合RTOS环境

### GPIO中断

#### 配置外部中断

```c
// 配置GPIO中断
void GPIO_ConfigInterrupt(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能时钟
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    // 配置中断引脚 (PC13)
    GPIO_InitStruct.Pin = GPIO_PIN_13;
    GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;     // 下降沿触发
    GPIO_InitStruct.Pull = GPIO_PULLUP;              // 上拉
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    // 配置NVIC
    HAL_NVIC_SetPriority(EXTI15_10_IRQn, 5, 0);
    HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);
}

// 中断触发模式
// GPIO_MODE_IT_RISING       - 上升沿触发
// GPIO_MODE_IT_FALLING      - 下降沿触发
// GPIO_MODE_IT_RISING_FALLING - 双边沿触发
```

#### 中断处理函数

```c
// 中断回调函数
void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_13) {
        // 按键中断处理
        // 注意：在中断中应快速处理，避免耗时操作
        
        // 方法1：设置标志，在主循环处理
        buttonPressedFlag = 1;
        
        // 方法2：使用RTOS信号量通知任务
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xSemaphoreGiveFromISR(buttonSemaphore, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}

// EXTI中断处理函数
void EXTI15_10_IRQHandler(void) {
    HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_13);
}
```

**代码说明**：
- 中断回调函数应尽快返回
- 避免在中断中执行耗时操作
- 使用标志或信号量通知主程序或任务

#### 中断消抖

```c
// 中断中的软件消抖
volatile uint32_t lastInterruptTime = 0;
#define INTERRUPT_DEBOUNCE_MS 200

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == GPIO_PIN_13) {
        uint32_t currentTime = HAL_GetTick();
        
        // 检查是否在消抖时间内
        if (currentTime - lastInterruptTime > INTERRUPT_DEBOUNCE_MS) {
            lastInterruptTime = currentTime;
            
            // 处理按键事件
            buttonPressedFlag = 1;
        }
    }
}
```

### 实际应用示例

#### LED闪烁

```c
// 简单闪烁
void LED_Blink(uint32_t delayMs) {
    LED_On();
    HAL_Delay(delayMs);
    LED_Off();
    HAL_Delay(delayMs);
}

// RTOS任务中的LED闪烁
void LED_BlinkTask(void *pvParameters) {
    TickType_t xLastWakeTime = xTaskGetTickCount();
    const TickType_t xFrequency = pdMS_TO_TICKS(500);  // 500ms
    
    while(1) {
        LED_Toggle();
        vTaskDelayUntil(&xLastWakeTime, xFrequency);
    }
}

// PWM软件实现（呼吸灯效果）
void LED_Breathe(void) {
    for (int brightness = 0; brightness < 100; brightness++) {
        for (int i = 0; i < 100; i++) {
            if (i < brightness) {
                LED_On();
            } else {
                LED_Off();
            }
            HAL_Delay(1);  // 实际应用中应使用定时器
        }
    }
}
```

#### 多按键扫描

```c
// 按键定义
typedef struct {
    GPIO_TypeDef *port;
    uint16_t pin;
    GPIO_PinState activeState;
    bool lastState;
    bool currentState;
    uint32_t pressTime;
} Button_t;

Button_t buttons[] = {
    {GPIOC, GPIO_PIN_13, GPIO_PIN_RESET, false, false, 0},  // 按键1
    {GPIOC, GPIO_PIN_14, GPIO_PIN_RESET, false, false, 0},  // 按键2
    {GPIOC, GPIO_PIN_15, GPIO_PIN_RESET, false, false, 0},  // 按键3
};

#define NUM_BUTTONS (sizeof(buttons) / sizeof(Button_t))

// 按键扫描任务
void Button_ScanTask(void *pvParameters) {
    while(1) {
        for (int i = 0; i < NUM_BUTTONS; i++) {
            GPIO_PinState pinState = HAL_GPIO_ReadPin(buttons[i].port, 
                                                       buttons[i].pin);
            
            buttons[i].currentState = (pinState == buttons[i].activeState);
            
            // 检测按键按下事件
            if (buttons[i].currentState && !buttons[i].lastState) {
                buttons[i].pressTime = HAL_GetTick();
                // 触发按键按下事件
                OnButtonPressed(i);
            }
            
            // 检测按键释放事件
            if (!buttons[i].currentState && buttons[i].lastState) {
                uint32_t pressDuration = HAL_GetTick() - buttons[i].pressTime;
                // 触发按键释放事件
                OnButtonReleased(i, pressDuration);
            }
            
            buttons[i].lastState = buttons[i].currentState;
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));  // 10ms扫描周期
    }
}

// 按键事件处理
void OnButtonPressed(uint8_t buttonIndex) {
    UART_Printf("Button %d pressed\r\n", buttonIndex);
}

void OnButtonReleased(uint8_t buttonIndex, uint32_t duration) {
    if (duration > 2000) {
        UART_Printf("Button %d long press (%lu ms)\r\n", buttonIndex, duration);
    } else {
        UART_Printf("Button %d short press (%lu ms)\r\n", buttonIndex, duration);
    }
}
```

**代码说明**：
- 支持多个按键
- 检测按下和释放事件
- 区分短按和长按


### 最佳实践

!!! tip "GPIO使用最佳实践"
    - **初始化顺序**：先使能时钟，再配置GPIO
    - **选择合适的模式**：根据应用选择推挽或开漏输出
    - **配置上下拉**：输入引脚应配置上拉或下拉，避免浮空
    - **输出速度**：根据需要选择，低速可降低EMI和功耗
    - **消抖处理**：机械按键必须消抖
    - **中断优先级**：合理配置中断优先级，避免冲突
    - **快速响应**：中断处理函数应尽快返回
    - **保护电路**：输出引脚应有限流电阻，输入引脚应有保护电路

### 常见陷阱

!!! warning "注意事项"
    - **忘记使能时钟**：GPIO配置前必须使能端口时钟
    - **浮空输入**：未配置上下拉的输入引脚易受干扰
    - **输出电流超限**：单个引脚最大输出电流有限（通常20-25mA）
    - **端口总电流超限**：整个端口的总电流也有限制
    - **短路风险**：输出引脚直接连接电源或地会损坏MCU
    - **中断风暴**：未消抖的按键可能触发大量中断
    - **竞态条件**：多任务访问GPIO需要保护
    - **复用冲突**：同一引脚不能同时用于多个功能

## 实践练习

1. **LED控制**：实现LED闪烁、呼吸灯效果
2. **按键输入**：实现按键消抖和长短按检测
3. **中断应用**：使用外部中断响应按键事件
4. **多按键扫描**：实现矩阵键盘扫描
5. **状态机**：使用按键控制LED的多种状态

## 自测问题

??? question "推挽输出和开漏输出有什么区别？各适用于什么场景？"
    推挽和开漏是两种不同的输出模式。
    
    ??? success "答案"
        **推挽输出（Push-Pull）**：
        - 可以输出强高电平和强低电平
        - 输出阻抗低，驱动能力强
        - 不需要外部上拉电阻
        - 适用场景：
          - 驱动LED
          - 控制继电器
          - 大多数数字输出
        
        **开漏输出（Open-Drain）**：
        - 只能输出低电平，高电平需要外部上拉
        - 可以实现线与（Wired-AND）
        - 可以连接不同电压的设备
        - 适用场景：
          - I2C总线（需要线与功能）
          - 多个设备共享一根信号线
          - 电平转换（3.3V MCU连接5V设备）
        
        **选择建议**：
        - 默认使用推挽输出
        - 需要线与或电平转换时使用开漏
        - I2C、1-Wire等协议必须使用开漏

??? question "为什么输入引脚需要配置上拉或下拉？"
    上拉和下拉电阻为输入引脚提供确定的默认状态。
    
    ??? success "答案"
        **浮空输入的问题**：
        - 引脚处于高阻态，容易受干扰
        - 读取值不确定，可能随机变化
        - 可能导致误触发中断
        - 增加功耗（CMOS输入在中间电平时功耗大）
        
        **上拉电阻（Pull-Up）**：
        - 将引脚默认拉到高电平
        - 适用于低电平有效的信号（如按键）
        - 典型值：10kΩ-100kΩ
        
        **下拉电阻（Pull-Down）**：
        - 将引脚默认拉到低电平
        - 适用于高电平有效的信号
        
        **选择建议**：
        - 按键通常使用上拉（按下时接地）
        - 根据外部电路的默认状态选择
        - 如果外部已有上下拉，内部可以不配置

??? question "如何选择GPIO的输出速度？"
    输出速度影响信号质量、EMI和功耗。
    
    ??? success "答案"
        **输出速度等级**：
        - **低速（2MHz）**：上升/下降时间慢
        - **中速（25MHz）**：平衡性能和EMI
        - **高速（50MHz）**：快速信号切换
        - **超高速（100MHz）**：最快切换速度
        
        **影响因素**：
        1. **EMI（电磁干扰）**：
           - 速度越快，EMI越大
           - 低速可减少辐射干扰
        
        2. **功耗**：
           - 高速模式功耗更大
           - 低速可降低动态功耗
        
        3. **信号完整性**：
           - 高速适用于短距离、低容性负载
           - 长线或大容性负载可能需要降低速度
        
        **选择建议**：
        - LED、继电器：低速
        - 按键输入：低速
        - SPI、I2C：中速到高速
        - 高速通信：高速或超高速
        - 医疗器械：优先选择低速，减少EMI

??? question "为什么按键需要消抖？如何实现？"
    机械按键存在物理抖动现象。
    
    ??? success "答案"
        **抖动现象**：
        - 机械触点闭合/断开时会弹跳
        - 持续时间：5-20ms
        - 表现为多次快速的开关状态变化
        - 可能被误认为多次按键
        
        **消抖方法**：
        
        1. **硬件消抖**：
           - RC滤波电路
           - 施密特触发器
           - 专用消抖芯片
        
        2. **软件消抖 - 延时法**：
           ```c
           if (button_pressed) {
               delay(20ms);
               if (button_still_pressed) {
                   // 确认按下
               }
           }
           ```
           - 优点：简单
           - 缺点：阻塞程序
        
        3. **软件消抖 - 状态机法**：
           - 不阻塞程序
           - 适合RTOS环境
           - 可以检测长按、双击等
        
        4. **软件消抖 - 计数法**：
           - 连续N次采样结果一致才确认
           - 抗干扰能力强
        
        **医疗器械建议**：
        - 使用硬件+软件双重消抖
        - 消抖时间20-50ms
        - 记录按键事件日志

??? question "在医疗器械中使用GPIO需要注意什么？"
    医疗器械对可靠性和安全性有严格要求。
    
    ??? success "答案"
        **医疗器械GPIO使用要点**：
        
        1. **电气安全**：
           - 输入引脚添加保护电路（TVS、限流电阻）
           - 输出引脚添加限流电阻
           - 符合IEC 60601-1电气安全要求
        
        2. **可靠性**：
           - 所有输入引脚配置上下拉，避免浮空
           - 关键信号使用硬件消抖
           - 实现看门狗监控
        
        3. **EMC抗干扰**：
           - 使用低速输出减少EMI
           - 添加滤波电容
           - 符合IEC 60601-1-2 EMC要求
        
        4. **故障检测**：
           - 定期检测关键输入状态
           - 检测输出是否正常工作
           - 记录异常事件
        
        5. **冗余设计**：
           - 关键信号使用双通道
           - 实现故障安全机制
           - 紧急停止按钮
        
        6. **测试验证**：
           - 进行ESD测试
           - 验证所有边界条件
           - 长期可靠性测试

## 相关资源

- [中断处理](../rtos/interrupt-handling.md)
- [SPI通信协议](spi.md)
- [I2C通信协议](i2c.md)

## 参考文献

1. STM32F4xx Reference Manual - STMicroelectronics
2. IEC 60601-1:2005+AMD1:2012 - Medical electrical equipment
3. IEC 60601-1-2:2014 - EMC requirements for medical electrical equipment
4. "Embedded Systems Architecture" - Tammy Noergaard
5. "The Art of Electronics" - Paul Horowitz & Winfield Hill
