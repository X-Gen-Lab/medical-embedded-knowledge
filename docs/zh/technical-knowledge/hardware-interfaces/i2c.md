---
title: I2C通信协议
description: I2C总线协议原理、配置和在医疗器械中的应用
difficulty: 中级
estimated_time: 2小时
tags:
- I2C
- 硬件接口
- 通信协议
related_modules:
- zh/technical-knowledge/hardware-interfaces/spi
- zh/technical-knowledge/hardware-interfaces/uart
last_updated: '2026-02-07'
version: '1.0'
language: zh-CN
---

# I2C通信协议

## 学习目标

完成本模块后，你将能够：
- 理解I2C总线的工作原理和时序
- 配置和使用I2C外设
- 实现I2C设备驱动程序
- 处理I2C通信错误和异常
- 应用医疗器械中的I2C通信最佳实践

## 前置知识

- C语言基础
- 数字电路基础
- 嵌入式系统基础

## 内容

### I2C总线基础

I2C (Inter-Integrated Circuit) 是由Philips开发的两线式串行总线协议。

**特点**：
- 只需两根线：SDA（数据线）和SCL（时钟线）
- 支持多主机、多从机
- 标准速度：100 kbit/s，快速模式：400 kbit/s，高速模式：3.4 Mbit/s
- 7位或10位设备地址
- 半双工通信

**硬件连接**：

```
VDD
 │
 ├─── 4.7kΩ ─── 4.7kΩ
 │              │
SDA ────────────┼──────────┬──────────┬────
                │          │          │
SCL ────────────┼──────────┼──────────┼────
                │          │          │
              Master    Slave1    Slave2
```

**说明**: 这是I2C总线的硬件连接图。SDA和SCL都需要上拉电阻(通常4.7kΩ)连接到VDD，因为I2C使用开漏输出。多个设备可以并联在同一总线上，通过不同的地址进行通信。


### I2C协议时序

**起始条件（Start）**：
- SCL为高电平时，SDA从高到低跳变

**停止条件（Stop）**：
- SCL为高电平时，SDA从低到高跳变

**数据传输**：
- SCL为低电平时，SDA可以改变
- SCL为高电平时，SDA必须稳定（数据有效）
- 每字节传输后需要ACK/NACK

**基本时序图**：

```
SDA: ──┐     ┌───┬───┬───┬───┬───┬───┬───┬───┐   ┌──
       └─────┘ 7 │ 6 │ 5 │ 4 │ 3 │ 2 │ 1 │ 0 └───┘
SCL: ────┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌─┐ ┌──
         └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘ └─┘
     Start  D7  D6  D5  D4  D3  D2  D1  D0  ACK Stop
```

**说明**: 这是I2C数据传输的时序图。显示了起始条件、8位数据传输(D7-D0)、应答位(ACK)和停止条件的时序关系。数据在SCL高电平时有效，在SCL低电平时可以改变。


### I2C寄存器配置（STM32示例）

