---
title: "术语表 / Glossary"
description: "医疗器械嵌入式软件开发相关术语的中英文对照和定义"
difficulty: 基础
estimated_time: 30分钟
tags:
  - glossary
  - terminology
  - reference
  - bilingual
language: "zh-CN"
---

# 术语表 / Glossary

本术语表提供医疗器械嵌入式软件开发中常用术语的定义和中英文对照。

This glossary provides definitions and Chinese-English translations for common terms in medical device embedded software development.

---

## A

### ADC (Analog-to-Digital Converter) | 模数转换器
将模拟信号转换为数字信号的电子器件。在医疗器械中用于采集传感器信号。

An electronic device that converts analog signals to digital signals. Used in medical devices to acquire sensor signals.

### Acceptance Criteria | 验收标准
定义软件需求是否满足的可验证条件。

Verifiable conditions that define whether software requirements are met.

---

## B

### BSS Segment | BSS段
存储未初始化全局变量和静态变量的内存区域，程序启动时清零。

Memory region storing uninitialized global and static variables, zeroed at program startup.

### Buffer Overflow | 缓冲区溢出
向缓冲区写入超过其容量的数据，可能导致安全漏洞。

Writing data beyond a buffer's capacity, potentially causing security vulnerabilities.

---

## C

### CERT C | CERT C安全编码标准
由卡内基梅隆大学软件工程研究所开发的C语言安全编码标准，专注于安全漏洞预防。

C language secure coding standard developed by Carnegie Mellon University's Software Engineering Institute, focusing on security vulnerability prevention.

### Class A/B/C Software | A/B/C类软件
IEC 62304定义的软件安全分类：Class A（低风险）、Class B（中风险）、Class C（高风险）。

Software safety classification defined by IEC 62304: Class A (low risk), Class B (medium risk), Class C (high risk).

### Configuration Management | 配置管理
系统地管理软件配置项的变更和版本的过程。

Process of systematically managing changes and versions of software configuration items.

---

## D

### DAC (Digital-to-Analog Converter) | 数模转换器
将数字信号转换为模拟信号的电子器件。

An electronic device that converts digital signals to analog signals.

### DMA (Direct Memory Access) | 直接内存访问
允许外设直接访问内存而不需要CPU干预的技术。

Technology allowing peripherals to access memory directly without CPU intervention.

---

## E

### EMC (Electromagnetic Compatibility) | 电磁兼容性
设备在电磁环境中正常工作且不对其他设备产生干扰的能力。

Ability of equipment to function properly in electromagnetic environment without causing interference to other equipment.

### Embedded System | 嵌入式系统
专用于特定功能的计算机系统，通常集成在更大的设备中。

Computer system dedicated to specific functions, typically integrated into larger devices.

---

## F

### FDA (Food and Drug Administration) | 美国食品药品监督管理局
负责监管美国医疗器械的联邦机构。

Federal agency responsible for regulating medical devices in the United States.

### FFT (Fast Fourier Transform) | 快速傅里叶变换
一种高效计算离散傅里叶变换的算法，用于信号处理。

An efficient algorithm for computing discrete Fourier transform, used in signal processing.

### Firmware | 固件
存储在非易失性存储器中的软件，控制硬件设备的基本功能。

Software stored in non-volatile memory that controls basic hardware device functions.

---

## H

### HAL (Hardware Abstraction Layer) | 硬件抽象层
提供统一接口访问硬件的软件层，隔离硬件依赖。

Software layer providing unified interface to access hardware, isolating hardware dependencies.

### Heap | 堆
用于动态内存分配的内存区域，由程序员手动管理。

Memory region for dynamic memory allocation, manually managed by programmers.

---

## I

### I2C (Inter-Integrated Circuit) | 集成电路总线
一种串行通信协议，用于连接低速外围设备。支持多主机和多从机。

Serial communication protocol for connecting low-speed peripheral devices. Supports multiple masters and slaves.

### IEC (International Electrotechnical Commission) | 国际电工委员会
制定电气和电子技术国际标准的组织。

Organization that develops international standards for electrical and electronic technologies.

### IEC 62304 | IEC 62304标准
医疗器械软件生命周期过程国际标准。

International standard for medical device software lifecycle processes.

### Interrupt | 中断
硬件或软件事件，暂停当前程序执行以处理紧急任务。

Hardware or software event that suspends current program execution to handle urgent tasks.

### ISO (International Organization for Standardization) | 国际标准化组织
制定国际标准的独立非政府组织。

Independent non-governmental organization that develops international standards.

### ISO 13485 | ISO 13485标准
医疗器械质量管理体系国际标准。

