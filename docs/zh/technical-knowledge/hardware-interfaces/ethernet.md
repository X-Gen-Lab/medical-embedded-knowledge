---
title: 以太网接口
description: 医疗设备中以太网的原理、配置和网络通信实现
difficulty: intermediate
estimated_time: 2-3小时
tags: 
---



# 以太网接口

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

以太网是医疗设备网络互联的核心技术，用于连接医院信息系统（HIS）、图像存档和通信系统（PACS）、以及设备间通信。相比无线通信，以太网提供更高的可靠性、带宽和安全性。

### 医疗设备中的以太网应用

- **HIS/PACS集成**: 与医院信息系统交换患者数据和影像
- **设备互联**: 多台医疗设备组网通信
- **远程监控**: 中央监护站实时监控病房设备
- **数据传输**: 大容量医疗影像和数据传输
- **固件升级**: 通过网络进行远程固件更新
- **时间同步**: NTP时间同步确保数据时间戳准确

### 以太网标准

| 标准 | 速度 | 介质 | 医疗应用 |
|------|------|------|----------|
| 10BASE-T | 10 Mbps | 双绞线 | 简单设备 |
| 100BASE-TX | 100 Mbps | 双绞线 | 常用标准 |
| 1000BASE-T | 1 Gbps | 双绞线 | 影像设备 |
| 10GBASE-T | 10 Gbps | 双绞线 | 高端影像 |

## 硬件接口

### PHY芯片选择

常用以太网PHY芯片：

```c
// 常用PHY芯片
#define PHY_LAN8720     0x0007C0F0  // SMSC LAN8720
#define PHY_DP83848     0x20005C90  // TI DP83848
#define PHY_KSZ8081     0x00221560  // Microchip KSZ8081

// PHY寄存器
#define PHY_BCR         0x00  // 基本控制寄存器
#define PHY_BSR         0x01  // 基本状态寄存器
#define PHY_PHYID1      0x02  // PHY标识符1
#define PHY_PHYID2      0x03  // PHY标识符2
#define PHY_ANAR        0x04  // 自动协商广告寄存器
#define PHY_ANLPAR      0x05  // 自动协商链路伙伴能力寄存器
```

### RMII/MII接口

```c
// RMII接口信号（7根信号线）
// - REF_CLK: 50MHz参考时钟
// - TXD[1:0]: 发送数据
// - TX_EN: 发送使能
// - RXD[1:0]: 接收数据
// - CRS_DV: 载波侦听/数据有效

// MII接口信号（16根信号线）
// - TX_CLK, RX_CLK: 发送/接收时钟
// - TXD[3:0], RXD[3:0]: 发送/接收数据
// - TX_EN, RX_DV: 发送使能/接收数据有效
// - CRS, COL: 载波侦听/冲突检测

// STM32 RMII配置
void ethernet_gpio_init(void) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    // 使能时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    
    // RMII引脚配置
    // PA1: RMII_REF_CLK
    // PA2: RMII_MDIO
    // PA7: RMII_CRS_DV
    // PC1: RMII_MDC
    // PC4: RMII_RXD0
    // PC5: RMII_RXD1
    // PB11: RMII_TX_EN
    // PB12: RMII_TXD0
    // PB13: RMII_TXD1
    
    GPIO_InitStruct.Pin = GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_7;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF11_ETH;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    
    // 其他引脚配置...
}
```

## LwIP协议栈

### LwIP初始化

