---
title: 蓝牙与BLE技术
difficulty: intermediate
estimated_time: 2-3小时
---

# 蓝牙与BLE技术

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

低功耗蓝牙（Bluetooth Low Energy, BLE）是医疗器械中最常用的无线技术之一。相比经典蓝牙，BLE专为低功耗、间歇性数据传输设计，非常适合可穿戴医疗设备、传感器和监护设备。

## BLE vs 经典蓝牙

| 特性 | BLE | 经典蓝牙 |
|------|-----|---------|
| **功耗** | 极低（微安级） | 高（毫安级） |
| **峰值电流** | <15 mA | >30 mA |
| **数据速率** | 1 Mbps | 1-3 Mbps |
| **延迟** | 6 ms | 100 ms |
| **范围** | 50-100m | 10-100m |
| **应用场景** | 传感器、可穿戴 | 音频、文件传输 |

## BLE协议栈架构

### 物理层（PHY）

```
频段: 2.4 GHz ISM频段
信道: 40个信道（3个广播信道 + 37个数据信道）
调制: GFSK（高斯频移键控）
发射功率: -20 dBm 到 +10 dBm
```

### 链路层（Link Layer）

负责：
- **广播和扫描**: 设备发现机制
- **连接管理**: 建立、维护、终止连接
- **数据包处理**: CRC校验、确认重传
- **跳频**: 自适应跳频避免干扰

### L2CAP层

逻辑链路控制和适配协议：
- 数据分段和重组
- 协议复用
- 流量控制

### ATT/GATT层

**ATT（Attribute Protocol）**: 定义数据交换的基本规则

**GATT（Generic Attribute Profile）**: 定义服务和特征的结构

```
Profile（配置文件）
  └── Service（服务）
        └── Characteristic（特征）
              ├── Value（值）
              └── Descriptor（描述符）
```

### GAP层

通用访问配置文件，定义设备角色：

- **Central（中心设备）**: 通常是智能手机或网关
- **Peripheral（外围设备）**: 通常是医疗传感器
- **Broadcaster（广播者）**: 只发送广播数据
- **Observer（观察者）**: 只接收广播数据

## GATT服务设计

### 标准医疗服务

Bluetooth SIG定义了多个医疗相关服务：

#### 血糖服务（Glucose Service）

```
UUID: 0x1808

特征:
- Glucose Measurement (0x2A18)
  - 血糖值、时间戳、类型
  - 通知（Notify）
  
- Glucose Measurement Context (0x2A34)
  - 测量上下文（餐前/餐后等）
  - 通知（Notify）
  
- Glucose Feature (0x2A51)
  - 设备支持的功能
  - 读取（Read）
  
- Record Access Control Point (0x2A52)
  - 历史记录访问
  - 写入（Write）+ 指示（Indicate）
```

#### 心率服务（Heart Rate Service）

```
UUID: 0x180D

特征:
- Heart Rate Measurement (0x2A37)
  - 心率值（bpm）
  - RR间期（可选）
  - 通知（Notify）
  
- Body Sensor Location (0x2A38)
  - 传感器位置（手腕、胸部等）
  - 读取（Read）
  
- Heart Rate Control Point (0x2A39)
  - 重置能量消耗
  - 写入（Write）
```

#### 血压服务（Blood Pressure Service）

```
UUID: 0x1810

特征:
- Blood Pressure Measurement (0x2A35)
  - 收缩压、舒张压、平均压
  - 指示（Indicate）
  
- Intermediate Cuff Pressure (0x2A36)
  - 测量过程中的袖带压力
  - 通知（Notify）
  
- Blood Pressure Feature (0x2A49)
  - 设备功能
  - 读取（Read）
```

### 自定义服务设计

当标准服务不满足需求时，设计自定义服务：

```c
// 示例：自定义ECG服务
#define CUSTOM_ECG_SERVICE_UUID    0x1234

// ECG波形数据特征
#define ECG_WAVEFORM_CHAR_UUID     0x1235
// 属性: Notify
// 数据格式: 采样率 + 多个采样点

// ECG配置特征
#define ECG_CONFIG_CHAR_UUID       0x1236
// 属性: Read, Write
// 数据格式: 采样率、增益、导联选择

// ECG状态特征
#define ECG_STATUS_CHAR_UUID       0x1237
// 属性: Read, Notify
// 数据格式: 电池电量、导联脱落状态
```

### 特征属性选择

