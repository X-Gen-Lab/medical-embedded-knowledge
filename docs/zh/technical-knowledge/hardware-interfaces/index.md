---
title: "硬件接口"
description: "硬件接口知识，包含I2C、SPI、UART、ADC、DAC、GPIO、CAN、USB、以太网和显示接口"
difficulty: "中级"
estimated_time: "12小时"
tags: ["硬件接口", "I2C", "SPI", "UART", "CAN", "USB", "以太网", "显示"]
---

# 硬件接口

本模块涵盖医疗器械嵌入式软件开发中的硬件接口核心知识，从基础的串行通信到复杂的网络接口和显示系统。

## 基础通信接口

- [I2C通信协议](i2c.md) - 两线式串行总线，用于连接传感器和外设
- [SPI通信协议](spi.md) - 高速全双工串行通信，用于存储器和显示器
- [UART通信协议](uart.md) - 异步串行通信，用于调试和设备通信
- [GPIO操作](gpio.md) - 通用输入输出，用于控制和状态检测

## 数据采集接口

- [ADC/DAC转换器](adc-dac.md) - 模拟数字转换，用于生理信号采集

## 高级通信接口

- [CAN总线通信](can-bus.md) - 医疗设备内部和设备间的可靠实时通信
- [USB接口](usb.md) - 数据传输、固件升级和设备充电
- [以太网接口](ethernet.md) - 医院网络集成和高速数据传输

## 人机交互接口

- [显示接口](display.md) - LCD、OLED、TFT显示驱动和GUI实现
