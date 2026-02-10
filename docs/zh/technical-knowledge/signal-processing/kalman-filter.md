---
title: "卡尔曼滤波器（Kalman Filter）"
description: "卡尔曼滤波器原理与实现，包括标准卡尔曼滤波、扩展卡尔曼滤波及医疗信号处理应用"
difficulty: "高级"
estimated_time: "3小时"
tags: ["卡尔曼滤波", "状态估计", "传感器融合", "信号处理"]
related_modules:
  - zh/technical-knowledge/signal-processing/adaptive-filters
  - zh/technical-knowledge/signal-processing/digital-filters
  - zh/technical-knowledge/rtos/task-scheduling
last_updated: 2026-02-10
version: 1.0
language: zh-CN
---

# 卡尔曼滤波器（Kalman Filter）

## 📋 学习目标

完成本章学习后，您将能够：

- ✅ 理解卡尔曼滤波器的基本原理
- ✅ 实现标准卡尔曼滤波器（KF）
- ✅ 实现扩展卡尔曼滤波器（EKF）
- ✅ 应用卡尔曼滤波器进行传感器融合
- ✅ 在医疗信号处理中应用卡尔曼滤波

## 前置知识

- 线性代数（矩阵运算）
- 概率论与统计
- 状态空间模型
- C/C++编程

---

## 1. 卡尔曼滤波器基础

### 1.1 什么是卡尔曼滤波器？

卡尔曼滤波器是一种**最优递归数据处理算法**，用于从一系列含有噪声的测量中估计动态系统的状态。

**核心思想**：
- 使用系统的动态模型进行预测
- 使用测量值进行校正
- 在预测和测量之间找到最优平衡

**优势**：
- ✅ 最优估计（最小均方误差）
- ✅ 递归计算（不需要存储历史数据）
- ✅ 实时性好
- ✅ 能融合多个传感器

### 1.2 系统模型

卡尔曼滤波器基于两个模型：

**状态方程（预测模型）**：
```
x(k) = F·x(k-1) + B·u(k) + w(k)
```

**观测方程（测量模型）**：
```
z(k) = H·x(k) + v(k)
```

其中：
- `x(k)`：k时刻的状态向量
- `F`：状态转移矩阵
- `B`：控制输入矩阵
- `u(k)`：控制输入
- `w(k)`：过程噪声，协方差为Q
- `z(k)`：测量向量
- `H`：观测矩阵
- `v(k)`：测量噪声，协方差为R


### 1.3 卡尔曼滤波器算法

**预测步骤**：
```
1. 状态预测：    x̂(k|k-1) = F·x̂(k-1|k-1) + B·u(k)
2. 协方差预测：  P(k|k-1) = F·P(k-1|k-1)·F^T + Q
```

**更新步骤**：
```
3. 卡尔曼增益：  K(k) = P(k|k-1)·H^T·[H·P(k|k-1)·H^T + R]^(-1)
4. 状态更新：    x̂(k|k) = x̂(k|k-1) + K(k)·[z(k) - H·x̂(k|k-1)]
5. 协方差更新：  P(k|k) = [I - K(k)·H]·P(k|k-1)
```

**符号说明**：
- `x̂(k|k-1)`：基于k-1时刻的k时刻状态预测
- `x̂(k|k)`：基于k时刻测量的k时刻状态估计
- `P(k|k)`：估计误差协方差矩阵
- `K(k)`：卡尔曼增益

---

## 2. 标准卡尔曼滤波器实现

### 2.1 数据结构定义

```c
#include <stdint.h>
#include <string.h>
#include <math.h>

#define MAX_STATE_DIM 10    // 最大状态维度
#define MAX_MEAS_DIM 5      // 最大测量维度

typedef struct {
    // 状态向量和协方差
    float x[MAX_STATE_DIM];              // 状态估计
    float P[MAX_STATE_DIM][MAX_STATE_DIM]; // 误差协方差
    
    // 系统矩阵
    float F[MAX_STATE_DIM][MAX_STATE_DIM]; // 状态转移矩阵
    float H[MAX_MEAS_DIM][MAX_STATE_DIM];  // 观测矩阵
    float Q[MAX_STATE_DIM][MAX_STATE_DIM]; // 过程噪声协方差
    float R[MAX_MEAS_DIM][MAX_MEAS_DIM];   // 测量噪声协方差
    float B[MAX_STATE_DIM][MAX_STATE_DIM]; // 控制输入矩阵（可选）
    
    // 维度
    uint8_t state_dim;   // 状态维度
    uint8_t meas_dim;    // 测量维度
    
    // 临时变量（避免重复分配）
    float K[MAX_STATE_DIM][MAX_MEAS_DIM];  // 卡尔曼增益
    float temp_x[MAX_STATE_DIM];
    float temp_P[MAX_STATE_DIM][MAX_STATE_DIM];
} KalmanFilter;

/**
 * @brief 初始化卡尔曼滤波器
 */
void kalman_filter_init(KalmanFilter* kf, uint8_t state_dim, uint8_t meas_dim) {
    kf->state_dim = state_dim;
    kf->meas_dim = meas_dim;
    
    // 初始化为零
    memset(kf->x, 0, sizeof(kf->x));
    memset(kf->P, 0, sizeof(kf->P));
    memset(kf->F, 0, sizeof(kf->F));
    memset(kf->H, 0, sizeof(kf->H));
    memset(kf->Q, 0, sizeof(kf->Q));
    memset(kf->R, 0, sizeof(kf->R));
    memset(kf->B, 0, sizeof(kf->B));
    
    // P初始化为单位矩阵
    for (uint8_t i = 0; i < state_dim; i++) {
        kf->P[i][i] = 1.0f;
    }
}
```

