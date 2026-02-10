---
title: 肺结节AI检测系统
description: LungAI智能肺结节检测系统的完整开发案例，包括3D CNN、CT图像分析和临床集成
difficulty: 高级
estimated_time: 2.5小时
tags:
  - 案例研究
  - 医学影像
  - 肺结节检测
  - 3D CNN
  - II类器械
related_modules:
  - zh/technical-knowledge/ai-ml/index
  - zh/regulatory-standards/ai-ml-regulations/index
  - zh/technical-knowledge/interoperability/dicom
last_updated: '2026-02-10'
version: '1.0'
language: zh-CN
---

# 肺结节AI检测系统

## 案例概述

### 产品简介
**产品名称**: LungAI智能肺结节检测系统  
**分类**: II类医疗器械（中等风险）  
**适用范围**: 用于胸部CT图像中肺结节的自动检测、分割和良恶性评估  
**目标用户**: 医院放射科、体检中心、肺癌筛查项目

### 临床背景

肺癌是全球癌症死亡的首要原因，早期发现和治疗可显著提高生存率。

#### 流行病学数据
- 全球每年新发肺癌约220万例
- 中国肺癌发病率和死亡率均居首位
- 5年生存率：I期>70%，IV期<5%
- 低剂量CT筛查可降低肺癌死亡率20%

#### 临床挑战
- **阅片工作量大**: 一次CT扫描300-500层图像
- **漏诊率高**: 小结节（<5mm）容易漏诊
- **诊断不一致**: 放射科医生间诊断差异大
- **经验依赖**: 需要丰富的临床经验

### 系统特点
- **高灵敏度检测**: 检测灵敏度>95%
- **3D分析**: 基于3D CNN的立体分析
- **良恶性评估**: 提供恶性概率评分
- **假阳性控制**: 假阳性率<0.5个/例
- **PACS集成**: 无缝集成到放射科工作流

## 技术架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    放射科工作站                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PACS查看器  │  │  AI辅助诊断  │  │  报告系统    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI分析引擎                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  肺部分割    │  │  结节检测    │  │  特征提取    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  良恶性分类  │  │  风险评分    │  │  报告生成    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    数据管理层                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  DICOM服务器 │  │  数据库      │  │  对象存储    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

#### 硬件要求
- **CT扫描仪**: 16排以上多层螺旋CT
- **层厚**: ≤1.5mm
- **重建算法**: 标准或肺算法
- **GPU服务器**: NVIDIA V100/A100

#### 软件平台
- **AI框架**: PyTorch, TensorFlow
- **3D处理**: SimpleITK, VTK
- **DICOM**: Pydicom, DCMTK, Orthanc
- **后端**: Python (FastAPI), Go
- **前端**: React, Three.js (3D可视化)
- **数据库**: PostgreSQL, MongoDB
- **消息队列**: RabbitMQ, Kafka

## AI模型设计

### 1. 肺部分割模型

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class UNet3D(nn.Module):
    """3D U-Net用于肺部分割"""
    
    def __init__(self, in_channels=1, out_channels=1, init_features=32):
        super(UNet3D, self).__init__()
        
        features = init_features
        
        # 编码器
        self.encoder1 = self._block(in_channels, features)
        self.pool1 = nn.MaxPool3d(kernel_size=2, stride=2)
        
        self.encoder2 = self._block(features, features * 2)
        self.pool2 = nn.MaxPool3d(kernel_size=2, stride=2)
        
        self.encoder3 = self._block(features * 2, features * 4)
        self.pool3 = nn.MaxPool3d(kernel_size=2, stride=2)
        
        self.encoder4 = self._block(features * 4, features * 8)
        self.pool4 = nn.MaxPool3d(kernel_size=2, stride=2)
        
        # 瓶颈层
        self.bottleneck = self._block(features * 8, features * 16)
        
        # 解码器
        self.upconv4 = nn.ConvTranspose3d(features * 16, features * 8, kernel_size=2, stride=2)
        self.decoder4 = self._block((features * 8) * 2, features * 8)
        
        self.upconv3 = nn.ConvTranspose3d(features * 8, features * 4, kernel_size=2, stride=2)
        self.decoder3 = self._block((features * 4) * 2, features * 4)
        
        self.upconv2 = nn.ConvTranspose3d(features * 4, features * 2, kernel_size=2, stride=2)
        self.decoder2 = self._block((features * 2) * 2, features * 2)
        
        self.upconv1 = nn.ConvTranspose3d(features * 2, features, kernel_size=2, stride=2)
        self.decoder1 = self._block(features * 2, features)
        
        # 输出层
        self.conv = nn.Conv3d(features, out_channels, kernel_size=1)
    
    def _block(self, in_channels, features):
        """卷积块"""
        return nn.Sequential(
            nn.Conv3d(in_channels, features, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm3d(features),
            nn.ReLU(inplace=True),
            nn.Conv3d(features, features, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm3d(features),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        # 编码路径
        enc1 = self.encoder1(x)
        enc2 = self.encoder2(self.pool1(enc1))
        enc3 = self.encoder3(self.pool2(enc2))
        enc4 = self.encoder4(self.pool3(enc3))
        
        # 瓶颈
        bottleneck = self.bottleneck(self.pool4(enc4))
        
        # 解码路径
        dec4 = self.upconv4(bottleneck)
        dec4 = torch.cat((dec4, enc4), dim=1)
        dec4 = self.decoder4(dec4)
        
        dec3 = self.upconv3(dec4)
        dec3 = torch.cat((dec3, enc3), dim=1)
        dec3 = self.decoder3(dec3)
        
        dec2 = self.upconv2(dec3)
        dec2 = torch.cat((dec2, enc2), dim=1)
        dec2 = self.decoder2(dec2)
        
        dec1 = self.upconv1(dec2)
        dec1 = torch.cat((dec1, enc1), dim=1)
        dec1 = self.decoder1(dec1)
        
        return torch.sigmoid(self.conv(dec1))

# 创建模型
lung_segmentation_model = UNet3D(in_channels=1, out_channels=1, init_features=32)

# 损失函数
class DiceLoss(nn.Module):
    """Dice损失函数"""
    
    def __init__(self, smooth=1.0):
        super(DiceLoss, self).__init__()
        self.smooth = smooth
    
    def forward(self, pred, target):
        pred = pred.contiguous().view(-1)
        target = target.contiguous().view(-1)
        
        intersection = (pred * target).sum()
        dice = (2. * intersection + self.smooth) / (pred.sum() + target.sum() + self.smooth)
        
        return 1 - dice

# 训练配置
criterion = DiceLoss()
optimizer = torch.optim.Adam(lung_segmentation_model.parameters(), lr=0.001)
```

### 2. 结节检测模型

```python
class NoduleDetectionNet(nn.Module):
    """3D CNN结节检测网络"""
    
    def __init__(self, in_channels=1, num_anchors=9):
        super(NoduleDetectionNet, self).__init__()
        
        # 特征提取骨干网络
        self.features = nn.Sequential(
            # Block 1
            nn.Conv3d(in_channels, 64, kernel_size=3, padding=1),
            nn.BatchNorm3d(64),
            nn.ReLU(inplace=True),
            nn.Conv3d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm3d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=2, stride=2),
            
            # Block 2
            nn.Conv3d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm3d(128),
            nn.ReLU(inplace=True),
            nn.Conv3d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm3d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=2, stride=2),
            
            # Block 3
            nn.Conv3d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm3d(256),
            nn.ReLU(inplace=True),
            nn.Conv3d(256, 256, kernel_size=3, padding=1),
            nn.BatchNorm3d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool3d(kernel_size=2, stride=2),
        )
        
        # 区域提议网络 (RPN)
        self.rpn_conv = nn.Conv3d(256, 512, kernel_size=3, padding=1)
        
        # 分类分支（前景/背景）
        self.rpn_cls = nn.Conv3d(512, num_anchors * 2, kernel_size=1)
        
        # 回归分支（边界框）
        self.rpn_reg = nn.Conv3d(512, num_anchors * 6, kernel_size=1)  # 6 = (x, y, z, d, h, w)
    
    def forward(self, x):
        # 特征提取
        features = self.features(x)
        
        # RPN
        rpn_features = F.relu(self.rpn_conv(features))
        
        # 分类和回归
        rpn_cls_score = self.rpn_cls(rpn_features)
        rpn_bbox_pred = self.rpn_reg(rpn_features)
        
        return rpn_cls_score, rpn_bbox_pred

# 创建模型
nodule_detection_model = NoduleDetectionNet(in_channels=1, num_anchors=9)
```

### 3. 良恶性分类模型

```python
class NoduleMalignancyClassifier(nn.Module):
    """结节良恶性分类模型"""
    
    def __init__(self, in_channels=1, num_classes=2):
        super(NoduleMalignancyClassifier, self).__init__()
        
        # 3D ResNet骨干
        self.conv1 = nn.Conv3d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
        self.bn1 = nn.BatchNorm3d(64)
        self.relu = nn.ReLU(inplace=True)
        self.maxpool = nn.MaxPool3d(kernel_size=3, stride=2, padding=1)
        
        # ResNet blocks
        self.layer1 = self._make_layer(64, 64, blocks=2)
        self.layer2 = self._make_layer(64, 128, blocks=2, stride=2)
        self.layer3 = self._make_layer(128, 256, blocks=2, stride=2)
        self.layer4 = self._make_layer(256, 512, blocks=2, stride=2)
        
        # 全局平均池化
        self.avgpool = nn.AdaptiveAvgPool3d((1, 1, 1))
        
        # 分类头
        self.fc = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(128, num_classes)
        )
    
    def _make_layer(self, in_channels, out_channels, blocks, stride=1):
        """构建ResNet层"""
        layers = []
        
        # 第一个块可能需要下采样
        layers.append(self._residual_block(in_channels, out_channels, stride))
        
        # 其余块
        for _ in range(1, blocks):
            layers.append(self._residual_block(out_channels, out_channels))
        
        return nn.Sequential(*layers)
    
    def _residual_block(self, in_channels, out_channels, stride=1):
        """残差块"""
        return nn.Sequential(
            nn.Conv3d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv3d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm3d(out_channels)
        )
    
    def forward(self, x):
        # 初始卷积
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        
        # ResNet blocks
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.layer4(x)
        
        # 全局池化
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        
        # 分类
        x = self.fc(x)
        
        return x

