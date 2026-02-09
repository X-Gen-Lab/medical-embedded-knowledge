---
title: 系统测试
description: 系统测试方法、策略和工具，包括功能测试、性能测试、安全测试和医疗器械软件系统测试最佳实践
difficulty: 高级
estimated_time: 4小时
tags:
- 系统测试
- 功能测试
- 性能测试
- 安全测试
- IEC 62304
related_modules:
- zh/software-engineering/testing-strategy/unit-testing
- zh/software-engineering/testing-strategy/integration-testing
- zh/regulatory-standards/iec-62304
last_updated: '2026-02-09'
version: '1.0'
language: zh-CN
---

# 系统测试

## 学习目标

完成本模块后，你将能够：
- 理解系统测试的概念和重要性
- 掌握不同类型的系统测试（功能、性能、安全、可靠性）
- 设计和执行系统测试用例
- 使用系统测试工具和框架
- 应用医疗器械软件系统测试的最佳实践
- 遵循IEC 62304和IEC 60601标准的系统测试要求

## 前置知识

- 单元测试和集成测试基础
- 软件需求工程
- 系统架构设计
- IEC 62304标准基础知识
- 医疗器械法规要求

## 内容

### 系统测试基础

**系统测试定义**：
系统测试是在完整的、集成的系统上进行的测试，验证系统是否满足规定的需求。

**系统测试的目的**：
- 验证系统功能完整性
- 验证系统性能指标
- 验证系统安全性
- 验证系统可靠性和稳定性
- 验证用户需求满足情况
- 发现系统级缺陷

**系统测试特点**：
```
✓ 测试完整系统
✓ 基于需求规格说明
✓ 黑盒测试为主
✓ 在真实或模拟环境中执行
✓ 验证端到端功能
✓ 发现系统级问题
```

**系统测试 vs 集成测试**：

| 维度 | 集成测试 | 系统测试 |
|------|---------|---------|
| 测试范围 | 模块间接口 | 完整系统 |
| 测试基础 | 设计文档 | 需求规格 |
| 测试方法 | 白盒/灰盒 | 黑盒为主 |
| 测试环境 | 部分集成 | 完整系统 |
| 测试目标 | 接口正确性 | 需求满足度 |
| 执行时机 | 集成阶段 | 系统完成后 |


### 系统测试类型

#### 1. 功能测试（Functional Testing）

**定义**：验证系统功能是否符合需求规格说明。

**测试内容**：
- 用户界面功能
- 数据处理功能
- 业务逻辑功能
- 输入输出功能
- 错误处理功能

**示例：血压监测系统功能测试**

```python
import unittest
import serial
import time

class BloodPressureSystemFunctionalTest(unittest.TestCase):
    """血压监测系统功能测试"""
    
    def setUp(self):
        """测试前准备"""
        self.device = serial.Serial('COM3', 115200, timeout=10)
        time.sleep(2)  # 等待系统启动
        self.clear_device_state()
    
    def tearDown(self):
        """测试后清理"""
        self.device.close()
    
    def test_normal_measurement_function(self):
        """测试正常测量功能"""
        # 发送测量命令
        self.device.write(b'START_MEASUREMENT\n')
        
        # 等待测量完成（最多30秒）
        response = self.wait_for_response('MEASUREMENT_COMPLETE', timeout=30)
        
        # 验证测量结果
        self.assertIsNotNone(response)
        systolic, diastolic, pulse = self.parse_bp_result(response)
        
        # 验证结果在合理范围内
        self.assertGreaterEqual(systolic, 60)
        self.assertLessEqual(systolic, 250)
        self.assertGreaterEqual(diastolic, 40)
        self.assertLessEqual(diastolic, 150)
        self.assertGreater(systolic, diastolic)
        self.assertGreaterEqual(pulse, 40)
        self.assertLessEqual(pulse, 200)
    
    def test_measurement_history_function(self):
        """测试测量历史记录功能"""
        # 执行多次测量
        for i in range(3):
            self.device.write(b'START_MEASUREMENT\n')
            self.wait_for_response('MEASUREMENT_COMPLETE', timeout=30)
            time.sleep(2)
        
        # 查询历史记录
        self.device.write(b'GET_HISTORY\n')
        response = self.device.readline().decode('utf-8')
        
        # 验证历史记录
        self.assertIn('HISTORY', response)
        history_count = self.parse_history_count(response)
        self.assertGreaterEqual(history_count, 3)
    
    def test_alarm_function(self):
        """测试报警功能"""
        # 设置报警阈值
        self.device.write(b'SET_ALARM_THRESHOLD:SYS=160,DIA=100\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('OK', response)
        
        # 模拟高血压测量
        self.device.write(b'SIMULATE_BP:SYS=170,DIA=110\n')
        self.device.write(b'START_MEASUREMENT\n')
        
        # 验证报警触发
        response = self.wait_for_response('ALARM_TRIGGERED', timeout=5)
        self.assertIsNotNone(response)
    
    def test_user_settings_function(self):
        """测试用户设置功能"""
        # 设置用户信息
        self.device.write(b'SET_USER:NAME=Test,AGE=45\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('OK', response)
        
        # 读取用户信息
        self.device.write(b'GET_USER\n')
        response = self.device.readline().decode('utf-8')
        
        # 验证设置已保存
        self.assertIn('NAME=Test', response)
        self.assertIn('AGE=45', response)
    
    def test_error_handling_function(self):
        """测试错误处理功能"""
        # 模拟传感器故障
        self.device.write(b'SIMULATE_SENSOR_FAULT\n')
        
        # 尝试测量
        self.device.write(b'START_MEASUREMENT\n')
        
        # 验证错误处理
        response = self.device.readline().decode('utf-8')
        self.assertIn('ERROR', response)
        self.assertIn('SENSOR_FAULT', response)
        
        # 验证系统仍可操作
        self.device.write(b'CLEAR_FAULT\n')
        self.device.write(b'GET_STATUS\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('READY', response)
    
    # 辅助方法
    def wait_for_response(self, expected_text, timeout=10):
        """等待特定响应"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.device.in_waiting:
                response = self.device.readline().decode('utf-8')
                if expected_text in response:
                    return response
            time.sleep(0.1)
        return None
    
    def parse_bp_result(self, response):
        """解析血压结果"""
        # 格式: "MEASUREMENT_COMPLETE:SYS=120,DIA=80,PULSE=75"
        parts = response.split(':')[1].split(',')
        systolic = int(parts[0].split('=')[1])
        diastolic = int(parts[1].split('=')[1])
        pulse = int(parts[2].split('=')[1])
        return systolic, diastolic, pulse
    
    def parse_history_count(self, response):
        """解析历史记录数量"""
        # 格式: "HISTORY:COUNT=5"
        count_str = response.split('COUNT=')[1].split(',')[0]
        return int(count_str)
    
    def clear_device_state(self):
        """清除设备状态"""
        self.device.write(b'RESET\n')
        time.sleep(1)

if __name__ == '__main__':
    unittest.main()
```

**代码说明**：
- 测试完整的用户功能
- 使用真实设备或模拟器
- 验证端到端功能流程
- 测试正常和异常情况


#### 2. 性能测试（Performance Testing）

**定义**：验证系统在特定负载下的性能指标。

**测试内容**：
- 响应时间
- 吞吐量
- 资源使用率
- 并发处理能力
- 稳定性

