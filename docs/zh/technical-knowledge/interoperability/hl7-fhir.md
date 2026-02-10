---
title: HL7 FHIR标准
difficulty: intermediate
estimated_time: 2-3小时
---

# HL7 FHIR标准

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

FHIR（Fast Healthcare Interoperability Resources，快速医疗互联互通资源）是HL7组织开发的下一代医疗数据交换标准。FHIR结合了HL7 v2的简单性、HL7 v3的严谨性和现代Web技术的易用性。

## 为什么选择FHIR？

### 相比HL7 v2的优势

```
HL7 v2:
- 基于管道分隔的文本消息
- 灵活但不一致
- 难以解析和验证
- 缺乏标准化

FHIR:
- 基于RESTful API
- 结构化JSON/XML
- 易于实现和测试
- 强类型和验证
```

### 核心特性

1. **RESTful架构**: 使用标准HTTP方法（GET, POST, PUT, DELETE）
2. **资源模型**: 80+标准资源类型
3. **多格式支持**: JSON, XML
4. **现代Web技术**: OAuth 2.0, OpenID Connect
5. **可扩展性**: 自定义扩展机制

## FHIR资源

### 资源结构

```json
{
  "resourceType": "Patient",
  "id": "example",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2024-02-10T12:00:00Z"
  },
  "text": {
    "status": "generated",
    "div": "<div>Patient John Doe</div>"
  },
  "identifier": [{
    "system": "http://hospital.com/patients",
    "value": "12345"
  }],
  "name": [{
    "use": "official",
    "family": "Doe",
    "given": ["John"]
  }],
  "gender": "male",
  "birthDate": "1980-01-01"
}
```

### 常用资源类型

#### 1. Patient（患者）

```json
{
  "resourceType": "Patient",
  "identifier": [{
    "system": "http://hospital.com/mrn",
    "value": "MRN12345"
  }],
  "name": [{
    "family": "Smith",
    "given": ["Jane", "Marie"]
  }],
  "telecom": [{
    "system": "phone",
    "value": "+1-555-1234",
    "use": "mobile"
  }],
  "gender": "female",
  "birthDate": "1985-03-15",
  "address": [{
    "line": ["123 Main St"],
    "city": "Boston",
    "state": "MA",
    "postalCode": "02101",
    "country": "USA"
  }]
}
```

#### 2. Observation（观察/测量）

```json
{
  "resourceType": "Observation",
  "status": "final",
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/observation-category",
      "code": "vital-signs"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "8867-4",
      "display": "Heart rate"
    }]
  },
  "subject": {
    "reference": "Patient/example"
  },
  "effectiveDateTime": "2024-02-10T12:00:00Z",
  "valueQuantity": {
    "value": 75,
    "unit": "beats/minute",
    "system": "http://unitsofmeasure.org",
    "code": "/min"
  },
  "interpretation": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
      "code": "N",
      "display": "Normal"
    }]
  }]
}
```

#### 3. Device（设备）

```json
{
  "resourceType": "Device",
  "identifier": [{
    "system": "http://hospital.com/devices",
    "value": "DEVICE-001"
  }],
  "udiCarrier": [{
    "deviceIdentifier": "(01)00643169001763",
    "carrierHRF": "(01)00643169001763(17)250101(10)ABC123"
  }],
  "status": "active",
  "manufacturer": "Acme Medical Devices",
  "deviceName": [{
    "name": "Acme Vital Signs Monitor",
    "type": "user-friendly-name"
  }],
  "modelNumber": "VSM-2000",
  "serialNumber": "SN123456",
  "type": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "706767009",
      "display": "Patient vital signs monitoring system"
    }]
  }
}
```

#### 4. DeviceMetric（设备指标）

```json
{
  "resourceType": "DeviceMetric",
  "identifier": [{
    "system": "http://hospital.com/device-metrics",
    "value": "METRIC-HR-001"
  }],
  "type": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "8867-4",
      "display": "Heart rate"
    }]
  },
  "unit": {
    "coding": [{
      "system": "http://unitsofmeasure.org",
      "code": "/min"
    }]
  },
  "source": {
    "reference": "Device/example"
  },
  "operationalStatus": "on",
  "category": "measurement"
}
```

## RESTful API操作

### CRUD操作

