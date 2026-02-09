---
title: 内存管理
description: 嵌入式C/C++中的内存管理技术，包括栈、堆、静态内存和内存池
difficulty: Intermediate
estimated_time: 2小时
tags:
- C语言
- 内存管理
- 嵌入式编程
related_modules:
- zh/technical-knowledge/embedded-c-cpp/pointer-operations
- zh/technical-knowledge/low-power-design
last_updated: '2026-02-07'
version: '1.0'
language: en-US
---


# Memory Management

## Learning Objectives

After completing this module, you will be able to:
- Understand memory layout and allocation strategies in embedded systems
- Master the use cases and limitations of stack, heap, and static memory
- Implement and use memory pool techniques
- Identify and avoid common memory management errors
- Apply memory safety practices in medical device software

## Prerequisites

- C language fundamentals
- Concepts of pointers and addresses
- Basic computer architecture knowledge

## Content

### Embedded System Memory Layout

In embedded systems, memory is typically divided into the following regions:

```
+------------------+  High Address
|   Stack          |  鈫?Grows downward
+------------------+
|        鈫?        |  Unused space
+------------------+
|   Heap           |  鈫?Grows upward
+------------------+
|   BSS (Uninitialized) |
+------------------+
|   Data (Initialized)  |
+------------------+
|   Text (Code)    |
+------------------+  Low Address
```

**Characteristics of Each Region**:

1. **Text Segment (Code)**: Stores program code, typically in Flash or ROM, read-only
2. **Data Segment**: Stores initialized global and static variables
3. **BSS Segment**: Stores uninitialized global and static variables, zeroed at startup
4. **Heap**: Dynamically allocated memory region, grows upward
5. **Stack**: Stores local variables, function parameters, and return addresses, grows downward

### Stack Memory Management

The stack is an automatically managed memory region following LIFO (Last In, First Out) principle.

**Advantages**:
- Fast allocation and deallocation
- Automatic management, no manual freeing required
- Contiguous memory, cache-friendly

**Disadvantages**:
- Fixed size, prone to overflow
- Lifetime limited to function scope
- Not suitable for large objects or dynamically sized data

**Example Code**:

```c
#include <stdint.h>

// Stack allocation - automatically freed when function returns
void stack_allocation_example(void) {
    uint8_t buffer[256];  // Allocate 256 bytes on stack
    int32_t sensor_value;
    
    // Use buffer and sensor_value
    sensor_value = read_sensor();
    process_data(buffer, sensor_value);
    
    // buffer and sensor_value automatically freed when function returns
}

// Dangerous: returning pointer to stack memory
uint8_t* dangerous_function(void) {
    uint8_t local_buffer[100];
    // Error! local_buffer is freed after function returns
    return local_buffer;  // Returns dangling pointer
}
```

**Best Practices**:
- Avoid allocating large arrays on stack (typically limit to a few KB)
- Don't return pointers to local variables
- Monitor stack usage and reserve sufficient stack space
- In RTOS, configure appropriate stack size for each task

!!! warning "Stack Overflow Risk"
    In medical device software, stack overflow can cause system crashes or unpredictable behavior. Must:
    - Use static analysis tools to detect potential stack overflows
    - Configure stack overflow detection mechanisms (e.g., MPU protection)
    - Perform worst-case stack usage analysis

### Heap Memory Management

The heap provides dynamic memory allocation but requires caution in embedded systems.

**Standard Heap Functions**:

```c
#include <stdlib.h>

void heap_allocation_example(void) {
    // Allocate memory
    uint8_t* buffer = (uint8_t*)malloc(1024);
    if (buffer == NULL) {
        // Handle allocation failure
        handle_allocation_error();
        return;
    }
    
    // Use buffer
    memset(buffer, 0, 1024);
    process_data(buffer, 1024);
    
    // Free memory
    free(buffer);
    buffer = NULL;  // Avoid dangling pointer
}
```

**Heap Problems**:

