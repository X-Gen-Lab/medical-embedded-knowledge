---
title: SPI通信协议
description: 掌握SPI（串行外设接口）通信协议的原理、配置和实现，学习如何在医疗器械中使用SPI与传感器和外设通信
difficulty: 中级
estimated_time: 40分钟
tags:
- SPI
- 串行通信
- 硬件接口
- 传感器
- 外设通信
related_modules:
- zh/technical-knowledge/hardware-interfaces/i2c
- zh/technical-knowledge/hardware-interfaces/uart
- zh/technical-knowledge/rtos/interrupt-handling
last_updated: '2026-02-09'
version: '1.0'
language: zh
---

# SPI通信协议

## 学习目标

完成本模块后，你将能够：
- 理解SPI协议的工作原理和特点
- 配置SPI接口的时钟极性和相位
- 实现SPI主从设备通信
- 处理SPI通信中的常见问题
- 在医疗器械中安全可靠地使用SPI

## 前置知识

- 数字电路基础
- C语言位操作
- 中断处理机制
- 微控制器外设编程

## 内容

### 概念介绍

SPI（Serial Peripheral Interface，串行外设接口）是一种高速、全双工、同步的串行通信协议。它由Motorola公司开发，广泛应用于微控制器与外设（如传感器、存储器、显示器）之间的通信。

**SPI的主要特点**：
- **全双工通信**：可以同时发送和接收数据
- **高速传输**：速度可达数十MHz
- **主从架构**：一个主设备控制一个或多个从设备
- **简单硬件**：只需4根信号线（或3根用于单向通信）


**SPI信号线**：
- **SCLK (Serial Clock)**：时钟信号，由主设备产生
- **MOSI (Master Out Slave In)**：主设备输出，从设备输入
- **MISO (Master In Slave Out)**：主设备输入，从设备输出
- **SS/CS (Slave Select/Chip Select)**：片选信号，选择从设备

```
主设备                    从设备
┌─────────┐              ┌─────────┐
│         │─────SCLK────>│         │
│         │─────MOSI────>│         │
│  MCU    │<────MISO─────│ Sensor  │
│         │─────SS──────>│         │
└─────────┘              └─────────┘
```

**说明**: 这是SPI总线的硬件连接图。主设备(MCU)通过SCLK提供时钟，MOSI发送数据，MISO接收数据，SS选择从设备。SPI是全双工通信，可以同时发送和接收数据。


### SPI工作模式

SPI有4种工作模式，由时钟极性（CPOL）和时钟相位（CPHA）决定。

#### 时钟极性和相位

- **CPOL (Clock Polarity)**：时钟空闲时的电平
  - CPOL=0：空闲时时钟为低电平
  - CPOL=1：空闲时时钟为高电平

- **CPHA (Clock Phase)**：数据采样的时钟边沿
  - CPHA=0：在时钟的第一个边沿采样数据
  - CPHA=1：在时钟的第二个边沿采样数据

| 模式 | CPOL | CPHA | 空闲时钟 | 采样边沿 |
|------|------|------|----------|----------|
| 0    | 0    | 0    | 低       | 上升沿   |
| 1    | 0    | 1    | 低       | 下降沿   |
| 2    | 1    | 0    | 高       | 下降沿   |
| 3    | 1    | 1    | 高       | 上升沿   |

### SPI配置

#### STM32 HAL库配置示例

