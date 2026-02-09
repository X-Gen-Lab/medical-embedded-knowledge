---
title: ADC/DAC转换器
description: 掌握ADC（模数转换器）和DAC（数模转换器）的原理、配置和应用，学习如何在医疗器械中实现精确的模拟信号采集和输出
difficulty: 中级
estimated_time: 50分钟
tags:
- ADC
- DAC
- 模数转换
- 数模转换
- 信号采集
- 传感器
related_modules:
- zh/technical-knowledge/signal-processing
- zh/technical-knowledge/hardware-interfaces/gpio
- zh/technical-knowledge/rtos/interrupt-handling
last_updated: '2026-02-09'
version: '1.0'
language: zh
---

# ADC/DAC转换器

## 学习目标

完成本模块后，你将能够：
- 理解ADC和DAC的工作原理和关键参数
- 配置和使用微控制器的ADC外设
- 实现精确的模拟信号采集
- 理解并应用DAC进行信号输出
- 在医疗器械中实现高质量的信号处理

## 前置知识

- 模拟电路基础
- 数字信号处理概念
- C语言编程
- 微控制器外设编程

## 内容

### 概念介绍

ADC（Analog-to-Digital Converter，模数转换器）将连续的模拟信号转换为离散的数字值，DAC（Digital-to-Analog Converter，数模转换器）则执行相反的操作。它们是嵌入式系统与现实世界交互的桥梁。

**在医疗器械中的应用**：
- **ADC**：采集生理信号（ECG、血压、体温、血氧等）
- **DAC**：生成控制信号、音频输出、波形发生器


### ADC关键参数

#### 分辨率（Resolution）

分辨率决定ADC能够区分的最小电压变化。

- **12位ADC**：2^12 = 4096个离散值
- **16位ADC**：2^16 = 65536个离散值

```
参考电压 = 3.3V，12位ADC
LSB = 3.3V / 4096 ≈ 0.806mV
```

**说明**: 这是ADC分辨率的计算示例。12位ADC有4096(2^12)个量化级别，LSB(最低有效位)表示最小可分辨的电压变化，等于参考电压除以量化级别数。分辨率越高，能检测的电压变化越小。


#### 采样率（Sampling Rate）

每秒采集的样本数，单位为SPS（Samples Per Second）或Hz。

**奈奎斯特定理**：采样率必须至少是信号最高频率的2倍。

```
信号最高频率 = 100Hz
最小采样率 = 200Hz
实际建议 = 500Hz - 1kHz（留有余量）
```

**说明**: 这是奈奎斯特采样定理的应用示例。采样率必须至少是信号最高频率的2倍才能准确重建信号。实际应用中建议使用5-10倍的采样率以留有余量，避免混叠失真。


#### 转换时间（Conversion Time）

完成一次ADC转换所需的时间。

```
转换时间 = 采样时间 + 转换周期
```

**说明**: 这是ADC转换时间的组成。采样时间是ADC采集输入信号的时间，转换周期是将采样值转换为数字值的时间。总转换时间决定了ADC的最大采样率。


#### 精度和误差

- **DNL（Differential Non-Linearity）**：微分非线性
- **INL（Integral Non-Linearity）**：积分非线性
- **偏移误差（Offset Error）**：零点偏移
- **增益误差（Gain Error）**：满量程误差

### ADC配置和使用

#### STM32 HAL库ADC配置

