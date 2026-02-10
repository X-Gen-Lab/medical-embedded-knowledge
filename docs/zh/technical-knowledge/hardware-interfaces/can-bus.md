---
title: CAN总线通信
description: 医疗设备中CAN总线的原理、配置和应用实践
difficulty: 中级
estimated_time: 2-3小时
tags:
  - CAN总线
  - 硬件接口
  - 通信协议
  - STM32
related_modules:
  - zh/technical-knowledge/hardware-interfaces/uart
  - zh/technical-knowledge/rtos/index
  - zh/regulatory-standards/iec-62304/index
last_updated: '2026-02-10'
version: '1.0'
language: zh-CN
---



# CAN总线通信

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

CAN（Controller Area Network）总线是一种多主机串行通信协议，广泛应用于医疗设备的内部通信和设备互联。其高可靠性、实时性和抗干扰能力使其成为医疗设备的理想选择。

### 为什么医疗设备需要CAN总线？

- **高可靠性**: 差分信号传输，强抗干扰能力
- **实时性**: 基于优先级的仲裁机制，确保关键消息优先传输
- **多主机**: 支持多个设备平等通信，无需中央控制器
- **错误检测**: 内置CRC校验、位填充、帧检查等多重错误检测机制
- **故障隔离**: 自动关闭故障节点，不影响总线其他设备

### 典型应用场景

1. **手术机器人**: 多个执行器和传感器之间的实时通信
2. **监护仪**: 多参数模块之间的数据交换
3. **输液泵网络**: 多台输液泵的集中监控和管理
4. **医疗推车**: 车载设备之间的互联互通
5. **呼吸机**: 控制单元与传感器/执行器的通信

## CAN总线基础

### 物理层特性

```c
// CAN总线物理层参数
#define CAN_BUS_SPEED_1M        1000000  // 1 Mbps（短距离）
#define CAN_BUS_SPEED_500K      500000   // 500 Kbps（常用）
#define CAN_BUS_SPEED_250K      250000   // 250 Kbps（中距离）
#define CAN_BUS_SPEED_125K      125000   // 125 Kbps（长距离）

// 总线长度限制
// 1 Mbps: 最大40米
// 500 Kbps: 最大100米
// 250 Kbps: 最大200米
// 125 Kbps: 最大500米

// 终端电阻
#define CAN_TERMINATION_RESISTANCE  120  // Ω
```

### CAN帧格式

CAN 2.0规范定义了两种帧格式：

**标准帧（CAN 2.0A）**:
- 11位标识符（ID）
- 最多8字节数据

**扩展帧（CAN 2.0B）**:
- 29位标识符（ID）
- 最多8字节数据

```c
// CAN消息结构
typedef struct {
    uint32_t id;              // 标识符（11位或29位）
    uint8_t  ide;             // 标识符扩展位（0=标准帧，1=扩展帧）
    uint8_t  rtr;             // 远程传输请求（0=数据帧，1=远程帧）
    uint8_t  dlc;             // 数据长度代码（0-8）
    uint8_t  data[8];         // 数据字节
    uint32_t timestamp;       // 时间戳（可选）
} can_message_t;

// 医疗设备CAN消息ID定义（示例）
#define CAN_ID_HEARTBEAT        0x100  // 心跳消息
#define CAN_ID_ECG_DATA         0x200  // ECG数据
#define CAN_ID_SPO2_DATA        0x201  // SpO2数据
#define CAN_ID_NIBP_DATA        0x202  // 血压数据
#define CAN_ID_TEMP_DATA        0x203  // 体温数据
#define CAN_ID_ALARM_CRITICAL   0x300  // 严重报警
#define CAN_ID_ALARM_WARNING    0x301  // 警告报警
#define CAN_ID_COMMAND          0x400  // 控制命令
#define CAN_ID_STATUS           0x500  // 状态信息
```

## CAN控制器配置

### STM32 CAN配置示例

