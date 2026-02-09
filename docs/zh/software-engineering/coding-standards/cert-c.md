---
title: CERT C安全编码规范
description: CERT C安全编码规范详解，包括安全规则、漏洞防范和最佳实践
difficulty: 中级
estimated_time: 55分钟
tags:
- CERT C
- 安全编码
- 漏洞防范
- 编码规范
- 医疗器械软件
related_modules:
- zh/software-engineering/coding-standards
- zh/software-engineering/coding-standards/misra-c
- zh/software-engineering/coding-standards/code-review-checklist
last_updated: '2026-02-09'
version: '1.0'
language: zh
---

# CERT C安全编码规范

## 学习目标

完成本模块后，你将能够：
- 理解CERT C规范的目的和安全重点
- 掌握常见的C语言安全漏洞及防范方法
- 应用CERT C规则编写安全的医疗器械软件
- 识别和修复代码中的安全问题
- 结合MISRA C和CERT C提高代码质量

## 前置知识

- C语言编程基础
- 软件安全基础知识
- 常见漏洞类型（缓冲区溢出、整数溢出等）
- MISRA C编码规范（推荐）

## 内容

### CERT C概述

CERT C安全编码标准由卡内基梅隆大学软件工程研究所（SEI）开发，专注于C语言的安全编程实践。与MISRA C侧重可靠性不同，CERT C更关注安全性。

**CERT C的目标**：
1. **防止安全漏洞**：避免常见的安全缺陷
2. **提高安全意识**：教育开发人员安全编程
3. **可验证性**：提供可检查的安全规则
4. **实用性**：提供实际可行的解决方案

**CERT C与MISRA C的关系**：
- MISRA C：侧重可靠性和可维护性
- CERT C：侧重安全性和漏洞防范
- 两者互补，建议同时应用

### 规则分类

CERT C规则按主题分为以下类别：

1. **PRE** - 预处理器
2. **DCL** - 声明和初始化
3. **EXP** - 表达式
4. **INT** - 整数
5. **FLP** - 浮点数
6. **ARR** - 数组
7. **STR** - 字符串
8. **MEM** - 内存管理
9. **FIO** - 文件I/O
10. **ENV** - 环境
11. **SIG** - 信号
12. **ERR** - 错误处理
13. **API** - API设计
14. **CON** - 并发
15. **MSC** - 杂项

### 关键安全规则

#### INT30-C：确保无符号整数运算不会回绕

```c
// 违反规则：无符号整数溢出
void bad_example(void) {
    unsigned int ui1 = UINT_MAX;
    unsigned int ui2 = 1;
    unsigned int sum = ui1 + ui2;  // 回绕到0
}

// 符合规则：检查溢出
#include <limits.h>
bool safe_add(unsigned int a, unsigned int b, unsigned int* result) {
    if (a > UINT_MAX - b) {
        return false;  // 溢出
    }
    *result = a + b;
    return true;
}

void good_example(void) {
    unsigned int ui1 = UINT_MAX;
    unsigned int ui2 = 1;
    unsigned int sum;
    
    if (safe_add(ui1, ui2, &sum)) {
        // 使用sum
    } else {
        // 处理溢出
    }
}
```

#### INT32-C：确保有符号整数运算不会导致溢出

```c
// 违反规则：有符号整数溢出（未定义行为）
void bad_example(void) {
    int si1 = INT_MAX;
    int si2 = 1;
    int sum = si1 + si2;  // 未定义行为
}

// 符合规则：检查溢出
#include <limits.h>
bool safe_signed_add(int a, int b, int* result) {
    if (((b > 0) && (a > INT_MAX - b)) ||
        ((b < 0) && (a < INT_MIN - b))) {
        return false;  // 溢出
    }
    *result = a + b;
    return true;
}
```

#### ARR30-C：不要形成或使用越界指针或数组下标

```c
// 违反规则：数组越界
void bad_example(void) {
    int array[10];
    int* ptr = array + 11;  // 越界指针
    *ptr = 42;  // 未定义行为
}

// 符合规则：边界检查
void good_example(void) {
    int array[10];
    size_t index = 5;
    
    if (index < sizeof(array) / sizeof(array[0])) {
        array[index] = 42;  // 安全访问
    }
}
```

#### ARR38-C：保证库函数不会形成无效指针

```c
// 违反规则：传递无效指针给库函数
void bad_example(void) {
    char src[] = "Hello";
    char dest[3];  // 太小
    strcpy(dest, src);  // 缓冲区溢出
}

// 符合规则：使用安全函数
void good_example(void) {
    char src[] = "Hello";
    char dest[10];
    
    strncpy(dest, src, sizeof(dest) - 1);
    dest[sizeof(dest) - 1] = '\0';  // 确保null终止
}

// 更好的方案：使用安全函数（C11）
#ifdef __STDC_LIB_EXT1__
void better_example(void) {
    char src[] = "Hello";
    char dest[10];
    
    strcpy_s(dest, sizeof(dest), src);
}
#endif
```