1. **Memory Fragmentation**: Frequent allocation and deallocation leads to fragmentation
2. **Non-determinism**: Allocation time is unpredictable
3. **Memory Leaks**: Forgetting to free leads to memory exhaustion
4. **Double Free**: Freeing the same memory twice causes crashes

!!! danger "Heap Usage Restrictions in Medical Devices"
    IEC 62304 and many medical device standards recommend:
    - Class B and C devices should avoid dynamic memory allocation
    - If necessary, requires thorough validation and testing
    - Consider using deterministic memory pools as alternative

### Static Memory Allocation

Static memory is allocated at compile time with lifetime spanning the entire program execution.

```c
// Global static variables
static uint8_t global_buffer[1024];
static sensor_data_t sensor_readings[100];

// Static variable within function
void static_allocation_example(void) {
    static uint32_t call_count = 0;  // Initialized only once
    call_count++;
    
    // call_count retains value between function calls
}
```

**Advantages**:
- Deterministic: allocated at compile time, no runtime overhead
- No fragmentation issues
- Clear lifetime

**Disadvantages**:
- Occupies RAM even when not in use
- Inflexible, fixed size
- Increases startup time (requires initialization)

### Memory Pool Technique

Memory pools are the recommended dynamic memory management method in medical device software.

**Memory Pool Principle**:
- Pre-allocate fixed-size memory blocks
- Provide deterministic allocation and deallocation
- Avoid memory fragmentation

**Implementation Example**:

```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define POOL_BLOCK_SIZE 128
#define POOL_BLOCK_COUNT 32

typedef struct {
    uint8_t data[POOL_BLOCK_SIZE];
    bool in_use;
} memory_block_t;

typedef struct {
    memory_block_t blocks[POOL_BLOCK_COUNT];
    uint32_t allocated_count;
    uint32_t peak_usage;
} memory_pool_t;

static memory_pool_t g_memory_pool;

// Initialize memory pool
void memory_pool_init(void) {
    memset(&g_memory_pool, 0, sizeof(memory_pool_t));
}

// Allocate from memory pool
void* memory_pool_alloc(void) {
    for (uint32_t i = 0; i < POOL_BLOCK_COUNT; i++) {
        if (!g_memory_pool.blocks[i].in_use) {
            g_memory_pool.blocks[i].in_use = true;
            g_memory_pool.allocated_count++;
            
            // Update peak usage
            if (g_memory_pool.allocated_count > g_memory_pool.peak_usage) {
                g_memory_pool.peak_usage = g_memory_pool.allocated_count;
            }
            
            return g_memory_pool.blocks[i].data;
        }
    }
    
    // Pool is full
    return NULL;
}

// Free to memory pool
void memory_pool_free(void* ptr) {
    if (ptr == NULL) {
        return;
    }
    
    // Find corresponding block
    for (uint32_t i = 0; i < POOL_BLOCK_COUNT; i++) {
        if (g_memory_pool.blocks[i].data == ptr) {
            if (g_memory_pool.blocks[i].in_use) {
                g_memory_pool.blocks[i].in_use = false;
                g_memory_pool.allocated_count--;
            }
            return;
        }
    }
    
    // Invalid pointer - log error
    log_error("Invalid pointer passed to memory_pool_free");
}

// Get memory pool statistics
void memory_pool_get_stats(uint32_t* allocated, uint32_t* peak) {
    *allocated = g_memory_pool.allocated_count;
    *peak = g_memory_pool.peak_usage;
}
```

### Medical Device Software Memory Management Best Practices

1. **Prioritize Static Allocation**
   - Determine all memory requirements at compile time
   - Avoid runtime non-determinism

2. **Use Memory Pools for Dynamic Allocation**
   - Provide deterministic allocation time
   - Avoid memory fragmentation
   - Facilitate monitoring and debugging

3. **Implement Memory Monitoring**
   ```c
   // Monitor stack usage
   void monitor_stack_usage(void) {
       extern uint32_t _stack_start;
       extern uint32_t _stack_end;
       uint32_t stack_size = &_stack_end - &_stack_start;
       uint32_t stack_used = get_stack_usage();
       
       if (stack_used > (stack_size * 0.8)) {
           log_warning("Stack usage high: %d/%d", stack_used, stack_size);
       }
   }
   ```

