---
title: "剂量计算"
description: "放射治疗中的剂量计算方法、算法和质量保证，确保治疗的准确性和安全性"
difficulty: 高级
estimated_time: 3-4小时
tags:
  - radiation-therapy
  - dose-calculation
  - treatment-planning
  - medical-physics
last_updated: "2026-02-11"
version: "1.0"
language: "zh-CN"
related_modules:
  - "zh/domain-specific/radiation-therapy/overview"
  - "zh/domain-specific/radiation-therapy/safety-interlocks"
---

# 剂量计算

## 学习目标

通过本文档的学习，你将能够：

- 理解放射治疗剂量计算的基本原理
- 掌握常用的剂量计算算法
- 了解剂量计算的质量保证方法
- 理解剂量计算在治疗计划中的应用

## 前置知识

在学习本文档之前，建议你已经掌握：

- 放射物理学基础
- 医学影像学基础
- 基本的数值计算方法
- 放射治疗系统概述

## 概述

剂量计算是放射治疗计划系统（TPS）的核心功能，用于精确计算患者体内的辐射剂量分布。准确的剂量计算对于确保治疗效果和患者安全至关重要。

## 剂量计算基础

### 1. 基本概念

**吸收剂量**：
- 定义：单位质量物质吸收的辐射能量
- 单位：戈瑞（Gy），1 Gy = 1 J/kg
- 临床应用：处方剂量、靶区剂量、危及器官剂量

**剂量分布**：
- 等剂量线：剂量相等的点连接而成的曲线
- 剂量体积直方图（DVH）：描述体积与剂量关系的图表
- 剂量梯度：剂量变化的空间速率

### 2. 影响因素

**射线特性**：
- 射线类型：光子、电子、质子
- 能量：影响穿透深度和剂量分布
- 束流强度：决定剂量率

**患者因素**：
- 组织密度：影响射线衰减
- 组织成分：不同组织的吸收特性
- 体表轮廓：影响射线入射条件

**几何因素**：
- 源皮距（SSD）：射线源到皮肤的距离
- 照射野大小：影响散射和剂量分布
- 照射角度：影响剂量分布的空间特性

## 剂量计算算法

### 1. 基于测量的算法

**百分深度剂量（PDD）法**：
```python
def calculate_pdd_dose(reference_dose, pdd_value, ssd_correction):
    """
    基于PDD的剂量计算
    
    参数:
        reference_dose: 参考点剂量 (Gy)
        pdd_value: 百分深度剂量值 (%)
        ssd_correction: SSD修正因子
    
    返回:
        计算的剂量 (Gy)
    """
    dose = reference_dose * (pdd_value / 100.0) * ssd_correction
    return dose

# 示例
reference_dose = 2.0  # Gy
pdd_at_depth = 85.0   # %
ssd_factor = 1.02
calculated_dose = calculate_pdd_dose(reference_dose, pdd_at_depth, ssd_factor)
print(f"计算剂量: {calculated_dose:.2f} Gy")
```

**组织空气比（TAR）法**：
- 适用于等中心照射
- 考虑散射和衰减
- 独立于SSD

### 2. 模型基础算法

**笔形束算法（Pencil Beam）**：
```python
import numpy as np

class PencilBeamCalculator:
    """笔形束剂量计算器"""
    
    def __init__(self, beam_energy, field_size):
        self.energy = beam_energy
        self.field_size = field_size
        self.kernel = self._load_dose_kernel()
    
    def _load_dose_kernel(self):
        """加载剂量核"""
        # 简化示例，实际应从测量数据或Monte Carlo计算获得
        return {
            'primary': np.array([1.0, 0.95, 0.90, 0.85]),
            'scatter': np.array([0.1, 0.08, 0.06, 0.04])
        }
    
    def calculate_dose(self, depth, off_axis_distance):
        """
        计算指定点的剂量
        
        参数:
            depth: 深度 (cm)
            off_axis_distance: 离轴距离 (cm)
        
        返回:
            剂量值 (相对单位)
        """
        # 主射线剂量
        primary_dose = self._calculate_primary(depth)
        
        # 散射剂量
        scatter_dose = self._calculate_scatter(depth, off_axis_distance)
        
        # 总剂量
        total_dose = primary_dose + scatter_dose
        
        return total_dose
    
    def _calculate_primary(self, depth):
        """计算主射线剂量"""
        # 简化的指数衰减模型
        mu = 0.03  # 衰减系数 (cm^-1)
        return np.exp(-mu * depth)
    
    def _calculate_scatter(self, depth, off_axis):
        """计算散射剂量"""
        # 简化的散射模型
        scatter_factor = 0.1 * np.exp(-0.02 * depth)
        lateral_falloff = np.exp(-0.05 * off_axis**2)
        return scatter_factor * lateral_falloff

# 使用示例
calculator = PencilBeamCalculator(beam_energy=6, field_size=10)
dose = calculator.calculate_dose(depth=10, off_axis_distance=5)
print(f"计算剂量: {dose:.4f}")
```

