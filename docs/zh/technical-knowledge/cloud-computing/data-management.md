---
title: 数据管理
difficulty: intermediate
estimated_time: 2-3小时
---

# 数据管理

## 学习目标

通过本文档的学习，你将能够：

- 理解核心概念和原理
- 掌握实际应用方法
- 了解最佳实践和注意事项

## 前置知识

在学习本文档之前，建议你已经掌握：

- 基础的嵌入式系统知识
- C/C++编程基础
- 相关领域的基本概念

## 概述

医疗数据管理是云平台的核心功能之一。医疗数据具有以下特点：

- **高价值**: 关系到患者健康和生命
- **高敏感性**: 包含个人隐私信息
- **多样性**: 包括结构化、半结构化和非结构化数据
- **大容量**: 医疗影像等数据量巨大
- **长期保存**: 法规要求长期存储

本文将介绍医疗云平台中的数据存储、处理和管理策略。

## 1. 医疗数据类型

### 1.1 结构化数据
- **患者基本信息**: 姓名、年龄、性别、病史
- **生理参数**: 心率、血压、血糖、体温
- **检验结果**: 血常规、生化指标
- **用药记录**: 药物名称、剂量、时间

### 1.2 半结构化数据
- **HL7消息**: 医疗信息交换标准
- **FHIR资源**: JSON/XML格式的医疗数据
- **设备日志**: JSON格式的设备运行日志

### 1.3 非结构化数据
- **医疗影像**: DICOM格式的CT、MRI、X光片
- **波形数据**: ECG、EEG波形
- **文档**: PDF格式的检查报告、病历
- **音视频**: 远程会诊录音录像

## 2. 数据存储方案

### 2.1 关系型数据库 (RDBMS)

适用于结构化数据，支持ACID事务。

#### PostgreSQL示例 - 患者数据模型

```sql
-- 患者表
CREATE TABLE patients (
    patient_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mrn VARCHAR(50) UNIQUE NOT NULL,  -- Medical Record Number
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10),
    phone VARCHAR(20),
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 索引
    CONSTRAINT chk_gender CHECK (gender IN ('male', 'female', 'other'))
);

CREATE INDEX idx_patients_mrn ON patients(mrn);
CREATE INDEX idx_patients_name ON patients(last_name, first_name);

-- 设备表
CREATE TABLE devices (
    device_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    serial_number VARCHAR(100) UNIQUE NOT NULL,
    device_type VARCHAR(50) NOT NULL,
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    firmware_version VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    last_seen TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_status CHECK (status IN ('active', 'inactive', 'maintenance', 'retired'))
);

CREATE INDEX idx_devices_serial ON devices(serial_number);
CREATE INDEX idx_devices_type ON devices(device_type);

-- 测量数据表 (时序数据)
CREATE TABLE measurements (
    measurement_id BIGSERIAL PRIMARY KEY,
    device_id UUID NOT NULL REFERENCES devices(device_id),
    patient_id UUID REFERENCES patients(patient_id),
    measurement_type VARCHAR(50) NOT NULL,
    value NUMERIC(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    measured_at TIMESTAMP NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- 分区键
    PARTITION BY RANGE (measured_at)
);

-- 创建分区 (按月)
CREATE TABLE measurements_2024_01 PARTITION OF measurements
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE measurements_2024_02 PARTITION OF measurements
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 索引
CREATE INDEX idx_measurements_device ON measurements(device_id, measured_at DESC);
CREATE INDEX idx_measurements_patient ON measurements(patient_id, measured_at DESC);

-- 告警表
CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id UUID NOT NULL REFERENCES devices(device_id),
    patient_id UUID REFERENCES patients(patient_id),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by UUID,
    acknowledged_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_severity CHECK (severity IN ('low', 'medium', 'high', 'critical'))
);

CREATE INDEX idx_alerts_device ON alerts(device_id, created_at DESC);
CREATE INDEX idx_alerts_unacknowledged ON alerts(acknowledged) WHERE acknowledged = FALSE;
```


#### 数据访问层 (Python)