# 创建模型
malignancy_classifier = NoduleMalignancyClassifier(in_channels=1, num_classes=2)

# 训练配置
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(malignancy_classifier.parameters(), lr=0.0001)
```


## 数据处理

### DICOM图像处理

```python
# dicom_processing.py
import pydicom
import numpy as np
import SimpleITK as sitk
from typing import Tuple, List

class CTImageProcessor:
    """CT图像处理器"""
    
    def __init__(self):
        self.hu_min = -1000  # 空气
        self.hu_max = 400    # 骨骼
        self.lung_hu_min = -1000
        self.lung_hu_max = -300
    
    def load_dicom_series(self, dicom_dir: str) -> Tuple[np.ndarray, dict]:
        """
        加载DICOM系列
        
        Returns:
            image: 3D numpy array (D, H, W)
            metadata: 元数据字典
        """
        # 使用SimpleITK读取DICOM系列
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(dicom_dir)
        reader.SetFileNames(dicom_names)
        image_sitk = reader.Execute()
        
        # 转换为numpy数组
        image = sitk.GetArrayFromImage(image_sitk)
        
        # 获取元数据
        metadata = {
            'spacing': image_sitk.GetSpacing(),  # (x, y, z)
            'origin': image_sitk.GetOrigin(),
            'direction': image_sitk.GetDirection(),
            'size': image_sitk.GetSize()
        }
        
        # 读取第一个DICOM文件获取更多信息
        dcm = pydicom.dcmread(dicom_names[0])
        metadata.update({
            'patient_id': dcm.PatientID,
            'study_date': dcm.StudyDate,
            'modality': dcm.Modality,
            'slice_thickness': float(dcm.SliceThickness),
            'pixel_spacing': [float(x) for x in dcm.PixelSpacing]
        })
        
        return image, metadata
    
    def resample_image(self, image: np.ndarray, old_spacing: Tuple, 
                      new_spacing: Tuple = (1.0, 1.0, 1.0)) -> np.ndarray:
        """
        重采样图像到统一间距
        """
        # 计算新的尺寸
        old_spacing = np.array(old_spacing)
        new_spacing = np.array(new_spacing)
        
        resize_factor = old_spacing / new_spacing
        new_shape = np.round(image.shape * resize_factor).astype(int)
        
        # 使用SimpleITK重采样
        image_sitk = sitk.GetImageFromArray(image)
        image_sitk.SetSpacing(old_spacing[::-1])  # ITK uses (z, y, x)
        
        resampler = sitk.ResampleImageFilter()
        resampler.SetOutputSpacing(new_spacing[::-1])
        resampler.SetSize(new_shape[::-1].tolist())
        resampler.SetInterpolator(sitk.sitkLinear)
        
        resampled_sitk = resampler.Execute(image_sitk)
        resampled = sitk.GetArrayFromImage(resampled_sitk)
        
        return resampled
    
    def normalize_hu(self, image: np.ndarray) -> np.ndarray:
        """
        HU值归一化到[0, 1]
        """
        image = np.clip(image, self.hu_min, self.hu_max)
        image = (image - self.hu_min) / (self.hu_max - self.hu_min)
        return image.astype(np.float32)
    
    def extract_lung_region(self, image: np.ndarray) -> np.ndarray:
        """
        提取肺部区域
        """
        # 阈值分割
        lung_mask = (image >= self.lung_hu_min) & (image <= self.lung_hu_max)
        
        # 形态学操作
        from scipy import ndimage
        
        # 闭运算填充小孔
        lung_mask = ndimage.binary_closing(lung_mask, structure=np.ones((5, 5, 5)))
        
        # 连通域分析，保留最大的两个区域（左右肺）
        labeled, num_features = ndimage.label(lung_mask)
        
        if num_features > 0:
            # 计算每个区域的大小
            sizes = ndimage.sum(lung_mask, labeled, range(1, num_features + 1))
            
            # 保留最大的两个区域
            top2_labels = np.argsort(sizes)[-2:] + 1
            lung_mask = np.isin(labeled, top2_labels)
        
        return lung_mask
    
    def preprocess_for_inference(self, image: np.ndarray, 
                                 spacing: Tuple) -> Tuple[np.ndarray, dict]:
        """
        推理前预处理
        """
        # 1. 重采样到1mm各向同性
        image_resampled = self.resample_image(image, spacing, (1.0, 1.0, 1.0))
        
        # 2. HU值归一化
        image_normalized = self.normalize_hu(image_resampled)
        
        # 3. 提取肺部区域
        lung_mask = self.extract_lung_region(image)
        lung_mask_resampled = self.resample_image(
            lung_mask.astype(np.float32), spacing, (1.0, 1.0, 1.0)
        ) > 0.5
        
        # 4. 应用肺部mask
        image_masked = image_normalized * lung_mask_resampled
        
        # 5. 裁剪到固定大小或padding
        image_processed, crop_info = self._crop_or_pad(image_masked, target_size=(128, 256, 256))
        
        preprocessing_info = {
            'original_shape': image.shape,
            'resampled_shape': image_resampled.shape,
            'final_shape': image_processed.shape,
            'crop_info': crop_info
        }
        
        return image_processed, preprocessing_info
    
    def _crop_or_pad(self, image: np.ndarray, 
                     target_size: Tuple[int, int, int]) -> Tuple[np.ndarray, dict]:
        """裁剪或填充到目标大小"""
        current_size = image.shape
        
        # 计算裁剪/填充量
        crop_or_pad = []
        for i in range(3):
            if current_size[i] > target_size[i]:
                # 需要裁剪
                start = (current_size[i] - target_size[i]) // 2
                end = start + target_size[i]
                crop_or_pad.append((start, end, 'crop'))
            elif current_size[i] < target_size[i]:
                # 需要填充
                pad_before = (target_size[i] - current_size[i]) // 2
                pad_after = target_size[i] - current_size[i] - pad_before
                crop_or_pad.append((pad_before, pad_after, 'pad'))
            else:
                crop_or_pad.append((0, 0, 'none'))
        
        # 执行裁剪/填充
        result = image.copy()
        
        # Z轴
        if crop_or_pad[0][2] == 'crop':
            result = result[crop_or_pad[0][0]:crop_or_pad[0][1], :, :]
        elif crop_or_pad[0][2] == 'pad':
            result = np.pad(result, ((crop_or_pad[0][0], crop_or_pad[0][1]), (0, 0), (0, 0)), 
                          mode='constant', constant_values=0)
        
        # Y轴
        if crop_or_pad[1][2] == 'crop':
            result = result[:, crop_or_pad[1][0]:crop_or_pad[1][1], :]
        elif crop_or_pad[1][2] == 'pad':
            result = np.pad(result, ((0, 0), (crop_or_pad[1][0], crop_or_pad[1][1]), (0, 0)), 
                          mode='constant', constant_values=0)
        
        # X轴
        if crop_or_pad[2][2] == 'crop':
            result = result[:, :, crop_or_pad[2][0]:crop_or_pad[2][1]]
        elif crop_or_pad[2][2] == 'pad':
            result = np.pad(result, ((0, 0), (0, 0), (crop_or_pad[2][0], crop_or_pad[2][1])), 
                          mode='constant', constant_values=0)
        
        crop_info = {
            'z': crop_or_pad[0],
            'y': crop_or_pad[1],
            'x': crop_or_pad[2]
        }
        
        return result, crop_info

# 使用示例
processor = CTImageProcessor()

# 加载DICOM
image, metadata = processor.load_dicom_series('/path/to/dicom/series')

# 预处理
processed_image, preproc_info = processor.preprocess_for_inference(
    image, 
    metadata['spacing']
)

print(f"Original shape: {image.shape}")
print(f"Processed shape: {processed_image.shape}")
```

### 数据增强

```python
# data_augmentation.py
import numpy as np
from scipy import ndimage
import random

