# IVDR法规要求

## IVDR概述

欧盟体外诊断医疗器械法规（In Vitro Diagnostic Regulation, IVDR 2017/746）于2017年发布，2022年5月26日全面实施，取代了原有的IVDD指令。

## 主要变化

### 1. 风险分类更严格

**新分类系统**

| 类别 | 风险等级 | 示例 | 合格评定 |
|------|---------|------|---------|
| **A类** | 低风险 | 样本容器、通用试剂 | 自我声明 |
| **B类** | 中低风险 | 妊娠自测、血糖仪 | 公告机构参与 |
| **C类** | 中高风险 | PSA检测、HbA1c | 公告机构参与 |
| **D类** | 高风险 | HIV筛查、血型鉴定 | 公告机构全面审查 |

**分类规则**

```python
class IVDRClassifier:
    """IVDR分类器"""
    
    def classify_device(self, device_info):
        """根据IVDR规则分类器械"""
        
        # 规则1: 用于血液、血液成分、细胞、组织或器官的筛查、诊断或分期
        if device_info.purpose in ["BLOOD_SCREENING", "TISSUE_TYPING"]:
            return "CLASS_D"
        
        # 规则2: 用于检测传染病的存在或暴露
        if device_info.detects_infectious_disease:
            if device_info.high_risk_pathogen:
                return "CLASS_D"
            else:
                return "CLASS_C"
        
        # 规则3: 用于检测遗传性疾病的存在
        if device_info.genetic_testing:
            if device_info.prenatal_screening:
                return "CLASS_C"
            else:
                return "CLASS_B"
        
        # 规则4: 用于预测、预后、监测或诊断癌症
        if device_info.cancer_related:
            return "CLASS_C"
        
        # 规则5: 伴随诊断
        if device_info.companion_diagnostic:
            return "CLASS_C"
        
        # 规则6: 自测器械
        if device_info.self_testing:
            return max("CLASS_B", self.classify_by_intended_use(device_info))
        
        # 规则7: 其他器械
        return "CLASS_A"
```

### 2. 临床证据要求

**临床性能研究**

```python
class ClinicalPerformanceStudy:
    """临床性能研究"""
    
    def design_study(self, device):
        """设计临床性能研究"""
        study_plan = {
            "objectives": self.define_objectives(device),
            "endpoints": self.define_endpoints(device),
            "sample_size": self.calculate_sample_size(device),
            "inclusion_criteria": self.define_inclusion_criteria(),
            "statistical_analysis": self.plan_statistical_analysis()
        }
        
        return study_plan
    
    def calculate_sample_size(self, device):
        """计算样本量"""
        # 基于预期灵敏度和特异性
        sensitivity = device.claimed_sensitivity
        specificity = device.claimed_specificity
        confidence_level = 0.95
        precision = 0.05
        
        # 使用二项分布计算
        n_sensitivity = self.binomial_sample_size(
            sensitivity, confidence_level, precision
        )
        n_specificity = self.binomial_sample_size(
            specificity, confidence_level, precision
        )
        
        return max(n_sensitivity, n_specificity)
    
    def analyze_results(self, study_data):
        """分析研究结果"""
        results = {
            "sensitivity": self.calculate_sensitivity(study_data),
            "specificity": self.calculate_specificity(study_data),
            "ppv": self.calculate_ppv(study_data),
            "npv": self.calculate_npv(study_data),
            "accuracy": self.calculate_accuracy(study_data),
            "confidence_intervals": self.calculate_ci(study_data)
        }
        
        return ClinicalPerformanceReport(results)
```

### 3. 质量管理体系

**ISO 13485:2016要求**

```python
class QMSCompliance:
    """质量管理体系合规性"""
    
    def __init__(self):
        self.iso13485_requirements = self.load_requirements()
    
    def verify_qms_compliance(self):
        """验证QMS合规性"""
        checks = {
            "management_responsibility": self.check_management(),
            "resource_management": self.check_resources(),
            "product_realization": self.check_realization(),
            "measurement_analysis": self.check_measurement(),
            "risk_management": self.check_risk_management(),
            "post_market_surveillance": self.check_pms()
        }
        
        return all(checks.values())
    
    def check_risk_management(self):
        """检查风险管理"""
        # ISO 14971要求
        risk_activities = [
            "risk_analysis_performed",
            "risk_evaluation_documented",
            "risk_control_implemented",
            "residual_risk_acceptable",
            "risk_management_review_conducted"
        ]
        
        return all(self.verify_activity(a) for a in risk_activities)
```

