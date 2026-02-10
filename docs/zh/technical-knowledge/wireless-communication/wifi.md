---
title: WiFi通信技术
difficulty: intermediate
estimated_time: 2-3小时
---

# WiFi通信技术

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

WiFi是医疗器械中用于高带宽数据传输的主要无线技术。相比BLE，WiFi提供更高的数据速率，适合医学影像、视频监护、大量数据上传等应用场景。

## WiFi标准演进

| 标准 | 频段 | 最大速率 | 发布年份 | 医疗应用 |
|------|------|---------|---------|---------|
| **802.11b** | 2.4 GHz | 11 Mbps | 1999 | 已淘汰 |
| **802.11g** | 2.4 GHz | 54 Mbps | 2003 | 基础监护 |
| **802.11n** | 2.4/5 GHz | 600 Mbps | 2009 | 影像传输 |
| **802.11ac** | 5 GHz | 6.9 Gbps | 2013 | 高清影像 |
| **802.11ax (WiFi 6)** | 2.4/5 GHz | 9.6 Gbps | 2019 | 实时手术视频 |
| **802.11ax (WiFi 6E)** | 6 GHz | 9.6 Gbps | 2020 | 未来应用 |

## WiFi在医疗器械中的应用

### 典型应用场景

#### 1. 医学影像设备

```
设备类型: 便携式超声、X光、CT
数据特点: 大文件（几MB到几GB）
WiFi要求: 
- 标准: 802.11ac或更高
- 带宽: >100 Mbps
- 延迟: <100ms
- 可靠性: 高优先级QoS
```

#### 2. 患者监护系统

```
设备类型: 床旁监护仪、遥测系统
数据特点: 连续小数据流
WiFi要求:
- 标准: 802.11n或更高
- 带宽: 1-10 Mbps
- 延迟: <50ms
- 可靠性: 冗余连接
```

#### 3. 输液泵和药物管理

```
设备类型: 智能输液泵、药物配送系统
数据特点: 间歇性小数据包
WiFi要求:
- 标准: 802.11n
- 带宽: <1 Mbps
- 延迟: <200ms
- 可靠性: 关键报警优先
```

#### 4. 手术室设备

```
设备类型: 手术导航、内窥镜
数据特点: 实时视频流
WiFi要求:
- 标准: 802.11ac/ax
- 带宽: 50-200 Mbps
- 延迟: <20ms
- 可靠性: 专用SSID
```

## WiFi协议详解

### 物理层（PHY）

#### 频段选择

**2.4 GHz频段**
```
优点:
- 穿透力强
- 覆盖范围广
- 设备成本低

缺点:
- 拥挤（仅3个非重叠信道）
- 干扰多（蓝牙、微波炉等）
- 速率相对较低

医疗应用: 低带宽监护设备
```

**5 GHz频段**
```
优点:
- 更多信道（23个非重叠信道）
- 干扰少
- 速率高

缺点:
- 穿透力弱
- 覆盖范围小
- 功耗稍高

医疗应用: 影像设备、高带宽应用
```

#### 信道规划

```
2.4 GHz推荐信道（避免重叠）:
- 信道1 (2412 MHz)
- 信道6 (2437 MHz)
- 信道11 (2462 MHz)

5 GHz推荐信道（医疗环境）:
- 36, 40, 44, 48 (5.15-5.25 GHz) - 室内
- 149, 153, 157, 161 (5.725-5.825 GHz) - 室内/室外
- 避免DFS信道（52-144）以防雷达干扰
```

### MAC层

#### CSMA/CA机制

```c
// WiFi使用载波侦听多路访问/冲突避免
void wifi_transmit_frame(uint8_t *data, uint16_t len) {
    // 1. 侦听信道
    while (channel_busy()) {
        wait_random_backoff();
    }
    
    // 2. 等待DIFS（分布式帧间间隔）
    wait_difs();
    
    // 3. 发送RTS（可选，用于大帧）
    if (len > RTS_THRESHOLD) {
        send_rts();
        wait_for_cts();
    }
    
    // 4. 发送数据
    transmit(data, len);
    
    // 5. 等待ACK
    if (!wait_for_ack(TIMEOUT)) {
        retransmit();
    }
}
```