```c
#include "stm32f4xx_hal.h"

// SPI句柄
SPI_HandleTypeDef hspi1;

// SPI初始化
void SPI_Init(void) {
    // 配置SPI参数
    hspi1.Instance = SPI1;
    hspi1.Init.Mode = SPI_MODE_MASTER;           // 主模式
    hspi1.Init.Direction = SPI_DIRECTION_2LINES; // 全双工
    hspi1.Init.DataSize = SPI_DATASIZE_8BIT;     // 8位数据
    hspi1.Init.CLKPolarity = SPI_POLARITY_LOW;   // CPOL=0
    hspi1.Init.CLKPhase = SPI_PHASE_1EDGE;       // CPHA=0 (模式0)
    hspi1.Init.NSS = SPI_NSS_SOFT;               // 软件控制片选
    hspi1.Init.BaudRatePrescaler = SPI_BAUDRATEPRESCALER_16; // 分频系数
    hspi1.Init.FirstBit = SPI_FIRSTBIT_MSB;      // MSB先传输
    hspi1.Init.TIMode = SPI_TIMODE_DISABLE;
    hspi1.Init.CRCCalculation = SPI_CRCCALCULATION_DISABLE;
    
    if (HAL_SPI_Init(&hspi1) != HAL_OK) {
        // 初始化失败处理
        Error_Handler();
    }
}

// GPIO配置（在HAL_SPI_MspInit中调用）
void HAL_SPI_MspInit(SPI_HandleTypeDef* hspi) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    if(hspi->Instance == SPI1) {
        // 使能时钟
        __HAL_RCC_SPI1_CLK_ENABLE();
        __HAL_RCC_GPIOA_CLK_ENABLE();
        
        // 配置GPIO引脚
        // PA5: SPI1_SCK
        // PA6: SPI1_MISO
        // PA7: SPI1_MOSI
        GPIO_InitStruct.Pin = GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7;
        GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
        GPIO_InitStruct.Pull = GPIO_NOPULL;
        GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
        GPIO_InitStruct.Alternate = GPIO_AF5_SPI1;
        HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
        
        // 配置片选引脚（PA4）
        GPIO_InitStruct.Pin = GPIO_PIN_4;
        GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
        GPIO_InitStruct.Pull = GPIO_PULLUP;
        GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
        HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
        
        // 片选默认为高（未选中）
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
    }
}
```

**代码说明**：
- 配置SPI为主模式，8位数据，模式0（CPOL=0, CPHA=0）
- 使用软件控制片选，提供更灵活的控制
- 配置GPIO为复用推挽输出，高速模式
- 片选引脚初始化为高电平（未选中状态）


### SPI数据传输

#### 阻塞式传输

```c
// 片选控制宏
#define SPI_CS_LOW()   HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET)
#define SPI_CS_HIGH()  HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET)

// 发送单字节
HAL_StatusTypeDef SPI_WriteByte(uint8_t data) {
    HAL_StatusTypeDef status;
    
    SPI_CS_LOW();  // 选中从设备
    status = HAL_SPI_Transmit(&hspi1, &data, 1, HAL_MAX_DELAY);
    SPI_CS_HIGH(); // 释放从设备
    
    return status;
}

// 读取单字节
HAL_StatusTypeDef SPI_ReadByte(uint8_t *data) {
    HAL_StatusTypeDef status;
    
    SPI_CS_LOW();
    status = HAL_SPI_Receive(&hspi1, data, 1, HAL_MAX_DELAY);
    SPI_CS_HIGH();
    
    return status;
}

// 全双工传输
HAL_StatusTypeDef SPI_TransferByte(uint8_t txData, uint8_t *rxData) {
    HAL_StatusTypeDef status;
    
    SPI_CS_LOW();
    status = HAL_SPI_TransmitReceive(&hspi1, &txData, rxData, 1, HAL_MAX_DELAY);
    SPI_CS_HIGH();
    
    return status;
}

// 传输多字节
HAL_StatusTypeDef SPI_Transfer(uint8_t *txBuffer, uint8_t *rxBuffer, uint16_t size) {
    HAL_StatusTypeDef status;
    
    SPI_CS_LOW();
    status = HAL_SPI_TransmitReceive(&hspi1, txBuffer, rxBuffer, size, HAL_MAX_DELAY);
    SPI_CS_HIGH();
    
    return status;
}
```

**代码说明**：
- 传输前拉低片选，传输后拉高片选
- 使用HAL库提供的传输函数
- 全双工传输可以同时发送和接收数据

#### 中断方式传输

