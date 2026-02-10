---
title: 显示接口
description: 医疗设备中LCD、OLED、TFT显示接口的原理和驱动实现
difficulty: 中级
estimated_time: 2-3小时
tags:
  - 显示接口
  - LCD
  - OLED
  - TFT
  - 硬件接口
related_modules:
  - zh/technical-knowledge/hardware-interfaces/spi
  - zh/technical-knowledge/hardware-interfaces/i2c
  - zh/regulatory-standards/iec-62366/index
last_updated: '2026-02-10'
version: '1.0'
language: zh-CN
---



# 显示接口

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

显示接口是医疗设备人机交互的核心组件，用于显示患者数据、波形、报警信息和操作界面。医疗设备常用的显示技术包括LCD、OLED和TFT，每种技术都有其特定的应用场景。

### 医疗设备显示要求

- **高可读性**: 在各种光照条件下清晰可读
- **快速响应**: 实时显示生理参数和波形
- **低功耗**: 便携设备需要长时间续航
- **高可靠性**: 符合医疗设备可靠性标准
- **易用性**: 符合IEC 62366可用性工程要求

### 显示技术对比

| 技术 | 分辨率 | 功耗 | 对比度 | 视角 | 应用场景 |
|------|--------|------|--------|------|----------|
| 字符LCD | 低 | 极低 | 低 | 窄 | 简单参数显示 |
| 单色图形LCD | 中 | 低 | 中 | 中 | 波形显示 |
| 彩色TFT | 高 | 高 | 高 | 宽 | 复杂GUI |
| OLED | 高 | 中 | 极高 | 宽 | 高端设备 |

## 字符LCD（1602/2004）

### 硬件连接

```c
// 1602 LCD引脚定义
#define LCD_RS_PIN      GPIO_PIN_0
#define LCD_RW_PIN      GPIO_PIN_1
#define LCD_EN_PIN      GPIO_PIN_2
#define LCD_D4_PIN      GPIO_PIN_4
#define LCD_D5_PIN      GPIO_PIN_5
#define LCD_D6_PIN      GPIO_PIN_6
#define LCD_D7_PIN      GPIO_PIN_7
#define LCD_GPIO_PORT   GPIOA

// LCD命令
#define LCD_CMD_CLEAR           0x01
#define LCD_CMD_HOME            0x02
#define LCD_CMD_ENTRY_MODE      0x06
#define LCD_CMD_DISPLAY_ON      0x0C
#define LCD_CMD_DISPLAY_OFF     0x08
#define LCD_CMD_CURSOR_ON       0x0E
#define LCD_CMD_FUNCTION_SET    0x28  // 4位模式，2行，5x8字体
#define LCD_CMD_SET_DDRAM       0x80
```

### 驱动实现

```c
// LCD初始化
void lcd1602_init(void) {
    // 等待LCD上电稳定
    HAL_Delay(50);
    
    // 初始化为4位模式
    lcd_write_nibble(0x03);
    HAL_Delay(5);
    lcd_write_nibble(0x03);
    HAL_Delay(1);
    lcd_write_nibble(0x03);
    HAL_Delay(1);
    lcd_write_nibble(0x02);
    
    // 功能设置
    lcd_send_command(LCD_CMD_FUNCTION_SET);
    lcd_send_command(LCD_CMD_DISPLAY_ON);
    lcd_send_command(LCD_CMD_CLEAR);
    lcd_send_command(LCD_CMD_ENTRY_MODE);
    
    HAL_Delay(2);
}

// 发送命令
void lcd_send_command(uint8_t cmd) {
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_RS_PIN, GPIO_PIN_RESET);  // RS=0
    lcd_write_byte(cmd);
}

// 发送数据
void lcd_send_data(uint8_t data) {
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_RS_PIN, GPIO_PIN_SET);  // RS=1
    lcd_write_byte(data);
}

// 写入字节（4位模式）
void lcd_write_byte(uint8_t byte) {
    lcd_write_nibble(byte >> 4);    // 高4位
    lcd_write_nibble(byte & 0x0F);  // 低4位
}

// 写入半字节
void lcd_write_nibble(uint8_t nibble) {
    // 设置数据线
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_D4_PIN, (nibble & 0x01) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_D5_PIN, (nibble & 0x02) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_D6_PIN, (nibble & 0x04) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_D7_PIN, (nibble & 0x08) ? GPIO_PIN_SET : GPIO_PIN_RESET);
    
    // 使能脉冲
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_EN_PIN, GPIO_PIN_SET);
    HAL_Delay(1);
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_EN_PIN, GPIO_PIN_RESET);
    HAL_Delay(1);
}

// 设置光标位置
void lcd_set_cursor(uint8_t row, uint8_t col) {
    uint8_t address = (row == 0) ? 0x00 : 0x40;
    address += col;
    lcd_send_command(LCD_CMD_SET_DDRAM | address);
}

// 显示字符串
void lcd_print(const char *str) {
    while (*str) {
        lcd_send_data(*str++);
    }
}

// 清屏
void lcd_clear(void) {
    lcd_send_command(LCD_CMD_CLEAR);
    HAL_Delay(2);
}
```

