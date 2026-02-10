---
title: USB接口
description: 医疗设备中USB Host/Device/OTG的原理、配置和应用
difficulty: intermediate
estimated_time: 2-3小时
tags: 
---



# USB接口

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

USB（Universal Serial Bus）是医疗设备中最常用的接口之一，用于数据传输、设备充电、固件升级和外设连接。医疗设备需要支持USB Device（从设备）、USB Host（主设备）和USB OTG（双角色）模式。

### 医疗设备中的USB应用

- **数据导出**: 将患者数据导出到U盘或PC
- **固件升级**: 通过USB更新设备软件
- **设备充电**: USB供电和电池充电
- **外设连接**: 连接打印机、键盘、鼠标等
- **PC通信**: 与医院信息系统（HIS）通信
- **调试接口**: 开发和维护时的调试端口

### USB版本对比

| 版本 | 速度 | 功率 | 医疗设备应用 |
|------|------|------|--------------|
| USB 1.1 | 12 Mbps | 2.5W | 简单数据传输 |
| USB 2.0 | 480 Mbps | 2.5W | 常用于医疗设备 |
| USB 3.0 | 5 Gbps | 4.5W | 高速数据传输 |
| USB 3.1 | 10 Gbps | 100W | 影像设备 |
| USB-C | 最高40 Gbps | 最高100W | 新一代设备 |

## USB基础概念

### USB拓扑结构

```
Host（主机）
  └── Hub（集线器）
       ├── Device 1（设备1）
       ├── Device 2（设备2）
       └── Device 3（设备3）
```

### USB传输类型

1. **控制传输（Control）**: 设备配置和命令
2. **批量传输（Bulk）**: 大量数据传输，无时间保证
3. **中断传输（Interrupt）**: 小量数据，低延迟
4. **同步传输（Isochronous）**: 实时数据流，如音视频

### USB设备类

```c
// 常用USB设备类
#define USB_CLASS_CDC           0x02  // 通信设备类（虚拟串口）
#define USB_CLASS_HID           0x03  // 人机接口设备
#define USB_CLASS_MSC           0x08  // 大容量存储设备
#define USB_CLASS_VENDOR        0xFF  // 厂商自定义类

// 医疗设备常用类
#define USB_CLASS_PHDC          0x0F  // 个人医疗设备类
```

## USB Device模式

### CDC虚拟串口（最常用）

```c
#include "usbd_cdc_if.h"

// USB CDC初始化
void usb_cdc_init(void) {
    // USB设备初始化由HAL库自动完成
    // 在usbd_cdc_if.c中实现回调函数
}

// 发送数据到PC
HAL_StatusTypeDef usb_cdc_transmit(uint8_t *data, uint16_t len) {
    return CDC_Transmit_FS(data, len);
}

// 接收数据回调（在usbd_cdc_if.c中实现）
static int8_t CDC_Receive_FS(uint8_t* Buf, uint32_t *Len) {
    // 处理接收到的数据
    process_usb_data(Buf, *Len);
    
    // 准备接收下一包数据
    USBD_CDC_SetRxBuffer(&hUsbDeviceFS, &Buf[0]);
    USBD_CDC_ReceivePacket(&hUsbDeviceFS);
    
    return USBD_OK;
}

// 医疗数据传输示例
void send_patient_data_via_usb(patient_data_t *data) {
    char buffer[256];
    int len;
    
    // 格式化数据为JSON
    len = snprintf(buffer, sizeof(buffer),
                   "{\"spo2\":%d,\"hr\":%d,\"temp\":%.1f}\n",
                   data->spo2, data->heart_rate, data->temperature);
    
    // 通过USB CDC发送
    usb_cdc_transmit((uint8_t*)buffer, len);
}
```

### USB MSC（大容量存储）