#### Create（创建）

```http
POST /fhir/Observation HTTP/1.1
Host: api.hospital.com
Content-Type: application/fhir+json
Authorization: Bearer <access_token>

{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "8867-4"
    }]
  },
  "valueQuantity": {
    "value": 75,
    "unit": "bpm"
  }
}
```

响应:
```http
HTTP/1.1 201 Created
Location: /fhir/Observation/12345
ETag: W/"1"

{
  "resourceType": "Observation",
  "id": "12345",
  "meta": {
    "versionId": "1",
    "lastUpdated": "2024-02-10T12:00:00Z"
  },
  ...
}
```

#### Read（读取）

```http
GET /fhir/Patient/example HTTP/1.1
Host: api.hospital.com
Accept: application/fhir+json
Authorization: Bearer <access_token>
```

#### Update（更新）

```http
PUT /fhir/Patient/example HTTP/1.1
Host: api.hospital.com
Content-Type: application/fhir+json
If-Match: W/"1"

{
  "resourceType": "Patient",
  "id": "example",
  ...
}
```

#### Delete（删除）

```http
DELETE /fhir/Patient/example HTTP/1.1
Host: api.hospital.com
```

### 搜索操作

#### 基本搜索

```http
# 按患者ID搜索观察
GET /fhir/Observation?patient=Patient/example

# 按日期范围搜索
GET /fhir/Observation?date=ge2024-01-01&date=le2024-12-31

# 按代码搜索
GET /fhir/Observation?code=8867-4

# 组合搜索
GET /fhir/Observation?patient=Patient/example&code=8867-4&date=ge2024-02-01
```

#### 高级搜索

```http
# 使用_include包含引用资源
GET /fhir/Observation?patient=Patient/example&_include=Observation:patient

# 使用_revinclude包含反向引用
GET /fhir/Patient/example?_revinclude=Observation:patient

# 排序
GET /fhir/Observation?patient=Patient/example&_sort=-date

# 分页
GET /fhir/Observation?patient=Patient/example&_count=20&_offset=40
```

## 实现示例

### Python实现（使用fhirclient）

```python
from fhirclient import client
from fhirclient.models.observation import Observation
from fhirclient.models.quantity import Quantity
from fhirclient.models.codeableconcept import CodeableConcept
from fhirclient.models.coding import Coding
from fhirclient.models.fhirreference import FHIRReference
import datetime

# 配置FHIR客户端
settings = {
    'app_id': 'medical_device_app',
    'api_base': 'https://api.hospital.com/fhir'
}
smart = client.FHIRClient(settings=settings)

# 创建心率观察
def create_heart_rate_observation(patient_id, heart_rate):
    obs = Observation()
    obs.status = 'final'
    
    # 设置类别
    obs.category = [CodeableConcept()]
    obs.category[0].coding = [Coding()]
    obs.category[0].coding[0].system = 'http://terminology.hl7.org/CodeSystem/observation-category'
    obs.category[0].coding[0].code = 'vital-signs'
    
    # 设置代码（LOINC）
    obs.code = CodeableConcept()
    obs.code.coding = [Coding()]
    obs.code.coding[0].system = 'http://loinc.org'
    obs.code.coding[0].code = '8867-4'
    obs.code.coding[0].display = 'Heart rate'
    
    # 设置患者引用
    obs.subject = FHIRReference()
    obs.subject.reference = f'Patient/{patient_id}'
    
    # 设置时间
    obs.effectiveDateTime = datetime.datetime.now().isoformat()
    
    # 设置值
    obs.valueQuantity = Quantity()
    obs.valueQuantity.value = heart_rate
    obs.valueQuantity.unit = 'beats/minute'
    obs.valueQuantity.system = 'http://unitsofmeasure.org'
    obs.valueQuantity.code = '/min'
    
    # 创建资源
    obs.create(smart.server)
    return obs.id

# 搜索患者的观察
def get_patient_observations(patient_id, code=None):
    search = Observation.where(struct={'patient': f'Patient/{patient_id}'})
    
    if code:
        search = search.where(struct={'code': code})
    
    observations = search.perform_resources(smart.server)
    
    results = []
    for obs in observations:
        results.append({
            'id': obs.id,
            'code': obs.code.coding[0].code if obs.code.coding else None,
            'value': obs.valueQuantity.value if obs.valueQuantity else None,
            'unit': obs.valueQuantity.unit if obs.valueQuantity else None,
            'date': obs.effectiveDateTime
        })
    
    return results

# 使用示例
patient_id = 'example'
obs_id = create_heart_rate_observation(patient_id, 75)
print(f"Created observation: {obs_id}")

observations = get_patient_observations(patient_id, code='8867-4')
for obs in observations:
    print(f"Heart rate: {obs['value']} {obs['unit']} at {obs['date']}")
```