### 2.2 矩阵运算辅助函数

```c
/**
 * @brief 矩阵乘法 C = A * B
 */
void matrix_multiply(const float A[][MAX_STATE_DIM], uint8_t A_rows, uint8_t A_cols,
                     const float B[][MAX_STATE_DIM], uint8_t B_cols,
                     float C[][MAX_STATE_DIM]) {
    for (uint8_t i = 0; i < A_rows; i++) {
        for (uint8_t j = 0; j < B_cols; j++) {
            C[i][j] = 0.0f;
            for (uint8_t k = 0; k < A_cols; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

/**
 * @brief 矩阵转置 B = A^T
 */
void matrix_transpose(const float A[][MAX_STATE_DIM], uint8_t rows, uint8_t cols,
                      float B[][MAX_STATE_DIM]) {
    for (uint8_t i = 0; i < rows; i++) {
        for (uint8_t j = 0; j < cols; j++) {
            B[j][i] = A[i][j];
        }
    }
}

/**
 * @brief 矩阵求逆（使用高斯-约旦消元法）
 * @note 仅适用于小矩阵，大矩阵应使用更高效的算法
 */
int matrix_inverse(float A[][MAX_MEAS_DIM], uint8_t n, 
                   float A_inv[][MAX_MEAS_DIM]) {
    
    // 创建增广矩阵 [A | I]
    float aug[MAX_MEAS_DIM][2 * MAX_MEAS_DIM];
    
    for (uint8_t i = 0; i < n; i++) {
        for (uint8_t j = 0; j < n; j++) {
            aug[i][j] = A[i][j];
            aug[i][j + n] = (i == j) ? 1.0f : 0.0f;
        }
    }
    
    // 高斯-约旦消元
    for (uint8_t i = 0; i < n; i++) {
        // 寻找主元
        float pivot = aug[i][i];
        if (fabsf(pivot) < 1e-10f) {
            return -1;  // 矩阵奇异
        }
        
        // 归一化当前行
        for (uint8_t j = 0; j < 2 * n; j++) {
            aug[i][j] /= pivot;
        }
        
        // 消元
        for (uint8_t k = 0; k < n; k++) {
            if (k != i) {
                float factor = aug[k][i];
                for (uint8_t j = 0; j < 2 * n; j++) {
                    aug[k][j] -= factor * aug[i][j];
                }
            }
        }
    }
    
    // 提取逆矩阵
    for (uint8_t i = 0; i < n; i++) {
        for (uint8_t j = 0; j < n; j++) {
            A_inv[i][j] = aug[i][j + n];
        }
    }
    
    return 0;
}
```

### 2.3 预测步骤

```c
/**
 * @brief 卡尔曼滤波器预测步骤
 * @param kf 卡尔曼滤波器结构
 * @param u 控制输入（可为NULL）
 */
void kalman_predict(KalmanFilter* kf, const float* u) {
    uint8_t n = kf->state_dim;
    
    // 1. 状态预测：x̂(k|k-1) = F·x̂(k-1|k-1) + B·u(k)
    for (uint8_t i = 0; i < n; i++) {
        kf->temp_x[i] = 0.0f;
        for (uint8_t j = 0; j < n; j++) {
            kf->temp_x[i] += kf->F[i][j] * kf->x[j];
        }
        
        // 添加控制输入（如果有）
        if (u != NULL) {
            for (uint8_t j = 0; j < n; j++) {
                kf->temp_x[i] += kf->B[i][j] * u[j];
            }
        }
    }
    
    // 更新状态
    memcpy(kf->x, kf->temp_x, n * sizeof(float));
    
    // 2. 协方差预测：P(k|k-1) = F·P(k-1|k-1)·F^T + Q
    
    // 计算 F·P
    float FP[MAX_STATE_DIM][MAX_STATE_DIM];
    matrix_multiply(kf->F, n, n, kf->P, n, FP);
    
    // 计算 F^T
    float FT[MAX_STATE_DIM][MAX_STATE_DIM];
    matrix_transpose(kf->F, n, n, FT);
    
    // 计算 F·P·F^T
    matrix_multiply(FP, n, n, FT, n, kf->temp_P);
    
    // 添加过程噪声 Q
    for (uint8_t i = 0; i < n; i++) {
        for (uint8_t j = 0; j < n; j++) {
            kf->P[i][j] = kf->temp_P[i][j] + kf->Q[i][j];
        }
    }
}
```