```c
// 实现U盘功能，用于数据导出
#include "usbd_msc.h"

// 存储介质操作函数
int8_t STORAGE_Init(uint8_t lun);
int8_t STORAGE_GetCapacity(uint8_t lun, uint32_t *block_num, uint16_t *block_size);
int8_t STORAGE_IsReady(uint8_t lun);
int8_t STORAGE_IsWriteProtected(uint8_t lun);
int8_t STORAGE_Read(uint8_t lun, uint8_t *buf, uint32_t blk_addr, uint16_t blk_len);
int8_t STORAGE_Write(uint8_t lun, uint8_t *buf, uint32_t blk_addr, uint16_t blk_len);

// 使用SD卡作为存储介质
int8_t STORAGE_Read(uint8_t lun, uint8_t *buf, uint32_t blk_addr, uint16_t blk_len) {
    if (BSP_SD_ReadBlocks((uint32_t*)buf, blk_addr, blk_len, SD_TIMEOUT) == MSD_OK) {
        return USBD_OK;
    }
    return USBD_FAIL;
}

int8_t STORAGE_Write(uint8_t lun, uint8_t *buf, uint32_t blk_addr, uint16_t blk_len) {
    if (BSP_SD_WriteBlocks((uint32_t*)buf, blk_addr, blk_len, SD_TIMEOUT) == MSD_OK) {
        return USBD_OK;
    }
    return USBD_FAIL;
}
```

### 自定义USB设备类

```c
// 医疗设备专用USB协议
#define USB_VENDOR_ID           0x1234
#define USB_PRODUCT_ID          0x5678
#define USB_DEVICE_VERSION      0x0100

// 自定义端点
#define CUSTOM_EP_IN            0x81
#define CUSTOM_EP_OUT           0x01
#define CUSTOM_EP_SIZE          64

// 自定义命令
#define CMD_GET_DEVICE_INFO     0x01
#define CMD_GET_PATIENT_DATA    0x02
#define CMD_SET_PARAMETERS      0x03
#define CMD_START_MEASUREMENT   0x04
#define CMD_STOP_MEASUREMENT    0x05

// 命令处理
void usb_process_command(uint8_t cmd, uint8_t *data, uint16_t len) {
    switch (cmd) {
        case CMD_GET_DEVICE_INFO:
            usb_send_device_info();
            break;
            
        case CMD_GET_PATIENT_DATA:
            usb_send_patient_data();
            break;
            
        case CMD_SET_PARAMETERS:
            usb_set_parameters(data, len);
            break;
            
        case CMD_START_MEASUREMENT:
            start_measurement();
            usb_send_ack();
            break;
            
        case CMD_STOP_MEASUREMENT:
            stop_measurement();
            usb_send_ack();
            break;
            
        default:
            usb_send_error(USB_ERROR_UNKNOWN_CMD);
            break;
    }
}
```

## USB Host模式

### 连接U盘读写文件

```c
#include "usbh_core.h"
#include "usbh_msc.h"
#include "ff.h"  // FatFs文件系统

USBH_HandleTypeDef hUSB_Host;
FATFS USBDISKFatFs;
FIL MyFile;

// USB Host初始化
void usb_host_init(void) {
    USBH_Init(&hUSB_Host, USBH_UserProcess, 0);
    USBH_RegisterClass(&hUSB_Host, USBH_MSC_CLASS);
    USBH_Start(&hUSB_Host);
}

// USB Host用户回调
void USBH_UserProcess(USBH_HandleTypeDef *phost, uint8_t id) {
    switch(id) {
        case HOST_USER_SELECT_CONFIGURATION:
            break;
            
        case HOST_USER_CLASS_ACTIVE:
            // U盘已连接并就绪
            if (f_mount(&USBDISKFatFs, "0:/", 0) == FR_OK) {
                log_info("USB disk mounted");
                usb_disk_ready = true;
            }
            break;
            
        case HOST_USER_CONNECTION:
            log_info("USB device connected");
            break;
            
        case HOST_USER_DISCONNECTION:
            log_info("USB device disconnected");
            f_mount(NULL, "0:/", 0);
            usb_disk_ready = false;
            break;
            
        default:
            break;
    }
}

// 导出患者数据到U盘
bool export_patient_data_to_usb(patient_data_t *data) {
    FRESULT res;
    UINT bytes_written;
    char filename[32];
    char buffer[512];
    
    if (!usb_disk_ready) {
        return false;
    }
    
    // 生成文件名（包含时间戳）
    snprintf(filename, sizeof(filename), "0:/patient_%lu.csv", HAL_GetTick());
    
    // 创建文件
    res = f_open(&MyFile, filename, FA_CREATE_ALWAYS | FA_WRITE);
    if (res != FR_OK) {
        log_error("Failed to create file: %d", res);
        return false;
    }
    
    // 写入CSV头
    f_write(&MyFile, "Time,SpO2,HR,Temp\n", 18, &bytes_written);
    
    // 写入数据
    for (int i = 0; i < data->sample_count; i++) {
        int len = snprintf(buffer, sizeof(buffer), "%lu,%d,%d,%.1f\n",
                          data->samples[i].timestamp,
                          data->samples[i].spo2,
                          data->samples[i].heart_rate,
                          data->samples[i].temperature);
        
        f_write(&MyFile, buffer, len, &bytes_written);
    }
    
    // 关闭文件
    f_close(&MyFile);
    
    log_info("Data exported to %s", filename);
    return true;
}
```