### 医疗应用示例

```c
// 显示患者生理参数
void display_vital_signs(patient_data_t *data) {
    char buffer[17];
    
    // 第一行：SpO2和心率
    lcd_set_cursor(0, 0);
    snprintf(buffer, sizeof(buffer), "SpO2:%3d%% HR:%3d", 
             data->spo2, data->heart_rate);
    lcd_print(buffer);
    
    // 第二行：体温和血压
    lcd_set_cursor(1, 0);
    snprintf(buffer, sizeof(buffer), "T:%.1fC BP:%3d/%2d",
             data->temperature, data->bp_sys, data->bp_dia);
    lcd_print(buffer);
}
```

## 单色图形LCD（12864）

### ST7920控制器

```c
// ST7920命令
#define LCD12864_CMD_CLEAR          0x01
#define LCD12864_CMD_HOME           0x02
#define LCD12864_CMD_ENTRY_MODE     0x06
#define LCD12864_CMD_DISPLAY_ON     0x0C
#define LCD12864_CMD_FUNCTION_SET   0x30  // 8位基本指令
#define LCD12864_CMD_EXTENDED       0x34  // 扩展指令集
#define LCD12864_CMD_GRAPHIC_ON     0x36  // 图形显示开

// 初始化12864 LCD
void lcd12864_init(void) {
    HAL_Delay(50);
    
    // 基本指令集
    lcd12864_send_command(LCD12864_CMD_FUNCTION_SET);
    lcd12864_send_command(LCD12864_CMD_DISPLAY_ON);
    lcd12864_send_command(LCD12864_CMD_CLEAR);
    
    // 切换到扩展指令集
    lcd12864_send_command(LCD12864_CMD_EXTENDED);
    lcd12864_send_command(LCD12864_CMD_GRAPHIC_ON);
}

// 设置图形坐标
void lcd12864_set_graphic_pos(uint8_t x, uint8_t y) {
    lcd12864_send_command(0x80 | y);        // 垂直地址
    lcd12864_send_command(0x80 | (x >> 4)); // 水平地址
}

// 画点
void lcd12864_draw_pixel(uint8_t x, uint8_t y, uint8_t color) {
    uint8_t page = y / 8;
    uint8_t bit = y % 8;
    
    // 读取当前字节
    lcd12864_set_graphic_pos(x, page);
    uint8_t data = lcd12864_read_data();
    
    // 修改像素
    if (color) {
        data |= (1 << bit);
    } else {
        data &= ~(1 << bit);
    }
    
    // 写回
    lcd12864_set_graphic_pos(x, page);
    lcd12864_send_data(data);
}

// 画线（Bresenham算法）
void lcd12864_draw_line(int x0, int y0, int x1, int y1) {
    int dx = abs(x1 - x0);
    int dy = abs(y1 - y0);
    int sx = (x0 < x1) ? 1 : -1;
    int sy = (y0 < y1) ? 1 : -1;
    int err = dx - dy;
    
    while (1) {
        lcd12864_draw_pixel(x0, y0, 1);
        
        if (x0 == x1 && y0 == y1) break;
        
        int e2 = 2 * err;
        if (e2 > -dy) {
            err -= dy;
            x0 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y0 += sy;
        }
    }
}

// 显示ECG波形
void display_ecg_waveform(int16_t *samples, uint16_t count) {
    const uint8_t baseline = 32;  // 基线位置
    const uint8_t scale = 10;     // 缩放因子
    
    lcd12864_clear();
    
    for (uint16_t i = 0; i < count - 1; i++) {
        int y0 = baseline - (samples[i] / scale);
        int y1 = baseline - (samples[i + 1] / scale);
        
        // 限制范围
        y0 = (y0 < 0) ? 0 : (y0 > 63) ? 63 : y0;
        y1 = (y1 < 0) ? 0 : (y1 > 63) ? 63 : y1;
        
        lcd12864_draw_line(i, y0, i + 1, y1);
    }
}
```

## OLED显示（SSD1306）

### I2C接口