```c
#include "stm32f4xx_hal.h"

CAN_HandleTypeDef hcan1;

// CAN初始化（500 Kbps @ 42 MHz APB1）
HAL_StatusTypeDef can_init(void) {
    CAN_FilterTypeDef filter_config;
    
    // CAN外设配置
    hcan1.Instance = CAN1;
    hcan1.Init.Prescaler = 6;                    // 时钟分频
    hcan1.Init.Mode = CAN_MODE_NORMAL;           // 正常模式
    hcan1.Init.SyncJumpWidth = CAN_SJW_1TQ;      // 同步跳转宽度
    hcan1.Init.TimeSeg1 = CAN_BS1_11TQ;          // 时间段1
    hcan1.Init.TimeSeg2 = CAN_BS2_2TQ;           // 时间段2
    hcan1.Init.TimeTriggeredMode = DISABLE;      // 时间触发模式
    hcan1.Init.AutoBusOff = ENABLE;              // 自动离线恢复
    hcan1.Init.AutoWakeUp = ENABLE;              // 自动唤醒
    hcan1.Init.AutoRetransmission = ENABLE;      // 自动重传
    hcan1.Init.ReceiveFifoLocked = DISABLE;      // 接收FIFO锁定
    hcan1.Init.TransmitFifoPriority = ENABLE;    // 发送FIFO优先级
    
    if (HAL_CAN_Init(&hcan1) != HAL_OK) {
        return HAL_ERROR;
    }
    
    // 配置接收过滤器（接收所有消息）
    filter_config.FilterBank = 0;
    filter_config.FilterMode = CAN_FILTERMODE_IDMASK;
    filter_config.FilterScale = CAN_FILTERSCALE_32BIT;
    filter_config.FilterIdHigh = 0x0000;
    filter_config.FilterIdLow = 0x0000;
    filter_config.FilterMaskIdHigh = 0x0000;
    filter_config.FilterMaskIdLow = 0x0000;
    filter_config.FilterFIFOAssignment = CAN_RX_FIFO0;
    filter_config.FilterActivation = ENABLE;
    filter_config.SlaveStartFilterBank = 14;
    
    if (HAL_CAN_ConfigFilter(&hcan1, &filter_config) != HAL_OK) {
        return HAL_ERROR;
    }
    
    // 启动CAN
    if (HAL_CAN_Start(&hcan1) != HAL_OK) {
        return HAL_ERROR;
    }
    
    // 激活接收中断
    if (HAL_CAN_ActivateNotification(&hcan1, CAN_IT_RX_FIFO0_MSG_PENDING) != HAL_OK) {
        return HAL_ERROR;
    }
    
    return HAL_OK;
}
```

### 波特率计算

CAN波特率由以下参数决定：

```
波特率 = APB时钟 / (Prescaler × (1 + TimeSeg1 + TimeSeg2))
```

```c
// 波特率计算示例（APB1 = 42 MHz）
typedef struct {
    uint32_t baudrate;
    uint16_t prescaler;
    uint8_t  bs1;
    uint8_t  bs2;
    uint8_t  sjw;
} can_timing_t;

const can_timing_t can_timing_table[] = {
    // 1 Mbps
    {1000000, 3, CAN_BS1_11TQ, CAN_BS2_2TQ, CAN_SJW_1TQ},
    // 500 Kbps
    {500000,  6, CAN_BS1_11TQ, CAN_BS2_2TQ, CAN_SJW_1TQ},
    // 250 Kbps
    {250000, 12, CAN_BS1_11TQ, CAN_BS2_2TQ, CAN_SJW_1TQ},
    // 125 Kbps
    {125000, 24, CAN_BS1_11TQ, CAN_BS2_2TQ, CAN_SJW_1TQ},
};
```

## CAN消息收发

### 发送消息