**示例：ECG监护系统性能测试**

```python
import time
import psutil
import threading

class ECGSystemPerformanceTest(unittest.TestCase):
    """ECG监护系统性能测试"""
    
    def test_response_time(self):
        """测试响应时间"""
        response_times = []
        
        # 执行100次测量
        for i in range(100):
            start_time = time.time()
            
            # 发送命令
            self.device.write(b'GET_ECG_DATA\n')
            
            # 等待响应
            response = self.device.readline()
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # 转换为毫秒
            response_times.append(response_time)
        
        # 计算统计数据
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # 验证性能要求
        self.assertLess(avg_response_time, 100, "平均响应时间应小于100ms")
        self.assertLess(max_response_time, 200, "最大响应时间应小于200ms")
        
        print(f"平均响应时间: {avg_response_time:.2f}ms")
        print(f"最大响应时间: {max_response_time:.2f}ms")
    
    def test_throughput(self):
        """测试吞吐量"""
        duration = 60  # 测试60秒
        start_time = time.time()
        sample_count = 0
        
        while time.time() - start_time < duration:
            self.device.write(b'GET_ECG_SAMPLE\n')
            response = self.device.readline()
            if response:
                sample_count += 1
        
        # 计算吞吐量（样本/秒）
        throughput = sample_count / duration
        
        # 验证吞吐量要求（至少250样本/秒）
        self.assertGreaterEqual(throughput, 250, 
                               "吞吐量应至少250样本/秒")
        
        print(f"吞吐量: {throughput:.2f} 样本/秒")
    
    def test_cpu_usage(self):
        """测试CPU使用率"""
        # 启动监测
        self.device.write(b'START_MONITORING\n')
        time.sleep(2)
        
        # 监测CPU使用率
        cpu_samples = []
        for i in range(30):
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_samples.append(cpu_percent)
        
        avg_cpu = sum(cpu_samples) / len(cpu_samples)
        max_cpu = max(cpu_samples)
        
        # 验证CPU使用率要求
        self.assertLess(avg_cpu, 50, "平均CPU使用率应小于50%")
        self.assertLess(max_cpu, 80, "峰值CPU使用率应小于80%")
        
        print(f"平均CPU使用率: {avg_cpu:.2f}%")
        print(f"峰值CPU使用率: {max_cpu:.2f}%")
    
    def test_memory_usage(self):
        """测试内存使用"""
        # 获取进程
        process = psutil.Process()
        
        # 启动监测
        self.device.write(b'START_MONITORING\n')
        time.sleep(2)
        
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 运行一段时间
        time.sleep(60)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        # 验证内存使用
        self.assertLess(final_memory, 100, "内存使用应小于100MB")
        self.assertLess(memory_growth, 10, "内存增长应小于10MB")
        
        print(f"初始内存: {initial_memory:.2f}MB")
        print(f"最终内存: {final_memory:.2f}MB")
        print(f"内存增长: {memory_growth:.2f}MB")
    
    def test_concurrent_operations(self):
        """测试并发操作"""
        results = []
        errors = []
        
        def concurrent_operation(thread_id):
            try:
                for i in range(10):
                    self.device.write(f'OPERATION_{thread_id}_{i}\n'.encode())
                    response = self.device.readline()
                    if response:
                        results.append((thread_id, i))
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # 启动多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=concurrent_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证并发处理
        self.assertEqual(len(errors), 0, "不应有错误发生")
        self.assertEqual(len(results), 50, "应完成所有操作")
    
    def test_long_term_stability(self):
        """测试长期稳定性"""
        duration = 3600  # 测试1小时
        start_time = time.time()
        error_count = 0
        operation_count = 0
        
        while time.time() - start_time < duration:
            try:
                self.device.write(b'HEARTBEAT\n')
                response = self.device.readline()
                if not response or b'ERROR' in response:
                    error_count += 1
                operation_count += 1
            except Exception as e:
                error_count += 1
            
            time.sleep(1)
        
        # 计算错误率
        error_rate = (error_count / operation_count) * 100
        
        # 验证稳定性（错误率应小于0.1%）
        self.assertLess(error_rate, 0.1, "错误率应小于0.1%")
        
        print(f"总操作数: {operation_count}")
        print(f"错误数: {error_count}")
        print(f"错误率: {error_rate:.4f}%")
```

**代码说明**：
- 测试响应时间和吞吐量
- 监测资源使用情况
- 验证并发处理能力
- 测试长期稳定性


#### 3. 安全测试（Security Testing）

**定义**：验证系统的安全性，防止未授权访问和数据泄露。

**测试内容**：
- 身份认证
- 访问控制
- 数据加密
- 审计日志
- 漏洞扫描

**示例：医疗设备安全测试**

```python
class MedicalDeviceSecurityTest(unittest.TestCase):
    """医疗设备安全测试"""
    
    def test_authentication(self):
        """测试身份认证"""
        # 测试无效凭证
        self.device.write(b'LOGIN:USER=invalid,PASS=wrong\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('AUTH_FAILED', response)
        
        # 测试有效凭证
        self.device.write(b'LOGIN:USER=admin,PASS=correct\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('AUTH_SUCCESS', response)
    
    def test_access_control(self):
        """测试访问控制"""
        # 以普通用户登录
        self.login_as_user('user', 'password')
        
        # 尝试执行管理员操作
        self.device.write(b'ADMIN_COMMAND\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('ACCESS_DENIED', response)
        
        # 以管理员登录
        self.login_as_user('admin', 'admin_password')
        
        # 执行管理员操作
        self.device.write(b'ADMIN_COMMAND\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('SUCCESS', response)
    
    def test_data_encryption(self):
        """测试数据加密"""
        # 发送敏感数据
        sensitive_data = "PATIENT_ID=12345,NAME=Test"
        self.device.write(f'STORE_DATA:{sensitive_data}\n'.encode())
        
        # 读取存储的数据
        self.device.write(b'GET_RAW_DATA\n')
        response = self.device.readline().decode('utf-8')
        
        # 验证数据已加密（不应包含明文）
        self.assertNotIn('PATIENT_ID=12345', response)
        self.assertNotIn('NAME=Test', response)
        
        # 使用正确密钥解密
        self.device.write(b'GET_DECRYPTED_DATA\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('PATIENT_ID=12345', response)
    
    def test_audit_logging(self):
        """测试审计日志"""
        # 执行一些操作
        self.device.write(b'START_MEASUREMENT\n')
        self.wait_for_response('MEASUREMENT_COMPLETE')
        
        self.device.write(b'CHANGE_SETTINGS\n')
        self.wait_for_response('SETTINGS_CHANGED')
        
        # 查询审计日志
        self.device.write(b'GET_AUDIT_LOG\n')
        response = self.device.readline().decode('utf-8')
        
        # 验证日志记录
        self.assertIn('START_MEASUREMENT', response)
        self.assertIn('CHANGE_SETTINGS', response)
        self.assertIn('TIMESTAMP', response)
        self.assertIn('USER', response)
    
    def test_session_timeout(self):
        """测试会话超时"""
        # 登录
        self.login_as_user('user', 'password')
        
        # 等待超时时间
        time.sleep(301)  # 5分钟+1秒
        
        # 尝试操作
        self.device.write(b'GET_STATUS\n')
        response = self.device.readline().decode('utf-8')
        
        # 验证会话已超时
        self.assertIn('SESSION_TIMEOUT', response)
    
    def test_password_policy(self):
        """测试密码策略"""
        # 测试弱密码
        self.device.write(b'CHANGE_PASSWORD:NEW=123\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('PASSWORD_TOO_WEAK', response)
        
        # 测试强密码
        self.device.write(b'CHANGE_PASSWORD:NEW=StrongP@ss123\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('PASSWORD_CHANGED', response)
    
    def test_sql_injection_protection(self):
        """测试SQL注入防护"""
        # 尝试SQL注入
        malicious_input = "'; DROP TABLE users; --"
        self.device.write(f'SEARCH:{malicious_input}\n'.encode())
        response = self.device.readline().decode('utf-8')
        
        # 验证系统未受影响
        self.assertNotIn('ERROR', response)
        
        # 验证数据库完整性
        self.device.write(b'CHECK_DB_INTEGRITY\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('INTEGRITY_OK', response)
    
    def login_as_user(self, username, password):
        """辅助方法：用户登录"""
        self.device.write(f'LOGIN:USER={username},PASS={password}\n'.encode())
        response = self.device.readline().decode('utf-8')
        self.assertIn('AUTH_SUCCESS', response)
```

