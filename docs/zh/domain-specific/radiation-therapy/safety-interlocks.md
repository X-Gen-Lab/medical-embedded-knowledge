# 放射治疗安全联锁系统

## 安全联锁概述

安全联锁系统是放射治疗设备的关键安全组件，通过硬件和软件的多层保护机制，防止意外照射和过量辐射。

## 联锁类型

### 1. 硬件联锁

```python
class HardwareInterlocks:
    """硬件联锁系统"""
    
    def __init__(self):
        self.interlocks = {
            "door_interlock": DoorInterlock(),
            "beam_stopper": BeamStopperInterlock(),
            "emergency_stop": EmergencyStopInterlock(),
            "collision_sensor": CollisionSensorInterlock(),
            "patient_monitoring": PatientMonitoringInterlock()
        }
    
    def check_all_interlocks(self):
        """检查所有联锁"""
        status = {}
        
        for name, interlock in self.interlocks.items():
            status[name] = interlock.is_safe()
        
        return all(status.values()), status
    
    def monitor_interlocks_during_treatment(self):
        """治疗期间监控联锁"""
        while self.treatment_active:
            safe, status = self.check_all_interlocks()
            
            if not safe:
                # 立即终止束流
                self.terminate_beam()
                
                # 记录事件
                self.log_interlock_event(status)
                
                # 通知操作员
                self.alert_operator(status)
                
                break
            
            time.sleep(0.01)  # 100Hz监控频率
```

### 2. 软件联锁

```python
class SoftwareInterlocks:
    """软件联锁系统"""
    
    def __init__(self):
        self.checks = [
            self.verify_patient_identity,
            self.verify_treatment_plan,
            self.verify_machine_parameters,
            self.verify_dose_limits,
            self.verify_beam_geometry,
            self.verify_imaging_alignment
        ]
    
    def pre_treatment_verification(self, patient, plan):
        """治疗前验证"""
        results = {}
        
        for check in self.checks:
            try:
                result = check(patient, plan)
                results[check.__name__] = result
            except Exception as e:
                results[check.__name__] = False
                self.log_error(f"{check.__name__} 失败: {str(e)}")
        
        if not all(results.values()):
            raise PreTreatmentVerificationError(
                f"验证失败: {[k for k, v in results.items() if not v]}"
            )
        
        return True
    
    def verify_dose_limits(self, patient, plan):
        """验证剂量限制"""
        # 检查单次剂量
        if plan.fraction_dose > self.max_fraction_dose:
            raise DoseLimitError("单次剂量超过限制")
        
        # 检查累积剂量
        delivered_dose = self.get_delivered_dose(patient)
        total_planned_dose = delivered_dose + plan.remaining_dose
        
        if total_planned_dose > plan.prescription_dose * 1.05:
            raise DoseLimitError("累积剂量超过处方剂量5%")
        
        # 检查危及器官剂量
        for oar in plan.organs_at_risk:
            oar_dose = plan.get_oar_dose(oar)
            if oar_dose > self.get_oar_limit(oar.name):
                raise DoseLimitError(f"{oar.name}剂量超过限制")
        
        return True
```

## 剂量监控

### 实时剂量监控

```python
class DoseMonitoringSystem:
    """剂量监控系统"""
    
    def __init__(self):
        self.primary_monitor = IonizationChamber("primary")
        self.secondary_monitor = IonizationChamber("secondary")
        self.dose_rate_limit = 600  # MU/min
    
    def monitor_dose_delivery(self, planned_mu):
        """监控剂量输出"""
        delivered_mu = 0
        start_time = time.time()
        
        while delivered_mu < planned_mu:
            # 读取主监测电离室
            primary_reading = self.primary_monitor.read()
            
            # 读取次监测电离室
            secondary_reading = self.secondary_monitor.read()
            
            # 交叉验证
            if not self.cross_check(primary_reading, secondary_reading):
                self.terminate_beam()
                raise MonitorDisagreementError("主次监测电离室读数不一致")
            
            # 更新已输出MU
            delivered_mu = primary_reading
            
            # 检查剂量率
            elapsed_time = time.time() - start_time
            current_dose_rate = delivered_mu / (elapsed_time / 60)
            
            if current_dose_rate > self.dose_rate_limit:
                self.terminate_beam()
                raise DoseRateError("剂量率超过限制")
            
            # 检查是否超过计划剂量
            if delivered_mu > planned_mu * 1.02:
                self.terminate_beam()
                raise OverdoseError("输出剂量超过计划剂量2%")
            
            time.sleep(0.01)
        
        return delivered_mu
    
    def cross_check(self, primary, secondary, tolerance=0.03):
        """交叉检查主次监测电离室"""
        if abs(primary - secondary) / primary > tolerance:
            return False
        return True
```

## 碰撞检测

### 几何碰撞检测