```c
#include "stm32f4xx_hal.h"

// ADC句柄
ADC_HandleTypeDef hadc1;

// ADC初始化
void ADC_Init(void) {
    ADC_ChannelConfTypeDef sConfig = {0};
    
    // 配置ADC
    hadc1.Instance = ADC1;
    hadc1.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV4;
    hadc1.Init.Resolution = ADC_RESOLUTION_12B;           // 12位分辨率
    hadc1.Init.ScanConvMode = DISABLE;                    // 单通道模式
    hadc1.Init.ContinuousConvMode = DISABLE;              // 单次转换
    hadc1.Init.DiscontinuousConvMode = DISABLE;
    hadc1.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;
    hadc1.Init.DataAlign = ADC_DATAALIGN_RIGHT;           // 右对齐
    hadc1.Init.NbrOfConversion = 1;
    hadc1.Init.DMAContinuousRequests = DISABLE;
    hadc1.Init.EOCSelection = ADC_EOC_SINGLE_CONV;
    
    if (HAL_ADC_Init(&hadc1) != HAL_OK) {
        Error_Handler();
    }
    
    // 配置ADC通道
    sConfig.Channel = ADC_CHANNEL_0;                      // 通道0 (PA0)
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_84CYCLES;       // 采样时间
    
    if (HAL_ADC_ConfigChannel(&hadc1, &sConfig) != HAL_OK) {
        Error_Handler();
    }
}

// GPIO和时钟配置
void HAL_ADC_MspInit(ADC_HandleTypeDef* hadc) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    if(hadc->Instance == ADC1) {
        // 使能时钟
        __HAL_RCC_ADC1_CLK_ENABLE();
        __HAL_RCC_GPIOA_CLK_ENABLE();
        
        // 配置GPIO为模拟输入
        // PA0: ADC1_IN0
        GPIO_InitStruct.Pin = GPIO_PIN_0;
        GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
        GPIO_InitStruct.Pull = GPIO_NOPULL;
        HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    }
}
```

**代码说明**：
- 配置12位分辨率，单次转换模式
- 采样时间84个时钟周期，平衡速度和精度
- GPIO配置为模拟输入模式


#### 单次转换

```c
// 读取ADC值
uint16_t ADC_ReadValue(void) {
    uint16_t adcValue = 0;
    
    // 启动转换
    HAL_ADC_Start(&hadc1);
    
    // 等待转换完成
    if (HAL_ADC_PollForConversion(&hadc1, 100) == HAL_OK) {
        adcValue = HAL_ADC_GetValue(&hadc1);
    }
    
    // 停止ADC
    HAL_ADC_Stop(&hadc1);
    
    return adcValue;
}

// 转换为电压值
float ADC_ToVoltage(uint16_t adcValue) {
    const float VREF = 3.3f;  // 参考电压
    const uint16_t ADC_MAX = 4095;  // 12位ADC最大值
    
    return (float)adcValue * VREF / ADC_MAX;
}

// 读取电压
float ADC_ReadVoltage(void) {
    uint16_t adcValue = ADC_ReadValue();
    return ADC_ToVoltage(adcValue);
}
```

**代码说明**：
- 启动转换并等待完成
- 将ADC值转换为实际电压值
- 注意参考电压的准确性

#### 连续转换模式

```c
// 配置连续转换
void ADC_ConfigContinuous(void) {
    hadc1.Init.ContinuousConvMode = ENABLE;  // 启用连续转换
    HAL_ADC_Init(&hadc1);
}

// 启动连续转换
void ADC_StartContinuous(void) {
    HAL_ADC_Start(&hadc1);
}

// 读取最新值（非阻塞）
uint16_t ADC_GetLatestValue(void) {
    return HAL_ADC_GetValue(&hadc1);
}

// 停止连续转换
void ADC_StopContinuous(void) {
    HAL_ADC_Stop(&hadc1);
}
```

#### 中断方式

```c
// 启动中断转换
void ADC_StartIT(void) {
    HAL_ADC_Start_IT(&hadc1);
}

// 转换完成回调
volatile uint16_t latestAdcValue = 0;
volatile uint8_t adcConvComplete = 0;

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc) {
    if (hadc->Instance == ADC1) {
        latestAdcValue = HAL_ADC_GetValue(hadc);
        adcConvComplete = 1;
    }
}

// 配置ADC中断
void HAL_ADC_MspInit_IT(ADC_HandleTypeDef* hadc) {
    if(hadc->Instance == ADC1) {
        HAL_NVIC_SetPriority(ADC_IRQn, 5, 0);
        HAL_NVIC_EnableIRQ(ADC_IRQn);
    }
}

// ADC中断处理函数
void ADC_IRQHandler(void) {
    HAL_ADC_IRQHandler(&hadc1);
}
```

**代码说明**：
- 中断方式适用于需要及时响应的场景
- 在回调函数中读取ADC值
- 避免在回调中执行耗时操作

#### DMA方式