### 连接打印机

```c
// USB打印机类
#include "usbh_printer.h"

// 打印报告
bool print_patient_report(patient_data_t *data) {
    uint8_t print_buffer[1024];
    uint16_t len;
    
    // 格式化打印内容（ESC/POS命令）
    len = format_print_data(print_buffer, sizeof(print_buffer), data);
    
    // 发送到打印机
    if (USBH_Printer_Write(&hUSB_Host, print_buffer, len) == USBH_OK) {
        return true;
    }
    
    return false;
}

// 格式化打印数据
uint16_t format_print_data(uint8_t *buffer, uint16_t size, patient_data_t *data) {
    uint16_t pos = 0;
    
    // ESC/POS初始化
    buffer[pos++] = 0x1B;  // ESC
    buffer[pos++] = 0x40;  // @（初始化）
    
    // 标题（加粗）
    buffer[pos++] = 0x1B;  // ESC
    buffer[pos++] = 0x45;  // E
    buffer[pos++] = 0x01;  // 加粗开
    pos += snprintf((char*)&buffer[pos], size - pos, "Patient Report\n");
    buffer[pos++] = 0x1B;  // ESC
    buffer[pos++] = 0x45;  // E
    buffer[pos++] = 0x00;  // 加粗关
    
    // 患者信息
    pos += snprintf((char*)&buffer[pos], size - pos,
                   "Patient ID: %s\n", data->patient_id);
    pos += snprintf((char*)&buffer[pos], size - pos,
                   "Date: %s\n\n", data->date);
    
    // 测量数据
    pos += snprintf((char*)&buffer[pos], size - pos,
                   "SpO2: %d%%\n", data->spo2);
    pos += snprintf((char*)&buffer[pos], size - pos,
                   "Heart Rate: %d bpm\n", data->heart_rate);
    pos += snprintf((char*)&buffer[pos], size - pos,
                   "Temperature: %.1f C\n\n", data->temperature);
    
    // 切纸
    buffer[pos++] = 0x1D;  // GS
    buffer[pos++] = 0x56;  // V
    buffer[pos++] = 0x00;  // 全切
    
    return pos;
}
```

## USB OTG模式

### 动态角色切换