| 属性 | 用途 | 示例 |
|------|------|------|
| **Read** | 读取静态或当前值 | 设备信息、当前配置 |
| **Write** | 写入配置或命令 | 设置参数、控制命令 |
| **Write Without Response** | 快速写入，无确认 | 高频控制命令 |
| **Notify** | 服务器主动推送 | 实时测量数据 |
| **Indicate** | 推送+客户端确认 | 重要事件、警报 |

## 配对与安全

### 安全级别

BLE提供多种安全模式：

#### Security Mode 1（加密）

- **Level 1**: 无安全（不推荐用于医疗）
- **Level 2**: 未认证配对加密
- **Level 3**: 认证配对加密
- **Level 4**: LE Secure Connections（推荐）

#### Security Mode 2（数据签名）

- **Level 1**: 未认证数据签名
- **Level 2**: 认证数据签名

### 配对方法

#### Just Works（简单配对）

```
适用场景: 无显示无输入设备
安全性: 低（易受中间人攻击）
医疗应用: 不推荐
```

#### Passkey Entry（密钥输入）

```
适用场景: 一方有显示，一方有输入
安全性: 中
医疗应用: 可接受
实现: 设备显示6位数字，用户在手机输入
```

#### Numeric Comparison（数字比较）

```
适用场景: 双方都有显示
安全性: 高
医疗应用: 推荐
实现: 双方显示6位数字，用户确认是否一致
```

#### Out of Band（带外配对）

```
适用场景: 使用NFC等其他通道交换密钥
安全性: 最高
医疗应用: 推荐（如果硬件支持）
```

### 医疗器械配对最佳实践

```c
// 推荐的安全配置
typedef struct {
    // 使用LE Secure Connections
    bool le_secure_connections;  // true
    
    // 要求MITM保护
    bool mitm_protection;        // true
    
    // 使用绑定（存储密钥）
    bool bonding;                // true
    
    // I/O能力
    io_capability_t io_cap;      // DISPLAY_YESNO 或 KEYBOARD_DISPLAY
    
    // 最小加密密钥长度
    uint8_t min_key_size;        // 16 bytes
    
} ble_security_config_t;
```

### 密钥管理

```c
// 安全存储配对密钥
void store_bonding_info(uint8_t *peer_addr, 
                        uint8_t *ltk,      // Long Term Key
                        uint8_t *irk,      // Identity Resolving Key
                        uint8_t *csrk) {   // Connection Signature Resolving Key
    
    // 使用安全存储（如ARM TrustZone、安全元件）
    secure_storage_write(BONDING_KEY, peer_addr, ltk, 16);
    secure_storage_write(IRK_KEY, peer_addr, irk, 16);
    secure_storage_write(CSRK_KEY, peer_addr, csrk, 16);
}

// 定期更新密钥
void refresh_keys_if_needed() {
    if (connection_count > KEY_REFRESH_THRESHOLD) {
        initiate_key_refresh();
    }
}
```

## 功耗优化

### 连接参数优化

```c
// 连接参数影响功耗和响应速度
typedef struct {
    uint16_t conn_interval_min;  // 连接间隔最小值
    uint16_t conn_interval_max;  // 连接间隔最大值
    uint16_t slave_latency;      // 从设备延迟
    uint16_t supervision_timeout; // 监督超时
} ble_conn_params_t;

// 低功耗配置（适合周期性数据上传）
ble_conn_params_t low_power_params = {
    .conn_interval_min = 400,    // 500ms
    .conn_interval_max = 800,    // 1000ms
    .slave_latency = 4,          // 可跳过4个连接事件
    .supervision_timeout = 4000  // 40s
};

// 低延迟配置（适合实时控制）
ble_conn_params_t low_latency_params = {
    .conn_interval_min = 8,      // 10ms
    .conn_interval_max = 16,     // 20ms
    .slave_latency = 0,
    .supervision_timeout = 400   // 4s
};
```

### 广播优化

```c
// 广播参数
typedef struct {
    uint16_t adv_interval;       // 广播间隔
    uint8_t adv_type;            // 广播类型
    int8_t tx_power;             // 发射功率
} ble_adv_params_t;

// 快速连接模式（设备开机后）
ble_adv_params_t fast_adv = {
    .adv_interval = 100,         // 100ms
    .adv_type = ADV_IND,         // 可连接
    .tx_power = 0                // 0 dBm
};

// 省电模式（已连接或长时间未连接）
ble_adv_params_t slow_adv = {
    .adv_interval = 1000,        // 1s
    .adv_type = ADV_IND,
    .tx_power = -12              // -12 dBm
};
```