### JavaScript实现（使用fhir.js）

```javascript
const fhir = require('fhir.js');

// 配置FHIR客户端
const client = fhir({
  baseUrl: 'https://api.hospital.com/fhir',
  auth: {
    bearer: 'access_token_here'
  }
});

// 创建血压观察
async function createBloodPressureObservation(patientId, systolic, diastolic) {
  const observation = {
    resourceType: 'Observation',
    status: 'final',
    category: [{
      coding: [{
        system: 'http://terminology.hl7.org/CodeSystem/observation-category',
        code: 'vital-signs'
      }]
    }],
    code: {
      coding: [{
        system: 'http://loinc.org',
        code: '85354-9',
        display: 'Blood pressure panel'
      }]
    },
    subject: {
      reference: `Patient/${patientId}`
    },
    effectiveDateTime: new Date().toISOString(),
    component: [
      {
        code: {
          coding: [{
            system: 'http://loinc.org',
            code: '8480-6',
            display: 'Systolic blood pressure'
          }]
        },
        valueQuantity: {
          value: systolic,
          unit: 'mmHg',
          system: 'http://unitsofmeasure.org',
          code: 'mm[Hg]'
        }
      },
      {
        code: {
          coding: [{
            system: 'http://loinc.org',
            code: '8462-4',
            display: 'Diastolic blood pressure'
          }]
        },
        valueQuantity: {
          value: diastolic,
          unit: 'mmHg',
          system: 'http://unitsofmeasure.org',
          code: 'mm[Hg]'
        }
      }
    ]
  };
  
  try {
    const result = await client.create({
      resource: observation
    });
    console.log('Created observation:', result.id);
    return result;
  } catch (error) {
    console.error('Error creating observation:', error);
    throw error;
  }
}

// 搜索患者的生命体征
async function getVitalSigns(patientId, startDate, endDate) {
  try {
    const bundle = await client.search({
      type: 'Observation',
      query: {
        patient: patientId,
        category: 'vital-signs',
        date: `ge${startDate}`,
        _sort: '-date',
        _count: 100
      }
    });
    
    const observations = bundle.entry ? bundle.entry.map(e => e.resource) : [];
    return observations;
  } catch (error) {
    console.error('Error searching observations:', error);
    throw error;
  }
}

// 使用示例
(async () => {
  await createBloodPressureObservation('example', 120, 80);
  
  const vitalSigns = await getVitalSigns('example', '2024-01-01', '2024-12-31');
  console.log(`Found ${vitalSigns.length} vital signs`);
})();
```

### C实现（使用libfhir）

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>
#include <jansson.h>

// FHIR客户端配置
typedef struct {
    char *base_url;
    char *access_token;
} fhir_client_t;

// HTTP响应结构
typedef struct {
    char *data;
    size_t size;
} http_response_t;

// 写入回调函数
static size_t write_callback(void *contents, size_t size, size_t nmemb, void *userp) {
    size_t realsize = size * nmemb;
    http_response_t *resp = (http_response_t *)userp;
    
    char *ptr = realloc(resp->data, resp->size + realsize + 1);
    if (!ptr) return 0;
    
    resp->data = ptr;
    memcpy(&(resp->data[resp->size]), contents, realsize);
    resp->size += realsize;
    resp->data[resp->size] = 0;
    
    return realsize;
}