```python
class CollisionDetection:
    """碰撞检测系统"""
    
    def __init__(self):
        self.gantry_model = GantryGeometryModel()
        self.patient_model = PatientGeometryModel()
        self.couch_model = CouchGeometryModel()
        self.safety_margin_mm = 50
    
    def check_collision_risk(self, gantry_angle, couch_angle, couch_position):
        """检查碰撞风险"""
        # 更新几何模型
        self.gantry_model.set_angle(gantry_angle)
        self.couch_model.set_angle(couch_angle)
        self.couch_model.set_position(couch_position)
        
        # 检查机架与患者
        gantry_patient_distance = self.calculate_min_distance(
            self.gantry_model, self.patient_model
        )
        
        if gantry_patient_distance < self.safety_margin_mm:
            return CollisionRisk.HIGH, "机架接近患者"
        
        # 检查机架与治疗床
        gantry_couch_distance = self.calculate_min_distance(
            self.gantry_model, self.couch_model
        )
        
        if gantry_couch_distance < self.safety_margin_mm:
            return CollisionRisk.HIGH, "机架接近治疗床"
        
        # 检查治疗床与墙壁
        couch_wall_distance = self.calculate_distance_to_walls(
            self.couch_model
        )
        
        if couch_wall_distance < self.safety_margin_mm:
            return CollisionRisk.MEDIUM, "治疗床接近墙壁"
        
        return CollisionRisk.NONE, "无碰撞风险"
    
    def predict_collision_along_path(self, start_state, end_state):
        """预测运动路径上的碰撞"""
        # 插值生成路径
        path = self.interpolate_path(start_state, end_state, num_steps=100)
        
        for step in path:
            risk, message = self.check_collision_risk(
                step.gantry_angle,
                step.couch_angle,
                step.couch_position
            )
            
            if risk != CollisionRisk.NONE:
                return True, step, message
        
        return False, None, "路径安全"
```

## 紧急停止

### 紧急停止系统

```python
class EmergencyStopSystem:
    """紧急停止系统"""
    
    def __init__(self):
        self.estop_buttons = [
            EmergencyButton("console"),
            EmergencyButton("treatment_room_1"),
            EmergencyButton("treatment_room_2"),
            EmergencyButton("pendant")
        ]
        self.response_time_ms = 100  # 最大响应时间
    
    def monitor_emergency_buttons(self):
        """监控紧急停止按钮"""
        while True:
            for button in self.estop_buttons:
                if button.is_pressed():
                    timestamp = time.time()
                    
                    # 立即终止所有运动和束流
                    self.emergency_shutdown()
                    
                    # 记录事件
                    self.log_emergency_stop(button.location, timestamp)
                    
                    # 等待复位
                    self.wait_for_reset()
                    
                    break
            
            time.sleep(0.001)  # 1kHz轮询
    
    def emergency_shutdown(self):
        """紧急关闭"""
        # 1. 终止束流（最高优先级）
        self.terminate_beam_immediately()
        
        # 2. 停止所有运动
        self.stop_all_motion()
        
        # 3. 关闭调制器
        self.disable_modulator()
        
        # 4. 激活束流阻挡器
        self.activate_beam_stopper()
        
        # 5. 设置系统状态
        self.set_system_state(SystemState.EMERGENCY_STOP)
        
        # 6. 通知所有子系统
        self.broadcast_emergency_stop()
```

## 患者安全监控

### 生命体征监控

```python
class PatientSafetyMonitoring:
    """患者安全监控"""
    
    def __init__(self):
        self.video_monitor = VideoMonitoringSystem()
        self.audio_monitor = AudioMonitoringSystem()
        self.motion_detector = MotionDetectionSystem()
    
    def monitor_patient_during_treatment(self):
        """治疗期间监控患者"""
        while self.treatment_active:
            # 视频监控
            video_frame = self.video_monitor.get_frame()
            if self.detect_patient_distress(video_frame):
                self.pause_treatment("检测到患者异常")
            
            # 音频监控
            audio_signal = self.audio_monitor.get_signal()
            if self.detect_patient_call(audio_signal):
                self.pause_treatment("患者呼叫")
            
            # 运动检测
            motion_level = self.motion_detector.measure_motion()
            if motion_level > self.motion_threshold:
                self.pause_treatment("患者运动超过阈值")
            
            time.sleep(0.1)  # 10Hz监控
    
    def detect_patient_distress(self, video_frame):
        """检测患者异常"""
        # 使用计算机视觉检测异常姿势或运动
        pose = self.estimate_pose(video_frame)
        
        if self.is_abnormal_pose(pose):
            return True
        
        return False
```

## 相关资源

- [放射治疗系统概述](overview.md)
- [剂量计算算法](dose-calculation.md)
- [质量保证程序](quality-assurance.md)
- [事故预防](accident-prevention.md)

## 参考标准

- IEC 60601-2-1: 医用电子加速器安全标准
- IEC 62083: 放射治疗计划系统安全要求
- IAEA Safety Report Series No. 17: 放射治疗事故教训
