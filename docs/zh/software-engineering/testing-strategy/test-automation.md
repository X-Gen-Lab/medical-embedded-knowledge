---
title: 测试自动化
difficulty: intermediate
estimated_time: 2-3小时
---

# 测试自动化

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

测试自动化是使用软件工具自动执行测试用例、比较实际结果与预期结果、生成测试报告的过程。对于医疗设备软件，自动化测试可以提高测试效率、确保测试一致性、支持持续集成和快速迭代。

## 为什么需要测试自动化？

### 医疗设备软件的挑战

- **频繁的回归测试**: 每次代码变更都需要验证现有功能
- **复杂的测试场景**: 需要测试大量的输入组合和边界条件
- **监管要求**: 需要可追溯的测试记录和文档
- **质量保证**: 确保每个版本都经过充分测试

### 自动化的优势

| 方面 | 手动测试 | 自动化测试 |
|------|---------|-----------|
| 执行速度 | 慢 | 快 |
| 可重复性 | 低 | 高 |
| 人为错误 | 高 | 低 |
| 成本（长期） | 高 | 低 |
| 覆盖率 | 有限 | 广泛 |
| CI/CD集成 | 困难 | 容易 |

## 测试自动化策略

### 测试金字塔

```
        /\
       /  \  UI测试 (10%)
      /____\  手动/自动化
     /      \
    / API测试 \ (30%)
   /___________\  自动化
  /             \
 /   单元测试    \ (60%)
/_________________\  自动化
```


### 自动化测试框架选择

#### Python测试框架

**pytest** - 推荐用于医疗设备软件

```python
# test_ecg_processor.py
import pytest
from medical_device.ecg import ECGProcessor

class TestECGProcessor:
    """ECG处理器测试"""
    
    @pytest.fixture
    def processor(self):
        """测试夹具 - 创建处理器实例"""
        return ECGProcessor(sample_rate=500)
    
    @pytest.fixture
    def sample_ecg_data(self):
        """测试夹具 - 生成样本ECG数据"""
        import numpy as np
        # 生成60秒的模拟ECG数据
        t = np.linspace(0, 60, 30000)
        ecg = np.sin(2 * np.pi * 1.2 * t)  # 72 bpm
        return ecg
    
    def test_heart_rate_calculation(self, processor, sample_ecg_data):
        """测试心率计算"""
        heart_rate = processor.calculate_heart_rate(sample_ecg_data)
        assert 70 <= heart_rate <= 75, f"心率应在70-75之间，实际: {heart_rate}"
    
    def test_r_peak_detection(self, processor, sample_ecg_data):
        """测试R波检测"""
        r_peaks = processor.detect_r_peaks(sample_ecg_data)
        assert len(r_peaks) > 0, "应该检测到R波"
        assert len(r_peaks) >= 70, "60秒应检测到至少70个R波"
    
    @pytest.mark.parametrize("noise_level", [0.1, 0.2, 0.5])
    def test_noise_tolerance(self, processor, sample_ecg_data, noise_level):
        """测试噪声容忍度"""
        import numpy as np
        noisy_data = sample_ecg_data + np.random.normal(0, noise_level, len(sample_ecg_data))
        heart_rate = processor.calculate_heart_rate(noisy_data)
        assert 60 <= heart_rate <= 85, f"噪声水平{noise_level}下心率计算失败"
    
    def test_invalid_input(self, processor):
        """测试无效输入处理"""
        with pytest.raises(ValueError):
            processor.calculate_heart_rate([])  # 空数据
        
        with pytest.raises(ValueError):
            processor.calculate_heart_rate(None)  # None
    
    @pytest.mark.slow
    def test_long_duration_processing(self, processor):
        """测试长时间数据处理"""
        import numpy as np
        # 24小时的数据
        long_data = np.random.randn(43200000)
        result = processor.process_continuous(long_data)
        assert result is not None

# pytest配置文件
# pytest.ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    critical: marks tests as critical for patient safety

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# 覆盖率配置
addopts = 
    --cov=medical_device
    --cov-report=html
    --cov-report=term
    --cov-fail-under=80
    --strict-markers
    -v
```