```c
// 发送CAN消息
HAL_StatusTypeDef can_send_message(uint32_t id, uint8_t *data, uint8_t len) {
    CAN_TxHeaderTypeDef tx_header;
    uint32_t tx_mailbox;
    
    // 配置发送头
    tx_header.StdId = id;                    // 标准ID
    tx_header.ExtId = 0;                     // 扩展ID（未使用）
    tx_header.IDE = CAN_ID_STD;              // 标准帧
    tx_header.RTR = CAN_RTR_DATA;            // 数据帧
    tx_header.DLC = len;                     // 数据长度
    tx_header.TransmitGlobalTime = DISABLE;  // 不使用全局时间
    
    // 发送消息
    if (HAL_CAN_AddTxMessage(&hcan1, &tx_header, data, &tx_mailbox) != HAL_OK) {
        return HAL_ERROR;
    }
    
    return HAL_OK;
}

// 发送心跳消息
void can_send_heartbeat(uint8_t device_id, uint8_t status) {
    uint8_t data[2];
    data[0] = device_id;
    data[1] = status;
    
    can_send_message(CAN_ID_HEARTBEAT, data, 2);
}

// 发送SpO2数据
void can_send_spo2_data(uint8_t spo2, uint8_t pulse_rate, uint8_t quality) {
    uint8_t data[4];
    data[0] = spo2;
    data[1] = pulse_rate;
    data[2] = quality;
    data[3] = 0;  // 保留
    
    can_send_message(CAN_ID_SPO2_DATA, data, 4);
}
```

### 接收消息

```c
// CAN接收中断回调
void HAL_CAN_RxFifo0MsgPendingCallback(CAN_HandleTypeDef *hcan) {
    CAN_RxHeaderTypeDef rx_header;
    uint8_t rx_data[8];
    
    // 从FIFO读取消息
    if (HAL_CAN_GetRxMessage(hcan, CAN_RX_FIFO0, &rx_header, rx_data) == HAL_OK) {
        // 处理接收到的消息
        can_process_message(rx_header.StdId, rx_data, rx_header.DLC);
    }
}

// 消息处理函数
void can_process_message(uint32_t id, uint8_t *data, uint8_t len) {
    switch (id) {
        case CAN_ID_HEARTBEAT:
            // 处理心跳消息
            process_heartbeat(data[0], data[1]);
            break;
            
        case CAN_ID_ECG_DATA:
            // 处理ECG数据
            process_ecg_data(data, len);
            break;
            
        case CAN_ID_ALARM_CRITICAL:
            // 处理严重报警
            process_critical_alarm(data, len);
            break;
            
        case CAN_ID_COMMAND:
            // 处理控制命令
            process_command(data, len);
            break;
            
        default:
            // 未知消息ID
            break;
    }
}
```

## 高级功能

### 消息过滤

```c
// 配置过滤器只接收特定ID范围的消息
HAL_StatusTypeDef can_config_filter(uint32_t id_low, uint32_t id_high) {
    CAN_FilterTypeDef filter_config;
    
    filter_config.FilterBank = 0;
    filter_config.FilterMode = CAN_FILTERMODE_IDMASK;
    filter_config.FilterScale = CAN_FILTERSCALE_32BIT;
    
    // 设置ID范围
    filter_config.FilterIdHigh = (id_low << 5);
    filter_config.FilterIdLow = 0;
    filter_config.FilterMaskIdHigh = ((id_high ^ id_low) << 5);
    filter_config.FilterMaskIdLow = 0;
    
    filter_config.FilterFIFOAssignment = CAN_RX_FIFO0;
    filter_config.FilterActivation = ENABLE;
    
    return HAL_CAN_ConfigFilter(&hcan1, &filter_config);
}

// 只接收报警消息（0x300-0x3FF）
can_config_filter(0x300, 0x3FF);
```

### 错误处理