```python
from sqlalchemy import create_engine, Column, String, DateTime, Numeric, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    
    patient_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mrn = Column(String(50), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(10))
    phone = Column(String(20))
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Measurement(Base):
    __tablename__ = 'measurements'
    
    measurement_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = Column(UUID(as_uuid=True), nullable=False)
    patient_id = Column(UUID(as_uuid=True))
    measurement_type = Column(String(50), nullable=False)
    value = Column(Numeric(10, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    measured_at = Column(DateTime, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

# 数据库连接
engine = create_engine(
    'postgresql://user:password@localhost:5432/medical_db',
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True  # 检查连接有效性
)

Session = sessionmaker(bind=engine)

# 数据访问对象
class MeasurementDAO:
    def __init__(self):
        self.session = Session()
    
    def create_measurement(self, device_id, patient_id, measurement_type, value, unit, measured_at):
        """创建新的测量记录"""
        measurement = Measurement(
            device_id=device_id,
            patient_id=patient_id,
            measurement_type=measurement_type,
            value=value,
            unit=unit,
            measured_at=measured_at
        )
        self.session.add(measurement)
        self.session.commit()
        return measurement
    
    def get_patient_measurements(self, patient_id, start_date, end_date, measurement_type=None):
        """获取患者的测量数据"""
        query = self.session.query(Measurement).filter(
            Measurement.patient_id == patient_id,
            Measurement.measured_at >= start_date,
            Measurement.measured_at <= end_date
        )
        
        if measurement_type:
            query = query.filter(Measurement.measurement_type == measurement_type)
        
        return query.order_by(Measurement.measured_at.desc()).all()
    
    def get_latest_measurement(self, device_id, measurement_type):
        """获取设备的最新测量值"""
        return self.session.query(Measurement).filter(
            Measurement.device_id == device_id,
            Measurement.measurement_type == measurement_type
        ).order_by(Measurement.measured_at.desc()).first()
```

### 2.2 时序数据库 (Time Series Database)

医疗设备产生大量时序数据，使用专门的时序数据库可以提高性能。

#### InfluxDB示例

```python
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

class InfluxDBManager:
    def __init__(self, url, token, org, bucket):
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket = bucket
        self.org = org
    
    def write_vital_signs(self, device_id, patient_id, vital_signs):
        """
        写入生命体征数据
        vital_signs: {
            'heart_rate': 75,
            'blood_pressure_systolic': 120,
            'blood_pressure_diastolic': 80,
            'spo2': 98,
            'temperature': 36.5
        }
        """
        points = []
        timestamp = datetime.utcnow()
        
        for measurement, value in vital_signs.items():
            point = Point("vital_signs") \
                .tag("device_id", device_id) \
                .tag("patient_id", patient_id) \
                .field(measurement, float(value)) \
                .time(timestamp, WritePrecision.NS)
            points.append(point)
        
        self.write_api.write(bucket=self.bucket, org=self.org, record=points)
    
    def query_heart_rate(self, patient_id, start_time, end_time):
        """查询心率数据"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start_time}, stop: {end_time})
          |> filter(fn: (r) => r["_measurement"] == "vital_signs")
          |> filter(fn: (r) => r["patient_id"] == "{patient_id}")
          |> filter(fn: (r) => r["_field"] == "heart_rate")
          |> aggregateWindow(every: 1m, fn: mean, createEmpty: false)
        '''
        
        result = self.query_api.query(org=self.org, query=query)
        
        data = []
        for table in result:
            for record in table.records:
                data.append({
                    'time': record.get_time(),
                    'value': record.get_value()
                })
        
        return data
    
    def calculate_statistics(self, patient_id, measurement, start_time, end_time):
        """计算统计数据"""
        query = f'''
        from(bucket: "{self.bucket}")
          |> range(start: {start_time}, stop: {end_time})
          |> filter(fn: (r) => r["_measurement"] == "vital_signs")
          |> filter(fn: (r) => r["patient_id"] == "{patient_id}")
          |> filter(fn: (r) => r["_field"] == "{measurement}")
          |> mean()
        '''
        
        result = self.query_api.query(org=self.org, query=query)
        
        if result and len(result) > 0 and len(result[0].records) > 0:
            return result[0].records[0].get_value()
        return None

# 使用示例
influx = InfluxDBManager(
    url="http://localhost:8086",
    token="your-token",
    org="medical-org",
    bucket="device-data"
)

# 写入数据
influx.write_vital_signs(
    device_id="device-001",
    patient_id="patient-123",
    vital_signs={
        'heart_rate': 75,
        'spo2': 98,
        'temperature': 36.5
    }
)

# 查询数据
heart_rate_data = influx.query_heart_rate(
    patient_id="patient-123",
    start_time="-1h",
    end_time="now()"
)
```