#### Java测试框架

**JUnit 5 + Mockito**

```java
// ECGProcessorTest.java
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@DisplayName("ECG处理器测试")
class ECGProcessorTest {
    
    private ECGProcessor processor;
    
    @Mock
    private DataLogger logger;
    
    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        processor = new ECGProcessor(500, logger);
    }
    
    @Test
    @DisplayName("应该正确计算心率")
    @Tag("unit")
    void shouldCalculateHeartRateCorrectly() {
        // Arrange
        double[] ecgData = generateSampleECG(60, 72);
        
        // Act
        int heartRate = processor.calculateHeartRate(ecgData);
        
        // Assert
        assertTrue(heartRate >= 70 && heartRate <= 75,
            "心率应在70-75之间，实际: " + heartRate);
        verify(logger).log(contains("Heart rate calculated"));
    }
    
    @ParameterizedTest
    @ValueSource(ints = {60, 80, 100, 120})
    @DisplayName("应该处理不同心率")
    void shouldHandleDifferentHeartRates(int expectedHR) {
        double[] ecgData = generateSampleECG(60, expectedHR);
        int actualHR = processor.calculateHeartRate(ecgData);
        assertEquals(expectedHR, actualHR, 5);
    }
    
    @Test
    @DisplayName("应该抛出异常当输入为空")
    void shouldThrowExceptionForEmptyInput() {
        assertThrows(IllegalArgumentException.class, () -> {
            processor.calculateHeartRate(new double[0]);
        });
    }
    
    @RepeatedTest(10)
    @DisplayName("应该产生一致的结果")
    void shouldProduceConsistentResults() {
        double[] ecgData = generateSampleECG(60, 72);
        int firstResult = processor.calculateHeartRate(ecgData);
        int secondResult = processor.calculateHeartRate(ecgData);
        assertEquals(firstResult, secondResult);
    }
    
    @Nested
    @DisplayName("R波检测测试")
    class RPeakDetectionTests {
        
        @Test
        @DisplayName("应该检测到所有R波")
        void shouldDetectAllRPeaks() {
            double[] ecgData = generateSampleECG(60, 72);
            List<Integer> rPeaks = processor.detectRPeaks(ecgData);
            assertTrue(rPeaks.size() >= 70);
        }
        
        @Test
        @DisplayName("R波间隔应该合理")
        void rPeakIntervalsShouldBeReasonable() {
            double[] ecgData = generateSampleECG(60, 72);
            List<Integer> rPeaks = processor.detectRPeaks(ecgData);
            
            for (int i = 1; i < rPeaks.size(); i++) {
                int interval = rPeaks.get(i) - rPeaks.get(i-1);
                assertTrue(interval > 200 && interval < 600,
                    "R-R间隔应该合理");
            }
        }
    }
    
    private double[] generateSampleECG(int durationSeconds, int heartRate) {
        // 生成模拟ECG数据
        int sampleRate = 500;
        int numSamples = durationSeconds * sampleRate;
        double[] data = new double[numSamples];
        
        double frequency = heartRate / 60.0;
        for (int i = 0; i < numSamples; i++) {
            double t = (double) i / sampleRate;
            data[i] = Math.sin(2 * Math.PI * frequency * t);
        }
        
        return data;
    }
}
```


## CI/CD集成

### GitHub Actions工作流