#### QoS（服务质量）

```c
// WiFi QoS优先级（WMM）
typedef enum {
    AC_BK = 0,  // Background（背景流量）
    AC_BE = 1,  // Best Effort（尽力而为）
    AC_VI = 2,  // Video（视频）
    AC_VO = 3   // Voice（语音）
} wifi_qos_ac_t;

// 医疗数据优先级映射
typedef struct {
    data_type_t type;
    wifi_qos_ac_t qos;
} medical_data_qos_t;

medical_data_qos_t qos_mapping[] = {
    {DATA_ALARM,        AC_VO},  // 报警 - 最高优先级
    {DATA_VITAL_SIGNS,  AC_VI},  // 生命体征 - 高优先级
    {DATA_WAVEFORM,     AC_VI},  // 波形数据 - 高优先级
    {DATA_IMAGE,        AC_BE},  // 影像 - 正常优先级
    {DATA_LOG,          AC_BK}   // 日志 - 低优先级
};
```

## 安全配置

### 加密标准

#### WPA2（推荐最低标准）

```c
// WPA2-PSK配置（个人模式）
typedef struct {
    char ssid[32];
    char password[64];
    wifi_auth_mode_t auth_mode;  // WPA2_PSK
    wifi_cipher_type_t cipher;   // AES
} wifi_config_psk_t;

wifi_config_psk_t config = {
    .ssid = "Hospital_Medical_Devices",
    .password = "StrongPassword123!",
    .auth_mode = WIFI_AUTH_WPA2_PSK,
    .cipher = WIFI_CIPHER_TYPE_CCMP  // AES-CCMP
};
```

#### WPA2-Enterprise（推荐医疗环境）

```c
// WPA2-Enterprise配置（企业模式）
typedef struct {
    char ssid[32];
    char identity[64];      // 用户名
    char password[64];      // 密码
    char ca_cert[2048];     // CA证书
    wifi_auth_mode_t auth_mode;  // WPA2_ENTERPRISE
    eap_method_t eap_method;     // EAP方法
} wifi_config_enterprise_t;

wifi_config_enterprise_t config = {
    .ssid = "Hospital_Secure",
    .identity = "device_12345",
    .password = "DevicePassword",
    .ca_cert = "-----BEGIN CERTIFICATE-----\n...",
    .auth_mode = WIFI_AUTH_WPA2_ENTERPRISE,
    .eap_method = EAP_METHOD_PEAP  // 或 EAP_TLS
};
```

#### WPA3（未来标准）

```
特性:
- 更强的加密（192位安全套件）
- 防暴力破解（SAE）
- 前向保密
- 简化配置（WiFi Easy Connect）

医疗应用: 新设备应考虑支持
```

### 证书管理

```c
// TLS证书验证
typedef struct {
    uint8_t *ca_cert;       // CA根证书
    uint8_t *client_cert;   // 客户端证书
    uint8_t *client_key;    // 客户端私钥
    bool verify_server;     // 验证服务器证书
} tls_config_t;

// 安全的证书存储
void store_certificates_securely() {
    // 使用安全存储区域
    secure_storage_write(CA_CERT_ID, ca_cert, ca_cert_len);
    secure_storage_write(CLIENT_CERT_ID, client_cert, cert_len);
    
    // 私钥应加密存储
    uint8_t encrypted_key[KEY_SIZE];
    encrypt_with_device_key(client_key, encrypted_key);
    secure_storage_write(CLIENT_KEY_ID, encrypted_key, KEY_SIZE);
}

// 证书过期检查
bool check_certificate_validity(uint8_t *cert) {
    time_t current_time = get_current_time();
    time_t not_before = get_cert_not_before(cert);
    time_t not_after = get_cert_not_after(cert);
    
    if (current_time < not_before || current_time > not_after) {
        log_error("Certificate expired or not yet valid");
        return false;
    }
    return true;
}
```

## 医疗环境WiFi部署

### 网络架构