**代码说明**：
- 测试身份认证和访问控制
- 验证数据加密和审计日志
- 测试会话管理和密码策略
- 检查常见安全漏洞


#### 4. 可靠性测试（Reliability Testing）

**定义**：验证系统在规定条件下的可靠运行能力。

**测试内容**：
- 故障恢复
- 数据完整性
- 错误处理
- 容错能力
- 平均无故障时间（MTBF）

**示例：可靠性测试**

```python
class SystemReliabilityTest(unittest.TestCase):
    """系统可靠性测试"""
    
    def test_power_failure_recovery(self):
        """测试断电恢复"""
        # 启动测量
        self.device.write(b'START_MEASUREMENT\n')
        time.sleep(5)
        
        # 模拟断电
        self.simulate_power_loss()
        time.sleep(2)
        
        # 恢复供电
        self.restore_power()
        time.sleep(5)
        
        # 验证系统恢复
        self.device.write(b'GET_STATUS\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('READY', response)
        
        # 验证数据完整性
        self.device.write(b'CHECK_DATA_INTEGRITY\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('INTEGRITY_OK', response)
    
    def test_sensor_failure_handling(self):
        """测试传感器故障处理"""
        # 模拟传感器故障
        self.device.write(b'SIMULATE_SENSOR_FAULT\n')
        
        # 验证故障检测
        self.device.write(b'GET_STATUS\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('SENSOR_FAULT', response)
        
        # 验证报警触发
        self.assertIn('ALARM_ACTIVE', response)
        
        # 验证系统进入安全状态
        self.device.write(b'GET_SAFETY_STATE\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('SAFE_STATE', response)
    
    def test_data_corruption_detection(self):
        """测试数据损坏检测"""
        # 存储数据
        test_data = "MEASUREMENT:SYS=120,DIA=80"
        self.device.write(f'STORE:{test_data}\n'.encode())
        
        # 模拟数据损坏
        self.device.write(b'CORRUPT_DATA\n')
        
        # 尝试读取数据
        self.device.write(b'RETRIEVE_DATA\n')
        response = self.device.readline().decode('utf-8')
        
        # 验证检测到损坏
        self.assertIn('DATA_CORRUPTED', response)
        
        # 验证使用备份数据
        self.assertIn('USING_BACKUP', response)
    
    def test_memory_leak_detection(self):
        """测试内存泄漏"""
        process = psutil.Process()
        
        # 记录初始内存
        initial_memory = process.memory_info().rss / 1024 / 1024
        
        # 执行大量操作
        for i in range(1000):
            self.device.write(b'ALLOCATE_RESOURCE\n')
            self.device.write(b'FREE_RESOURCE\n')
        
        # 强制垃圾回收
        self.device.write(b'FORCE_GC\n')
        time.sleep(5)
        
        # 记录最终内存
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        # 验证无明显内存泄漏（增长<5MB）
        self.assertLess(memory_growth, 5, 
                       f"内存增长{memory_growth:.2f}MB，可能存在内存泄漏")
    
    def test_watchdog_functionality(self):
        """测试看门狗功能"""
        # 启动系统
        self.device.write(b'START_SYSTEM\n')
        time.sleep(2)
        
        # 模拟系统挂起
        self.device.write(b'SIMULATE_HANG\n')
        
        # 等待看门狗超时（假设5秒）
        time.sleep(6)
        
        # 验证系统已重启
        self.device.write(b'GET_STATUS\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('RESTARTED_BY_WATCHDOG', response)
    
    def test_mtbf_measurement(self):
        """测试平均无故障时间"""
        test_duration = 24 * 3600  # 24小时
        start_time = time.time()
        failure_count = 0
        
        while time.time() - start_time < test_duration:
            # 执行操作
            self.device.write(b'HEARTBEAT\n')
            response = self.device.readline()
            
            # 检测故障
            if not response or b'FAILURE' in response:
                failure_count += 1
                # 记录故障时间
                failure_time = time.time() - start_time
                print(f"故障发生在 {failure_time/3600:.2f} 小时")
            
            time.sleep(60)  # 每分钟检查一次
        
        # 计算MTBF
        if failure_count > 0:
            mtbf = test_duration / failure_count / 3600  # 小时
            print(f"MTBF: {mtbf:.2f} 小时")
            
            # 验证MTBF要求（例如：>1000小时）
            self.assertGreater(mtbf, 1000, "MTBF应大于1000小时")
        else:
            print("测试期间无故障发生")
```

**代码说明**：
- 测试故障恢复能力
- 验证数据完整性保护
- 检测内存泄漏
- 测试看门狗功能
- 测量平均无故障时间


#### 5. 可用性测试（Usability Testing）

**定义**：验证系统的易用性和用户体验。

**测试内容**：
- 用户界面友好性
- 操作流程合理性
- 错误提示清晰性
- 学习曲线
- 用户满意度

**示例：可用性测试**