```c
#include "lwip/init.h"
#include "lwip/netif.h"
#include "lwip/timeouts.h"
#include "netif/ethernet.h"
#include "ethernetif.h"

struct netif gnetif;

// 网络配置
#define IP_ADDR0    192
#define IP_ADDR1    168
#define IP_ADDR2    1
#define IP_ADDR3    100

#define NETMASK_ADDR0   255
#define NETMASK_ADDR1   255
#define NETMASK_ADDR2   255
#define NETMASK_ADDR3   0

#define GW_ADDR0    192
#define GW_ADDR1    168
#define GW_ADDR2    1
#define GW_ADDR3    1

// LwIP初始化
void lwip_init_task(void) {
    ip4_addr_t ipaddr, netmask, gw;
    
    // 初始化LwIP
    lwip_init();
    
    // 配置IP地址
    IP4_ADDR(&ipaddr, IP_ADDR0, IP_ADDR1, IP_ADDR2, IP_ADDR3);
    IP4_ADDR(&netmask, NETMASK_ADDR0, NETMASK_ADDR1, NETMASK_ADDR2, NETMASK_ADDR3);
    IP4_ADDR(&gw, GW_ADDR0, GW_ADDR1, GW_ADDR2, GW_ADDR3);
    
    // 添加网络接口
    netif_add(&gnetif, &ipaddr, &netmask, &gw, NULL, &ethernetif_init, &ethernet_input);
    
    // 设置为默认接口
    netif_set_default(&gnetif);
    
    // 启动接口
    if (netif_is_link_up(&gnetif)) {
        netif_set_up(&gnetif);
    } else {
        netif_set_down(&gnetif);
    }
}
```

### DHCP动态IP

```c
#include "lwip/dhcp.h"

// 启用DHCP
void ethernet_dhcp_start(void) {
    dhcp_start(&gnetif);
    log_info("DHCP started");
}

// DHCP状态检查
void ethernet_dhcp_process(void) {
    static uint8_t dhcp_state = 0;
    
    switch (dhcp_state) {
        case 0:
            if (dhcp_supplied_address(&gnetif)) {
                // 获取到IP地址
                log_info("DHCP: IP assigned");
                log_info("IP: %s", ip4addr_ntoa(netif_ip4_addr(&gnetif)));
                log_info("Netmask: %s", ip4addr_ntoa(netif_ip4_netmask(&gnetif)));
                log_info("Gateway: %s", ip4addr_ntoa(netif_ip4_gw(&gnetif)));
                dhcp_state = 1;
            } else {
                // 检查超时
                struct dhcp *dhcp = netif_dhcp_data(&gnetif);
                if (dhcp->tries > MAX_DHCP_TRIES) {
                    // DHCP失败，使用静态IP
                    dhcp_stop(&gnetif);
                    use_static_ip();
                    dhcp_state = 2;
                }
            }
            break;
            
        case 1:
            // 已获取IP，监控链路状态
            if (!netif_is_link_up(&gnetif)) {
                dhcp_state = 0;
                dhcp_start(&gnetif);
            }
            break;
            
        case 2:
            // 使用静态IP
            break;
    }
}
```

## TCP/IP通信

### TCP服务器

```c
#include "lwip/tcp.h"

struct tcp_pcb *server_pcb;

// TCP服务器回调函数
err_t tcp_server_accept(void *arg, struct tcp_pcb *newpcb, err_t err) {
    err_t ret_err;
    
    log_info("TCP client connected");
    
    // 设置接收回调
    tcp_recv(newpcb, tcp_server_recv);
    
    // 设置错误回调
    tcp_err(newpcb, tcp_server_error);
    
    // 设置发送回调
    tcp_sent(newpcb, tcp_server_sent);
    
    return ERR_OK;
}

// 接收数据回调
err_t tcp_server_recv(void *arg, struct tcp_pcb *tpcb, struct pbuf *p, err_t err) {
    if (p == NULL) {
        // 连接关闭
        tcp_close(tpcb);
        log_info("TCP client disconnected");
        return ERR_OK;
    }
    
    // 处理接收到的数据
    process_tcp_data(p->payload, p->len);
    
    // 通知已接收
    tcp_recved(tpcb, p->tot_len);
    
    // 释放pbuf
    pbuf_free(p);
    
    return ERR_OK;
}

// 启动TCP服务器
void tcp_server_init(uint16_t port) {
    // 创建PCB
    server_pcb = tcp_new();
    
    if (server_pcb != NULL) {
        // 绑定端口
        err_t err = tcp_bind(server_pcb, IP_ADDR_ANY, port);
        
        if (err == ERR_OK) {
            // 监听
            server_pcb = tcp_listen(server_pcb);
            
            // 设置接受回调
            tcp_accept(server_pcb, tcp_server_accept);
            
            log_info("TCP server started on port %d", port);
        } else {
            log_error("TCP bind failed");
            memp_free(MEMP_TCP_PCB, server_pcb);
        }
    }
}

// 发送数据
err_t tcp_server_send(struct tcp_pcb *tpcb, uint8_t *data, uint16_t len) {
    err_t err;
    
    // 检查发送缓冲区
    if (tcp_sndbuf(tpcb) < len) {
        return ERR_MEM;
    }
    
    // 发送数据
    err = tcp_write(tpcb, data, len, TCP_WRITE_FLAG_COPY);
    if (err == ERR_OK) {
        tcp_output(tpcb);
    }
    
    return err;
}
```