```c
#include "usb_otg.h"

typedef enum {
    USB_MODE_NONE,
    USB_MODE_DEVICE,
    USB_MODE_HOST
} usb_mode_t;

usb_mode_t current_usb_mode = USB_MODE_NONE;

// 检测USB ID引脚状态
void usb_otg_detect_mode(void) {
    if (HAL_GPIO_ReadPin(USB_ID_GPIO_Port, USB_ID_Pin) == GPIO_PIN_RESET) {
        // ID引脚接地，切换到Host模式
        if (current_usb_mode != USB_MODE_HOST) {
            usb_switch_to_host_mode();
        }
    } else {
        // ID引脚悬空，切换到Device模式
        if (current_usb_mode != USB_MODE_DEVICE) {
            usb_switch_to_device_mode();
        }
    }
}

// 切换到Host模式
void usb_switch_to_host_mode(void) {
    if (current_usb_mode == USB_MODE_DEVICE) {
        // 停止Device模式
        USBD_Stop(&hUsbDeviceFS);
        USBD_DeInit(&hUsbDeviceFS);
    }
    
    // 启动Host模式
    USBH_Init(&hUSB_Host, USBH_UserProcess, 0);
    USBH_RegisterClass(&hUSB_Host, USBH_MSC_CLASS);
    USBH_Start(&hUSB_Host);
    
    current_usb_mode = USB_MODE_HOST;
    log_info("Switched to USB Host mode");
}

// 切换到Device模式
void usb_switch_to_device_mode(void) {
    if (current_usb_mode == USB_MODE_HOST) {
        // 停止Host模式
        USBH_Stop(&hUSB_Host);
        USBH_DeInit(&hUSB_Host);
    }
    
    // 启动Device模式
    USBD_Init(&hUsbDeviceFS, &FS_Desc, DEVICE_FS);
    USBD_RegisterClass(&hUsbDeviceFS, &USBD_CDC);
    USBD_CDC_RegisterInterface(&hUsbDeviceFS, &USBD_Interface_fops_FS);
    USBD_Start(&hUsbDeviceFS);
    
    current_usb_mode = USB_MODE_DEVICE;
    log_info("Switched to USB Device mode");
}
```

## 固件升级（DFU）

### USB DFU（Device Firmware Upgrade）

```c
#include "usbd_dfu.h"

// DFU状态
typedef enum {
    DFU_STATE_IDLE,
    DFU_STATE_DOWNLOAD_SYNC,
    DFU_STATE_DOWNLOAD_BUSY,
    DFU_STATE_DOWNLOAD_IDLE,
    DFU_STATE_MANIFEST_SYNC,
    DFU_STATE_MANIFEST,
    DFU_STATE_MANIFEST_WAIT_RESET,
    DFU_STATE_UPLOAD_IDLE,
    DFU_STATE_ERROR
} dfu_state_t;

// Flash操作
uint16_t DFU_If_Erase(uint32_t addr) {
    HAL_FLASH_Unlock();
    
    FLASH_EraseInitTypeDef erase_init;
    uint32_t sector_error;
    
    erase_init.TypeErase = FLASH_TYPEERASE_SECTORS;
    erase_init.Sector = get_flash_sector(addr);
    erase_init.NbSectors = 1;
    erase_init.VoltageRange = FLASH_VOLTAGE_RANGE_3;
    
    if (HAL_FLASHEx_Erase(&erase_init, &sector_error) != HAL_OK) {
        HAL_FLASH_Lock();
        return DFU_ERROR_ERASE;
    }
    
    HAL_FLASH_Lock();
    return DFU_ERROR_NONE;
}

uint16_t DFU_If_Write(uint8_t *src, uint8_t *dest, uint32_t len) {
    HAL_FLASH_Unlock();
    
    for (uint32_t i = 0; i < len; i += 4) {
        uint32_t data = *(uint32_t*)(src + i);
        
        if (HAL_FLASH_Program(FLASH_TYPEPROGRAM_WORD,
                             (uint32_t)(dest + i),
                             data) != HAL_OK) {
            HAL_FLASH_Lock();
            return DFU_ERROR_WRITE;
        }
    }
    
    HAL_FLASH_Lock();
    return DFU_ERROR_NONE;
}

// 进入DFU模式
void enter_dfu_mode(void) {
    // 设置标志位
    *((uint32_t*)0x2001FFF0) = 0xDEADBEEF;
    
    // 复位进入DFU
    NVIC_SystemReset();
}

// 在启动代码中检查DFU标志
void check_dfu_flag(void) {
    if (*((uint32_t*)0x2001FFF0) == 0xDEADBEEF) {
        // 清除标志
        *((uint32_t*)0x2001FFF0) = 0;
        
        // 启动DFU
        start_dfu_mode();
    }
}
```

## USB电源管理

### USB充电检测