```c
#include "stm32f4xx.h"

// I2C初始化
void I2C1_Init(void) {
    // 使能I2C1和GPIOB时钟
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
    
    // 配置PB6(SCL)和PB7(SDA)为复用功能
    GPIOB->MODER |= (2 << 12) | (2 << 14);  // 复用模式
    GPIOB->AFR[0] |= (4 << 24) | (4 << 28); // AF4 = I2C1
    GPIOB->OTYPER |= (1 << 6) | (1 << 7);   // 开漏输出
    GPIOB->PUPDR |= (1 << 12) | (1 << 14);  // 上拉
    
    // 复位I2C1
    I2C1->CR1 |= I2C_CR1_SWRST;
    I2C1->CR1 &= ~I2C_CR1_SWRST;
    
    // 配置I2C时钟（假设APB1=42MHz，目标100kHz）
    I2C1->CR2 = 42;  // FREQ = 42MHz
    I2C1->CCR = 210; // CCR = 42MHz / (2 * 100kHz) = 210
    I2C1->TRISE = 43; // TRISE = (1000ns / 23.8ns) + 1 = 43
    
    // 使能I2C1
    I2C1->CR1 |= I2C_CR1_PE;
}

// 发送起始条件
void I2C1_Start(void) {
    I2C1->CR1 |= I2C_CR1_START;
    while (!(I2C1->SR1 & I2C_SR1_SB));  // 等待起始条件发送完成
}

// 发送停止条件
void I2C1_Stop(void) {
    I2C1->CR1 |= I2C_CR1_STOP;
}

// 发送地址
void I2C1_SendAddress(uint8_t address, uint8_t direction) {
    I2C1->DR = (address << 1) | direction;
    while (!(I2C1->SR1 & I2C_SR1_ADDR)); // 等待地址发送完成
    (void)I2C1->SR2;  // 读SR2清除ADDR标志
}

// 写一个字节
void I2C1_WriteByte(uint8_t data) {
    while (!(I2C1->SR1 & I2C_SR1_TXE)); // 等待发送缓冲区空
    I2C1->DR = data;
}

// 读一个字节
uint8_t I2C1_ReadByte(uint8_t ack) {
    if (ack) {
        I2C1->CR1 |= I2C_CR1_ACK;  // 使能ACK
    } else {
        I2C1->CR1 &= ~I2C_CR1_ACK; // 禁用ACK
    }
    
    while (!(I2C1->SR1 & I2C_SR1_RXNE)); // 等待接收缓冲区非空
    return I2C1->DR;
}
```

### I2C设备驱动示例

**EEPROM驱动（AT24C02）**：

```c
#include <stdint.h>
#include <stdbool.h>

#define EEPROM_ADDRESS  0x50  // 7位地址

// 写单字节
bool EEPROM_WriteByte(uint8_t mem_addr, uint8_t data) {
    I2C1_Start();
    I2C1_SendAddress(EEPROM_ADDRESS, 0);  // 写模式
    I2C1_WriteByte(mem_addr);
    I2C1_WriteByte(data);
    I2C1_Stop();
    
    // 等待写周期完成（~5ms）
    HAL_Delay(5);
    
    return true;
}

// 读单字节
bool EEPROM_ReadByte(uint8_t mem_addr, uint8_t* data) {
    // 写内存地址
    I2C1_Start();
    I2C1_SendAddress(EEPROM_ADDRESS, 0);  // 写模式
    I2C1_WriteByte(mem_addr);
    
    // 重新起始，读数据
    I2C1_Start();
    I2C1_SendAddress(EEPROM_ADDRESS, 1);  // 读模式
    *data = I2C1_ReadByte(0);  // NACK
    I2C1_Stop();
    
    return true;
}

// 页写（最多8字节）
bool EEPROM_WritePage(uint8_t mem_addr, const uint8_t* data, uint8_t len) {
    if (len > 8 || len == 0) {
        return false;
    }
    
    I2C1_Start();
    I2C1_SendAddress(EEPROM_ADDRESS, 0);
    I2C1_WriteByte(mem_addr);
    
    for (uint8_t i = 0; i < len; i++) {
        I2C1_WriteByte(data[i]);
    }
    
    I2C1_Stop();
    HAL_Delay(5);  // 写周期
    
    return true;
}

// 顺序读
bool EEPROM_ReadSequential(uint8_t mem_addr, uint8_t* data, uint8_t len) {
    if (len == 0) {
        return false;
    }
    
    // 写内存地址
    I2C1_Start();
    I2C1_SendAddress(EEPROM_ADDRESS, 0);
    I2C1_WriteByte(mem_addr);
    
    // 重新起始，读数据
    I2C1_Start();
    I2C1_SendAddress(EEPROM_ADDRESS, 1);
    
    for (uint8_t i = 0; i < len - 1; i++) {
        data[i] = I2C1_ReadByte(1);  // ACK
    }
    data[len - 1] = I2C1_ReadByte(0);  // 最后一个字节NACK
    
    I2C1_Stop();
    
    return true;
}
```

**温度传感器驱动（LM75）**：

