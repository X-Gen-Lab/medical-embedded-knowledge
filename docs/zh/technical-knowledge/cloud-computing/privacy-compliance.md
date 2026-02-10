---
title: 隐私与合规
difficulty: intermediate
estimated_time: 2-3小时
---

# 隐私与合规

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

医疗数据的隐私保护和法规合规是医疗设备云平台的首要任务。违反隐私法规可能导致巨额罚款、法律诉讼和声誉损失。本文将介绍主要的医疗数据隐私法规及其技术实现。

## 1. 主要法规概述

### 1.1 HIPAA (Health Insurance Portability and Accountability Act)

**适用范围**: 美国

**核心要求**:
- **隐私规则**: 保护个人健康信息(PHI)的使用和披露
- **安全规则**: 要求实施物理、技术和管理保障措施
- **违规通知规则**: 数据泄露时必须通知受影响的个人

**关键概念**:
- **PHI (Protected Health Information)**: 受保护的健康信息
- **BAA (Business Associate Agreement)**: 业务伙伴协议
- **Minimum Necessary**: 最小必要原则

### 1.2 GDPR (General Data Protection Regulation)

**适用范围**: 欧盟及处理欧盟居民数据的组织

**核心原则**:
- **合法性、公平性和透明度**: 数据处理必须合法、公平且透明
- **目的限制**: 只能用于明确的合法目的
- **数据最小化**: 只收集必要的数据
- **准确性**: 确保数据准确并及时更新
- **存储限制**: 不得超过必要期限存储
- **完整性和保密性**: 确保数据安全

**个人权利**:
- 访问权
- 更正权
- 删除权（被遗忘权）
- 限制处理权
- 数据可携带权
- 反对权

### 1.3 中国《数据安全法》和《个人信息保护法》

**适用范围**: 中国境内及处理中国公民数据的组织

**核心要求**:
- **数据分类分级**: 根据重要程度进行分类分级保护
- **数据本地化**: 重要数据和个人信息需在境内存储
- **跨境传输限制**: 出境需要安全评估
- **安全保护义务**: 采取技术和管理措施保护数据安全


## 2. 数据加密

### 2.1 传输加密 (Encryption in Transit)

#### TLS/SSL配置

```python
from flask import Flask
import ssl

app = Flask(__name__)

# 配置TLS
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain('cert.pem', 'key.pem')

# 强制使用强加密套件
context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')

if __name__ == '__main__':
    app.run(ssl_context=context, host='0.0.0.0', port=443)
```

