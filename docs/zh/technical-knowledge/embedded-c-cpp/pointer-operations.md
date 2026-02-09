---
title: 指针操作
description: 嵌入式C/C++中的指针技术，包括指针算术、函数指针和指针安全
difficulty: 中级
estimated_time: 2小时
tags:
- C语言
- 指针
- 嵌入式编程
related_modules:
- zh/technical-knowledge/embedded-c-cpp/memory-management
- zh/technical-knowledge/embedded-c-cpp/bit-manipulation
last_updated: '2026-02-07'
version: '1.0'
language: zh-CN
---

# 指针操作

## 学习目标

完成本模块后，你将能够：
- 理解指针的本质和内存地址的关系
- 掌握指针算术运算和数组访问
- 使用函数指针实现回调和状态机
- 理解指针的常见陷阱和安全使用方法
- 应用医疗器械软件中的指针安全实践

## 前置知识

- C语言基础
- 内存管理基础
- 数据类型和变量

## 内容

### 指针基础

指针是存储内存地址的变量。在嵌入式系统中，指针用于：
- 访问硬件寄存器
- 高效传递大数据结构
- 实现动态数据结构
- 回调函数和中断处理

**基本语法**：

```c
#include <stdint.h>

void pointer_basics(void) {
    uint32_t value = 0x12345678;
    uint32_t* ptr;  // 声明指针
    
    ptr = &value;   // 获取value的地址
    
    // 解引用指针
    uint32_t read_value = *ptr;  // read_value = 0x12345678
    
    // 通过指针修改值
    *ptr = 0xABCDEF00;  // value现在是0xABCDEF00
}
```

**指针大小**：
- 在32位系统中，指针通常是4字节
- 在64位系统中，指针通常是8字节
- 在嵌入式系统中，取决于架构（如ARM Cortex-M是32位）

### 指针算术

指针可以进行算术运算，但运算单位是指向类型的大小。

```c
void pointer_arithmetic(void) {
    uint32_t array[5] = {10, 20, 30, 40, 50};
    uint32_t* ptr = array;  // 指向第一个元素
    
    // 指针递增
    ptr++;  // 现在指向array[1]，地址增加4字节（sizeof(uint32_t)）
    
    // 指针加法
    ptr = array + 2;  // 指向array[2]
    
    // 指针减法
    ptr = ptr - 1;  // 指向array[1]
    
    // 两个指针相减得到元素个数
    uint32_t* end = &array[4];
    ptrdiff_t count = end - array;  // count = 4
}
```

**数组和指针的关系**：

```c
void array_pointer_relationship(void) {
    uint8_t data[10];
    
    // 以下表达式等价
    data[3] = 0xFF;
    *(data + 3) = 0xFF;
    *(3 + data) = 0xFF;
    3[data] = 0xFF;  // 合法但不推荐
}
```

### 指针类型和类型转换

**void指针**：通用指针类型，可以指向任何类型。

```c
void void_pointer_example(void) {
    uint32_t value = 100;
    void* generic_ptr = &value;
    
    // 使用前必须转换为具体类型
    uint32_t* typed_ptr = (uint32_t*)generic_ptr;
    uint32_t result = *typed_ptr;
}
```

**指针类型转换**：

```c
#include <stdint.h>

void pointer_casting(void) {
    uint32_t data = 0x12345678;
    uint32_t* ptr32 = &data;
    
    // 转换为字节指针
    uint8_t* ptr8 = (uint8_t*)ptr32;
    
    // 在小端系统中：
    // ptr8[0] = 0x78
    // ptr8[1] = 0x56
    // ptr8[2] = 0x34
    // ptr8[3] = 0x12
}
```

!!! warning "对齐要求"
    某些架构要求特定类型的数据必须对齐到特定边界。不对齐的访问可能导致：
    - 性能下降
    - 硬件异常
    - 数据损坏

### 硬件寄存器访问

在嵌入式系统中，指针常用于访问硬件寄存器。