```c
// USB充电类型
typedef enum {
    USB_CHARGE_NONE,
    USB_CHARGE_SDP,      // 标准下行端口（500mA）
    USB_CHARGE_CDP,      // 充电下行端口（1.5A）
    USB_CHARGE_DCP,      // 专用充电端口（最高2A）
    USB_CHARGE_UNKNOWN
} usb_charge_type_t;

// 检测USB充电类型
usb_charge_type_t detect_usb_charge_type(void) {
    // 读取D+/D-电压
    uint16_t dp_voltage = adc_read_dp();
    uint16_t dm_voltage = adc_read_dm();
    
    if (dp_voltage > 2000 && dm_voltage > 2000) {
        // D+和D-都高，DCP
        return USB_CHARGE_DCP;
    } else if (dp_voltage > 2000 || dm_voltage > 2000) {
        // 其中一个高，CDP
        return USB_CHARGE_CDP;
    } else {
        // 都低，SDP
        return USB_CHARGE_SDP;
    }
}

// 设置充电电流
void set_charge_current(usb_charge_type_t type) {
    uint16_t current_ma;
    
    switch (type) {
        case USB_CHARGE_SDP:
            current_ma = 500;
            break;
        case USB_CHARGE_CDP:
            current_ma = 1500;
            break;
        case USB_CHARGE_DCP:
            current_ma = 2000;
            break;
        default:
            current_ma = 100;  // 安全电流
            break;
    }
    
    // 配置充电IC
    charger_set_current(current_ma);
    log_info("Charge current set to %d mA", current_ma);
}
```

### USB挂起和唤醒

```c
// USB挂起回调
void HAL_PCD_SuspendCallback(PCD_HandleTypeDef *hpcd) {
    // USB总线挂起，进入低功耗模式
    log_info("USB suspended");
    
    // 降低系统时钟
    SystemClock_Config_LowPower();
    
    // 进入停止模式
    HAL_PWR_EnterSTOPMode(PWR_LOWPOWERREGULATOR_ON, PWR_STOPENTRY_WFI);
}

// USB唤醒回调
void HAL_PCD_ResumeCallback(PCD_HandleTypeDef *hpcd) {
    // USB总线唤醒，恢复正常模式
    log_info("USB resumed");
    
    // 恢复系统时钟
    SystemClock_Config();
}
```

## 安全性考虑

### USB数据加密

```c
#include "mbedtls/aes.h"

// AES加密USB数据
bool usb_send_encrypted_data(uint8_t *data, uint16_t len) {
    uint8_t encrypted[256];
    uint8_t iv[16] = {0};  // 初始化向量
    mbedtls_aes_context aes;
    
    // 初始化AES
    mbedtls_aes_init(&aes);
    mbedtls_aes_setkey_enc(&aes, encryption_key, 256);
    
    // 加密数据
    mbedtls_aes_crypt_cbc(&aes, MBEDTLS_AES_ENCRYPT, len,
                          iv, data, encrypted);
    
    // 发送加密数据
    usb_cdc_transmit(encrypted, len);
    
    mbedtls_aes_free(&aes);
    return true;
}
```

### USB访问控制

```c
// USB连接认证
typedef enum {
    USB_AUTH_NONE,
    USB_AUTH_PENDING,
    USB_AUTH_SUCCESS,
    USB_AUTH_FAILED
} usb_auth_state_t;

usb_auth_state_t usb_auth_state = USB_AUTH_NONE;

// 认证挑战-响应
bool usb_authenticate(void) {
    uint8_t challenge[16];
    uint8_t response[16];
    uint8_t expected_response[16];
    
    // 生成随机挑战
    generate_random(challenge, sizeof(challenge));
    
    // 发送挑战
    usb_cdc_transmit(challenge, sizeof(challenge));
    
    // 等待响应
    if (usb_receive_with_timeout(response, sizeof(response), 5000)) {
        // 计算期望的响应
        calculate_hmac(challenge, sizeof(challenge),
                      device_key, sizeof(device_key),
                      expected_response);
        
        // 验证响应
        if (memcmp(response, expected_response, sizeof(response)) == 0) {
            usb_auth_state = USB_AUTH_SUCCESS;
            return true;
        }
    }
    
    usb_auth_state = USB_AUTH_FAILED;
    return false;
}
```