### TCP客户端

```c
struct tcp_pcb *client_pcb;

// 连接回调
err_t tcp_client_connected(void *arg, struct tcp_pcb *tpcb, err_t err) {
    if (err == ERR_OK) {
        log_info("TCP connected to server");
        
        // 设置回调
        tcp_recv(tpcb, tcp_client_recv);
        tcp_err(tpcb, tcp_client_error);
        tcp_sent(tpcb, tcp_client_sent);
        
        // 发送初始数据
        send_hello_message(tpcb);
    } else {
        log_error("TCP connection failed");
    }
    
    return err;
}

// 连接到服务器
void tcp_client_connect(const char *server_ip, uint16_t port) {
    ip_addr_t server_addr;
    
    // 解析IP地址
    ipaddr_aton(server_ip, &server_addr);
    
    // 创建PCB
    client_pcb = tcp_new();
    
    if (client_pcb != NULL) {
        // 连接
        err_t err = tcp_connect(client_pcb, &server_addr, port, tcp_client_connected);
        
        if (err != ERR_OK) {
            log_error("TCP connect failed: %d", err);
            memp_free(MEMP_TCP_PCB, client_pcb);
        }
    }
}
```

### UDP通信

```c
#include "lwip/udp.h"

struct udp_pcb *udp_pcb;

// UDP接收回调
void udp_receive_callback(void *arg, struct udp_pcb *upcb,
                         struct pbuf *p, const ip_addr_t *addr, u16_t port) {
    if (p != NULL) {
        // 处理接收到的数据
        process_udp_data(p->payload, p->len, addr, port);
        
        // 释放pbuf
        pbuf_free(p);
    }
}

// UDP初始化
void udp_init_comm(uint16_t local_port) {
    // 创建PCB
    udp_pcb = udp_new();
    
    if (udp_pcb != NULL) {
        // 绑定端口
        err_t err = udp_bind(udp_pcb, IP_ADDR_ANY, local_port);
        
        if (err == ERR_OK) {
            // 设置接收回调
            udp_recv(udp_pcb, udp_receive_callback, NULL);
            
            log_info("UDP initialized on port %d", local_port);
        } else {
            log_error("UDP bind failed");
            udp_remove(udp_pcb);
        }
    }
}

// UDP发送
void udp_send_data(const char *dest_ip, uint16_t dest_port,
                   uint8_t *data, uint16_t len) {
    struct pbuf *p;
    ip_addr_t dest_addr;
    
    // 解析目标IP
    ipaddr_aton(dest_ip, &dest_addr);
    
    // 分配pbuf
    p = pbuf_alloc(PBUF_TRANSPORT, len, PBUF_RAM);
    
    if (p != NULL) {
        // 复制数据
        pbuf_take(p, data, len);
        
        // 发送
        udp_sendto(udp_pcb, p, &dest_addr, dest_port);
        
        // 释放pbuf
        pbuf_free(p);
    }
}
```

## 医疗协议实现

### HL7 MLLP（最小下层协议）

