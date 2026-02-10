---
title: DMA（直接内存访问）
description: "掌握直接内存访问(DMA)技术在医疗设备中的应用，提高数据传输效率和系统性能"
difficulty: 高级
estimated_time: 3-4小时
last_updated: "2026-02-11"
version: "1.0"
language: "zh-CN"
tags:
  - dma
  - memory-management
  - performance
  - embedded-systems
---

# DMA（直接内存访问）

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

DMA（Direct Memory Access）允许外设直接访问内存，无需CPU干预，大幅提高数据传输效率并降低CPU负载。在医疗设备中，DMA广泛用于高速数据采集、图像传输和通信接口。

## 🎯 学习目标

- 理解DMA工作原理和优势
- 掌握DMA控制器配置
- 实现循环缓冲区设计
- 优化DMA与中断协作
- 确保数据一致性和安全性

## DMA基础

### 1. DMA工作原理

**传统数据传输 vs DMA传输**:

```c
// 传统方式：CPU参与每次传输
void traditional_transfer(uint8_t *src, uint8_t *dst, uint32_t size) {
    for (uint32_t i = 0; i < size; i++) {
        dst[i] = src[i];  // CPU执行每次复制
    }
}

// DMA方式：CPU只需配置，硬件自动传输
void dma_transfer(uint8_t *src, uint8_t *dst, uint32_t size) {
    // 配置DMA
    DMA_Stream->PAR = (uint32_t)src;   // 源地址
    DMA_Stream->M0AR = (uint32_t)dst;  // 目标地址
    DMA_Stream->NDTR = size;           // 传输大小
    
    // 启动DMA
    DMA_Stream->CR |= DMA_SxCR_EN;
    
    // CPU可以执行其他任务
    // DMA完成后触发中断
}
```

### 2. DMA优势

**性能提升**:
- CPU负载降低60-90%
- 数据传输速度提高
- 支持后台传输
- 降低功耗

**医疗设备应用**:
- 高速ADC数据采集（ECG、EEG）
- 图像传输（超声、X光）
- 串口/网络数据收发
- 音频数据处理

## DMA控制器配置

### 1. 基本配置

**STM32 DMA配置示例**:
```c
// DMA配置结构
typedef struct {
    uint32_t channel;           // DMA通道
    uint32_t direction;         // 传输方向
    uint32_t periph_inc;        // 外设地址递增
    uint32_t mem_inc;           // 内存地址递增
    uint32_t periph_data_size;  // 外设数据宽度
    uint32_t mem_data_size;     // 内存数据宽度
    uint32_t mode;              // 传输模式（正常/循环）
    uint32_t priority;          // 优先级
} dma_config_t;

// 初始化DMA用于ADC数据采集
void init_adc_dma(uint16_t *buffer, uint32_t buffer_size) {
    // 使能DMA时钟
    RCC->AHB1ENR |= RCC_AHB1ENR_DMA2EN;
    
    // 禁用DMA流以进行配置
    DMA2_Stream0->CR &= ~DMA_SxCR_EN;
    while (DMA2_Stream0->CR & DMA_SxCR_EN);
    
    // 配置DMA
    DMA2_Stream0->CR = 0;
    DMA2_Stream0->CR |= (0 << DMA_SxCR_CHSEL_Pos);  // 通道0
    DMA2_Stream0->CR |= DMA_SxCR_MINC;              // 内存地址递增
    DMA2_Stream0->CR |= DMA_SxCR_CIRC;              // 循环模式
    DMA2_Stream0->CR |= (1 << DMA_SxCR_MSIZE_Pos);  // 16位内存
    DMA2_Stream0->CR |= (1 << DMA_SxCR_PSIZE_Pos);  // 16位外设
    DMA2_Stream0->CR |= (2 << DMA_SxCR_PL_Pos);     // 高优先级
    
    // 设置地址和大小
    DMA2_Stream0->PAR = (uint32_t)&ADC1->DR;        // ADC数据寄存器
    DMA2_Stream0->M0AR = (uint32_t)buffer;          // 目标缓冲区
    DMA2_Stream0->NDTR = buffer_size;               // 传输数量
    
    // 使能传输完成中断
    DMA2_Stream0->CR |= DMA_SxCR_TCIE;
    NVIC_EnableIRQ(DMA2_Stream0_IRQn);
    
    // 启动DMA
    DMA2_Stream0->CR |= DMA_SxCR_EN;
}
```

### 2. 高级配置