### 2.3 对象存储 (Object Storage)

用于存储医疗影像、文档等大文件。

#### AWS S3示例

```python
import boto3
from botocore.exceptions import ClientError
import hashlib
import json

class MedicalImageStorage:
    def __init__(self, bucket_name, region='us-east-1'):
        self.s3_client = boto3.client('s3', region_name=region)
        self.bucket_name = bucket_name
    
    def upload_dicom_image(self, file_path, patient_id, study_id, series_id):
        """
        上传DICOM影像
        使用分层存储结构: patient_id/study_id/series_id/filename
        """
        # 计算文件哈希值用于完整性验证
        file_hash = self._calculate_file_hash(file_path)
        
        # 构建S3对象键
        file_name = file_path.split('/')[-1]
        object_key = f"dicom/{patient_id}/{study_id}/{series_id}/{file_name}"
        
        # 元数据
        metadata = {
            'patient-id': patient_id,
            'study-id': study_id,
            'series-id': series_id,
            'file-hash': file_hash,
            'content-type': 'application/dicom'
        }
        
        try:
            # 上传文件
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                object_key,
                ExtraArgs={
                    'Metadata': metadata,
                    'ServerSideEncryption': 'AES256',  # 服务器端加密
                    'StorageClass': 'STANDARD_IA'  # 不频繁访问存储类
                }
            )
            
            # 生成预签名URL (24小时有效)
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': object_key},
                ExpiresIn=86400
            )
            
            return {
                'success': True,
                'object_key': object_key,
                'url': url,
                'hash': file_hash
            }
            
        except ClientError as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def download_dicom_image(self, object_key, download_path):
        """下载DICOM影像"""
        try:
            self.s3_client.download_file(
                self.bucket_name,
                object_key,
                download_path
            )
            
            # 验证文件完整性
            metadata = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=object_key
            )['Metadata']
            
            stored_hash = metadata.get('file-hash')
            downloaded_hash = self._calculate_file_hash(download_path)
            
            if stored_hash != downloaded_hash:
                raise ValueError("File integrity check failed")
            
            return {'success': True, 'path': download_path}
            
        except ClientError as e:
            return {'success': False, 'error': str(e)}
    
    def list_patient_studies(self, patient_id):
        """列出患者的所有检查"""
        prefix = f"dicom/{patient_id}/"
        
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                Delimiter='/'
            )
            
            studies = []
            if 'CommonPrefixes' in response:
                for prefix in response['CommonPrefixes']:
                    study_id = prefix['Prefix'].split('/')[-2]
                    studies.append(study_id)
            
            return studies
            
        except ClientError as e:
            return []
    
    def _calculate_file_hash(self, file_path):
        """计算文件SHA256哈希值"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def set_lifecycle_policy(self):
        """设置生命周期策略"""
        lifecycle_policy = {
            'Rules': [
                {
                    'Id': 'Archive old DICOM images',
                    'Status': 'Enabled',
                    'Prefix': 'dicom/',
                    'Transitions': [
                        {
                            'Days': 90,
                            'StorageClass': 'GLACIER'  # 90天后转到冰川存储
                        },
                        {
                            'Days': 365,
                            'StorageClass': 'DEEP_ARCHIVE'  # 1年后转到深度归档
                        }
                    ]
                },
                {
                    'Id': 'Delete temporary files',
                    'Status': 'Enabled',
                    'Prefix': 'temp/',
                    'Expiration': {
                        'Days': 7  # 7天后删除临时文件
                    }
                }
            ]
        }
        
        self.s3_client.put_bucket_lifecycle_configuration(
            Bucket=self.bucket_name,
            LifecycleConfiguration=lifecycle_policy
        )

# 使用示例
storage = MedicalImageStorage(bucket_name='medical-images-bucket')

# 上传影像
result = storage.upload_dicom_image(
    file_path='/path/to/image.dcm',
    patient_id='P12345',
    study_id='S001',
    series_id='SE001'
)

# 设置生命周期策略
storage.set_lifecycle_policy()
```