#### HTTPS请求验证

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class SecureAPIClient:
    def __init__(self, base_url, cert_path=None):
        self.base_url = base_url
        self.session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        
        # 配置证书验证
        if cert_path:
            self.session.verify = cert_path
        else:
            self.session.verify = True  # 使用系统证书
    
    def post_patient_data(self, data, token):
        """发送患者数据（加密传输）"""
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-Request-ID': str(uuid.uuid4())
        }
        
        response = self.session.post(
            f'{self.base_url}/api/v1/patients',
            json=data,
            headers=headers,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
```

### 2.2 静态加密 (Encryption at Rest)

#### 数据库加密

```python
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64
import os

class EncryptionManager:
    def __init__(self, master_key=None):
        if master_key is None:
            # 从环境变量或密钥管理服务获取
            master_key = os.environ.get('ENCRYPTION_MASTER_KEY')
        
        self.master_key = master_key.encode()
        self.cipher = self._create_cipher()
    
    def _create_cipher(self):
        """创建加密器"""
        # 使用PBKDF2派生密钥
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'medical_device_salt',  # 实际应用中应使用随机salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key))
        return Fernet(key)
    
    def encrypt_field(self, plaintext):
        """加密字段"""
        if plaintext is None:
            return None
        
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        
        encrypted = self.cipher.encrypt(plaintext)
        return base64.b64encode(encrypted).decode()
    
    def decrypt_field(self, ciphertext):
        """解密字段"""
        if ciphertext is None:
            return None
        
        ciphertext = base64.b64decode(ciphertext)
        decrypted = self.cipher.decrypt(ciphertext)
        return decrypted.decode()

# SQLAlchemy模型中使用加密
from sqlalchemy import Column, String, TypeDecorator

class EncryptedString(TypeDecorator):
    """加密字符串类型"""
    impl = String
    cache_ok = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encryption_manager = EncryptionManager()
    
    def process_bind_param(self, value, dialect):
        """存储时加密"""
        if value is not None:
            return self.encryption_manager.encrypt_field(value)
        return value
    
    def process_result_value(self, value, dialect):
        """读取时解密"""
        if value is not None:
            return self.encryption_manager.decrypt_field(value)
        return value

# 使用示例
class Patient(Base):
    __tablename__ = 'patients'
    
    patient_id = Column(UUID(as_uuid=True), primary_key=True)
    mrn = Column(String(50), unique=True, nullable=False)
    
    # 敏感字段加密存储
    ssn = Column(EncryptedString(100))  # 社会安全号
    phone = Column(EncryptedString(50))
    email = Column(EncryptedString(100))
    address = Column(EncryptedString(500))
```

#### AWS KMS集成

```python
import boto3
import base64

class KMSEncryptionManager:
    def __init__(self, key_id, region='us-east-1'):
        self.kms_client = boto3.client('kms', region_name=region)
        self.key_id = key_id
    
    def encrypt_data(self, plaintext):
        """使用KMS加密数据"""
        if isinstance(plaintext, str):
            plaintext = plaintext.encode()
        
        response = self.kms_client.encrypt(
            KeyId=self.key_id,
            Plaintext=plaintext
        )
        
        # 返回base64编码的密文
        return base64.b64encode(response['CiphertextBlob']).decode()
    
    def decrypt_data(self, ciphertext):
        """使用KMS解密数据"""
        ciphertext_blob = base64.b64decode(ciphertext)
        
        response = self.kms_client.decrypt(
            CiphertextBlob=ciphertext_blob
        )
        
        return response['Plaintext'].decode()
    
    def generate_data_key(self):
        """生成数据加密密钥"""
        response = self.kms_client.generate_data_key(
            KeyId=self.key_id,
            KeySpec='AES_256'
        )
        
        return {
            'plaintext_key': response['Plaintext'],
            'encrypted_key': base64.b64encode(response['CiphertextBlob']).decode()
        }
    
    def encrypt_large_data(self, data):
        """
        加密大数据（使用信封加密）
        1. 生成数据密钥
        2. 使用数据密钥加密数据
        3. 使用KMS加密数据密钥
        """
        # 生成数据密钥
        data_key = self.generate_data_key()
        
        # 使用数据密钥加密数据
        cipher = Fernet(base64.urlsafe_b64encode(data_key['plaintext_key']))
        encrypted_data = cipher.encrypt(data.encode() if isinstance(data, str) else data)
        
        return {
            'encrypted_data': base64.b64encode(encrypted_data).decode(),
            'encrypted_key': data_key['encrypted_key']
        }
    
    def decrypt_large_data(self, encrypted_data, encrypted_key):
        """解密大数据"""
        # 解密数据密钥
        plaintext_key = self.decrypt_data(encrypted_key)
        
        # 使用数据密钥解密数据
        cipher = Fernet(base64.urlsafe_b64encode(plaintext_key.encode()))
        encrypted_data_bytes = base64.b64decode(encrypted_data)
        decrypted_data = cipher.decrypt(encrypted_data_bytes)
        
        return decrypted_data.decode()

# 使用示例
kms = KMSEncryptionManager(key_id='arn:aws:kms:us-east-1:123456789:key/abc-123')

# 加密小数据
encrypted_ssn = kms.encrypt_data('123-45-6789')

# 加密大数据（如医疗影像）
with open('medical_image.dcm', 'rb') as f:
    image_data = f.read()

encrypted_image = kms.encrypt_large_data(image_data)
```


## 3. 访问控制

### 3.1 基于角色的访问控制 (RBAC)

```python
from enum import Enum
from functools import wraps
from flask import request, jsonify

class Role(Enum):
    ADMIN = 'admin'
    DOCTOR = 'doctor'
    NURSE = 'nurse'
    PATIENT = 'patient'
    DEVICE_OPERATOR = 'device_operator'

class Permission(Enum):
    READ_PATIENT_DATA = 'read:patient_data'
    WRITE_PATIENT_DATA = 'write:patient_data'
    READ_DEVICE_DATA = 'read:device_data'
    WRITE_DEVICE_DATA = 'write:device_data'
    MANAGE_USERS = 'manage:users'
    MANAGE_DEVICES = 'manage:devices'
    VIEW_AUDIT_LOGS = 'view:audit_logs'

# 角色权限映射
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.READ_PATIENT_DATA,
        Permission.WRITE_PATIENT_DATA,
        Permission.READ_DEVICE_DATA,
        Permission.WRITE_DEVICE_DATA,
        Permission.MANAGE_USERS,
        Permission.MANAGE_DEVICES,
        Permission.VIEW_AUDIT_LOGS
    ],
    Role.DOCTOR: [
        Permission.READ_PATIENT_DATA,
        Permission.WRITE_PATIENT_DATA,
        Permission.READ_DEVICE_DATA
    ],
    Role.NURSE: [
        Permission.READ_PATIENT_DATA,
        Permission.READ_DEVICE_DATA,
        Permission.WRITE_DEVICE_DATA
    ],
    Role.PATIENT: [
        Permission.READ_PATIENT_DATA  # 只能读取自己的数据
    ],
    Role.DEVICE_OPERATOR: [
        Permission.READ_DEVICE_DATA,
        Permission.WRITE_DEVICE_DATA,
        Permission.MANAGE_DEVICES
    ]
}