```
典型医疗机构WiFi架构:

[Internet]
    |
[防火墙]
    |
[核心交换机]
    |
    +-- [医疗设备VLAN] -- [无线控制器] -- [AP] -- [医疗器械]
    |
    +-- [临床VLAN] -- [无线控制器] -- [AP] -- [医护人员设备]
    |
    +-- [访客VLAN] -- [无线控制器] -- [AP] -- [访客设备]
```

### VLAN隔离

```c
// 医疗设备应部署在独立VLAN
typedef struct {
    uint16_t vlan_id;
    char ssid[32];
    ip_addr_t subnet;
    ip_addr_t gateway;
} network_config_t;

network_config_t medical_device_network = {
    .vlan_id = 100,
    .ssid = "Medical_Devices_Only",
    .subnet = "10.100.0.0/24",
    .gateway = "10.100.0.1"
};

// 访问控制列表
typedef struct {
    ip_addr_t allowed_server;
    uint16_t allowed_port;
} acl_rule_t;

acl_rule_t device_acl[] = {
    {"10.200.1.10", 443},  // HTTPS到数据服务器
    {"10.200.1.20", 8883}, // MQTTS到消息代理
    // 拒绝其他所有连接
};
```

### 漫游支持

```c
// 802.11r快速漫游（适合移动设备）
typedef struct {
    bool ft_enabled;           // Fast Transition
    uint8_t mobility_domain[2]; // MDID
    bool over_ds;              // Over-the-DS
} fast_roaming_config_t;

fast_roaming_config_t roaming_config = {
    .ft_enabled = true,
    .mobility_domain = {0x01, 0x02},
    .over_ds = true
};

// 漫游决策
void roaming_decision() {
    int8_t current_rssi = get_current_ap_rssi();
    
    if (current_rssi < ROAMING_THRESHOLD) {
        // 扫描更好的AP
        ap_info_t *better_ap = scan_for_better_ap();
        
        if (better_ap && better_ap->rssi > current_rssi + HYSTERESIS) {
            // 执行漫游
            fast_transition_to_ap(better_ap);
        }
    }
}

// 典型阈值
#define ROAMING_THRESHOLD -75  // dBm
#define HYSTERESIS 5           // dB
```

## 功耗管理

### 省电模式

```c
// WiFi省电模式
typedef enum {
    WIFI_PS_NONE,      // 无省电
    WIFI_PS_MIN_MODEM, // 最小调制解调器省电
    WIFI_PS_MAX_MODEM  // 最大调制解调器省电
} wifi_ps_type_t;

// 根据应用选择省电模式
void configure_power_save(device_type_t type) {
    switch(type) {
        case DEVICE_CONTINUOUS_MONITOR:
            // 连续监护 - 禁用省电
            esp_wifi_set_ps(WIFI_PS_NONE);
            break;
            
        case DEVICE_PERIODIC_UPLOAD:
            // 周期上传 - 最大省电
            esp_wifi_set_ps(WIFI_PS_MAX_MODEM);
            break;
            
        case DEVICE_ON_DEMAND:
            // 按需传输 - 动态省电
            esp_wifi_set_ps(WIFI_PS_MIN_MODEM);
            break;
    }
}
```

### Listen Interval优化

```c
// Listen Interval: 设备唤醒接收信标的间隔
typedef struct {
    uint16_t listen_interval;  // 信标间隔的倍数
    uint16_t beacon_interval;  // 通常100ms
} power_save_config_t;

// 低功耗配置
power_save_config_t low_power = {
    .listen_interval = 10,     // 每1秒唤醒一次
    .beacon_interval = 100     // 100ms信标间隔
};

// 功耗对比
// Listen Interval = 1:  ~100mA (几乎无省电)
// Listen Interval = 3:  ~50mA
// Listen Interval = 10: ~20mA
// 深度睡眠:            ~10μA
```

### DTIM（Delivery Traffic Indication Message）

```c
// DTIM配置影响组播/广播接收
void configure_dtim() {
    // DTIM Period = 3 表示每3个信标发送一次DTIM
    // 设备必须在DTIM信标时唤醒以接收组播数据
    
    wifi_config_t config;
    config.sta.listen_interval = 3;  // 与DTIM Period匹配
    
    esp_wifi_set_config(WIFI_IF_STA, &config);
}
```

## 实际实现示例