```c
// 中断传输完成标志
volatile uint8_t spiTxComplete = 0;
volatile uint8_t spiRxComplete = 0;

// 中断方式发送
HAL_StatusTypeDef SPI_WriteBytes_IT(uint8_t *data, uint16_t size) {
    HAL_StatusTypeDef status;
    
    spiTxComplete = 0;
    SPI_CS_LOW();
    
    status = HAL_SPI_Transmit_IT(&hspi1, data, size);
    
    if (status != HAL_OK) {
        SPI_CS_HIGH();
        return status;
    }
    
    // 等待传输完成（实际应用中应使用RTOS信号量）
    while (!spiTxComplete) {
        // 可以执行其他任务
    }
    
    SPI_CS_HIGH();
    return HAL_OK;
}

// 发送完成回调
void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi->Instance == SPI1) {
        spiTxComplete = 1;
    }
}

// 接收完成回调
void HAL_SPI_RxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi->Instance == SPI1) {
        spiRxComplete = 1;
    }
}

// 传输完成回调
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi->Instance == SPI1) {
        spiTxComplete = 1;
        spiRxComplete = 1;
    }
}

// 错误回调
void HAL_SPI_ErrorCallback(SPI_HandleTypeDef *hspi) {
    if (hspi->Instance == SPI1) {
        // 记录错误
        uint32_t error = HAL_SPI_GetError(hspi);
        logError("SPI Error: 0x%08X", error);
        
        // 释放片选
        SPI_CS_HIGH();
    }
}
```

**代码说明**：
- 使用中断方式可以在传输期间执行其他任务
- 通过回调函数通知传输完成
- 必须实现错误处理回调


#### DMA方式传输

```c
// DMA句柄（在HAL_SPI_MspInit中配置）
DMA_HandleTypeDef hdma_spi1_tx;
DMA_HandleTypeDef hdma_spi1_rx;

// DMA配置
void HAL_SPI_MspInit_DMA(SPI_HandleTypeDef* hspi) {
    if(hspi->Instance == SPI1) {
        // 使能DMA时钟
        __HAL_RCC_DMA2_CLK_ENABLE();
        
        // 配置TX DMA
        hdma_spi1_tx.Instance = DMA2_Stream3;
        hdma_spi1_tx.Init.Channel = DMA_CHANNEL_3;
        hdma_spi1_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
        hdma_spi1_tx.Init.PeriphInc = DMA_PINC_DISABLE;
        hdma_spi1_tx.Init.MemInc = DMA_MINC_ENABLE;
        hdma_spi1_tx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
        hdma_spi1_tx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
        hdma_spi1_tx.Init.Mode = DMA_NORMAL;
        hdma_spi1_tx.Init.Priority = DMA_PRIORITY_HIGH;
        HAL_DMA_Init(&hdma_spi1_tx);
        
        __HAL_LINKDMA(hspi, hdmatx, hdma_spi1_tx);
        
        // 配置RX DMA
        hdma_spi1_rx.Instance = DMA2_Stream2;
        hdma_spi1_rx.Init.Channel = DMA_CHANNEL_3;
        hdma_spi1_rx.Init.Direction = DMA_PERIPH_TO_MEMORY;
        hdma_spi1_rx.Init.PeriphInc = DMA_PINC_DISABLE;
        hdma_spi1_rx.Init.MemInc = DMA_MINC_ENABLE;
        hdma_spi1_rx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
        hdma_spi1_rx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
        hdma_spi1_rx.Init.Mode = DMA_NORMAL;
        hdma_spi1_rx.Init.Priority = DMA_PRIORITY_HIGH;
        HAL_DMA_Init(&hdma_spi1_rx);
        
        __HAL_LINKDMA(hspi, hdmarx, hdma_spi1_rx);
        
        // 配置DMA中断
        HAL_NVIC_SetPriority(DMA2_Stream3_IRQn, 5, 0);
        HAL_NVIC_EnableIRQ(DMA2_Stream3_IRQn);
        HAL_NVIC_SetPriority(DMA2_Stream2_IRQn, 5, 0);
        HAL_NVIC_EnableIRQ(DMA2_Stream2_IRQn);
    }
}

// DMA传输
HAL_StatusTypeDef SPI_Transfer_DMA(uint8_t *txBuffer, uint8_t *rxBuffer, uint16_t size) {
    HAL_StatusTypeDef status;
    
    SPI_CS_LOW();
    
    status = HAL_SPI_TransmitReceive_DMA(&hspi1, txBuffer, rxBuffer, size);
    
    if (status != HAL_OK) {
        SPI_CS_HIGH();
        return status;
    }
    
    return HAL_OK;
}

// DMA中断处理函数
void DMA2_Stream3_IRQHandler(void) {
    HAL_DMA_IRQHandler(&hdma_spi1_tx);
}

void DMA2_Stream2_IRQHandler(void) {
    HAL_DMA_IRQHandler(&hdma_spi1_rx);
}
```