```python
class SystemUsabilityTest(unittest.TestCase):
    """系统可用性测试"""
    
    def test_startup_time(self):
        """测试启动时间"""
        # 重启设备
        self.device.write(b'RESTART\n')
        
        start_time = time.time()
        
        # 等待系统就绪
        while True:
            self.device.write(b'GET_STATUS\n')
            response = self.device.readline().decode('utf-8')
            if 'READY' in response:
                break
            time.sleep(0.5)
        
        startup_time = time.time() - start_time
        
        # 验证启动时间（应小于10秒）
        self.assertLess(startup_time, 10, 
                       f"启动时间{startup_time:.2f}秒，应小于10秒")
    
    def test_error_message_clarity(self):
        """测试错误消息清晰性"""
        # 触发各种错误
        error_scenarios = [
            (b'INVALID_COMMAND\n', '无效命令'),
            (b'START_WITHOUT_SENSOR\n', '传感器未连接'),
            (b'EXCEED_LIMIT\n', '超出限制')
        ]
        
        for command, expected_context in error_scenarios:
            self.device.write(command)
            response = self.device.readline().decode('utf-8')
            
            # 验证错误消息包含上下文信息
            self.assertIn('ERROR', response)
            # 错误消息应该是描述性的，不只是错误代码
            self.assertGreater(len(response), 20, 
                             "错误消息应该是描述性的")
    
    def test_operation_feedback(self):
        """测试操作反馈"""
        # 启动长时间操作
        self.device.write(b'START_CALIBRATION\n')
        
        # 验证立即反馈
        response = self.device.readline().decode('utf-8')
        self.assertIn('CALIBRATION_STARTED', response)
        
        # 验证进度反馈
        time.sleep(2)
        self.device.write(b'GET_PROGRESS\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('PROGRESS', response)
        
        # 验证完成反馈
        self.wait_for_response('CALIBRATION_COMPLETE', timeout=30)
    
    def test_help_information(self):
        """测试帮助信息"""
        # 请求帮助
        self.device.write(b'HELP\n')
        response = self.device.readline().decode('utf-8')
        
        # 验证帮助信息完整性
        self.assertIn('COMMANDS', response)
        self.assertIn('DESCRIPTION', response)
        
        # 请求特定命令帮助
        self.device.write(b'HELP:START_MEASUREMENT\n')
        response = self.device.readline().decode('utf-8')
        self.assertIn('START_MEASUREMENT', response)
        self.assertIn('USAGE', response)


### 系统测试方法

#### 黑盒测试方法

**等价类划分**：

```python
def test_blood_pressure_equivalence_classes(self):
    """血压测量等价类测试"""
    # 等价类1：正常血压（90-140/60-90）
    test_cases_normal = [
        (120, 80),
        (110, 70),
        (130, 85)
    ]
    
    for sys, dia in test_cases_normal:
        result = self.measure_bp(sys, dia)
        self.assertEqual(result.category, 'NORMAL')
    
    # 等价类2：高血压（>140/>90）
    test_cases_high = [
        (150, 95),
        (160, 100),
        (180, 110)
    ]
    
    for sys, dia in test_cases_high:
        result = self.measure_bp(sys, dia)
        self.assertEqual(result.category, 'HYPERTENSION')
    
    # 等价类3：低血压（<90/<60）
    test_cases_low = [
        (85, 55),
        (80, 50),
        (75, 45)
    ]
    
    for sys, dia in test_cases_low:
        result = self.measure_bp(sys, dia)
        self.assertEqual(result.category, 'HYPOTENSION')
```

**边界值分析**：

```python
def test_blood_pressure_boundary_values(self):
    """血压测量边界值测试"""
    # 正常范围边界
    boundary_cases = [
        (89, 59, 'HYPOTENSION'),   # 刚好低于正常
        (90, 60, 'NORMAL'),         # 正常下限
        (140, 90, 'NORMAL'),        # 正常上限
        (141, 91, 'HYPERTENSION')   # 刚好高于正常
    ]
    
    for sys, dia, expected in boundary_cases:
        result = self.measure_bp(sys, dia)
        self.assertEqual(result.category, expected,
                        f"边界值({sys}/{dia})分类错误")
```

**决策表测试**：

```python
def test_alarm_decision_table(self):
    """报警决策表测试"""
    # 决策表：
    # 条件1：血压高 | T | T | F | F
    # 条件2：心率高 | T | F | T | F
    # 动作：报警   | T | T | T | F
    
    test_cases = [
        # (bp_high, hr_high, should_alarm)
        (True, True, True),    # 两者都高
        (True, False, True),   # 只有血压高
        (False, True, True),   # 只有心率高
        (False, False, False)  # 都正常
    ]
    
    for bp_high, hr_high, should_alarm in test_cases:
        self.set_bp_high(bp_high)
        self.set_hr_high(hr_high)
        
        alarm_status = self.check_alarm()
        self.assertEqual(alarm_status, should_alarm)
```

**状态转换测试**：

```python
def test_system_state_transitions(self):
    """系统状态转换测试"""
    # 状态转换图：
    # IDLE -> MEASURING -> PROCESSING -> DISPLAYING -> IDLE
    
    # 初始状态
    self.assertEqual(self.get_state(), 'IDLE')
    
    # IDLE -> MEASURING
    self.device.write(b'START_MEASUREMENT\n')
    time.sleep(0.5)
    self.assertEqual(self.get_state(), 'MEASURING')
    
    # MEASURING -> PROCESSING
    self.wait_for_state('PROCESSING', timeout=30)
    
    # PROCESSING -> DISPLAYING
    self.wait_for_state('DISPLAYING', timeout=5)
    
    # DISPLAYING -> IDLE
    time.sleep(5)
    self.assertEqual(self.get_state(), 'IDLE')
    
    # 测试非法转换
    self.assertEqual(self.get_state(), 'IDLE')
    self.device.write(b'FORCE_STATE:PROCESSING\n')
    response = self.device.readline().decode('utf-8')
    self.assertIn('INVALID_TRANSITION', response)
```


### 医疗器械软件系统测试最佳实践

#### 1. 遵循IEC 62304要求

**IEC 62304系统测试要求**：

```python
class IEC62304SystemTest(unittest.TestCase):
    """
    @test_suite: 系统测试套件
    @standard: IEC 62304:2006+AMD1:2015
    @safety_class: C
    @test_level: 系统级
    """
    
    def test_ST_001_normal_measurement_flow(self):
        """
        @test_id: ST_001
        @requirement: REQ_SYS_001
        @description: 验证正常测量流程
        @safety_class: C
        @test_type: 功能测试
        @preconditions: 系统已初始化，传感器已连接
        @test_steps:
            1. 启动测量
            2. 等待测量完成
            3. 验证结果显示
        @expected_result: 测量成功完成，结果在有效范围内
        @traceability: REQ_SYS_001 -> DES_SYS_001 -> ST_001
        """
        # 测试实现
        self.device.write(b'START_MEASUREMENT\n')
        response = self.wait_for_response('MEASUREMENT_COMPLETE', timeout=30)
        self.assertIsNotNone(response)
        
        # 验证结果
        result = self.parse_result(response)
        self.assertTrue(self.is_valid_result(result))
    
    def test_ST_002_alarm_response_time(self):
        """
        @test_id: ST_002
        @requirement: REQ_ALARM_001
        @description: 验证报警响应时间
        @safety_class: C
        @test_type: 性能测试
        @acceptance_criteria: 报警响应时间 < 500ms (IEC 60601-1-8)
        """
        start_time = time.time()
        
        # 触发报警条件
        self.inject_critical_value()
        
        # 等待报警
        alarm_triggered = self.wait_for_alarm(timeout=1)
        
        response_time = (time.time() - start_time) * 1000
        
        self.assertTrue(alarm_triggered)
        self.assertLess(response_time, 500, 
                       f"报警响应时间{response_time:.2f}ms超过500ms要求")
