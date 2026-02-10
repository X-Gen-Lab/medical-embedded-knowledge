---
title: "放射治疗设备软件概述"
description: "放射治疗系统架构、治疗计划系统（TPS）、剂量计算算法（PBC和蒙特卡洛）和治疗执行流程"
difficulty: "高级"
estimated_time: "85分钟"
tags:
  - 放射治疗
  - TPS
  - 剂量计算
  - IMRT
  - 蒙特卡洛
  - 笔形束卷积
  - 治疗计划
related_modules:
  - "zh/domain-specific/radiation-therapy/dose-calculation"

  - "zh/domain-specific/radiation-therapy/safety-interlocks"
last_updated: "2026-02-11"
version: "1.0"
language: "zh-CN"
---

# 放射治疗设备软件概述

## 什么是放射治疗？

放射治疗（Radiation Therapy）是利用高能射线（如X射线、伽马射线、电子束、质子束等）精确照射肿瘤组织，破坏癌细胞DNA，达到治疗目的的医疗技术。

## 放射治疗系统组成

### 系统架构

```python
class RadiationTherapySystem:
    """放射治疗系统"""
    
    def __init__(self):
        self.components = {
            "treatment_planning": TreatmentPlanningSystem(),
            "dose_calculation": DoseCalculationEngine(),
            "beam_delivery": BeamDeliverySystem(),
            "imaging": ImagingSystem(),
            "patient_positioning": PositioningSystem(),
            "safety_interlocks": SafetyInterlockSystem(),
            "record_verify": RecordAndVerifySystem()
        }
    
    def execute_treatment(self, patient, treatment_plan):
        """执行治疗"""
        # 1. 验证治疗计划
        if not self.components["record_verify"].verify_plan(treatment_plan):
            raise TreatmentError("治疗计划验证失败")
        
        # 2. 患者定位
        positioning_result = self.components["patient_positioning"].position_patient(
            patient, treatment_plan.setup_parameters
        )
        
        # 3. 影像引导验证
        imaging_result = self.components["imaging"].acquire_verification_image()
        if not self.verify_patient_position(imaging_result, treatment_plan):
            return self.request_repositioning()
        
        # 4. 安全检查
        if not self.components["safety_interlocks"].check_all():
            raise SafetyError("安全联锁检查失败")
        
        # 5. 执行照射
        delivery_result = self.components["beam_delivery"].deliver_treatment(
            treatment_plan
        )
        
        # 6. 记录治疗数据
        self.record_treatment(patient, treatment_plan, delivery_result)
        
        return delivery_result
```

## 治疗计划系统（TPS）

### 核心功能

**1. 图像处理与融合**

```python
class ImageProcessing:
    """图像处理模块"""
    
    def import_dicom_images(self, dicom_files):
        """导入DICOM图像"""
        image_series = []
        
        for file in dicom_files:
            ds = pydicom.dcmread(file)
            
            # 提取图像信息
            image = {
                "patient_id": ds.PatientID,
                "study_uid": ds.StudyInstanceUID,
                "series_uid": ds.SeriesInstanceUID,
                "modality": ds.Modality,  # CT, MR, PET等
                "slice_thickness": ds.SliceThickness,
                "pixel_spacing": ds.PixelSpacing,
                "image_position": ds.ImagePositionPatient,
                "image_orientation": ds.ImageOrientationPatient,
                "pixel_data": ds.pixel_array
            }
            
            image_series.append(image)
        
        # 排序切片
        sorted_series = self.sort_slices(image_series)
        
        # 构建3D体积
        volume = self.construct_3d_volume(sorted_series)
        
        return volume
    
    def register_images(self, fixed_image, moving_image, method="rigid"):
        """图像配准"""
        if method == "rigid":
            # 刚性配准（平移+旋转）
            transform = self.rigid_registration(fixed_image, moving_image)
        elif method == "deformable":
            # 可变形配准
            transform = self.deformable_registration(fixed_image, moving_image)
        else:
            raise ValueError(f"不支持的配准方法: {method}")
        
        # 应用变换
        registered_image = self.apply_transform(moving_image, transform)
        
        # 计算配准质量指标
        quality_metrics = {
            "mutual_information": self.calculate_mi(fixed_image, registered_image),
            "normalized_cross_correlation": self.calculate_ncc(fixed_image, registered_image),
            "mean_squared_error": self.calculate_mse(fixed_image, registered_image)
        }
        
        return registered_image, transform, quality_metrics
    
    def fuse_multimodality_images(self, ct_image, pet_image, mri_image=None):
        """多模态图像融合"""
        # CT作为参考图像（提供电子密度信息）
        reference = ct_image
        
        # 配准PET到CT
        pet_registered, _ = self.register_images(reference, pet_image)
        
        # 如果有MRI，也配准到CT
        if mri_image:
            mri_registered, _ = self.register_images(reference, mri_image)
        
        # 创建融合图像
        fused = FusedImage(
            ct=reference,
            pet=pet_registered,
            mri=mri_registered if mri_image else None
        )
        
        return fused
```

**2. 靶区和危及器官勾画**