```c
// DMA句柄
DMA_HandleTypeDef hdma_adc1;

// 配置DMA
void HAL_ADC_MspInit_DMA(ADC_HandleTypeDef* hadc) {
    if(hadc->Instance == ADC1) {
        // 使能DMA时钟
        __HAL_RCC_DMA2_CLK_ENABLE();
        
        // 配置DMA
        hdma_adc1.Instance = DMA2_Stream0;
        hdma_adc1.Init.Channel = DMA_CHANNEL_0;
        hdma_adc1.Init.Direction = DMA_PERIPH_TO_MEMORY;
        hdma_adc1.Init.PeriphInc = DMA_PINC_DISABLE;
        hdma_adc1.Init.MemInc = DMA_MINC_ENABLE;
        hdma_adc1.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
        hdma_adc1.Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;
        hdma_adc1.Init.Mode = DMA_CIRCULAR;  // 循环模式
        hdma_adc1.Init.Priority = DMA_PRIORITY_HIGH;
        HAL_DMA_Init(&hdma_adc1);
        
        __HAL_LINKDMA(hadc, DMA_Handle, hdma_adc1);
        
        // 配置DMA中断
        HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 5, 0);
        HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn);
    }
}

// ADC缓冲区
#define ADC_BUFFER_SIZE 100
uint16_t adcBuffer[ADC_BUFFER_SIZE];

// 启动DMA转换
void ADC_StartDMA(void) {
    HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adcBuffer, ADC_BUFFER_SIZE);
}

// DMA传输完成回调
void HAL_ADC_ConvHalfCpltCallback(ADC_HandleTypeDef* hadc) {
    // 前半部分缓冲区已满，可以处理数据
    // 处理 adcBuffer[0] 到 adcBuffer[ADC_BUFFER_SIZE/2-1]
}

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc) {
    // 后半部分缓冲区已满，可以处理数据
    // 处理 adcBuffer[ADC_BUFFER_SIZE/2] 到 adcBuffer[ADC_BUFFER_SIZE-1]
}

// DMA中断处理函数
void DMA2_Stream0_IRQHandler(void) {
    HAL_DMA_IRQHandler(&hdma_adc1);
}
```

**代码说明**：
- DMA循环模式适用于连续采样
- 使用双缓冲机制，一半处理数据时另一半继续采集
- CPU占用率低，适合高速采样


### 多通道ADC

```c
// 配置多通道扫描
void ADC_ConfigMultiChannel(void) {
    ADC_ChannelConfTypeDef sConfig = {0};
    
    hadc1.Init.ScanConvMode = ENABLE;  // 启用扫描模式
    hadc1.Init.NbrOfConversion = 3;    // 3个通道
    HAL_ADC_Init(&hadc1);
    
    // 配置通道1 (PA0)
    sConfig.Channel = ADC_CHANNEL_0;
    sConfig.Rank = 1;
    sConfig.SamplingTime = ADC_SAMPLETIME_84CYCLES;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
    
    // 配置通道2 (PA1)
    sConfig.Channel = ADC_CHANNEL_1;
    sConfig.Rank = 2;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
    
    // 配置通道3 (PA4)
    sConfig.Channel = ADC_CHANNEL_4;
    sConfig.Rank = 3;
    HAL_ADC_ConfigChannel(&hadc1, &sConfig);
}

// 多通道DMA采集
#define NUM_CHANNELS 3
uint16_t adcMultiBuffer[NUM_CHANNELS];

void ADC_StartMultiChannelDMA(void) {
    HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adcMultiBuffer, NUM_CHANNELS);
}

// 读取特定通道的值
uint16_t ADC_GetChannelValue(uint8_t channel) {
    if (channel < NUM_CHANNELS) {
        return adcMultiBuffer[channel];
    }
    return 0;
}
```

**代码说明**：
- 扫描模式按顺序转换多个通道
- DMA自动将结果存储到缓冲区
- 适用于需要同时监测多个信号的场景

### 实际应用：温度传感器