```c
// HL7消息分隔符
#define HL7_START_BLOCK     0x0B  // 垂直制表符
#define HL7_END_BLOCK       0x1C  // 文件分隔符
#define HL7_CARRIAGE_RETURN 0x0D  // 回车

// HL7消息结构
typedef struct {
    char message[2048];
    uint16_t length;
} hl7_message_t;

// 发送HL7消息
void send_hl7_message(struct tcp_pcb *tpcb, const char *hl7_msg) {
    uint8_t buffer[2100];
    uint16_t len = 0;
    
    // 添加起始块
    buffer[len++] = HL7_START_BLOCK;
    
    // 添加HL7消息
    uint16_t msg_len = strlen(hl7_msg);
    memcpy(&buffer[len], hl7_msg, msg_len);
    len += msg_len;
    
    // 添加结束块和回车
    buffer[len++] = HL7_END_BLOCK;
    buffer[len++] = HL7_CARRIAGE_RETURN;
    
    // 发送
    tcp_server_send(tpcb, buffer, len);
}

// 解析HL7消息
bool parse_hl7_message(uint8_t *data, uint16_t len, hl7_message_t *msg) {
    // 查找起始块
    uint16_t start = 0;
    while (start < len && data[start] != HL7_START_BLOCK) {
        start++;
    }
    
    if (start >= len) {
        return false;
    }
    
    // 查找结束块
    uint16_t end = start + 1;
    while (end < len && data[end] != HL7_END_BLOCK) {
        end++;
    }
    
    if (end >= len) {
        return false;
    }
    
    // 提取消息
    msg->length = end - start - 1;
    memcpy(msg->message, &data[start + 1], msg->length);
    msg->message[msg->length] = '\0';
    
    return true;
}

// 创建HL7 ORU消息（观察结果）
void create_hl7_oru_message(patient_data_t *data, char *buffer, uint16_t size) {
    snprintf(buffer, size,
             "MSH|^~\\&|DEVICE|HOSPITAL|HIS|HOSPITAL|%s||ORU^R01|%lu|P|2.5\r"
             "PID|1||%s||%s^%s||%s|%s\r"
             "OBR|1||%s|SPO2^Pulse Oximetry\r"
             "OBX|1|NM|SPO2^SpO2||%d|%%|95-100|N|||F\r"
             "OBX|2|NM|HR^Heart Rate||%d|bpm|60-100|N|||F\r",
             get_current_timestamp(),
             HAL_GetTick(),
             data->patient_id,
             data->last_name,
             data->first_name,
             data->birth_date,
             data->gender,
             data->order_id,
             data->spo2,
             data->heart_rate);
}
```

### DICOM网络传输

```c
// DICOM关联请求
typedef struct {
    uint8_t  pdu_type;
    uint8_t  reserved1;
    uint32_t pdu_length;
    uint16_t protocol_version;
    uint16_t reserved2;
    char     called_ae[16];
    char     calling_ae[16];
    uint8_t  reserved3[32];
} dicom_associate_rq_t;

// 发送DICOM关联请求
void send_dicom_associate_request(struct tcp_pcb *tpcb) {
    dicom_associate_rq_t assoc_rq = {0};
    
    assoc_rq.pdu_type = 0x01;  // A-ASSOCIATE-RQ
    assoc_rq.pdu_length = htonl(sizeof(dicom_associate_rq_t) - 6);
    assoc_rq.protocol_version = htons(0x0001);
    
    strncpy(assoc_rq.called_ae, "PACS_SERVER", 16);
    strncpy(assoc_rq.calling_ae, "MEDICAL_DEV", 16);
    
    tcp_server_send(tpcb, (uint8_t*)&assoc_rq, sizeof(assoc_rq));
}
```

## 网络安全

### TLS/SSL加密