// 创建观察资源
char* create_observation_json(const char *patient_id, 
                              const char *code,
                              const char *display,
                              double value,
                              const char *unit) {
    json_t *root = json_object();
    
    json_object_set_new(root, "resourceType", json_string("Observation"));
    json_object_set_new(root, "status", json_string("final"));
    
    // 代码
    json_t *code_obj = json_object();
    json_t *coding_array = json_array();
    json_t *coding = json_object();
    json_object_set_new(coding, "system", json_string("http://loinc.org"));
    json_object_set_new(coding, "code", json_string(code));
    json_object_set_new(coding, "display", json_string(display));
    json_array_append_new(coding_array, coding);
    json_object_set_new(code_obj, "coding", coding_array);
    json_object_set_new(root, "code", code_obj);
    
    // 患者引用
    json_t *subject = json_object();
    char ref[256];
    snprintf(ref, sizeof(ref), "Patient/%s", patient_id);
    json_object_set_new(subject, "reference", json_string(ref));
    json_object_set_new(root, "subject", subject);
    
    // 值
    json_t *value_qty = json_object();
    json_object_set_new(value_qty, "value", json_real(value));
    json_object_set_new(value_qty, "unit", json_string(unit));
    json_object_set_new(value_qty, "system", json_string("http://unitsofmeasure.org"));
    json_object_set_new(root, "valueQuantity", value_qty);
    
    char *json_str = json_dumps(root, JSON_COMPACT);
    json_decref(root);
    
    return json_str;
}

// 发送FHIR请求
int fhir_create_resource(fhir_client_t *client, const char *resource_type, const char *json_data) {
    CURL *curl;
    CURLcode res;
    http_response_t response = {NULL, 0};
    
    curl = curl_easy_init();
    if (!curl) return -1;
    
    // 构建URL
    char url[512];
    snprintf(url, sizeof(url), "%s/%s", client->base_url, resource_type);
    
    // 设置请求头
    struct curl_slist *headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/fhir+json");
    
    char auth_header[256];
    snprintf(auth_header, sizeof(auth_header), "Authorization: Bearer %s", client->access_token);
    headers = curl_slist_append(headers, auth_header);
    
    // 配置CURL
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_data);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    
    // 执行请求
    res = curl_easy_perform(curl);
    
    if (res == CURLE_OK) {
        long http_code = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
        printf("HTTP Status: %ld\n", http_code);
        printf("Response: %s\n", response.data);
    }
    
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    free(response.data);
    
    return (res == CURLE_OK) ? 0 : -1;
}

// 使用示例
int main() {
    fhir_client_t client = {
        .base_url = "https://api.hospital.com/fhir",
        .access_token = "your_access_token"
    };
    
    // 创建心率观察
    char *json = create_observation_json("example", "8867-4", "Heart rate", 75.0, "bpm");
    fhir_create_resource(&client, "Observation", json);
    free(json);
    
    return 0;
}
```

## SMART on FHIR

### OAuth 2.0授权流程

```
1. 应用注册
   - 获取client_id和client_secret
   - 配置redirect_uri

2. 授权请求
   GET /authorize?
     response_type=code&
     client_id=APP_ID&
     redirect_uri=https://app.com/callback&
     scope=patient/Observation.read patient/Patient.read&
     state=RANDOM_STATE&
     aud=https://fhir.hospital.com

3. 用户授权
   - 用户登录并授权

4. 授权码交换
   POST /token
   Content-Type: application/x-www-form-urlencoded
   
   grant_type=authorization_code&
   code=AUTH_CODE&
   redirect_uri=https://app.com/callback&
   client_id=APP_ID&
   client_secret=SECRET

5. 访问令牌响应
   {
     "access_token": "eyJ...",
     "token_type": "Bearer",
     "expires_in": 3600,
     "scope": "patient/Observation.read patient/Patient.read",
     "patient": "123"
   }

6. 使用访问令牌
   GET /fhir/Patient/123
   Authorization: Bearer eyJ...
```

## 最佳实践

1. ✅ 使用标准术语系统（LOINC, SNOMED CT）
2. ✅ 实施适当的错误处理
3. ✅ 使用批量操作提高效率
4. ✅ 实施缓存策略
5. ✅ 验证资源完整性
6. ✅ 记录API使用情况

## 参考资源

- [FHIR官方网站](https://www.hl7.org/fhir/)
- [FHIR规范](https://www.hl7.org/fhir/documentation.html)
- [SMART on FHIR](https://docs.smarthealthit.org/)
- [公共测试服务器](https://test.fhir.org/)

---

**下一步**: 了解 [DICOM标准](dicom.md)