### ESP32 WiFi实现

```c
#include "esp_wifi.h"
#include "esp_event.h"
#include "nvs_flash.h"

// WiFi事件处理
static void wifi_event_handler(void* arg, esp_event_base_t event_base,
                                int32_t event_id, void* event_data) {
    if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } 
    else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
        log_warning("WiFi disconnected, reconnecting...");
        esp_wifi_connect();
        xEventGroupClearBits(wifi_event_group, WIFI_CONNECTED_BIT);
    } 
    else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
        ip_event_got_ip_t* event = (ip_event_got_ip_t*) event_data;
        log_info("Got IP: " IPSTR, IP2STR(&event->ip_info.ip));
        xEventGroupSetBits(wifi_event_group, WIFI_CONNECTED_BIT);
    }
}

// 初始化WiFi
void wifi_init_sta(void) {
    // 1. 初始化NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);
    
    // 2. 初始化TCP/IP栈
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();
    
    // 3. 初始化WiFi
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    
    // 4. 注册事件处理器
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, 
                                                ESP_EVENT_ANY_ID,
                                                &wifi_event_handler, 
                                                NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, 
                                                IP_EVENT_STA_GOT_IP,
                                                &wifi_event_handler, 
                                                NULL));
    
    // 5. 配置WiFi
    wifi_config_t wifi_config = {
        .sta = {
            .ssid = "Hospital_Medical",
            .password = "SecurePassword",
            .threshold.authmode = WIFI_AUTH_WPA2_PSK,
            .pmf_cfg = {
                .capable = true,
                .required = false
            },
        },
    };
    
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());
}

// 发送数据到服务器
esp_err_t send_medical_data(const char *server_url, 
                            const uint8_t *data, 
                            size_t len) {
    esp_http_client_config_t config = {
        .url = server_url,
        .method = HTTP_METHOD_POST,
        .timeout_ms = 5000,
        .cert_pem = server_cert_pem,  // TLS证书
    };
    
    esp_http_client_handle_t client = esp_http_client_init(&config);
    
    // 设置请求头
    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_header(client, "Authorization", "Bearer TOKEN");
    
    // 发送数据
    esp_http_client_set_post_field(client, (const char*)data, len);
    
    esp_err_t err = esp_http_client_perform(client);
    
    if (err == ESP_OK) {
        int status = esp_http_client_get_status_code(client);
        log_info("HTTP POST Status = %d", status);
    } else {
        log_error("HTTP POST failed: %s", esp_err_to_name(err));
    }
    
    esp_http_client_cleanup(client);
    return err;
}
```

### Linux WiFi实现（使用wpa_supplicant）

```c
// wpa_supplicant配置文件
const char *wpa_config = 
"ctrl_interface=/var/run/wpa_supplicant\n"
"update_config=1\n"
"\n"
"network={\n"
"    ssid=\"Hospital_Secure\"\n"
"    key_mgmt=WPA-EAP\n"
"    eap=PEAP\n"
"    identity=\"device_12345\"\n"
"    password=\"DevicePassword\"\n"
"    ca_cert=\"/etc/ssl/certs/hospital_ca.pem\"\n"
"    phase2=\"auth=MSCHAPV2\"\n"
"}\n";

// 使用D-Bus控制wpa_supplicant
#include <dbus/dbus.h>

DBusConnection* init_dbus_connection() {
    DBusError error;
    dbus_error_init(&error);
    
    DBusConnection *conn = dbus_bus_get(DBUS_BUS_SYSTEM, &error);
    if (dbus_error_is_set(&error)) {
        log_error("D-Bus connection error: %s", error.message);
        dbus_error_free(&error);
        return NULL;
    }
    
    return conn;
}

// 连接到WiFi网络
bool connect_to_network(const char *ssid) {
    DBusConnection *conn = init_dbus_connection();
    if (!conn) return false;
    
    // 调用wpa_supplicant的AddNetwork方法
    DBusMessage *msg = dbus_message_new_method_call(
        "fi.w1.wpa_supplicant1",
        "/fi/w1/wpa_supplicant1",
        "fi.w1.wpa_supplicant1.Interface",
        "AddNetwork"
    );
    
    // ... 设置网络参数并发送消息
    
    return true;
}
```