```c
#include "mbedtls/ssl.h"
#include "mbedtls/net_sockets.h"

mbedtls_ssl_context ssl;
mbedtls_ssl_config conf;

// TLS初始化
int tls_init(void) {
    int ret;
    
    // 初始化SSL上下文
    mbedtls_ssl_init(&ssl);
    mbedtls_ssl_config_init(&conf);
    
    // 设置默认配置
    ret = mbedtls_ssl_config_defaults(&conf,
                                      MBEDTLS_SSL_IS_CLIENT,
                                      MBEDTLS_SSL_TRANSPORT_STREAM,
                                      MBEDTLS_SSL_PRESET_DEFAULT);
    if (ret != 0) {
        return ret;
    }
    
    // 设置证书验证
    mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_REQUIRED);
    
    // 设置CA证书
    mbedtls_ssl_conf_ca_chain(&conf, &cacert, NULL);
    
    // 应用配置
    mbedtls_ssl_setup(&ssl, &conf);
    
    return 0;
}

// TLS连接
int tls_connect(const char *hostname, uint16_t port) {
    int ret;
    mbedtls_net_context server_fd;
    
    // 初始化网络上下文
    mbedtls_net_init(&server_fd);
    
    // 连接服务器
    char port_str[6];
    snprintf(port_str, sizeof(port_str), "%d", port);
    ret = mbedtls_net_connect(&server_fd, hostname, port_str, MBEDTLS_NET_PROTO_TCP);
    if (ret != 0) {
        return ret;
    }
    
    // 设置BIO回调
    mbedtls_ssl_set_bio(&ssl, &server_fd,
                       mbedtls_net_send,
                       mbedtls_net_recv,
                       NULL);
    
    // TLS握手
    while ((ret = mbedtls_ssl_handshake(&ssl)) != 0) {
        if (ret != MBEDTLS_ERR_SSL_WANT_READ &&
            ret != MBEDTLS_ERR_SSL_WANT_WRITE) {
            return ret;
        }
    }
    
    // 验证证书
    uint32_t flags = mbedtls_ssl_get_verify_result(&ssl);
    if (flags != 0) {
        log_error("Certificate verification failed: 0x%08lx", flags);
        return -1;
    }
    
    log_info("TLS connection established");
    return 0;
}

// TLS发送数据
int tls_send(uint8_t *data, uint16_t len) {
    int ret;
    
    while ((ret = mbedtls_ssl_write(&ssl, data, len)) <= 0) {
        if (ret != MBEDTLS_ERR_SSL_WANT_READ &&
            ret != MBEDTLS_ERR_SSL_WANT_WRITE) {
            return ret;
        }
    }
    
    return ret;
}

// TLS接收数据
int tls_receive(uint8_t *buffer, uint16_t size) {
    int ret;
    
    ret = mbedtls_ssl_read(&ssl, buffer, size);
    
    if (ret == MBEDTLS_ERR_SSL_WANT_READ ||
        ret == MBEDTLS_ERR_SSL_WANT_WRITE) {
        return 0;
    }
    
    return ret;
}
```

### 防火墙和访问控制

```c
// IP白名单
typedef struct {
    ip4_addr_t ip_addr;
    bool       enabled;
} ip_whitelist_entry_t;

#define MAX_WHITELIST_ENTRIES 10
ip_whitelist_entry_t ip_whitelist[MAX_WHITELIST_ENTRIES];

// 检查IP是否在白名单中
bool is_ip_allowed(const ip4_addr_t *addr) {
    for (int i = 0; i < MAX_WHITELIST_ENTRIES; i++) {
        if (ip_whitelist[i].enabled &&
            ip4_addr_cmp(&ip_whitelist[i].ip_addr, addr)) {
            return true;
        }
    }
    return false;
}

// TCP连接过滤
err_t tcp_server_accept_filtered(void *arg, struct tcp_pcb *newpcb, err_t err) {
    // 检查客户端IP
    if (!is_ip_allowed(&newpcb->remote_ip)) {
        log_warning("Connection rejected from %s", ip4addr_ntoa(&newpcb->remote_ip));
        tcp_abort(newpcb);
        return ERR_ABRT;
    }
    
    // 允许连接
    return tcp_server_accept(arg, newpcb, err);
}
```

## 网络诊断

### Ping实现

