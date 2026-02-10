---
title: "实验室信息系统（LIS）集成"
description: "LIS系统架构、HL7/ASTM/FHIR接口标准、样本追踪和双向通信实现"
difficulty: "中级"
estimated_time: "70分钟"
tags:
  - LIS
  - HL7
  - ASTM
  - FHIR
  - 接口集成
  - 样本追踪
  - 互操作性
related_modules:
  - "zh/domain-specific/ivd/overview"

last_updated: "2026-02-11"
version: "1.0"
language: "zh-CN"
---

# 实验室信息系统（LIS）集成

## LIS系统概述

实验室信息系统（Laboratory Information System, LIS）是用于管理医学实验室工作流程、样本追踪、结果报告和质量控制的综合信息系统。

## 系统架构

### 典型LIS架构

```python
class LISArchitecture:
    """LIS系统架构"""
    
    def __init__(self):
        self.components = {
            "order_management": OrderManagementModule(),
            "sample_tracking": SampleTrackingModule(),
            "instrument_interface": InstrumentInterfaceModule(),
            "result_management": ResultManagementModule(),
            "quality_control": QualityControlModule(),
            "reporting": ReportingModule(),
            "billing": BillingModule(),
            "inventory": InventoryModule()
        }
    
    def process_workflow(self, order):
        """处理工作流程"""
        # 1. 接收医嘱
        order_id = self.components["order_management"].receive_order(order)
        
        # 2. 样本采集和追踪
        sample = self.components["sample_tracking"].register_sample(order_id)
        
        # 3. 分配到仪器
        instrument = self.components["instrument_interface"].assign_instrument(sample)
        
        # 4. 接收结果
        result = self.components["result_management"].receive_result(sample)
        
        # 5. 质控验证
        if self.components["quality_control"].validate(result):
            # 6. 生成报告
            report = self.components["reporting"].generate_report(result)
            return report
        else:
            return self.handle_qc_failure(result)
```

## 接口标准

### 1. HL7接口

**HL7 v2.x消息**