**代码说明**：
- DMA方式适用于大量数据传输，CPU占用率低
- 需要配置TX和RX两个DMA通道
- 传输完成后在回调函数中释放片选

### 实际应用示例

#### 读取加速度传感器（ADXL345）

```c
// ADXL345寄存器地址
#define ADXL345_REG_DEVID       0x00
#define ADXL345_REG_POWER_CTL   0x2D
#define ADXL345_REG_DATA_FORMAT 0x31
#define ADXL345_REG_DATAX0      0x32

// 读写命令位
#define ADXL345_READ_BIT        0x80
#define ADXL345_MULTI_BYTE_BIT  0x40

// 写寄存器
HAL_StatusTypeDef ADXL345_WriteRegister(uint8_t reg, uint8_t value) {
    uint8_t txData[2];
    
    txData[0] = reg & 0x3F;  // 写命令（bit7=0）
    txData[1] = value;
    
    SPI_CS_LOW();
    HAL_StatusTypeDef status = HAL_SPI_Transmit(&hspi1, txData, 2, HAL_MAX_DELAY);
    SPI_CS_HIGH();
    
    return status;
}

// 读寄存器
HAL_StatusTypeDef ADXL345_ReadRegister(uint8_t reg, uint8_t *value) {
    uint8_t txData[2];
    uint8_t rxData[2];
    
    txData[0] = reg | ADXL345_READ_BIT;  // 读命令（bit7=1）
    txData[1] = 0x00;  // 虚拟字节
    
    SPI_CS_LOW();
    HAL_StatusTypeDef status = HAL_SPI_TransmitReceive(&hspi1, txData, rxData, 2, HAL_MAX_DELAY);
    SPI_CS_HIGH();
    
    if (status == HAL_OK) {
        *value = rxData[1];
    }
    
    return status;
}

// 读取多个寄存器
HAL_StatusTypeDef ADXL345_ReadRegisters(uint8_t reg, uint8_t *buffer, uint8_t count) {
    uint8_t txData[32];
    uint8_t rxData[32];
    
    if (count > 31) {
        return HAL_ERROR;
    }
    
    txData[0] = reg | ADXL345_READ_BIT | ADXL345_MULTI_BYTE_BIT;
    for (int i = 1; i <= count; i++) {
        txData[i] = 0x00;
    }
    
    SPI_CS_LOW();
    HAL_StatusTypeDef status = HAL_SPI_TransmitReceive(&hspi1, txData, rxData, count + 1, HAL_MAX_DELAY);
    SPI_CS_HIGH();
    
    if (status == HAL_OK) {
        memcpy(buffer, &rxData[1], count);
    }
    
    return status;
}

// 初始化ADXL345
HAL_StatusTypeDef ADXL345_Init(void) {
    uint8_t devId;
    
    // 读取设备ID验证通信
    if (ADXL345_ReadRegister(ADXL345_REG_DEVID, &devId) != HAL_OK) {
        return HAL_ERROR;
    }
    
    if (devId != 0xE5) {
        logError("ADXL345: Invalid device ID: 0x%02X", devId);
        return HAL_ERROR;
    }
    
    // 配置数据格式：±2g, 全分辨率
    ADXL345_WriteRegister(ADXL345_REG_DATA_FORMAT, 0x08);
    
    // 启动测量模式
    ADXL345_WriteRegister(ADXL345_REG_POWER_CTL, 0x08);
    
    return HAL_OK;
}

// 读取加速度数据
typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} AccelData_t;

HAL_StatusTypeDef ADXL345_ReadAccel(AccelData_t *accel) {
    uint8_t buffer[6];
    
    // 读取6个字节（X, Y, Z各2字节）
    if (ADXL345_ReadRegisters(ADXL345_REG_DATAX0, buffer, 6) != HAL_OK) {
        return HAL_ERROR;
    }
    
    // 组合成16位有符号整数
    accel->x = (int16_t)((buffer[1] << 8) | buffer[0]);
    accel->y = (int16_t)((buffer[3] << 8) | buffer[2]);
    accel->z = (int16_t)((buffer[5] << 8) | buffer[4]);
    
    return HAL_OK;
}
```