```c
#define LM75_ADDRESS    0x48
#define LM75_REG_TEMP   0x00
#define LM75_REG_CONF   0x01

// 读取温度
bool LM75_ReadTemperature(float* temperature) {
    uint8_t data[2];
    
    // 写寄存器地址
    I2C1_Start();
    I2C1_SendAddress(LM75_ADDRESS, 0);
    I2C1_WriteByte(LM75_REG_TEMP);
    
    // 读取温度数据
    I2C1_Start();
    I2C1_SendAddress(LM75_ADDRESS, 1);
    data[0] = I2C1_ReadByte(1);  // 高字节，ACK
    data[1] = I2C1_ReadByte(0);  // 低字节，NACK
    I2C1_Stop();
    
    // 转换温度值（11位，0.125°C分辨率）
    int16_t temp_raw = (data[0] << 8) | data[1];
    temp_raw >>= 5;  // 右移5位，保留11位
    
    if (temp_raw & 0x0400) {  // 负温度
        temp_raw |= 0xF800;
    }
    
    *temperature = temp_raw * 0.125f;
    
    return true;
}

// 配置传感器
bool LM75_Configure(uint8_t config) {
    I2C1_Start();
    I2C1_SendAddress(LM75_ADDRESS, 0);
    I2C1_WriteByte(LM75_REG_CONF);
    I2C1_WriteByte(config);
    I2C1_Stop();
    
    return true;
}
```

### 错误处理

```c
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    I2C_OK = 0,
    I2C_ERROR_TIMEOUT,
    I2C_ERROR_NACK,
    I2C_ERROR_BUS_BUSY,
    I2C_ERROR_ARBITRATION_LOST
} i2c_status_t;

// 带超时的I2C写操作
i2c_status_t I2C_WriteWithTimeout(uint8_t dev_addr, 
                                   const uint8_t* data, 
                                   uint16_t len, 
                                   uint32_t timeout_ms) {
    uint32_t start_time = HAL_GetTick();
    
    // 检查总线忙
    while (I2C1->SR2 & I2C_SR2_BUSY) {
        if ((HAL_GetTick() - start_time) > timeout_ms) {
            return I2C_ERROR_BUS_BUSY;
        }
    }
    
    // 发送起始条件
    I2C1_Start();
    
    // 发送地址
    I2C1->DR = (dev_addr << 1);
    start_time = HAL_GetTick();
    while (!(I2C1->SR1 & I2C_SR1_ADDR)) {
        if (I2C1->SR1 & I2C_SR1_AF) {  // NACK
            I2C1_Stop();
            return I2C_ERROR_NACK;
        }
        if ((HAL_GetTick() - start_time) > timeout_ms) {
            I2C1_Stop();
            return I2C_ERROR_TIMEOUT;
        }
    }
    (void)I2C1->SR2;  // 清除ADDR
    
    // 发送数据
    for (uint16_t i = 0; i < len; i++) {
        start_time = HAL_GetTick();
        while (!(I2C1->SR1 & I2C_SR1_TXE)) {
            if ((HAL_GetTick() - start_time) > timeout_ms) {
                I2C1_Stop();
                return I2C_ERROR_TIMEOUT;
            }
        }
        I2C1->DR = data[i];
    }
    
    // 等待传输完成
    start_time = HAL_GetTick();
    while (!(I2C1->SR1 & I2C_SR1_BTF)) {
        if ((HAL_GetTick() - start_time) > timeout_ms) {
            I2C1_Stop();
            return I2C_ERROR_TIMEOUT;
        }
    }
    
    I2C1_Stop();
    return I2C_OK;
}

// 总线恢复
void I2C_BusRecovery(void) {
    // 禁用I2C外设
    I2C1->CR1 &= ~I2C_CR1_PE;
    
    // 配置SCL和SDA为GPIO输出
    GPIOB->MODER &= ~((3 << 12) | (3 << 14));
    GPIOB->MODER |= (1 << 12) | (1 << 14);  // 输出模式
    
    // 产生9个时钟脉冲
    for (int i = 0; i < 9; i++) {
        GPIOB->BSRR = (1 << 6);  // SCL高
        delay_us(5);
        GPIOB->BSRR = (1 << (6 + 16));  // SCL低
        delay_us(5);
    }
    
    // 发送停止条件
    GPIOB->BSRR = (1 << (7 + 16));  // SDA低
    delay_us(5);
    GPIOB->BSRR = (1 << 6);  // SCL高
    delay_us(5);
    GPIOB->BSRR = (1 << 7);  // SDA高
    delay_us(5);
    
    // 恢复I2C复用功能
    GPIOB->MODER &= ~((3 << 12) | (3 << 14));
    GPIOB->MODER |= (2 << 12) | (2 << 14);  // 复用模式
    
    // 重新初始化I2C
    I2C1_Init();
}
```