## 调试和诊断

### USB抓包分析

使用Wireshark或USBPcap进行USB通信分析：

```bash
# Windows下使用USBPcap
# 1. 安装USBPcap
# 2. 选择USB设备
# 3. 开始抓包

# Linux下使用usbmon
sudo modprobe usbmon
sudo cat /sys/kernel/debug/usb/usbmon/1u > usb_capture.log
```

### USB日志记录

```c
// USB事件日志
typedef struct {
    uint32_t timestamp_ms;
    uint8_t  event_type;
    uint16_t data_len;
    uint8_t  data[64];
} usb_log_entry_t;

#define USB_LOG_SIZE 50
usb_log_entry_t usb_log[USB_LOG_SIZE];
uint16_t usb_log_index = 0;

// 记录USB事件
void usb_log_event(uint8_t type, uint8_t *data, uint16_t len) {
    usb_log_entry_t *entry = &usb_log[usb_log_index];
    
    entry->timestamp_ms = HAL_GetTick();
    entry->event_type = type;
    entry->data_len = (len > 64) ? 64 : len;
    memcpy(entry->data, data, entry->data_len);
    
    usb_log_index = (usb_log_index + 1) % USB_LOG_SIZE;
}

// 打印USB日志
void usb_print_log(void) {
    printf("USB Event Log:\n");
    for (int i = 0; i < USB_LOG_SIZE; i++) {
        usb_log_entry_t *entry = &usb_log[i];
        if (entry->timestamp_ms > 0) {
            printf("[%lu] Type: %d, Len: %d\n",
                   entry->timestamp_ms,
                   entry->event_type,
                   entry->data_len);
        }
    }
}
```

## 最佳实践

### 1. 符合医疗设备标准

- 遵循IEC 60601-1电气安全要求
- 实现USB隔离（医疗级隔离芯片）
- 限制USB供电电流
- 实现过流保护

### 2. 数据完整性

```c
// 添加CRC校验
uint32_t calculate_crc32(uint8_t *data, uint16_t len) {
    uint32_t crc = 0xFFFFFFFF;
    
    for (uint16_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xEDB88320;
            } else {
                crc >>= 1;
            }
        }
    }
    
    return ~crc;
}

// 发送带CRC的数据
void usb_send_with_crc(uint8_t *data, uint16_t len) {
    uint8_t buffer[260];  // 数据 + CRC
    uint32_t crc;
    
    memcpy(buffer, data, len);
    crc = calculate_crc32(data, len);
    memcpy(&buffer[len], &crc, 4);
    
    usb_cdc_transmit(buffer, len + 4);
}
```

### 3. 错误处理

```c
// USB错误恢复
void usb_error_recovery(void) {
    // 重新初始化USB
    USBD_Stop(&hUsbDeviceFS);
    HAL_Delay(100);
    USBD_Start(&hUsbDeviceFS);
    
    log_warning("USB reinitialized");
}

// 超时处理
bool usb_send_with_retry(uint8_t *data, uint16_t len, uint8_t max_retries) {
    for (uint8_t i = 0; i < max_retries; i++) {
        if (usb_cdc_transmit(data, len) == HAL_OK) {
            return true;
        }
        HAL_Delay(100);
    }
    
    log_error("USB send failed after %d retries", max_retries);
    return false;
}
```

### 4. 性能优化

- 使用DMA传输大量数据
- 合理设置缓冲区大小
- 避免在中断中执行耗时操作
- 使用RTOS任务处理USB数据

## 总结

USB接口为医疗设备提供了灵活、高速的数据传输和设备互联能力。正确实现USB功能，结合适当的安全机制和错误处理，可以构建可靠的医疗设备通信系统。

## 相关资源

- [UART串口通信](uart.md)
- [IEC 62304软件生命周期](../../regulatory-standards/iec-62304.md)
- [IEC 60601-1电气安全](../../regulatory-standards/iec-60601-1.md)