```c
// CAN错误状态
typedef enum {
    CAN_ERROR_NONE = 0,
    CAN_ERROR_STUFF,      // 位填充错误
    CAN_ERROR_FORM,       // 格式错误
    CAN_ERROR_ACK,        // 应答错误
    CAN_ERROR_BIT_RECESSIVE,  // 隐性位错误
    CAN_ERROR_BIT_DOMINANT,   // 显性位错误
    CAN_ERROR_CRC,        // CRC错误
    CAN_ERROR_BUS_OFF     // 总线关闭
} can_error_t;

// 错误处理回调
void HAL_CAN_ErrorCallback(CAN_HandleTypeDef *hcan) {
    uint32_t error_code = HAL_CAN_GetError(hcan);
    
    if (error_code & HAL_CAN_ERROR_EWG) {
        // 错误警告（TEC或REC > 96）
        log_warning("CAN: Error warning");
    }
    
    if (error_code & HAL_CAN_ERROR_EPV) {
        // 错误被动（TEC或REC > 127）
        log_error("CAN: Error passive");
    }
    
    if (error_code & HAL_CAN_ERROR_BOF) {
        // 总线关闭（TEC > 255）
        log_critical("CAN: Bus off");
        
        // 尝试恢复
        HAL_CAN_ResetError(hcan);
    }
}

// 获取错误计数器
void can_get_error_counters(uint8_t *tec, uint8_t *rec) {
    uint32_t esr = hcan1.Instance->ESR;
    *tec = (esr >> 16) & 0xFF;  // 发送错误计数器
    *rec = (esr >> 24) & 0xFF;  // 接收错误计数器
}
```

### 时间戳和同步

```c
// 启用时间戳
typedef struct {
    uint32_t id;
    uint8_t  data[8];
    uint8_t  dlc;
    uint32_t timestamp_ms;
} can_message_with_timestamp_t;

// 接收带时间戳的消息
void can_receive_with_timestamp(can_message_with_timestamp_t *msg) {
    CAN_RxHeaderTypeDef rx_header;
    
    if (HAL_CAN_GetRxMessage(&hcan1, CAN_RX_FIFO0, &rx_header, msg->data) == HAL_OK) {
        msg->id = rx_header.StdId;
        msg->dlc = rx_header.DLC;
        msg->timestamp_ms = HAL_GetTick();  // 使用系统时钟
    }
}
```

## 医疗设备应用实例

### 多参数监护仪CAN网络

```c
// 监护仪模块定义
#define MODULE_ID_MAIN_UNIT     0x01
#define MODULE_ID_ECG           0x02
#define MODULE_ID_SPO2          0x03
#define MODULE_ID_NIBP          0x04
#define MODULE_ID_TEMP          0x05

// 心跳监控
typedef struct {
    uint8_t  module_id;
    uint32_t last_heartbeat_ms;
    uint8_t  status;
    bool     online;
} module_status_t;

module_status_t modules[5];

// 心跳超时检测
void can_check_module_heartbeat(void) {
    uint32_t current_time = HAL_GetTick();
    
    for (int i = 0; i < 5; i++) {
        if (modules[i].online) {
            if (current_time - modules[i].last_heartbeat_ms > 3000) {
                // 3秒未收到心跳，标记为离线
                modules[i].online = false;
                log_error("Module %d offline", modules[i].module_id);
                
                // 触发报警
                trigger_module_offline_alarm(modules[i].module_id);
            }
        }
    }
}

// 处理心跳消息
void process_heartbeat(uint8_t module_id, uint8_t status) {
    for (int i = 0; i < 5; i++) {
        if (modules[i].module_id == module_id) {
            modules[i].last_heartbeat_ms = HAL_GetTick();
            modules[i].status = status;
            modules[i].online = true;
            break;
        }
    }
}
```

### 输液泵网络管理