```

#### 2. 需求追溯矩阵

建立完整的需求追溯：

```
需求ID          | 设计ID        | 系统测试ID
----------------|--------------|------------------
REQ_SYS_001     | DES_SYS_001  | ST_001, ST_002
REQ_SYS_002     | DES_SYS_002  | ST_003
REQ_ALARM_001   | DES_ALARM_001| ST_004, ST_005
REQ_SAFETY_001  | DES_SAFETY_001| ST_006, ST_007, ST_008
```

#### 3. 风险驱动测试

基于风险分析确定测试优先级：

```python
class RiskBasedSystemTest(unittest.TestCase):
    """基于风险的系统测试"""
    
    def test_high_risk_alarm_failure(self):
        """
        @risk_id: RISK_001
        @risk_level: 高
        @hazard: 报警失败导致患者未得到及时治疗
        @severity: 严重
        @probability: 中
        @risk_control: 冗余报警机制
        """
        # 测试主报警
        self.trigger_alarm_condition()
        self.assertTrue(self.is_primary_alarm_active())
        
        # 模拟主报警失败
        self.disable_primary_alarm()
        
        # 验证备用报警激活
        self.assertTrue(self.is_backup_alarm_active())
    
    def test_medium_risk_data_loss(self):
        """
        @risk_id: RISK_002
        @risk_level: 中
        @hazard: 测量数据丢失
        @severity: 中
        @probability: 低
        @risk_control: 数据备份机制
        """
        # 存储数据
        test_data = self.generate_test_data()
        self.store_data(test_data)
        
        # 模拟存储故障
        self.simulate_storage_failure()
        
        # 验证数据可从备份恢复
        recovered_data = self.recover_from_backup()
        self.assertEqual(test_data, recovered_data)
```

#### 4. 环境测试

测试不同环境条件下的系统行为：

```python
class EnvironmentalSystemTest(unittest.TestCase):
    """环境测试"""
    
    def test_temperature_range(self):
        """测试温度范围（IEC 60601-1）"""
        # 工作温度范围：10°C - 40°C
        test_temperatures = [10, 15, 25, 35, 40]
        
        for temp in test_temperatures:
            self.set_chamber_temperature(temp)
            time.sleep(300)  # 等待温度稳定
            
            # 执行功能测试
            result = self.perform_measurement()
            self.assertTrue(result.success, 
                          f"在{temp}°C时测量失败")
    
    def test_humidity_range(self):
        """测试湿度范围"""
        # 相对湿度：30% - 75%
        test_humidity = [30, 50, 75]
        
        for humidity in test_humidity:
            self.set_chamber_humidity(humidity)
            time.sleep(300)
            
            result = self.perform_measurement()
            self.assertTrue(result.success,
                          f"在{humidity}%湿度时测量失败")
    
    def test_power_supply_variation(self):
        """测试电源电压变化"""
        # 电源电压：±10%
        nominal_voltage = 12.0
        test_voltages = [10.8, 12.0, 13.2]  # -10%, 0%, +10%
        
        for voltage in test_voltages:
            self.set_supply_voltage(voltage)
            time.sleep(10)
            
            result = self.perform_measurement()
            self.assertTrue(result.success,
                          f"在{voltage}V时测量失败")
```

#### 5. 电磁兼容性（EMC）测试

```python
class EMCSystemTest(unittest.TestCase):
    """电磁兼容性测试（IEC 60601-1-2）"""
    
    def test_esd_immunity(self):
        """测试静电放电抗扰度"""
        # IEC 61000-4-2: ±8kV接触放电，±15kV空气放电
        
        # 执行正常操作
        self.start_measurement()
        
        # 施加ESD
        self.apply_esd(contact=8000, air=15000)
        
        # 验证系统继续正常工作
        result = self.get_measurement_result()
        self.assertTrue(result.valid)
        self.assertFalse(self.has_error())
    
    def test_rf_immunity(self):
        """测试射频电磁场抗扰度"""
        # IEC 61000-4-3: 10 V/m
        
        self.start_measurement()
        
        # 施加RF场
        self.apply_rf_field(field_strength=10)  # V/m
        
        # 验证测量准确性
        result = self.get_measurement_result()
        self.assertTrue(result.valid)
        self.assertLess(result.error_percentage, 5)
```


### 系统测试工具

#### 1. 自动化测试框架

**pytest + pytest-html**：

```python
# conftest.py - pytest配置
import pytest
import serial

@pytest.fixture(scope="session")
def device():
    """设备连接fixture"""
    dev = serial.Serial('COM3', 115200, timeout=10)
    yield dev
    dev.close()

@pytest.fixture(scope="function")
def reset_device(device):
    """每个测试前重置设备"""
    device.write(b'RESET\n')
    time.sleep(2)

# pytest.ini - pytest配置文件
[pytest]
markers =
    functional: 功能测试
    performance: 性能测试
    security: 安全测试
    reliability: 可靠性测试
    smoke: 冒烟测试
    regression: 回归测试

# 运行测试并生成HTML报告
# pytest --html=report.html --self-contained-html
```

#### 2. Robot Framework

```robot
*** Settings ***
Library    SerialLibrary
Library    DateTime
Suite Setup    Connect To Device
Suite Teardown    Disconnect From Device

*** Variables ***
${DEVICE_PORT}    COM3
${BAUD_RATE}      115200
${TIMEOUT}        10

*** Test Cases ***
System Functional Test Suite
    [Documentation]    完整的系统功能测试套件
    [Tags]    functional    system
    
    Test Normal Measurement
    Test Alarm Functionality
    Test Data Storage
    Test User Settings

Test Normal Measurement
    [Documentation]    测试正常测量流程
    Send Command    START_MEASUREMENT
    ${response}=    Wait For Response    MEASUREMENT_COMPLETE    timeout=30
    Should Contain    ${response}    SUCCESS
    ${result}=    Parse Measurement Result    ${response}
    Validate Measurement Range    ${result}

Test Alarm Functionality
    [Documentation]    测试报警功能
    Set Alarm Threshold    SYS=160    DIA=100
    Simulate High Blood Pressure    SYS=170    DIA=110
    ${alarm}=    Wait For Alarm    timeout=5
    Should Be True    ${alarm}

*** Keywords ***
Connect To Device
    Open Serial Port    ${DEVICE_PORT}    ${BAUD_RATE}
    Sleep    2s

Send Command
    [Arguments]    ${command}
    Write Data    ${command}\n

Wait For Response
    [Arguments]    ${expected}    ${timeout}=10
    ${response}=    Read Until    ${expected}    timeout=${timeout}
    [Return]    ${response}

Validate Measurement Range
    [Arguments]    ${result}
    Should Be True    ${result.systolic} >= 60
    Should Be True    ${result.systolic} <= 250
    Should Be True    ${result.diastolic} >= 40
    Should Be True    ${result.diastolic} <= 150
```

#### 3. 性能测试工具

**Locust - 负载测试**：

```python
from locust import User, task, between
import serial