### 2.4 NoSQL数据库

用于存储半结构化数据，如FHIR资源、设备日志等。

#### MongoDB示例

```python
from pymongo import MongoClient
from datetime import datetime
import json

class FHIRResourceStore:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.db = self.client['medical_db']
        self.patients = self.db['patients']
        self.observations = self.db['observations']
        
        # 创建索引
        self.patients.create_index('identifier.value')
        self.observations.create_index([('subject.reference', 1), ('effectiveDateTime', -1)])
    
    def store_patient(self, fhir_patient):
        """存储FHIR Patient资源"""
        patient_doc = {
            'resourceType': 'Patient',
            'id': fhir_patient.get('id'),
            'identifier': fhir_patient.get('identifier', []),
            'name': fhir_patient.get('name', []),
            'gender': fhir_patient.get('gender'),
            'birthDate': fhir_patient.get('birthDate'),
            'telecom': fhir_patient.get('telecom', []),
            'address': fhir_patient.get('address', []),
            'meta': {
                'lastUpdated': datetime.utcnow().isoformat(),
                'versionId': '1'
            }
        }
        
        result = self.patients.insert_one(patient_doc)
        return str(result.inserted_id)
    
    def store_observation(self, fhir_observation):
        """存储FHIR Observation资源（如生命体征）"""
        observation_doc = {
            'resourceType': 'Observation',
            'id': fhir_observation.get('id'),
            'status': fhir_observation.get('status'),
            'category': fhir_observation.get('category', []),
            'code': fhir_observation.get('code'),
            'subject': fhir_observation.get('subject'),
            'effectiveDateTime': fhir_observation.get('effectiveDateTime'),
            'valueQuantity': fhir_observation.get('valueQuantity'),
            'device': fhir_observation.get('device'),
            'meta': {
                'lastUpdated': datetime.utcnow().isoformat()
            }
        }
        
        result = self.observations.insert_one(observation_doc)
        return str(result.inserted_id)
    
    def query_patient_observations(self, patient_id, code=None, start_date=None, end_date=None):
        """查询患者的观察数据"""
        query = {
            'subject.reference': f'Patient/{patient_id}'
        }
        
        if code:
            query['code.coding.code'] = code
        
        if start_date or end_date:
            query['effectiveDateTime'] = {}
            if start_date:
                query['effectiveDateTime']['$gte'] = start_date
            if end_date:
                query['effectiveDateTime']['$lte'] = end_date
        
        observations = self.observations.find(query).sort('effectiveDateTime', -1)
        return list(observations)
    
    def aggregate_vital_signs(self, patient_id, vital_sign_code, days=7):
        """聚合生命体征数据"""
        pipeline = [
            {
                '$match': {
                    'subject.reference': f'Patient/{patient_id}',
                    'code.coding.code': vital_sign_code,
                    'effectiveDateTime': {
                        '$gte': (datetime.utcnow() - timedelta(days=days)).isoformat()
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'avg': {'$avg': '$valueQuantity.value'},
                    'min': {'$min': '$valueQuantity.value'},
                    'max': {'$max': '$valueQuantity.value'},
                    'count': {'$sum': 1}
                }
            }
        ]
        
        result = list(self.observations.aggregate(pipeline))
        return result[0] if result else None

# 使用示例
fhir_store = FHIRResourceStore('mongodb://localhost:27017/')

# 存储患者
patient = {
    'id': 'patient-123',
    'identifier': [{'system': 'http://hospital.org/mrn', 'value': 'MRN12345'}],
    'name': [{'family': 'Smith', 'given': ['John']}],
    'gender': 'male',
    'birthDate': '1980-01-01'
}
fhir_store.store_patient(patient)

# 存储观察数据（心率）
observation = {
    'id': 'obs-001',
    'status': 'final',
    'code': {
        'coding': [{
            'system': 'http://loinc.org',
            'code': '8867-4',
            'display': 'Heart rate'
        }]
    },
    'subject': {'reference': 'Patient/patient-123'},
    'effectiveDateTime': datetime.utcnow().isoformat(),
    'valueQuantity': {
        'value': 75,
        'unit': 'beats/minute',
        'system': 'http://unitsofmeasure.org',
        'code': '/min'
    }
}
fhir_store.store_observation(observation)
```


