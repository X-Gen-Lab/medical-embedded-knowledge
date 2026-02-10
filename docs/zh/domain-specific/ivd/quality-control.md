# IVD质量控制实施

## 质量控制概述

质量控制（Quality Control, QC）是确保IVD检测结果准确性和可靠性的关键过程，通过定期使用已知浓度的质控品来监测分析系统的性能。

## Westgard规则

### 规则实现

```python
class WestgardRules:
    """Westgard多规则质控"""
    
    def __init__(self, mean, std_dev):
        self.mean = mean
        self.std_dev = std_dev
        self.control_limits = {
            "1s": (mean - std_dev, mean + std_dev),
            "2s": (mean - 2*std_dev, mean + 2*std_dev),
            "3s": (mean - 3*std_dev, mean + 3*std_dev)
        }
    
    def check_1_2s(self, value):
        """1_2s规则：单个值超过±2SD（警告规则）"""
        lower_2s, upper_2s = self.control_limits["2s"]
        return value < lower_2s or value > upper_2s
    
    def check_1_3s(self, value):
        """1_3s规则：单个值超过±3SD（拒绝规则）"""
        lower_3s, upper_3s = self.control_limits["3s"]
        return value < lower_3s or value > upper_3s
    
    def check_2_2s(self, values):
        """2_2s规则：连续2个值超过同侧±2SD"""
        if len(values) < 2:
            return False
        
        lower_2s, upper_2s = self.control_limits["2s"]
        
        # 检查最后两个值
        last_two = values[-2:]
        
        # 两个都在上侧
        if all(v > upper_2s for v in last_two):
            return True
        
        # 两个都在下侧
        if all(v < lower_2s for v in last_two):
            return True
        
        return False
    
    def check_R_4s(self, values):
        """R_4s规则：一个值超过+2SD，另一个超过-2SD（范围>4SD）"""
        if len(values) < 2:
            return False
        
        lower_2s, upper_2s = self.control_limits["2s"]
        
        # 检查最后两个值
        last_two = values[-2:]
        
        # 一个在上侧，一个在下侧
        if (last_two[0] > upper_2s and last_two[1] < lower_2s) or \
           (last_two[0] < lower_2s and last_two[1] > upper_2s):
            return True
        
        return False
    
    def check_4_1s(self, values):
        """4_1s规则：连续4个值超过同侧±1SD"""
        if len(values) < 4:
            return False
        
        lower_1s, upper_1s = self.control_limits["1s"]
        
        # 检查最后四个值
        last_four = values[-4:]
        
        # 四个都在上侧
        if all(v > upper_1s for v in last_four):
            return True
        
        # 四个都在下侧
        if all(v < lower_1s for v in last_four):
            return True
        
        return False
    
    def check_10_x(self, values):
        """10_x规则：连续10个值在均值同侧"""
        if len(values) < 10:
            return False
        
        # 检查最后10个值
        last_ten = values[-10:]
        
        # 十个都在上侧
        if all(v > self.mean for v in last_ten):
            return True
        
        # 十个都在下侧
        if all(v < self.mean for v in last_ten):
            return True
        
        return False
    
    def evaluate(self, values):
        """评估质控数据"""
        if not values:
            return QCResult(status="NO_DATA")
        
        current_value = values[-1]
        
        # 按顺序应用规则
        violations = []
        
        # 1_3s - 最严重，立即拒绝
        if self.check_1_3s(current_value):
            violations.append("1_3s")
            return QCResult(
                status="REJECT",
                violations=violations,
                action="停止检测，调查原因"
            )
        
        # 1_2s - 警告规则，需要检查其他规则
        if self.check_1_2s(current_value):
            violations.append("1_2s")
            
            # 检查其他规则
            if self.check_2_2s(values):
                violations.append("2_2s")
            
            if self.check_R_4s(values):
                violations.append("R_4s")
            
            if self.check_4_1s(values):
                violations.append("4_1s")
            
            if self.check_10_x(values):
                violations.append("10_x")
            
            # 如果触发了其他规则，拒绝
            if len(violations) > 1:
                return QCResult(
                    status="REJECT",
                    violations=violations,
                    action="停止检测，调查原因"
                )
            else:
                return QCResult(
                    status="WARNING",
                    violations=violations,
                    action="继续检测，密切监控"
                )
        
        # 没有违反任何规则
        return QCResult(
            status="ACCEPT",
            violations=[],
            action="继续正常检测"
        )
```

## 质控品管理

### 质控品追踪