### 医疗器械中的I2C应用

**1. 传感器接口**：
- 温度传感器（体温监测）
- 加速度计（活动监测）
- 压力传感器（血压计）

**2. EEPROM存储**：
- 校准数据
- 配置参数
- 设备序列号

**3. RTC时钟**：
- 时间戳记录
- 定时任务

**最佳实践**：

```c
// 医疗器械I2C通信封装
typedef struct {
    uint8_t device_addr;
    uint32_t timeout_ms;
    uint8_t retry_count;
} i2c_device_t;

i2c_status_t medical_i2c_read(i2c_device_t* dev, 
                               uint8_t reg_addr,
                               uint8_t* data,
                               uint16_t len) {
    i2c_status_t status;
    
    for (uint8_t retry = 0; retry < dev->retry_count; retry++) {
        status = I2C_ReadWithTimeout(dev->device_addr, 
                                     reg_addr,
                                     data, 
                                     len,
                                     dev->timeout_ms);
        
        if (status == I2C_OK) {
            return I2C_OK;
        }
        
        // 记录错误
        log_i2c_error(dev->device_addr, status, retry);
        
        // 总线恢复
        if (status == I2C_ERROR_BUS_BUSY) {
            I2C_BusRecovery();
        }
        
        HAL_Delay(10);  // 重试延时
    }
    
    // 所有重试失败，触发错误处理
    handle_critical_i2c_failure(dev->device_addr);
    
    return status;
}
```

## 实践练习

1. 实现一个I2C扫描程序，检测总线上的所有设备
2. 编写EEPROM驱动，实现读写和校验
3. 实现一个温度传感器驱动，包含错误处理
4. 设计一个I2C总线监控工具，记录所有通信

## 相关资源

### 相关知识模块

- [SPI通信协议](spi.md) - 高速串行外设接口
- [UART通信协议](uart.md) - 通用异步收发传输器

### 深入学习

- [硬件接口概述](index.md) - 嵌入式系统常用硬件接口介绍
- [嵌入式C/C++编程](../embedded-c-cpp/index.md) - 指针操作和位操作技巧

## 参考文献

1. I2C-bus specification and user manual (NXP)
2. STM32 Reference Manual - I2C章节
3. IEC 62304:2006+AMD1:2015 - Medical device software
4. "Embedded Systems Architecture" by Tammy Noergaard
5. Application Note AN4235 - I2C timing configuration tool


## 自测问题

??? question "问题1：I2C总线的基本特点是什么？"
    **问题**：描述I2C总线的主要特点和优势。
    
    ??? success "答案"
        **I2C总线特点**：
        
        1. **双线通信**：
           - SDA（数据线）
           - SCL（时钟线）
           - 加上GND，只需3根线
        
        2. **多主多从**：
           - 支持多个主设备
           - 支持多个从设备（最多127个）
           - 通过地址识别设备
        
        3. **半双工通信**：
           - 同一时间只能单向传输
           - 主设备控制时钟
        
        4. **速度等级**：
           - 标准模式：100 kbit/s
           - 快速模式：400 kbit/s
           - 快速模式+：1 Mbit/s
           - 高速模式：3.4 Mbit/s
        
        5. **开漏输出**：
           - 需要上拉电阻
           - 支持总线仲裁
           - 允许多主设备
        
        **优势**：
        - 线路简单，节省引脚
        - 支持多设备
        - 广泛的器件支持
        - 适合短距离通信
        
        **知识点回顾**：I2C是嵌入式系统中最常用的通信协议之一。