```c
// NTC热敏电阻温度测量
// 使用Steinhart-Hart方程

#define R_SERIES    10000.0f  // 串联电阻 (Ω)
#define R_NTC_25C   10000.0f  // 25°C时NTC电阻 (Ω)
#define B_VALUE     3950.0f   // B值
#define T_NOMINAL   298.15f   // 25°C (K)

float NTC_CalculateTemperature(uint16_t adcValue) {
    // 计算NTC电阻值
    float voltage = ADC_ToVoltage(adcValue);
    float r_ntc = R_SERIES * voltage / (3.3f - voltage);
    
    // Steinhart-Hart简化方程
    float steinhart;
    steinhart = r_ntc / R_NTC_25C;              // (R/Ro)
    steinhart = logf(steinhart);                 // ln(R/Ro)
    steinhart /= B_VALUE;                        // 1/B * ln(R/Ro)
    steinhart += 1.0f / T_NOMINAL;               // + (1/To)
    steinhart = 1.0f / steinhart;                // 反转
    steinhart -= 273.15f;                        // 转换为摄氏度
    
    return steinhart;
}

// 温度采集任务
void TemperatureSensorTask(void *pvParameters) {
    float temperature;
    uint16_t adcValue;
    
    while(1) {
        // 读取ADC值
        adcValue = ADC_ReadValue();
        
        // 计算温度
        temperature = NTC_CalculateTemperature(adcValue);
        
        // 记录或显示温度
        UART_Printf("Temperature: %.2f °C\r\n", temperature);
        
        // 延时
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}
```

**代码说明**：
- 使用分压电路和NTC热敏电阻测量温度
- Steinhart-Hart方程提供高精度温度计算
- 适用于医疗器械中的体温监测

### DAC配置和使用

#### DAC基础配置

```c
// DAC句柄
DAC_HandleTypeDef hdac;

// DAC初始化
void DAC_Init(void) {
    DAC_ChannelConfTypeDef sConfig = {0};
    
    // 配置DAC
    hdac.Instance = DAC;
    
    if (HAL_DAC_Init(&hdac) != HAL_OK) {
        Error_Handler();
    }
    
    // 配置DAC通道1
    sConfig.DAC_Trigger = DAC_TRIGGER_NONE;              // 软件触发
    sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;  // 使能输出缓冲
    
    if (HAL_DAC_ConfigChannel(&hdac, &sConfig, DAC_CHANNEL_1) != HAL_OK) {
        Error_Handler();
    }
}

// GPIO配置
void HAL_DAC_MspInit(DAC_HandleTypeDef* hdac) {
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    if(hdac->Instance == DAC) {
        // 使能时钟
        __HAL_RCC_DAC_CLK_ENABLE();
        __HAL_RCC_GPIOA_CLK_ENABLE();
        
        // 配置GPIO为模拟输出
        // PA4: DAC_OUT1
        GPIO_InitStruct.Pin = GPIO_PIN_4;
        GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
        GPIO_InitStruct.Pull = GPIO_NOPULL;
        HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
    }
}
```

#### DAC输出

```c
// 设置DAC输出值 (12位)
void DAC_SetValue(uint16_t value) {
    HAL_DAC_SetValue(&hdac, DAC_CHANNEL_1, DAC_ALIGN_12B_R, value);
}

// 设置DAC输出电压
void DAC_SetVoltage(float voltage) {
    const float VREF = 3.3f;
    const uint16_t DAC_MAX = 4095;  // 12位DAC
    
    // 限制电压范围
    if (voltage < 0.0f) voltage = 0.0f;
    if (voltage > VREF) voltage = VREF;
    
    // 计算DAC值
    uint16_t dacValue = (uint16_t)(voltage * DAC_MAX / VREF);
    
    DAC_SetValue(dacValue);
}

// 启动DAC
void DAC_Start(void) {
    HAL_DAC_Start(&hdac, DAC_CHANNEL_1);
}

// 停止DAC
void DAC_Stop(void) {
    HAL_DAC_Stop(&hdac, DAC_CHANNEL_1);
}
```

**代码说明**：
- DAC输出范围0-VREF（通常3.3V）
- 12位分辨率，步进约0.806mV
- 输出缓冲器提供驱动能力

#### 波形生成