**双缓冲模式**:
```c
// 双缓冲配置 - 一个缓冲区处理时，另一个接收数据
typedef struct {
    uint16_t buffer0[BUFFER_SIZE];
    uint16_t buffer1[BUFFER_SIZE];
    volatile uint8_t active_buffer;
} double_buffer_t;

double_buffer_t ecg_buffers;

void init_double_buffer_dma(void) {
    // 配置DMA双缓冲模式
    DMA2_Stream0->CR |= DMA_SxCR_DBM;  // 使能双缓冲
    
    // 设置两个缓冲区地址
    DMA2_Stream0->M0AR = (uint32_t)ecg_buffers.buffer0;
    DMA2_Stream0->M1AR = (uint32_t)ecg_buffers.buffer1;
    
    // 使能传输完成中断
    DMA2_Stream0->CR |= DMA_SxCR_TCIE;
    
    // 启动DMA
    DMA2_Stream0->CR |= DMA_SxCR_EN;
}

// DMA中断处理 - 自动切换缓冲区
void DMA2_Stream0_IRQHandler(void) {
    if (DMA2->LISR & DMA_LISR_TCIF0) {
        // 清除中断标志
        DMA2->LIFCR = DMA_LIFCR_CTCIF0;
        
        // 检查当前目标缓冲区
        if (DMA2_Stream0->CR & DMA_SxCR_CT) {
            // 当前使用buffer1，处理buffer0
            ecg_buffers.active_buffer = 0;
            process_ecg_buffer(ecg_buffers.buffer0, BUFFER_SIZE);
        } else {
            // 当前使用buffer0，处理buffer1
            ecg_buffers.active_buffer = 1;
            process_ecg_buffer(ecg_buffers.buffer1, BUFFER_SIZE);
        }
    }
}
```

## 循环缓冲区设计

### 1. 基本循环缓冲区

**实现原理**:
```c
// 循环缓冲区结构
typedef struct {
    uint16_t *buffer;
    uint32_t size;
    volatile uint32_t write_index;  // DMA写入位置
    volatile uint32_t read_index;   // CPU读取位置
} circular_buffer_t;

// 初始化循环缓冲区
void circular_buffer_init(circular_buffer_t *cb, uint16_t *buffer, uint32_t size) {
    cb->buffer = buffer;
    cb->size = size;
    cb->write_index = 0;
    cb->read_index = 0;
}

// 获取可读数据量
uint32_t circular_buffer_available(circular_buffer_t *cb) {
    uint32_t write_idx = cb->write_index;
    uint32_t read_idx = cb->read_index;
    
    if (write_idx >= read_idx) {
        return write_idx - read_idx;
    } else {
        return cb->size - read_idx + write_idx;
    }
}

// 读取数据
uint32_t circular_buffer_read(circular_buffer_t *cb, uint16_t *data, uint32_t count) {
    uint32_t available = circular_buffer_available(cb);
    uint32_t to_read = (count < available) ? count : available;
    
    for (uint32_t i = 0; i < to_read; i++) {
        data[i] = cb->buffer[cb->read_index];
        cb->read_index = (cb->read_index + 1) % cb->size;
    }
    
    return to_read;
}

// 更新DMA写入位置（在DMA中断中调用）
void circular_buffer_update_write_index(circular_buffer_t *cb) {
    // 从DMA控制器读取当前位置
    uint32_t remaining = DMA2_Stream0->NDTR;
    cb->write_index = cb->size - remaining;
}
```

### 2. 医疗设备应用：ECG数据采集

**完整实现**:
```c
// ECG采集系统配置
#define ECG_SAMPLE_RATE     1000    // 1kHz采样率
#define ECG_BUFFER_SIZE     2000    // 2秒数据
#define ECG_CHANNELS        12      // 12导联

typedef struct {
    uint16_t raw_buffer[ECG_BUFFER_SIZE * ECG_CHANNELS];
    circular_buffer_t circular_buf;
    uint32_t samples_processed;
    uint32_t overrun_count;
} ecg_acquisition_t;

ecg_acquisition_t ecg_system;

// 初始化ECG采集
void ecg_acquisition_init(void) {
    // 初始化循环缓冲区
    circular_buffer_init(&ecg_system.circular_buf,
                        ecg_system.raw_buffer,
                        ECG_BUFFER_SIZE * ECG_CHANNELS);
    
    // 配置ADC
    configure_adc_for_ecg();
    
    // 配置DMA
    init_adc_dma(ecg_system.raw_buffer, ECG_BUFFER_SIZE * ECG_CHANNELS);
    
    // 启动ADC
    ADC1->CR2 |= ADC_CR2_ADON;
}

// DMA半传输完成中断
void DMA2_Stream0_IRQHandler(void) {
    // 半传输完成
    if (DMA2->LISR & DMA_LISR_HTIF0) {
        DMA2->LIFCR = DMA_LIFCR_CHTIF0;
        
        // 更新写入索引
        circular_buffer_update_write_index(&ecg_system.circular_buf);
        
        // 通知处理任务
        notify_ecg_processing_task();
    }
    
    // 传输完成
    if (DMA2->LISR & DMA_LISR_TCIF0) {
        DMA2->LIFCR = DMA_LIFCR_CTCIF0;
        
        // 更新写入索引
        circular_buffer_update_write_index(&ecg_system.circular_buf);
        
        // 通知处理任务
        notify_ecg_processing_task();
    }
}

// ECG处理任务
void ecg_processing_task(void *param) {
    uint16_t sample_buffer[ECG_CHANNELS * 100];  // 100ms数据
    
    while (1) {
        // 等待数据就绪
        wait_for_ecg_data();
        
        // 读取数据
        uint32_t samples_read = circular_buffer_read(
            &ecg_system.circular_buf,
            sample_buffer,
            ECG_CHANNELS * 100
        );
        
        if (samples_read > 0) {
            // 处理ECG数据
            process_ecg_samples(sample_buffer, samples_read / ECG_CHANNELS);
            ecg_system.samples_processed += samples_read / ECG_CHANNELS;
        }
        
        // 检查缓冲区溢出
        if (circular_buffer_available(&ecg_system.circular_buf) > 
            ECG_BUFFER_SIZE * ECG_CHANNELS * 0.9) {
            ecg_system.overrun_count++;
            log_warning("ECG buffer near full");
        }
    }
}
```