```c
#include <stdint.h>

// GPIO寄存器定义
#define GPIO_BASE_ADDR  0x40020000
#define GPIO_MODER      (*(volatile uint32_t*)(GPIO_BASE_ADDR + 0x00))
#define GPIO_ODR        (*(volatile uint32_t*)(GPIO_BASE_ADDR + 0x14))
#define GPIO_IDR        (*(volatile uint32_t*)(GPIO_BASE_ADDR + 0x10))

// 使用结构体映射寄存器
typedef struct {
    volatile uint32_t MODER;    // 模式寄存器
    volatile uint32_t OTYPER;   // 输出类型寄存器
    volatile uint32_t OSPEEDR;  // 输出速度寄存器
    volatile uint32_t PUPDR;    // 上拉/下拉寄存器
    volatile uint32_t IDR;      // 输入数据寄存器
    volatile uint32_t ODR;      // 输出数据寄存器
    volatile uint32_t BSRR;     // 位设置/复位寄存器
    volatile uint32_t LCKR;     // 配置锁定寄存器
} GPIO_TypeDef;

#define GPIOA ((GPIO_TypeDef*)0x40020000)

void gpio_operations(void) {
    // 设置PA5为输出模式
    GPIOA->MODER |= (1 << 10);
    
    // 设置PA5输出高电平
    GPIOA->ODR |= (1 << 5);
    
    // 读取PA3输入状态
    uint32_t input = (GPIOA->IDR >> 3) & 0x01;
}
```

**volatile关键字**：
- 告诉编译器该变量可能被外部因素改变
- 防止编译器优化掉对该变量的访问
- 硬件寄存器访问必须使用volatile

### 函数指针

函数指针用于实现回调、状态机和多态行为。

**基本用法**：

```c
#include <stdint.h>

// 函数指针类型定义
typedef void (*callback_t)(uint32_t);

// 回调函数示例
void on_data_received(uint32_t data) {
    // 处理接收到的数据
    process_data(data);
}

void on_error_occurred(uint32_t error_code) {
    // 处理错误
    log_error(error_code);
}

// 使用函数指针的模块
typedef struct {
    callback_t data_callback;
    callback_t error_callback;
} uart_config_t;

void uart_init(uart_config_t* config) {
    // 保存回调函数
    static uart_config_t uart_cfg;
    uart_cfg = *config;
}

void uart_interrupt_handler(void) {
    uint32_t status = read_uart_status();
    
    if (status & UART_DATA_READY) {
        uint32_t data = read_uart_data();
        if (uart_cfg.data_callback != NULL) {
            uart_cfg.data_callback(data);  // 调用回调
        }
    }
    
    if (status & UART_ERROR) {
        uint32_t error = read_uart_error();
        if (uart_cfg.error_callback != NULL) {
            uart_cfg.error_callback(error);
        }
    }
}

// 使用示例
void setup_uart(void) {
    uart_config_t config = {
        .data_callback = on_data_received,
        .error_callback = on_error_occurred
    };
    
    uart_init(&config);
}
```

**状态机实现**：

```c
typedef enum {
    STATE_IDLE,
    STATE_MEASURING,
    STATE_PROCESSING,
    STATE_COMPLETE,
    STATE_ERROR
} system_state_t;

// 状态处理函数类型
typedef system_state_t (*state_handler_t)(void);

// 各状态的处理函数
system_state_t handle_idle(void) {
    if (start_button_pressed()) {
        return STATE_MEASURING;
    }
    return STATE_IDLE;
}

system_state_t handle_measuring(void) {
    if (measurement_complete()) {
        return STATE_PROCESSING;
    }
    if (measurement_error()) {
        return STATE_ERROR;
    }
    return STATE_MEASURING;
}

system_state_t handle_processing(void) {
    process_measurement_data();
    return STATE_COMPLETE;
}

system_state_t handle_complete(void) {
    display_results();
    return STATE_IDLE;
}

system_state_t handle_error(void) {
    log_error_and_reset();
    return STATE_IDLE;
}

// 状态机表
state_handler_t state_table[] = {
    [STATE_IDLE] = handle_idle,
    [STATE_MEASURING] = handle_measuring,
    [STATE_PROCESSING] = handle_processing,
    [STATE_COMPLETE] = handle_complete,
    [STATE_ERROR] = handle_error
};

// 状态机执行
void run_state_machine(void) {
    static system_state_t current_state = STATE_IDLE;
    
    if (current_state < sizeof(state_table)/sizeof(state_table[0])) {
        if (state_table[current_state] != NULL) {
            current_state = state_table[current_state]();
        }
    }
}
```