```c
// 生成正弦波
#define SINE_SAMPLES 100
uint16_t sineWave[SINE_SAMPLES];

void DAC_GenerateSineWave(void) {
    const float PI = 3.14159265f;
    const uint16_t DAC_OFFSET = 2048;  // 中心值
    const uint16_t DAC_AMPLITUDE = 2000;  // 幅度
    
    for (int i = 0; i < SINE_SAMPLES; i++) {
        float angle = 2.0f * PI * i / SINE_SAMPLES;
        float value = sinf(angle);
        sineWave[i] = DAC_OFFSET + (uint16_t)(value * DAC_AMPLITUDE);
    }
}

// 使用定时器和DMA输出波形
TIM_HandleTypeDef htim6;
DMA_HandleTypeDef hdma_dac1;

void DAC_ConfigWaveformOutput(void) {
    // 配置定时器触发
    DAC_ChannelConfTypeDef sConfig = {0};
    sConfig.DAC_Trigger = DAC_TRIGGER_T6_TRGO;  // 定时器6触发
    sConfig.DAC_OutputBuffer = DAC_OUTPUTBUFFER_ENABLE;
    HAL_DAC_ConfigChannel(&hdac, &sConfig, DAC_CHANNEL_1);
    
    // 配置定时器6
    htim6.Instance = TIM6;
    htim6.Init.Prescaler = 0;
    htim6.Init.Period = 999;  // 更新频率 = 84MHz / (0+1) / (999+1) = 84kHz
    HAL_TIM_Base_Init(&htim6);
    
    // 生成正弦波数据
    DAC_GenerateSineWave();
    
    // 启动DAC DMA
    HAL_DAC_Start_DMA(&hdac, DAC_CHANNEL_1, (uint32_t*)sineWave, 
                      SINE_SAMPLES, DAC_ALIGN_12B_R);
    
    // 启动定时器
    HAL_TIM_Base_Start(&htim6);
}
```

**代码说明**：
- 使用定时器触发DAC更新
- DMA自动从缓冲区读取数据输出
- 可生成任意波形（正弦波、三角波、方波等）


### 信号调理

#### 滤波

```c
// 简单移动平均滤波
#define FILTER_SIZE 10
uint16_t filterBuffer[FILTER_SIZE];
uint8_t filterIndex = 0;

uint16_t ADC_MovingAverage(uint16_t newValue) {
    uint32_t sum = 0;
    
    // 更新缓冲区
    filterBuffer[filterIndex] = newValue;
    filterIndex = (filterIndex + 1) % FILTER_SIZE;
    
    // 计算平均值
    for (int i = 0; i < FILTER_SIZE; i++) {
        sum += filterBuffer[i];
    }
    
    return (uint16_t)(sum / FILTER_SIZE);
}

// 指数移动平均滤波 (EMA)
float ADC_ExponentialMovingAverage(float newValue, float prevEMA, float alpha) {
    // alpha: 平滑系数 (0-1)，越小越平滑
    return alpha * newValue + (1.0f - alpha) * prevEMA;
}

// 中值滤波（去除脉冲干扰）
uint16_t ADC_MedianFilter(uint16_t *samples, uint8_t size) {
    uint16_t temp[size];
    memcpy(temp, samples, size * sizeof(uint16_t));
    
    // 冒泡排序
    for (int i = 0; i < size - 1; i++) {
        for (int j = 0; j < size - i - 1; j++) {
            if (temp[j] > temp[j + 1]) {
                uint16_t swap = temp[j];
                temp[j] = temp[j + 1];
                temp[j + 1] = swap;
            }
        }
    }
    
    // 返回中值
    return temp[size / 2];
}
```

**代码说明**：
- 移动平均滤波：简单有效，适用于平稳信号
- 指数移动平均：响应速度和平滑度可调
- 中值滤波：有效去除脉冲干扰

#### 校准

```c
// ADC校准数据
typedef struct {
    float offset;  // 偏移
    float gain;    // 增益
} ADC_Calibration_t;

ADC_Calibration_t adcCal = {0.0f, 1.0f};

// 两点校准
void ADC_TwoPointCalibration(float knownValue1, uint16_t adcValue1,
                              float knownValue2, uint16_t adcValue2) {
    // 计算增益和偏移
    adcCal.gain = (knownValue2 - knownValue1) / (adcValue2 - adcValue1);
    adcCal.offset = knownValue1 - adcCal.gain * adcValue1;
}

// 应用校准
float ADC_ApplyCalibration(uint16_t adcValue) {
    return adcCal.gain * adcValue + adcCal.offset;
}

// 示例：温度传感器校准
void TemperatureSensor_Calibrate(void) {
    uint16_t adc0C, adc100C;
    
    // 在0°C环境中测量
    UART_SendString("请将传感器置于0°C环境，按任意键继续...\r\n");
    // 等待用户输入
    adc0C = ADC_ReadValue();
    
    // 在100°C环境中测量
    UART_SendString("请将传感器置于100°C环境，按任意键继续...\r\n");
    // 等待用户输入
    adc100C = ADC_ReadValue();
    
    // 执行两点校准
    ADC_TwoPointCalibration(0.0f, adc0C, 100.0f, adc100C);
    
    UART_Printf("校准完成: Gain=%.4f, Offset=%.4f\r\n", 
                adcCal.gain, adcCal.offset);
}
```