```c
#include "i2c.h"

#define SSD1306_I2C_ADDR    0x78  // I2C地址（7位地址 << 1）
#define SSD1306_WIDTH       128
#define SSD1306_HEIGHT      64

// SSD1306命令
#define SSD1306_CMD_DISPLAY_OFF         0xAE
#define SSD1306_CMD_DISPLAY_ON          0xAF
#define SSD1306_CMD_SET_CONTRAST        0x81
#define SSD1306_CMD_NORMAL_DISPLAY      0xA6
#define SSD1306_CMD_INVERSE_DISPLAY     0xA7
#define SSD1306_CMD_SET_MULTIPLEX       0xA8
#define SSD1306_CMD_SET_DISPLAY_OFFSET  0xD3
#define SSD1306_CMD_SET_START_LINE      0x40
#define SSD1306_CMD_CHARGE_PUMP         0x8D
#define SSD1306_CMD_MEMORY_MODE         0x20
#define SSD1306_CMD_SEG_REMAP           0xA1
#define SSD1306_CMD_COM_SCAN_DEC        0xC8

// 显示缓冲区
uint8_t ssd1306_buffer[SSD1306_WIDTH * SSD1306_HEIGHT / 8];

// 发送命令
void ssd1306_send_command(uint8_t cmd) {
    uint8_t data[2] = {0x00, cmd};  // 0x00 = 命令模式
    HAL_I2C_Master_Transmit(&hi2c1, SSD1306_I2C_ADDR, data, 2, HAL_MAX_DELAY);
}

// 发送数据
void ssd1306_send_data(uint8_t *data, uint16_t len) {
    uint8_t buffer[len + 1];
    buffer[0] = 0x40;  // 0x40 = 数据模式
    memcpy(&buffer[1], data, len);
    HAL_I2C_Master_Transmit(&hi2c1, SSD1306_I2C_ADDR, buffer, len + 1, HAL_MAX_DELAY);
}

// 初始化OLED
void ssd1306_init(void) {
    HAL_Delay(100);
    
    ssd1306_send_command(SSD1306_CMD_DISPLAY_OFF);
    ssd1306_send_command(SSD1306_CMD_SET_MULTIPLEX);
    ssd1306_send_command(0x3F);  // 64行
    ssd1306_send_command(SSD1306_CMD_SET_DISPLAY_OFFSET);
    ssd1306_send_command(0x00);
    ssd1306_send_command(SSD1306_CMD_SET_START_LINE | 0x00);
    ssd1306_send_command(SSD1306_CMD_CHARGE_PUMP);
    ssd1306_send_command(0x14);  // 使能电荷泵
    ssd1306_send_command(SSD1306_CMD_MEMORY_MODE);
    ssd1306_send_command(0x00);  // 水平寻址模式
    ssd1306_send_command(SSD1306_CMD_SEG_REMAP);
    ssd1306_send_command(SSD1306_CMD_COM_SCAN_DEC);
    ssd1306_send_command(SSD1306_CMD_SET_CONTRAST);
    ssd1306_send_command(0xFF);  // 最大对比度
    ssd1306_send_command(SSD1306_CMD_NORMAL_DISPLAY);
    ssd1306_send_command(SSD1306_CMD_DISPLAY_ON);
    
    ssd1306_clear();
    ssd1306_update();
}

// 清空缓冲区
void ssd1306_clear(void) {
    memset(ssd1306_buffer, 0, sizeof(ssd1306_buffer));
}

// 更新显示
void ssd1306_update(void) {
    // 设置列地址范围
    ssd1306_send_command(0x21);  // 列地址
    ssd1306_send_command(0);     // 起始列
    ssd1306_send_command(127);   // 结束列
    
    // 设置页地址范围
    ssd1306_send_command(0x22);  // 页地址
    ssd1306_send_command(0);     // 起始页
    ssd1306_send_command(7);     // 结束页
    
    // 发送缓冲区数据
    ssd1306_send_data(ssd1306_buffer, sizeof(ssd1306_buffer));
}

// 画点
void ssd1306_draw_pixel(uint8_t x, uint8_t y, uint8_t color) {
    if (x >= SSD1306_WIDTH || y >= SSD1306_HEIGHT) {
        return;
    }
    
    if (color) {
        ssd1306_buffer[x + (y / 8) * SSD1306_WIDTH] |= (1 << (y % 8));
    } else {
        ssd1306_buffer[x + (y / 8) * SSD1306_WIDTH] &= ~(1 << (y % 8));
    }
}

// 显示字符（8x16字体）
void ssd1306_draw_char(uint8_t x, uint8_t y, char ch, const uint8_t *font) {
    uint16_t offset = (ch - ' ') * 16;  // 每个字符16字节
    
    for (uint8_t i = 0; i < 8; i++) {
        for (uint8_t j = 0; j < 16; j++) {
            if (font[offset + j] & (1 << i)) {
                ssd1306_draw_pixel(x + i, y + j, 1);
            }
        }
    }
}

// 显示字符串
void ssd1306_print(uint8_t x, uint8_t y, const char *str, const uint8_t *font) {
    while (*str) {
        ssd1306_draw_char(x, y, *str, font);
        x += 8;
        str++;
    }
}
```