## 性能优化

### TCP/IP栈优化

```c
// TCP窗口大小优化
void optimize_tcp_for_medical_imaging() {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    
    // 增大接收缓冲区（用于大文件传输）
    int recv_buf_size = 256 * 1024;  // 256KB
    setsockopt(sock, SOL_SOCKET, SO_RCVBUF, 
               &recv_buf_size, sizeof(recv_buf_size));
    
    // 增大发送缓冲区
    int send_buf_size = 256 * 1024;
    setsockopt(sock, SOL_SOCKET, SO_SNDBUF,
               &send_buf_size, sizeof(send_buf_size));
    
    // 启用TCP_NODELAY（禁用Nagle算法，减少延迟）
    int flag = 1;
    setsockopt(sock, IPPROTO_TCP, TCP_NODELAY,
               &flag, sizeof(flag));
    
    // 设置TCP keepalive
    int keepalive = 1;
    setsockopt(sock, SOL_SOCKET, SO_KEEPALIVE,
               &keepalive, sizeof(keepalive));
    
    int keepidle = 60;   // 60秒后开始探测
    int keepintvl = 10;  // 探测间隔10秒
    int keepcnt = 3;     // 探测3次
    setsockopt(sock, IPPROTO_TCP, TCP_KEEPIDLE,
               &keepidle, sizeof(keepidle));
    setsockopt(sock, IPPROTO_TCP, TCP_KEEPINTVL,
               &keepintvl, sizeof(keepintvl));
    setsockopt(sock, IPPROTO_TCP, TCP_KEEPCNT,
               &keepcnt, sizeof(keepcnt));
}
```

### 多连接并发

```c
// 使用多个TCP连接提高吞吐量
#define NUM_PARALLEL_CONNECTIONS 4

typedef struct {
    int socket;
    pthread_t thread;
    uint8_t *data_chunk;
    size_t chunk_size;
} transfer_context_t;

void* transfer_thread(void *arg) {
    transfer_context_t *ctx = (transfer_context_t*)arg;
    
    // 发送数据块
    size_t sent = 0;
    while (sent < ctx->chunk_size) {
        ssize_t n = send(ctx->socket, 
                        ctx->data_chunk + sent,
                        ctx->chunk_size - sent, 
                        0);
        if (n < 0) {
            log_error("Send failed");
            break;
        }
        sent += n;
    }
    
    return NULL;
}

// 并行传输大文件
void parallel_transfer(uint8_t *data, size_t total_size) {
    transfer_context_t contexts[NUM_PARALLEL_CONNECTIONS];
    size_t chunk_size = total_size / NUM_PARALLEL_CONNECTIONS;
    
    // 创建多个连接
    for (int i = 0; i < NUM_PARALLEL_CONNECTIONS; i++) {
        contexts[i].socket = create_connection();
        contexts[i].data_chunk = data + (i * chunk_size);
        contexts[i].chunk_size = chunk_size;
        
        pthread_create(&contexts[i].thread, NULL, 
                      transfer_thread, &contexts[i]);
    }
    
    // 等待所有传输完成
    for (int i = 0; i < NUM_PARALLEL_CONNECTIONS; i++) {
        pthread_join(contexts[i].thread, NULL);
        close(contexts[i].socket);
    }
}
```

## 故障诊断与监控

### 连接质量监控