**代码说明**：
- 两点校准可以补偿偏移和增益误差
- 校准数据应保存到非易失性存储器
- 定期校准确保长期精度

### 最佳实践

!!! tip "ADC/DAC使用最佳实践"
    - **选择合适的分辨率**：根据精度要求选择，不是越高越好
    - **配置适当的采样时间**：平衡速度和精度，信号源阻抗高时需要更长采样时间
    - **使用参考电压**：外部精密参考电压提供更高精度
    - **信号调理**：使用运放、滤波器等调理信号到ADC输入范围
    - **抗混叠滤波**：采样前使用低通滤波器防止混叠
    - **校准**：定期校准补偿温度漂移和器件差异
    - **过采样**：通过过采样和平均提高有效分辨率
    - **隔离**：医疗器械中使用隔离ADC保护患者安全

### 常见陷阱

!!! warning "注意事项"
    - **输入超范围**：输入电压超过VREF会损坏ADC
    - **采样时间不足**：导致采样不准确，特别是高阻抗信号源
    - **参考电压不稳定**：参考电压波动直接影响ADC精度
    - **忽略输入阻抗**：ADC输入阻抗有限，需要考虑信号源阻抗
    - **混叠**：采样率不足导致高频信号混叠到低频
    - **噪声**：PCB布局不当、电源噪声影响ADC精度
    - **温度漂移**：未考虑温度对ADC精度的影响
    - **DAC负载**：DAC输出能力有限，重负载需要缓冲器

## 实践练习

1. **基础采集**：使用ADC读取电位器电压值
2. **温度测量**：实现NTC热敏电阻温度测量系统
3. **信号滤波**：比较不同滤波算法的效果
4. **波形生成**：使用DAC生成正弦波、三角波
5. **校准系统**：实现完整的ADC校准和验证流程

## 自测问题

??? question "什么是ADC的分辨率？如何选择合适的分辨率？"
    分辨率决定ADC能够区分的最小电压变化。
    
    ??? success "答案"
        **分辨率定义**：
        - N位ADC可以表示2^N个不同的数字值
        - LSB = VREF / 2^N
        
        **常见分辨率**：
        - 8位：256级，LSB = 3.3V/256 ≈ 12.9mV
        - 10位：1024级，LSB ≈ 3.2mV
        - 12位：4096级，LSB ≈ 0.8mV
        - 16位：65536级，LSB ≈ 50μV
        
        **选择原则**：
        1. **精度需求**：测量精度应小于LSB
        2. **信号范围**：信号变化范围应覆盖多个LSB
        3. **噪声水平**：噪声应小于LSB，否则高分辨率无意义
        4. **速度要求**：高分辨率通常意味着较慢的转换速度
        5. **成本考虑**：高分辨率ADC成本更高
        
        **医疗器械建议**：
        - 体温测量：12-16位
        - ECG信号：16-24位
        - 血压测量：12-16位

??? question "什么是奈奎斯特采样定理？为什么重要？"
    奈奎斯特定理是数字信号处理的基础。
    
    ??? success "答案"
        **奈奎斯特定理**：
        采样频率必须至少是信号最高频率的2倍，才能完整重建原始信号。
        
        ```
        fs ≥ 2 × fmax
        ```
        
        **实际应用**：
        - 信号最高频率100Hz → 最小采样率200Hz
        - 实际建议：采样率 = (2.5-5) × fmax
        - 留有余量应对滤波器非理想特性
        
        **违反定理的后果**：
        - **混叠（Aliasing）**：高频信号被错误地表示为低频
        - 无法从采样数据恢复原始信号
        - 导致测量错误
        
        **防止混叠**：
        1. 提高采样率
        2. 使用抗混叠滤波器（低通滤波器）
        3. 限制信号带宽
        
        **医疗器械示例**：
        - ECG信号：0.05-150Hz → 采样率≥500Hz（实际常用1kHz）
        - 血氧信号：DC-5Hz → 采样率≥25Hz（实际常用100Hz）