#### STR31-C：保证存储字符串的空间足够大

```c
// 违反规则：缓冲区太小
void bad_example(void) {
    char buffer[5];
    sprintf(buffer, "Hello, World!");  // 缓冲区溢出
}

// 符合规则：使用安全函数
void good_example(void) {
    char buffer[20];
    snprintf(buffer, sizeof(buffer), "Hello, World!");
}
```

#### MEM30-C：不要访问已释放的内存

```c
// 违反规则：使用已释放的内存
void bad_example(void) {
    int* ptr = malloc(sizeof(int));
    *ptr = 42;
    free(ptr);
    *ptr = 100;  // 使用已释放的内存
}

// 符合规则：释放后置NULL
void good_example(void) {
    int* ptr = malloc(sizeof(int));
    if (ptr != NULL) {
        *ptr = 42;
        free(ptr);
        ptr = NULL;  // 防止悬空指针
    }
}
```

#### MEM34-C：只释放动态分配的内存

```c
// 违反规则：释放栈内存
void bad_example(void) {
    int stack_var = 42;
    int* ptr = &stack_var;
    free(ptr);  // 错误：释放栈内存
}

// 符合规则：只释放堆内存
void good_example(void) {
    int* ptr = malloc(sizeof(int));
    if (ptr != NULL) {
        *ptr = 42;
        free(ptr);  // 正确：释放堆内存
    }
}
```

#### FIO30-C：排除文件名中的用户输入

```c
// 违反规则：直接使用用户输入作为文件名
void bad_example(const char* user_input) {
    FILE* file = fopen(user_input, "r");  // 路径遍历漏洞
    // ...
}

// 符合规则：验证和清理文件名
#include <string.h>
#include <ctype.h>

bool is_safe_filename(const char* filename) {
    // 检查路径遍历字符
    if (strstr(filename, "..") != NULL) {
        return false;
    }
    if (strchr(filename, '/') != NULL || strchr(filename, '\\') != NULL) {
        return false;
    }
    
    // 只允许字母数字和特定字符
    for (const char* p = filename; *p != '\0'; p++) {
        if (!isalnum(*p) && *p != '_' && *p != '-' && *p != '.') {
            return false;
        }
    }
    
    return true;
}

void good_example(const char* user_input) {
    if (is_safe_filename(user_input)) {
        char safe_path[256];
        snprintf(safe_path, sizeof(safe_path), "/safe/directory/%s", user_input);
        FILE* file = fopen(safe_path, "r");
        // ...
    }
}
```

#### ERR33-C：检测并处理标准库错误

```c
// 违反规则：忽略错误返回值
void bad_example(void) {
    FILE* file = fopen("data.txt", "r");
    fread(buffer, 1, 100, file);  // 未检查fopen返回值
    fclose(file);
}

// 符合规则：检查所有错误
void good_example(void) {
    FILE* file = fopen("data.txt", "r");
    if (file == NULL) {
        // 处理文件打开错误
        perror("Failed to open file");
        return;
    }
    
    size_t bytes_read = fread(buffer, 1, 100, file);
    if (bytes_read < 100) {
        if (feof(file)) {
            // 到达文件末尾
        } else if (ferror(file)) {
            // 读取错误
            perror("Failed to read file");
        }
    }
    
    if (fclose(file) != 0) {
        perror("Failed to close file");
    }
}
```

### 安全编码模式

#### 1. 输入验证

```c
// 输入验证模板
typedef enum {
    VALIDATION_OK,
    VALIDATION_ERROR_NULL,
    VALIDATION_ERROR_RANGE,
    VALIDATION_ERROR_FORMAT
} ValidationResult_t;

ValidationResult_t validate_input(const char* input, size_t max_length) {
    // 空指针检查
    if (input == NULL) {
        return VALIDATION_ERROR_NULL;
    }
    
    // 长度检查
    size_t length = strnlen(input, max_length + 1);
    if (length > max_length) {
        return VALIDATION_ERROR_RANGE;
    }
    
    // 格式检查
    for (size_t i = 0; i < length; i++) {
        if (!isprint(input[i])) {
            return VALIDATION_ERROR_FORMAT;
        }
    }
    
    return VALIDATION_OK;
}
```

#### 2. 安全的字符串操作