```python
class HL7Interface:
    """HL7接口实现"""
    
    def __init__(self):
        self.message_types = {
            "ORM": "医嘱消息",
            "ORU": "观察结果",
            "QRY": "查询消息",
            "ACK": "确认消息"
        }
    
    def parse_orm_message(self, hl7_message):
        """解析医嘱消息（ORM^O01）"""
        message = hl7.parse(hl7_message)
        
        # 提取患者信息（PID段）
        patient_info = {
            "patient_id": message.segment("PID")[3][0],
            "patient_name": message.segment("PID")[5][0],
            "date_of_birth": message.segment("PID")[7][0],
            "gender": message.segment("PID")[8][0]
        }
        
        # 提取医嘱信息（ORC段）
        order_info = {
            "order_control": message.segment("ORC")[1][0],
            "placer_order_number": message.segment("ORC")[2][0],
            "order_status": message.segment("ORC")[5][0]
        }
        
        # 提取检验项目（OBR段）
        test_info = {
            "set_id": message.segment("OBR")[1][0],
            "placer_order_number": message.segment("OBR")[2][0],
            "universal_service_id": message.segment("OBR")[4][0],
            "observation_datetime": message.segment("OBR")[7][0],
            "specimen_source": message.segment("OBR")[15][0]
        }
        
        return LabOrder(patient_info, order_info, test_info)
    
    def create_oru_message(self, test_result):
        """创建观察结果消息（ORU^R01）"""
        message = hl7.Message("ORU", "R01")
        
        # MSH - 消息头
        message.add_segment("MSH", [
            "|", "^~\\&",
            "LIS_SYSTEM", "LABORATORY",
            "HIS_SYSTEM", "HOSPITAL",
            datetime.now().strftime("%Y%m%d%H%M%S"),
            "",
            "ORU^R01^ORU_R01",
            self.generate_message_control_id(),
            "P",  # 生产环境
            "2.5.1",
            "",
            "",
            "",
            "UNICODE UTF-8"
        ])
        
        # PID - 患者识别
        message.add_segment("PID", [
            "1",  # Set ID
            "",   # 患者ID（外部）
            test_result.patient_id,  # 患者ID（内部）
            "",   # 备用患者ID
            test_result.patient_name,  # 患者姓名
            "",   # 母亲姓名
            test_result.date_of_birth,  # 出生日期
            test_result.gender,  # 性别
            "",   # 患者别名
            "",   # 种族
            test_result.address,  # 地址
            "",   # 县代码
            test_result.phone,  # 电话
            "",   # 工作电话
            "",   # 主要语言
            "",   # 婚姻状况
            "",   # 宗教
            "",   # 患者账号
            "",   # SSN
            "",   # 驾照号
        ])
        
        # PV1 - 患者就诊
        message.add_segment("PV1", [
            "1",  # Set ID
            test_result.patient_class,  # 患者类别（I=住院，O=门诊）
            test_result.assigned_location,  # 分配位置
            "",   # 入院类型
            "",   # 预约ID
            "",   # 先前位置
            test_result.attending_doctor,  # 主治医生
            "",   # 转诊医生
            "",   # 会诊医生
            "",   # 医院服务
            "",   # 临时位置
            "",   # 预约类型
            "",   # 入院ID
            "",   # 入院来源
            "",   # 救护车状态
            "",   # VIP指示器
            "",   # 主治医生
            "",   # 患者类型
            test_result.visit_number,  # 就诊号
            "",   # 财务类别
            "",   # 收费价格指示器
            "",   # 礼貌代码
            "",   # 信用评级
            "",   # 合同代码
            "",   # 合同生效日期
            "",   # 合同金额
            "",   # 合同期限
            "",   # 利息代码
            "",   # 转账到坏账代码
            "",   # 转账到坏账日期
            "",   # 坏账机构代码
            "",   # 坏账恢复金额
            "",   # 删除账户指示器
            "",   # 删除账户日期
            "",   # 出院处置
            "",   # 出院到位置
            "",   # 饮食类型
            "",   # 服务机构
            "",   # 床位状态
            "",   # 账户状态
            "",   # 待定位置
            "",   # 先前临时位置
            test_result.admission_datetime,  # 入院日期时间
            "",   # 出院日期时间
        ])
        
        # ORC - 通用医嘱段
        message.add_segment("ORC", [
            "RE",  # 医嘱控制（RE=观察结果报告）
            test_result.placer_order_number,  # 申请方医嘱号
            test_result.filler_order_number,  # 执行方医嘱号
            "",   # 申请方组号
            "",   # 医嘱状态
            "",   # 响应标志
            "",   # 数量/时间
            "",   # 父医嘱
            test_result.transaction_datetime,  # 事务日期时间
            "",   # 录入者
            "",   # 验证者
            test_result.ordering_provider,  # 医嘱提供者
            "",   # 录入者位置
            "",   # 回调电话号码
            test_result.order_effective_datetime,  # 医嘱生效日期时间
            "",   # 医嘱控制代码原因
        ])
        
        # OBR - 观察请求段
        message.add_segment("OBR", [
            "1",  # Set ID
            test_result.placer_order_number,  # 申请方医嘱号
            test_result.filler_order_number,  # 执行方医嘱号
            test_result.universal_service_id,  # 通用服务ID
            "",   # 优先级
            "",   # 请求日期时间
            test_result.observation_datetime,  # 观察日期时间
            test_result.observation_end_datetime,  # 观察结束日期时间
            "",   # 采集量
            "",   # 采集者ID
            "",   # 标本操作代码
            "",   # 危险代码
            "",   # 相关临床信息
            "",   # 标本接收日期时间
            test_result.specimen_source,  # 标本来源
            test_result.ordering_provider,  # 医嘱提供者
            "",   # 医嘱回调电话号码
            "",   # 申请方字段1
            "",   # 申请方字段2
            "",   # 执行方字段1
            "",   # 执行方字段2
            test_result.results_rpt_status_chng_datetime,  # 结果报告状态改变日期时间
            "",   # 收费到实践
            "",   # 诊断服务段ID
            test_result.result_status,  # 结果状态（F=最终，P=初步）
            "",   # 父结果
            "",   # 数量/时间
            "",   # 结果副本
            "",   # 父号
            "",   # 运输方式
            "",   # 结果原因
            "",   # 主结果解释者
            "",   # 助理结果解释者
            "",   # 技术员
            "",   # 转录员
            "",   # 计划日期时间
        ])
        
        # OBX - 观察结果段（可以有多个）
        for idx, observation in enumerate(test_result.observations, 1):
            message.add_segment("OBX", [
                str(idx),  # Set ID
                observation.value_type,  # 值类型（NM=数值，ST=字符串，CE=编码条目）
                observation.observation_id,  # 观察标识符
                observation.observation_sub_id,  # 观察子ID
                observation.observation_value,  # 观察值
                observation.units,  # 单位
                observation.reference_range,  # 参考范围
                observation.abnormal_flags,  # 异常标志（N=正常，H=高，L=低，HH=危急高，LL=危急低）
                "",   # 概率
                "",   # 异常测试性质
                observation.observation_result_status,  # 观察结果状态（F=最终）
                "",   # 生效日期
                "",   # 用户定义访问检查
                observation.datetime_of_observation,  # 观察日期时间
                "",   # 生产者ID
                "",   # 负责观察者
                "",   # 观察方法
            ])
        
        # NTE - 注释和评论段（可选）
        if test_result.comments:
            for idx, comment in enumerate(test_result.comments, 1):
                message.add_segment("NTE", [
                    str(idx),  # Set ID
                    "L",  # 注释来源（L=实验室）
                    comment,  # 注释
                ])
        
        return message.to_string()
    
    def send_acknowledgment(self, original_message, status="AA"):
        """发送确认消息（ACK）"""
        ack = hl7.Message("ACK")
        
        # MSH段
        ack.add_segment("MSH", [
            "|", "^~\\&",
            "LIS_SYSTEM", "LABORATORY",
            original_message.sending_application,
            original_message.sending_facility,
            datetime.now().strftime("%Y%m%d%H%M%S"),
            "",
            "ACK",
            self.generate_message_control_id(),
            "P",
            "2.5.1"
        ])
        
        # MSA段 - 消息确认
        ack.add_segment("MSA", [
            status,  # 确认代码（AA=应用接受，AE=应用错误，AR=应用拒绝）
            original_message.message_control_id,  # 消息控制ID
            "Message received successfully" if status == "AA" else "Error processing message"
        ])
        
        return ack.to_string()
```