??? question "问题2：I2C通信的基本时序是什么？"
    **问题**：描述I2C的起始条件、停止条件和数据传输时序。
    
    ??? success "答案"
        **I2C时序**：
        
        **1. 起始条件（Start Condition）**：
        ```
        SDA: ‾‾‾‾\____
        SCL: ‾‾‾‾‾‾‾‾‾
        ```

**说明**: 这是I2C起始条件的时序。当SCL为高电平时，SDA从高电平变为低电平，表示通信开始。这是I2C协议的特殊信号，用于通知所有设备准备接收数据。

        - SCL为高时，SDA从高到低
        - 表示通信开始
        
        **2. 停止条件（Stop Condition）**：
        ```
        SDA: ____/‾‾‾‾
        SCL: ‾‾‾‾‾‾‾‾‾
        ```

**说明**: 这是I2C停止条件的时序。当SCL为高电平时，SDA从低电平变为高电平，表示通信结束。这是I2C协议的特殊信号，用于释放总线。

        - SCL为高时，SDA从低到高
        - 表示通信结束
        
        **3. 数据传输**：
        ```
        SDA: ‾‾\__/‾‾\__/‾‾
        SCL: __/‾‾\__/‾‾\__
             数据位有效
        ```

**说明**: 这是I2C数据位传输的时序。数据在SCL低电平时可以改变，在SCL高电平时保持稳定并被采样。这确保了数据传输的可靠性。

        - SCL为低时，SDA可以变化
        - SCL为高时，SDA必须稳定
        - 每个字节后跟一个ACK/NACK位
        
        **4. 应答位（ACK/NACK）**：
        ```
        ACK:  SDA = 0（从设备拉低）
        NACK: SDA = 1（从设备释放）
        ```
        
        **完整传输示例**：
        ```
        START → 地址(7位) + R/W(1位) → ACK → 
        数据字节1 → ACK → 数据字节2 → ACK → 
        STOP
        ```
        
        **知识点回顾**：理解I2C时序是正确实现通信的基础。

??? question "问题3：如何实现I2C读写操作？"
    **问题**：编写代码实现I2C的基本读写操作。
    
    ??? success "答案"
        **I2C写操作**：
        
        ```c
        #include <stdint.h>
        #include <stdbool.h>
        
        // I2C写单个字节
        bool i2c_write_byte(uint8_t device_addr, uint8_t reg_addr, 
                           uint8_t data) {
            // 1. 发送起始条件
            i2c_start();
            
            // 2. 发送设备地址 + 写位(0)
            if (!i2c_send_byte((device_addr << 1) | 0)) {
                i2c_stop();
                return false;  // 无应答
            }
            
            // 3. 发送寄存器地址
            if (!i2c_send_byte(reg_addr)) {
                i2c_stop();
                return false;
            }
            
            // 4. 发送数据
            if (!i2c_send_byte(data)) {
                i2c_stop();
                return false;
            }
            
            // 5. 发送停止条件
            i2c_stop();
            return true;
        }
        
        // I2C写多个字节
        bool i2c_write_bytes(uint8_t device_addr, uint8_t reg_addr,
                            const uint8_t* data, uint8_t length) {
            i2c_start();
            
            if (!i2c_send_byte((device_addr << 1) | 0)) {
                i2c_stop();
                return false;
            }
            
            if (!i2c_send_byte(reg_addr)) {
                i2c_stop();
                return false;
            }
            
            for (uint8_t i = 0; i < length; i++) {
                if (!i2c_send_byte(data[i])) {
                    i2c_stop();
                    return false;
                }
            }
            
            i2c_stop();
            return true;
        }
        ```
        
        **I2C读操作**：
        
        ```c
        // I2C读单个字节
        bool i2c_read_byte(uint8_t device_addr, uint8_t reg_addr,
                          uint8_t* data) {
            // 1. 写寄存器地址
            i2c_start();
            if (!i2c_send_byte((device_addr << 1) | 0)) {
                i2c_stop();
                return false;
            }
            if (!i2c_send_byte(reg_addr)) {
                i2c_stop();
                return false;
            }
            
            // 2. 重新起始（Repeated Start）
            i2c_start();
            
            // 3. 发送设备地址 + 读位(1)
            if (!i2c_send_byte((device_addr << 1) | 1)) {
                i2c_stop();
                return false;
            }
            
            // 4. 读取数据，发送NACK
            *data = i2c_receive_byte(false);  // NACK
            
            // 5. 停止条件
            i2c_stop();
            return true;
        }
        
        // I2C读多个字节
        bool i2c_read_bytes(uint8_t device_addr, uint8_t reg_addr,
                           uint8_t* data, uint8_t length) {
            i2c_start();
            if (!i2c_send_byte((device_addr << 1) | 0)) {
                i2c_stop();
                return false;
            }
            if (!i2c_send_byte(reg_addr)) {
                i2c_stop();
                return false;
            }
            
            i2c_start();  // Repeated Start
            if (!i2c_send_byte((device_addr << 1) | 1)) {
                i2c_stop();
                return false;
            }
            
            for (uint8_t i = 0; i < length; i++) {
                // 最后一个字节发送NACK
                bool ack = (i < length - 1);
                data[i] = i2c_receive_byte(ack);
            }
            
            i2c_stop();
            return true;
        }
        ```
        
        **知识点回顾**：I2C读操作需要使用重复起始条件来切换方向。