??? question "如何提高ADC的测量精度？"
    提高ADC精度需要从多个方面入手。
    
    ??? success "答案"
        **硬件方面**：
        
        1. **使用精密参考电压**：
           - 外部精密参考（如REF3030）
           - 温度系数<10ppm/°C
        
        2. **信号调理**：
           - 运放缓冲高阻抗信号
           - 滤波器去除噪声
           - 放大小信号到ADC输入范围
        
        3. **PCB设计**：
           - 模拟地和数字地分离
           - 短而宽的模拟信号走线
           - 远离数字信号和开关电源
        
        4. **电源滤波**：
           - 使用LDO为ADC供电
           - 添加去耦电容
        
        **软件方面**：
        
        1. **过采样和平均**：
           - 采集多个样本求平均
           - 可提高有效分辨率
        
        2. **校准**：
           - 两点校准补偿偏移和增益误差
           - 定期校准补偿温度漂移
        
        3. **滤波**：
           - 移动平均滤波
           - 中值滤波去除脉冲干扰
        
        4. **适当的采样时间**：
           - 根据信号源阻抗配置
           - 确保充分充电
        
        **验证方法**：
        - 使用精密电压源测试
        - 计算实际精度和线性度
        - 长期稳定性测试

??? question "DAC输出缓冲器的作用是什么？"
    DAC输出缓冲器影响输出特性。
    
    ??? success "答案"
        **输出缓冲器的作用**：
        
        1. **提供驱动能力**：
           - 无缓冲：输出阻抗高（~15kΩ），驱动能力弱
           - 有缓冲：输出阻抗低（~1Ω），可驱动较大负载
        
        2. **隔离负载**：
           - 防止负载变化影响DAC内部
           - 提高输出稳定性
        
        3. **改善线性度**：
           - 减少负载对输出的影响
           - 提高精度
        
        **权衡**：
        - 缓冲器增加功耗
        - 可能引入偏移误差
        - 限制输出范围（通常0.2V-VREF-0.2V）
        
        **选择建议**：
        - 轻负载（>10kΩ）：可不使用缓冲器
        - 重负载（<10kΩ）：必须使用缓冲器
        - 需要精确输出范围：考虑外部运放
        
        **医疗器械应用**：
        - 控制信号输出：通常使用缓冲器
        - 驱动执行器：可能需要外部功率放大器

??? question "在医疗器械中使用ADC需要注意什么？"
    医疗器械对信号采集有严格要求。
    
    ??? success "答案"
        **医疗器械ADC使用要点**：
        
        1. **患者安全**：
           - 使用隔离ADC（如AMC1200）
           - 符合IEC 60601-1电气安全要求
           - 漏电流<10μA
        
        2. **精度和可靠性**：
           - 选择医疗级ADC
           - 定期校准和验证
           - 记录所有测量数据
        
        3. **EMC抗干扰**：
           - 符合IEC 60601-1-2 EMC要求
           - 使用屏蔽和滤波
           - 抗电刀干扰（对于手术设备）
        
        4. **信号质量**：
           - 抗混叠滤波器
           - 适当的采样率
           - 低噪声设计
        
        5. **数据完整性**：
           - CRC校验
           - 数据范围检查
           - 异常值检测
        
        6. **可追溯性**：
           - 记录校准数据
           - 保存原始采样数据
           - 符合FDA 21 CFR Part 11（如适用）
        
        7. **测试验证**：
           - 使用医疗级测试设备
           - 进行临床验证
           - 长期稳定性测试

## 相关资源

- [信号处理](../signal-processing/index.md)
- [GPIO操作](gpio.md)
- [中断处理](../rtos/interrupt-handling.md)

## 参考文献

1. STM32F4xx Reference Manual - STMicroelectronics
2. IEC 60601-1:2005+AMD1:2012 - Medical electrical equipment
3. "The Art of Electronics" - Paul Horowitz & Winfield Hill
4. "Understanding Delta-Sigma Data Converters" - Texas Instruments
5. "Medical Device Design: Innovation from Concept to Market" - Peter J. Ogrodnik