class CTDataAugmentation:
    """CT图像数据增强"""
    
    def __init__(self, p=0.5):
        self.p = p  # 应用增强的概率
    
    def random_flip(self, image: np.ndarray, nodule_coords: List = None):
        """随机翻转"""
        if random.random() < self.p:
            # 左右翻转
            image = np.flip(image, axis=2).copy()
            
            if nodule_coords:
                # 更新结节坐标
                nodule_coords = [(z, y, image.shape[2] - x - 1) 
                               for z, y, x in nodule_coords]
        
        return image, nodule_coords
    
    def random_rotation(self, image: np.ndarray, max_angle=15):
        """随机旋转"""
        if random.random() < self.p:
            # 在XY平面随机旋转
            angle = random.uniform(-max_angle, max_angle)
            
            # 对每个切片旋转
            rotated = np.zeros_like(image)
            for i in range(image.shape[0]):
                rotated[i] = ndimage.rotate(image[i], angle, reshape=False, order=1)
            
            return rotated
        
        return image
    
    def random_scale(self, image: np.ndarray, scale_range=(0.9, 1.1)):
        """随机缩放"""
        if random.random() < self.p:
            scale = random.uniform(*scale_range)
            
            # 计算新尺寸
            new_shape = tuple(int(s * scale) for s in image.shape)
            
            # 缩放
            scaled = ndimage.zoom(image, scale, order=1)
            
            # 裁剪或填充回原始大小
            if scale > 1.0:
                # 裁剪
                start = tuple((s - o) // 2 for s, o in zip(scaled.shape, image.shape))
                end = tuple(st + o for st, o in zip(start, image.shape))
                scaled = scaled[start[0]:end[0], start[1]:end[1], start[2]:end[2]]
            else:
                # 填充
                pad_width = tuple((o - s) // 2 for o, s in zip(image.shape, scaled.shape))
                pad_width = [(p, image.shape[i] - scaled.shape[i] - p) 
                           for i, p in enumerate(pad_width)]
                scaled = np.pad(scaled, pad_width, mode='constant', constant_values=0)
            
            return scaled
        
        return image
    
    def random_noise(self, image: np.ndarray, noise_std=0.01):
        """添加随机噪声"""
        if random.random() < self.p:
            noise = np.random.normal(0, noise_std, image.shape)
            return np.clip(image + noise, 0, 1)
        
        return image
    
    def random_contrast(self, image: np.ndarray, contrast_range=(0.8, 1.2)):
        """随机对比度调整"""
        if random.random() < self.p:
            factor = random.uniform(*contrast_range)
            mean = image.mean()
            return np.clip((image - mean) * factor + mean, 0, 1)
        
        return image
    
    def random_brightness(self, image: np.ndarray, brightness_range=(-0.1, 0.1)):
        """随机亮度调整"""
        if random.random() < self.p:
            delta = random.uniform(*brightness_range)
            return np.clip(image + delta, 0, 1)
        
        return image
    
    def apply_augmentation(self, image: np.ndarray, nodule_coords: List = None):
        """应用所有增强"""
        # 几何变换
        image, nodule_coords = self.random_flip(image, nodule_coords)
        image = self.random_rotation(image)
        image = self.random_scale(image)
        
        # 强度变换
        image = self.random_noise(image)
        image = self.random_contrast(image)
        image = self.random_brightness(image)
        
        return image, nodule_coords

# 使用示例
augmentor = CTDataAugmentation(p=0.5)

# 应用增强
augmented_image, augmented_coords = augmentor.apply_augmentation(
    processed_image,
    nodule_coords=[(64, 128, 128)]  # 示例结节坐标
)
```


## 推理服务实现

### FastAPI推理服务

```python
# inference_service.py
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple
import numpy as np
import torch
import SimpleITK as sitk
from datetime import datetime
import asyncio
import io

app = FastAPI(title="LungAI Inference Service")

# 加载模型
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
lung_seg_model = UNet3D().to(device)
lung_seg_model.load_state_dict(torch.load('models/lung_segmentation.pth'))
lung_seg_model.eval()

nodule_det_model = NoduleDetectionNet().to(device)
nodule_det_model.load_state_dict(torch.load('models/nodule_detection.pth'))
nodule_det_model.eval()

malignancy_model = NoduleMalignancyClassifier().to(device)
malignancy_model.load_state_dict(torch.load('models/malignancy_classifier.pth'))
malignancy_model.eval()

class CTScanRequest(BaseModel):
    patient_id: str
    study_id: str
    series_id: str
    dicom_files: List[str]

class NoduleInfo(BaseModel):
    nodule_id: int
    position: Tuple[float, float, float]  # (x, y, z) in mm
    size: Tuple[float, float, float]  # (width, height, depth) in mm
    volume: float  # mm³
    malignancy_score: float  # 0-1
    malignancy_class: str  # "benign" or "malignant"
    confidence: float
    characteristics: Dict[str, any]

class InferenceResult(BaseModel):
    patient_id: str
    study_id: str
    timestamp: str
    num_nodules: int
    nodules: List[NoduleInfo]
    risk_assessment: str
    recommendations: List[str]
    processing_time: float

@app.post("/api/v1/analyze_ct", response_model=InferenceResult)
async def analyze_ct_scan(
    patient_id: str,
    study_id: str,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = None
):
    """
    分析CT扫描图像
    """
    start_time = datetime.now()
    
    try:
        # 1. 加载DICOM系列
        ct_image, metadata = await load_dicom_series(files)
        
        # 2. 预处理
        processor = CTImageProcessor()
        processed_image, preproc_info = processor.preprocess_for_inference(
            ct_image,
            metadata['spacing']
        )
        
        # 3. 肺部分割
        lung_mask = segment_lungs(processed_image)
        
        # 4. 结节检测
        nodule_candidates = detect_nodules(processed_image, lung_mask)
        
        # 5. 假阳性过滤和良恶性分类
        nodules = []
        for idx, candidate in enumerate(nodule_candidates):
            # 提取结节区域
            nodule_patch = extract_nodule_patch(processed_image, candidate)
            
            # 良恶性分类
            malignancy_score, malignancy_class, confidence = classify_malignancy(nodule_patch)
            
            # 计算特征
            characteristics = calculate_nodule_characteristics(nodule_patch, candidate)
            
            nodule_info = NoduleInfo(
                nodule_id=idx + 1,
                position=candidate['position'],
                size=candidate['size'],
                volume=candidate['volume'],
                malignancy_score=float(malignancy_score),
                malignancy_class=malignancy_class,
                confidence=float(confidence),
                characteristics=characteristics
            )
            nodules.append(nodule_info)
        
        # 6. 风险评估
        risk_assessment = assess_patient_risk(nodules)
        
        # 7. 生成建议
        recommendations = generate_recommendations(nodules, risk_assessment)
        
        # 8. 计算处理时间
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 9. 构建结果
        result = InferenceResult(
            patient_id=patient_id,
            study_id=study_id,
            timestamp=datetime.utcnow().isoformat(),
            num_nodules=len(nodules),
            nodules=nodules,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            processing_time=processing_time
        )
        
        # 10. 异步保存结果
        if background_tasks:
            background_tasks.add_task(save_result_to_db, result)
            background_tasks.add_task(send_to_pacs, result, metadata)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def load_dicom_series(files: List[UploadFile]) -> Tuple[np.ndarray, dict]:
    """加载DICOM系列"""
    import tempfile
    import shutil
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 保存上传的文件
        for file in files:
            file_path = f"{temp_dir}/{file.filename}"
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(file.file, f)
        
        # 使用CTImageProcessor加载
        processor = CTImageProcessor()
        image, metadata = processor.load_dicom_series(temp_dir)
        
        return image, metadata
        
    finally:
        # 清理临时文件
        shutil.rmtree(temp_dir)

def segment_lungs(image: np.ndarray) -> np.ndarray:
    """肺部分割"""
    with torch.no_grad():
        # 转换为tensor
        image_tensor = torch.from_numpy(image).unsqueeze(0).unsqueeze(0).float().to(device)
        
        # 推理
        lung_mask = lung_seg_model(image_tensor)
        
        # 转换回numpy
        lung_mask = lung_mask.squeeze().cpu().numpy()
        lung_mask = (lung_mask > 0.5).astype(np.uint8)
    
    return lung_mask

def detect_nodules(image: np.ndarray, lung_mask: np.ndarray) -> List[Dict]:
    """检测结节"""
    with torch.no_grad():
        # 应用肺部mask
        masked_image = image * lung_mask
        
        # 转换为tensor
        image_tensor = torch.from_numpy(masked_image).unsqueeze(0).unsqueeze(0).float().to(device)
        
        # 推理
        rpn_cls_score, rpn_bbox_pred = nodule_det_model(image_tensor)
        
        # 后处理：NMS和阈值过滤
        nodule_candidates = post_process_detections(
            rpn_cls_score.cpu().numpy(),
            rpn_bbox_pred.cpu().numpy(),
            confidence_threshold=0.5,
            nms_threshold=0.3
        )
    
    return nodule_candidates

def post_process_detections(cls_scores, bbox_preds, confidence_threshold=0.5, nms_threshold=0.3):
    """后处理检测结果"""
    from scipy import ndimage
    
    # Softmax
    cls_probs = np.exp(cls_scores) / np.sum(np.exp(cls_scores), axis=1, keepdims=True)
    
    # 获取前景概率
    fg_probs = cls_probs[:, 1]
    
    # 阈值过滤
    keep_indices = fg_probs > confidence_threshold
    
    if not np.any(keep_indices):
        return []
    
    # 提取候选框
    boxes = bbox_preds[keep_indices]
    scores = fg_probs[keep_indices]
    
    # NMS
    keep = nms_3d(boxes, scores, nms_threshold)
    
    # 构建结果
    nodule_candidates = []
    for idx in keep:
        box = boxes[idx]
        score = scores[idx]
        
        # 计算位置和大小
        x, y, z, w, h, d = box
        
        nodule_candidates.append({
            'position': (float(x), float(y), float(z)),
            'size': (float(w), float(h), float(d)),
            'volume': float(w * h * d),
            'confidence': float(score)
        })
    
    return nodule_candidates

def nms_3d(boxes, scores, threshold):
    """3D非极大值抑制"""
    # 按分数排序
    order = scores.argsort()[::-1]
    
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        
        # 计算IoU
        ious = compute_iou_3d(boxes[i], boxes[order[1:]])
        
        # 保留IoU小于阈值的框
        inds = np.where(ious <= threshold)[0]
        order = order[inds + 1]
    
    return keep

def compute_iou_3d(box1, boxes):
    """计算3D IoU"""
    x1, y1, z1, w1, h1, d1 = box1
    x2, y2, z2, w2, h2, d2 = boxes.T
    
    # 计算交集
    x_left = np.maximum(x1 - w1/2, x2 - w2/2)
    x_right = np.minimum(x1 + w1/2, x2 + w2/2)
    y_top = np.maximum(y1 - h1/2, y2 - h2/2)
    y_bottom = np.minimum(y1 + h1/2, y2 + h2/2)
    z_front = np.maximum(z1 - d1/2, z2 - d2/2)
    z_back = np.minimum(z1 + d1/2, z2 + d2/2)
    
    intersection = np.maximum(0, x_right - x_left) * \
                   np.maximum(0, y_bottom - y_top) * \
                   np.maximum(0, z_back - z_front)
    
    # 计算并集
    vol1 = w1 * h1 * d1
    vol2 = w2 * h2 * d2
    union = vol1 + vol2 - intersection
    
    # IoU
    iou = intersection / (union + 1e-6)
    
    return iou

def extract_nodule_patch(image: np.ndarray, candidate: Dict, patch_size=32) -> np.ndarray:
    """提取结节区域"""
    x, y, z = candidate['position']
    x, y, z = int(x), int(y), int(z)
    
    # 计算patch边界
    half_size = patch_size // 2
    
    z_start = max(0, z - half_size)
    z_end = min(image.shape[0], z + half_size)
    y_start = max(0, y - half_size)
    y_end = min(image.shape[1], y + half_size)
    x_start = max(0, x - half_size)
    x_end = min(image.shape[2], x + half_size)
    
    # 提取patch
    patch = image[z_start:z_end, y_start:y_end, x_start:x_end]
    
    # 填充到固定大小
    if patch.shape != (patch_size, patch_size, patch_size):
        padded = np.zeros((patch_size, patch_size, patch_size))
        padded[:patch.shape[0], :patch.shape[1], :patch.shape[2]] = patch
        patch = padded
    
    return patch

def classify_malignancy(nodule_patch: np.ndarray) -> Tuple[float, str, float]:
    """良恶性分类"""
    with torch.no_grad():
        # 转换为tensor
        patch_tensor = torch.from_numpy(nodule_patch).unsqueeze(0).unsqueeze(0).float().to(device)
        
        # 推理
        logits = malignancy_model(patch_tensor)
        probs = torch.softmax(logits, dim=1)
        
        # 获取结果
        malignancy_score = probs[0, 1].item()  # 恶性概率
        malignancy_class = "malignant" if malignancy_score > 0.5 else "benign"
        confidence = max(probs[0]).item()
    
    return malignancy_score, malignancy_class, confidence

def calculate_nodule_characteristics(patch: np.ndarray, candidate: Dict) -> Dict:
    """计算结节特征"""
    from scipy import ndimage
    
    # 二值化
    threshold = patch.mean() + patch.std()
    binary = patch > threshold
    
    # 计算特征
    characteristics = {
        'diameter_mm': np.mean(candidate['size']),
        'volume_mm3': candidate['volume'],
        'sphericity': calculate_sphericity(binary),
        'density_hu': float(patch.mean()),
        'texture_std': float(patch.std()),
        'edge_sharpness': calculate_edge_sharpness(patch),
        'spiculation': detect_spiculation(patch)
    }
    
    return characteristics

def calculate_sphericity(binary_mask: np.ndarray) -> float:
    """计算球形度"""
    volume = np.sum(binary_mask)
    if volume == 0:
        return 0.0
    
    # 计算表面积（简化）
    from scipy import ndimage
    surface = ndimage.binary_erosion(binary_mask) != binary_mask
    surface_area = np.sum(surface)
    
    # 球形度 = (π^(1/3) * (6V)^(2/3)) / A
    sphericity = (np.pi ** (1/3) * (6 * volume) ** (2/3)) / (surface_area + 1e-6)
    
    return float(min(sphericity, 1.0))

def calculate_edge_sharpness(patch: np.ndarray) -> float:
    """计算边缘锐度"""
    from scipy import ndimage
    
    # Sobel梯度
    gradient = ndimage.sobel(patch)
    sharpness = np.mean(np.abs(gradient))
    
    return float(sharpness)

def detect_spiculation(patch: np.ndarray) -> bool:
    """检测毛刺征"""
    # 简化实现：检测边缘的不规则性
    from scipy import ndimage
    
    # 二值化
    threshold = patch.mean()
    binary = patch > threshold
    
    # 边缘检测
    edges = ndimage.binary_erosion(binary) != binary
    
    # 计算边缘的不规则性
    edge_coords = np.argwhere(edges)
    if len(edge_coords) < 10:
        return False
    
    # 计算到中心的距离变化
    center = np.array(patch.shape) / 2
    distances = np.linalg.norm(edge_coords - center, axis=1)
    irregularity = np.std(distances) / (np.mean(distances) + 1e-6)
    
    return irregularity > 0.3

def assess_patient_risk(nodules: List[NoduleInfo]) -> str:
    """评估患者风险"""
    if not nodules:
        return "low"
    
    # 检查是否有高风险结节
    high_risk_count = sum(1 for n in nodules if n.malignancy_score > 0.7)
    medium_risk_count = sum(1 for n in nodules if 0.3 < n.malignancy_score <= 0.7)
    
    # 检查大结节
    large_nodules = sum(1 for n in nodules if n.characteristics['diameter_mm'] > 8)
    
    if high_risk_count > 0 or large_nodules > 0:
        return "high"
    elif medium_risk_count > 0 or len(nodules) > 3:
        return "medium"
    else:
        return "low"

def generate_recommendations(nodules: List[NoduleInfo], risk_level: str) -> List[str]:
    """生成临床建议"""
    recommendations = []
    
    if risk_level == "high":
        recommendations.append("建议立即转诊胸外科或肿瘤科")
        recommendations.append("考虑进行PET-CT检查")
        recommendations.append("必要时进行穿刺活检")
        recommendations.append("1个月内复查CT")
    elif risk_level == "medium":
        recommendations.append("建议3个月内复查CT")
        recommendations.append("密切观察结节变化")
        recommendations.append("必要时咨询胸外科医生")
    else:
        recommendations.append("建议6-12个月复查CT")
        recommendations.append("继续常规体检")
    
    # 针对特定结节特征的建议
    for nodule in nodules:
        if nodule.characteristics.get('spiculation'):
            recommendations.append(f"结节{nodule.nodule_id}存在毛刺征，需要重点关注")
        
        if nodule.characteristics['diameter_mm'] > 10:
            recommendations.append(f"结节{nodule.nodule_id}直径>{10}mm，建议进一步检查")
    
    return list(set(recommendations))  # 去重

async def save_result_to_db(result: InferenceResult):
    """保存结果到数据库"""
    # 实际实现中连接数据库保存
    pass

async def send_to_pacs(result: InferenceResult, metadata: dict):
    """发送结果到PACS系统"""
    # 实际实现中通过DICOM协议发送
    pass

@app.get("/api/v1/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "models_loaded": {
            "lung_segmentation": lung_seg_model is not None,
            "nodule_detection": nodule_det_model is not None,
            "malignancy_classification": malignancy_model is not None
        },
        "device": str(device),
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/batch_analyze")
async def batch_analyze(studies: List[CTScanRequest]):
    """批量分析"""
    results = []
    
    for study in studies:
        try:
            result = await analyze_ct_scan(
                patient_id=study.patient_id,
                study_id=study.study_id,
                files=study.dicom_files
            )
            results.append(result)
        except Exception as e:
            results.append({
                "error": str(e),
                "study_id": study.study_id
            })
    
    return {"results": results, "total": len(studies)}
```

### PACS集成

```python
# pacs_integration.py
from pynetdicom import AE, evt, StoragePresentationContexts
from pynetdicom.sop_class import CTImageStorage, SecondaryCaptureImageStorage
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid
import numpy as np
from datetime import datetime

class PACSIntegration:
    """PACS系统集成"""
    
    def __init__(self, pacs_host: str, pacs_port: int, ae_title: str = "LUNGAI"):
        self.pacs_host = pacs_host
        self.pacs_port = pacs_port
        self.ae_title = ae_title
        
        # 创建Application Entity
        self.ae = AE(ae_title=ae_title)
        self.ae.add_requested_context(CTImageStorage)
        self.ae.add_requested_context(SecondaryCaptureImageStorage)
    
    def send_structured_report(self, result: InferenceResult, original_study: Dataset):
        """发送结构化报告到PACS"""
        
        # 创建DICOM SR (Structured Report)
        sr_dataset = self._create_sr_dataset(result, original_study)
        
        # 发送到PACS
        assoc = self.ae.associate(self.pacs_host, self.pacs_port)
        
        if assoc.is_established:
            status = assoc.send_c_store(sr_dataset)
            
            if status:
                print(f"SR sent successfully: {status.Status}")
            else:
                print("Failed to send SR")
            
            assoc.release()
        else:
            print("Association rejected or aborted")
    
    def _create_sr_dataset(self, result: InferenceResult, original_study: Dataset) -> Dataset:
        """创建结构化报告数据集"""
        
        # 创建新的Dataset
        sr = Dataset()
        
        # SOP Common Module
        sr.SOPClassUID = '1.2.840.10008.5.1.4.1.1.88.11'  # Basic Text SR
        sr.SOPInstanceUID = generate_uid()
        
        # Patient Module
        sr.PatientName = original_study.PatientName
        sr.PatientID = result.patient_id
        sr.PatientBirthDate = original_study.get('PatientBirthDate', '')
        sr.PatientSex = original_study.get('PatientSex', '')
        
        # Study Module
        sr.StudyInstanceUID = original_study.StudyInstanceUID
        sr.StudyDate = original_study.StudyDate
        sr.StudyTime = original_study.StudyTime
        sr.ReferringPhysicianName = original_study.get('ReferringPhysicianName', '')
        sr.StudyID = result.study_id
        sr.AccessionNumber = original_study.get('AccessionNumber', '')
        
        # SR Document Series Module
        sr.Modality = 'SR'
        sr.SeriesInstanceUID = generate_uid()
        sr.SeriesNumber = '9999'
        sr.SeriesDate = datetime.now().strftime('%Y%m%d')
        sr.SeriesTime = datetime.now().strftime('%H%M%S')
        
        # SR Document General Module
        sr.InstanceNumber = '1'
        sr.ContentDate = datetime.now().strftime('%Y%m%d')
        sr.ContentTime = datetime.now().strftime('%H%M%S')
        
        # SR Document Content Module
        sr.ValueType = 'CONTAINER'
        sr.ConceptNameCodeSequence = [self._create_code('AI Analysis', 'LungAI', 'AI分析报告')]
        sr.ContinuityOfContent = 'SEPARATE'
        
        # Content Sequence
        content_seq = []
        
        # 添加结节信息
        for nodule in result.nodules:
            nodule_item = Dataset()
            nodule_item.ValueType = 'TEXT'
            nodule_item.ConceptNameCodeSequence = [
                self._create_code('Finding', 'DCM', f'结节 {nodule.nodule_id}')
            ]
            nodule_item.TextValue = self._format_nodule_info(nodule)
            content_seq.append(nodule_item)
        
        # 添加风险评估
        risk_item = Dataset()
        risk_item.ValueType = 'TEXT'
        risk_item.ConceptNameCodeSequence = [
            self._create_code('Risk Assessment', 'LungAI', '风险评估')
        ]
        risk_item.TextValue = result.risk_assessment
        content_seq.append(risk_item)
        
        # 添加建议
        for rec in result.recommendations:
            rec_item = Dataset()
            rec_item.ValueType = 'TEXT'
            rec_item.ConceptNameCodeSequence = [
                self._create_code('Recommendation', 'LungAI', '临床建议')
            ]
            rec_item.TextValue = rec
            content_seq.append(rec_item)
        
        sr.ContentSequence = content_seq
        
        return sr
    
    def _create_code(self, value: str, scheme: str, meaning: str) -> Dataset:
        """创建代码序列项"""
        code = Dataset()
        code.CodeValue = value
        code.CodingSchemeDesignator = scheme
        code.CodeMeaning = meaning
        return code
    
    def _format_nodule_info(self, nodule: NoduleInfo) -> str:
        """格式化结节信息"""
        info = f"位置: ({nodule.position[0]:.1f}, {nodule.position[1]:.1f}, {nodule.position[2]:.1f}) mm\n"
        info += f"大小: {nodule.characteristics['diameter_mm']:.1f} mm\n"
        info += f"体积: {nodule.volume:.1f} mm³\n"
        info += f"恶性评分: {nodule.malignancy_score:.2f}\n"
        info += f"分类: {nodule.malignancy_class}\n"
        info += f"置信度: {nodule.confidence:.2f}\n"
        
        if nodule.characteristics.get('spiculation'):
            info += "特征: 毛刺征\n"
        
        return info
    
    def query_worklist(self, date: str = None) -> List[Dataset]:
        """查询PACS工作列表"""
        from pynetdicom.sop_class import ModalityWorklistInformationFind
        
        self.ae.add_requested_context(ModalityWorklistInformationFind)
        
        # 创建查询数据集
        query = Dataset()
        query.PatientName = ''
        query.PatientID = ''
        query.ScheduledProcedureStepSequence = [Dataset()]
        query.ScheduledProcedureStepSequence[0].Modality = 'CT'
        query.ScheduledProcedureStepSequence[0].ScheduledStationAETitle = ''
        
        if date:
            query.ScheduledProcedureStepSequence[0].ScheduledProcedureStepStartDate = date
        
        # 执行查询
        assoc = self.ae.associate(self.pacs_host, self.pacs_port)
        
        results = []
        if assoc.is_established:
            responses = assoc.send_c_find(query, ModalityWorklistInformationFind)
            
            for (status, identifier) in responses:
                if status and identifier:
                    results.append(identifier)
            
            assoc.release()
        
        return results
```


## 临床验证

### 多中心临床试验设计

```markdown
# LungAI临床验证方案

## 1. 研究目标

### 主要目标
评估LungAI系统在肺结节检测和良恶性评估中的诊断性能

### 次要目标
- 评估系统的灵敏度和特异性
- 评估假阳性率
- 评估与放射科医生诊断的一致性
- 评估系统在不同人群和扫描参数下的表现

## 2. 研究设计

### 研究类型
回顾性、多中心、诊断准确性研究

### 研究中心
- 三级甲等医院放射科: 5家
- 肺癌筛查中心: 3家
- 总计: 8个中心

### 样本量计算
- 预期灵敏度: 95%
- 预期假阳性率: 0.5个/例
- 置信区间: 95%
- 精度: ±2%
- 计算样本量: 1500例CT扫描

### 纳入标准
- 胸部CT扫描
- 层厚 ≤1.5mm
- 图像质量合格
- 有完整的临床和病理资料

### 排除标准
- 图像质量不合格
- 既往肺部手术史
- 严重肺部疾病影响判读
- 数据不完整

## 3. 研究流程

### 数据收集
1. 收集1500例胸部CT扫描
2. 包含不同扫描参数和设备
3. 涵盖不同大小和类型的结节
4. 包含正常病例和阳性病例

### AI分析
1. 所有CT扫描通过LungAI系统分析
2. 记录检测到的所有结节
3. 记录每个结节的特征和评分
4. 记录处理时间

### 金标准建立
1. 3名资深放射科医生独立阅片
2. 不知晓AI分析结果
3. 标注所有≥3mm的结节
4. 不一致时由专家组讨论决定
5. 病理结果作为良恶性判断的金标准

### 数据分析
- 结节检测性能
- 假阳性分析
- 良恶性分类性能
- 亚组分析

## 4. 统计分析

### 主要终点
- 灵敏度 (按结节计算)
- 假阳性率 (每例CT的假阳性数)
- 良恶性分类准确率
- AUC

### 次要终点
- 不同大小结节的检测率
- 不同类型结节的检测率
- 处理时间
- 与医生诊断的一致性

### 统计方法
- FROC (Free-Response ROC) 分析
- 灵敏度分析（分层）
- ROC曲线分析
- Kappa一致性分析
```

### 临床验证结果

```python
# clinical_validation.py
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, roc_curve, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

class LungAIValidation:
    """LungAI临床验证分析"""
    
    def __init__(self, results_csv: str, ground_truth_csv: str):
        self.ai_results = pd.read_csv(results_csv)
        self.ground_truth = pd.read_csv(ground_truth_csv)
    
    def calculate_detection_metrics(self):
        """计算检测性能指标"""
        
        # 按结节大小分组
        size_groups = {
            'small': (3, 6),      # 3-6mm
            'medium': (6, 10),    # 6-10mm
            'large': (10, 30)     # >10mm
        }
        
        metrics = {}
        
        for group_name, (min_size, max_size) in size_groups.items():
            # 筛选该大小范围的结节
            gt_nodules = self.ground_truth[
                (self.ground_truth['diameter'] >= min_size) &
                (self.ground_truth['diameter'] < max_size)
            ]
            
            # 计算检测率
            detected = 0
            for _, gt_nodule in gt_nodules.iterrows():
                # 检查是否被AI检测到（距离<5mm）
                ai_nodules = self.ai_results[
                    self.ai_results['study_id'] == gt_nodule['study_id']
                ]
                
                for _, ai_nodule in ai_nodules.iterrows():
                    distance = self._calculate_distance(
                        gt_nodule[['x', 'y', 'z']].values,
                        ai_nodule[['x', 'y', 'z']].values
                    )
                    
                    if distance < 5.0:  # 5mm阈值
                        detected += 1
                        break
            
            sensitivity = detected / len(gt_nodules) if len(gt_nodules) > 0 else 0
            
            metrics[group_name] = {
                'total_nodules': len(gt_nodules),
                'detected': detected,
                'sensitivity': sensitivity
            }
        
        # 计算总体灵敏度
        total_gt = len(self.ground_truth)
        total_detected = sum(m['detected'] for m in metrics.values())
        overall_sensitivity = total_detected / total_gt if total_gt > 0 else 0
        
        metrics['overall'] = {
            'total_nodules': total_gt,
            'detected': total_detected,
            'sensitivity': overall_sensitivity
        }
        
        return metrics
    
    def calculate_false_positive_rate(self):
        """计算假阳性率"""
        
        # 按病例统计
        studies = self.ai_results['study_id'].unique()
        
        fp_counts = []
        
        for study_id in studies:
            ai_nodules = self.ai_results[self.ai_results['study_id'] == study_id]
            gt_nodules = self.ground_truth[self.ground_truth['study_id'] == study_id]
            
            fp_count = 0
            
            for _, ai_nodule in ai_nodules.iterrows():
                # 检查是否为假阳性
                is_fp = True
                
                for _, gt_nodule in gt_nodules.iterrows():
                    distance = self._calculate_distance(
                        ai_nodule[['x', 'y', 'z']].values,
                        gt_nodule[['x', 'y', 'z']].values
                    )
                    
                    if distance < 5.0:
                        is_fp = False
                        break
                
                if is_fp:
                    fp_count += 1
            
            fp_counts.append(fp_count)
        
        # 计算统计量
        fp_rate = {
            'mean': np.mean(fp_counts),
            'median': np.median(fp_counts),
            'std': np.std(fp_counts),
            'max': np.max(fp_counts),
            'per_case_distribution': fp_counts
        }
        
        return fp_rate
    
    def calculate_malignancy_metrics(self):
        """计算良恶性分类性能"""
        
        # 匹配AI检测和金标准
        matched_pairs = self._match_nodules()
        
        if len(matched_pairs) == 0:
            return None
        
        # 提取标签和预测
        y_true = [pair['gt_malignant'] for pair in matched_pairs]
        y_pred = [pair['ai_malignant'] for pair in matched_pairs]
        y_score = [pair['ai_score'] for pair in matched_pairs]
        
        # 计算指标
        cm = confusion_matrix(y_true, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        
        # AUC
        auc = roc_auc_score(y_true, y_score)
        
        metrics = {
            'confusion_matrix': cm,
            'sensitivity': sensitivity,
            'specificity': specificity,
            'ppv': ppv,
            'npv': npv,
            'accuracy': accuracy,
            'auc': auc,
            'total_nodules': len(matched_pairs)
        }
        
        return metrics
    
    def _match_nodules(self):
        """匹配AI检测和金标准结节"""
        matched_pairs = []
        
        for _, gt_nodule in self.ground_truth.iterrows():
            if pd.isna(gt_nodule.get('malignant')):
                continue
            
            ai_nodules = self.ai_results[
                self.ai_results['study_id'] == gt_nodule['study_id']
            ]
            
            best_match = None
            min_distance = float('inf')
            
            for _, ai_nodule in ai_nodules.iterrows():
                distance = self._calculate_distance(
                    gt_nodule[['x', 'y', 'z']].values,
                    ai_nodule[['x', 'y', 'z']].values
                )
                
                if distance < min_distance and distance < 5.0:
                    min_distance = distance
                    best_match = ai_nodule
            
            if best_match is not None:
                matched_pairs.append({
                    'gt_malignant': int(gt_nodule['malignant']),
                    'ai_malignant': int(best_match['malignancy_class'] == 'malignant'),
                    'ai_score': float(best_match['malignancy_score'])
                })
        
        return matched_pairs
    
    def _calculate_distance(self, pos1, pos2):
        """计算3D欧氏距离"""
        return np.linalg.norm(pos1 - pos2)
    
    def plot_froc_curve(self):
        """绘制FROC曲线"""
        # 计算不同阈值下的灵敏度和假阳性率
        thresholds = np.linspace(0, 1, 50)
        
        sensitivities = []
        fp_rates = []
        
        for threshold in thresholds:
            # 过滤AI结果
            filtered_results = self.ai_results[
                self.ai_results['confidence'] >= threshold
            ]
            
            # 计算灵敏度
            detected = 0
            for _, gt_nodule in self.ground_truth.iterrows():
                ai_nodules = filtered_results[
                    filtered_results['study_id'] == gt_nodule['study_id']
                ]
                
                for _, ai_nodule in ai_nodules.iterrows():
                    distance = self._calculate_distance(
                        gt_nodule[['x', 'y', 'z']].values,
                        ai_nodule[['x', 'y', 'z']].values
                    )
                    
                    if distance < 5.0:
                        detected += 1
                        break
            
            sensitivity = detected / len(self.ground_truth)
            sensitivities.append(sensitivity)
            
            # 计算假阳性率
            studies = filtered_results['study_id'].unique()
            total_fp = 0
            
            for study_id in studies:
                ai_nodules = filtered_results[filtered_results['study_id'] == study_id]
                gt_nodules = self.ground_truth[self.ground_truth['study_id'] == study_id]
                
                for _, ai_nodule in ai_nodules.iterrows():
                    is_fp = True
                    
                    for _, gt_nodule in gt_nodules.iterrows():
                        distance = self._calculate_distance(
                            ai_nodule[['x', 'y', 'z']].values,
                            gt_nodule[['x', 'y', 'z']].values
                        )
                        
                        if distance < 5.0:
                            is_fp = False
                            break
                    
                    if is_fp:
                        total_fp += 1
            
            fp_rate = total_fp / len(studies) if len(studies) > 0 else 0
            fp_rates.append(fp_rate)
        
        # 绘制FROC曲线
        plt.figure(figsize=(10, 6))
        plt.plot(fp_rates, sensitivities, 'b-', linewidth=2, label='LungAI')
        plt.xlabel('False Positives per Scan')
        plt.ylabel('Sensitivity')
        plt.title('FROC Curve - Nodule Detection Performance')
        plt.grid(True, alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.savefig('froc_curve.png', dpi=300)
        plt.close()
    
    def generate_validation_report(self):
        """生成验证报告"""
        
        # 计算所有指标
        detection_metrics = self.calculate_detection_metrics()
        fp_rate = self.calculate_false_positive_rate()
        malignancy_metrics = self.calculate_malignancy_metrics()
        
        report = f"""
# LungAI临床验证报告

## 1. 研究概况

- 总病例数: {len(self.ai_results['study_id'].unique())}
- 总结节数: {len(self.ground_truth)}
- 研究中心数: {self.ground_truth['center_id'].nunique()}
- 数据收集时间: {self.ground_truth['scan_date'].min()} 至 {self.ground_truth['scan_date'].max()}

## 2. 结节检测性能

### 2.1 按大小分层的灵敏度

"""
        
        for size_group, metrics in detection_metrics.items():
            if size_group != 'overall':
                report += f"\n**{size_group.capitalize()} 结节**\n"
                report += f"- 总数: {metrics['total_nodules']}\n"
                report += f"- 检测到: {metrics['detected']}\n"
                report += f"- 灵敏度: {metrics['sensitivity']:.2%}\n"
        
        report += f"\n**总体**\n"
        report += f"- 总结节数: {detection_metrics['overall']['total_nodules']}\n"
        report += f"- 检测到: {detection_metrics['overall']['detected']}\n"
        report += f"- 总体灵敏度: {detection_metrics['overall']['sensitivity']:.2%}\n"
        
        report += f"\n### 2.2 假阳性率\n\n"
        report += f"- 平均假阳性数/例: {fp_rate['mean']:.2f}\n"
        report += f"- 中位数: {fp_rate['median']:.1f}\n"
        report += f"- 标准差: {fp_rate['std']:.2f}\n"
        report += f"- 最大值: {fp_rate['max']}\n"
        
        if malignancy_metrics:
            report += f"\n## 3. 良恶性分类性能\n\n"
            report += f"- 灵敏度: {malignancy_metrics['sensitivity']:.2%}\n"
            report += f"- 特异性: {malignancy_metrics['specificity']:.2%}\n"
            report += f"- 阳性预测值: {malignancy_metrics['ppv']:.2%}\n"
            report += f"- 阴性预测值: {malignancy_metrics['npv']:.2%}\n"
            report += f"- 准确率: {malignancy_metrics['accuracy']:.2%}\n"
            report += f"- AUC: {malignancy_metrics['auc']:.3f}\n"
        
        return report

# 使用示例
validator = LungAIValidation('ai_results.csv', 'ground_truth.csv')
report = validator.generate_validation_report()
print(report)

validator.plot_froc_curve()
```

### 实际验证结果

```python
# 基于实际临床试验的结果示例

validation_results = {
    'study_info': {
        'total_cases': 1523,
        'total_nodules': 2847,
        'centers': 8,
        'duration': '2024-06 至 2025-12'
    },
    
    'detection_performance': {
        'overall_sensitivity': 0.953,
        'small_nodules_3_6mm': {
            'count': 1245,
            'sensitivity': 0.887
        },
        'medium_nodules_6_10mm': {
            'count': 982,
            'sensitivity': 0.976
        },
        'large_nodules_10mm': {
            'count': 620,
            'sensitivity': 0.995
        }
    },
    
    'false_positive_rate': {
        'mean_per_case': 0.42,
        'median': 0,
        'std': 0.68,
        'max': 4
    },
    
    'malignancy_classification': {
        'sensitivity': 0.921,
        'specificity': 0.884,
        'ppv': 0.756,
        'npv': 0.967,
        'accuracy': 0.895,
        'auc': 0.947
    },
    
    'processing_time': {
        'mean_seconds': 45.3,
        'median_seconds': 42.1,
        'std_seconds': 12.7
    }
}
```


## 法规合规

### IEC 62304 软件开发

#### 软件安全分类

根据IEC 62304标准，LungAI系统被分类为**Class B**（中等风险）软件：

- 系统用于辅助诊断，不直接控制治疗
- 错误诊断可能导致轻微伤害
- 最终诊断由医生确认

#### 软件开发计划

```markdown
# LungAI软件开发计划

## 1. 项目概述

### 1.1 产品描述
LungAI智能肺结节检测系统，用于胸部CT图像中肺结节的自动检测、分割和良恶性评估。

### 1.2 预期用途
辅助放射科医生进行肺结节筛查和诊断，提高检测效率和准确性。

### 1.3 安全分类
Class B - 中等风险

## 2. 组织架构

### 2.1 项目团队
- 项目经理: 1名
- AI算法工程师: 3名
- 软件开发工程师: 4名
- 测试工程师: 2名
- 质量工程师: 1名
- 临床专家: 2名

### 2.2 职责分工
- 项目经理: 整体协调和进度管理
- AI工程师: 模型设计、训练和优化
- 软件工程师: 系统架构、接口开发
- 测试工程师: 测试计划和执行
- 质量工程师: 质量保证和合规审查
- 临床专家: 需求定义和临床验证

## 3. 开发流程

### 3.1 需求分析
- 收集用户需求
- 定义功能需求
- 定义性能需求
- 定义安全需求
- 需求评审和批准

### 3.2 架构设计
- 系统架构设计
- 软件架构设计
- 接口设计
- 数据库设计
- 设计评审和批准

### 3.3 详细设计
- 模块详细设计
- AI模型设计
- 算法设计
- 详细设计评审

### 3.4 实现
- 编码规范
- 代码审查
- 单元测试
- 版本控制

### 3.5 集成与测试
- 集成测试
- 系统测试
- 性能测试
- 安全测试

### 3.6 验证与确认
- 需求追溯
- 临床验证
- 用户验收测试

## 4. 风险管理

### 4.1 风险识别
- 技术风险
- 临床风险
- 数据安全风险
- 合规风险

### 4.2 风险评估
- 严重性评估
- 概率评估
- 风险等级确定

### 4.3 风险控制
- 风险缓解措施
- 残余风险评估
- 风险监控

## 5. 配置管理

### 5.1 版本控制
- Git版本控制
- 分支管理策略
- 标签管理

### 5.2 变更管理
- 变更请求流程
- 变更评审
- 变更实施
- 变更验证

### 5.3 发布管理
- 发布计划
- 发布检查清单
- 发布批准

## 6. 问题解决

### 6.1 问题报告
- 问题跟踪系统
- 问题分类
- 优先级定义

### 6.2 问题分析
- 根因分析
- 影响评估

### 6.3 问题解决
- 解决方案设计
- 实施和验证
- 问题关闭

## 7. 文档管理

### 7.1 必需文档
- 软件需求规格说明 (SRS)
- 软件架构设计文档 (SAD)
- 软件详细设计文档 (SDD)
- 测试计划和报告
- 用户手册
- 维护手册

### 7.2 文档控制
- 文档编号规则
- 版本管理
- 审批流程
- 分发控制

## 8. 维护计划

### 8.1 维护类型
- 纠正性维护
- 预防性维护
- 完善性维护
- 适应性维护

### 8.2 维护流程
- 维护请求
- 影响分析
- 实施和测试
- 发布和部署
```

#### 软件需求规格说明 (SRS)

```markdown
# LungAI软件需求规格说明

## 1. 功能需求

### FR-001: DICOM图像加载
**描述**: 系统应能够加载和解析DICOM格式的CT图像  
**优先级**: 高  
**验证方法**: 测试

**详细需求**:
- 支持标准DICOM格式
- 支持多帧DICOM
- 提取必要的元数据（间距、方向等）
- 处理不同的传输语法

### FR-002: 图像预处理
**描述**: 系统应对CT图像进行预处理  
**优先级**: 高  
**验证方法**: 测试

**详细需求**:
- HU值归一化
- 重采样到统一间距（1mm各向同性）
- 肺部区域提取
- 图像质量检查

### FR-003: 肺部分割
**描述**: 系统应自动分割肺部区域  
**优先级**: 高  
**验证方法**: 测试

**详细需求**:
- 分割左右肺
- Dice系数 ≥0.95
- 处理时间 <10秒

### FR-004: 结节检测
**描述**: 系统应检测肺部结节  
**优先级**: 高  
**验证方法**: 临床验证

**详细需求**:
- 检测≥3mm的结节
- 灵敏度 ≥95%（≥6mm结节）
- 假阳性率 ≤0.5个/例
- 提供结节位置、大小、体积

### FR-005: 良恶性评估
**描述**: 系统应评估结节的良恶性  
**优先级**: 高  
**验证方法**: 临床验证

**详细需求**:
- 提供恶性概率评分（0-1）
- 分类为良性或恶性
- AUC ≥0.90
- 提供置信度

### FR-006: 结果可视化
**描述**: 系统应提供结果可视化  
**优先级**: 中  
**验证方法**: 用户测试

**详细需求**:
- 3D结节标注
- 多平面重建（MPR）
- 结节特征显示
- 报告生成

### FR-007: PACS集成
**描述**: 系统应与PACS系统集成  
**优先级**: 中  
**验证方法**: 集成测试

**详细需求**:
- DICOM C-FIND查询
- DICOM C-STORE发送
- 结构化报告（SR）
- 工作列表（Worklist）

## 2. 性能需求

### PR-001: 处理时间
- 单例CT扫描分析时间 ≤60秒
- 肺部分割时间 ≤10秒
- 结节检测时间 ≤30秒
- 良恶性评估时间 ≤5秒/结节

### PR-002: 并发处理
- 支持至少10个并发分析任务
- 队列管理
- 负载均衡

### PR-003: 可用性
- 系统可用性 ≥99.5%
- 平均故障间隔时间(MTBF) ≥720小时
- 平均修复时间(MTTR) ≤4小时

## 3. 安全需求

### SR-001: 数据加密
- 传输加密（TLS 1.2+）
- 静态数据加密（AES-256）
- 密钥管理

### SR-002: 访问控制
- 基于角色的访问控制(RBAC)
- 用户认证
- 操作审计日志

### SR-003: 数据隐私
- HIPAA合规
- 数据匿名化
- 患者隐私保护

## 4. 接口需求

### IR-001: DICOM接口
- 支持DICOM 3.0标准
- C-FIND, C-STORE, C-MOVE
- 结构化报告

### IR-002: REST API
- RESTful API设计
- JSON数据格式
- API版本管理
- API文档

### IR-003: 用户界面
- Web界面
- 响应式设计
- 多语言支持（中文、英文）

## 5. 质量需求

### QR-001: 可靠性
- 无严重缺陷
- 关键缺陷 ≤5个
- 一般缺陷 ≤20个

### QR-002: 可维护性
- 代码注释率 ≥30%
- 模块化设计
- 日志记录

### QR-003: 可测试性
- 单元测试覆盖率 ≥80%
- 集成测试覆盖率 ≥90%
- 自动化测试

## 6. 法规需求

### RR-001: IEC 62304合规
- Class B软件开发流程
- 必需文档
- 追溯性

### RR-002: FDA合规
- 软件验证文档
- 510(k)申报资料
- 临床验证

### RR-003: HIPAA合规
- 数据安全
- 隐私保护
- 审计追踪
```


#### 风险管理文档

```markdown
# LungAI风险管理文档

## 1. 风险识别

### 1.1 技术风险

#### R-001: 结节漏检
**描述**: AI系统未能检测到实际存在的结节  
**严重性**: 严重  
**概率**: 中等  
**风险等级**: 高

**可能原因**:
- 结节过小（<3mm）
- 结节位置特殊
- 图像质量差
- 模型训练不足

**风险控制措施**:
- 设置最小检测阈值（3mm）
- 多模型集成
- 图像质量检查
- 持续模型优化
- 医生最终审核

**残余风险**: 中等

#### R-002: 假阳性过高
**描述**: 系统检测到过多的假阳性结节  
**严重性**: 中等  
**概率**: 中等  
**风险等级**: 中等

**可能原因**:
- 血管误判
- 淋巴结误判
- 图像伪影

**风险控制措施**:
- 假阳性抑制算法
- 置信度阈值设置
- 后处理过滤
- 用户可调整灵敏度

**残余风险**: 低

#### R-003: 良恶性误判
**描述**: 系统错误评估结节的良恶性  
**严重性**: 严重  
**概率**: 低  
**风险等级**: 中等

**可能原因**:
- 特征提取不准确
- 训练数据偏差
- 罕见病例

**风险控制措施**:
- 提供概率评分而非绝对判断
- 显示置信度
- 医生最终决策
- 持续学习和更新

**残余风险**: 低

### 1.2 数据安全风险

#### R-004: 患者数据泄露
**描述**: 患者医疗数据被未授权访问  
**严重性**: 严重  
**概率**: 低  
**风险等级**: 中等

**可能原因**:
- 网络攻击
- 内部泄露
- 系统漏洞

**风险控制措施**:
- 数据加密（传输和存储）
- 访问控制和认证
- 审计日志
- 定期安全审计
- 数据匿名化

**残余风险**: 低

### 1.3 系统可用性风险

#### R-005: 系统故障
**描述**: 系统无法正常运行  
**严重性**: 中等  
**概率**: 低  
**风险等级**: 低

**可能原因**:
- 硬件故障
- 软件缺陷
- 网络中断

**风险控制措施**:
- 冗余设计
- 自动故障转移
- 定期备份
- 监控和告警
- 快速恢复机制

**残余风险**: 低

## 2. 风险评估矩阵

| 风险ID | 描述 | 严重性 | 概率 | 风险等级 | 控制措施 | 残余风险 |
|--------|------|--------|------|----------|----------|----------|
| R-001 | 结节漏检 | 严重 | 中等 | 高 | 多模型集成、医生审核 | 中等 |
| R-002 | 假阳性过高 | 中等 | 中等 | 中等 | 假阳性抑制、阈值调整 | 低 |
| R-003 | 良恶性误判 | 严重 | 低 | 中等 | 概率评分、医生决策 | 低 |
| R-004 | 数据泄露 | 严重 | 低 | 中等 | 加密、访问控制 | 低 |
| R-005 | 系统故障 | 中等 | 低 | 低 | 冗余设计、监控 | 低 |

## 3. 风险控制验证

### R-001验证
- 临床验证：灵敏度≥95%（≥6mm结节）
- 测试用例：1500例CT扫描
- 验证结果：灵敏度97.6%，满足要求

### R-002验证
- 临床验证：假阳性率≤0.5个/例
- 测试用例：1500例CT扫描
- 验证结果：假阳性率0.42个/例，满足要求

### R-003验证
- 临床验证：AUC≥0.90
- 测试用例：620个病理确认结节
- 验证结果：AUC=0.947，满足要求

### R-004验证
- 安全审计：通过第三方安全评估
- 渗透测试：无高危漏洞
- 合规审查：符合HIPAA要求

### R-005验证
- 可用性测试：99.7%可用性
- 故障恢复测试：MTTR<2小时
- 负载测试：支持20并发任务

## 4. 风险监控

### 4.1 上市后监控
- 收集用户反馈
- 监控系统性能
- 分析不良事件
- 定期风险评审

### 4.2 持续改进
- 模型更新和优化
- 软件缺陷修复
- 安全补丁
- 功能增强
```

## 部署与运维

### Docker部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  # AI推理服务
  inference-service:
    build:
      context: .
      dockerfile: Dockerfile.inference
    image: lungai/inference:latest
    container_name: lungai-inference
    ports:
      - "8000:8000"
    environment:
      - CUDA_VISIBLE_DEVICES=0
      - MODEL_PATH=/models
      - LOG_LEVEL=INFO
    volumes:
      - ./models:/models:ro
      - ./logs:/logs
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
  
  # PostgreSQL数据库
  postgres:
    image: postgres:14
    container_name: lungai-postgres
    environment:
      - POSTGRES_DB=lungai
      - POSTGRES_USER=lungai
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    restart: unless-stopped
  
  # Redis缓存
  redis:
    image: redis:7-alpine
    container_name: lungai-redis
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped
  
  # Nginx反向代理
  nginx:
    image: nginx:alpine
    container_name: lungai-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - inference-service
    restart: unless-stopped
  
  # Prometheus监控
  prometheus:
    image: prom/prometheus:latest
    container_name: lungai-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    restart: unless-stopped
  
  # Grafana可视化
  grafana:
    image: grafana/grafana:latest
    container_name: lungai-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:
  prometheus-data:
  grafana-data:
```

### Kubernetes部署

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lungai-inference
  namespace: medical-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: lungai-inference
  template:
    metadata:
      labels:
        app: lungai-inference
    spec:
      containers:
      - name: inference
        image: lungai/inference:v1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: MODEL_PATH
          value: "/models"
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "8Gi"
            cpu: "4"
            nvidia.com/gpu: "1"
          limits:
            memory: "16Gi"
            cpu: "8"
            nvidia.com/gpu: "1"
        volumeMounts:
        - name: models
          mountPath: /models
          readOnly: true
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: lungai-models-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: lungai-inference-service
  namespace: medical-ai
spec:
  selector:
    app: lungai-inference
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: lungai-inference-hpa
  namespace: medical-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: lungai-inference
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```


### 监控和日志

```python
# monitoring.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import logging
import time
from functools import wraps

# Prometheus指标
inference_requests_total = Counter(
    'lungai_inference_requests_total',
    'Total number of inference requests',
    ['status']
)

inference_duration_seconds = Histogram(
    'lungai_inference_duration_seconds',
    'Inference duration in seconds',
    buckets=[1, 5, 10, 30, 60, 120]
)

nodules_detected_total = Counter(
    'lungai_nodules_detected_total',
    'Total number of nodules detected'
)

active_inference_tasks = Gauge(
    'lungai_active_inference_tasks',
    'Number of active inference tasks'
)

model_load_time_seconds = Gauge(
    'lungai_model_load_time_seconds',
    'Model loading time in seconds'
)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/lungai.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('LungAI')

def monitor_inference(func):
    """推理监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        active_inference_tasks.inc()
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            
            # 记录成功
            inference_requests_total.labels(status='success').inc()
            
            # 记录检测到的结节数
            if hasattr(result, 'num_nodules'):
                nodules_detected_total.inc(result.num_nodules)
            
            # 记录处理时间
            duration = time.time() - start_time
            inference_duration_seconds.observe(duration)
            
            logger.info(f"Inference completed: {result.study_id}, "
                       f"nodules={result.num_nodules}, duration={duration:.2f}s")
            
            return result
            
        except Exception as e:
            # 记录失败
            inference_requests_total.labels(status='error').inc()
            logger.error(f"Inference failed: {str(e)}", exc_info=True)
            raise
            
        finally:
            active_inference_tasks.dec()
    
    return wrapper

# 启动Prometheus metrics服务器
def start_metrics_server(port=9091):
    """启动metrics服务器"""
    start_http_server(port)
    logger.info(f"Metrics server started on port {port}")
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'lungai-inference'
    static_configs:
      - targets: ['inference-service:9091']
    
  - job_name: 'lungai-system'
    static_configs:
      - targets: ['node-exporter:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - 'alerts.yml'
```

```yaml
# alerts.yml
groups:
  - name: lungai_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(lungai_inference_requests_total{status="error"}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors/sec"
      
      - alert: SlowInference
        expr: histogram_quantile(0.95, lungai_inference_duration_seconds) > 120
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Slow inference detected"
          description: "95th percentile inference time is {{ $value }}s"
      
      - alert: ServiceDown
        expr: up{job="lungai-inference"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "LungAI service is down"
          description: "Service has been down for more than 2 minutes"
```

### 性能优化

```python
# performance_optimization.py
import torch
import torch.nn as nn
from torch.cuda.amp import autocast, GradScaler
import tensorrt as trt
import onnx

class ModelOptimizer:
    """模型优化器"""
    
    @staticmethod
    def quantize_model(model, calibration_data):
        """模型量化"""
        # 动态量化
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            {nn.Linear, nn.Conv3d},
            dtype=torch.qint8
        )
        
        return quantized_model
    
    @staticmethod
    def export_to_onnx(model, input_shape, output_path):
        """导出为ONNX格式"""
        dummy_input = torch.randn(input_shape)
        
        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=13,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={
                'input': {0: 'batch_size'},
                'output': {0: 'batch_size'}
            }
        )
        
        print(f"Model exported to {output_path}")
    
    @staticmethod
    def convert_to_tensorrt(onnx_path, engine_path):
        """转换为TensorRT引擎"""
        logger = trt.Logger(trt.Logger.WARNING)
        builder = trt.Builder(logger)
        network = builder.create_network(
            1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
        )
        parser = trt.OnnxParser(network, logger)
        
        # 解析ONNX模型
        with open(onnx_path, 'rb') as model:
            if not parser.parse(model.read()):
                for error in range(parser.num_errors):
                    print(parser.get_error(error))
                return None
        
        # 配置构建器
        config = builder.create_builder_config()
        config.max_workspace_size = 4 << 30  # 4GB
        config.set_flag(trt.BuilderFlag.FP16)  # 启用FP16
        
        # 构建引擎
        engine = builder.build_engine(network, config)
        
        # 保存引擎
        with open(engine_path, 'wb') as f:
            f.write(engine.serialize())
        
        print(f"TensorRT engine saved to {engine_path}")
        
        return engine

class InferencePipeline:
    """优化的推理管道"""
    
    def __init__(self, model, device='cuda'):
        self.model = model.to(device)
        self.model.eval()
        self.device = device
        self.scaler = GradScaler()
    
    @torch.no_grad()
    def inference_with_amp(self, input_data):
        """使用自动混合精度推理"""
        input_tensor = torch.from_numpy(input_data).to(self.device)
        
        with autocast():
            output = self.model(input_tensor)
        
        return output.cpu().numpy()
    
    def batch_inference(self, data_list, batch_size=4):
        """批量推理"""
        results = []
        
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i+batch_size]
            
            # 转换为tensor
            batch_tensor = torch.stack([
                torch.from_numpy(data) for data in batch
            ]).to(self.device)
            
            # 推理
            with autocast():
                batch_output = self.model(batch_tensor)
            
            results.extend(batch_output.cpu().numpy())
        
        return results

# 使用示例
optimizer = ModelOptimizer()

# 1. 量化模型
quantized_model = optimizer.quantize_model(model, calibration_data)

# 2. 导出ONNX
optimizer.export_to_onnx(
    model,
    input_shape=(1, 1, 128, 256, 256),
    output_path='models/lungai.onnx'
)

# 3. 转换TensorRT
optimizer.convert_to_tensorrt(
    'models/lungai.onnx',
    'models/lungai.trt'
)

# 4. 优化推理
pipeline = InferencePipeline(model)
result = pipeline.inference_with_amp(input_data)
```

## 总结

### 系统特点

1. **高精度检测**
   - 整体灵敏度: 95.3%
   - 假阳性率: 0.42个/例
   - 良恶性分类AUC: 0.947

2. **高效处理**
   - 平均处理时间: 45秒/例
   - 支持批量处理
   - GPU加速

3. **完整工作流**
   - DICOM图像加载
   - 自动肺部分割
   - 结节检测和分类
   - PACS集成
   - 结构化报告

4. **法规合规**
   - IEC 62304 Class B
   - 完整的开发文档
   - 风险管理
   - 临床验证

5. **生产就绪**
   - Docker容器化
   - Kubernetes编排
   - 监控和告警
   - 性能优化

### 技术亮点

- **3D深度学习**: 充分利用CT的3D信息
- **多模型集成**: 分割、检测、分类三个模型协同
- **端到端流程**: 从DICOM到结构化报告
- **高性能推理**: TensorRT优化，混合精度
- **可扩展架构**: 微服务设计，易于扩展

### 应用价值

1. **提高筛查效率**: 减少放射科医生工作量
2. **降低漏诊率**: AI辅助提高检测灵敏度
3. **标准化诊断**: 减少主观差异
4. **早期发现**: 提高早期肺癌检出率
5. **降低成本**: 提高筛查项目可行性

### 未来展望

1. **模型优化**
   - 更大规模的训练数据
   - 多中心数据集成
   - 持续学习机制

2. **功能扩展**
   - 结节生长速度评估
   - 多时相对比分析
   - 其他肺部疾病检测

3. **技术升级**
   - Transformer架构
   - 自监督学习
   - 联邦学习

4. **临床整合**
   - 临床决策支持
   - 个性化风险评估
   - 治疗方案推荐

---

**文档版本**: v1.0  
**最后更新**: 2026年2月10日  
**作者**: LungAI开发团队  
**审核**: 医疗AI专家组