### 指针安全和常见陷阱

#### 1. 空指针检查

```c
// 错误示例
void unsafe_function(uint8_t* data) {
    *data = 0xFF;  // 如果data是NULL，崩溃！
}

// 正确示例
void safe_function(uint8_t* data) {
    if (data == NULL) {
        return;  // 或记录错误
    }
    *data = 0xFF;
}
```

#### 2. 悬空指针

```c
// 错误示例
uint8_t* get_buffer(void) {
    uint8_t local_buffer[100];
    return local_buffer;  // 返回局部变量地址！
}

// 正确示例
uint8_t* get_buffer(void) {
    static uint8_t static_buffer[100];
    return static_buffer;  // 返回静态变量地址
}
```

#### 3. 指针越界

```c
// 错误示例
void unsafe_access(void) {
    uint8_t buffer[10];
    uint8_t* ptr = buffer;
    
    for (int i = 0; i <= 10; i++) {  // 越界！
        ptr[i] = 0;
    }
}

// 正确示例
void safe_access(void) {
    uint8_t buffer[10];
    uint8_t* ptr = buffer;
    
    for (int i = 0; i < 10; i++) {
        ptr[i] = 0;
    }
}
```

#### 4. 类型不匹配

```c
// 危险示例
void type_mismatch(void) {
    uint8_t data = 0xFF;
    uint32_t* ptr = (uint32_t*)&data;  // 类型不匹配
    *ptr = 0x12345678;  // 可能写入超出data的内存
}
```

### 医疗器械软件指针使用最佳实践

1. **始终检查空指针**
   ```c
   void safe_api(uint8_t* buffer, size_t size) {
       if (buffer == NULL || size == 0) {
           log_error("Invalid parameters");
           return;
       }
       // 处理buffer
   }
   ```

2. **使用const保护只读数据**
   ```c
   void process_data(const uint8_t* input, uint8_t* output, size_t size) {
       // input不能被修改
       for (size_t i = 0; i < size; i++) {
           output[i] = transform(input[i]);
       }
   }
   ```

3. **限制指针作用域**
   ```c
   void limited_scope_example(void) {
       uint8_t buffer[100];
       {
           uint8_t* ptr = buffer;
           // 使用ptr
       }
       // ptr在此处不可见
   }
   ```

4. **使用断言验证指针**
   ```c
   #include <assert.h>
   
   void assert_example(uint8_t* data) {
       assert(data != NULL);  // 开发时检查
       // 使用data
   }
   ```

5. **遵循MISRA C规则**
   - Rule 11.5: 不要从void*转换为其他指针类型
   - Rule 11.8: 不要移除const或volatile限定符
   - Rule 17.4: 数组索引应该是唯一的数组访问形式

### 实践示例：安全的缓冲区操作