```python
class ContoringModule:
    """勾画模块"""
    
    def __init__(self):
        self.structure_types = {
            "GTV": "肿瘤大体积（Gross Tumor Volume）",
            "CTV": "临床靶区（Clinical Target Volume）",
            "PTV": "计划靶区（Planning Target Volume）",
            "OAR": "危及器官（Organ At Risk）",
            "PRV": "计划危及器官体积（Planning organ at Risk Volume）"
        }
    
    def create_structure(self, name, structure_type, color):
        """创建结构"""
        structure = Structure(
            name=name,
            type=structure_type,
            color=color,
            contours=[],
            volume=0.0,
            center_of_mass=None
        )
        
        return structure
    
    def add_contour(self, structure, slice_index, points):
        """添加轮廓"""
        contour = Contour(
            slice_index=slice_index,
            points=points,  # [(x1, y1), (x2, y2), ...]
            area=self.calculate_contour_area(points)
        )
        
        structure.contours.append(contour)
        
        # 更新体积
        structure.volume = self.calculate_structure_volume(structure)
        
        # 更新质心
        structure.center_of_mass = self.calculate_center_of_mass(structure)
    
    def auto_segment(self, image, organ_name, method="atlas"):
        """自动分割"""
        if method == "atlas":
            # 基于图谱的分割
            contours = self.atlas_based_segmentation(image, organ_name)
        elif method == "deep_learning":
            # 深度学习分割
            contours = self.dl_segmentation(image, organ_name)
        else:
            raise ValueError(f"不支持的分割方法: {method}")
        
        return contours
    
    def expand_structure(self, structure, margin_mm):
        """扩展结构（如GTV→CTV→PTV）"""
        expanded_contours = []
        
        for contour in structure.contours:
            # 对每个轮廓进行扩展
            expanded_points = self.expand_contour(contour.points, margin_mm)
            expanded_contours.append(Contour(
                slice_index=contour.slice_index,
                points=expanded_points,
                area=self.calculate_contour_area(expanded_points)
            ))
        
        expanded_structure = Structure(
            name=f"{structure.name}_expanded_{margin_mm}mm",
            type=structure.type,
            color=structure.color,
            contours=expanded_contours
        )
        
        expanded_structure.volume = self.calculate_structure_volume(expanded_structure)
        
        return expanded_structure
```

**3. 治疗计划优化**

```python
class TreatmentPlanOptimizer:
    """治疗计划优化器"""
    
    def __init__(self):
        self.optimization_algorithm = "IMRT"  # IMRT, VMAT, SBRT等
    
    def create_optimization_objectives(self, structures, prescription):
        """创建优化目标"""
        objectives = []
        
        # 靶区目标
        for target in structures.get_targets():
            # 处方剂量目标
            objectives.append(DoseObjective(
                structure=target,
                type="MIN_DOSE",
                dose=prescription.dose * 0.95,  # 95%处方剂量
                volume=98,  # 98%体积
                priority=100,
                weight=1.0
            ))
            
            objectives.append(DoseObjective(
                structure=target,
                type="MAX_DOSE",
                dose=prescription.dose * 1.07,  # 107%处方剂量
                volume=2,  # 2%体积
                priority=90,
                weight=0.8
            ))
            
            # 均匀性目标
            objectives.append(UniformityObjective(
                structure=target,
                priority=80,
                weight=0.5
            ))
        
        # 危及器官目标
        for oar in structures.get_oars():
            constraints = self.get_oar_constraints(oar.name)
            
            for constraint in constraints:
                objectives.append(DoseObjective(
                    structure=oar,
                    type="MAX_DOSE",
                    dose=constraint.dose,
                    volume=constraint.volume,
                    priority=constraint.priority,
                    weight=constraint.weight
                ))
        
        return objectives
    
    def optimize_plan(self, plan, objectives, max_iterations=100):
        """优化计划"""
        iteration = 0
        converged = False
        
        while iteration < max_iterations and not converged:
            # 计算当前剂量分布
            dose_distribution = self.calculate_dose(plan)
            
            # 评估目标函数
            objective_value = self.evaluate_objectives(
                dose_distribution, objectives
            )
            
            # 计算梯度
            gradients = self.calculate_gradients(
                dose_distribution, objectives
            )
            
            # 更新射野权重/MLC形状
            plan = self.update_plan_parameters(plan, gradients)
            
            # 检查收敛
            if self.check_convergence(objective_value):
                converged = True
            
            iteration += 1
        
        return plan, dose_distribution
    
    def evaluate_objectives(self, dose_distribution, objectives):
        """评估目标函数"""
        total_cost = 0.0
        
        for obj in objectives:
            structure_dose = dose_distribution.get_structure_dose(obj.structure)
            
            if obj.type == "MIN_DOSE":
                # 最小剂量目标
                underdose = max(0, obj.dose - structure_dose.get_percentile(obj.volume))
                cost = obj.weight * (underdose ** 2)
            elif obj.type == "MAX_DOSE":
                # 最大剂量目标
                overdose = max(0, structure_dose.get_percentile(100 - obj.volume) - obj.dose)
                cost = obj.weight * (overdose ** 2)
            elif obj.type == "MEAN_DOSE":
                # 平均剂量目标
                deviation = abs(structure_dose.mean - obj.dose)
                cost = obj.weight * (deviation ** 2)
            
            total_cost += cost * obj.priority
        
        return total_cost
```