## 技术文档要求

### 1. 通用规范文档（GSPR）

```python
class GSPRDocumentation:
    """通用安全和性能要求文档"""
    
    def create_gspr_checklist(self):
        """创建GSPR检查清单"""
        requirements = {
            "Chapter I - General Requirements": [
                "达到制造商预期性能",
                "设计和制造不损害患者安全",
                "风险可接受",
                "正常使用条件下性能不受影响"
            ],
            "Chapter II - Design and Manufacturing": [
                "化学、物理和生物特性",
                "感染和微生物污染",
                "制造和环境特性",
                "具有测量功能的器械",
                "辐射防护",
                "内置软件的器械",
                "电气和电子系统",
                "机械和热风险防护"
            ],
            "Chapter III - Information": [
                "标签和使用说明",
                "用户培训要求"
            ]
        }
        
        return requirements
```

### 2. 软件文档要求

**IEC 62304合规性**

```python
class SoftwareDocumentation:
    """软件文档"""
    
    def generate_software_documentation(self, software_class):
        """生成软件文档"""
        docs = {
            "software_development_plan": self.create_sdp(),
            "software_requirements": self.document_requirements(),
            "software_architecture": self.document_architecture(),
            "software_detailed_design": self.document_design(),
            "software_unit_testing": self.document_unit_tests(),
            "software_integration_testing": self.document_integration(),
            "software_system_testing": self.document_system_tests(),
            "software_release": self.document_release()
        }
        
        if software_class in ["B", "C"]:
            docs["software_risk_management"] = self.document_risks()
        
        return docs
    
    def document_requirements(self):
        """文档化软件需求"""
        return {
            "functional_requirements": self.list_functional_req(),
            "performance_requirements": self.list_performance_req(),
            "interface_requirements": self.list_interface_req(),
            "safety_requirements": self.list_safety_req(),
            "security_requirements": self.list_security_req(),
            "traceability_matrix": self.create_traceability()
        }
```

### 3. 临床评价报告

```python
class ClinicalEvaluationReport:
    """临床评价报告"""
    
    def create_cer(self, device):
        """创建临床评价报告"""
        report = {
            "executive_summary": self.write_summary(),
            "device_description": self.describe_device(device),
            "clinical_background": self.research_clinical_context(),
            "literature_review": self.conduct_literature_review(),
            "clinical_data_analysis": self.analyze_clinical_data(),
            "performance_evaluation": self.evaluate_performance(),
            "benefit_risk_analysis": self.analyze_benefit_risk(),
            "conclusions": self.draw_conclusions()
        }
        
        return report
    
    def conduct_literature_review(self):
        """进行文献综述"""
        search_strategy = {
            "databases": ["PubMed", "Embase", "Cochrane"],
            "keywords": self.define_search_terms(),
            "inclusion_criteria": self.define_inclusion(),
            "exclusion_criteria": self.define_exclusion(),
            "quality_assessment": self.assess_study_quality()
        }
        
        return LiteratureReview(search_strategy)
```

## 上市后监督

### 1. 警戒系统

```python
class VigilanceSystem:
    """警戒系统"""
    
    def __init__(self):
        self.incident_database = IncidentDatabase()
        self.reporting_authority = "Competent Authority"
    
    def handle_incident(self, incident):
        """处理事件"""
        # 评估严重性
        severity = self.assess_severity(incident)
        
        # 确定报告时限
        if severity == "SERIOUS":
            deadline = timedelta(days=15)
        else:
            deadline = timedelta(days=30)
        
        # 创建报告
        report = self.create_incident_report(incident)
        
        # 提交给主管当局
        self.submit_to_authority(report, deadline)
        
        # 采取纠正措施
        if self.requires_fsca(incident):
            self.initiate_fsca(incident)
    
    def initiate_fsca(self, incident):
        """启动现场安全纠正措施（FSCA）"""
        fsca = {
            "type": self.determine_fsca_type(incident),
            "affected_devices": self.identify_affected_devices(),
            "customers_to_notify": self.get_customer_list(),
            "corrective_action": self.define_corrective_action(),
            "timeline": self.create_timeline()
        }
        
        return FSCA(fsca)
```

### 2. 定期安全更新报告（PSUR）