## DMA与中断协作

### 1. 中断配置策略

**中断类型**:
```c
// DMA中断类型
typedef enum {
    DMA_INT_TRANSFER_COMPLETE = 0,  // 传输完成
    DMA_INT_HALF_TRANSFER,          // 半传输完成
    DMA_INT_TRANSFER_ERROR,         // 传输错误
    DMA_INT_DIRECT_MODE_ERROR,      // 直接模式错误
    DMA_INT_FIFO_ERROR              // FIFO错误
} dma_interrupt_type_t;

// 配置DMA中断
void configure_dma_interrupts(DMA_Stream_TypeDef *stream, uint32_t interrupts) {
    // 传输完成中断
    if (interrupts & (1 << DMA_INT_TRANSFER_COMPLETE)) {
        stream->CR |= DMA_SxCR_TCIE;
    }
    
    // 半传输完成中断
    if (interrupts & (1 << DMA_INT_HALF_TRANSFER)) {
        stream->CR |= DMA_SxCR_HTIE;
    }
    
    // 传输错误中断
    if (interrupts & (1 << DMA_INT_TRANSFER_ERROR)) {
        stream->CR |= DMA_SxCR_TEIE;
    }
    
    // 直接模式错误中断
    if (interrupts & (1 << DMA_INT_DIRECT_MODE_ERROR)) {
        stream->CR |= DMA_SxCR_DMEIE;
    }
    
    // FIFO错误中断
    if (interrupts & (1 << DMA_INT_FIFO_ERROR)) {
        stream->FCR |= DMA_SxFCR_FEIE;
    }
}
```

### 2. 中断优先级管理

**医疗设备中断优先级设计**:
```c
// 中断优先级定义
#define IRQ_PRIORITY_CRITICAL   0   // 关键生命支持
#define IRQ_PRIORITY_HIGH       1   // 实时数据采集
#define IRQ_PRIORITY_MEDIUM     2   // 通信
#define IRQ_PRIORITY_LOW        3   // 用户界面

// 配置中断优先级
void configure_interrupt_priorities(void) {
    // DMA用于ECG采集 - 高优先级
    NVIC_SetPriority(DMA2_Stream0_IRQn, IRQ_PRIORITY_HIGH);
    
    // DMA用于图像传输 - 中优先级
    NVIC_SetPriority(DMA2_Stream1_IRQn, IRQ_PRIORITY_MEDIUM);
    
    // DMA用于串口通信 - 低优先级
    NVIC_SetPriority(DMA1_Stream6_IRQn, IRQ_PRIORITY_LOW);
    
    // 使能中断
    NVIC_EnableIRQ(DMA2_Stream0_IRQn);
    NVIC_EnableIRQ(DMA2_Stream1_IRQn);
    NVIC_EnableIRQ(DMA1_Stream6_IRQn);
}
```

### 3. 中断处理最佳实践

**快速中断处理**:
```c
// 中断服务程序应尽可能短
void DMA2_Stream0_IRQHandler(void) {
    uint32_t start_time = get_cycle_count();
    
    // 快速检查和清除标志
    if (DMA2->LISR & DMA_LISR_TCIF0) {
        DMA2->LIFCR = DMA_LIFCR_CTCIF0;
        
        // 最小化处理 - 只设置标志
        ecg_data_ready = true;
        
        // 通知RTOS任务（不阻塞）
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        vTaskNotifyGiveFromISR(ecg_task_handle, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
    
    // 错误处理
    if (DMA2->LISR & DMA_LISR_TEIF0) {
        DMA2->LIFCR = DMA_LIFCR_CTEIF0;
        dma_error_count++;
        // 记录错误，在任务中处理
    }
    
    uint32_t isr_duration = get_cycle_count() - start_time;
    if (isr_duration > MAX_ISR_CYCLES) {
        log_warning("DMA ISR too long: %u cycles", isr_duration);
    }
}

// 在RTOS任务中处理数据
void ecg_processing_task(void *param) {
    while (1) {
        // 等待DMA中断通知
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
        
        // 处理数据（可以花费更多时间）
        process_ecg_data();
        
        // 执行复杂算法
        detect_arrhythmia();
        
        // 更新显示
        update_ecg_waveform();
    }
}
```