```c
// WiFi连接质量指标
typedef struct {
    int8_t rssi;           // 信号强度 (dBm)
    uint8_t noise;         // 噪声水平
    uint32_t tx_rate;      // 发送速率 (Kbps)
    uint32_t rx_rate;      // 接收速率 (Kbps)
    uint32_t tx_packets;   // 发送包数
    uint32_t rx_packets;   // 接收包数
    uint32_t tx_errors;    // 发送错误
    uint32_t rx_errors;    // 接收错误
    uint32_t retries;      // 重传次数
} wifi_stats_t;

// 定期监控连接质量
void monitor_wifi_quality() {
    wifi_stats_t stats;
    get_wifi_stats(&stats);
    
    // 信号强度评估
    if (stats.rssi > -50) {
        log_info("Excellent signal: %d dBm", stats.rssi);
    } else if (stats.rssi > -60) {
        log_info("Good signal: %d dBm", stats.rssi);
    } else if (stats.rssi > -70) {
        log_warning("Fair signal: %d dBm", stats.rssi);
    } else {
        log_error("Poor signal: %d dBm", stats.rssi);
        // 考虑切换到备用网络或报警
    }
    
    // 错误率检查
    float error_rate = (float)(stats.tx_errors + stats.rx_errors) /
                       (stats.tx_packets + stats.rx_packets);
    if (error_rate > 0.01) {  // >1%错误率
        log_warning("High error rate: %.2f%%", error_rate * 100);
    }
    
    // 重传率检查
    float retry_rate = (float)stats.retries / stats.tx_packets;
    if (retry_rate > 0.1) {  // >10%重传率
        log_warning("High retry rate: %.2f%%", retry_rate * 100);
    }
}
```

### 网络诊断工具

```c
// Ping测试
bool test_connectivity(const char *host) {
    struct addrinfo hints, *res;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_RAW;
    hints.ai_protocol = IPPROTO_ICMP;
    
    if (getaddrinfo(host, NULL, &hints, &res) != 0) {
        return false;
    }
    
    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sock < 0) {
        freeaddrinfo(res);
        return false;
    }
    
    // 发送ICMP Echo Request
    uint8_t packet[64];
    create_icmp_echo_request(packet, sizeof(packet));
    
    sendto(sock, packet, sizeof(packet), 0,
           res->ai_addr, res->ai_addrlen);
    
    // 等待回复
    struct timeval tv = {.tv_sec = 2, .tv_usec = 0};
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    
    uint8_t reply[1024];
    ssize_t n = recvfrom(sock, reply, sizeof(reply), 0, NULL, NULL);
    
    close(sock);
    freeaddrinfo(res);
    
    return n > 0;
}

// 带宽测试
float measure_bandwidth(const char *server_url) {
    // 下载测试文件并测量速度
    time_t start = time(NULL);
    size_t bytes_received = download_test_file(server_url);
    time_t end = time(NULL);
    
    float duration = difftime(end, start);
    float bandwidth_mbps = (bytes_received * 8) / (duration * 1000000);
    
    return bandwidth_mbps;
}
```

## 安全最佳实践

### 防止常见攻击

```c
// 1. 防止SSID欺骗
bool verify_ap_identity(const char *expected_bssid) {
    wifi_ap_record_t ap_info;
    esp_wifi_sta_get_ap_info(&ap_info);
    
    // 验证BSSID（MAC地址）
    if (memcmp(ap_info.bssid, expected_bssid, 6) != 0) {
        log_error("AP BSSID mismatch - possible rogue AP");
        esp_wifi_disconnect();
        return false;
    }
    
    return true;
}

// 2. 实现证书固定
bool verify_server_certificate(const uint8_t *cert, size_t cert_len) {
    // 计算证书指纹
    uint8_t fingerprint[32];
    mbedtls_sha256(cert, cert_len, fingerprint, 0);
    
    // 与预期指纹比较
    const uint8_t expected_fingerprint[32] = {
        0x12, 0x34, 0x56, /* ... */
    };
    
    if (memcmp(fingerprint, expected_fingerprint, 32) != 0) {
        log_error("Certificate fingerprint mismatch");
        return false;
    }
    
    return true;
}

// 3. 实现重放攻击防护
typedef struct {
    uint32_t sequence_number;
    uint64_t timestamp;
    uint8_t nonce[16];
} secure_message_t;

bool validate_message(secure_message_t *msg) {
    static uint32_t last_seq = 0;
    
    // 检查序列号
    if (msg->sequence_number <= last_seq) {
        log_error("Replay attack detected");
        return false;
    }
    
    // 检查时间戳（允许5分钟时钟偏差）
    uint64_t current_time = get_current_timestamp();
    if (abs(current_time - msg->timestamp) > 300) {
        log_error("Message timestamp out of range");
        return false;
    }
    
    last_seq = msg->sequence_number;
    return true;
}
```

## 测试与验证

### 性能测试