```c
// 安全的字符串复制
int safe_string_copy(char* dest, size_t dest_size, const char* src) {
    if (dest == NULL || src == NULL || dest_size == 0) {
        return -1;
    }
    
    size_t src_len = strlen(src);
    if (src_len >= dest_size) {
        return -1;  // 目标缓冲区太小
    }
    
    memcpy(dest, src, src_len + 1);  // 包括null终止符
    return 0;
}

// 安全的字符串连接
int safe_string_concat(char* dest, size_t dest_size, const char* src) {
    if (dest == NULL || src == NULL || dest_size == 0) {
        return -1;
    }
    
    size_t dest_len = strnlen(dest, dest_size);
    size_t src_len = strlen(src);
    
    if (dest_len + src_len >= dest_size) {
        return -1;  // 缓冲区太小
    }
    
    memcpy(dest + dest_len, src, src_len + 1);
    return 0;
}
```

#### 3. 安全的整数运算

```c
// 安全的整数运算库
typedef struct {
    bool overflow;
    int result;
} SafeIntResult_t;

SafeIntResult_t safe_int_add(int a, int b) {
    SafeIntResult_t result = {false, 0};
    
    if (((b > 0) && (a > INT_MAX - b)) ||
        ((b < 0) && (a < INT_MIN - b))) {
        result.overflow = true;
    } else {
        result.result = a + b;
    }
    
    return result;
}

SafeIntResult_t safe_int_multiply(int a, int b) {
    SafeIntResult_t result = {false, 0};
    
    if (a > 0) {
        if (b > 0) {
            if (a > INT_MAX / b) {
                result.overflow = true;
            }
        } else {
            if (b < INT_MIN / a) {
                result.overflow = true;
            }
        }
    } else {
        if (b > 0) {
            if (a < INT_MIN / b) {
                result.overflow = true;
            }
        } else {
            if ((a != 0) && (b < INT_MAX / a)) {
                result.overflow = true;
            }
        }
    }
    
    if (!result.overflow) {
        result.result = a * b;
    }
    
    return result;
}
```

### 医疗器械软件中的应用

#### 安全威胁模型

医疗器械软件面临的安全威胁：

1. **数据完整性**：患者数据被篡改
2. **可用性**：设备被拒绝服务攻击
3. **机密性**：患者隐私泄露
4. **认证**：未授权访问设备功能

#### CERT C在IEC 62304中的应用

- **5.1.1 软件开发计划**：包含安全编码标准
- **5.5.3 软件单元验证**：包含安全代码审查
- **7.1 软件维护计划**：包含安全补丁流程
- **9 软件风险管理**：识别和缓解安全风险

#### 与IEC 81001-5-1的关系

IEC 81001-5-1（医疗器械网络安全）要求：
- 安全编码实践
- 漏洞管理
- 安全测试

CERT C帮助满足这些要求。

## 最佳实践

!!! tip "CERT C应用最佳实践"
    1. **结合MISRA C使用**：CERT C关注安全，MISRA C关注可靠性
    2. **优先处理高风险规则**：关注缓冲区溢出、整数溢出等
    3. **使用安全函数**：优先使用C11 Annex K安全函数
    4. **输入验证**：验证所有外部输入
    5. **错误处理**：检查所有函数返回值
    6. **代码审查**：定期进行安全代码审查
    7. **静态分析**：使用工具检测安全问题
    8. **安全培训**：培训团队安全编码实践

## 常见陷阱

!!! warning "注意事项"
    1. **忽略整数溢出**：整数溢出可导致严重安全问题
    2. **不安全的字符串函数**：strcpy、sprintf等不检查边界
    3. **未检查返回值**：忽略错误可能导致安全漏洞
    4. **悬空指针**：使用已释放的内存
    5. **缓冲区溢出**：数组越界访问
    6. **格式字符串漏洞**：用户输入作为格式字符串
    7. **路径遍历**：未验证文件路径
    8. **竞态条件**：多线程访问共享资源

## 实践练习

1. **漏洞识别练习**：
   - 识别代码中的安全漏洞
   - 分类漏洞类型（缓冲区溢出、整数溢出等）

2. **安全修复练习**：
   - 修复不安全的代码
   - 应用CERT C规则

3. **安全代码审查**：
   - 使用CERT C检查清单审查代码
   - 编写审查报告

4. **威胁建模练习**：
   - 为医疗设备识别安全威胁
   - 应用CERT C规则缓解威胁

## 自测问题