### 2. ASTM接口

**ASTM E1394标准**

```python
class ASTMInterface:
    """ASTM接口实现"""
    
    def __init__(self):
        self.STX = '\x02'  # 开始字符
        self.ETX = '\x03'  # 结束字符
        self.EOT = '\x04'  # 传输结束
        self.ENQ = '\x05'  # 查询
        self.ACK = '\x06'  # 确认
        self.NAK = '\x15'  # 否定确认
        self.LF = '\x0A'   # 换行
        self.CR = '\x0D'   # 回车
    
    def create_result_message(self, test_result):
        """创建结果消息"""
        frames = []
        
        # Header记录
        header = self.create_header_record()
        frames.append(header)
        
        # Patient记录
        patient = self.create_patient_record(test_result.patient)
        frames.append(patient)
        
        # Order记录
        order = self.create_order_record(test_result.order)
        frames.append(order)
        
        # Result记录
        for result in test_result.results:
            result_record = self.create_result_record(result)
            frames.append(result_record)
        
        # Terminator记录
        terminator = self.create_terminator_record()
        frames.append(terminator)
        
        return self.build_message(frames)
    
    def create_header_record(self):
        """创建Header记录（H记录）"""
        fields = [
            "H",  # 记录类型
            "\\^&",  # 分隔符定义
            "",  # 消息控制ID
            "",  # 访问密码
            "LIS_SYSTEM",  # 发送者名称或ID
            "",  # 发送者街道地址
            "",  # 保留字段
            "",  # 发送者电话号码
            "",  # 发送者特征
            "",  # 接收者ID
            "",  # 注释或特殊说明
            "",  # 处理ID
            "ASTM-E1394",  # 版本号
            datetime.now().strftime("%Y%m%d%H%M%S")  # 时间戳
        ]
        return "|".join(fields)
    
    def create_patient_record(self, patient):
        """创建Patient记录（P记录）"""
        fields = [
            "P",  # 记录类型
            "1",  # 序列号
            patient.patient_id,  # 患者ID
            "",  # 实验室分配的患者ID
            "",  # 患者ID号3
            patient.patient_name,  # 患者姓名
            "",  # 母亲姓名
            patient.date_of_birth,  # 出生日期
            patient.gender,  # 性别
            "",  # 患者种族
            patient.address,  # 患者地址
            "",  # 保留字段
            patient.phone,  # 患者电话号码
            patient.attending_physician,  # 主治医生
            "",  # 特殊字段1
            "",  # 特殊字段2
            "",  # 患者身高
            "",  # 患者体重
            "",  # 患者诊断
            "",  # 患者活动药物
            "",  # 患者饮食
            "",  # 实践字段1
            "",  # 实践字段2
            "",  # 入院和出院日期
            "",  # 入院状态
            "",  # 位置
            "",  # 备用诊断代码和分类
            "",  # 患者宗教
            "",  # 婚姻状况
            "",  # 隔离状态
            "",  # 语言
            "",  # 医院服务
            "",  # 医院机构
            "",  # 剂量类别
        ]
        return "|".join(fields)
    
    def create_order_record(self, order):
        """创建Order记录（O记录）"""
        fields = [
            "O",  # 记录类型
            "1",  # 序列号
            order.specimen_id,  # 标本ID
            "",  # 仪器标本ID
            order.universal_test_id,  # 通用测试ID
            order.priority,  # 优先级
            order.requested_datetime,  # 请求日期时间
            order.collection_datetime,  # 采集日期时间
            "",  # 采集结束时间
            "",  # 采集量
            "",  # 采集者ID
            "",  # 操作代码
            "",  # 危险代码
            "",  # 相关临床信息
            order.received_datetime,  # 标本接收日期时间
            order.specimen_descriptor,  # 标本描述符
            order.ordering_physician,  # 医嘱医生
            "",  # 医生电话号码
            "",  # 用户字段1
            "",  # 用户字段2
            "",  # 实验室字段1
            "",  # 实验室字段2
            "",  # 报告日期时间
            "",  # 仪器收费到计算机系统
            "",  # 仪器段ID
            order.report_type,  # 报告类型
            "",  # 保留字段
            "",  # 位置或病房的标本
            "",  # 感染标志
            "",  # 标本服务
            "",  # 标本机构
        ]
        return "|".join(fields)
    
    def create_result_record(self, result):
        """创建Result记录（R记录）"""
        fields = [
            "R",  # 记录类型
            str(result.sequence_number),  # 序列号
            result.universal_test_id,  # 通用测试ID
            result.data_measurement,  # 数据或测量值
            result.units,  # 单位
            result.reference_ranges,  # 参考范围
            result.abnormal_flag,  # 异常标志
            "",  # 结果异常性质
            result.result_status,  # 结果状态
            "",  # 日期更改仪器规范值
            "",  # 操作员识别
            "",  # 日期时间测试开始
            result.datetime_test_completed,  # 日期时间测试完成
            result.instrument_id,  # 仪器识别
        ]
        return "|".join(fields)
    
    def create_terminator_record(self):
        """创建Terminator记录（L记录）"""
        fields = [
            "L",  # 记录类型
            "1",  # 序列号
            "N"   # 终止代码（N=正常终止）
        ]
        return "|".join(fields)
    
    def build_message(self, frames):
        """构建完整消息"""
        message_frames = []
        
        for idx, frame in enumerate(frames, 1):
            # 计算校验和
            checksum = self.calculate_checksum(frame)
            
            # 构建帧
            frame_number = str(idx % 8)  # 帧号0-7循环
            complete_frame = f"{self.STX}{frame_number}{frame}{self.CR}{self.ETX}{checksum}{self.CR}{self.LF}"
            message_frames.append(complete_frame)
        
        # 添加EOT
        message_frames.append(self.EOT)
        
        return "".join(message_frames)
    
    def calculate_checksum(self, data):
        """计算校验和"""
        checksum = sum(ord(c) for c in data) % 256
        return f"{checksum:02X}"
```