class MedicalDeviceUser(User):
    """医疗设备负载测试"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """用户启动时连接设备"""
        self.device = serial.Serial('COM3', 115200, timeout=5)
    
    @task(3)
    def measure_blood_pressure(self):
        """测量血压（权重3）"""
        start_time = time.time()
        
        try:
            self.device.write(b'START_MEASUREMENT\n')
            response = self.device.readline()
            
            response_time = (time.time() - start_time) * 1000
            
            if b'MEASUREMENT_COMPLETE' in response:
                self.environment.events.request.fire(
                    request_type="MEASURE",
                    name="Blood Pressure Measurement",
                    response_time=response_time,
                    response_length=len(response),
                    exception=None,
                    context={}
                )
            else:
                raise Exception("Measurement failed")
        except Exception as e:
            self.environment.events.request.fire(
                request_type="MEASURE",
                name="Blood Pressure Measurement",
                response_time=0,
                response_length=0,
                exception=e,
                context={}
            )
    
    @task(1)
    def get_history(self):
        """获取历史记录（权重1）"""
        start_time = time.time()
        
        self.device.write(b'GET_HISTORY\n')
        response = self.device.readline()
        
        response_time = (time.time() - start_time) * 1000
        
        self.environment.events.request.fire(
            request_type="QUERY",
            name="Get History",
            response_time=response_time,
            response_length=len(response),
            exception=None,
            context={}
        )
```

#### 4. 持续集成配置

**GitHub Actions**：

```yaml
name: System Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨2点运行

jobs:
  system-test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-html pytest-cov
    
    - name: Run smoke tests
      run: |
        pytest tests/system/ -m smoke --html=smoke_report.html
    
    - name: Run functional tests
      run: |
        pytest tests/system/ -m functional --html=functional_report.html
    
    - name: Run performance tests
      if: github.event_name == 'schedule'
      run: |
        pytest tests/system/ -m performance --html=performance_report.html
    
    - name: Run security tests
      run: |
        pytest tests/system/ -m security --html=security_report.html
    
    - name: Generate coverage report
      run: |
        pytest tests/system/ --cov=src --cov-report=html
    
    - name: Upload test reports
      if: always()
      uses: actions/upload-artifact@v2
      with:
        name: test-reports
        path: |
          *_report.html
          htmlcov/
    
    - name: Check test results
      run: |
        if [ $? -ne 0 ]; then
          echo "System tests failed"
          exit 1
        fi
```


### 常见陷阱

!!! warning "注意事项"
    
    **1. 测试环境不真实**
    ```python
    # 错误：使用模拟器进行所有测试
    def test_with_simulator_only(self):
        simulator = DeviceSimulator()
        result = simulator.measure()
        # 模拟器可能隐藏真实硬件问题
    
    # 正确：在真实设备上测试
    def test_with_real_device(self):
        real_device = RealDevice('COM3')
        result = real_device.measure()
        # 发现真实硬件问题
    ```
    
    **2. 忽略边界条件**
    ```python
    # 错误：只测试正常情况
    def test_incomplete(self):
        result = measure_bp(120, 80)
        self.assertTrue(result.valid)
        # 没有测试边界和异常情况
    
    # 正确：全面测试
    def test_complete(self):
        # 正常
        self.assertTrue(measure_bp(120, 80).valid)
        # 边界
        self.assertTrue(measure_bp(90, 60).valid)
        self.assertTrue(measure_bp(140, 90).valid)
        # 异常
        self.assertFalse(measure_bp(50, 30).valid)
        self.assertFalse(measure_bp(250, 150).valid)
    ```
    
    **3. 测试数据不充分**
    ```python
    # 错误：使用单一测试数据
    def test_with_single_data(self):
        result = process_ecg([100, 101, 102])
        # 不能代表真实ECG信号
    
    # 正确：使用真实或接近真实的数据
    def test_with_realistic_data(self):
        # 使用真实ECG数据库
        ecg_data = load_mit_bih_database()
        for record in ecg_data:
            result = process_ecg(record)
            self.assertTrue(result.valid)
    ```
    
    **4. 忽略性能要求**
    ```python
    # 错误：只验证功能正确性
    def test_function_only(self):
        result = calculate()
        self.assertEqual(expected, result)
        # 没有验证性能
    
    # 正确：同时验证功能和性能
    def test_function_and_performance(self):
        start = time.time()
        result = calculate()
        duration = time.time() - start
        
        self.assertEqual(expected, result)
        self.assertLess(duration, 0.1)  # 100ms要求
    ```
    
    **5. 测试不可重复**
    ```python
    # 错误：依赖外部状态
    def test_non_repeatable(self):
        # 依赖之前测试的状态
        result = get_current_state()
        # 结果不可预测
    
    # 正确：每次测试独立
    def setUp(self):
        self.reset_to_known_state()
    
    def test_repeatable(self):
        # 从已知状态开始
        result = perform_operation()
        # 结果可预测
    ```
    
    **6. 忽略并发问题**
    ```python
    # 错误：只测试单线程
    def test_single_thread(self):
        result = shared_resource.access()
        # 可能隐藏并发问题
    
    # 正确：测试并发访问
    def test_concurrent_access(self):
        threads = []
        for i in range(10):
            t = threading.Thread(
                target=shared_resource.access)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # 验证数据一致性
        self.assertTrue(shared_resource.is_consistent())
    ```
    
    **7. 测试覆盖不足**
    ```python
    # 错误：只测试主要路径
    def test_main_path_only(self):
        result = main_function(valid_input)
        self.assertTrue(result.success)
        # 没有测试错误路径
    
    # 正确：测试所有路径
    def test_all_paths(self):
        # 主要路径
        self.assertTrue(main_function(valid_input).success)
        
        # 错误路径
        self.assertFalse(main_function(None).success)
        self.assertFalse(main_function(invalid).success)
        
        # 边界情况
        self.assertTrue(main_function(min_valid).success)
        self.assertTrue(main_function(max_valid).success)
    ```


## 最佳实践

### 系统测试策略

**测试金字塔**：

```
        /\
       /  \  系统测试（少量，慢速，昂贵）
      /____\
     /      \
    / 集成测试 \ （中等数量，中等速度）
   /__________\
  /            \
 /  单元测试    \ （大量，快速，便宜）
/________________\
```

**测试优先级**：

1. **P0 - 冒烟测试**：基本功能验证
2. **P1 - 核心功能测试**：主要用例
3. **P2 - 扩展功能测试**：次要用例
4. **P3 - 边界和异常测试**：边界条件

### 测试数据管理

```python
class TestDataManager:
    """测试数据管理器"""
    
    @staticmethod
    def load_test_data(test_type):
        """加载测试数据"""
        data_files = {
            'normal_bp': 'data/normal_blood_pressure.json',
            'abnormal_bp': 'data/abnormal_blood_pressure.json',
            'ecg_normal': 'data/ecg_normal_rhythm.dat',
            'ecg_arrhythmia': 'data/ecg_arrhythmia.dat'
        }
        
        with open(data_files[test_type], 'r') as f:
            return json.load(f)
    
    @staticmethod
    def generate_test_data(pattern, count):
        """生成测试数据"""
        if pattern == 'normal_ecg':
            return generate_normal_ecg(count)
        elif pattern == 'noisy_ecg':
            return generate_noisy_ecg(count)
        # 更多模式...
```

### 测试报告

```python
class TestReporter:
    """测试报告生成器"""
    
    def generate_report(self, test_results):
        """生成测试报告"""
        report = {
            'summary': self.generate_summary(test_results),
            'details': self.generate_details(test_results),
            'coverage': self.calculate_coverage(test_results),
            'defects': self.list_defects(test_results),
            'recommendations': self.generate_recommendations(test_results)
        }
        
        return report
    
    def generate_summary(self, results):
        """生成摘要"""
        return {
            'total_tests': len(results),
            'passed': sum(1 for r in results if r.passed),
            'failed': sum(1 for r in results if not r.passed),
            'pass_rate': self.calculate_pass_rate(results),
            'execution_time': sum(r.duration for r in results)
        }
```

### 缺陷管理

```python
class DefectTracker:
    """缺陷跟踪器"""
    
    def log_defect(self, test_id, description, severity):
        """记录缺陷"""
        defect = {
            'id': self.generate_defect_id(),
            'test_id': test_id,
            'description': description,
            'severity': severity,
            'status': 'OPEN',
            'timestamp': datetime.now(),
            'environment': self.get_environment_info()
        }
        
        self.save_defect(defect)
        return defect['id']
    
    def get_defect_statistics(self):
        """获取缺陷统计"""
        defects = self.load_all_defects()
        
        return {
            'total': len(defects),
            'by_severity': self.group_by_severity(defects),
            'by_status': self.group_by_status(defects),
            'by_module': self.group_by_module(defects)
        }
```


## 实践练习

1. **基础练习**：为一个简单的温度监测系统设计系统测试计划，包括功能测试、性能测试和可靠性测试。

2. **中级练习**：实现一个血压监测系统的完整系统测试套件：
   - 功能测试：测量、历史记录、报警
   - 性能测试：响应时间、吞吐量
   - 安全测试：身份认证、数据加密
   - 可靠性测试：故障恢复、数据完整性

3. **高级练习**：为一个ECG监护系统建立完整的系统测试框架：
   - 设计测试策略和测试计划
   - 实现自动化测试脚本
   - 集成到CI/CD流程
   - 生成测试报告
   - 建立缺陷跟踪系统

4. **综合练习**：执行一个完整的系统测试周期：
   - 需求分析和测试计划
   - 测试用例设计
   - 测试环境搭建
   - 测试执行和缺陷记录
   - 测试报告和总结
   - 回归测试


## 相关资源

### 相关知识模块

- [单元测试](unit-testing.md) - 模块内部测试
- [集成测试](integration-testing.md) - 模块间接口测试
- [IEC 62304标准](../../regulatory-standards/iec-62304/index.md) - 医疗器械软件生命周期

### 深入学习

- [测试策略概述](index.md) - 测试策略整体框架
- [软件验证](../../regulatory-standards/fda-regulations/software-validation.md) - FDA软件验证要求

### 工具和框架

- [pytest](https://pytest.org/) - Python测试框架
- [Robot Framework](https://robotframework.org/) - 验收测试框架
- [Locust](https://locust.io/) - 性能测试工具
- [Selenium](https://www.selenium.dev/) - Web UI自动化测试
- [JMeter](https://jmeter.apache.org/) - 性能和负载测试


## 参考文献

1. IEC 62304:2006+AMD1:2015 - Medical device software - Software life cycle processes, Section 5.7 (Software System Testing)
2. IEC 60601-1:2005+AMD1:2012 - Medical electrical equipment - Part 1: General requirements for basic safety and essential performance
3. IEC 60601-1-2:2014 - Medical electrical equipment - Part 1-2: General requirements for basic safety and essential performance - Collateral standard: Electromagnetic disturbances
4. IEC 60601-1-8:2006+AMD1:2012 - Medical electrical equipment - Part 1-8: General requirements for basic safety and essential performance - Collateral standard: General requirements, tests and guidance for alarm systems
5. "Software Testing: A Craftsman's Approach" by Paul C. Jorgensen, Chapter 10 (System Testing)
6. "Embedded Software Development for Safety-Critical Systems" by Chris Hobbs, Chapter 9 (System Testing)
7. FDA Guidance for the Content of Premarket Submissions for Software Contained in Medical Devices (2005)
8. ISO/IEC 25010:2011 - Systems and software engineering - Systems and software Quality Requirements and Evaluation (SQuaRE)


## 自测问题

??? question "问题1：什么是系统测试？它与集成测试有什么区别？"
    **问题**：解释系统测试的定义，并说明它与集成测试的主要区别。
    
    ??? success "答案"
        **系统测试定义**：
        系统测试是在完整的、集成的系统上进行的测试，验证系统是否满足规定的需求。
        
        **主要特点**：
        - 测试完整系统
        - 基于需求规格说明
        - 黑盒测试为主
        - 在真实或模拟环境中执行
        - 验证端到端功能
        
        **与集成测试的区别**：
        
        | 维度 | 集成测试 | 系统测试 |
        |------|---------|---------|
        | 测试范围 | 模块间接口 | 完整系统 |
        | 测试基础 | 设计文档 | 需求规格 |
        | 测试方法 | 白盒/灰盒 | 黑盒为主 |
        | 测试环境 | 部分集成 | 完整系统 |
        | 测试目标 | 接口正确性 | 需求满足度 |
        | 执行时机 | 集成阶段 | 系统完成后 |
        | 测试人员 | 开发人员 | 测试人员 |
        
        **示例对比**：
        ```python
        # 集成测试：测试模块间接口
        def test_sensor_to_processor_integration(self):
            sensor_data = sensor.read()
            processed = processor.process(sensor_data)
            # 验证接口数据传递
        
        # 系统测试：测试完整功能
        def test_complete_measurement_flow(self):
            device.start_measurement()
            result = device.get_result()
            # 验证端到端功能
        ```
        
        **知识点回顾**：系统测试关注完整系统的需求满足度，集成测试关注模块间的接口正确性。

??? question "问题2：系统测试包括哪些主要类型？"
    **问题**：列举系统测试的主要类型及其测试内容。
    
    ??? success "答案"
        **系统测试主要类型**：
        
        **1. 功能测试（Functional Testing）**
        - 验证系统功能是否符合需求
        - 测试内容：
          - 用户界面功能
          - 数据处理功能
          - 业务逻辑功能
          - 输入输出功能
          - 错误处理功能
        
        **2. 性能测试（Performance Testing）**
        - 验证系统性能指标
        - 测试内容：
          - 响应时间
          - 吞吐量
          - 资源使用率
          - 并发处理能力
          - 稳定性
        
        **3. 安全测试（Security Testing）**
        - 验证系统安全性
        - 测试内容：
          - 身份认证
          - 访问控制
          - 数据加密
          - 审计日志
          - 漏洞扫描
        
        **4. 可靠性测试（Reliability Testing）**
        - 验证系统可靠运行能力
        - 测试内容：
          - 故障恢复
          - 数据完整性
          - 错误处理
          - 容错能力
          - MTBF（平均无故障时间）
        
        **5. 可用性测试（Usability Testing）**
        - 验证系统易用性
        - 测试内容：
          - 用户界面友好性
          - 操作流程合理性
          - 错误提示清晰性
          - 学习曲线
          - 用户满意度
        
        **6. 兼容性测试（Compatibility Testing）**
        - 验证系统兼容性
        - 测试内容：
          - 硬件兼容性
          - 软件兼容性
          - 操作系统兼容性
          - 浏览器兼容性
        
        **7. 环境测试（Environmental Testing）**
        - 验证不同环境条件下的系统行为
        - 测试内容：
          - 温度范围
          - 湿度范围
          - 电源电压变化
          - 电磁兼容性
        
        **医疗器械特有测试**：
        - 报警系统测试（IEC 60601-1-8）
        - 电气安全测试（IEC 60601-1）
        - EMC测试（IEC 60601-1-2）
        - 生物兼容性测试
        
        **知识点回顾**：系统测试包括多种类型，全面验证系统的功能、性能、安全、可靠性等方面。

??? question "问题3：如何为医疗器械软件设计系统测试？"
    **问题**：列举医疗器械软件系统测试的关键要点和最佳实践。
    
    ??? success "答案"
        **医疗器械软件系统测试关键要点**：
        
        **1. 遵循IEC 62304要求**
        ```python
        """
        @test_id: ST_001
        @requirement: REQ_SYS_001
        @safety_class: C
        @test_type: 功能测试
        @traceability: REQ -> DES -> TEST
        """
        ```
        
        **2. 建立需求追溯矩阵**
        ```
        需求 → 设计 → 测试用例
        确保每个需求都有对应的测试
        ```
        
        **3. 风险驱动测试**
        - 高风险功能：更多测试用例
        - 安全关键路径：100%覆盖
        - 基于风险分析确定优先级
        
        **4. 测试安全关键功能**
        ```python
        def test_alarm_response_time(self):
            # IEC 60601-1-8要求：<500ms
            response_time = measure_alarm_response()
            self.assertLess(response_time, 500)
        ```
        
        **5. 环境测试**
        - 温度范围：10°C - 40°C
        - 湿度范围：30% - 75%
        - 电源电压：±10%
        - EMC测试
        
        **6. 性能验证**
        - 响应时间要求
        - 吞吐量要求
        - 资源使用限制
        - 长期稳定性
        
        **7. 数据完整性**
        - 数据存储和恢复
        - 数据加密
        - 数据备份
        - 审计日志
        
        **8. 错误处理**
        - 传感器故障
        - 通信故障
        - 电源故障
        - 软件异常
        
        **9. 用户界面测试**
        - 操作流程
        - 错误提示
        - 报警显示
        - 可用性
        
        **10. 文档化**
        - 测试计划
        - 测试用例
        - 测试报告
        - 缺陷记录
        - 追溯矩阵
        
        **测试检查清单**：
        ```
        ☐ 所有需求都有测试用例
        ☐ 安全关键功能100%覆盖
        ☐ 性能要求已验证
        ☐ 环境测试已完成
        ☐ 报警系统已测试
        ☐ 错误处理已验证
        ☐ 数据完整性已确认
        ☐ 可用性已评估
        ☐ 测试文档已完成
        ☐ 缺陷已跟踪和解决
        ```
        
        **知识点回顾**：医疗器械软件系统测试需要遵循标准、关注安全、全面覆盖、完整文档化。

??? question "问题4：什么是黑盒测试方法？常用的黑盒测试技术有哪些？"
    **问题**：解释黑盒测试的概念，并列举常用的黑盒测试技术。
    
    ??? success "答案"
        **黑盒测试定义**：
        黑盒测试是基于需求规格说明，不考虑内部实现，只关注输入和输出的测试方法。
        
        **特点**：
        - 不需要了解内部代码
        - 基于需求规格
        - 从用户角度测试
        - 发现功能缺陷
        
        **常用黑盒测试技术**：
        
        **1. 等价类划分**
        ```python
        # 将输入域划分为等价类
        # 血压分类：低血压、正常、高血压
        test_cases = [
            (80, 50, 'HYPOTENSION'),   # 低血压
            (120, 80, 'NORMAL'),        # 正常
            (160, 100, 'HYPERTENSION')  # 高血压
        ]
        ```
        
        **2. 边界值分析**
        ```python
        # 测试边界值和边界附近的值
        boundary_cases = [
            (89, 59, 'HYPOTENSION'),   # 刚好低于正常
            (90, 60, 'NORMAL'),         # 正常下限
            (140, 90, 'NORMAL'),        # 正常上限
            (141, 91, 'HYPERTENSION')   # 刚好高于正常
        ]
        ```
        
        **3. 决策表测试**
        ```
        条件1：血压高 | T | T | F | F
        条件2：心率高 | T | F | T | F
        动作：报警   | T | T | T | F
        ```
        
        **4. 状态转换测试**
        ```
        IDLE → MEASURING → PROCESSING → DISPLAYING → IDLE
        测试所有状态转换
        ```
        
        **5. 因果图法**
        ```
        原因1 AND 原因2 → 结果1
        原因3 OR 原因4 → 结果2
        ```
        
        **6. 正交实验设计**
        ```
        减少测试用例数量
        保持测试覆盖率
        ```
        
        **7. 场景测试**
        ```python
        # 测试完整的用户场景
        def test_measurement_scenario(self):
            # 1. 用户登录
            self.login()
            # 2. 启动测量
            self.start_measurement()
            # 3. 查看结果
            result = self.get_result()
            # 4. 保存历史
            self.save_to_history()
        ```
        
        **8. 错误推测法**
        ```python
        # 基于经验预测可能的错误
        error_cases = [
            None,           # NULL指针
            "",             # 空字符串
            -1,             # 负数
            INT_MAX,        # 最大值
            "' OR '1'='1"   # SQL注入
        ]
        ```
        
        **选择建议**：
        - 功能测试：等价类划分 + 边界值分析
        - 复杂逻辑：决策表测试
        - 状态机：状态转换测试
        - 用户流程：场景测试
        
        **知识点回顾**：黑盒测试基于需求规格，使用多种技术设计测试用例，不关注内部实现。

??? question "问题5：如何建立有效的系统测试流程？"
    **问题**：描述一个完整的系统测试流程和关键活动。
    
    ??? success "答案"
        **系统测试流程**：
        
        **1. 测试计划阶段**
        - 分析需求规格说明
        - 识别测试范围和目标
        - 确定测试策略
        - 评估资源和时间
        - 识别风险
        
        **2. 测试设计阶段**
        - 设计测试用例
        - 准备测试数据
        - 建立追溯矩阵
        - 评审测试用例
        
        **3. 测试环境准备**
        - 搭建测试环境
        - 配置测试工具
        - 准备测试设备
        - 验证环境就绪
        
        **4. 测试执行阶段**
        - 执行测试用例
        - 记录测试结果
        - 报告缺陷
        - 跟踪缺陷修复
        
        **5. 测试评估阶段**
        - 分析测试结果
        - 计算覆盖率
        - 评估质量指标
        - 生成测试报告
        
        **6. 回归测试**
        - 验证缺陷修复
        - 确保无新缺陷
        - 重新执行关键测试
        
        **7. 测试总结**
        - 总结经验教训
        - 更新测试资产
        - 归档测试文档
        
        **关键活动**：
        
        ```python
        class SystemTestProcess:
            def execute_test_cycle(self):
                # 1. 准备
                self.prepare_test_environment()
                self.load_test_data()
                
                # 2. 执行
                results = []
                for test_case in self.test_cases:
                    result = self.execute_test(test_case)
                    results.append(result)
                    
                    if not result.passed:
                        self.log_defect(test_case, result)
                
                # 3. 报告
                report = self.generate_report(results)
                self.publish_report(report)
                
                # 4. 评估
                if self.meets_exit_criteria(results):
                    return "PASS"
                else:
                    return "FAIL"
        ```
        
        **退出标准**：
        ```
        ☐ 所有P0/P1测试用例通过
        ☐ 无严重缺陷未解决
        ☐ 测试覆盖率达标
        ☐ 性能指标满足要求
        ☐ 测试文档完整
        ```
        
        **持续改进**：
        - 分析测试效率
        - 优化测试用例
        - 改进测试工具
        - 培训测试人员
        
        **知识点回顾**：系统测试流程包括计划、设计、执行、评估等阶段，需要建立明确的标准和持续改进机制。