### 数据传输优化

```c
// 使用通知而非指示（无需确认）
void send_sensor_data_optimized(uint8_t *data, uint16_t len) {
    // Notify: 无需等待确认，更快更省电
    ble_gatts_hvx(conn_handle, SENSOR_CHAR_HANDLE, 
                  BLE_GATT_HVX_NOTIFICATION, data, len);
}

// 批量传输减少唤醒次数
#define BATCH_SIZE 10
void batch_sensor_readings() {
    static sensor_reading_t buffer[BATCH_SIZE];
    static uint8_t count = 0;
    
    buffer[count++] = read_sensor();
    
    if (count >= BATCH_SIZE) {
        send_batch(buffer, count);
        count = 0;
    }
}

// 自适应MTU
void negotiate_mtu() {
    // 请求更大的MTU以减少分包
    ble_gattc_exchange_mtu_request(conn_handle, 247); // 最大MTU
}
```

### 睡眠模式管理

```c
// 状态机管理功耗模式
typedef enum {
    POWER_MODE_ACTIVE,      // 活跃传输
    POWER_MODE_IDLE,        // 空闲但已连接
    POWER_MODE_SLEEP,       // 深度睡眠
    POWER_MODE_SHUTDOWN     // 关机
} power_mode_t;

void enter_sleep_mode() {
    // 1. 停止非必要外设
    disable_leds();
    disable_sensors();
    
    // 2. 配置唤醒源
    configure_wakeup_source(BUTTON_PIN);
    configure_wakeup_source(RTC_ALARM);
    
    // 3. 进入系统睡眠
    system_sleep();
}

// 功耗测量示例
// 活跃传输: 10-15 mA
// 连接空闲: 50-200 μA
// 广播: 100-500 μA (取决于间隔)
// 深度睡眠: 1-5 μA
```

## 医疗器械蓝牙配置文件

### Continua Health Alliance认证

Continua（现为Personal Connected Health Alliance）定义了医疗设备互操作性标准：

#### Continua设计指南

```
要求:
1. 使用标准GATT服务（如血糖、血压、体温等）
2. 实现IEEE 11073-20601协议
3. 支持特定的安全要求
4. 通过互操作性测试

好处:
- 与认证的健康平台兼容
- 简化监管审批
- 提高市场接受度
```

### IEEE 11073个人健康设备（PHD）

```c
// IEEE 11073-20601 over BLE
// 使用标准对象模型表示医疗数据

typedef struct {
    uint16_t partition;      // 分区（如MDC_PART_SCADA）
    uint16_t code;           // 术语代码（如MDC_TEMP_BODY）
    float value;             // 测量值
    uint16_t unit;           // 单位（如MDC_DIM_DEGC）
    absolute_time_t timestamp; // 时间戳
} ieee_11073_measurement_t;

// 示例：体温测量
ieee_11073_measurement_t temp_measurement = {
    .partition = 0x0002,     // MDC_PART_SCADA
    .code = 0x4188,          // MDC_TEMP_BODY
    .value = 37.5,
    .unit = 0x17A0,          // MDC_DIM_DEGC (摄氏度)
    .timestamp = get_current_time()
};
```

## 实际实现示例

### Nordic nRF52系列实现