### 医疗应用示例

```c
// 显示SpO2和心率
void oled_display_vital_signs(uint8_t spo2, uint8_t hr) {
    char buffer[32];
    
    ssd1306_clear();
    
    // 显示SpO2
    ssd1306_print(0, 0, "SpO2:", font_8x16);
    snprintf(buffer, sizeof(buffer), "%d%%", spo2);
    ssd1306_print(48, 0, buffer, font_16x32);
    
    // 显示心率
    ssd1306_print(0, 32, "HR:", font_8x16);
    snprintf(buffer, sizeof(buffer), "%d", hr);
    ssd1306_print(48, 32, buffer, font_16x32);
    
    ssd1306_update();
}

// 显示脉搏波形
void oled_display_pleth_waveform(uint8_t *samples, uint16_t count) {
    const uint8_t baseline = 48;
    const uint8_t scale = 4;
    
    // 清除波形区域
    for (uint8_t x = 0; x < 128; x++) {
        for (uint8_t y = 40; y < 64; y++) {
            ssd1306_draw_pixel(x, y, 0);
        }
    }
    
    // 绘制波形
    for (uint16_t i = 0; i < count && i < 128; i++) {
        uint8_t y = baseline - (samples[i] / scale);
        y = (y < 40) ? 40 : (y > 63) ? 63 : y;
        ssd1306_draw_pixel(i, y, 1);
    }
    
    ssd1306_update();
}
```

## TFT彩色显示（ILI9341）

### SPI接口

```c
#include "spi.h"

#define ILI9341_WIDTH   240
#define ILI9341_HEIGHT  320

// ILI9341命令
#define ILI9341_CMD_SWRESET     0x01
#define ILI9341_CMD_SLPOUT      0x11
#define ILI9341_CMD_DISPON      0x29
#define ILI9341_CMD_CASET       0x2A
#define ILI9341_CMD_PASET       0x2B
#define ILI9341_CMD_RAMWR       0x2C
#define ILI9341_CMD_MADCTL      0x36
#define ILI9341_CMD_PIXFMT      0x3A

// 引脚定义
#define LCD_CS_PIN      GPIO_PIN_0
#define LCD_DC_PIN      GPIO_PIN_1
#define LCD_RST_PIN     GPIO_PIN_2
#define LCD_GPIO_PORT   GPIOA

// 颜色定义（RGB565）
#define COLOR_BLACK     0x0000
#define COLOR_WHITE     0xFFFF
#define COLOR_RED       0xF800
#define COLOR_GREEN     0x07E0
#define COLOR_BLUE      0x001F
#define COLOR_YELLOW    0xFFE0
#define COLOR_CYAN      0x07FF
#define COLOR_MAGENTA   0xF81F

// 发送命令
void ili9341_send_command(uint8_t cmd) {
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_DC_PIN, GPIO_PIN_RESET);  // DC=0
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_CS_PIN, GPIO_PIN_RESET);  // CS=0
    HAL_SPI_Transmit(&hspi1, &cmd, 1, HAL_MAX_DELAY);
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_CS_PIN, GPIO_PIN_SET);    // CS=1
}

// 发送数据
void ili9341_send_data(uint8_t data) {
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_DC_PIN, GPIO_PIN_SET);    // DC=1
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_CS_PIN, GPIO_PIN_RESET);  // CS=0
    HAL_SPI_Transmit(&hspi1, &data, 1, HAL_MAX_DELAY);
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_CS_PIN, GPIO_PIN_SET);    // CS=1
}

// 初始化ILI9341
void ili9341_init(void) {
    // 硬件复位
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_RST_PIN, GPIO_PIN_RESET);
    HAL_Delay(10);
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_RST_PIN, GPIO_PIN_SET);
    HAL_Delay(120);
    
    // 软件复位
    ili9341_send_command(ILI9341_CMD_SWRESET);
    HAL_Delay(150);
    
    // 退出睡眠模式
    ili9341_send_command(ILI9341_CMD_SLPOUT);
    HAL_Delay(500);
    
    // 像素格式：16位/像素
    ili9341_send_command(ILI9341_CMD_PIXFMT);
    ili9341_send_data(0x55);
    
    // 显示方向
    ili9341_send_command(ILI9341_CMD_MADCTL);
    ili9341_send_data(0x48);  // MX, BGR
    
    // 打开显示
    ili9341_send_command(ILI9341_CMD_DISPON);
    HAL_Delay(100);
}

// 设置窗口
void ili9341_set_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1) {
    // 列地址
    ili9341_send_command(ILI9341_CMD_CASET);
    ili9341_send_data(x0 >> 8);
    ili9341_send_data(x0 & 0xFF);
    ili9341_send_data(x1 >> 8);
    ili9341_send_data(x1 & 0xFF);
    
    // 行地址
    ili9341_send_command(ILI9341_CMD_PASET);
    ili9341_send_data(y0 >> 8);
    ili9341_send_data(y0 & 0xFF);
    ili9341_send_data(y1 >> 8);
    ili9341_send_data(y1 & 0xFF);
    
    // 写RAM
    ili9341_send_command(ILI9341_CMD_RAMWR);
}

// 画点
void ili9341_draw_pixel(uint16_t x, uint16_t y, uint16_t color) {
    ili9341_set_window(x, y, x, y);
    ili9341_send_data(color >> 8);
    ili9341_send_data(color & 0xFF);
}

// 填充矩形
void ili9341_fill_rect(uint16_t x, uint16_t y, uint16_t w, uint16_t h, uint16_t color) {
    ili9341_set_window(x, y, x + w - 1, y + h - 1);
    
    uint32_t pixel_count = w * h;
    uint8_t color_high = color >> 8;
    uint8_t color_low = color & 0xFF;
    
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_DC_PIN, GPIO_PIN_SET);
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
    
    for (uint32_t i = 0; i < pixel_count; i++) {
        HAL_SPI_Transmit(&hspi1, &color_high, 1, HAL_MAX_DELAY);
        HAL_SPI_Transmit(&hspi1, &color_low, 1, HAL_MAX_DELAY);
    }
    
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_CS_PIN, GPIO_PIN_SET);
}

// 清屏
void ili9341_clear(uint16_t color) {
    ili9341_fill_rect(0, 0, ILI9341_WIDTH, ILI9341_HEIGHT, color);
}
```