```yaml
# .github/workflows/medical-device-ci.yml
name: Medical Device CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: '3.9'
  
jobs:
  # 单元测试
  unit-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: 设置Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: 安装依赖
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: 运行单元测试
      run: |
        pytest tests/unit \
          --cov=medical_device \
          --cov-report=xml \
          --cov-report=html \
          --junitxml=junit/test-results.xml
    
    - name: 上传覆盖率报告
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
    
    - name: 发布测试结果
      uses: EnricoMi/publish-unit-test-result-action@v2
      if: always()
      with:
        files: junit/test-results.xml
  
  # 集成测试
  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: medical_device_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: 设置Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: 安装依赖
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: 运行集成测试
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/medical_device_test
        REDIS_URL: redis://localhost:6379
      run: |
        pytest tests/integration -v --tb=short
  
  # 性能测试
  performance-tests:
    runs-on: ubuntu-latest
    needs: integration-tests
    
    steps:
    - uses: actions/checkout@v3
    
    - name: 设置Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: 安装依赖
      run: |
        pip install -r requirements.txt
        pip install locust
    
    - name: 运行性能测试
      run: |
        locust -f tests/performance/locustfile.py \
          --headless \
          --users 100 \
          --spawn-rate 10 \
          --run-time 5m \
          --host https://staging.medical-device.com \
          --html performance-report.html
    
    - name: 上传性能报告
      uses: actions/upload-artifact@v3
      with:
        name: performance-report
        path: performance-report.html
  
  # 安全扫描
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: 运行Bandit安全扫描
      run: |
        pip install bandit
        bandit -r medical_device/ -f json -o bandit-report.json
    
    - name: 运行Safety依赖检查
      run: |
        pip install safety
        safety check --json > safety-report.json
    
    - name: 上传安全报告
      uses: actions/upload-artifact@v3
      with:
        name: security-reports
        path: |
          bandit-report.json
          safety-report.json
  
  # 构建Docker镜像
  build-docker:
    runs-on: ubuntu-latest
    needs: [unit-tests, integration-tests, security-scan]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: 设置Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: 登录Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
    
    - name: 构建并推送
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: |
          medical-device:${{ github.sha }}
          medical-device:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: 扫描Docker镜像
      run: |
        docker run --rm \
          -v /var/run/docker.sock:/var/run/docker.sock \
          aquasec/trivy image medical-device:${{ github.sha }}
```

### GitLab CI/CD配置

```yaml
# .gitlab-ci.yml
stages:
  - test
  - security
  - build
  - deploy

variables:
  PYTHON_VERSION: "3.9"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

before_script:
  - python -V
  - pip install virtualenv
  - virtualenv venv
  - source venv/bin/activate
  - pip install -r requirements.txt

# 单元测试
unit-test:
  stage: test
  script:
    - pip install pytest pytest-cov
    - pytest tests/unit --cov=medical_device --cov-report=term --cov-report=xml
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - htmlcov/
    expire_in: 1 week

# 集成测试
integration-test:
  stage: test
  services:
    - postgres:13
    - redis:6
  variables:
    POSTGRES_DB: medical_device_test
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: postgres
    DATABASE_URL: postgresql://postgres:postgres@postgres:5432/medical_device_test
  script:
    - pytest tests/integration -v
  only:
    - merge_requests
    - main

# 代码质量检查
code-quality:
  stage: test
  script:
    - pip install pylint flake8 mypy
    - pylint medical_device/
    - flake8 medical_device/
    - mypy medical_device/
  allow_failure: true

# 安全扫描
security-sast:
  stage: security
  script:
    - pip install bandit
    - bandit -r medical_device/ -f json -o bandit-report.json
  artifacts:
    reports:
      sast: bandit-report.json

# 依赖扫描
dependency-scanning:
  stage: security
  script:
    - pip install safety
    - safety check --json > safety-report.json
  artifacts:
    paths:
      - safety-report.json

# 构建
build:
  stage: build
  script:
    - python setup.py bdist_wheel
  artifacts:
    paths:
      - dist/
    expire_in: 1 month
  only:
    - tags
    - main

# 部署到测试环境
deploy-staging:
  stage: deploy
  script:
    - echo "Deploying to staging environment"
    - pip install dist/*.whl
    - python scripts/deploy_staging.py
  environment:
    name: staging
    url: https://staging.medical-device.com
  only:
    - develop

# 部署到生产环境
deploy-production:
  stage: deploy
  script:
    - echo "Deploying to production environment"
    - pip install dist/*.whl
    - python scripts/deploy_production.py
  environment:
    name: production
    url: https://medical-device.com
  when: manual
  only:
    - tags
```


## 测试数据管理

### 测试数据生成