class AccessControl:
    @staticmethod
    def has_permission(user_role, required_permission):
        """检查用户是否有权限"""
        role = Role(user_role)
        permissions = ROLE_PERMISSIONS.get(role, [])
        return required_permission in permissions
    
    @staticmethod
    def require_permission(permission):
        """装饰器：要求特定权限"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 从JWT token获取用户角色
                token = request.headers.get('Authorization', '').replace('Bearer ', '')
                user_data = verify_jwt_token(token)
                
                if not user_data:
                    return jsonify({'error': 'Invalid token'}), 401
                
                user_role = user_data.get('role')
                
                if not AccessControl.has_permission(user_role, permission):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator

# 使用示例
@app.route('/api/v1/patients/<patient_id>', methods=['GET'])
@AccessControl.require_permission(Permission.READ_PATIENT_DATA)
def get_patient(patient_id):
    """获取患者信息"""
    # 额外检查：患者只能访问自己的数据
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_data = verify_jwt_token(token)
    
    if user_data['role'] == Role.PATIENT.value:
        if user_data['user_id'] != patient_id:
            return jsonify({'error': 'Access denied'}), 403
    
    patient = get_patient_from_db(patient_id)
    return jsonify(patient)

@app.route('/api/v1/devices/<device_id>/data', methods=['POST'])
@AccessControl.require_permission(Permission.WRITE_DEVICE_DATA)
def post_device_data(device_id):
    """上传设备数据"""
    data = request.json
    save_device_data(device_id, data)
    return jsonify({'status': 'success'}), 201
```

### 3.2 属性基于访问控制 (ABAC)

```python
from typing import Dict, Any

class ABACPolicy:
    def __init__(self):
        self.policies = []
    
    def add_policy(self, policy):
        """添加访问策略"""
        self.policies.append(policy)
    
    def evaluate(self, subject: Dict, resource: Dict, action: str, environment: Dict) -> bool:
        """
        评估访问请求
        
        subject: 主体属性（用户）
        resource: 资源属性（数据）
        action: 操作（read, write, delete）
        environment: 环境属性（时间、位置等）
        """
        for policy in self.policies:
            if policy.matches(subject, resource, action, environment):
                return policy.effect == 'allow'
        
        # 默认拒绝
        return False

class Policy:
    def __init__(self, name, effect, conditions):
        self.name = name
        self.effect = effect  # 'allow' or 'deny'
        self.conditions = conditions
    
    def matches(self, subject, resource, action, environment):
        """检查策略是否匹配"""
        for condition in self.conditions:
            if not condition(subject, resource, action, environment):
                return False
        return True

# 定义策略条件
def doctor_can_read_assigned_patients(subject, resource, action, environment):
    """医生只能读取分配给他的患者数据"""
    if action != 'read':
        return False
    
    if subject.get('role') != 'doctor':
        return False
    
    assigned_patients = subject.get('assigned_patients', [])
    patient_id = resource.get('patient_id')
    
    return patient_id in assigned_patients

def only_during_business_hours(subject, resource, action, environment):
    """只在工作时间允许访问"""
    from datetime import datetime
    
    current_hour = datetime.now().hour
    return 8 <= current_hour <= 18

def same_department_access(subject, resource, action, environment):
    """同部门访问"""
    return subject.get('department') == resource.get('department')

# 创建ABAC策略引擎
abac = ABACPolicy()

# 添加策略
abac.add_policy(Policy(
    name='DoctorReadAssignedPatients',
    effect='allow',
    conditions=[doctor_can_read_assigned_patients]
))

abac.add_policy(Policy(
    name='BusinessHoursAccess',
    effect='allow',
    conditions=[only_during_business_hours, same_department_access]
))

# 使用示例
subject = {
    'user_id': 'doctor-001',
    'role': 'doctor',
    'department': 'cardiology',
    'assigned_patients': ['patient-123', 'patient-456']
}

resource = {
    'patient_id': 'patient-123',
    'department': 'cardiology',
    'data_type': 'medical_record'
}

action = 'read'
environment = {'timestamp': datetime.now()}

if abac.evaluate(subject, resource, action, environment):
    print("Access granted")
else:
    print("Access denied")
```

### 3.3 OAuth 2.0 和 JWT

```python
import jwt
from datetime import datetime, timedelta
from flask import request, jsonify

class AuthenticationManager:
    def __init__(self, secret_key, algorithm='HS256'):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def generate_token(self, user_id, role, permissions, expires_in=3600):
        """生成JWT token"""
        payload = {
            'user_id': user_id,
            'role': role,
            'permissions': permissions,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iss': 'medical-device-platform',
            'aud': 'medical-api'
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token):
        """验证JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                audience='medical-api',
                issuer='medical-device-platform'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError('Token has expired')
        except jwt.InvalidTokenError:
            raise ValueError('Invalid token')
    
    def refresh_token(self, token):
        """刷新token"""
        try:
            # 验证旧token（允许过期）
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={'verify_exp': False}
            )
            
            # 生成新token
            new_token = self.generate_token(
                user_id=payload['user_id'],
                role=payload['role'],
                permissions=payload['permissions']
            )
            
            return new_token
        except jwt.InvalidTokenError:
            raise ValueError('Invalid token')