### 医疗GUI实现

```c
// 监护仪界面布局
typedef struct {
    uint16_t x, y, width, height;
    uint16_t bg_color, fg_color;
    char     label[32];
    char     value[32];
    char     unit[16];
} parameter_widget_t;

// 参数显示控件
void draw_parameter_widget(parameter_widget_t *widget) {
    // 绘制背景
    ili9341_fill_rect(widget->x, widget->y, widget->width, widget->height, widget->bg_color);
    
    // 绘制标签
    ili9341_draw_string(widget->x + 5, widget->y + 5, widget->label,
                       font_16x24, widget->fg_color, widget->bg_color);
    
    // 绘制数值（大字体）
    ili9341_draw_string(widget->x + 10, widget->y + 35, widget->value,
                       font_32x48, widget->fg_color, widget->bg_color);
    
    // 绘制单位
    ili9341_draw_string(widget->x + widget->width - 40, widget->y + 50,
                       widget->unit, font_16x24, widget->fg_color, widget->bg_color);
}

// 监护仪主界面
void display_monitor_screen(patient_data_t *data) {
    // 清屏
    ili9341_clear(COLOR_BLACK);
    
    // SpO2控件
    parameter_widget_t spo2_widget = {
        .x = 10, .y = 10, .width = 110, .height = 80,
        .bg_color = COLOR_BLUE, .fg_color = COLOR_WHITE,
        .label = "SpO2", .unit = "%"
    };
    snprintf(spo2_widget.value, sizeof(spo2_widget.value), "%d", data->spo2);
    draw_parameter_widget(&spo2_widget);
    
    // 心率控件
    parameter_widget_t hr_widget = {
        .x = 130, .y = 10, .width = 110, .height = 80,
        .bg_color = COLOR_GREEN, .fg_color = COLOR_WHITE,
        .label = "HR", .unit = "bpm"
    };
    snprintf(hr_widget.value, sizeof(hr_widget.value), "%d", data->heart_rate);
    draw_parameter_widget(&hr_widget);
    
    // 体温控件
    parameter_widget_t temp_widget = {
        .x = 10, .y = 100, .width = 110, .height = 80,
        .bg_color = COLOR_YELLOW, .fg_color = COLOR_BLACK,
        .label = "TEMP", .unit = "°C"
    };
    snprintf(temp_widget.value, sizeof(temp_widget.value), "%.1f", data->temperature);
    draw_parameter_widget(&temp_widget);
    
    // 血压控件
    parameter_widget_t bp_widget = {
        .x = 130, .y = 100, .width = 110, .height = 80,
        .bg_color = COLOR_RED, .fg_color = COLOR_WHITE,
        .label = "BP", .unit = "mmHg"
    };
    snprintf(bp_widget.value, sizeof(bp_widget.value), "%d/%d",
             data->bp_sys, data->bp_dia);
    draw_parameter_widget(&bp_widget);
    
    // 波形区域
    draw_waveform_area(10, 190, 230, 120, data);
}

// 绘制波形
void draw_waveform_area(uint16_t x, uint16_t y, uint16_t w, uint16_t h,
                       patient_data_t *data) {
    // 绘制背景
    ili9341_fill_rect(x, y, w, h, COLOR_BLACK);
    
    // 绘制网格
    for (uint16_t i = 0; i < w; i += 20) {
        ili9341_draw_vline(x + i, y, h, COLOR_GREEN);
    }
    for (uint16_t i = 0; i < h; i += 20) {
        ili9341_draw_hline(x, y + i, w, COLOR_GREEN);
    }
    
    // 绘制ECG波形
    uint16_t baseline = y + h / 2;
    for (uint16_t i = 0; i < data->ecg_sample_count - 1 && i < w; i++) {
        int16_t y0 = baseline - (data->ecg_samples[i] / 10);
        int16_t y1 = baseline - (data->ecg_samples[i + 1] / 10);
        
        // 限制范围
        y0 = (y0 < y) ? y : (y0 > y + h) ? y + h : y0;
        y1 = (y1 < y) ? y : (y1 > y + h) ? y + h : y1;
        
        ili9341_draw_line(x + i, y0, x + i + 1, y1, COLOR_YELLOW);
    }
}

// 报警界面
void display_alarm_screen(alarm_t *alarm) {
    // 红色背景闪烁
    static bool flash_state = false;
    uint16_t bg_color = flash_state ? COLOR_RED : COLOR_BLACK;
    flash_state = !flash_state;
    
    ili9341_clear(bg_color);
    
    // 显示报警图标
    draw_alarm_icon(60, 50, 120, 120, COLOR_WHITE);
    
    // 显示报警信息
    ili9341_draw_string_centered(160, "ALARM!", font_32x48,
                                 COLOR_WHITE, bg_color);
    ili9341_draw_string_centered(220, alarm->message, font_16x24,
                                 COLOR_WHITE, bg_color);
}
```