??? question "问题4：I2C通信中常见的问题和解决方法"
    **问题**：列举I2C通信中常见的问题及其解决方法。
    
    ??? success "答案"
        **常见问题及解决方法**：
        
        **1. 总线挂起（Bus Hang）**：
        - **现象**：SDA或SCL被拉低，无法通信
        - **原因**：
          - 从设备等待时钟
          - 主设备复位时从设备处于传输中
        - **解决**：
          ```c
          // 发送9个时钟脉冲释放总线
          void i2c_bus_recovery(void) {
              for (int i = 0; i < 9; i++) {
                  scl_high();
                  delay_us(5);
                  scl_low();
                  delay_us(5);
              }
              i2c_stop();
          }
          ```
        
        **2. 地址冲突**：
        - **现象**：多个设备响应同一地址
        - **原因**：设备地址配置错误
        - **解决**：
          - 检查设备地址配置
          - 使用I2C扫描工具
          - 修改可配置地址
        
        **3. 上拉电阻不当**：
        - **现象**：通信不稳定或失败
        - **原因**：
          - 上拉电阻过大：上升沿慢
          - 上拉电阻过小：功耗大
        - **解决**：
          ```
          计算公式：
          R_pullup = (Vdd - 0.4V) / (3mA * N_devices)
          
          典型值：
          - 100kHz: 4.7kΩ - 10kΩ
          - 400kHz: 2.2kΩ - 4.7kΩ
          ```
        
        **4. 时序违规**：
        - **现象**：偶发通信失败
        - **原因**：时序参数不满足要求
        - **解决**：
          ```c
          // 确保满足时序要求
          #define I2C_DELAY_US  5  // 根据速度调整
          
          void i2c_scl_high(void) {
              SCL_HIGH();
              delay_us(I2C_DELAY_US);
          }
          
          void i2c_scl_low(void) {
              SCL_LOW();
              delay_us(I2C_DELAY_US);
          }
          ```
        
        **5. 电磁干扰**：
        - **现象**：长线通信不稳定
        - **解决**：
          - 使用屏蔽线
          - 降低通信速度
          - 添加滤波电容
          - 缩短线缆长度
        
        **调试技巧**：
        ```c
        // I2C总线扫描
        void i2c_scan(void) {
            printf("Scanning I2C bus...\n");
            for (uint8_t addr = 1; addr < 127; addr++) {
                i2c_start();
                if (i2c_send_byte(addr << 1)) {
                    printf("Device found at 0x%02X\n", addr);
                }
                i2c_stop();
            }
        }
        ```
        
        **知识点回顾**：了解常见问题有助于快速定位和解决I2C通信故障。

