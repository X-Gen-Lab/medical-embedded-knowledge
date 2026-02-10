---
title: "实时操作系统（RTOS）"
description: "RTOS知识，包含任务调度、同步机制、中断处理和资源管理"
difficulty: "中级"
estimated_time: "10小时"
tags: ["RTOS", "任务调度", "实时系统"]
---

# 实时操作系统（RTOS）

本模块涵盖医疗器械嵌入式软件开发中的实时操作系统核心知识。

## 主要内容

### 核心概念
- [任务调度](task-scheduling.md) - 优先级调度、时间片轮转和调度策略
- [同步机制](synchronization.md) - 信号量、互斥锁、事件标志
- [中断处理](interrupt-handling.md) - 中断服务程序和中断优先级管理
- [RTOS资源管理](resource-management.md) - 内存管理和资源分配

### RTOS选型与优化
- [RTOS选型指南](rtos-selection-guide.md) - FreeRTOS、Zephyr、ThreadX等主流RTOS对比与选择
- [多RTOS对比表](rtos-comparison.md) - 详细的技术特性和性能对比
- [RTOS性能调优](rtos-performance-tuning.md) - 任务优化、内存管理、中断处理优化
- [RTOS安全认证](rtos-safety-certification.md) - SafeRTOS、ThreadX等认证RTOS详解

## 学习路径

建议按以下顺序学习：

1. **基础阶段**：
   - 任务调度 → 同步机制 → 中断处理
   
2. **进阶阶段**：
   - 资源管理 → RTOS选型指南 → 多RTOS对比表
   
3. **高级阶段**：
   - RTOS性能调优 → RTOS安全认证

## 相关资源

- [嵌入式C/C++编程](../embedded-c-cpp/index.md)
- [硬件接口](../hardware-interfaces/index.md)
- [软件架构设计](../../software-engineering/architecture-design/index.md)