## 3. 数据湖架构

数据湖是一个集中式存储库，可以存储任意规模的结构化和非结构化数据。

### 3.1 数据湖分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    数据消费层                            │
│  BI工具 | 机器学习 | 数据分析 | 报告生成                  │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    精炼层 (Gold)                         │
│  - 业务级聚合数据                                        │
│  - 优化的查询性能                                        │
│  - 数据集市                                              │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    清洗层 (Silver)                       │
│  - 清洗和验证的数据                                      │
│  - 标准化格式                                            │
│  - 去重和质量检查                                        │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    原始层 (Bronze)                       │
│  - 原始数据                                              │
│  - 保持原始格式                                          │
│  - 不可变存储                                            │
└─────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────┐
│                    数据源                                │
│  医疗设备 | HIS | PACS | 实验室系统                      │
└─────────────────────────────────────────────────────────┘
```

### 3.2 AWS数据湖实现

```python
import boto3
import json
from datetime import datetime

class MedicalDataLake:
    def __init__(self, bucket_name, region='us-east-1'):
        self.s3 = boto3.client('s3', region_name=region)
        self.glue = boto3.client('glue', region_name=region)
        self.athena = boto3.client('athena', region_name=region)
        self.bucket_name = bucket_name
    
    def ingest_raw_data(self, data, source_system, data_type):
        """
        摄取原始数据到Bronze层
        """
        timestamp = datetime.utcnow()
        date_partition = timestamp.strftime('%Y/%m/%d')
        
        # 构建S3路径: bronze/source/type/year/month/day/
        object_key = f"bronze/{source_system}/{data_type}/{date_partition}/{timestamp.timestamp()}.json"
        
        # 上传到S3
        self.s3.put_object(
            Bucket=self.bucket_name,
            Key=object_key,
            Body=json.dumps(data),
            Metadata={
                'source-system': source_system,
                'data-type': data_type,
                'ingestion-time': timestamp.isoformat()
            }
        )
        
        return object_key
    
    def create_glue_catalog(self):
        """创建Glue数据目录"""
        
        # 创建数据库
        try:
            self.glue.create_database(
                DatabaseInput={
                    'Name': 'medical_data_lake',
                    'Description': 'Medical device data lake'
                }
            )
        except self.glue.exceptions.AlreadyExistsException:
            pass
        
        # 创建表 - 设备测量数据
        self.glue.create_table(
            DatabaseName='medical_data_lake',
            TableInput={
                'Name': 'device_measurements',
                'StorageDescriptor': {
                    'Columns': [
                        {'Name': 'device_id', 'Type': 'string'},
                        {'Name': 'patient_id', 'Type': 'string'},
                        {'Name': 'measurement_type', 'Type': 'string'},
                        {'Name': 'value', 'Type': 'double'},
                        {'Name': 'unit', 'Type': 'string'},
                        {'Name': 'measured_at', 'Type': 'timestamp'}
                    ],
                    'Location': f's3://{self.bucket_name}/silver/measurements/',
                    'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                    'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                    'SerdeInfo': {
                        'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe',
                        'Parameters': {
                            'field.delim': ',',
                            'serialization.format': ','
                        }
                    }
                },
                'PartitionKeys': [
                    {'Name': 'year', 'Type': 'string'},
                    {'Name': 'month', 'Type': 'string'},
                    {'Name': 'day', 'Type': 'string'}
                ],
                'TableType': 'EXTERNAL_TABLE'
            }
        )
    
    def query_with_athena(self, query, output_location):
        """使用Athena查询数据"""
        
        response = self.athena.start_query_execution(
            QueryString=query,
            QueryExecutionContext={
                'Database': 'medical_data_lake'
            },
            ResultConfiguration={
                'OutputLocation': output_location
            }
        )
        
        query_execution_id = response['QueryExecutionId']
        
        # 等待查询完成
        while True:
            response = self.athena.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            
            state = response['QueryExecution']['Status']['State']
            
            if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
                break
            
            time.sleep(1)
        
        if state == 'SUCCEEDED':
            # 获取查询结果
            results = self.athena.get_query_results(
                QueryExecutionId=query_execution_id
            )
            return results
        else:
            raise Exception(f"Query failed with state: {state}")