**卷积/叠加算法（Convolution/Superposition）**：
- 更准确的散射计算
- 考虑组织不均匀性
- 计算速度较快

### 3. 蒙特卡罗算法

**基本原理**：
```python
import random
import math

class MonteCarloSimulator:
    """简化的蒙特卡罗剂量计算模拟器"""
    
    def __init__(self, num_particles=10000):
        self.num_particles = num_particles
        self.dose_grid = {}
    
    def simulate_photon_transport(self, energy, start_pos):
        """
        模拟光子输运
        
        参数:
            energy: 初始能量 (MeV)
            start_pos: 起始位置 (x, y, z)
        
        返回:
            能量沉积位置列表
        """
        position = list(start_pos)
        current_energy = energy
        depositions = []
        
        while current_energy > 0.01:  # 能量阈值
            # 采样自由程
            mean_free_path = self._get_mean_free_path(current_energy)
            distance = -mean_free_path * math.log(random.random())
            
            # 更新位置
            direction = self._sample_direction()
            position[0] += distance * direction[0]
            position[1] += distance * direction[1]
            position[2] += distance * direction[2]
            
            # 采样相互作用类型
            interaction = self._sample_interaction(current_energy)
            
            if interaction == 'photoelectric':
                # 光电效应：全部能量沉积
                depositions.append((tuple(position), current_energy))
                break
            elif interaction == 'compton':
                # 康普顿散射：部分能量沉积
                energy_transfer = self._sample_compton_energy(current_energy)
                depositions.append((tuple(position), energy_transfer))
                current_energy -= energy_transfer
            elif interaction == 'pair_production':
                # 电子对产生
                depositions.append((tuple(position), current_energy - 1.022))
                break
        
        return depositions
    
    def _get_mean_free_path(self, energy):
        """获取平均自由程"""
        # 简化模型
        return 5.0 / (1.0 + 0.1 * energy)
    
    def _sample_direction(self):
        """采样新方向"""
        # 简化：各向同性
        theta = math.acos(2 * random.random() - 1)
        phi = 2 * math.pi * random.random()
        return (
            math.sin(theta) * math.cos(phi),
            math.sin(theta) * math.sin(phi),
            math.cos(theta)
        )
    
    def _sample_interaction(self, energy):
        """采样相互作用类型"""
        rand = random.random()
        if energy < 0.5:
            return 'photoelectric' if rand < 0.7 else 'compton'
        elif energy < 1.5:
            return 'compton'
        else:
            if rand < 0.6:
                return 'compton'
            else:
                return 'pair_production'
    
    def _sample_compton_energy(self, energy):
        """采样康普顿散射能量转移"""
        # 简化的Klein-Nishina公式
        return energy * random.random() * 0.5
    
    def calculate_dose_distribution(self, beam_energy, beam_position):
        """
        计算剂量分布
        
        参数:
            beam_energy: 束流能量 (MeV)
            beam_position: 束流位置
        
        返回:
            剂量网格
        """
        print(f"模拟 {self.num_particles} 个粒子...")
        
        for i in range(self.num_particles):
            depositions = self.simulate_photon_transport(
                beam_energy, 
                beam_position
            )
            
            # 累积剂量
            for pos, energy in depositions:
                grid_pos = self._position_to_grid(pos)
                if grid_pos not in self.dose_grid:
                    self.dose_grid[grid_pos] = 0.0
                self.dose_grid[grid_pos] += energy
            
            if (i + 1) % 1000 == 0:
                print(f"  进度: {i + 1}/{self.num_particles}")
        
        # 归一化
        self._normalize_dose()
        
        return self.dose_grid
    
    def _position_to_grid(self, position):
        """将位置转换为网格坐标"""
        grid_size = 1.0  # cm
        return (
            int(position[0] / grid_size),
            int(position[1] / grid_size),
            int(position[2] / grid_size)
        )
    
    def _normalize_dose(self):
        """归一化剂量"""
        if not self.dose_grid:
            return
        
        max_dose = max(self.dose_grid.values())
        for pos in self.dose_grid:
            self.dose_grid[pos] /= max_dose

# 使用示例
simulator = MonteCarloSimulator(num_particles=5000)
dose_dist = simulator.calculate_dose_distribution(
    beam_energy=6.0,
    beam_position=(0, 0, 0)
)
print(f"计算完成，网格点数: {len(dose_dist)}")
```