### 2.4 更新步骤

```c
/**
 * @brief 卡尔曼滤波器更新步骤
 * @param kf 卡尔曼滤波器结构
 * @param z 测量向量
 */
void kalman_update(KalmanFilter* kf, const float* z) {
    uint8_t n = kf->state_dim;
    uint8_t m = kf->meas_dim;
    
    // 1. 计算创新（innovation）：y = z - H·x̂(k|k-1)
    float y[MAX_MEAS_DIM];
    for (uint8_t i = 0; i < m; i++) {
        y[i] = z[i];
        for (uint8_t j = 0; j < n; j++) {
            y[i] -= kf->H[i][j] * kf->x[j];
        }
    }
    
    // 2. 计算创新协方差：S = H·P·H^T + R
    
    // 计算 H·P
    float HP[MAX_MEAS_DIM][MAX_STATE_DIM];
    for (uint8_t i = 0; i < m; i++) {
        for (uint8_t j = 0; j < n; j++) {
            HP[i][j] = 0.0f;
            for (uint8_t k = 0; k < n; k++) {
                HP[i][j] += kf->H[i][k] * kf->P[k][j];
            }
        }
    }
    
    // 计算 H^T
    float HT[MAX_STATE_DIM][MAX_MEAS_DIM];
    for (uint8_t i = 0; i < m; i++) {
        for (uint8_t j = 0; j < n; j++) {
            HT[j][i] = kf->H[i][j];
        }
    }
    
    // 计算 S = H·P·H^T + R
    float S[MAX_MEAS_DIM][MAX_MEAS_DIM];
    for (uint8_t i = 0; i < m; i++) {
        for (uint8_t j = 0; j < m; j++) {
            S[i][j] = kf->R[i][j];
            for (uint8_t k = 0; k < n; k++) {
                S[i][j] += HP[i][k] * HT[k][j];
            }
        }
    }
    
    // 3. 计算卡尔曼增益：K = P·H^T·S^(-1)
    
    // 计算 S^(-1)
    float S_inv[MAX_MEAS_DIM][MAX_MEAS_DIM];
    if (matrix_inverse(S, m, S_inv) != 0) {
        // 矩阵奇异，跳过更新
        return;
    }
    
    // 计算 P·H^T
    float PHT[MAX_STATE_DIM][MAX_MEAS_DIM];
    for (uint8_t i = 0; i < n; i++) {
        for (uint8_t j = 0; j < m; j++) {
            PHT[i][j] = 0.0f;
            for (uint8_t k = 0; k < n; k++) {
                PHT[i][j] += kf->P[i][k] * HT[k][j];
            }
        }
    }
    
    // 计算 K = P·H^T·S^(-1)
    for (uint8_t i = 0; i < n; i++) {
        for (uint8_t j = 0; j < m; j++) {
            kf->K[i][j] = 0.0f;
            for (uint8_t k = 0; k < m; k++) {
                kf->K[i][j] += PHT[i][k] * S_inv[k][j];
            }
        }
    }
    
    // 4. 状态更新：x̂(k|k) = x̂(k|k-1) + K·y
    for (uint8_t i = 0; i < n; i++) {
        for (uint8_t j = 0; j < m; j++) {
            kf->x[i] += kf->K[i][j] * y[j];
        }
    }
    
    // 5. 协方差更新：P(k|k) = (I - K·H)·P(k|k-1)
    
    // 计算 K·H
    float KH[MAX_STATE_DIM][MAX_STATE_DIM];
    for (uint8_t i = 0; i < n; i++) {
        for (uint8_t j = 0; j < n; j++) {
            KH[i][j] = 0.0f;
            for (uint8_t k = 0; k < m; k++) {
                KH[i][j] += kf->K[i][k] * kf->H[k][j];
            }
        }
    }
    
    // 计算 (I - K·H)·P
    for (uint8_t i = 0; i < n; i++) {
        for (uint8_t j = 0; j < n; j++) {
            float I_KH = (i == j) ? 1.0f : 0.0f;
            I_KH -= KH[i][j];
            
            kf->temp_P[i][j] = 0.0f;
            for (uint8_t k = 0; k < n; k++) {
                float I_KH_k = (i == k) ? 1.0f : 0.0f;
                I_KH_k -= KH[i][k];
                kf->temp_P[i][j] += I_KH_k * kf->P[k][j];
            }
        }
    }
    
    // 更新P
    memcpy(kf->P, kf->temp_P, sizeof(kf->temp_P));
}
```