```c
#include "ble.h"
#include "ble_srv_common.h"

// 定义心率服务
typedef struct {
    uint16_t service_handle;
    ble_gatts_char_handles_t hrm_handles;
    uint8_t uuid_type;
} ble_hrs_t;

// 初始化心率服务
uint32_t ble_hrs_init(ble_hrs_t *p_hrs) {
    uint32_t err_code;
    ble_uuid_t ble_uuid;
    ble_add_char_params_t add_char_params;
    
    // 添加服务
    BLE_UUID_BLE_ASSIGN(ble_uuid, BLE_UUID_HEART_RATE_SERVICE);
    err_code = sd_ble_gatts_service_add(BLE_GATTS_SRVC_TYPE_PRIMARY,
                                         &ble_uuid,
                                         &p_hrs->service_handle);
    VERIFY_SUCCESS(err_code);
    
    // 添加心率测量特征
    memset(&add_char_params, 0, sizeof(add_char_params));
    add_char_params.uuid = BLE_UUID_HEART_RATE_MEASUREMENT_CHAR;
    add_char_params.max_len = 10;
    add_char_params.char_props.notify = 1;
    add_char_params.cccd_write_access = SEC_OPEN;
    
    err_code = characteristic_add(p_hrs->service_handle,
                                   &add_char_params,
                                   &p_hrs->hrm_handles);
    return err_code;
}

// 发送心率数据
uint32_t ble_hrs_heart_rate_measurement_send(ble_hrs_t *p_hrs, 
                                              uint16_t heart_rate) {
    uint8_t encoded_hrm[10];
    uint16_t len = 0;
    
    // 编码心率数据
    encoded_hrm[len++] = 0x00; // Flags: 心率值格式为UINT8
    encoded_hrm[len++] = (uint8_t)heart_rate;
    
    // 发送通知
    ble_gatts_hvx_params_t hvx_params;
    memset(&hvx_params, 0, sizeof(hvx_params));
    hvx_params.handle = p_hrs->hrm_handles.value_handle;
    hvx_params.type = BLE_GATT_HVX_NOTIFICATION;
    hvx_params.p_len = &len;
    hvx_params.p_data = encoded_hrm;
    
    return sd_ble_gatts_hvx(p_hrs->conn_handle, &hvx_params);
}
```

### ESP32实现

```c
#include "esp_bt.h"
#include "esp_gap_ble_api.h"
#include "esp_gatts_api.h"

// GATT服务定义
static const uint16_t GATTS_SERVICE_UUID = 0x180D; // 心率服务
static const uint16_t GATTS_CHAR_UUID = 0x2A37;    // 心率测量

// 特征值
static uint8_t char_value[4] = {0x00, 0x00, 0x00, 0x00};

// GATT事件处理
static void gatts_event_handler(esp_gatts_cb_event_t event,
                                esp_gatt_if_t gatts_if,
                                esp_ble_gatts_cb_param_t *param) {
    switch (event) {
        case ESP_GATTS_REG_EVT:
            // 创建服务
            esp_ble_gatts_create_service(gatts_if, 
                                         &service_id, 
                                         GATTS_NUM_HANDLE);
            break;
            
        case ESP_GATTS_CREATE_EVT:
            // 启动服务
            esp_ble_gatts_start_service(param->create.service_handle);
            
            // 添加特征
            esp_ble_gatts_add_char(param->create.service_handle,
                                   &char_uuid,
                                   ESP_GATT_PERM_READ,
                                   ESP_GATT_CHAR_PROP_BIT_READ | 
                                   ESP_GATT_CHAR_PROP_BIT_NOTIFY,
                                   &char_val,
                                   NULL);
            break;
            
        case ESP_GATTS_WRITE_EVT:
            // 处理写入事件（如CCCD配置）
            if (param->write.handle == cccd_handle) {
                uint16_t descr_value = param->write.value[1]<<8 | 
                                       param->write.value[0];
                if (descr_value == 0x0001) {
                    // 客户端启用通知
                    notifications_enabled = true;
                }
            }
            break;
    }
}

// 发送心率通知
void send_heart_rate_notification(uint8_t heart_rate) {
    if (notifications_enabled) {
        uint8_t notify_data[2];
        notify_data[0] = 0x00; // Flags
        notify_data[1] = heart_rate;
        
        esp_ble_gatts_send_indicate(gatts_if, 
                                     conn_id,
                                     char_handle,
                                     sizeof(notify_data),
                                     notify_data,
                                     false); // false = notify, true = indicate
    }
}
```

## 测试与验证

### 功能测试

```python
# 使用Python bleak库进行BLE测试
import asyncio
from bleak import BleakClient, BleakScanner

async def test_heart_rate_service():
    # 1. 扫描设备
    devices = await BleakScanner.discover()
    target_device = None
    for d in devices:
        if "HeartRate" in d.name:
            target_device = d
            break
    
    # 2. 连接设备
    async with BleakClient(target_device.address) as client:
        print(f"Connected: {client.is_connected}")
        
        # 3. 读取设备信息
        model = await client.read_gatt_char("00002a24-0000-1000-8000-00805f9b34fb")
        print(f"Model: {model.decode()}")
        
        # 4. 启用心率通知
        def notification_handler(sender, data):
            flags = data[0]
            hr_value = data[1]
            print(f"Heart Rate: {hr_value} bpm")
        
        await client.start_notify("00002a37-0000-1000-8000-00805f9b34fb",
                                   notification_handler)
        
        # 5. 接收数据
        await asyncio.sleep(30)
        
        # 6. 停止通知
        await client.stop_notify("00002a37-0000-1000-8000-00805f9b34fb")

asyncio.run(test_heart_rate_service())
```