```python
class QualityControlMaterialManagement:
    """质控品管理"""
    
    def __init__(self):
        self.qc_materials = {}
        self.qc_results = []
    
    def register_qc_material(self, material):
        """注册质控品"""
        qc_lot = QCLot(
            lot_number=material.lot_number,
            analyte=material.analyte,
            level=material.level,  # Level 1, 2, 3
            target_value=material.target_value,
            acceptable_range=material.acceptable_range,
            expiration_date=material.expiration_date,
            opened_date=None,
            stability_after_opening_days=material.stability_days
        )
        
        self.qc_materials[material.lot_number] = qc_lot
        
        return qc_lot
    
    def open_qc_material(self, lot_number):
        """开启质控品"""
        qc_lot = self.qc_materials[lot_number]
        qc_lot.opened_date = datetime.now()
        
        # 计算失效日期
        expiry_after_opening = qc_lot.opened_date + timedelta(
            days=qc_lot.stability_after_opening_days
        )
        
        # 使用较早的日期
        qc_lot.effective_expiration = min(
            qc_lot.expiration_date,
            expiry_after_opening
        )
        
        return qc_lot
    
    def check_qc_validity(self, lot_number):
        """检查质控品有效性"""
        qc_lot = self.qc_materials[lot_number]
        
        # 检查是否过期
        if datetime.now() > qc_lot.effective_expiration:
            raise QCMaterialExpired(f"质控品{lot_number}已过期")
        
        # 检查是否已开启
        if qc_lot.opened_date is None:
            raise QCMaterialNotOpened(f"质控品{lot_number}未开启")
        
        return True
```

## 质控图表

### Levey-Jennings图

```python
class LeveyJenningsChart:
    """Levey-Jennings质控图"""
    
    def __init__(self, analyte, level, target_mean, target_sd):
        self.analyte = analyte
        self.level = level
        self.target_mean = target_mean
        self.target_sd = target_sd
        self.data_points = []
    
    def add_data_point(self, value, timestamp):
        """添加数据点"""
        data_point = QCDataPoint(
            value=value,
            timestamp=timestamp,
            z_score=(value - self.target_mean) / self.target_sd
        )
        
        self.data_points.append(data_point)
        
        return data_point
    
    def plot_chart(self, num_points=30):
        """绘制质控图"""
        recent_points = self.data_points[-num_points:]
        
        chart = {
            "title": f"{self.analyte} - Level {self.level}",
            "x_axis": [p.timestamp for p in recent_points],
            "y_axis": [p.value for p in recent_points],
            "mean_line": self.target_mean,
            "control_limits": {
                "+3SD": self.target_mean + 3 * self.target_sd,
                "+2SD": self.target_mean + 2 * self.target_sd,
                "+1SD": self.target_mean + 1 * self.target_sd,
                "Mean": self.target_mean,
                "-1SD": self.target_mean - 1 * self.target_sd,
                "-2SD": self.target_mean - 2 * self.target_sd,
                "-3SD": self.target_mean - 3 * self.target_sd
            }
        }
        
        return chart
    
    def calculate_statistics(self, period_days=30):
        """计算统计数据"""
        cutoff_date = datetime.now() - timedelta(days=period_days)
        recent_data = [
            p.value for p in self.data_points
            if p.timestamp >= cutoff_date
        ]
        
        if not recent_data:
            return None
        
        stats = {
            "n": len(recent_data),
            "mean": np.mean(recent_data),
            "std_dev": np.std(recent_data, ddof=1),
            "cv_percent": (np.std(recent_data, ddof=1) / np.mean(recent_data)) * 100,
            "min": np.min(recent_data),
            "max": np.max(recent_data),
            "range": np.max(recent_data) - np.min(recent_data)
        }
        
        return stats
```

## 内部质控（IQC）

### 日常质控流程