??? question "CERT C和MISRA C有什么区别？应该如何选择？"
    两个标准有不同的侧重点。
    
    ??? success "答案"
        **CERT C**：
        - 侧重安全性
        - 防止安全漏洞
        - 关注缓冲区溢出、整数溢出等安全问题
        - 适用于面临安全威胁的系统
        
        **MISRA C**：
        - 侧重可靠性和可维护性
        - 防止未定义行为
        - 关注代码质量和一致性
        - 适用于安全关键系统
        
        **选择建议**：
        - 医疗器械软件：建议同时应用两者
        - Class C设备：必须应用两者
        - 联网设备：必须应用CERT C
        - 两者互补，不冲突

??? question "为什么整数溢出是安全问题？"
    整数溢出可能导致严重的安全漏洞。
    
    ??? success "答案"
        整数溢出的安全影响：
        
        1. **缓冲区分配错误**：
           ```c
           size_t size = user_input * sizeof(int);  // 可能溢出
           int* buffer = malloc(size);  // 分配的内存太小
           ```
        
        2. **数组越界**：
           ```c
           unsigned int index = user_input + offset;  // 可能回绕
           array[index] = value;  // 越界访问
           ```
        
        3. **逻辑错误**：
           ```c
           if (a + b > MAX) {  // 如果a+b溢出，检查失败
               // 错误处理
           }
           ```
        
        **防范措施**：
        - 使用安全的整数运算函数
        - 在运算前检查溢出
        - 使用更大的数据类型
        - 使用编译器内置函数（如__builtin_add_overflow）

??? question "如何安全地处理用户输入？"
    用户输入是主要的攻击向量。
    
    ??? success "答案"
        安全处理用户输入的步骤：
        
        1. **验证输入**：
           - 检查空指针
           - 检查长度
           - 检查格式
           - 检查范围
        
        2. **清理输入**：
           - 移除危险字符
           - 转义特殊字符
           - 规范化路径
        
        3. **限制输入**：
           - 设置最大长度
           - 使用白名单而非黑名单
           - 限制允许的字符集
        
        4. **安全使用**：
           - 不要直接用于文件路径
           - 不要直接用于SQL查询
           - 不要直接用于系统命令
           - 不要直接用于格式字符串
        
        **原则**：永远不要信任用户输入

??? question "什么是格式字符串漏洞？如何防范？"
    格式字符串漏洞是严重的安全问题。
    
    ??? success "答案"
        **格式字符串漏洞**：
        
        ```c
        // 漏洞代码
        char user_input[100];
        gets(user_input);
        printf(user_input);  // 危险！
        ```
        
        **攻击示例**：
        - 用户输入"%s%s%s"可能导致崩溃
        - 用户输入"%n"可能写入内存
        - 用户输入"%x"可能泄露栈内容
        
        **防范方法**：
        
        ```c
        // 正确做法
        printf("%s", user_input);  // 使用格式字符串
        
        // 或使用fputs
        fputs(user_input, stdout);
        ```
        
        **规则**：永远不要将用户输入直接用作格式字符串

??? question "在医疗器械软件中，哪些CERT C规则最重要？"
    不同规则的优先级不同。
    
    ??? success "答案"
        医疗器械软件的高优先级CERT C规则：
        
        1. **INT30-C, INT32-C**：整数溢出
           - 影响剂量计算、时间计算等
        
        2. **ARR30-C, ARR38-C**：数组越界
           - 影响数据完整性和系统稳定性
        
        3. **STR31-C**：字符串缓冲区
           - 防止缓冲区溢出
        
        4. **MEM30-C, MEM34-C**：内存管理
           - 防止内存泄漏和悬空指针
        
        5. **FIO30-C**：文件操作
           - 防止路径遍历攻击
        
        6. **ERR33-C**：错误处理
           - 确保错误被正确处理
        
        7. **API00-C**：API设计
           - 确保接口安全
        
        优先级基于对患者安全的潜在影响。

## 相关资源

- [编码标准概述](index.md)
- [MISRA C编码规范](misra-c.md)
- [代码审查检查清单](code-review-checklist.md)
- [静态分析](../static-analysis/index.md)

## 参考文献

1. SEI CERT C Coding Standard, Software Engineering Institute, Carnegie Mellon University, 2016
2. Seacord, Robert C. "Secure Coding in C and C++, 2nd Edition." Addison-Wesley, 2013
3. Seacord, Robert C. "The CERT C Secure Coding Standard." Addison-Wesley, 2008
4. IEC 62304:2006+AMD1:2015 - Medical device software - Software life cycle processes
5. IEC 81001-5-1:2021 - Health software and health IT systems safety, effectiveness and security - Part 5-1: Security
6. FDA Guidance - Content of Premarket Submissions for Management of Cybersecurity in Medical Devices, 2014
7. 《C和C++安全编码》，Robert C. Seacord，机械工业出版社，2014