## 缓存一致性

### 1. 缓存管理

**DMA传输前后的缓存操作**:
```c
// 缓存行大小
#define CACHE_LINE_SIZE 32

// 对齐到缓存行的缓冲区
__attribute__((aligned(CACHE_LINE_SIZE)))
uint8_t dma_tx_buffer[DMA_BUFFER_SIZE];

__attribute__((aligned(CACHE_LINE_SIZE)))
uint8_t dma_rx_buffer[DMA_BUFFER_SIZE];

// DMA发送前清除缓存
void dma_transmit_with_cache(uint8_t *data, uint32_t size) {
    // 复制数据到DMA缓冲区
    memcpy(dma_tx_buffer, data, size);
    
    // 清除缓存（写回到内存）
    SCB_CleanDCache_by_Addr((uint32_t *)dma_tx_buffer, size);
    
    // 配置并启动DMA
    start_dma_transfer(dma_tx_buffer, UART_DR, size);
}

// DMA接收后使缓存无效
void dma_receive_with_cache(uint8_t *data, uint32_t size) {
    // 使接收缓冲区缓存无效
    SCB_InvalidateDCache_by_Addr((uint32_t *)dma_rx_buffer, size);
    
    // 配置并启动DMA
    start_dma_transfer(UART_DR, dma_rx_buffer, size);
    
    // 等待传输完成
    wait_dma_complete();
    
    // 再次使缓存无效（确保读取最新数据）
    SCB_InvalidateDCache_by_Addr((uint32_t *)dma_rx_buffer, size);
    
    // 复制数据
    memcpy(data, dma_rx_buffer, size);
}
```

### 2. 非缓存内存区域

**配置MPU使DMA缓冲区非缓存**:
```c
// 配置DMA缓冲区为非缓存区域
void configure_dma_memory_region(void) {
    // 禁用MPU
    MPU->CTRL = 0;
    
    // 配置DMA缓冲区区域
    MPU->RBAR = DMA_BUFFER_BASE | MPU_REGION_VALID | 0;
    MPU->RASR = MPU_REGION_SIZE_64KB |
                MPU_REGION_FULL_ACCESS |
                MPU_SHAREABLE |
                MPU_NON_CACHEABLE |  // 非缓存
                MPU_REGION_ENABLE;
    
    // 启用MPU
    MPU->CTRL = MPU_CTRL_ENABLE | MPU_CTRL_PRIVDEFENA;
    
    // 内存屏障
    __DSB();
    __ISB();
}

// 在非缓存区域分配DMA缓冲区
__attribute__((section(".dma_buffer")))
uint8_t dma_buffer[DMA_BUFFER_SIZE];

// 链接脚本配置
/*
MEMORY
{
    RAM (xrw)      : ORIGIN = 0x20000000, LENGTH = 128K
    DMA_RAM (xrw)  : ORIGIN = 0x20020000, LENGTH = 64K
}

SECTIONS
{
    .dma_buffer (NOLOAD) :
    {
        *(.dma_buffer)
    } > DMA_RAM
}
*/
```

## 性能优化

### 1. DMA传输优化

**批量传输**:
```c
// 批量DMA传输减少中断次数
#define BATCH_SIZE 1024

typedef struct {
    uint8_t data[BATCH_SIZE];
    uint32_t count;
    bool ready;
} dma_batch_t;

dma_batch_t tx_batch;

void queue_data_for_transmission(uint8_t *data, uint32_t size) {
    for (uint32_t i = 0; i < size; i++) {
        tx_batch.data[tx_batch.count++] = data[i];
        
        // 批次满时发送
        if (tx_batch.count >= BATCH_SIZE) {
            flush_tx_batch();
        }
    }
}

void flush_tx_batch(void) {
    if (tx_batch.count > 0) {
        // 启动DMA传输
        start_dma_transfer(tx_batch.data, UART_DR, tx_batch.count);
        tx_batch.count = 0;
    }
}
```

### 2. 突发传输

**配置DMA突发模式**:
```c
// 配置DMA突发传输提高效率
void configure_dma_burst_mode(DMA_Stream_TypeDef *stream) {
    // 配置内存突发传输（4次传输）
    stream->CR &= ~DMA_SxCR_MBURST;
    stream->CR |= (1 << DMA_SxCR_MBURST_Pos);  // INCR4
    
    // 配置外设突发传输（4次传输）
    stream->CR &= ~DMA_SxCR_PBURST;
    stream->CR |= (1 << DMA_SxCR_PBURST_Pos);  // INCR4
    
    // 配置FIFO
    stream->FCR |= DMA_SxFCR_DMDIS;  // 禁用直接模式
    stream->FCR &= ~DMA_SxFCR_FTH;
    stream->FCR |= (3 << DMA_SxFCR_FTH_Pos);  // 全FIFO阈值
}
```