**代码说明**：
- ADXL345使用SPI模式3（CPOL=1, CPHA=1）
- 读命令需要设置bit7为1
- 多字节读取需要设置bit6为1
- 数据为小端格式（LSB在前）


### 最佳实践

!!! tip "SPI通信最佳实践"
    - **确认时钟模式**：仔细阅读外设数据手册，确认CPOL和CPHA设置
    - **控制传输速度**：根据外设规格和PCB布线质量选择合适的时钟频率
    - **片选时序**：确保片选信号在时钟之前拉低，在传输完成后拉高
    - **添加延时**：某些外设需要在片选和时钟之间添加延时
    - **错误处理**：检查每次传输的返回状态，实现超时和重试机制
    - **多从设备**：使用独立的片选信号控制每个从设备
    - **电气特性**：注意信号完整性，长距离传输需要考虑阻抗匹配
    - **中断优先级**：SPI中断优先级应高于应用任务，低于关键中断

### 常见陷阱

!!! warning "注意事项"
    - **时钟模式不匹配**：主从设备的CPOL和CPHA必须一致，否则数据错误
    - **片选时序错误**：片选信号在时钟期间变化会导致通信失败
    - **忘记释放片选**：传输后未拉高片选，导致从设备一直被选中
    - **缓冲区溢出**：接收缓冲区大小不足，导致数据丢失
    - **时钟频率过高**：超过外设最大频率，导致数据错误
    - **多主冲突**：多个主设备同时访问总线（SPI不支持多主）
    - **信号完整性**：长线传输、高速率时信号质量差
    - **忽略数据手册**：不同外设的SPI实现可能有细微差异

## 实践练习

1. **基础通信**：使用SPI读写一个简单的外设（如EEPROM）
2. **传感器接口**：实现与加速度计或温度传感器的SPI通信
3. **性能测试**：测试不同时钟频率下的传输可靠性
4. **多从设备**：实现一个主设备控制多个从设备的系统
5. **错误处理**：模拟通信错误，验证错误处理和恢复机制

## 自测问题

??? question "SPI的四种工作模式有什么区别？如何选择？"
    SPI的工作模式由CPOL和CPHA两个参数决定。
    
    ??? success "答案"
        **四种模式**：
        - **模式0** (CPOL=0, CPHA=0)：空闲低电平，上升沿采样
        - **模式1** (CPOL=0, CPHA=1)：空闲低电平，下降沿采样
        - **模式2** (CPOL=1, CPHA=0)：空闲高电平，下降沿采样
        - **模式3** (CPOL=1, CPHA=1)：空闲高电平，上升沿采样
        
        **选择方法**：
        1. 查阅从设备数据手册，确认支持的模式
        2. 主设备配置必须与从设备一致
        3. 模式0和模式3最常用
        4. 如果数据手册未明确说明，可以逐个尝试
        
        **注意**：时钟模式不匹配是SPI通信失败的最常见原因。