## 触摸屏支持

### 电阻触摸屏（XPT2046）

```c
// XPT2046命令
#define XPT2046_CMD_X   0xD0
#define XPT2046_CMD_Y   0x90

// 读取触摸坐标
bool xpt2046_read_touch(uint16_t *x, uint16_t *y) {
    uint8_t tx_data[3], rx_data[3];
    
    // 读取X坐标
    tx_data[0] = XPT2046_CMD_X;
    HAL_SPI_TransmitReceive(&hspi2, tx_data, rx_data, 3, HAL_MAX_DELAY);
    uint16_t raw_x = ((rx_data[1] << 8) | rx_data[2]) >> 3;
    
    // 读取Y坐标
    tx_data[0] = XPT2046_CMD_Y;
    HAL_SPI_TransmitReceive(&hspi2, tx_data, rx_data, 3, HAL_MAX_DELAY);
    uint16_t raw_y = ((rx_data[1] << 8) | rx_data[2]) >> 3;
    
    // 校准转换
    *x = (raw_x - TOUCH_CAL_X_MIN) * ILI9341_WIDTH / (TOUCH_CAL_X_MAX - TOUCH_CAL_X_MIN);
    *y = (raw_y - TOUCH_CAL_Y_MIN) * ILI9341_HEIGHT / (TOUCH_CAL_Y_MAX - TOUCH_CAL_Y_MIN);
    
    // 检查是否有效
    return (raw_x > 100 && raw_y > 100);
}

// 按钮控件
typedef struct {
    uint16_t x, y, width, height;
    char     label[32];
    uint16_t color;
    void     (*callback)(void);
} button_t;

// 绘制按钮
void draw_button(button_t *btn) {
    // 绘制按钮背景
    ili9341_fill_rect(btn->x, btn->y, btn->width, btn->height, btn->color);
    
    // 绘制边框
    ili9341_draw_rect(btn->x, btn->y, btn->width, btn->height, COLOR_WHITE);
    
    // 绘制文字（居中）
    uint16_t text_x = btn->x + (btn->width - strlen(btn->label) * 16) / 2;
    uint16_t text_y = btn->y + (btn->height - 24) / 2;
    ili9341_draw_string(text_x, text_y, btn->label, font_16x24,
                       COLOR_WHITE, btn->color);
}

// 检查按钮点击
bool check_button_press(button_t *btn, uint16_t touch_x, uint16_t touch_y) {
    if (touch_x >= btn->x && touch_x <= btn->x + btn->width &&
        touch_y >= btn->y && touch_y <= btn->y + btn->height) {
        // 按钮被点击
        if (btn->callback != NULL) {
            btn->callback();
        }
        return true;
    }
    return false;
}

// 医疗设备按钮示例
void button_start_measurement(void) {
    start_measurement();
    log_info("Measurement started");
}

void button_stop_measurement(void) {
    stop_measurement();
    log_info("Measurement stopped");
}

void button_export_data(void) {
    export_patient_data();
    log_info("Data exported");
}

// 创建按钮界面
button_t buttons[] = {
    {10, 250, 70, 50, "START", COLOR_GREEN, button_start_measurement},
    {90, 250, 70, 50, "STOP", COLOR_RED, button_stop_measurement},
    {170, 250, 70, 50, "EXPORT", COLOR_BLUE, button_export_data}
};

// 触摸处理任务
void touch_task(void) {
    uint16_t touch_x, touch_y;
    static bool last_touch_state = false;
    
    bool touch_detected = xpt2046_read_touch(&touch_x, &touch_y);
    
    if (touch_detected && !last_touch_state) {
        // 新的触摸事件
        for (int i = 0; i < sizeof(buttons) / sizeof(button_t); i++) {
            if (check_button_press(&buttons[i], touch_x, touch_y)) {
                break;
            }
        }
    }
    
    last_touch_state = touch_detected;
}
```