```python
# test_data_factory.py
from faker import Faker
import random
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List

fake = Faker('zh_CN')

@dataclass
class PatientData:
    """患者数据"""
    patient_id: str
    name: str
    gender: str
    birth_date: str
    phone: str
    address: str

@dataclass
class VitalSigns:
    """生命体征数据"""
    patient_id: str
    timestamp: datetime
    heart_rate: int
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    temperature: float
    spo2: int

class TestDataFactory:
    """测试数据工厂"""
    
    @staticmethod
    def create_patient(patient_id=None) -> PatientData:
        """创建患者数据"""
        return PatientData(
            patient_id=patient_id or f"P{random.randint(100000, 999999)}",
            name=fake.name(),
            gender=random.choice(['M', 'F']),
            birth_date=fake.date_of_birth(minimum_age=18, maximum_age=90).isoformat(),
            phone=fake.phone_number(),
            address=fake.address()
        )
    
    @staticmethod
    def create_vital_signs(patient_id: str, timestamp=None) -> VitalSigns:
        """创建生命体征数据"""
        return VitalSigns(
            patient_id=patient_id,
            timestamp=timestamp or datetime.now(),
            heart_rate=random.randint(60, 100),
            blood_pressure_systolic=random.randint(110, 140),
            blood_pressure_diastolic=random.randint(70, 90),
            temperature=round(random.uniform(36.0, 37.5), 1),
            spo2=random.randint(95, 100)
        )
    
    @staticmethod
    def create_ecg_data(duration_seconds=60, sample_rate=500, heart_rate=72):
        """创建ECG数据"""
        import numpy as np
        num_samples = duration_seconds * sample_rate
        t = np.linspace(0, duration_seconds, num_samples)
        frequency = heart_rate / 60.0
        
        # 生成基础正弦波
        ecg = np.sin(2 * np.pi * frequency * t)
        
        # 添加噪声
        noise = np.random.normal(0, 0.1, num_samples)
        ecg += noise
        
        return ecg
    
    @staticmethod
    def create_batch_patients(count=100) -> List[PatientData]:
        """批量创建患者数据"""
        return [TestDataFactory.create_patient() for _ in range(count)]
    
    @staticmethod
    def create_patient_history(patient_id: str, days=30) -> List[VitalSigns]:
        """创建患者历史数据"""
        history = []
        start_date = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            for hour in range(0, 24, 4):  # 每4小时一次测量
                timestamp = start_date + timedelta(days=day, hours=hour)
                history.append(
                    TestDataFactory.create_vital_signs(patient_id, timestamp)
                )
        
        return history

# 使用示例
def test_patient_data_processing():
    """测试患者数据处理"""
    # 创建测试数据
    patient = TestDataFactory.create_patient()
    vitals = TestDataFactory.create_vital_signs(patient.patient_id)
    
    # 执行测试
    processor = PatientDataProcessor()
    result = processor.process(patient, vitals)
    
    assert result is not None
    assert result.patient_id == patient.patient_id
```

### 测试数据库管理

```python
# test_database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from medical_device.models import Base, Patient, VitalSigns

@pytest.fixture(scope='session')
def test_engine():
    """创建测试数据库引擎"""
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope='function')
def db_session(test_engine):
    """创建数据库会话"""
    Session = sessionmaker(bind=test_engine)
    session = Session()
    
    yield session
    
    # 清理
    session.rollback()
    session.close()

@pytest.fixture
def sample_patient(db_session):
    """创建样本患者"""
    patient = Patient(
        patient_id='P123456',
        name='张三',
        gender='M',
        birth_date='1980-01-01'
    )
    db_session.add(patient)
    db_session.commit()
    return patient

def test_patient_crud(db_session, sample_patient):
    """测试患者CRUD操作"""
    # Read
    patient = db_session.query(Patient).filter_by(
        patient_id='P123456'
    ).first()
    assert patient is not None
    assert patient.name == '张三'
    
    # Update
    patient.name = '李四'
    db_session.commit()
    
    updated_patient = db_session.query(Patient).filter_by(
        patient_id='P123456'
    ).first()
    assert updated_patient.name == '李四'
    
    # Delete
    db_session.delete(patient)
    db_session.commit()
    
    deleted_patient = db_session.query(Patient).filter_by(
        patient_id='P123456'
    ).first()
    assert deleted_patient is None
```