# 使用示例
data_lake = MedicalDataLake(bucket_name='medical-data-lake')

# 摄取原始数据
device_data = {
    'device_id': 'device-001',
    'patient_id': 'patient-123',
    'measurements': [
        {'type': 'heart_rate', 'value': 75, 'unit': 'bpm'},
        {'type': 'spo2', 'value': 98, 'unit': '%'}
    ],
    'timestamp': datetime.utcnow().isoformat()
}

data_lake.ingest_raw_data(device_data, 'iot_devices', 'vital_signs')

# 创建数据目录
data_lake.create_glue_catalog()

# 查询数据
query = """
SELECT 
    device_id,
    AVG(value) as avg_heart_rate,
    MIN(value) as min_heart_rate,
    MAX(value) as max_heart_rate
FROM device_measurements
WHERE measurement_type = 'heart_rate'
    AND year = '2024'
    AND month = '01'
GROUP BY device_id
"""

results = data_lake.query_with_athena(
    query=query,
    output_location=f's3://{data_lake.bucket_name}/athena-results/'
)
```

## 4. 数据备份和恢复

### 4.1 备份策略

#### 3-2-1备份规则
- **3份副本**: 保持数据的3个副本
- **2种介质**: 使用2种不同的存储介质
- **1份异地**: 至少1份副本存储在异地

#### 备份类型
- **完全备份**: 备份所有数据
- **增量备份**: 只备份自上次备份以来的变化
- **差异备份**: 备份自上次完全备份以来的变化

### 4.2 PostgreSQL备份

```bash
#!/bin/bash
# 数据库备份脚本

# 配置
DB_NAME="medical_db"
DB_USER="postgres"
BACKUP_DIR="/backups/postgresql"
S3_BUCKET="s3://medical-backups"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

# 生成备份文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

# 执行备份
pg_dump -U $DB_USER -d $DB_NAME | gzip > $BACKUP_FILE

# 上传到S3
aws s3 cp $BACKUP_FILE $S3_BUCKET/postgresql/

# 删除本地旧备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete

# 验证备份
if [ -f "$BACKUP_FILE" ]; then
    echo "Backup completed successfully: $BACKUP_FILE"
else
    echo "Backup failed!"
    exit 1
fi
```

### 4.3 灾难恢复计划

```python
class DisasterRecoveryManager:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.rds = boto3.client('rds')
        self.ec2 = boto3.client('ec2')
    
    def create_rds_snapshot(self, db_instance_id):
        """创建RDS快照"""
        snapshot_id = f"{db_instance_id}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
        
        response = self.rds.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceIdentifier=db_instance_id,
            Tags=[
                {'Key': 'Type', 'Value': 'Manual'},
                {'Key': 'Purpose', 'Value': 'DisasterRecovery'}
            ]
        )
        
        return snapshot_id
    
    def restore_from_snapshot(self, snapshot_id, new_instance_id):
        """从快照恢复数据库"""
        response = self.rds.restore_db_instance_from_db_snapshot(
            DBInstanceIdentifier=new_instance_id,
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceClass='db.t3.large',
            MultiAZ=True,
            PubliclyAccessible=False
        )
        
        return response
    
    def setup_cross_region_replication(self, source_bucket, dest_bucket, dest_region):
        """设置跨区域复制"""
        replication_config = {
            'Role': 'arn:aws:iam::123456789:role/s3-replication-role',
            'Rules': [
                {
                    'ID': 'ReplicateAll',
                    'Status': 'Enabled',
                    'Priority': 1,
                    'Filter': {},
                    'Destination': {
                        'Bucket': f'arn:aws:s3:::{dest_bucket}',
                        'ReplicationTime': {
                            'Status': 'Enabled',
                            'Time': {'Minutes': 15}
                        },
                        'Metrics': {
                            'Status': 'Enabled',
                            'EventThreshold': {'Minutes': 15}
                        }
                    }
                }
            ]
        }
        
        self.s3.put_bucket_replication(
            Bucket=source_bucket,
            ReplicationConfiguration=replication_config
        )
