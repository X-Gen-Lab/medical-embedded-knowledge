---
title: DICOM标准
difficulty: intermediate
estimated_time: 2-3小时
---

# DICOM标准

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

DICOM（Digital Imaging and Communications in Medicine，医学数字成像和通信）是医学影像领域的国际标准，定义了医学影像及相关信息的格式和交换方式。

## DICOM核心概念

### 信息对象定义（IOD）

DICOM定义了多种信息对象：

- **CT Image**: CT扫描图像
- **MR Image**: MRI图像  
- **US Image**: 超声图像
- **X-Ray Image**: X光图像
- **SR Document**: 结构化报告
- **GSPS**: 图形标注呈现状态

### 服务对象对类（SOP Class）

SOP Class = IOD + DIMSE服务

常用SOP Classes:
- **Storage**: 存储图像
- **Query/Retrieve**: 查询和检索
- **Print**: 打印
- **Worklist**: 工作列表管理

## DICOM文件格式

### 文件结构

```
[128字节前导码]
[4字节DICOM前缀: "DICM"]
[文件元信息]
[数据集]
```

### 数据元素

```
Tag (Group, Element) | VR | Length | Value
(0010,0010)         | PN | 10     | "John^Doe"
```

### 示例代码（Python pydicom）

```python
import pydicom
from pydicom.dataset import Dataset, FileDataset
import datetime
import numpy as np

# 创建DICOM文件
def create_dicom_image(pixel_array, patient_name, patient_id):
    # 文件元信息
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'  # CT Image Storage
    file_meta.MediaStorageSOPInstanceUID = pydicom.uid.generate_uid()
    file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
    
    # 创建数据集
    ds = FileDataset("ct_image.dcm", {}, file_meta=file_meta, preamble=b"\0" * 128)
    
    # 患者信息
    ds.PatientName = patient_name
    ds.PatientID = patient_id
    ds.PatientBirthDate = '19800101'
    ds.PatientSex = 'M'
    
    # 检查信息
    ds.StudyInstanceUID = pydicom.uid.generate_uid()
    ds.SeriesInstanceUID = pydicom.uid.generate_uid()
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.StudyDate = datetime.date.today().strftime('%Y%m%d')
    ds.StudyTime = datetime.datetime.now().strftime('%H%M%S')
    ds.Modality = 'CT'
    
    # 图像信息
    ds.SamplesPerPixel = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.Rows = pixel_array.shape[0]
    ds.Columns = pixel_array.shape[1]
    ds.BitsAllocated = 16
    ds.BitsStored = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 1  # 有符号
    
    # 像素数据
    ds.PixelData = pixel_array.tobytes()
    
    # 保存
    ds.save_as("ct_image.dcm")
    return ds

# 读取DICOM文件
def read_dicom_file(filename):
    ds = pydicom.dcmread(filename)
    
    print(f"Patient Name: {ds.PatientName}")
    print(f"Patient ID: {ds.PatientID}")
    print(f"Modality: {ds.Modality}")
    print(f"Image Size: {ds.Rows} x {ds.Columns}")
    
    # 获取像素数据
    pixel_array = ds.pixel_array
    return pixel_array
```

## DICOM网络协议

### DIMSE服务

#### C-STORE（存储）

```python
from pynetdicom import AE, StoragePresentationContexts

# 发送DICOM图像到PACS
def send_to_pacs(dicom_file, pacs_ip, pacs_port):
    ae = AE()
    ae.requested_contexts = StoragePresentationContexts
    
    # 建立关联
    assoc = ae.associate(pacs_ip, pacs_port)
    
    if assoc.is_established:
        # 读取DICOM文件
        ds = pydicom.dcmread(dicom_file)
        
        # 发送C-STORE请求
        status = assoc.send_c_store(ds)
        
        if status:
            print(f'C-STORE status: 0x{status.Status:04x}')
        
        assoc.release()
    else:
        print('Association rejected or aborted')

# 使用示例
send_to_pacs('ct_image.dcm', '192.168.1.100', 104)
```

#### C-FIND（查询）