# OAuth 2.0 授权服务器
class OAuth2Server:
    def __init__(self):
        self.auth_manager = AuthenticationManager(secret_key='your-secret-key')
        self.authorization_codes = {}  # 临时存储授权码
    
    def authorize(self, client_id, redirect_uri, scope, state):
        """授权端点"""
        # 生成授权码
        import secrets
        code = secrets.token_urlsafe(32)
        
        # 存储授权码
        self.authorization_codes[code] = {
            'client_id': client_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
            'expires_at': datetime.utcnow() + timedelta(minutes=10)
        }
        
        # 重定向到客户端
        return f"{redirect_uri}?code={code}&state={state}"
    
    def token(self, grant_type, code, client_id, client_secret, redirect_uri):
        """令牌端点"""
        if grant_type != 'authorization_code':
            return {'error': 'unsupported_grant_type'}, 400
        
        # 验证授权码
        auth_code_data = self.authorization_codes.get(code)
        
        if not auth_code_data:
            return {'error': 'invalid_grant'}, 400
        
        if auth_code_data['client_id'] != client_id:
            return {'error': 'invalid_client'}, 401
        
        if auth_code_data['redirect_uri'] != redirect_uri:
            return {'error': 'invalid_grant'}, 400
        
        if datetime.utcnow() > auth_code_data['expires_at']:
            return {'error': 'expired_token'}, 400
        
        # 删除已使用的授权码
        del self.authorization_codes[code]
        
        # 生成访问令牌
        access_token = self.auth_manager.generate_token(
            user_id='user-123',
            role='doctor',
            permissions=['read:patient_data'],
            expires_in=3600
        )
        
        refresh_token = self.auth_manager.generate_token(
            user_id='user-123',
            role='doctor',
            permissions=['read:patient_data'],
            expires_in=86400  # 24小时
        )
        
        return {
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': refresh_token,
            'scope': auth_code_data['scope']
        }
```


## 4. 审计日志

### 4.1 审计日志系统

```python
from datetime import datetime
import json
import hashlib

class AuditLogger:
    def __init__(self, log_storage):
        self.log_storage = log_storage
    
    def log_access(self, user_id, resource_type, resource_id, action, result, metadata=None):
        """记录访问日志"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'action': action,
            'result': result,  # 'success' or 'denied'
            'ip_address': metadata.get('ip_address') if metadata else None,
            'user_agent': metadata.get('user_agent') if metadata else None,
            'session_id': metadata.get('session_id') if metadata else None
        }
        
        # 计算日志哈希值（防篡改）
        log_entry['hash'] = self._calculate_hash(log_entry)
        
        # 存储日志
        self.log_storage.store(log_entry)
        
        return log_entry
    
    def log_data_modification(self, user_id, table_name, record_id, operation, old_value, new_value):
        """记录数据修改日志"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'table_name': table_name,
            'record_id': record_id,
            'operation': operation,  # 'insert', 'update', 'delete'
            'old_value': old_value,
            'new_value': new_value
        }
        
        log_entry['hash'] = self._calculate_hash(log_entry)
        self.log_storage.store(log_entry)
        
        return log_entry
    
    def log_authentication(self, user_id, auth_method, result, metadata=None):
        """记录认证日志"""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'auth_method': auth_method,  # 'password', 'mfa', 'sso'
            'result': result,  # 'success' or 'failed'
            'ip_address': metadata.get('ip_address') if metadata else None,
            'failure_reason': metadata.get('failure_reason') if metadata else None
        }
        
        log_entry['hash'] = self._calculate_hash(log_entry)
        self.log_storage.store(log_entry)
        
        return log_entry
    
    def _calculate_hash(self, log_entry):
        """计算日志哈希值"""
        # 移除hash字段（如果存在）
        entry_copy = {k: v for k, v in log_entry.items() if k != 'hash'}
        
        # 序列化并计算哈希
        entry_json = json.dumps(entry_copy, sort_keys=True)
        return hashlib.sha256(entry_json.encode()).hexdigest()
    
    def verify_log_integrity(self, log_entry):
        """验证日志完整性"""
        stored_hash = log_entry.get('hash')
        calculated_hash = self._calculate_hash(log_entry)
        
        return stored_hash == calculated_hash
    
    def query_logs(self, filters):
        """查询审计日志"""
        return self.log_storage.query(filters)