## 回归测试自动化

### 回归测试套件

```python
# regression_test_suite.py
import pytest
from medical_device import ECGProcessor, PatientDataManager
from test_data_factory import TestDataFactory

class RegressionTestSuite:
    """回归测试套件"""
    
    @pytest.mark.regression
    class TestECGProcessing:
        """ECG处理回归测试"""
        
        def test_heart_rate_calculation_accuracy(self):
            """测试心率计算准确性 - 回归测试"""
            processor = ECGProcessor(sample_rate=500)
            
            # 测试已知的心率值
            test_cases = [
                (60, 60),   # 60 bpm
                (72, 72),   # 72 bpm
                (100, 100), # 100 bpm
                (120, 120)  # 120 bpm
            ]
            
            for expected_hr, input_hr in test_cases:
                ecg_data = TestDataFactory.create_ecg_data(
                    duration_seconds=60,
                    heart_rate=input_hr
                )
                calculated_hr = processor.calculate_heart_rate(ecg_data)
                assert abs(calculated_hr - expected_hr) <= 2, \
                    f"心率计算偏差过大: 期望{expected_hr}, 实际{calculated_hr}"
        
        def test_r_peak_detection_consistency(self):
            """测试R波检测一致性 - 回归测试"""
            processor = ECGProcessor(sample_rate=500)
            ecg_data = TestDataFactory.create_ecg_data(duration_seconds=60)
            
            # 多次运行应该产生相同结果
            results = [processor.detect_r_peaks(ecg_data) for _ in range(10)]
            
            # 验证结果一致性
            first_result = results[0]
            for result in results[1:]:
                assert len(result) == len(first_result), \
                    "R波检测结果不一致"
        
        def test_filter_performance(self):
            """测试滤波器性能 - 回归测试"""
            processor = ECGProcessor(sample_rate=500)
            ecg_data = TestDataFactory.create_ecg_data(duration_seconds=60)
            
            import time
            start_time = time.time()
            filtered_data = processor.apply_bandpass_filter(ecg_data)
            elapsed_time = time.time() - start_time
            
            # 性能回归检查
            assert elapsed_time < 0.1, \
                f"滤波器性能退化: {elapsed_time}秒 > 0.1秒"
            assert len(filtered_data) == len(ecg_data), \
                "滤波后数据长度改变"
    
    @pytest.mark.regression
    class TestPatientDataManagement:
        """患者数据管理回归测试"""
        
        def test_patient_search_functionality(self, db_session):
            """测试患者搜索功能 - 回归测试"""
            # 创建测试数据
            patients = TestDataFactory.create_batch_patients(100)
            for patient in patients:
                db_session.add(patient)
            db_session.commit()
            
            manager = PatientDataManager(db_session)
            
            # 测试各种搜索条件
            results = manager.search_patients(name='张')
            assert len(results) > 0, "按姓名搜索失败"
            
            results = manager.search_patients(gender='M')
            assert all(p.gender == 'M' for p in results), "按性别搜索失败"
        
        def test_data_export_format(self, db_session):
            """测试数据导出格式 - 回归测试"""
            patient = TestDataFactory.create_patient()
            db_session.add(patient)
            db_session.commit()
            
            manager = PatientDataManager(db_session)
            exported_data = manager.export_patient_data(patient.patient_id)
            
            # 验证导出格式
            required_fields = ['patient_id', 'name', 'gender', 'birth_date']
            for field in required_fields:
                assert field in exported_data, \
                    f"导出数据缺少字段: {field}"

# 运行回归测试
# pytest -m regression -v
```

### 视觉回归测试