### 3. 链式DMA

**链表DMA传输**:
```c
// DMA链表节点
typedef struct dma_node {
    uint32_t src_addr;
    uint32_t dst_addr;
    uint32_t size;
    struct dma_node *next;
} dma_node_t;

// 配置链式DMA传输
void configure_linked_dma(dma_node_t *first_node) {
    dma_node_t *current = first_node;
    
    while (current != NULL) {
        // 配置当前传输
        DMA_Stream->PAR = current->src_addr;
        DMA_Stream->M0AR = current->dst_addr;
        DMA_Stream->NDTR = current->size;
        
        // 启动传输
        DMA_Stream->CR |= DMA_SxCR_EN;
        
        // 等待完成
        while (!(DMA2->LISR & DMA_LISR_TCIF0));
        DMA2->LIFCR = DMA_LIFCR_CTCIF0;
        
        // 下一个节点
        current = current->next;
    }
}

// 医疗图像传输示例
void transfer_medical_image(medical_image_t *image) {
    // 创建DMA链表
    dma_node_t nodes[3];
    
    // 节点0: 传输图像头
    nodes[0].src_addr = (uint32_t)&image->header;
    nodes[0].dst_addr = (uint32_t)&network_buffer;
    nodes[0].size = sizeof(image_header_t);
    nodes[0].next = &nodes[1];
    
    // 节点1: 传输图像数据
    nodes[1].src_addr = (uint32_t)image->data;
    nodes[1].dst_addr = (uint32_t)&network_buffer[sizeof(image_header_t)];
    nodes[1].size = image->data_size;
    nodes[1].next = &nodes[2];
    
    // 节点2: 传输校验和
    nodes[2].src_addr = (uint32_t)&image->checksum;
    nodes[2].dst_addr = (uint32_t)&network_buffer[sizeof(image_header_t) + image->data_size];
    nodes[2].size = sizeof(uint32_t);
    nodes[2].next = NULL;
    
    // 执行链式传输
    configure_linked_dma(&nodes[0]);
}
```

## 医疗设备应用实例

### 1. 超声成像系统

**高速图像数据采集**:
```c
// 超声图像采集系统
#define ULTRASOUND_WIDTH    640
#define ULTRASOUND_HEIGHT   480
#define ULTRASOUND_FPS      30
#define BYTES_PER_PIXEL     2

typedef struct {
    uint16_t frame_buffer[2][ULTRASOUND_WIDTH * ULTRASOUND_HEIGHT];
    uint8_t active_buffer;
    uint32_t frame_count;
    uint32_t dropped_frames;
} ultrasound_system_t;

ultrasound_system_t us_system;

// 初始化超声DMA
void init_ultrasound_dma(void) {
    // 配置DMA双缓冲模式
    DMA2_Stream1->CR = 0;
    DMA2_Stream1->CR |= DMA_SxCR_DBM;           // 双缓冲
    DMA2_Stream1->CR |= DMA_SxCR_CIRC;          // 循环模式
    DMA2_Stream1->CR |= DMA_SxCR_MINC;          // 内存递增
    DMA2_Stream1->CR |= (1 << DMA_SxCR_MSIZE_Pos);  // 16位
    DMA2_Stream1->CR |= (1 << DMA_SxCR_PSIZE_Pos);  // 16位
    DMA2_Stream1->CR |= (3 << DMA_SxCR_PL_Pos);     // 最高优先级
    
    // 配置突发传输
    DMA2_Stream1->CR |= (2 << DMA_SxCR_MBURST_Pos);  // INCR8
    DMA2_Stream1->FCR |= DMA_SxFCR_DMDIS;
    DMA2_Stream1->FCR |= (3 << DMA_SxFCR_FTH_Pos);
    
    // 设置地址
    DMA2_Stream1->PAR = (uint32_t)&ADC_DATA_REG;
    DMA2_Stream1->M0AR = (uint32_t)us_system.frame_buffer[0];
    DMA2_Stream1->M1AR = (uint32_t)us_system.frame_buffer[1];
    DMA2_Stream1->NDTR = ULTRASOUND_WIDTH * ULTRASOUND_HEIGHT;
    
    // 使能中断
    DMA2_Stream1->CR |= DMA_SxCR_TCIE;
    NVIC_SetPriority(DMA2_Stream1_IRQn, IRQ_PRIORITY_HIGH);
    NVIC_EnableIRQ(DMA2_Stream1_IRQn);
    
    // 启动DMA
    DMA2_Stream1->CR |= DMA_SxCR_EN;
}

// DMA中断 - 帧完成
void DMA2_Stream1_IRQHandler(void) {
    if (DMA2->LISR & DMA_LISR_TCIF1) {
        DMA2->LIFCR = DMA_LIFCR_CTCIF1;
        
        // 确定完成的缓冲区
        uint8_t completed_buffer = (DMA2_Stream1->CR & DMA_SxCR_CT) ? 0 : 1;
        
        // 通知图像处理任务
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        xQueueSendFromISR(frame_queue, &completed_buffer, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
        
        us_system.frame_count++;
    }
}

// 图像处理任务
void ultrasound_processing_task(void *param) {
    uint8_t buffer_id;
    
    while (1) {
        // 等待新帧
        if (xQueueReceive(frame_queue, &buffer_id, pdMS_TO_TICKS(100)) == pdTRUE) {
            // 处理图像
            process_ultrasound_frame(us_system.frame_buffer[buffer_id]);
            
            // 应用滤波
            apply_image_filters(us_system.frame_buffer[buffer_id]);
            
            // 发送到显示
            send_to_display(us_system.frame_buffer[buffer_id]);
        } else {
            us_system.dropped_frames++;
        }
    }
}
```