# CloudWatch Logs集成
import boto3

class CloudWatchLogStorage:
    def __init__(self, log_group_name, log_stream_name, region='us-east-1'):
        self.client = boto3.client('logs', region_name=region)
        self.log_group_name = log_group_name
        self.log_stream_name = log_stream_name
        
        # 创建日志组和日志流（如果不存在）
        self._ensure_log_group_exists()
        self._ensure_log_stream_exists()
    
    def _ensure_log_group_exists(self):
        try:
            self.client.create_log_group(logGroupName=self.log_group_name)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass
    
    def _ensure_log_stream_exists(self):
        try:
            self.client.create_log_stream(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name
            )
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass
    
    def store(self, log_entry):
        """存储日志到CloudWatch"""
        self.client.put_log_events(
            logGroupName=self.log_group_name,
            logStreamName=self.log_stream_name,
            logEvents=[
                {
                    'timestamp': int(datetime.utcnow().timestamp() * 1000),
                    'message': json.dumps(log_entry)
                }
            ]
        )
    
    def query(self, filters):
        """查询日志"""
        # 构建CloudWatch Insights查询
        query_string = self._build_query_string(filters)
        
        response = self.client.start_query(
            logGroupName=self.log_group_name,
            startTime=int((datetime.utcnow() - timedelta(days=7)).timestamp()),
            endTime=int(datetime.utcnow().timestamp()),
            queryString=query_string
        )
        
        query_id = response['queryId']
        
        # 等待查询完成
        while True:
            result = self.client.get_query_results(queryId=query_id)
            status = result['status']
            
            if status in ['Complete', 'Failed', 'Cancelled']:
                break
            
            time.sleep(1)
        
        return result.get('results', [])
    
    def _build_query_string(self, filters):
        """构建查询字符串"""
        conditions = []
        
        if 'user_id' in filters:
            conditions.append(f"user_id = '{filters['user_id']}'")
        
        if 'resource_type' in filters:
            conditions.append(f"resource_type = '{filters['resource_type']}'")
        
        if 'action' in filters:
            conditions.append(f"action = '{filters['action']}'")
        
        where_clause = ' and '.join(conditions) if conditions else '1=1'
        
        return f"""
        fields @timestamp, user_id, resource_type, resource_id, action, result
        | filter {where_clause}
        | sort @timestamp desc
        | limit 100
        """

# 使用示例
log_storage = CloudWatchLogStorage(
    log_group_name='/medical-platform/audit-logs',
    log_stream_name='api-access'
)

audit_logger = AuditLogger(log_storage)