??? question "为什么SPI需要片选信号？可以省略吗？"
    片选信号用于选择要通信的从设备。
    
    ??? success "答案"
        **片选的作用**：
        1. **设备选择**：在多从设备系统中选择目标设备
        2. **同步起始**：标记传输的开始和结束
        3. **总线释放**：未选中的从设备释放MISO线
        4. **复位状态**：某些设备使用片选复位内部状态机
        
        **是否可以省略**：
        - 单从设备系统中，理论上可以将片选固定为低电平
        - 但不推荐，因为：
          - 失去了传输边界标记
          - 无法复位从设备状态
          - 增加了功耗（从设备一直激活）
          - 降低了系统灵活性
        
        **最佳实践**：始终使用片选信号，即使只有一个从设备。

??? question "SPI和I2C有什么区别？如何选择？"
    SPI和I2C都是常用的串行通信协议，但特点不同。
    
    ??? success "答案"
        **主要区别**：
        
        | 特性 | SPI | I2C |
        |------|-----|-----|
        | 速度 | 更快（可达数十MHz） | 较慢（标准100kHz，快速400kHz） |
        | 信号线 | 4根（多从设备需更多） | 2根（SCL, SDA） |
        | 通信方式 | 全双工 | 半双工 |
        | 从设备数量 | 受片选引脚限制 | 理论上127个（7位地址） |
        | 硬件复杂度 | 简单 | 需要上拉电阻 |
        | 多主支持 | 不支持 | 支持 |
        
        **选择建议**：
        - **选择SPI**：需要高速传输、全双工通信、从设备数量少
        - **选择I2C**：引脚资源紧张、需要多个从设备、需要多主支持
        - **医疗器械**：SPI更常用于高速传感器，I2C用于低速外设

??? question "如何调试SPI通信问题？"
    SPI通信问题的调试需要系统化的方法。
    
    ??? success "答案"
        **调试步骤**：
        
        1. **硬件检查**：
           - 使用示波器或逻辑分析仪查看信号
           - 检查时钟、数据线的波形质量
           - 确认片选时序正确
        
        2. **配置验证**：
           - 确认CPOL和CPHA设置正确
           - 检查时钟频率是否在外设规格范围内
           - 验证数据位宽（8位/16位）配置
        
        3. **软件调试**：
           - 添加日志记录每次传输的数据
           - 检查返回状态码
           - 验证缓冲区大小和数据对齐
        
        4. **常见问题**：
           - 读取到全0xFF或全0x00：通常是时钟模式错误
           - 数据错位：可能是字节序或位序问题
           - 间歇性错误：检查信号完整性和时序余量
        
        **工具**：逻辑分析仪是调试SPI的最佳工具，可以清晰看到时序关系。

??? question "在医疗器械中使用SPI需要注意什么？"
    医疗器械对可靠性和安全性有严格要求。
    
    ??? success "答案"
        **医疗器械SPI使用要点**：
        
        1. **可靠性**：
           - 实现CRC或校验和验证数据完整性
           - 添加超时和重试机制
           - 记录所有通信错误
        
        2. **确定性**：
           - 使用阻塞式传输或RTOS同步机制
           - 避免不确定的等待时间
           - 明确定义错误处理流程
        
        3. **可追溯性**：
           - 记录关键传输的日志
           - 实现诊断和自检功能
           - 保存错误历史
        
        4. **符合标准**：
           - 遵循IEC 60601-1电气安全要求
           - 满足IEC 62304软件开发流程
           - 考虑EMC抗干扰设计
        
        5. **测试验证**：
           - 进行边界条件测试
           - 验证错误处理路径
           - 进行长期稳定性测试

## 相关资源

- [I2C通信协议](i2c.md)
- [UART通信协议](uart.md)
- [中断处理](../rtos/interrupt-handling.md)

## 参考文献

1. SPI Block Guide V04.01 - Motorola/Freescale
2. STM32F4xx Reference Manual - STMicroelectronics
3. IEC 60601-1:2005+AMD1:2012 - Medical electrical equipment
4. "Embedded Systems Architecture" - Tammy Noergaard
5. "The Art of Designing Embedded Systems" - Jack Ganssle