### 2. 多通道生理监护

**同步多通道数据采集**:
```c
// 多通道监护系统
#define NUM_CHANNELS 8
#define SAMPLES_PER_CHANNEL 1000

typedef struct {
    uint16_t channel_data[NUM_CHANNELS][SAMPLES_PER_CHANNEL];
    uint32_t sample_index;
    bool data_ready[NUM_CHANNELS];
} multi_channel_monitor_t;

multi_channel_monitor_t monitor;

// 配置多个DMA流用于不同通道
void init_multi_channel_dma(void) {
    // ECG通道 (DMA2 Stream0)
    configure_channel_dma(DMA2_Stream0, 
                         &ADC1->DR,
                         monitor.channel_data[0],
                         SAMPLES_PER_CHANNEL);
    
    // SpO2通道 (DMA2 Stream1)
    configure_channel_dma(DMA2_Stream1,
                         &ADC2->DR,
                         monitor.channel_data[1],
                         SAMPLES_PER_CHANNEL);
    
    // 血压通道 (DMA2 Stream2)
    configure_channel_dma(DMA2_Stream2,
                         &ADC3->DR,
                         monitor.channel_data[2],
                         SAMPLES_PER_CHANNEL);
    
    // 启动所有DMA流
    start_all_dma_streams();
}

void configure_channel_dma(DMA_Stream_TypeDef *stream,
                          volatile uint32_t *periph_addr,
                          uint16_t *mem_addr,
                          uint32_t size) {
    stream->CR = 0;
    stream->CR |= DMA_SxCR_CIRC;    // 循环模式
    stream->CR |= DMA_SxCR_MINC;    // 内存递增
    stream->CR |= (1 << DMA_SxCR_MSIZE_Pos);
    stream->CR |= (1 << DMA_SxCR_PSIZE_Pos);
    stream->CR |= DMA_SxCR_TCIE;    // 传输完成中断
    
    stream->PAR = (uint32_t)periph_addr;
    stream->M0AR = (uint32_t)mem_addr;
    stream->NDTR = size;
    
    stream->CR |= DMA_SxCR_EN;
}
```

## 错误处理与恢复

### 1. DMA错误检测

**错误类型和处理**:
```c
// DMA错误统计
typedef struct {
    uint32_t transfer_errors;
    uint32_t fifo_errors;
    uint32_t direct_mode_errors;
    uint32_t timeout_errors;
} dma_error_stats_t;

dma_error_stats_t dma_errors;

// DMA错误处理
void handle_dma_errors(DMA_Stream_TypeDef *stream) {
    uint32_t isr_flags;
    
    // 读取中断状态
    if (stream == DMA2_Stream0) {
        isr_flags = DMA2->LISR;
    } else {
        isr_flags = DMA2->HISR;
    }
    
    // 传输错误
    if (isr_flags & DMA_LISR_TEIF0) {
        dma_errors.transfer_errors++;
        DMA2->LIFCR = DMA_LIFCR_CTEIF0;
        
        // 重新配置DMA
        reinit_dma_stream(stream);
        log_error("DMA transfer error");
    }
    
    // FIFO错误
    if (isr_flags & DMA_LISR_FEIF0) {
        dma_errors.fifo_errors++;
        DMA2->LIFCR = DMA_LIFCR_CFEIF0;
        
        // 调整FIFO阈值
        adjust_fifo_threshold(stream);
        log_error("DMA FIFO error");
    }
    
    // 直接模式错误
    if (isr_flags & DMA_LISR_DMEIF0) {
        dma_errors.direct_mode_errors++;
        DMA2->LIFCR = DMA_LIFCR_CDMEIF0;
        log_error("DMA direct mode error");
    }
}

// 重新初始化DMA流
void reinit_dma_stream(DMA_Stream_TypeDef *stream) {
    // 禁用DMA
    stream->CR &= ~DMA_SxCR_EN;
    while (stream->CR & DMA_SxCR_EN);
    
    // 清除所有标志
    if (stream == DMA2_Stream0) {
        DMA2->LIFCR = 0x3F;
    }
    
    // 重新配置
    configure_dma_stream(stream);
    
    // 重新启动
    stream->CR |= DMA_SxCR_EN;
}
```