```python
# visual_regression_test.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image, ImageChops
import os

class VisualRegressionTest:
    """视觉回归测试"""
    
    @pytest.fixture
    def driver(self):
        """创建WebDriver"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(1920, 1080)
        yield driver
        driver.quit()
    
    def capture_screenshot(self, driver, url, filename):
        """捕获截图"""
        driver.get(url)
        driver.save_screenshot(filename)
    
    def compare_images(self, baseline_path, current_path, threshold=0.01):
        """比较图像"""
        baseline = Image.open(baseline_path)
        current = Image.open(current_path)
        
        # 计算差异
        diff = ImageChops.difference(baseline, current)
        
        # 计算差异百分比
        histogram = diff.histogram()
        total_pixels = sum(histogram)
        different_pixels = sum(histogram[1:])
        diff_percentage = different_pixels / total_pixels
        
        return diff_percentage <= threshold
    
    @pytest.mark.visual
    def test_dashboard_layout(self, driver):
        """测试仪表板布局 - 视觉回归"""
        url = 'https://medical-device.com/dashboard'
        baseline_path = 'tests/visual/baseline/dashboard.png'
        current_path = 'tests/visual/current/dashboard.png'
        
        # 捕获当前截图
        self.capture_screenshot(driver, url, current_path)
        
        # 如果基线不存在，创建基线
        if not os.path.exists(baseline_path):
            os.makedirs(os.path.dirname(baseline_path), exist_ok=True)
            self.capture_screenshot(driver, url, baseline_path)
            pytest.skip("创建基线图像")
        
        # 比较图像
        is_similar = self.compare_images(baseline_path, current_path)
        assert is_similar, "仪表板布局发生变化"
```


## API自动化测试

### REST API测试

```python
# test_api.py
import pytest
import requests
from requests.auth import HTTPBasicAuth

class TestMedicalDeviceAPI:
    """医疗设备API测试"""
    
    BASE_URL = "https://api.medical-device.com/v1"
    
    @pytest.fixture(scope='class')
    def auth_token(self):
        """获取认证令牌"""
        response = requests.post(
            f"{self.BASE_URL}/auth/login",
            json={
                "username": "test_user",
                "password": "test_password"
            }
        )
        assert response.status_code == 200
        return response.json()['token']
    
    @pytest.fixture
    def headers(self, auth_token):
        """请求头"""
        return {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
    
    def test_get_patients_list(self, headers):
        """测试获取患者列表"""
        response = requests.get(
            f"{self.BASE_URL}/patients",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'patients' in data
        assert isinstance(data['patients'], list)
    
    def test_create_patient(self, headers):
        """测试创建患者"""
        patient_data = {
            "name": "测试患者",
            "gender": "M",
            "birth_date": "1980-01-01",
            "phone": "13800138000"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/patients",
            json=patient_data,
            headers=headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert 'patient_id' in data
        assert data['name'] == patient_data['name']
        
        # 清理
        patient_id = data['patient_id']
        requests.delete(
            f"{self.BASE_URL}/patients/{patient_id}",
            headers=headers
        )
    
    def test_get_patient_by_id(self, headers):
        """测试根据ID获取患者"""
        # 先创建患者
        patient_data = {"name": "测试患者", "gender": "M", "birth_date": "1980-01-01"}
        create_response = requests.post(
            f"{self.BASE_URL}/patients",
            json=patient_data,
            headers=headers
        )
        patient_id = create_response.json()['patient_id']
        
        # 获取患者
        response = requests.get(
            f"{self.BASE_URL}/patients/{patient_id}",
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['patient_id'] == patient_id
        assert data['name'] == patient_data['name']
        
        # 清理
        requests.delete(
            f"{self.BASE_URL}/patients/{patient_id}",
            headers=headers
        )
    
    def test_update_patient(self, headers):
        """测试更新患者信息"""
        # 创建患者
        patient_data = {"name": "原始姓名", "gender": "M", "birth_date": "1980-01-01"}
        create_response = requests.post(
            f"{self.BASE_URL}/patients",
            json=patient_data,
            headers=headers
        )
        patient_id = create_response.json()['patient_id']
        
        # 更新患者
        update_data = {"name": "更新后姓名"}
        response = requests.patch(
            f"{self.BASE_URL}/patients/{patient_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['name'] == update_data['name']
        
        # 清理
        requests.delete(
            f"{self.BASE_URL}/patients/{patient_id}",
            headers=headers
        )
    
    def test_delete_patient(self, headers):
        """测试删除患者"""
        # 创建患者
        patient_data = {"name": "待删除患者", "gender": "M", "birth_date": "1980-01-01"}
        create_response = requests.post(
            f"{self.BASE_URL}/patients",
            json=patient_data,
            headers=headers
        )
        patient_id = create_response.json()['patient_id']
        
        # 删除患者
        response = requests.delete(
            f"{self.BASE_URL}/patients/{patient_id}",
            headers=headers
        )
        
        assert response.status_code == 204
        
        # 验证已删除
        get_response = requests.get(
            f"{self.BASE_URL}/patients/{patient_id}",
            headers=headers
        )
        assert get_response.status_code == 404
    
    @pytest.mark.parametrize("invalid_data", [
        {},  # 空数据
        {"name": ""},  # 空姓名
        {"name": "测试", "gender": "X"},  # 无效性别
        {"name": "测试", "birth_date": "invalid"},  # 无效日期
    ])
    def test_create_patient_validation(self, headers, invalid_data):
        """测试患者创建验证"""
        response = requests.post(
            f"{self.BASE_URL}/patients",
            json=invalid_data,
            headers=headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
```