### 3. FHIR接口

**现代RESTful API**

```python
class FHIRInterface:
    """FHIR接口实现"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.version = "R4"
    
    def create_diagnostic_report(self, test_result):
        """创建诊断报告资源"""
        report = {
            "resourceType": "DiagnosticReport",
            "id": test_result.report_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.now().isoformat()
            },
            "status": "final",  # registered | partial | preliminary | final
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                    "code": "LAB",
                    "display": "Laboratory"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": test_result.test_code,
                    "display": test_result.test_name
                }]
            },
            "subject": {
                "reference": f"Patient/{test_result.patient_id}"
            },
            "effectiveDateTime": test_result.effective_datetime,
            "issued": test_result.issued_datetime,
            "performer": [{
                "reference": f"Organization/{test_result.lab_id}",
                "display": test_result.lab_name
            }],
            "result": [
                {
                    "reference": f"Observation/{obs.id}"
                }
                for obs in test_result.observations
            ],
            "conclusion": test_result.conclusion
        }
        
        return report
    
    def create_observation(self, observation):
        """创建观察资源"""
        obs = {
            "resourceType": "Observation",
            "id": observation.id,
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "laboratory",
                    "display": "Laboratory"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": observation.loinc_code,
                    "display": observation.test_name
                }]
            },
            "subject": {
                "reference": f"Patient/{observation.patient_id}"
            },
            "effectiveDateTime": observation.effective_datetime,
            "issued": observation.issued_datetime,
            "valueQuantity": {
                "value": observation.value,
                "unit": observation.unit,
                "system": "http://unitsofmeasure.org",
                "code": observation.ucum_code
            },
            "referenceRange": [{
                "low": {
                    "value": observation.ref_range_low,
                    "unit": observation.unit
                },
                "high": {
                    "value": observation.ref_range_high,
                    "unit": observation.unit
                }
            }],
            "interpretation": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    "code": observation.interpretation_code,  # N, H, L, HH, LL
                    "display": observation.interpretation_display
                }]
            }]
        }
        
        return obs
    
    def submit_report(self, diagnostic_report):
        """提交诊断报告"""
        response = requests.post(
            f"{self.base_url}/DiagnosticReport",
            json=diagnostic_report,
            headers={
                "Content-Type": "application/fhir+json",
                "Accept": "application/fhir+json"
            }
        )
        
        if response.status_code == 201:
            return response.json()
        else:
            raise FHIRError(f"提交失败: {response.text}")
```