```python
class InternalQualityControl:
    """内部质控"""
    
    def __init__(self):
        self.westgard_rules = {}
        self.qc_schedule = QCSchedule()
    
    def run_daily_qc(self, instrument_id, date):
        """运行日常质控"""
        qc_results = []
        
        # 获取该仪器的质控计划
        qc_tests = self.qc_schedule.get_tests_for_instrument(instrument_id, date)
        
        for test in qc_tests:
            # 运行质控测试
            result = self.run_qc_test(test)
            
            # 评估结果
            evaluation = self.evaluate_qc_result(result)
            
            qc_results.append({
                "test": test,
                "result": result,
                "evaluation": evaluation
            })
            
            # 如果质控失败，停止
            if evaluation.status == "REJECT":
                self.handle_qc_failure(test, result, evaluation)
                break
        
        # 生成质控报告
        report = self.generate_qc_report(instrument_id, date, qc_results)
        
        return report
    
    def run_qc_test(self, test):
        """运行质控测试"""
        # 获取质控品
        qc_material = self.get_qc_material(test.lot_number)
        
        # 检查有效性
        self.check_qc_validity(qc_material)
        
        # 运行测试
        measured_value = self.measure_qc_sample(
            qc_material,
            test.analyte,
            test.method
        )
        
        return QCResult(
            analyte=test.analyte,
            level=qc_material.level,
            measured_value=measured_value,
            target_value=qc_material.target_value,
            acceptable_range=qc_material.acceptable_range,
            timestamp=datetime.now()
        )
    
    def evaluate_qc_result(self, result):
        """评估质控结果"""
        # 获取该分析物的Westgard规则
        rules = self.westgard_rules.get(result.analyte)
        
        if rules is None:
            # 如果没有建立规则，使用简单的范围检查
            return self.simple_range_check(result)
        
        # 获取历史数据
        historical_data = self.get_historical_qc_data(
            result.analyte,
            result.level,
            days=30
        )
        
        # 添加当前值
        all_values = historical_data + [result.measured_value]
        
        # 应用Westgard规则
        evaluation = rules.evaluate(all_values)
        
        return evaluation
    
    def handle_qc_failure(self, test, result, evaluation):
        """处理质控失败"""
        # 1. 停止患者样本检测
        self.stop_patient_testing(test.instrument_id)
        
        # 2. 记录事件
        self.log_qc_failure(test, result, evaluation)
        
        # 3. 通知相关人员
        self.notify_supervisor(test, result, evaluation)
        
        # 4. 启动调查程序
        investigation = self.initiate_investigation(test, result, evaluation)
        
        return investigation
```

## 外部质量评估（EQA）

### 室间质评管理

```python
class ExternalQualityAssessment:
    """外部质量评估"""
    
    def __init__(self):
        self.eqa_provider = "CAP"  # College of American Pathologists
        self.eqa_results = []
    
    def process_eqa_sample(self, eqa_sample):
        """处理室间质评样本"""
        # 像患者样本一样测试
        result = self.test_sample(
            sample_id=eqa_sample.id,
            analyte=eqa_sample.analyte,
            method=eqa_sample.method
        )
        
        # 记录结果
        eqa_result = EQAResult(
            provider=self.eqa_provider,
            survey_id=eqa_sample.survey_id,
            sample_id=eqa_sample.id,
            analyte=eqa_sample.analyte,
            reported_value=result.value,
            reported_unit=result.unit,
            method=eqa_sample.method,
            instrument=result.instrument,
            test_date=datetime.now()
        )
        
        self.eqa_results.append(eqa_result)
        
        # 提交结果
        self.submit_eqa_result(eqa_result)
        
        return eqa_result
    
    def evaluate_eqa_performance(self, survey_id):
        """评估室间质评表现"""
        # 接收评估报告
        report = self.receive_eqa_report(survey_id)
        
        performance = {
            "survey_id": survey_id,
            "analytes": {}
        }
        
        for analyte_result in report.results:
            # 计算SDI (Standard Deviation Index)
            sdi = (analyte_result.lab_value - analyte_result.peer_mean) / \
                  analyte_result.peer_sd
            
            # 评估表现
            if abs(sdi) <= 2.0:
                status = "ACCEPTABLE"
            elif abs(sdi) <= 3.0:
                status = "WARNING"
            else:
                status = "UNACCEPTABLE"
            
            performance["analytes"][analyte_result.analyte] = {
                "lab_value": analyte_result.lab_value,
                "peer_mean": analyte_result.peer_mean,
                "peer_sd": analyte_result.peer_sd,
                "sdi": sdi,
                "status": status
            }
        
        # 如果有不可接受的结果，启动纠正措施
        unacceptable = [
            a for a, r in performance["analytes"].items()
            if r["status"] == "UNACCEPTABLE"
        ]
        
        if unacceptable:
            self.initiate_corrective_action(survey_id, unacceptable)
        
        return performance
```

## 相关资源

- [IVD软件特点](overview.md)
- [统计质量控制](statistical-qc.md)
- [质控故障排除](qc-troubleshooting.md)
- [质量管理体系](quality-management.md)

## 参考标准

- CLSI C24-A3: 统计质量控制
- CLSI EP23: 实验室质量控制
- ISO 15189: 医学实验室质量和能力要求
- Westgard QC: 质量控制规则和程序