### 2. 超时保护

**DMA传输超时检测**:
```c
// DMA传输超时监控
typedef struct {
    uint32_t start_time;
    uint32_t timeout_ms;
    bool is_active;
} dma_timeout_t;

dma_timeout_t dma_timeouts[8];  // 每个DMA流一个

// 启动DMA传输并设置超时
bool start_dma_with_timeout(DMA_Stream_TypeDef *stream, 
                           uint32_t stream_id,
                           uint32_t timeout_ms) {
    // 记录开始时间
    dma_timeouts[stream_id].start_time = get_tick_count();
    dma_timeouts[stream_id].timeout_ms = timeout_ms;
    dma_timeouts[stream_id].is_active = true;
    
    // 启动DMA
    stream->CR |= DMA_SxCR_EN;
    
    return true;
}

// 超时监控任务
void dma_timeout_monitor_task(void *param) {
    while (1) {
        for (uint32_t i = 0; i < 8; i++) {
            if (dma_timeouts[i].is_active) {
                uint32_t elapsed = get_tick_count() - dma_timeouts[i].start_time;
                
                if (elapsed > dma_timeouts[i].timeout_ms) {
                    // 超时处理
                    handle_dma_timeout(i);
                    dma_timeouts[i].is_active = false;
                    dma_errors.timeout_errors++;
                }
            }
        }
        
        vTaskDelay(pdMS_TO_TICKS(10));
    }
}

void handle_dma_timeout(uint32_t stream_id) {
    log_error("DMA stream %u timeout", stream_id);
    
    // 停止DMA
    DMA_Stream_TypeDef *stream = get_dma_stream(stream_id);
    stream->CR &= ~DMA_SxCR_EN;
    
    // 重新初始化
    reinit_dma_stream(stream);
    
    // 通知系统
    notify_system_error(ERROR_DMA_TIMEOUT);
}
```

## 调试技巧

### 1. DMA状态监控

**实时监控工具**:
```c
// DMA状态结构
typedef struct {
    bool is_enabled;
    uint32_t remaining_transfers;
    uint32_t current_target;  // 双缓冲模式
    uint32_t total_transfers;
    uint32_t transfer_rate;   // 传输速率
} dma_status_t;

// 读取DMA状态
void get_dma_status(DMA_Stream_TypeDef *stream, dma_status_t *status) {
    status->is_enabled = (stream->CR & DMA_SxCR_EN) != 0;
    status->remaining_transfers = stream->NDTR;
    status->current_target = (stream->CR & DMA_SxCR_CT) ? 1 : 0;
    
    // 计算传输速率
    static uint32_t last_count = 0;
    static uint32_t last_time = 0;
    uint32_t current_time = get_tick_count();
    uint32_t current_count = status->total_transfers;
    
    if (current_time > last_time) {
        status->transfer_rate = (current_count - last_count) * 1000 / 
                               (current_time - last_time);
    }
    
    last_count = current_count;
    last_time = current_time;
}

// 打印DMA状态
void print_dma_status(void) {
    dma_status_t status;
    
    printf("DMA Status Report:\n");
    for (uint32_t i = 0; i < 8; i++) {
        DMA_Stream_TypeDef *stream = get_dma_stream(i);
        get_dma_status(stream, &status);
        
        printf("Stream %u: %s, Remaining: %u, Rate: %u/s\n",
               i,
               status.is_enabled ? "ENABLED" : "DISABLED",
               status.remaining_transfers,
               status.transfer_rate);
    }
    
    printf("Errors: TE=%u, FE=%u, DME=%u, TO=%u\n",
           dma_errors.transfer_errors,
           dma_errors.fifo_errors,
           dma_errors.direct_mode_errors,
           dma_errors.timeout_errors);
}
```

### 2. 性能分析