```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    uint8_t* data;
    size_t size;
    size_t capacity;
} safe_buffer_t;

// 初始化缓冲区
bool safe_buffer_init(safe_buffer_t* buffer, uint8_t* storage, size_t capacity) {
    if (buffer == NULL || storage == NULL || capacity == 0) {
        return false;
    }
    
    buffer->data = storage;
    buffer->size = 0;
    buffer->capacity = capacity;
    return true;
}

// 安全写入
bool safe_buffer_write(safe_buffer_t* buffer, const uint8_t* data, size_t len) {
    if (buffer == NULL || data == NULL) {
        return false;
    }
    
    if (buffer->size + len > buffer->capacity) {
        return false;  // 空间不足
    }
    
    memcpy(buffer->data + buffer->size, data, len);
    buffer->size += len;
    return true;
}

// 安全读取
bool safe_buffer_read(safe_buffer_t* buffer, uint8_t* data, size_t len) {
    if (buffer == NULL || data == NULL) {
        return false;
    }
    
    if (len > buffer->size) {
        return false;  // 数据不足
    }
    
    memcpy(data, buffer->data, len);
    return true;
}
```

## 实践练习

1. 实现一个安全的字符串操作库，包含边界检查
2. 使用函数指针实现一个简单的命令解析器
3. 编写代码访问特定的硬件寄存器（如定时器或ADC）
4. 实现一个基于函数指针的事件系统

## 相关资源

### 相关知识模块

- [内存管理](memory-management.md) - 动态内存分配和内存池管理
- [位操作](bit-manipulation.md) - 位运算和寄存器操作技巧

### 深入学习

- [嵌入式C/C++概述](index.md) - 嵌入式C/C++编程基础
- [硬件接口](../hardware-interfaces/index.md) - 使用指针访问硬件寄存器

## 参考文献

1. MISRA C:2012 - Guidelines for the use of the C language in critical systems
2. IEC 62304:2006+AMD1:2015 - Medical device software
3. "Expert C Programming: Deep C Secrets" by Peter van der Linden
4. "C Traps and Pitfalls" by Andrew Koenig
5. ARM Cortex-M Programming Guide to Memory Barrier Instructions


## 自测问题

??? question "问题1：指针和地址的区别是什么？"
    **问题**：解释指针和地址的概念，以及它们之间的关系。
    
    ??? success "答案"
        **地址（Address）**：
        - 内存中的位置标识
        - 是一个数值
        - 例如：0x20000100
        
        **指针（Pointer）**：
        - 存储地址的变量
        - 有类型信息
        - 可以进行运算
        
        **关系**：
        ```c
        int value = 42;
        int* ptr = &value;  // ptr是指针，存储value的地址
        
        printf("value的地址: %p\n", (void*)&value);  // 地址
        printf("ptr的值: %p\n", (void*)ptr);         // 指针存储的地址
        printf("ptr指向的值: %d\n", *ptr);           // 解引用指针
        ```
        
        **关键区别**：
        1. 地址是数值，指针是变量
        2. 指针有类型，地址没有
        3. 指针可以运算，地址只是数值
        4. 指针占用内存，地址是内存位置
        
        **知识点回顾**：理解指针和地址的区别是掌握指针的基础。

??? question "问题2：指针运算的规则是什么？"
    **问题**：解释指针加减运算的规则，以及为什么指针运算与类型相关。
    
    ??? success "答案"
        **指针运算规则**：
        
        ```c
        int arr[5] = {10, 20, 30, 40, 50};
        int* ptr = arr;
        
        // 指针加法
        ptr + 1;  // 地址增加 sizeof(int) 字节（通常4字节）
        ptr + 2;  // 地址增加 2 * sizeof(int) 字节
        
        // 指针减法
        ptr - 1;  // 地址减少 sizeof(int) 字节
        
        // 指针相减（得到元素个数）
        int* end = &arr[4];
        ptrdiff_t diff = end - ptr;  // diff = 4（元素个数）
        ```
        
        **为什么与类型相关**：
        ```c
        char* char_ptr = (char*)0x1000;
        int* int_ptr = (int*)0x1000;
        
        char_ptr + 1;  // 0x1001（增加1字节）
        int_ptr + 1;   // 0x1004（增加4字节）
        ```
        
        **指针运算示例**：
        ```c
        // 数组遍历
        int arr[5] = {1, 2, 3, 4, 5};
        for (int* p = arr; p < arr + 5; p++) {
            printf("%d ", *p);
        }
        
        // 等价于
        for (int i = 0; i < 5; i++) {
            printf("%d ", arr[i]);
        }
        ```
        
        **注意事项**：
        - 只能对同一数组的指针进行相减
        - 指针加减整数，不能指针加指针
        - 指针比较只对同一数组有意义
        - 指针运算可能导致越界
        
        **知识点回顾**：指针运算是基于类型大小的，这使得数组访问更加自然。