```

## 5. 数据质量管理

### 5.1 数据验证

```python
from pydantic import BaseModel, validator, Field
from typing import Optional
from datetime import datetime

class VitalSignsMeasurement(BaseModel):
    """生命体征数据模型"""
    device_id: str = Field(..., min_length=1, max_length=100)
    patient_id: str = Field(..., min_length=1, max_length=100)
    heart_rate: Optional[float] = Field(None, ge=20, le=300)
    blood_pressure_systolic: Optional[int] = Field(None, ge=50, le=250)
    blood_pressure_diastolic: Optional[int] = Field(None, ge=30, le=150)
    spo2: Optional[float] = Field(None, ge=0, le=100)
    temperature: Optional[float] = Field(None, ge=30.0, le=45.0)
    measured_at: datetime
    
    @validator('blood_pressure_systolic', 'blood_pressure_diastolic')
    def validate_blood_pressure(cls, v, values):
        """验证血压值的合理性"""
        if 'blood_pressure_systolic' in values and 'blood_pressure_diastolic' in values:
            systolic = values.get('blood_pressure_systolic')
            diastolic = v if 'blood_pressure_diastolic' not in values else values.get('blood_pressure_diastolic')
            
            if systolic and diastolic and systolic <= diastolic:
                raise ValueError('Systolic pressure must be greater than diastolic pressure')
        
        return v
    
    @validator('measured_at')
    def validate_timestamp(cls, v):
        """验证时间戳不能是未来时间"""
        if v > datetime.utcnow():
            raise ValueError('Measurement timestamp cannot be in the future')
        return v

# 使用示例
try:
    measurement = VitalSignsMeasurement(
        device_id='device-001',
        patient_id='patient-123',
        heart_rate=75,
        blood_pressure_systolic=120,
        blood_pressure_diastolic=80,
        spo2=98,
        temperature=36.5,
        measured_at=datetime.utcnow()
    )
    print("Data validation passed")
except ValueError as e:
    print(f"Data validation failed: {e}")
```

### 5.2 数据清洗

```python
import pandas as pd
import numpy as np

class DataCleaner:
    def clean_vital_signs(self, df):
        """清洗生命体征数据"""
        
        # 1. 删除重复记录
        df = df.drop_duplicates(subset=['device_id', 'measured_at'])
        
        # 2. 处理缺失值
        # 对于数值型数据，使用前向填充
        numeric_columns = ['heart_rate', 'spo2', 'temperature']
        df[numeric_columns] = df[numeric_columns].fillna(method='ffill')
        
        # 3. 处理异常值
        df = self._remove_outliers(df, 'heart_rate', 40, 200)
        df = self._remove_outliers(df, 'spo2', 70, 100)
        df = self._remove_outliers(df, 'temperature', 35.0, 42.0)
        
        # 4. 数据类型转换
        df['measured_at'] = pd.to_datetime(df['measured_at'])
        
        # 5. 排序
        df = df.sort_values(['patient_id', 'measured_at'])
        
        return df
    
    def _remove_outliers(self, df, column, min_val, max_val):
        """移除异常值"""
        df = df[(df[column] >= min_val) & (df[column] <= max_val)]
        return df
    
    def detect_anomalies(self, df, column):
        """使用IQR方法检测异常值"""
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
        return anomalies
```

## 总结

医疗数据管理需要综合考虑：

1. **数据类型**: 选择合适的存储方案
2. **性能要求**: 优化查询和写入性能
3. **成本控制**: 使用分层存储和生命周期策略
4. **数据质量**: 实施验证和清洗流程
5. **备份恢复**: 建立完善的灾难恢复计划

## 参考资源

- [AWS Data Lake Best Practices](https://aws.amazon.com/big-data/datalakes-and-analytics/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [MongoDB Healthcare Solutions](https://www.mongodb.com/industries/healthcare)
- [PostgreSQL High Availability](https://www.postgresql.org/docs/current/high-availability.html)