4. **Use Static Analysis Tools**
   - Coverity, PC-lint, etc. to detect memory errors
   - Comply with MISRA C rules

5. **Boundary Checking**
   ```c
   // Safe memory copy
   void safe_memcpy(void* dest, const void* src, size_t dest_size, size_t src_size) {
       size_t copy_size = (src_size < dest_size) ? src_size : dest_size;
       memcpy(dest, src, copy_size);
   }
   ```

## Practice Exercises

1. Implement a multi-level memory pool supporting different block sizes
2. Write a stack usage monitoring tool to detect stack overflow
3. Use Valgrind or similar tools to detect memory leaks
4. Analyze the memory layout of a simple program

## References

1. IEC 62304:2006+AMD1:2015 - Medical device software - Software life cycle processes
2. MISRA C:2012 - Guidelines for the use of the C language in critical systems
3. "Embedded C Coding Standard" by Michael Barr
4. ISO 26262 - Road vehicles - Functional safety (memory management sections)
5. "Memory Management in Embedded Systems" - Embedded.com article series

## Self-Assessment Questions

??? question "Question 1: What are the main differences between stack and heap?"
    **Question**: List at least 3 main differences between stack memory and heap memory.
    
    ??? success "Answer"
        Main differences include:
        
        1. **Allocation Method**:
           - Stack: Automatically allocated and freed, managed by compiler
           - Heap: Manually allocated and freed, requires malloc/free calls
        
        2. **Lifetime**:
           - Stack: Variable lifetime limited to function scope
           - Heap: Variable lifetime controlled by programmer
        
        3. **Size**:
           - Stack: Typically smaller (few KB to few MB)
           - Heap: Typically larger, limited by system memory
        
        4. **Speed**:
           - Stack: Fast allocation, only requires moving stack pointer
           - Heap: Slow allocation, requires finding suitable memory block
        
        5. **Fragmentation**:
           - Stack: No fragmentation
           - Heap: Frequent allocation/deallocation causes memory fragmentation
        
        **Key Takeaway**: In medical device software, prioritize stack or static allocation to avoid heap non-determinism.

??? question "Question 2: What is stack overflow and how to prevent it?"
    **Question**: Explain causes of stack overflow and provide at least 3 prevention methods.
    
    ??? success "Answer"
        **Stack Overflow Causes**:
        - Allocating too large arrays or structures on stack
        - Deep recursion
        - Too many function call levels
        - Insufficient stack size configuration
        
        **Prevention Methods**:
        
        1. **Avoid Large Arrays**:
           ```c
           // Wrong
           void function(void) {
               uint8_t large_buffer[10000];  // 10KB on stack
           }
           
           // Correct
           static uint8_t large_buffer[10000];  // Static allocation
           ```
        
        2. **Limit Recursion Depth**:
           ```c
           int recursive_function(int n, int depth) {
               if (depth > MAX_RECURSION_DEPTH) {
                   return ERROR_TOO_DEEP;
               }
               // Recursive logic
           }
           ```
        
        3. **Configure Sufficient Stack Space**:
           - Allocate appropriate stack size for each task in RTOS
           - Use stack usage analysis tools to determine actual requirements
        
        4. **Use Static Analysis Tools**:
           - Use tools to detect potential stack overflows
           - Perform worst-case stack usage analysis
        
        5. **Implement Stack Monitoring**:
           ```c
           void monitor_stack(void) {
               uint32_t stack_used = get_stack_usage();
               if (stack_used > STACK_WARNING_THRESHOLD) {
                   log_warning("Stack usage high");
               }
           }
           ```
        
        **Key Takeaway**: Stack overflow is a serious issue in medical device software that must be prevented through design and testing.

## Related Resources

- [Pointer Operations](pointer-operations.md)
- [Low Power Design](../../low-power-design/index.md)
- [MISRA C Coding Standards](/zh/software-engineering/coding-standards/misra-c.md)