```c
// 输液泵CAN协议
#define CAN_ID_PUMP_BASE        0x600
#define CAN_ID_PUMP_STATUS(n)   (CAN_ID_PUMP_BASE + (n))
#define CAN_ID_PUMP_COMMAND(n)  (CAN_ID_PUMP_BASE + 0x100 + (n))

// 输液泵状态
typedef struct {
    uint8_t  pump_id;
    uint16_t flow_rate_ml_h;      // 流速（ml/h）
    uint16_t volume_infused_ml;   // 已输注量（ml）
    uint16_t volume_to_infuse_ml; // 待输注量（ml）
    uint8_t  status;              // 状态
    uint8_t  alarm_code;          // 报警代码
} pump_status_t;

// 发送输液泵状态
void can_send_pump_status(pump_status_t *status) {
    uint8_t data[8];
    
    data[0] = status->pump_id;
    data[1] = status->flow_rate_ml_h >> 8;
    data[2] = status->flow_rate_ml_h & 0xFF;
    data[3] = status->volume_infused_ml >> 8;
    data[4] = status->volume_infused_ml & 0xFF;
    data[5] = status->status;
    data[6] = status->alarm_code;
    data[7] = 0;  // 保留
    
    can_send_message(CAN_ID_PUMP_STATUS(status->pump_id), data, 8);
}

// 发送输液泵控制命令
typedef enum {
    PUMP_CMD_START = 0x01,
    PUMP_CMD_STOP = 0x02,
    PUMP_CMD_PAUSE = 0x03,
    PUMP_CMD_SET_RATE = 0x04,
    PUMP_CMD_SET_VOLUME = 0x05
} pump_command_t;

void can_send_pump_command(uint8_t pump_id, pump_command_t cmd, uint16_t param) {
    uint8_t data[4];
    
    data[0] = cmd;
    data[1] = param >> 8;
    data[2] = param & 0xFF;
    data[3] = 0;  // 校验和
    
    can_send_message(CAN_ID_PUMP_COMMAND(pump_id), data, 4);
}
```

## CANopen协议

CANopen是基于CAN的高层协议，广泛应用于医疗设备。

### 对象字典

```c
// CANopen对象字典条目
typedef struct {
    uint16_t index;
    uint8_t  subindex;
    uint8_t  data_type;
    uint8_t  access;
    void     *data;
    uint32_t size;
} od_entry_t;

// 标准对象
#define OD_DEVICE_TYPE          0x1000
#define OD_ERROR_REGISTER       0x1001
#define OD_HEARTBEAT_TIME       0x1017
#define OD_IDENTITY             0x1018

// 制造商特定对象（医疗设备参数）
#define OD_SPO2_VALUE           0x2000
#define OD_PULSE_RATE           0x2001
#define OD_ALARM_LIMITS         0x2100
```

### NMT（网络管理）

```c
// NMT状态
typedef enum {
    NMT_STATE_INITIALIZING = 0,
    NMT_STATE_PRE_OPERATIONAL = 127,
    NMT_STATE_OPERATIONAL = 5,
    NMT_STATE_STOPPED = 4
} nmt_state_t;

// NMT命令
#define NMT_CMD_START           0x01
#define NMT_CMD_STOP            0x02
#define NMT_CMD_PRE_OPERATIONAL 0x80
#define NMT_CMD_RESET_NODE      0x81
#define NMT_CMD_RESET_COMM      0x82

// 发送NMT命令
void canopen_send_nmt_command(uint8_t node_id, uint8_t command) {
    uint8_t data[2];
    data[0] = command;
    data[1] = node_id;  // 0 = 所有节点
    
    can_send_message(0x000, data, 2);
}
```

## 安全性和可靠性

### 消息完整性检查

```c
// CRC-8校验
uint8_t crc8(uint8_t *data, uint8_t len) {
    uint8_t crc = 0xFF;
    
    for (uint8_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 0x80) {
                crc = (crc << 1) ^ 0x07;
            } else {
                crc <<= 1;
            }
        }
    }
    
    return crc;
}

// 发送带校验的消息
void can_send_message_with_crc(uint32_t id, uint8_t *data, uint8_t len) {
    uint8_t tx_data[8];
    
    // 复制数据
    memcpy(tx_data, data, len);
    
    // 添加CRC
    tx_data[len] = crc8(data, len);
    
    can_send_message(id, tx_data, len + 1);
}
```