# 记录访问日志
@app.route('/api/v1/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    user_id = get_current_user_id()
    
    try:
        # 检查权限
        if not has_permission(user_id, 'read:patient_data'):
            audit_logger.log_access(
                user_id=user_id,
                resource_type='patient',
                resource_id=patient_id,
                action='read',
                result='denied',
                metadata={
                    'ip_address': request.remote_addr,
                    'user_agent': request.user_agent.string
                }
            )
            return jsonify({'error': 'Access denied'}), 403
        
        # 获取患者数据
        patient = get_patient_from_db(patient_id)
        
        # 记录成功访问
        audit_logger.log_access(
            user_id=user_id,
            resource_type='patient',
            resource_id=patient_id,
            action='read',
            result='success',
            metadata={
                'ip_address': request.remote_addr,
                'user_agent': request.user_agent.string
            }
        )
        
        return jsonify(patient)
        
    except Exception as e:
        # 记录错误
        audit_logger.log_access(
            user_id=user_id,
            resource_type='patient',
            resource_id=patient_id,
            action='read',
            result='error',
            metadata={
                'ip_address': request.remote_addr,
                'error': str(e)
            }
        )
        raise
```

### 4.2 审计报告生成

```python
from datetime import datetime, timedelta
import pandas as pd

class AuditReportGenerator:
    def __init__(self, audit_logger):
        self.audit_logger = audit_logger
    
    def generate_access_report(self, start_date, end_date, user_id=None):
        """生成访问报告"""
        filters = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        if user_id:
            filters['user_id'] = user_id
        
        logs = self.audit_logger.query_logs(filters)
        
        # 转换为DataFrame
        df = pd.DataFrame(logs)
        
        # 统计分析
        report = {
            'total_accesses': len(df),
            'successful_accesses': len(df[df['result'] == 'success']),
            'denied_accesses': len(df[df['result'] == 'denied']),
            'unique_users': df['user_id'].nunique(),
            'most_accessed_resources': df['resource_id'].value_counts().head(10).to_dict(),
            'access_by_hour': df.groupby(df['timestamp'].dt.hour).size().to_dict()
        }
        
        return report
    
    def generate_compliance_report(self, start_date, end_date):
        """生成合规报告"""
        logs = self.audit_logger.query_logs({
            'start_date': start_date,
            'end_date': end_date
        })
        
        df = pd.DataFrame(logs)
        
        # HIPAA合规检查
        report = {
            'audit_log_completeness': self._check_log_completeness(df),
            'access_control_violations': self._check_access_violations(df),
            'encryption_compliance': self._check_encryption_compliance(df),
            'data_retention_compliance': self._check_retention_compliance(df)
        }
        
        return report
    
    def _check_log_completeness(self, df):
        """检查日志完整性"""
        required_fields = ['timestamp', 'user_id', 'resource_type', 'action', 'result']
        
        completeness = {}
        for field in required_fields:
            missing_count = df[field].isna().sum()
            completeness[field] = {
                'total': len(df),
                'missing': missing_count,
                'completeness_rate': (len(df) - missing_count) / len(df) * 100
            }
        
        return completeness
    
    def _check_access_violations(self, df):
        """检查访问违规"""
        violations = df[df['result'] == 'denied']
        
        return {
            'total_violations': len(violations),
            'violations_by_user': violations['user_id'].value_counts().to_dict(),
            'violations_by_resource': violations['resource_type'].value_counts().to_dict()
        }
```


## 5. 数据匿名化和去标识化

### 5.1 数据脱敏技术

```python
import hashlib
import random
import string
from faker import Faker

class DataAnonymizer:
    def __init__(self):
        self.faker = Faker()
        self.hash_salt = 'medical_platform_salt'
    
    def anonymize_patient_data(self, patient_data):
        """匿名化患者数据"""
        anonymized = patient_data.copy()
        
        # 移除直接标识符
        anonymized['name'] = self._pseudonymize(patient_data['name'])
        anonymized['ssn'] = self._mask_ssn(patient_data.get('ssn'))
        anonymized['email'] = self._mask_email(patient_data.get('email'))
        anonymized['phone'] = self._mask_phone(patient_data.get('phone'))
        anonymized['address'] = self._generalize_address(patient_data.get('address'))
        
        # 泛化准标识符
        anonymized['date_of_birth'] = self._generalize_date(patient_data['date_of_birth'])
        anonymized['zip_code'] = self._generalize_zip_code(patient_data.get('zip_code'))
        
        return anonymized
    
    def _pseudonymize(self, value):
        """假名化 - 使用一致的哈希"""
        if not value:
            return None
        
        hash_input = f"{value}{self.hash_salt}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _mask_ssn(self, ssn):
        """掩码社会安全号"""
        if not ssn:
            return None
        
        # 只保留后4位: XXX-XX-1234
        return f"XXX-XX-{ssn[-4:]}"
    
    def _mask_email(self, email):
        """掩码电子邮件"""
        if not email:
            return None
        
        # 保留域名，掩码用户名: j***@example.com
        username, domain = email.split('@')
        masked_username = username[0] + '*' * (len(username) - 1)
        return f"{masked_username}@{domain}"
    
    def _mask_phone(self, phone):
        """掩码电话号码"""
        if not phone:
            return None
        
        # 只保留后4位: (XXX) XXX-1234
        return f"(XXX) XXX-{phone[-4:]}"
    
    def _generalize_address(self, address):
        """泛化地址 - 只保留城市和州"""
        if not address:
            return None
        
        # 假设地址格式: "123 Main St, Springfield, IL 62701"
        parts = address.split(',')
        if len(parts) >= 2:
            return f"{parts[-2].strip()}, {parts[-1].strip()[:2]}"
        
        return None
    
    def _generalize_date(self, date_str):
        """泛化日期 - 只保留年份"""
        if not date_str:
            return None
        
        # 假设格式: YYYY-MM-DD
        return date_str[:4]
    
    def _generalize_zip_code(self, zip_code):
        """泛化邮政编码 - 只保留前3位"""
        if not zip_code:
            return None
        
        return f"{zip_code[:3]}XX"
    
    def k_anonymize(self, dataframe, quasi_identifiers, k=5):
        """
        K-匿名化
        确保每个准标识符组合至少有k条记录
        """
        import pandas as pd
        
        # 按准标识符分组
        grouped = dataframe.groupby(quasi_identifiers)
        
        # 过滤掉少于k条记录的组
        filtered = grouped.filter(lambda x: len(x) >= k)
        
        return filtered
    
    def l_diversity(self, dataframe, quasi_identifiers, sensitive_attribute, l=2):
        """
        L-多样性
        确保每个等价类中敏感属性至少有l个不同值
        """
        import pandas as pd
        
        # 按准标识符分组
        grouped = dataframe.groupby(quasi_identifiers)
        
        # 过滤掉敏感属性少于l个不同值的组
        filtered = grouped.filter(
            lambda x: x[sensitive_attribute].nunique() >= l
        )
        
        return filtered

# 使用示例
anonymizer = DataAnonymizer()

patient_data = {
    'patient_id': 'P12345',
    'name': 'John Smith',
    'ssn': '123-45-6789',
    'email': 'john.smith@example.com',
    'phone': '(555) 123-4567',
    'address': '123 Main St, Springfield, IL 62701',
    'date_of_birth': '1980-05-15',
    'zip_code': '62701',
    'diagnosis': 'Hypertension'
}

anonymized_data = anonymizer.anonymize_patient_data(patient_data)
print(anonymized_data)
```

### 5.2 差分隐私

```python
import numpy as np

class DifferentialPrivacy:
    def __init__(self, epsilon=1.0):
        """
        epsilon: 隐私预算，越小隐私保护越强
        """
        self.epsilon = epsilon
    
    def add_laplace_noise(self, true_value, sensitivity):
        """
        添加拉普拉斯噪声
        
        sensitivity: 查询的敏感度（单个记录变化对结果的最大影响）
        """
        scale = sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return true_value + noise
    
    def noisy_count(self, count):
        """带噪声的计数查询"""
        # 计数查询的敏感度为1
        return int(self.add_laplace_noise(count, sensitivity=1))
    
    def noisy_sum(self, sum_value, max_value):
        """带噪声的求和查询"""
        # 求和查询的敏感度为max_value
        return self.add_laplace_noise(sum_value, sensitivity=max_value)
    
    def noisy_average(self, values, min_value, max_value):
        """带噪声的平均值查询"""
        true_avg = np.mean(values)
        count = len(values)
        
        # 平均值的敏感度
        sensitivity = (max_value - min_value) / count
        
        return self.add_laplace_noise(true_avg, sensitivity)

# 使用示例
dp = DifferentialPrivacy(epsilon=0.5)

# 查询患者数量（带隐私保护）
true_patient_count = 1000
noisy_count = dp.noisy_count(true_patient_count)
print(f"True count: {true_patient_count}, Noisy count: {noisy_count}")

# 查询平均心率（带隐私保护）
heart_rates = [70, 75, 80, 72, 78, 85, 68, 73, 77, 82]
noisy_avg = dp.noisy_average(heart_rates, min_value=40, max_value=200)
print(f"True average: {np.mean(heart_rates):.2f}, Noisy average: {noisy_avg:.2f}")
```

## 6. 合规检查清单

### 6.1 HIPAA合规检查

```python
class HIPAAComplianceChecker:
    def __init__(self):
        self.checks = []
    
    def check_encryption_at_rest(self, storage_config):
        """检查静态加密"""
        result = {
            'check': 'Encryption at Rest',
            'status': 'pass' if storage_config.get('encryption_enabled') else 'fail',
            'details': storage_config
        }
        self.checks.append(result)
        return result
    
    def check_encryption_in_transit(self, api_config):
        """检查传输加密"""
        result = {
            'check': 'Encryption in Transit',
            'status': 'pass' if api_config.get('tls_enabled') else 'fail',
            'details': api_config
        }
        self.checks.append(result)
        return result
    
    def check_access_controls(self, iam_config):
        """检查访问控制"""
        has_rbac = iam_config.get('rbac_enabled', False)
        has_mfa = iam_config.get('mfa_enabled', False)
        
        result = {
            'check': 'Access Controls',
            'status': 'pass' if (has_rbac and has_mfa) else 'fail',
            'details': {
                'rbac_enabled': has_rbac,
                'mfa_enabled': has_mfa
            }
        }
        self.checks.append(result)
        return result
    
    def check_audit_logging(self, logging_config):
        """检查审计日志"""
        result = {
            'check': 'Audit Logging',
            'status': 'pass' if logging_config.get('audit_enabled') else 'fail',
            'details': logging_config
        }
        self.checks.append(result)
        return result
    
    def check_backup_and_recovery(self, backup_config):
        """检查备份和恢复"""
        has_backup = backup_config.get('backup_enabled', False)
        has_dr_plan = backup_config.get('disaster_recovery_plan', False)
        
        result = {
            'check': 'Backup and Recovery',
            'status': 'pass' if (has_backup and has_dr_plan) else 'fail',
            'details': backup_config
        }
        self.checks.append(result)
        return result
    
    def generate_report(self):
        """生成合规报告"""
        total_checks = len(self.checks)
        passed_checks = sum(1 for check in self.checks if check['status'] == 'pass')
        
        report = {
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'compliance_rate': (passed_checks / total_checks * 100) if total_checks > 0 else 0,
            'checks': self.checks
        }
        
        return report

# 使用示例
checker = HIPAAComplianceChecker()

# 执行检查
checker.check_encryption_at_rest({'encryption_enabled': True, 'algorithm': 'AES-256'})
checker.check_encryption_in_transit({'tls_enabled': True, 'tls_version': '1.3'})
checker.check_access_controls({'rbac_enabled': True, 'mfa_enabled': True})
checker.check_audit_logging({'audit_enabled': True, 'retention_days': 365})
checker.check_backup_and_recovery({'backup_enabled': True, 'disaster_recovery_plan': True})

# 生成报告
report = checker.generate_report()
print(f"Compliance Rate: {report['compliance_rate']:.2f}%")
```

### 6.2 GDPR合规检查

```python
class GDPRComplianceManager:
    def __init__(self):
        self.data_registry = {}
    
    def register_data_processing(self, purpose, legal_basis, data_categories, retention_period):
        """注册数据处理活动"""
        processing_id = str(uuid.uuid4())
        
        self.data_registry[processing_id] = {
            'purpose': purpose,
            'legal_basis': legal_basis,  # consent, contract, legal_obligation, etc.
            'data_categories': data_categories,
            'retention_period': retention_period,
            'registered_at': datetime.utcnow().isoformat()
        }
        
        return processing_id
    
    def handle_data_subject_request(self, request_type, subject_id):
        """处理数据主体请求"""
        if request_type == 'access':
            return self._handle_access_request(subject_id)
        elif request_type == 'rectification':
            return self._handle_rectification_request(subject_id)
        elif request_type == 'erasure':
            return self._handle_erasure_request(subject_id)
        elif request_type == 'portability':
            return self._handle_portability_request(subject_id)
        else:
            raise ValueError(f"Unknown request type: {request_type}")
    
    def _handle_access_request(self, subject_id):
        """处理访问请求 - 提供个人数据副本"""
        # 收集所有相关数据
        data = {
            'patient_data': get_patient_data(subject_id),
            'measurements': get_measurements(subject_id),
            'audit_logs': get_audit_logs(subject_id)
        }
        
        return {
            'request_type': 'access',
            'subject_id': subject_id,
            'data': data,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def _handle_erasure_request(self, subject_id):
        """处理删除请求 - 删除个人数据"""
        # 检查是否有法律义务保留数据
        if self._has_legal_retention_requirement(subject_id):
            return {
                'request_type': 'erasure',
                'status': 'denied',
                'reason': 'Legal retention requirement'
            }
        
        # 删除数据
        delete_patient_data(subject_id)
        delete_measurements(subject_id)
        anonymize_audit_logs(subject_id)
        
        return {
            'request_type': 'erasure',
            'status': 'completed',
            'subject_id': subject_id,
            'completed_at': datetime.utcnow().isoformat()
        }
    
    def _handle_portability_request(self, subject_id):
        """处理数据可携带请求 - 以机器可读格式提供数据"""
        data = {
            'patient_data': get_patient_data(subject_id),
            'measurements': get_measurements(subject_id)
        }
        
        # 转换为标准格式（如FHIR）
        fhir_bundle = convert_to_fhir(data)
        
        return {
            'request_type': 'portability',
            'subject_id': subject_id,
            'format': 'FHIR',
            'data': fhir_bundle,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def check_consent(self, subject_id, purpose):
        """检查同意"""
        consent = get_consent_record(subject_id, purpose)
        
        if not consent:
            return False
        
        # 检查同意是否有效
        if consent.get('withdrawn'):
            return False
        
        if consent.get('expiry_date'):
            if datetime.fromisoformat(consent['expiry_date']) < datetime.utcnow():
                return False
        
        return True
```

## 7. 安全最佳实践

### 关键要点

1. **默认安全**: 系统设计时就考虑安全性
2. **最小权限**: 只授予必要的权限
3. **纵深防御**: 多层安全措施
4. **持续监控**: 实时监控和告警
5. **定期审计**: 定期进行安全审计
6. **员工培训**: 定期进行安全意识培训
7. **事件响应**: 制定并演练事件响应计划

### 安全检查清单

- [ ] 所有数据传输使用TLS 1.2+
- [ ] 敏感数据静态加密
- [ ] 实施强密码策略
- [ ] 启用多因素认证(MFA)
- [ ] 实施基于角色的访问控制(RBAC)
- [ ] 记录所有访问和修改操作
- [ ] 定期备份数据
- [ ] 测试灾难恢复计划
- [ ] 定期更新和打补丁
- [ ] 进行安全漏洞扫描
- [ ] 实施入侵检测系统(IDS)
- [ ] 制定数据泄露响应计划

## 总结

隐私保护和合规是医疗设备云平台的基础。需要：

1. **了解法规**: 深入理解HIPAA、GDPR等法规要求
2. **技术实现**: 实施加密、访问控制、审计日志等技术措施
3. **流程管理**: 建立数据处理流程和事件响应流程
4. **持续改进**: 定期审查和更新安全措施

## 参考资源

- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [GDPR Official Text](https://gdpr.eu/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CIS Controls](https://www.cisecurity.org/controls/)