??? question "问题5：如何在医疗器械中安全使用I2C？"
    **问题**：在医疗器械软件中使用I2C通信时，需要考虑哪些安全因素？
    
    ??? success "答案"
        **医疗器械I2C安全考虑**：
        
        **1. 错误检测和处理**：
        ```c
        typedef enum {
            I2C_OK,
            I2C_ERROR_TIMEOUT,
            I2C_ERROR_NACK,
            I2C_ERROR_BUS_BUSY
        } i2c_status_t;
        
        i2c_status_t i2c_read_with_retry(uint8_t addr, uint8_t reg,
                                        uint8_t* data, uint8_t retries) {
            for (uint8_t i = 0; i < retries; i++) {
                i2c_status_t status = i2c_read_byte(addr, reg, data);
                if (status == I2C_OK) {
                    return I2C_OK;
                }
                delay_ms(10);  // 重试延迟
            }
            return I2C_ERROR_TIMEOUT;
        }
        ```
        
        **2. 超时保护**：
        ```c
        bool i2c_wait_ack(uint32_t timeout_ms) {
            uint32_t start = get_tick_ms();
            while (!i2c_check_ack()) {
                if (get_tick_ms() - start > timeout_ms) {
                    return false;  // 超时
                }
            }
            return true;
        }
        ```
        
        **3. 数据校验**：
        ```c
        // 使用CRC校验
        bool i2c_read_with_crc(uint8_t addr, uint8_t reg,
                              uint8_t* data, uint8_t length) {
            uint8_t buffer[length + 1];  // 数据 + CRC
            if (!i2c_read_bytes(addr, reg, buffer, length + 1)) {
                return false;
            }
            
            uint8_t crc = calculate_crc(buffer, length);
            if (crc != buffer[length]) {
                return false;  // CRC错误
            }
            
            memcpy(data, buffer, length);
            return true;
        }
        ```
        
        **4. 关键数据双读验证**：
        ```c
        bool i2c_read_critical_data(uint8_t addr, uint8_t reg,
                                   uint8_t* data) {
            uint8_t data1, data2;
            
            // 读取两次
            if (!i2c_read_byte(addr, reg, &data1)) {
                return false;
            }
            delay_ms(1);
            if (!i2c_read_byte(addr, reg, &data2)) {
                return false;
            }
            
            // 比较结果
            if (data1 != data2) {
                // 数据不一致，再读一次
                uint8_t data3;
                if (!i2c_read_byte(addr, reg, &data3)) {
                    return false;
                }
                // 多数表决
                if (data1 == data3) {
                    *data = data1;
                } else if (data2 == data3) {
                    *data = data2;
                } else {
                    return false;  // 无法确定
                }
            } else {
                *data = data1;
            }
            return true;
        }
        ```
        
        **5. 故障记录**：
        ```c
        typedef struct {
            uint32_t total_transactions;
            uint32_t failed_transactions;
            uint32_t timeout_count;
            uint32_t nack_count;
            uint32_t crc_error_count;
        } i2c_statistics_t;
        
        void i2c_log_error(i2c_status_t error) {
            stats.failed_transactions++;
            switch (error) {
                case I2C_ERROR_TIMEOUT:
                    stats.timeout_count++;
                    break;
                case I2C_ERROR_NACK:
                    stats.nack_count++;
                    break;
                // ...
            }
            log_event(EVENT_I2C_ERROR, error);
        }
        ```
        
        **6. 设备健康检查**：
        ```c
        bool i2c_device_health_check(uint8_t addr) {
            // 读取设备ID寄存器
            uint8_t device_id;
            if (!i2c_read_byte(addr, REG_DEVICE_ID, &device_id)) {
                return false;
            }
            
            // 验证ID
            if (device_id != EXPECTED_DEVICE_ID) {
                return false;
            }
            
            return true;
        }
        ```
        
        **知识点回顾**：在医疗器械中，I2C通信必须具备完善的错误检测和恢复机制。