## 质量保证

### 1. 剂量计算验证

**基准测试**：
```python
class DoseCalculationQA:
    """剂量计算质量保证"""
    
    def __init__(self, calculator):
        self.calculator = calculator
        self.tolerance = 0.02  # 2% 容差
    
    def verify_homogeneous_phantom(self):
        """验证均匀模体中的剂量计算"""
        test_cases = [
            {'depth': 5, 'field_size': 10, 'expected': 1.00},
            {'depth': 10, 'field_size': 10, 'expected': 0.67},
            {'depth': 20, 'field_size': 10, 'expected': 0.45},
        ]
        
        results = []
        for case in test_cases:
            calculated = self.calculator.calculate_dose(
                depth=case['depth'],
                field_size=case['field_size']
            )
            
            difference = abs(calculated - case['expected']) / case['expected']
            passed = difference <= self.tolerance
            
            results.append({
                'case': case,
                'calculated': calculated,
                'difference': difference * 100,
                'passed': passed
            })
        
        return results
    
    def verify_heterogeneous_phantom(self):
        """验证非均匀模体中的剂量计算"""
        # 包含骨骼、肺等不同密度组织的模体
        pass
    
    def generate_qa_report(self):
        """生成QA报告"""
        print("=" * 60)
        print("剂量计算质量保证报告")
        print("=" * 60)
        
        # 均匀模体测试
        print("\n1. 均匀模体测试:")
        results = self.verify_homogeneous_phantom()
        
        for i, result in enumerate(results, 1):
            status = "✓ 通过" if result['passed'] else "✗ 失败"
            print(f"\n  测试 {i}: {status}")
            print(f"    深度: {result['case']['depth']} cm")
            print(f"    野大小: {result['case']['field_size']} cm")
            print(f"    期望值: {result['case']['expected']:.3f}")
            print(f"    计算值: {result['calculated']:.3f}")
            print(f"    差异: {result['difference']:.2f}%")
        
        # 统计
        passed_count = sum(1 for r in results if r['passed'])
        print(f"\n总计: {passed_count}/{len(results)} 通过")
        print("=" * 60)
```

### 2. 临床验证

**患者特定QA**：
- 独立剂量计算验证
- 测量验证（电离室、胶片、二维阵列）
- Gamma分析

## 最佳实践

### 算法选择
- 简单几何：笔形束算法
- 复杂几何：卷积/叠加算法
- 高精度要求：蒙特卡罗算法
- 考虑计算时间和精度的平衡

### 质量控制
- 定期进行基准测试
- 验证算法参数配置
- 记录和分析偏差
- 建立纠正措施流程

### 临床应用
- 理解算法的局限性
- 在不确定区域增加测量验证
- 保持算法和测量数据的一致性
- 定期更新和校准

## 合规性要求

### IEC 60601-2-1
- 剂量计算精度要求
- 质量保证程序
- 文档要求

### AAPM TG报告
- TG-65：组织不均匀性修正
- TG-105：蒙特卡罗在治疗计划中的应用
- TG-329：剂量计算算法的质量保证

## 工具与资源

### 开源工具
- TOPAS：基于Geant4的蒙特卡罗工具
- DOSXYZnrc：EGSnrc的剂量计算工具
- PRIMO：用户友好的蒙特卡罗界面

### 商业系统
- Eclipse（Varian）
- RayStation（RaySearch）
- Pinnacle（Philips）

## 总结

准确的剂量计算是放射治疗的基础。理解不同算法的原理、适用范围和局限性，建立完善的质量保证体系，对于确保治疗的安全性和有效性至关重要。

---

**相关文档**:
- [放射治疗概述](overview.md)
- [安全互锁系统](safety-interlocks.md)

**参考文献**:
- AAPM TG-65: Tissue Inhomogeneity Corrections
- IAEA TRS-430: Commissioning and Quality Assurance of TPS
- Khan's Physics of Radiation Therapy

**标签**: #放射治疗 #剂量计算 #治疗计划 #医学物理