```python
class PSURGenerator:
    """PSUR生成器"""
    
    def generate_psur(self, device, period):
        """生成定期安全更新报告"""
        psur = {
            "reporting_period": period,
            "device_information": self.get_device_info(device),
            "sales_data": self.collect_sales_data(period),
            "incident_data": self.collect_incident_data(period),
            "trend_analysis": self.analyze_trends(),
            "literature_review": self.review_new_literature(),
            "risk_benefit_assessment": self.assess_risk_benefit(),
            "conclusions": self.draw_conclusions()
        }
        
        return PSUR(psur)
    
    def analyze_trends(self):
        """分析趋势"""
        incidents = self.incident_database.get_all()
        
        # 按类型分组
        by_type = self.group_by_type(incidents)
        
        # 计算发生率
        rates = self.calculate_incident_rates(by_type)
        
        # 识别趋势
        trends = self.identify_trends(rates)
        
        return TrendAnalysis(trends)
```

## 唯一器械标识（UDI）

### UDI实施

```python
class UDISystem:
    """UDI系统"""
    
    def generate_udi(self, device):
        """生成UDI"""
        # UDI-DI: 器械标识
        udi_di = self.generate_udi_di(device)
        
        # UDI-PI: 生产标识
        udi_pi = self.generate_udi_pi(device)
        
        # 完整UDI
        udi = f"{udi_di}{udi_pi}"
        
        # 生成条形码
        barcode = self.generate_barcode(udi)
        
        return UDI(udi_di, udi_pi, barcode)
    
    def register_in_eudamed(self, device, udi):
        """在EUDAMED中注册"""
        registration = {
            "basic_udi_di": udi.udi_di,
            "device_name": device.name,
            "risk_class": device.risk_class,
            "manufacturer": device.manufacturer,
            "intended_purpose": device.intended_purpose,
            "clinical_size": device.size if applicable
        }
        
        self.eudamed_api.register(registration)
```

## 合规检查清单

### 上市前检查

```python
class PreMarketChecklist:
    """上市前检查清单"""
    
    def verify_compliance(self, device):
        """验证合规性"""
        checks = {
            "分类正确": self.verify_classification(device),
            "技术文档完整": self.verify_technical_docs(device),
            "临床证据充分": self.verify_clinical_evidence(device),
            "QMS认证": self.verify_qms_certification(),
            "风险管理完成": self.verify_risk_management(device),
            "标签符合要求": self.verify_labeling(device),
            "UDI分配": self.verify_udi(device),
            "公告机构审查": self.verify_nb_review(device),
            "EUDAMED注册": self.verify_eudamed_registration(device)
        }
        
        compliance_status = all(checks.values())
        
        if not compliance_status:
            failed_checks = [k for k, v in checks.items() if not v]
            raise ComplianceError(f"以下检查未通过: {failed_checks}")
        
        return compliance_status
```

## 过渡期安排

### 时间表

| 日期 | 要求 |
|------|------|
| 2022年5月26日 | IVDR全面实施 |
| 2025年5月26日 | A类器械过渡期结束 |
| 2027年5月26日 | B类和C类器械过渡期结束 |
| 2028年5月26日 | D类器械过渡期结束 |

```python
class TransitionManager:
    """过渡期管理器"""
    
    def check_transition_status(self, device):
        """检查过渡状态"""
        current_date = datetime.now()
        
        deadlines = {
            "CLASS_A": datetime(2025, 5, 26),
            "CLASS_B": datetime(2027, 5, 26),
            "CLASS_C": datetime(2027, 5, 26),
            "CLASS_D": datetime(2028, 5, 26)
        }
        
        deadline = deadlines[device.risk_class]
        days_remaining = (deadline - current_date).days
        
        if days_remaining < 180:
            return TransitionStatus(
                urgent=True,
                days_remaining=days_remaining,
                action_required="立即启动IVDR合规项目"
            )
        
        return TransitionStatus(
            urgent=False,
            days_remaining=days_remaining,
            action_required="按计划推进合规工作"
        )
```

## 相关资源

- [IVD软件特点](overview.md)
- [临床性能评价](clinical-performance.md)
- [质量管理体系](quality-management.md)
- [上市后监督](post-market-surveillance.md)

## 参考文献

- IVDR 2017/746: 欧盟体外诊断医疗器械法规
- MDCG 2020-16: IVDR分类指南
- MDCG 2020-5: 临床证据指南
- MDCG 2019-11: 通用规范文档模板