```c
#include "lwip/icmp.h"
#include "lwip/inet_chksum.h"

// Ping请求
void send_ping(const char *dest_ip) {
    struct pbuf *p;
    struct icmp_echo_hdr *iecho;
    ip_addr_t dest_addr;
    size_t ping_size = sizeof(struct icmp_echo_hdr) + 32;
    
    // 解析目标IP
    ipaddr_aton(dest_ip, &dest_addr);
    
    // 分配pbuf
    p = pbuf_alloc(PBUF_IP, (u16_t)ping_size, PBUF_RAM);
    if (p == NULL) {
        return;
    }
    
    // 填充ICMP头
    iecho = (struct icmp_echo_hdr *)p->payload;
    ICMPH_TYPE_SET(iecho, ICMP_ECHO);
    ICMPH_CODE_SET(iecho, 0);
    iecho->chksum = 0;
    iecho->id = 0xABCD;
    iecho->seqno = htons(ping_seq_num++);
    
    // 填充数据
    memset((char*)iecho + sizeof(struct icmp_echo_hdr), 0xA5, 32);
    
    // 计算校验和
    iecho->chksum = inet_chksum(iecho, ping_size);
    
    // 发送
    raw_sendto(ping_pcb, p, &dest_addr);
    
    pbuf_free(p);
}
```

### 网络统计

```c
// 网络统计信息
typedef struct {
    uint32_t tx_packets;
    uint32_t rx_packets;
    uint32_t tx_bytes;
    uint32_t rx_bytes;
    uint32_t tx_errors;
    uint32_t rx_errors;
    uint32_t link_down_count;
} network_stats_t;

network_stats_t net_stats = {0};

// 打印网络统计
void print_network_stats(void) {
    printf("Network Statistics:\n");
    printf("  TX Packets: %lu\n", net_stats.tx_packets);
    printf("  RX Packets: %lu\n", net_stats.rx_packets);
    printf("  TX Bytes: %lu\n", net_stats.tx_bytes);
    printf("  RX Bytes: %lu\n", net_stats.rx_bytes);
    printf("  TX Errors: %lu\n", net_stats.tx_errors);
    printf("  RX Errors: %lu\n", net_stats.rx_errors);
    printf("  Link Down: %lu\n", net_stats.link_down_count);
}

// LwIP统计
void print_lwip_stats(void) {
#if LWIP_STATS
    stats_display();
#endif
}
```

## 时间同步（NTP）

```c
#include "lwip/apps/sntp.h"

// NTP初始化
void ntp_init(void) {
    // 设置NTP服务器
    sntp_setservername(0, "pool.ntp.org");
    sntp_setservername(1, "time.nist.gov");
    
    // 设置操作模式
    sntp_setoperatingmode(SNTP_OPMODE_POLL);
    
    // 启动SNTP
    sntp_init();
    
    log_info("NTP client started");
}

// 获取网络时间
time_t get_network_time(void) {
    return sntp_get_current_timestamp();
}

// 时间同步回调
void sntp_set_system_time(uint32_t sec) {
    // 更新RTC
    set_rtc_time(sec);
    
    log_info("System time synchronized: %lu", sec);
}
```

## 医疗设备应用实例

### 中央监护站

```c
// 监护站服务器
#define MONITOR_SERVER_PORT 8080
#define MAX_CONNECTED_DEVICES 20

typedef struct {
    struct tcp_pcb *pcb;
    uint8_t  device_id;
    char     device_name[32];
    uint32_t last_heartbeat_ms;
    bool     connected;
} connected_device_t;

connected_device_t connected_devices[MAX_CONNECTED_DEVICES];

// 处理设备数据
void process_device_data(uint8_t device_id, uint8_t *data, uint16_t len) {
    // 解析数据包
    device_data_packet_t *packet = (device_data_packet_t*)data;
    
    // 更新设备状态
    for (int i = 0; i < MAX_CONNECTED_DEVICES; i++) {
        if (connected_devices[i].device_id == device_id) {
            connected_devices[i].last_heartbeat_ms = HAL_GetTick();
            
            // 存储数据到数据库
            store_patient_data(packet);
            
            // 检查报警
            check_alarm_conditions(packet);
            
            // 转发到显示界面
            update_monitor_display(device_id, packet);
            
            break;
        }
    }
}

// 心跳超时检测
void check_device_heartbeat(void) {
    uint32_t current_time = HAL_GetTick();
    
    for (int i = 0; i < MAX_CONNECTED_DEVICES; i++) {
        if (connected_devices[i].connected) {
            if (current_time - connected_devices[i].last_heartbeat_ms > 10000) {
                // 10秒未收到心跳
                log_warning("Device %d timeout", connected_devices[i].device_id);
                
                // 触发报警
                trigger_device_offline_alarm(connected_devices[i].device_id);
                
                // 标记为离线
                connected_devices[i].connected = false;
            }
        }
    }
}
```