### 使用Tavern进行API测试

```yaml
# tests/api/test_patients.tavern.yaml
---
test_name: 患者管理API测试

stages:
  - name: 登录获取令牌
    request:
      url: "{base_url}/auth/login"
      method: POST
      json:
        username: test_user
        password: test_password
    response:
      status_code: 200
      save:
        json:
          auth_token: token

  - name: 创建患者
    request:
      url: "{base_url}/patients"
      method: POST
      headers:
        Authorization: "Bearer {auth_token}"
      json:
        name: 测试患者
        gender: M
        birth_date: "1980-01-01"
        phone: "13800138000"
    response:
      status_code: 201
      json:
        name: 测试患者
        gender: M
      save:
        json:
          patient_id: patient_id

  - name: 获取患者信息
    request:
      url: "{base_url}/patients/{patient_id}"
      method: GET
      headers:
        Authorization: "Bearer {auth_token}"
    response:
      status_code: 200
      json:
        patient_id: "{patient_id}"
        name: 测试患者

  - name: 更新患者信息
    request:
      url: "{base_url}/patients/{patient_id}"
      method: PATCH
      headers:
        Authorization: "Bearer {auth_token}"
      json:
        name: 更新后姓名
    response:
      status_code: 200
      json:
        name: 更新后姓名

  - name: 删除患者
    request:
      url: "{base_url}/patients/{patient_id}"
      method: DELETE
      headers:
        Authorization: "Bearer {auth_token}"
    response:
      status_code: 204

  - name: 验证患者已删除
    request:
      url: "{base_url}/patients/{patient_id}"
      method: GET
      headers:
        Authorization: "Bearer {auth_token}"
    response:
      status_code: 404
```

## 测试报告和度量

### 自定义测试报告

```python
# conftest.py
import pytest
from datetime import datetime
import json

class TestReport:
    """测试报告生成器"""
    
    def __init__(self):
        self.results = {
            'start_time': datetime.now().isoformat(),
            'tests': [],
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'errors': 0
            }
        }
    
    def add_test_result(self, nodeid, outcome, duration, error=None):
        """添加测试结果"""
        self.results['tests'].append({
            'test': nodeid,
            'outcome': outcome,
            'duration': duration,
            'error': error
        })
        
        self.results['summary']['total'] += 1
        self.results['summary'][outcome] += 1
    
    def generate_report(self, filename='test_report.json'):
        """生成报告"""
        self.results['end_time'] = datetime.now().isoformat()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

@pytest.fixture(scope='session')
def test_report():
    """测试报告夹具"""
    return TestReport()

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """钩子：生成测试报告"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == 'call':
        test_report = item.config._test_report
        test_report.add_test_result(
            nodeid=item.nodeid,
            outcome=report.outcome,
            duration=report.duration,
            error=str(report.longrepr) if report.failed else None
        )

def pytest_configure(config):
    """配置钩子"""
    config._test_report = TestReport()

def pytest_sessionfinish(session, exitstatus):
    """会话结束钩子"""
    test_report = session.config._test_report
    test_report.generate_report()
```

### HTML测试报告