## GUI框架集成

### LVGL（Light and Versatile Graphics Library）

```c
#include "lvgl.h"

// 显示缓冲区
static lv_disp_draw_buf_t draw_buf;
static lv_color_t buf1[ILI9341_WIDTH * 10];
static lv_color_t buf2[ILI9341_WIDTH * 10];

// 显示驱动回调
void lvgl_flush_cb(lv_disp_drv_t *disp_drv, const lv_area_t *area, lv_color_t *color_p) {
    uint16_t width = area->x2 - area->x1 + 1;
    uint16_t height = area->y2 - area->y1 + 1;
    
    ili9341_set_window(area->x1, area->y1, area->x2, area->y2);
    
    // 发送像素数据
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_DC_PIN, GPIO_PIN_SET);
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
    HAL_SPI_Transmit_DMA(&hspi1, (uint8_t*)color_p, width * height * 2);
    
    // 在DMA完成回调中调用 lv_disp_flush_ready(disp_drv);
}

// 触摸驱动回调
void lvgl_read_cb(lv_indev_drv_t *indev_drv, lv_indev_data_t *data) {
    uint16_t x, y;
    
    if (xpt2046_read_touch(&x, &y)) {
        data->state = LV_INDEV_STATE_PRESSED;
        data->point.x = x;
        data->point.y = y;
    } else {
        data->state = LV_INDEV_STATE_RELEASED;
    }
}

// LVGL初始化
void lvgl_init(void) {
    lv_init();
    
    // 初始化显示缓冲区
    lv_disp_draw_buf_init(&draw_buf, buf1, buf2, ILI9341_WIDTH * 10);
    
    // 注册显示驱动
    static lv_disp_drv_t disp_drv;
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res = ILI9341_WIDTH;
    disp_drv.ver_res = ILI9341_HEIGHT;
    disp_drv.flush_cb = lvgl_flush_cb;
    disp_drv.draw_buf = &draw_buf;
    lv_disp_drv_register(&disp_drv);
    
    // 注册触摸驱动
    static lv_indev_drv_t indev_drv;
    lv_indev_drv_init(&indev_drv);
    indev_drv.type = LV_INDEV_TYPE_POINTER;
    indev_drv.read_cb = lvgl_read_cb;
    lv_indev_drv_register(&indev_drv);
}

// 创建监护仪界面
void create_monitor_ui(void) {
    // 创建主屏幕
    lv_obj_t *scr = lv_scr_act();
    lv_obj_set_style_bg_color(scr, lv_color_black(), 0);
    
    // SpO2标签
    lv_obj_t *spo2_label = lv_label_create(scr);
    lv_label_set_text(spo2_label, "SpO2");
    lv_obj_align(spo2_label, LV_ALIGN_TOP_LEFT, 10, 10);
    
    // SpO2数值
    lv_obj_t *spo2_value = lv_label_create(scr);
    lv_obj_set_style_text_font(spo2_value, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(spo2_value, lv_color_make(0, 150, 255), 0);
    lv_label_set_text(spo2_value, "98");
    lv_obj_align(spo2_value, LV_ALIGN_TOP_LEFT, 10, 40);
    
    // 心率标签
    lv_obj_t *hr_label = lv_label_create(scr);
    lv_label_set_text(hr_label, "HR");
    lv_obj_align(hr_label, LV_ALIGN_TOP_RIGHT, -10, 10);
    
    // 心率数值
    lv_obj_t *hr_value = lv_label_create(scr);
    lv_obj_set_style_text_font(hr_value, &lv_font_montserrat_48, 0);
    lv_obj_set_style_text_color(hr_value, lv_color_make(0, 255, 0), 0);
    lv_label_set_text(hr_value, "72");
    lv_obj_align(hr_value, LV_ALIGN_TOP_RIGHT, -10, 40);
    
    // 波形图表
    lv_obj_t *chart = lv_chart_create(scr);
    lv_obj_set_size(chart, 220, 100);
    lv_obj_align(chart, LV_ALIGN_BOTTOM_MID, 0, -60);
    lv_chart_set_type(chart, LV_CHART_TYPE_LINE);
    lv_chart_set_range(chart, LV_CHART_AXIS_PRIMARY_Y, 0, 100);
    
    // 添加数据系列
    lv_chart_series_t *ser = lv_chart_add_series(chart,
                                                  lv_color_make(255, 255, 0),
                                                  LV_CHART_AXIS_PRIMARY_Y);
    
    // 按钮
    lv_obj_t *btn_start = lv_btn_create(scr);
    lv_obj_set_size(btn_start, 70, 40);
    lv_obj_align(btn_start, LV_ALIGN_BOTTOM_LEFT, 10, -10);
    lv_obj_t *btn_label = lv_label_create(btn_start);
    lv_label_set_text(btn_label, "START");
    lv_obj_center(btn_label);
}

// LVGL任务（在RTOS任务中调用）
void lvgl_task(void) {
    while (1) {
        lv_timer_handler();
        vTaskDelay(pdMS_TO_TICKS(5));
    }
}
```