### PACS影像传输

```c
// DICOM C-STORE请求
typedef struct {
    char     patient_id[64];
    char     study_uid[128];
    char     series_uid[128];
    char     instance_uid[128];
    uint8_t  *image_data;
    uint32_t image_size;
} dicom_image_t;

// 发送DICOM影像到PACS
bool send_image_to_pacs(const char *pacs_ip, uint16_t pacs_port,
                        dicom_image_t *image) {
    struct tcp_pcb *pacs_pcb;
    ip_addr_t pacs_addr;
    
    // 解析PACS服务器地址
    ipaddr_aton(pacs_ip, &pacs_addr);
    
    // 创建TCP连接
    pacs_pcb = tcp_new();
    if (pacs_pcb == NULL) {
        return false;
    }
    
    // 连接到PACS
    err_t err = tcp_connect(pacs_pcb, &pacs_addr, pacs_port,
                           pacs_connected_callback);
    if (err != ERR_OK) {
        tcp_abort(pacs_pcb);
        return false;
    }
    
    // 等待连接建立...
    // 发送DICOM关联请求
    // 发送C-STORE请求
    // 传输影像数据
    // 关闭连接
    
    return true;
}
```

## 最佳实践

### 1. 网络可靠性

```c
// 链路状态监控
void ethernet_link_monitor(void) {
    static bool last_link_state = false;
    bool current_link_state = netif_is_link_up(&gnetif);
    
    if (current_link_state != last_link_state) {
        if (current_link_state) {
            log_info("Ethernet link up");
            netif_set_up(&gnetif);
            
            // 重新启动DHCP
            if (use_dhcp) {
                dhcp_start(&gnetif);
            }
        } else {
            log_warning("Ethernet link down");
            netif_set_down(&gnetif);
            net_stats.link_down_count++;
        }
        
        last_link_state = current_link_state;
    }
}
```

### 2. 内存管理

```c
// 配置LwIP内存池
#define MEM_SIZE                (10*1024)  // 堆大小
#define MEMP_NUM_PBUF           10         // pbuf数量
#define MEMP_NUM_TCP_PCB        10         // TCP PCB数量
#define MEMP_NUM_TCP_SEG        20         // TCP段数量
#define PBUF_POOL_SIZE          20         // pbuf池大小

// 监控内存使用
void check_lwip_memory(void) {
    size_t mem_available = mem_get_available();
    
    if (mem_available < 1024) {
        log_warning("Low memory: %d bytes available", mem_available);
    }
}
```

### 3. 符合医疗标准

- 遵循IEC 80001-1网络风险管理
- 实现网络隔离（医疗网络与办公网络分离）
- 使用加密通信保护患者数据
- 记录所有网络通信日志
- 定期进行网络安全审计

### 4. 性能优化

```c
// 启用零拷贝
#define LWIP_NETIF_TX_SINGLE_PBUF  1

// 启用校验和硬件加速
#define CHECKSUM_BY_HARDWARE       1

// 优化TCP参数
#define TCP_MSS                    1460
#define TCP_WND                    (4*TCP_MSS)
#define TCP_SND_BUF                (4*TCP_MSS)
```

## 总结

以太网为医疗设备提供了高速、可靠的网络通信能力。正确实现以太网功能，结合适当的安全机制和医疗协议，可以构建安全可靠的医疗设备网络系统。

## 相关资源

- [Wi-Fi无线通信](../wireless-communication/wifi.md)
- [IEC 62304软件生命周期](../../regulatory-standards/iec-62304.md)
- [IEC 80001-1网络风险管理](../../regulatory-standards/iec-80001-1.md)