```python
# 使用pytest-html生成HTML报告
# pytest --html=report.html --self-contained-html

# 自定义HTML报告
from py.xml import html

def pytest_html_report_title(report):
    """自定义报告标题"""
    report.title = "医疗设备软件测试报告"

def pytest_html_results_summary(prefix, summary, postfix):
    """自定义摘要"""
    prefix.extend([
        html.h2("测试环境"),
        html.p("操作系统: Ubuntu 20.04"),
        html.p("Python版本: 3.9"),
        html.p("测试日期: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    ])

def pytest_html_results_table_header(cells):
    """自定义表头"""
    cells.insert(2, html.th("测试类型"))
    cells.insert(3, html.th("优先级"))

def pytest_html_results_table_row(report, cells):
    """自定义表格行"""
    # 添加测试类型
    test_type = "单元测试"
    if "integration" in report.nodeid:
        test_type = "集成测试"
    elif "e2e" in report.nodeid:
        test_type = "端到端测试"
    
    cells.insert(2, html.td(test_type))
    
    # 添加优先级
    priority = "中"
    if "critical" in report.keywords:
        priority = "高"
    elif "low" in report.keywords:
        priority = "低"
    
    cells.insert(3, html.td(priority))
```

## 测试最佳实践

### 1. 测试命名规范

```python
# 好的测试命名
def test_ecg_processor_calculates_correct_heart_rate_for_normal_rhythm():
    """测试ECG处理器为正常心律计算正确的心率"""
    pass

def test_patient_manager_raises_error_when_patient_id_is_invalid():
    """测试当患者ID无效时患者管理器抛出错误"""
    pass

# 不好的测试命名
def test_1():
    pass

def test_ecg():
    pass
```

### 2. 测试独立性

```python
# 好的做法 - 测试独立
class TestPatientManager:
    @pytest.fixture
    def manager(self):
        return PatientManager()
    
    def test_add_patient(self, manager):
        patient = manager.add_patient("张三")
        assert patient is not None
    
    def test_remove_patient(self, manager):
        patient = manager.add_patient("李四")
        result = manager.remove_patient(patient.id)
        assert result is True

# 不好的做法 - 测试相互依赖
class TestPatientManager:
    def test_add_patient(self):
        self.patient = manager.add_patient("张三")
        assert self.patient is not None
    
    def test_remove_patient(self):
        # 依赖于test_add_patient
        result = manager.remove_patient(self.patient.id)
        assert result is True
```

### 3. 使用测试夹具

```python
@pytest.fixture(scope='session')
def database():
    """会话级数据库夹具"""
    db = create_test_database()
    yield db
    db.close()

@pytest.fixture(scope='module')
def test_data():
    """模块级测试数据"""
    return load_test_data()

@pytest.fixture(scope='function')
def clean_database(database):
    """函数级数据库清理"""
    yield database
    database.clear()
```

### 4. 参数化测试

```python
@pytest.mark.parametrize("heart_rate,expected_category", [
    (40, "bradycardia"),
    (60, "normal"),
    (100, "normal"),
    (120, "tachycardia"),
])
def test_heart_rate_categorization(heart_rate, expected_category):
    """测试心率分类"""
    category = categorize_heart_rate(heart_rate)
    assert category == expected_category
```

## 总结

测试自动化是确保医疗设备软件质量的关键实践。通过建立完善的自动化测试体系，可以：

- ✅ 提高测试效率和覆盖率
- ✅ 支持持续集成和快速迭代
- ✅ 确保测试一致性和可重复性
- ✅ 降低长期测试成本
- ✅ 满足监管合规要求

## 相关资源

- [测试策略概述](index.md)
- [性能测试](performance-testing.md)
- [安全测试](security-testing.md)
- [硬件在环测试](hil-testing.md)

## 参考资料

- pytest文档: https://docs.pytest.org/
- JUnit 5文档: https://junit.org/junit5/docs/current/user-guide/
- Selenium文档: https://www.selenium.dev/documentation/
- GitHub Actions文档: https://docs.github.com/en/actions
- GitLab CI/CD文档: https://docs.gitlab.com/ee/ci/