## 性能优化

### DMA传输

```c
// 使用DMA加速SPI传输
void ili9341_fill_rect_dma(uint16_t x, uint16_t y, uint16_t w, uint16_t h,
                           uint16_t color) {
    ili9341_set_window(x, y, x + w - 1, y + h - 1);
    
    // 准备颜色缓冲区
    static uint16_t color_buffer[ILI9341_WIDTH];
    for (uint16_t i = 0; i < w; i++) {
        color_buffer[i] = color;
    }
    
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_DC_PIN, GPIO_PIN_SET);
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
    
    // 使用DMA传输每一行
    for (uint16_t row = 0; row < h; row++) {
        HAL_SPI_Transmit_DMA(&hspi1, (uint8_t*)color_buffer, w * 2);
        // 等待DMA完成
        while (HAL_SPI_GetState(&hspi1) != HAL_SPI_STATE_READY);
    }
    
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_CS_PIN, GPIO_PIN_SET);
}
```

### 双缓冲

```c
// 双缓冲区
uint16_t frame_buffer[2][ILI9341_WIDTH * ILI9341_HEIGHT];
uint8_t current_buffer = 0;

// 切换缓冲区
void swap_buffers(void) {
    // 将当前缓冲区内容传输到显示器
    ili9341_set_window(0, 0, ILI9341_WIDTH - 1, ILI9341_HEIGHT - 1);
    
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_DC_PIN, GPIO_PIN_SET);
    HAL_GPIO_WritePin(LCD_GPIO_PORT, LCD_CS_PIN, GPIO_PIN_RESET);
    HAL_SPI_Transmit_DMA(&hspi1,
                        (uint8_t*)frame_buffer[current_buffer],
                        ILI9341_WIDTH * ILI9341_HEIGHT * 2);
    
    // 切换到另一个缓冲区
    current_buffer = 1 - current_buffer;
}
```

## 最佳实践

### 1. 符合IEC 62366可用性要求

- 清晰的信息层次结构
- 适当的字体大小和对比度
- 明确的报警指示
- 易于操作的触摸目标（最小44x44像素）
- 一致的颜色编码

### 2. 低功耗设计

```c
// 自动背光调节
void adjust_backlight(uint8_t ambient_light) {
    uint8_t brightness;
    
    if (ambient_light < 20) {
        brightness = 50;  // 暗环境
    } else if (ambient_light < 100) {
        brightness = 75;  // 正常环境
    } else {
        brightness = 100; // 明亮环境
    }
    
    set_backlight_pwm(brightness);
}

// 屏幕超时
void screen_timeout_check(void) {
    static uint32_t last_touch_time = 0;
    
    if (HAL_GetTick() - last_touch_time > 60000) {
        // 60秒无操作，降低亮度
        set_backlight_pwm(20);
    }
}
```

### 3. 错误处理

```c
// 显示初始化失败处理
bool display_init_with_retry(void) {
    for (uint8_t retry = 0; retry < 3; retry++) {
        if (ili9341_init() == HAL_OK) {
            return true;
        }
        HAL_Delay(100);
    }
    
    log_error("Display initialization failed");
    return false;
}
```

## 总结

显示接口是医疗设备用户体验的关键。选择合适的显示技术，实现清晰、响应快速的界面，并符合医疗设备可用性标准，可以提高设备的安全性和易用性。

## 相关资源


- [IEC 62366可用性工程](../../regulatory-standards/iec-62366/index.md)- [SPI总线通信](spi.md)
- [I2C总线通信](i2c.md)