### 消息序列号

```c
// 消息序列号管理
typedef struct {
    uint32_t id;
    uint8_t  sequence;
    uint8_t  expected_sequence;
    uint32_t lost_count;
} message_sequence_t;

// 检查序列号
bool can_check_sequence(message_sequence_t *seq, uint8_t received_seq) {
    if (received_seq != seq->expected_sequence) {
        // 检测到丢包
        seq->lost_count++;
        seq->expected_sequence = received_seq + 1;
        return false;
    }
    
    seq->expected_sequence = (received_seq + 1) & 0xFF;
    return true;
}
```

## 调试和诊断

### CAN总线分析

```c
// CAN统计信息
typedef struct {
    uint32_t tx_count;
    uint32_t rx_count;
    uint32_t error_count;
    uint32_t bus_off_count;
    uint32_t last_error_code;
} can_statistics_t;

can_statistics_t can_stats = {0};

// 更新统计信息
void can_update_statistics(void) {
    // 在发送/接收/错误回调中更新
}

// 打印CAN统计
void can_print_statistics(void) {
    printf("CAN Statistics:\n");
    printf("  TX: %lu\n", can_stats.tx_count);
    printf("  RX: %lu\n", can_stats.rx_count);
    printf("  Errors: %lu\n", can_stats.error_count);
    printf("  Bus-off: %lu\n", can_stats.bus_off_count);
}
```

### 日志记录

```c
// CAN消息日志
#define CAN_LOG_SIZE 100

typedef struct {
    uint32_t timestamp_ms;
    uint32_t id;
    uint8_t  data[8];
    uint8_t  dlc;
    bool     is_tx;  // true=发送，false=接收
} can_log_entry_t;

can_log_entry_t can_log[CAN_LOG_SIZE];
uint16_t can_log_index = 0;

// 记录CAN消息
void can_log_message(uint32_t id, uint8_t *data, uint8_t dlc, bool is_tx) {
    can_log_entry_t *entry = &can_log[can_log_index];
    
    entry->timestamp_ms = HAL_GetTick();
    entry->id = id;
    memcpy(entry->data, data, dlc);
    entry->dlc = dlc;
    entry->is_tx = is_tx;
    
    can_log_index = (can_log_index + 1) % CAN_LOG_SIZE;
}
```

## 最佳实践

### 1. 消息优先级设计

- 严重报警: 最高优先级（ID < 0x100）
- 控制命令: 高优先级（0x100-0x1FF）
- 实时数据: 中优先级（0x200-0x2FF）
- 状态信息: 低优先级（0x300-0x3FF）
- 心跳/诊断: 最低优先级（> 0x400）

### 2. 错误恢复策略

```c
// 自动恢复机制
void can_error_recovery(void) {
    uint8_t tec, rec;
    can_get_error_counters(&tec, &rec);
    
    if (tec > 200 || rec > 200) {
        // 错误计数器过高，重新初始化
        HAL_CAN_Stop(&hcan1);
        HAL_Delay(100);
        HAL_CAN_Start(&hcan1);
        
        log_warning("CAN: Reinitialized due to high error count");
    }
}
```

### 3. 实时性保证

- 使用中断而非轮询
- 合理设置消息优先级
- 避免在中断中执行耗时操作
- 使用RTOS任务处理复杂逻辑

### 4. 符合IEC 62304要求

- 记录所有CAN通信错误
- 实现故障检测和隔离
- 定期测试总线恢复机制
- 文档化消息协议和错误处理

## 总结

CAN总线为医疗设备提供了可靠、实时的通信解决方案。正确配置和使用CAN总线，结合适当的错误处理和安全机制，可以构建稳定可靠的医疗设备网络。

## 相关资源

- [UART串口通信](uart.md)
- [RTOS任务调度](../rtos/task-scheduling.md)
- [IEC 62304软件生命周期](../../regulatory-standards/iec-62304/index.md)