```python
from pynetdicom import AE
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelFind

# 查询患者检查
def query_studies(patient_id, pacs_ip, pacs_port):
    ae = AE()
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
    
    assoc = ae.associate(pacs_ip, pacs_port)
    
    if assoc.is_established:
        # 创建查询数据集
        ds = Dataset()
        ds.QueryRetrieveLevel = 'STUDY'
        ds.PatientID = patient_id
        ds.StudyInstanceUID = ''
        ds.StudyDate = ''
        ds.StudyDescription = ''
        
        # 发送C-FIND请求
        responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
        
        for (status, identifier) in responses:
            if status and identifier:
                print(f"Study UID: {identifier.StudyInstanceUID}")
                print(f"Study Date: {identifier.StudyDate}")
                print(f"Description: {identifier.StudyDescription}")
        
        assoc.release()

query_studies('12345', '192.168.1.100', 104)
```

#### C-MOVE（检索）

```python
from pynetdicom.sop_class import PatientRootQueryRetrieveInformationModelMove

def retrieve_study(study_uid, dest_ae_title, pacs_ip, pacs_port):
    ae = AE()
    ae.add_requested_context(PatientRootQueryRetrieveInformationModelMove)
    
    assoc = ae.associate(pacs_ip, pacs_port)
    
    if assoc.is_established:
        ds = Dataset()
        ds.QueryRetrieveLevel = 'STUDY'
        ds.StudyInstanceUID = study_uid
        
        # 发送C-MOVE请求
        responses = assoc.send_c_move(ds, dest_ae_title, PatientRootQueryRetrieveInformationModelMove)
        
        for (status, identifier) in responses:
            if status:
                print(f'C-MOVE status: 0x{status.Status:04x}')
        
        assoc.release()
```

## DICOM SCP实现

```python
from pynetdicom import AE, evt, StoragePresentationContexts
from pynetdicom.sop_class import Verification

# 处理C-STORE请求
def handle_store(event):
    """处理接收到的DICOM图像"""
    ds = event.dataset
    ds.file_meta = event.file_meta
    
    # 保存到文件
    filename = f"{ds.SOPInstanceUID}.dcm"
    ds.save_as(filename, write_like_original=False)
    
    print(f"Stored: {filename}")
    
    # 返回成功状态
    return 0x0000

# 启动DICOM SCP服务器
def start_dicom_server(port=11112):
    ae = AE()
    ae.ae_title = b'MY_STORAGE_SCP'
    
    # 添加支持的存储SOP Classes
    ae.supported_contexts = StoragePresentationContexts
    
    # 添加验证SOP Class
    ae.add_supported_context(Verification)
    
    # 绑定事件处理器
    handlers = [(evt.EVT_C_STORE, handle_store)]
    
    # 启动服务器
    ae.start_server(('', port), evt_handlers=handlers)

# 启动服务器
start_dicom_server()
```

## DICOM Web (DICOMweb)

### WADO-RS（检索）

```python
import requests

# 检索检查
def retrieve_study_dicomweb(base_url, study_uid):
    url = f"{base_url}/studies/{study_uid}"
    headers = {'Accept': 'multipart/related; type=application/dicom'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        # 处理multipart响应
        return response.content
    else:
        print(f"Error: {response.status_code}")
        return None

# 检索元数据
def retrieve_metadata(base_url, study_uid):
    url = f"{base_url}/studies/{study_uid}/metadata"
    headers = {'Accept': 'application/dicom+json'}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return None
```

### STOW-RS（存储）

```python
def store_instance_dicomweb(base_url, dicom_file):
    url = f"{base_url}/studies"
    
    with open(dicom_file, 'rb') as f:
        dicom_data = f.read()
    
    # 构建multipart请求
    files = {
        'file': ('image.dcm', dicom_data, 'application/dicom')
    }
    
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        print("Successfully stored")
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None
```

### QIDO-RS（查询）

```python
def query_studies_dicomweb(base_url, patient_id):
    url = f"{base_url}/studies"
    params = {
        'PatientID': patient_id,
        'includefield': 'StudyDate,StudyDescription'
    }
    headers = {'Accept': 'application/dicom+json'}
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code == 200:
        studies = response.json()
        for study in studies:
            print(f"Study UID: {study['0020000D']['Value'][0]}")
            print(f"Study Date: {study.get('00080020', {}).get('Value', [''])[0]}")
    
    return response.json() if response.status_code == 200 else None
```

## 参考资源

- [DICOM标准](https://www.dicomstandard.org/)
- [pydicom文档](https://pydicom.github.io/)
- [pynetdicom文档](https://pydicom.github.io/pynetdicom/)

---

**下一步**: 了解 [IEEE 11073标准](ieee-11073.md)