International standard for medical device quality management systems.

### ISO 14971 | ISO 14971标准
医疗器械风险管理国际标准。

International standard for medical device risk management.

---

## M

### Memory Fragmentation | 内存碎片
频繁分配和释放内存导致的内存空间不连续现象。

Non-contiguous memory space resulting from frequent allocation and deallocation.

### Memory Leak | 内存泄漏
程序分配内存后未能正确释放，导致可用内存逐渐减少。

Failure to properly release allocated memory, causing gradual reduction in available memory.

### Memory Pool | 内存池
预先分配的固定大小内存块集合，提供确定性的内存管理。

Collection of pre-allocated fixed-size memory blocks providing deterministic memory management.

### MISRA C | MISRA C编码标准
汽车工业软件可靠性协会制定的C语言编码标准，广泛应用于安全关键系统。

C language coding standard developed by Motor Industry Software Reliability Association, widely used in safety-critical systems.

### MPU (Memory Protection Unit) | 内存保护单元
硬件组件，用于保护内存区域免受非法访问。

Hardware component used to protect memory regions from illegal access.

---

## P

### PMA (Premarket Approval) | 上市前批准
FDA对高风险医疗器械的审批流程。

FDA approval process for high-risk medical devices.

### Pointer | 指针
存储内存地址的变量，用于间接访问数据。

Variable storing memory address, used for indirect data access.

### Property-Based Testing | 基于属性的测试
通过验证系统属性在大量随机输入下保持不变来测试软件的方法。

Testing method that verifies system properties hold across many random inputs.

---

## R

### Real-Time System | 实时系统
必须在规定时间内响应事件的系统，分为硬实时和软实时。

System that must respond to events within specified time, classified as hard real-time or soft real-time.

### Requirements Traceability | 需求追溯
建立需求与设计、实现、测试之间的关联关系。

Establishing relationships between requirements and design, implementation, and testing.

### Risk Management | 风险管理
识别、评估和控制产品风险的系统过程。

Systematic process of identifying, evaluating, and controlling product risks.

### RTOS (Real-Time Operating System) | 实时操作系统
能够在规定时间内响应外部事件的操作系统。

Operating system capable of responding to external events within specified time.

---

## S

### Safety Classification | 安全分类
根据软件故障可能造成的危害程度对软件进行分类。

Classifying software based on severity of harm that software failure may cause.

### SOUP (Software of Unknown Provenance) | 来源不明软件
第三方软件、开源软件或商业现成软件，需要特殊管理。

Third-party software, open-source software, or commercial off-the-shelf software requiring special management.

### SPI (Serial Peripheral Interface) | 串行外设接口
一种高速全双工同步串行通信协议。

High-speed full-duplex synchronous serial communication protocol.

### Stack | 栈
自动管理的内存区域，用于存储局部变量和函数调用信息。

Automatically managed memory region for storing local variables and function call information.

### Stack Overflow | 栈溢出
栈内存使用超过分配大小，可能导致系统崩溃。

Stack memory usage exceeding allocated size, potentially causing system crash.

### Static Analysis | 静态分析
不执行程序而分析源代码以发现潜在缺陷的技术。

Technique of analyzing source code without executing it to find potential defects.

### Static Memory | 静态内存
在编译时分配、生命周期贯穿整个程序的内存。

Memory allocated at compile time with lifetime spanning entire program execution.

---

## T

### Task Scheduling | 任务调度
RTOS中决定哪个任务在何时执行的机制。

Mechanism in RTOS determining which task executes when.

### Traceability Matrix | 追溯矩阵
文档化需求与其他工件（设计、测试等）之间关系的表格。

Table documenting relationships between requirements and other artifacts (design, tests, etc.).

---

## U

### UART (Universal Asynchronous Receiver/Transmitter) | 通用异步收发器
一种异步串行通信协议，常用于设备间通信。

Asynchronous serial communication protocol commonly used for inter-device communication.

### Unit Testing | 单元测试
对软件最小可测试单元进行验证的测试方法。

Testing method that verifies smallest testable units of software.

---

## V

### Validation | 确认
验证产品满足用户需求和预期用途的过程。

Process of verifying product meets user needs and intended use.

### Verification | 验证
验证产品满足规定需求的过程。

Process of verifying product meets specified requirements.

---

## W

### Watchdog Timer | 看门狗定时器
硬件或软件定时器，用于检测和恢复系统故障。

Hardware or software timer used to detect and recover from system failures.

---

*本术语表持续更新中。如有建议或补充，欢迎反馈。*

*This glossary is continuously updated. Suggestions and additions are welcome.*