**DMA性能测量**:
```c
// 性能测量工具
typedef struct {
    uint32_t total_bytes;
    uint32_t total_time_us;
    uint32_t min_transfer_time;
    uint32_t max_transfer_time;
    uint32_t avg_transfer_time;
} dma_performance_t;

dma_performance_t dma_perf;

// 测量DMA传输性能
void measure_dma_performance(void *src, void *dst, uint32_t size) {
    uint32_t start_time = get_microseconds();
    
    // 启动DMA传输
    start_dma_transfer(src, dst, size);
    
    // 等待完成
    wait_dma_complete();
    
    uint32_t elapsed = get_microseconds() - start_time;
    
    // 更新统计
    dma_perf.total_bytes += size;
    dma_perf.total_time_us += elapsed;
    
    if (elapsed < dma_perf.min_transfer_time || dma_perf.min_transfer_time == 0) {
        dma_perf.min_transfer_time = elapsed;
    }
    
    if (elapsed > dma_perf.max_transfer_time) {
        dma_perf.max_transfer_time = elapsed;
    }
    
    dma_perf.avg_transfer_time = dma_perf.total_time_us / 
                                 (dma_perf.total_bytes / size);
    
    // 计算吞吐量
    float throughput_mbps = (float)size * 8 / elapsed;
    printf("DMA Transfer: %u bytes in %u us (%.2f Mbps)\n",
           size, elapsed, throughput_mbps);
}
```

## 最佳实践

### 1. 设计原则

- **使用循环缓冲区**: 避免数据丢失
- **双缓冲模式**: 实现零拷贝处理
- **对齐缓冲区**: 提高传输效率
- **配置合适的优先级**: 关键数据高优先级
- **使能错误中断**: 及时发现问题
- **缓存管理**: 确保数据一致性

### 2. 常见陷阱

**陷阱1: 缓冲区未对齐**
```c
// 错误：未对齐的缓冲区可能导致性能下降
uint8_t buffer[1024];

// 正确：对齐到缓存行
__attribute__((aligned(32)))
uint8_t buffer[1024];
```

**陷阱2: 忘记缓存管理**
```c
// 错误：DMA写入后直接读取可能读到旧数据
start_dma_receive(buffer, size);
wait_dma_complete();
uint32_t value = buffer[0];  // 可能是缓存中的旧值

// 正确：使缓存无效
start_dma_receive(buffer, size);
wait_dma_complete();
SCB_InvalidateDCache_by_Addr((uint32_t *)buffer, size);
uint32_t value = buffer[0];
```

**陷阱3: 中断处理过长**
```c
// 错误：在中断中处理大量数据
void DMA_IRQHandler(void) {
    // 清除标志
    clear_dma_flags();
    
    // 错误：处理时间过长
    for (int i = 0; i < 1000; i++) {
        process_sample(buffer[i]);
    }
}

// 正确：只设置标志，在任务中处理
void DMA_IRQHandler(void) {
    clear_dma_flags();
    data_ready = true;
    notify_processing_task();  // 快速返回
}
```

### 3. 性能优化清单

- [ ] 使用DMA而非CPU复制数据
- [ ] 配置突发传输模式
- [ ] 使用双缓冲减少延迟
- [ ] 批量传输减少中断次数
- [ ] 配置非缓存内存区域（适当场景）
- [ ] 优化中断优先级
- [ ] 监控DMA性能指标
- [ ] 实现错误恢复机制

## 合规性要求

### IEC 62304要求

**软件设计文档**:
- DMA配置说明
- 数据流图
- 缓冲区管理策略
- 错误处理机制

**风险分析**:
- DMA传输失败风险
- 数据丢失风险
- 缓冲区溢出风险
- 缓存一致性问题

**验证测试**:
- DMA功能测试
- 性能基准测试
- 错误注入测试
- 长时间稳定性测试

### FDA指南

**数据完整性**:
- 传输错误检测
- 数据校验机制
- 审计日志
- 故障恢复

## 工具与资源

### 开发工具

**调试器**:
- Segger J-Link（DMA监控）
- Lauterbach TRACE32
- ST-Link（STM32）

**分析工具**:
- 逻辑分析仪（验证时序）
- 示波器（信号质量）
- 性能分析器

### 参考资料

**技术文档**:
- STM32 DMA应用笔记
- ARM AMBA DMA规范
- 处理器参考手册

**标准规范**:
- IEC 62304: 医疗设备软件
- IEC 60601-1: 医疗电气设备安全
- MISRA C: 编码标准

## 总结

DMA是提高医疗设备性能的关键技术。关键要点：

1. **正确配置**: 选择合适的传输模式和参数
2. **缓冲区设计**: 使用循环缓冲区和双缓冲
3. **中断管理**: 快速中断处理，任务中处理数据
4. **缓存一致性**: 正确管理缓存操作
5. **错误处理**: 实现完善的错误检测和恢复
6. **性能优化**: 突发传输、批量处理、优先级配置
7. **合规性**: 满足医疗设备标准要求

通过合理使用DMA技术，可以显著提高医疗设备的数据处理能力和系统响应性能。

---

**相关文档**:
- [多核处理器编程](multicore-programming.md)
- [看门狗与故障恢复](watchdog-recovery.md)
- [实时操作系统](../rtos/index.md)
- [硬件接口](../hardware-interfaces/index.md)

**标签**: #DMA #直接内存访问 #循环缓冲区 #性能优化 #医疗设备 #数据采集