## 剂量计算算法

### 1. 笔形束卷积算法（PBC）

```python
class PencilBeamConvolution:
    """笔形束卷积算法"""
    
    def __init__(self):
        self.kernel_data = self.load_kernel_data()
    
    def calculate_dose(self, ct_image, beam_geometry, monitor_units):
        """计算剂量分布"""
        # 1. 射线追踪
        ray_paths = self.trace_rays(ct_image, beam_geometry)
        
        # 2. 计算每条射线的能量沉积
        dose_distribution = np.zeros(ct_image.shape)
        
        for ray in ray_paths:
            # 计算射线路径上的辐射长度
            radiological_depth = self.calculate_radiological_depth(
                ct_image, ray.path
            )
            
            # 应用深度剂量曲线
            depth_dose = self.apply_depth_dose_curve(
                radiological_depth, beam_geometry.energy
            )
            
            # 应用离轴比
            off_axis_ratio = self.apply_off_axis_ratio(
                ray.position, beam_geometry.central_axis
            )
            
            # 卷积核计算侧向散射
            scattered_dose = self.convolve_kernel(
                ray.position, depth_dose, self.kernel_data
            )
            
            # 累加剂量
            dose_distribution += scattered_dose * off_axis_ratio
        
        # 3. 归一化到监测单位
        dose_distribution *= monitor_units * self.calibration_factor
        
        return dose_distribution
    
    def calculate_radiological_depth(self, ct_image, ray_path):
        """计算辐射学深度"""
        depth = 0.0
        
        for point in ray_path:
            # 获取CT值
            ct_value = ct_image.get_value(point)
            
            # 转换为电子密度
            electron_density = self.ct_to_density(ct_value)
            
            # 累加辐射学深度
            depth += electron_density * self.step_size
        
        return depth
    
    def ct_to_density(self, ct_value):
        """CT值转电子密度"""
        # 使用双线性转换
        if ct_value < 0:
            # 水以下（空气、肺）
            density = 0.001 + (ct_value + 1000) * (1.0 - 0.001) / 1000
        else:
            # 水以上（软组织、骨骼）
            density = 1.0 + ct_value * (1.8 - 1.0) / 1000
        
        return density
```

### 2. 蒙特卡洛算法

```python
class MonteCarloSimulation:
    """蒙特卡洛剂量计算"""
    
    def __init__(self, num_histories=1e8):
        self.num_histories = int(num_histories)
        self.variance_reduction = True
    
    def simulate_dose(self, ct_image, beam_geometry, monitor_units):
        """模拟剂量分布"""
        # 初始化剂量矩阵
        dose_matrix = np.zeros(ct_image.shape)
        dose_squared = np.zeros(ct_image.shape)
        
        # 模拟粒子历史
        for i in range(self.num_histories):
            # 生成初始粒子
            particle = self.generate_particle(beam_geometry)
            
            # 追踪粒子
            while particle.is_active:
                # 采样自由程
                step_length = self.sample_free_path(particle, ct_image)
                
                # 移动粒子
                particle.move(step_length)
                
                # 检查是否出界
                if not ct_image.contains(particle.position):
                    break
                
                # 采样相互作用类型
                interaction = self.sample_interaction(particle, ct_image)
                
                if interaction == "PHOTOELECTRIC":
                    # 光电效应 - 粒子被吸收
                    self.deposit_energy(
                        dose_matrix, particle.position, particle.energy
                    )
                    particle.is_active = False
                    
                elif interaction == "COMPTON":
                    # 康普顿散射
                    scattered_energy, scatter_angle = self.compton_scatter(
                        particle.energy
                    )
                    
                    # 沉积能量
                    deposited_energy = particle.energy - scattered_energy
                    self.deposit_energy(
                        dose_matrix, particle.position, deposited_energy
                    )
                    
                    # 更新粒子
                    particle.energy = scattered_energy
                    particle.direction = self.rotate_direction(
                        particle.direction, scatter_angle
                    )
                    
                elif interaction == "PAIR_PRODUCTION":
                    # 电子对产生
                    self.create_electron_positron_pair(particle)
        
        # 计算统计不确定度
        uncertainty = np.sqrt(
            (dose_squared / self.num_histories - (dose_matrix / self.num_histories) ** 2)
            / self.num_histories
        )
        
        # 归一化
        dose_matrix *= monitor_units * self.calibration_factor / self.num_histories
        
        return dose_matrix, uncertainty
```

## 相关资源


- [剂量计算](dose-calculation.md)
- [安全联锁](safety-interlocks.md)- [剂量计算算法详解](dose-calculation.md)
- [安全联锁系统](safety-interlocks.md)

## 参考标准

- IEC 60601-2-1: 医用电子加速器安全标准
- IEC 62083: 放射治疗计划系统要求
- AAPM TG-53: 质量保证指南
- ICRU 83: 处方、记录和报告光子束IMRT