??? question "问题3：什么是空指针、野指针和悬空指针？"
    **问题**：解释这三种危险指针的概念，以及如何避免它们。
    
    ??? success "答案"
        **1. 空指针（NULL Pointer）**：
        ```c
        int* ptr = NULL;  // 显式初始化为NULL
        
        // 使用前检查
        if (ptr != NULL) {
            *ptr = 10;
        }
        ```
        - 定义：指向地址0的指针
        - 用途：表示指针未指向有效对象
        - 安全：解引用会导致段错误（可检测）
        
        **2. 野指针（Wild Pointer）**：
        ```c
        int* ptr;  // 未初始化，包含随机值
        *ptr = 10; // 危险！可能写入任意内存
        
        // 正确做法
        int* ptr = NULL;  // 或指向有效对象
        ```
        - 定义：未初始化的指针
        - 危险：指向随机内存位置
        - 后果：不可预测的行为，难以调试
        
        **3. 悬空指针（Dangling Pointer）**：
        ```c
        int* ptr = (int*)malloc(sizeof(int));
        free(ptr);
        *ptr = 10;  // 危险！指向已释放的内存
        
        // 正确做法
        free(ptr);
        ptr = NULL;  // 释放后置NULL
        ```
        - 定义：指向已释放内存的指针
        - 危险：内存可能被重新分配
        - 后果：数据损坏、崩溃
        
        **预防措施**：
        ```c
        // 1. 始终初始化指针
        int* ptr = NULL;
        
        // 2. 释放后置NULL
        free(ptr);
        ptr = NULL;
        
        // 3. 使用前检查
        if (ptr != NULL) {
            *ptr = 10;
        }
        
        // 4. 避免返回局部变量地址
        int* dangerous_function(void) {
            int local = 10;
            return &local;  // 错误！返回悬空指针
        }
        ```
        
        **知识点回顾**：正确的指针管理是避免内存错误的关键。

??? question "问题4：如何使用指针访问硬件寄存器？"
    **问题**：在嵌入式系统中，如何使用指针安全地访问硬件寄存器？
    
    ??? success "答案"
        **硬件寄存器访问**：
        
        ```c
        #include <stdint.h>
        
        // 方法1：直接定义寄存器地址
        #define GPIO_BASE    0x40020000
        #define GPIO_MODER   (*(volatile uint32_t*)(GPIO_BASE + 0x00))
        #define GPIO_ODR     (*(volatile uint32_t*)(GPIO_BASE + 0x14))
        
        // 使用
        GPIO_MODER = 0x55555555;  // 配置模式
        GPIO_ODR = 0x0001;        // 设置输出
        
        // 方法2：使用结构体映射
        typedef struct {
            volatile uint32_t MODER;    // 偏移0x00
            volatile uint32_t OTYPER;   // 偏移0x04
            volatile uint32_t OSPEEDR;  // 偏移0x08
            volatile uint32_t PUPDR;    // 偏移0x0C
            volatile uint32_t IDR;      // 偏移0x10
            volatile uint32_t ODR;      // 偏移0x14
        } GPIO_TypeDef;
        
        #define GPIOA ((GPIO_TypeDef*)0x40020000)
        
        // 使用
        GPIOA->MODER = 0x55555555;
        GPIOA->ODR = 0x0001;
        
        // 方法3：使用指针变量
        volatile uint32_t* gpio_moder = (volatile uint32_t*)0x40020000;
        *gpio_moder = 0x55555555;
        ```
        
        **关键要点**：
        
        1. **使用volatile关键字**：
           ```c
           volatile uint32_t* reg = (volatile uint32_t*)0x40020000;
           // volatile告诉编译器不要优化对该地址的访问
           ```
        
        2. **正确的类型转换**：
           ```c
           // 错误
           uint32_t* reg = 0x40020000;  // 警告：整数到指针
           
           // 正确
           uint32_t* reg = (uint32_t*)0x40020000;
           ```
        
        3. **对齐要求**：
           ```c
           // 确保地址对齐
           volatile uint32_t* reg = (volatile uint32_t*)0x40020000;
           // 0x40020000是4字节对齐的
           ```
        
        4. **原子性考虑**：
           ```c
           // 读-修改-写可能不是原子的
           GPIO_ODR |= 0x0001;  // 可能被中断打断
           
           // 使用硬件原子操作
           GPIO_BSRR = 0x0001;  // 位设置寄存器（原子）
           ```
        
        **知识点回顾**：正确使用指针访问硬件寄存器是嵌入式编程的核心技能。