## 样本追踪

### 条形码系统

```python
class SampleTrackingSystem:
    """样本追踪系统"""
    
    def __init__(self):
        self.barcode_generator = BarcodeGenerator()
        self.tracking_database = TrackingDatabase()
    
    def register_sample(self, sample_info):
        """注册样本"""
        # 生成唯一样本ID
        sample_id = self.generate_sample_id()
        
        # 生成条形码
        barcode = self.barcode_generator.generate(
            sample_id,
            barcode_type="CODE128"
        )
        
        # 记录样本信息
        sample = Sample(
            id=sample_id,
            barcode=barcode,
            patient_id=sample_info.patient_id,
            sample_type=sample_info.sample_type,
            collection_datetime=sample_info.collection_datetime,
            collector_id=sample_info.collector_id,
            status="COLLECTED"
        )
        
        self.tracking_database.insert(sample)
        
        return sample
    
    def track_sample_journey(self, sample_id):
        """追踪样本流程"""
        events = self.tracking_database.get_events(sample_id)
        
        journey = []
        for event in events:
            journey.append({
                "timestamp": event.timestamp,
                "location": event.location,
                "action": event.action,
                "user": event.user,
                "status": event.status
            })
        
        return SampleJourney(sample_id, journey)
    
    def update_sample_status(self, sample_id, new_status, location):
        """更新样本状态"""
        event = TrackingEvent(
            sample_id=sample_id,
            timestamp=datetime.now(),
            location=location,
            action=f"状态更新为{new_status}",
            user=self.get_current_user(),
            status=new_status
        )
        
        self.tracking_database.add_event(event)
```

## 中间件集成

### 双向接口引擎

```python
class InterfaceEngine:
    """接口引擎"""
    
    def __init__(self):
        self.hl7_interface = HL7Interface()
        self.astm_interface = ASTMInterface()
        self.fhir_interface = FHIRInterface()
        self.message_queue = MessageQueue()
    
    def route_message(self, message, protocol):
        """路由消息"""
        if protocol == "HL7":
            return self.hl7_interface.process(message)
        elif protocol == "ASTM":
            return self.astm_interface.process(message)
        elif protocol == "FHIR":
            return self.fhir_interface.process(message)
        else:
            raise UnsupportedProtocolError(f"不支持的协议: {protocol}")
    
    def transform_message(self, message, source_format, target_format):
        """转换消息格式"""
        # 解析源格式
        parsed_data = self.parse_message(message, source_format)
        
        # 转换为目标格式
        transformed_message = self.format_message(parsed_data, target_format)
        
        return transformed_message
    
    def handle_bidirectional_communication(self, instrument_id):
        """处理双向通信"""
        # 监听来自仪器的消息
        incoming_message = self.listen_for_message(instrument_id)
        
        if incoming_message:
            # 处理结果消息
            result = self.process_result_message(incoming_message)
            
            # 发送确认
            ack = self.send_acknowledgment(instrument_id)
        
        # 检查是否有待发送的医嘱
        pending_orders = self.get_pending_orders(instrument_id)
        
        if pending_orders:
            # 发送医嘱到仪器
            for order in pending_orders:
                self.send_order_to_instrument(instrument_id, order)
```

## 相关资源


- [IVD概述](overview.md)
- [互操作性标准](../../technical-knowledge/interoperability/index.md)- [IVD软件特点](overview.md)

## 参考标准

- HL7 v2.5.1: 健康信息交换标准
- ASTM E1394: 临床仪器与计算机系统之间的数据传输标准
- FHIR R4: 快速健康互操作性资源
- IHE LTW: 实验室测试工作流程