### 性能测试

```c
// 吞吐量测试
void throughput_test() {
    uint32_t start_time = get_timestamp_ms();
    uint32_t bytes_sent = 0;
    uint8_t test_data[244]; // 最大有效载荷
    
    // 持续发送1秒
    while (get_timestamp_ms() - start_time < 1000) {
        if (ble_send_notification(test_data, sizeof(test_data)) == SUCCESS) {
            bytes_sent += sizeof(test_data);
        }
    }
    
    float throughput_kbps = (bytes_sent * 8) / 1000.0;
    printf("Throughput: %.2f kbps\n", throughput_kbps);
    // 预期: 100-700 kbps (取决于连接参数和MTU)
}

// 延迟测试
void latency_test() {
    uint32_t send_time = get_timestamp_us();
    
    // 发送带时间戳的数据
    send_timestamped_data(send_time);
    
    // 在接收端计算延迟
    // 典型延迟: 10-100ms (取决于连接间隔)
}
```

### 互操作性测试

测试与不同平台的兼容性：

- **iOS**: 使用Core Bluetooth框架
- **Android**: 使用Android BLE API
- **Windows**: 使用Windows.Devices.Bluetooth
- **Linux**: 使用BlueZ协议栈

## 常见问题与解决方案

### 连接不稳定

```c
// 问题：频繁断连
// 解决方案：

// 1. 增加监督超时
conn_params.supervision_timeout = 4000; // 40秒

// 2. 实现自动重连
void on_disconnect(uint8_t reason) {
    if (reason != USER_INITIATED) {
        start_advertising(); // 自动开始广播
    }
}

// 3. 监控连接质量
void monitor_connection_quality() {
    int8_t rssi = get_rssi();
    if (rssi < -85) {
        log_warning("Weak signal: %d dBm", rssi);
    }
}
```

### 数据丢失

```c
// 问题：通知数据丢失
// 解决方案：

// 1. 使用指示而非通知（关键数据）
ble_gatts_hvx(conn_handle, char_handle, 
              BLE_GATT_HVX_INDICATION, data, len);

// 2. 实现应用层确认
typedef struct {
    uint16_t sequence_number;
    uint8_t data[20];
} reliable_packet_t;

// 3. 流量控制
#define MAX_PENDING_NOTIFICATIONS 5
if (pending_notifications < MAX_PENDING_NOTIFICATIONS) {
    send_notification();
    pending_notifications++;
}
```

### 功耗过高

```c
// 问题：电池续航不足
// 解决方案：

// 1. 优化连接间隔
request_connection_parameter_update(500, 1000, 4, 4000);

// 2. 减少广播频率
set_advertising_interval(1000); // 1秒

// 3. 使用事件驱动而非轮询
// 差的做法：
while(1) {
    if (sensor_data_ready()) {
        send_data();
    }
    delay_ms(10);
}

// 好的做法：
void sensor_interrupt_handler() {
    send_data();
    enter_sleep_mode();
}
```

## 最佳实践总结

### 设计阶段

1. ✅ 优先使用标准GATT服务
2. ✅ 遵循Bluetooth SIG设计指南
3. ✅ 考虑Continua认证要求
4. ✅ 规划功耗预算

### 实现阶段

1. ✅ 使用LE Secure Connections
2. ✅ 实现适当的配对方法
3. ✅ 优化连接参数
4. ✅ 实现错误处理和重连机制

### 测试阶段

1. ✅ 多平台互操作性测试
2. ✅ 长时间稳定性测试
3. ✅ 功耗测量
4. ✅ 无线共存测试

## 参考资源

- [Bluetooth Core Specification](https://www.bluetooth.com/specifications/specs/)
- [GATT Specification Supplement](https://www.bluetooth.com/specifications/gss/)
- [Medical Device Working Group](https://www.bluetooth.com/special-interest-groups/medical-devices/)
- [Nordic Semiconductor BLE教程](https://infocenter.nordicsemi.com/)
- [ESP32 BLE文档](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/bluetooth/index.html)

---

**下一步**: 了解 [WiFi通信技术](wifi.md)