??? question "问题5：函数指针的应用场景"
    **问题**：解释函数指针的概念，并给出在嵌入式系统中的实际应用示例。
    
    ??? success "答案"
        **函数指针基础**：
        
        ```c
        // 函数声明
        int add(int a, int b) {
            return a + b;
        }
        
        // 函数指针声明
        int (*func_ptr)(int, int);
        
        // 赋值
        func_ptr = add;
        
        // 调用
        int result = func_ptr(3, 4);  // result = 7
        ```
        
        **应用1：回调函数**：
        ```c
        // 定时器回调
        typedef void (*timer_callback_t)(void);
        
        void timer_init(timer_callback_t callback) {
            // 保存回调函数指针
            timer_callback = callback;
        }
        
        void my_timer_handler(void) {
            // 定时器到期时的处理
        }
        
        // 使用
        timer_init(my_timer_handler);
        ```
        
        **应用2：状态机**：
        ```c
        typedef enum {
            STATE_IDLE,
            STATE_RUNNING,
            STATE_ERROR
        } state_t;
        
        typedef void (*state_handler_t)(void);
        
        void idle_handler(void) { /* 处理空闲状态 */ }
        void running_handler(void) { /* 处理运行状态 */ }
        void error_handler(void) { /* 处理错误状态 */ }
        
        state_handler_t state_table[] = {
            idle_handler,
            running_handler,
            error_handler
        };
        
        void state_machine_run(state_t current_state) {
            state_table[current_state]();
        }
        ```
        
        **应用3：中断向量表**：
        ```c
        typedef void (*isr_t)(void);
        
        // 中断服务程序
        void timer_isr(void) { /* 定时器中断 */ }
        void uart_isr(void) { /* UART中断 */ }
        
        // 中断向量表
        const isr_t vector_table[] __attribute__((section(".isr_vector"))) = {
            (isr_t)&_estack,      // 栈顶
            reset_handler,         // 复位
            nmi_handler,          // NMI
            hardfault_handler,    // 硬件错误
            // ...
            timer_isr,            // 定时器
            uart_isr,             // UART
        };
        ```
        
        **应用4：命令处理器**：
        ```c
        typedef void (*cmd_handler_t)(const char* args);
        
        typedef struct {
            const char* name;
            cmd_handler_t handler;
        } command_t;
        
        void cmd_help(const char* args) { /* 帮助命令 */ }
        void cmd_reset(const char* args) { /* 复位命令 */ }
        
        const command_t commands[] = {
            {"help", cmd_help},
            {"reset", cmd_reset},
            {NULL, NULL}
        };
        
        void process_command(const char* cmd, const char* args) {
            for (int i = 0; commands[i].name != NULL; i++) {
                if (strcmp(cmd, commands[i].name) == 0) {
                    commands[i].handler(args);
                    return;
                }
            }
        }
        ```
        
        **知识点回顾**：函数指针提供了代码的灵活性和可扩展性，是高级C编程的重要工具。