```python
# 使用iperf3进行吞吐量测试
import subprocess
import json

def test_wifi_throughput(server_ip):
    # TCP测试
    result = subprocess.run([
        'iperf3', '-c', server_ip,
        '-t', '30',  # 30秒测试
        '-J'         # JSON输出
    ], capture_output=True, text=True)
    
    data = json.loads(result.stdout)
    throughput_mbps = data['end']['sum_received']['bits_per_second'] / 1e6
    
    print(f"TCP Throughput: {throughput_mbps:.2f} Mbps")
    
    # UDP测试
    result = subprocess.run([
        'iperf3', '-c', server_ip,
        '-u',            # UDP模式
        '-b', '100M',    # 目标带宽
        '-t', '30',
        '-J'
    ], capture_output=True, text=True)
    
    data = json.loads(result.stdout)
    jitter = data['end']['sum']['jitter_ms']
    packet_loss = data['end']['sum']['lost_percent']
    
    print(f"UDP Jitter: {jitter:.2f} ms")
    print(f"Packet Loss: {packet_loss:.2f}%")
```

### 漫游测试

```python
# 测试设备在AP间漫游
def test_roaming():
    import time
    import subprocess
    
    # 记录初始AP
    initial_ap = get_current_ap_bssid()
    print(f"Initial AP: {initial_ap}")
    
    # 移动设备或降低信号
    print("Move device or reduce signal strength...")
    time.sleep(10)
    
    # 检查是否漫游到新AP
    new_ap = get_current_ap_bssid()
    if new_ap != initial_ap:
        print(f"Roamed to new AP: {new_ap}")
        
        # 测试漫游期间的数据丢失
        packet_loss = measure_packet_loss_during_roaming()
        print(f"Packet loss during roaming: {packet_loss}%")
    else:
        print("No roaming occurred")
```

## 常见问题解决

### 连接失败

```c
// 诊断连接失败原因
void diagnose_connection_failure(wifi_err_reason_t reason) {
    switch(reason) {
        case WIFI_REASON_AUTH_EXPIRE:
            log_error("Authentication expired - check credentials");
            break;
            
        case WIFI_REASON_4WAY_HANDSHAKE_TIMEOUT:
            log_error("4-way handshake timeout - check password");
            break;
            
        case WIFI_REASON_NO_AP_FOUND:
            log_error("AP not found - check SSID and range");
            break;
            
        case WIFI_REASON_ASSOC_FAIL:
            log_error("Association failed - AP may be full");
            break;
            
        case WIFI_REASON_HANDSHAKE_TIMEOUT:
            log_error("Handshake timeout - check signal strength");
            break;
            
        default:
            log_error("Connection failed: reason %d", reason);
    }
}
```

### 性能下降

```c
// 性能问题排查
void troubleshoot_performance() {
    // 1. 检查信道拥塞
    wifi_scan_config_t scan_config = {
        .show_hidden = true,
        .scan_type = WIFI_SCAN_TYPE_ACTIVE
    };
    esp_wifi_scan_start(&scan_config, true);
    
    uint16_t ap_count = 0;
    esp_wifi_scan_get_ap_num(&ap_count);
    
    if (ap_count > 10) {
        log_warning("Crowded WiFi environment: %d APs detected", ap_count);
    }
    
    // 2. 检查干扰
    int8_t noise_floor = get_noise_floor();
    if (noise_floor > -85) {
        log_warning("High noise floor: %d dBm", noise_floor);
    }
    
    // 3. 检查PHY速率
    wifi_sta_info_t sta_info;
    esp_wifi_sta_get_info(&sta_info);
    
    if (sta_info.phy_11n == 0) {
        log_warning("Not using 802.11n - check AP configuration");
    }
}
```

## 参考资源

- [IEEE 802.11 Standards](https://www.ieee802.org/11/)
- [WiFi Alliance Certification](https://www.wi-fi.org/)
- [ESP32 WiFi Driver](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-guides/wifi.html)
- [wpa_supplicant Documentation](https://w1.fi/wpa_supplicant/)
- [AAMI TIR57 - Wireless Coexistence](https://www.aami.org/)

---

**下一步**: 探索 [其他无线技术](other-wireless.md)
