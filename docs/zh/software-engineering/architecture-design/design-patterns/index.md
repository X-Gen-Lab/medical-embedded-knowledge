---
title: 设计模式（Design Patterns）
description: 医疗器械嵌入式软件中常用的设计模式及其应用
difficulty: 中级
estimated_time: 120分钟
tags:
- 设计模式
- 软件架构
- 面向对象
- 嵌入式
- 医疗器械
related_modules:
- zh/software-engineering/architecture-design
- zh/software-engineering/architecture-design/modular-design
- zh/software-engineering/architecture-design/layered-architecture
last_updated: '2026-02-09'
version: '1.0'
language: zh
---

# 设计模式（Design Patterns）

## 学习目标

完成本模块后，你将能够：
- 理解设计模式的概念和分类
- 掌握医疗器械嵌入式软件中常用的设计模式
- 在C语言中实现经典设计模式
- 识别何时应该使用特定的设计模式
- 避免设计模式的误用和过度使用
- 将设计模式应用于实际的医疗器械项目
- 理解设计模式如何支持IEC 62304合规性

## 前置知识

- C/C++编程基础
- 函数指针和结构体
- 模块化设计原则
- 软件架构基础
- 面向对象概念（封装、继承、多态）

## 内容

### 概念介绍

设计模式是软件设计中常见问题的可复用解决方案。它们是经过验证的最佳实践，可以提高代码的可维护性、可扩展性和可读性。

**设计模式的三大类**：
1. **创建型模式（Creational Patterns）**：关注对象创建机制
2. **结构型模式（Structural Patterns）**：关注对象组合和关系
3. **行为型模式（Behavioral Patterns）**：关注对象间的通信和职责分配

**在医疗器械软件中的价值**：
- 提供经过验证的解决方案
- 提高代码质量和可维护性
- 促进团队沟通（共同语言）
- 支持需求追溯和文档化
- 便于代码审查和验证

### 创建型模式

#### 1. 工厂模式（Factory Pattern）

**目的**：提供创建对象的统一接口，隐藏创建逻辑。

**适用场景**：
- 需要根据配置或条件创建不同类型的对象
- 对象创建过程复杂
- 需要集中管理对象创建

**C语言实现**：

```c
// sensor_factory.h
typedef enum {
    SENSOR_TYPE_TEMPERATURE,
    SENSOR_TYPE_PRESSURE,
    SENSOR_TYPE_SPO2,
    SENSOR_TYPE_ECG
} SensorType;

// 通用传感器接口
typedef struct {
    int (*init)(void);
    int (*read)(void* data, size_t size);
    int (*deinit)(void);
    void* context;  // 传感器特定上下文
} Sensor;

// 工厂函数
Sensor* sensor_factory_create(SensorType type);
void sensor_factory_destroy(Sensor* sensor);

// sensor_factory.c
Sensor* sensor_factory_create(SensorType type) {
    Sensor* sensor = (Sensor*)malloc(sizeof(Sensor));
    if (sensor == NULL) {
        return NULL;
    }
    
    switch (type) {
        case SENSOR_TYPE_TEMPERATURE:
            sensor->init = temp_sensor_init;
            sensor->read = temp_sensor_read;
            sensor->deinit = temp_sensor_deinit;
            sensor->context = create_temp_context();
            break;
            
        case SENSOR_TYPE_PRESSURE:
            sensor->init = pressure_sensor_init;
            sensor->read = pressure_sensor_read;
            sensor->deinit = pressure_sensor_deinit;
            sensor->context = create_pressure_context();
            break;
            
        case SENSOR_TYPE_SPO2:
            sensor->init = spo2_sensor_init;
            sensor->read = spo2_sensor_read;
            sensor->deinit = spo2_sensor_deinit;
            sensor->context = create_spo2_context();
            break;
            
        default:
            free(sensor);
            return NULL;
    }
    
    return sensor;
}

void sensor_factory_destroy(Sensor* sensor) {
    if (sensor != NULL) {
        if (sensor->context != NULL) {
            free(sensor->context);
        }
        free(sensor);
    }
}

// 使用示例
void measure_temperature(void) {
    Sensor* temp_sensor = sensor_factory_create(SENSOR_TYPE_TEMPERATURE);
    if (temp_sensor == NULL) {
        return;
    }
    
    temp_sensor->init();
    
    float temperature;
    temp_sensor->read(&temperature, sizeof(temperature));
    
    printf("Temperature: %.1f°C\n", temperature);
    
    temp_sensor->deinit();
    sensor_factory_destroy(temp_sensor);
}
```

**医疗器械应用示例**：

```c
// 多参数监护仪的传感器管理
typedef struct {
    Sensor* sensors[MAX_SENSORS];
    size_t sensor_count;
} MonitorSystem;

int monitor_init(MonitorSystem* monitor, const SensorType* types, size_t count) {
    monitor->sensor_count = 0;
    
    for (size_t i = 0; i < count && i < MAX_SENSORS; i++) {
        Sensor* sensor = sensor_factory_create(types[i]);
        if (sensor == NULL) {
            // 清理已创建的传感器
            for (size_t j = 0; j < monitor->sensor_count; j++) {
                sensor_factory_destroy(monitor->sensors[j]);
            }
            return -1;
        }
        
        if (sensor->init() != 0) {
            sensor_factory_destroy(sensor);
            continue;  // 跳过初始化失败的传感器
        }
        
        monitor->sensors[monitor->sensor_count++] = sensor;
    }
    
    return monitor->sensor_count > 0 ? 0 : -1;
}
```

#### 2. 单例模式（Singleton Pattern）

**目的**：确保一个类只有一个实例，并提供全局访问点。

**适用场景**：
- 系统配置管理
- 日志记录器
- 硬件资源管理（如UART、SPI控制器）

**C语言实现**：

```c
// logger.h
typedef struct Logger Logger;

// 获取单例实例
Logger* logger_get_instance(void);

// 日志接口
void logger_log(Logger* logger, LogLevel level, const char* message);
void logger_log_error(Logger* logger, const char* message);
void logger_log_info(Logger* logger, const char* message);

// logger.c
struct Logger {
    FILE* log_file;
    LogLevel min_level;
    bool initialized;
};

static Logger g_logger_instance = {
    .log_file = NULL,
    .min_level = LOG_LEVEL_INFO,
    .initialized = false
};

Logger* logger_get_instance(void) {
    if (!g_logger_instance.initialized) {
        g_logger_instance.log_file = fopen("system.log", "a");
        g_logger_instance.initialized = true;
    }
    return &g_logger_instance;
}

void logger_log(Logger* logger, LogLevel level, const char* message) {
    if (logger == NULL || logger->log_file == NULL) {
        return;
    }
    
    if (level < logger->min_level) {
        return;
    }
    
    time_t now = time(NULL);
    fprintf(logger->log_file, "[%s] %s: %s\n", 
            ctime(&now), log_level_to_string(level), message);
    fflush(logger->log_file);
}

// 使用示例
void some_function(void) {
    Logger* logger = logger_get_instance();
    logger_log_info(logger, "Function started");
    
    // 执行操作
    
    logger_log_info(logger, "Function completed");
}
```

**线程安全的单例（RTOS环境）**：

```c
// config_manager.h
typedef struct ConfigManager ConfigManager;

ConfigManager* config_manager_get_instance(void);
int config_manager_get_value(ConfigManager* mgr, const char* key, char* value, size_t size);
int config_manager_set_value(ConfigManager* mgr, const char* key, const char* value);

// config_manager.c
struct ConfigManager {
    ConfigEntry* entries;
    size_t entry_count;
    SemaphoreHandle_t mutex;
    bool initialized;
};

static ConfigManager g_config_instance = {
    .entries = NULL,
    .entry_count = 0,
    .mutex = NULL,
    .initialized = false
};

ConfigManager* config_manager_get_instance(void) {
    // 双重检查锁定（Double-Checked Locking）
    if (!g_config_instance.initialized) {
        taskENTER_CRITICAL();
        
        if (!g_config_instance.initialized) {
            g_config_instance.mutex = xSemaphoreCreateMutex();
            g_config_instance.entries = load_config_from_flash();
            g_config_instance.initialized = true;
        }
        
        taskEXIT_CRITICAL();
    }
    
    return &g_config_instance;
}

int config_manager_get_value(ConfigManager* mgr, const char* key, char* value, size_t size) {
    if (mgr == NULL || key == NULL || value == NULL) {
        return -1;
    }
    
    xSemaphoreTake(mgr->mutex, portMAX_DELAY);
    
    int result = find_and_copy_value(mgr->entries, mgr->entry_count, key, value, size);
    
    xSemaphoreGive(mgr->mutex);
    
    return result;
}
```


### 结构型模式

#### 3. 适配器模式（Adapter Pattern）

**目的**：将一个接口转换成客户期望的另一个接口，使原本不兼容的接口可以协同工作。

**适用场景**：
- 集成第三方库或遗留代码
- 统一不同硬件的接口
- 支持多种通信协议

**C语言实现**：

```c
// 目标接口（我们期望的接口）
typedef struct {
    int (*send)(const uint8_t* data, size_t len);
    int (*receive)(uint8_t* buffer, size_t len);
} CommunicationInterface;

// 适配器：UART到通用通信接口
typedef struct {
    CommunicationInterface base;
    UART_Handle uart_handle;
} UARTAdapter;

static int uart_adapter_send(const uint8_t* data, size_t len) {
    UARTAdapter* adapter = container_of(base, UARTAdapter, base);
    return UART_write(adapter->uart_handle, data, len);
}

static int uart_adapter_receive(uint8_t* buffer, size_t len) {
    UARTAdapter* adapter = container_of(base, UARTAdapter, base);
    return UART_read(adapter->uart_handle, buffer, len);
}

UARTAdapter* uart_adapter_create(UART_Handle handle) {
    UARTAdapter* adapter = malloc(sizeof(UARTAdapter));
    if (adapter != NULL) {
        adapter->base.send = uart_adapter_send;
        adapter->base.receive = uart_adapter_receive;
        adapter->uart_handle = handle;
    }
    return adapter;
}

// 适配器：SPI到通用通信接口
typedef struct {
    CommunicationInterface base;
    SPI_Handle spi_handle;
    GPIO_Pin cs_pin;
} SPIAdapter;

static int spi_adapter_send(const uint8_t* data, size_t len) {
    SPIAdapter* adapter = container_of(base, SPIAdapter, base);
    GPIO_write(adapter->cs_pin, 0);  // CS低电平
    int result = SPI_transfer(adapter->spi_handle, data, NULL, len);
    GPIO_write(adapter->cs_pin, 1);  // CS高电平
    return result;
}

// 使用示例：统一的数据传输函数
int send_patient_data(CommunicationInterface* comm, const PatientData* data) {
    uint8_t buffer[256];
    size_t len = serialize_patient_data(data, buffer, sizeof(buffer));
    return comm->send(buffer, len);
}

// 可以使用UART或SPI，无需修改上层代码
void example_usage(void) {
    // 使用UART
    UARTAdapter* uart = uart_adapter_create(uart_handle);
    send_patient_data((CommunicationInterface*)uart, &patient_data);
    
    // 使用SPI
    SPIAdapter* spi = spi_adapter_create(spi_handle, cs_pin);
    send_patient_data((CommunicationInterface*)spi, &patient_data);
}
```

#### 4. 装饰器模式（Decorator Pattern）

**目的**：动态地给对象添加额外的职责，而不修改其结构。

**适用场景**：
- 添加日志记录
- 添加数据验证
- 添加加密/解密
- 添加缓存

**C语言实现**：

```c
// 基础数据存储接口
typedef struct Storage Storage;

struct Storage {
    int (*write)(Storage* self, const void* data, size_t size);
    int (*read)(Storage* self, void* data, size_t size);
    void* context;
};

// 基础Flash存储实现
typedef struct {
    Storage base;
    uint32_t address;
} FlashStorage;

static int flash_write(Storage* self, const void* data, size_t size) {
    FlashStorage* flash = (FlashStorage*)self;
    return flash_program(flash->address, data, size);
}

static int flash_read(Storage* self, void* data, size_t size) {
    FlashStorage* flash = (FlashStorage*)self;
    return flash_read_data(flash->address, data, size);
}

// 装饰器：添加CRC校验
typedef struct {
    Storage base;
    Storage* wrapped;  // 被装饰的存储对象
} CRCDecorator;

static int crc_decorator_write(Storage* self, const void* data, size_t size) {
    CRCDecorator* decorator = (CRCDecorator*)self;
    
    // 计算CRC
    uint16_t crc = calculate_crc(data, size);
    
    // 写入数据
    int result = decorator->wrapped->write(decorator->wrapped, data, size);
    if (result != 0) {
        return result;
    }
    
    // 写入CRC
    return decorator->wrapped->write(decorator->wrapped, &crc, sizeof(crc));
}

static int crc_decorator_read(Storage* self, void* data, size_t size) {
    CRCDecorator* decorator = (CRCDecorator*)self;
    
    // 读取数据
    int result = decorator->wrapped->read(decorator->wrapped, data, size);
    if (result != 0) {
        return result;
    }
    
    // 读取并验证CRC
    uint16_t stored_crc, calculated_crc;
    decorator->wrapped->read(decorator->wrapped, &stored_crc, sizeof(stored_crc));
    calculated_crc = calculate_crc(data, size);
    
    return (stored_crc == calculated_crc) ? 0 : -1;
}

// 装饰器：添加加密
typedef struct {
    Storage base;
    Storage* wrapped;
    uint8_t encryption_key[16];
} EncryptionDecorator;

static int encryption_decorator_write(Storage* self, const void* data, size_t size) {
    EncryptionDecorator* decorator = (EncryptionDecorator*)self;
    
    // 加密数据
    uint8_t* encrypted = malloc(size);
    aes_encrypt(data, encrypted, size, decorator->encryption_key);
    
    // 写入加密数据
    int result = decorator->wrapped->write(decorator->wrapped, encrypted, size);
    
    free(encrypted);
    return result;
}

// 使用示例：组合多个装饰器
void example_decorated_storage(void) {
    // 创建基础Flash存储
    FlashStorage* flash = create_flash_storage(0x08000000);
    
    // 添加CRC校验装饰器
    CRCDecorator* crc_storage = create_crc_decorator((Storage*)flash);
    
    // 添加加密装饰器
    EncryptionDecorator* encrypted_storage = 
        create_encryption_decorator((Storage*)crc_storage, encryption_key);
    
    // 使用装饰后的存储（自动加密+CRC校验）
    PatientData data;
    encrypted_storage->base.write((Storage*)encrypted_storage, &data, sizeof(data));
}
```

### 行为型模式

#### 5. 观察者模式（Observer Pattern）

**目的**：定义对象间的一对多依赖关系，当一个对象状态改变时，所有依赖它的对象都会收到通知。

**适用场景**：
- 事件处理系统
- 数据变化通知
- 报警系统
- UI更新

**C语言实现**：

```c
// 观察者接口
typedef void (*ObserverCallback)(void* observer, const void* subject, const void* data);

typedef struct Observer {
    ObserverCallback callback;
    void* context;
    struct Observer* next;
} Observer;

// 主题（被观察者）
typedef struct {
    Observer* observers;
    void* data;
} Subject;

// 注册观察者
void subject_attach(Subject* subject, Observer* observer) {
    observer->next = subject->observers;
    subject->observers = observer;
}

// 移除观察者
void subject_detach(Subject* subject, Observer* observer) {
    Observer** current = &subject->observers;
    while (*current != NULL) {
        if (*current == observer) {
            *current = observer->next;
            return;
        }
        current = &(*current)->next;
    }
}

// 通知所有观察者
void subject_notify(Subject* subject, const void* data) {
    Observer* observer = subject->observers;
    while (observer != NULL) {
        observer->callback(observer->context, subject, data);
        observer = observer->next;
    }
}

// 医疗器械应用：心率监测
typedef struct {
    Subject base;
    uint16_t heart_rate;
    uint16_t threshold_low;
    uint16_t threshold_high;
} HeartRateMonitor;

void heart_rate_update(HeartRateMonitor* monitor, uint16_t new_rate) {
    monitor->heart_rate = new_rate;
    subject_notify(&monitor->base, &new_rate);
}

// 观察者1：显示模块
void display_observer_callback(void* context, const void* subject, const void* data) {
    uint16_t heart_rate = *(const uint16_t*)data;
    update_heart_rate_display(heart_rate);
}

// 观察者2：报警模块
void alarm_observer_callback(void* context, const void* subject, const void* data) {
    HeartRateMonitor* monitor = (HeartRateMonitor*)subject;
    uint16_t heart_rate = *(const uint16_t*)data;
    
    if (heart_rate < monitor->threshold_low) {
        trigger_alarm(ALARM_BRADYCARDIA);
    } else if (heart_rate > monitor->threshold_high) {
        trigger_alarm(ALARM_TACHYCARDIA);
    }
}

// 观察者3：数据记录模块
void logger_observer_callback(void* context, const void* subject, const void* data) {
    uint16_t heart_rate = *(const uint16_t*)data;
    log_measurement(MEASUREMENT_HEART_RATE, heart_rate, get_timestamp());
}

// 使用示例
void setup_heart_rate_monitoring(void) {
    HeartRateMonitor monitor;
    monitor.threshold_low = 50;
    monitor.threshold_high = 120;
    
    // 创建观察者
    Observer display_observer = {
        .callback = display_observer_callback,
        .context = NULL
    };
    
    Observer alarm_observer = {
        .callback = alarm_observer_callback,
        .context = NULL
    };
    
    Observer logger_observer = {
        .callback = logger_observer_callback,
        .context = NULL
    };
    
    // 注册观察者
    subject_attach(&monitor.base, &display_observer);
    subject_attach(&monitor.base, &alarm_observer);
    subject_attach(&monitor.base, &logger_observer);
    
    // 更新心率时，所有观察者自动收到通知
    heart_rate_update(&monitor, 75);
}
```

#### 6. 状态模式（State Pattern）

**目的**：允许对象在内部状态改变时改变其行为。

**适用场景**：
- 设备状态机
- 协议状态管理
- 用户界面状态
- 测量流程控制

**C语言实现**：

```c
// 状态接口
typedef struct State State;
typedef struct Context Context;

struct State {
    void (*enter)(Context* ctx);
    void (*exit)(Context* ctx);
    void (*handle_event)(Context* ctx, Event event);
};

// 上下文
struct Context {
    State* current_state;
    void* data;
};

void context_change_state(Context* ctx, State* new_state) {
    if (ctx->current_state != NULL && ctx->current_state->exit != NULL) {
        ctx->current_state->exit(ctx);
    }
    
    ctx->current_state = new_state;
    
    if (new_state != NULL && new_state->enter != NULL) {
        new_state->enter(ctx);
    }
}

void context_handle_event(Context* ctx, Event event) {
    if (ctx->current_state != NULL && ctx->current_state->handle_event != NULL) {
        ctx->current_state->handle_event(ctx, event);
    }
}

// 医疗器械应用：血压计状态机
typedef struct {
    Context base;
    uint16_t systolic;
    uint16_t diastolic;
    uint16_t pulse;
} BPMonitor;

// 空闲状态
static void idle_state_enter(Context* ctx) {
    display_message("Ready to measure");
    turn_off_pump();
}

static void idle_state_handle_event(Context* ctx, Event event) {
    if (event == EVENT_START_BUTTON) {
        context_change_state(ctx, &inflating_state);
    }
}

static State idle_state = {
    .enter = idle_state_enter,
    .exit = NULL,
    .handle_event = idle_state_handle_event
};

// 充气状态
static void inflating_state_enter(Context* ctx) {
    display_message("Inflating...");
    turn_on_pump();
}

static void inflating_state_exit(Context* ctx) {
    turn_off_pump();
}

static void inflating_state_handle_event(Context* ctx, Event event) {
    BPMonitor* monitor = (BPMonitor*)ctx;
    
    if (event == EVENT_PRESSURE_TARGET_REACHED) {
        context_change_state(ctx, &measuring_state);
    } else if (event == EVENT_STOP_BUTTON) {
        context_change_state(ctx, &idle_state);
    }
}

static State inflating_state = {
    .enter = inflating_state_enter,
    .exit = inflating_state_exit,
    .handle_event = inflating_state_handle_event
};

// 测量状态
static void measuring_state_enter(Context* ctx) {
    display_message("Measuring...");
    start_measurement();
}

static void measuring_state_handle_event(Context* ctx, Event event) {
    BPMonitor* monitor = (BPMonitor*)ctx;
    
    if (event == EVENT_MEASUREMENT_COMPLETE) {
        // 保存测量结果
        monitor->systolic = get_systolic();
        monitor->diastolic = get_diastolic();
        monitor->pulse = get_pulse();
        
        context_change_state(ctx, &result_state);
    } else if (event == EVENT_MEASUREMENT_ERROR) {
        context_change_state(ctx, &error_state);
    }
}

static State measuring_state = {
    .enter = measuring_state_enter,
    .exit = NULL,
    .handle_event = measuring_state_handle_event
};

// 结果显示状态
static void result_state_enter(Context* ctx) {
    BPMonitor* monitor = (BPMonitor*)ctx;
    display_result(monitor->systolic, monitor->diastolic, monitor->pulse);
    save_measurement(monitor->systolic, monitor->diastolic, monitor->pulse);
}

static void result_state_handle_event(Context* ctx, Event event) {
    if (event == EVENT_OK_BUTTON) {
        context_change_state(ctx, &idle_state);
    }
}

static State result_state = {
    .enter = result_state_enter,
    .exit = NULL,
    .handle_event = result_state_handle_event
};

// 错误状态
static void error_state_enter(Context* ctx) {
    display_message("Measurement error");
    trigger_error_alarm();
}

static void error_state_handle_event(Context* ctx, Event event) {
    if (event == EVENT_OK_BUTTON) {
        context_change_state(ctx, &idle_state);
    }
}

static State error_state = {
    .enter = error_state_enter,
    .exit = NULL,
    .handle_event = error_state_handle_event
};
```


#### 7. 策略模式（Strategy Pattern）

**目的**：定义一系列算法，将每个算法封装起来，并使它们可以互换。

**适用场景**：
- 多种算法选择（滤波算法、计算方法）
- 不同的数据处理策略
- 可配置的行为

**C语言实现**：

```c
// 策略接口
typedef struct {
    int (*process)(const void* input, void* output, size_t size);
    const char* name;
} ProcessingStrategy;

// 策略1：简单移动平均滤波
static int moving_average_process(const void* input, void* output, size_t size) {
    const int16_t* in = (const int16_t*)input;
    int16_t* out = (int16_t*)output;
    
    for (size_t i = 0; i < size; i++) {
        int32_t sum = 0;
        size_t count = 0;
        
        for (int j = -2; j <= 2; j++) {
            int idx = i + j;
            if (idx >= 0 && idx < size) {
                sum += in[idx];
                count++;
            }
        }
        
        out[i] = sum / count;
    }
    
    return 0;
}

static ProcessingStrategy moving_average_strategy = {
    .process = moving_average_process,
    .name = "Moving Average"
};

// 策略2：中值滤波
static int median_filter_process(const void* input, void* output, size_t size) {
    const int16_t* in = (const int16_t*)input;
    int16_t* out = (int16_t*)output;
    
    for (size_t i = 0; i < size; i++) {
        int16_t window[5];
        size_t count = 0;
        
        for (int j = -2; j <= 2; j++) {
            int idx = i + j;
            if (idx >= 0 && idx < size) {
                window[count++] = in[idx];
            }
        }
        
        // 排序并取中值
        qsort(window, count, sizeof(int16_t), compare_int16);
        out[i] = window[count / 2];
    }
    
    return 0;
}

static ProcessingStrategy median_filter_strategy = {
    .process = median_filter_process,
    .name = "Median Filter"
};

// 策略3：卡尔曼滤波
static int kalman_filter_process(const void* input, void* output, size_t size) {
    // 卡尔曼滤波实现
    return 0;
}

static ProcessingStrategy kalman_filter_strategy = {
    .process = kalman_filter_process,
    .name = "Kalman Filter"
};

// 使用策略的上下文
typedef struct {
    ProcessingStrategy* strategy;
    void* config;
} SignalProcessor;

int signal_processor_process(SignalProcessor* processor, 
                            const void* input, void* output, size_t size) {
    if (processor->strategy == NULL) {
        return -1;
    }
    
    return processor->strategy->process(input, output, size);
}

void signal_processor_set_strategy(SignalProcessor* processor, 
                                  ProcessingStrategy* strategy) {
    processor->strategy = strategy;
}

// 使用示例
void example_strategy_usage(void) {
    SignalProcessor processor;
    int16_t input[100], output[100];
    
    // 读取信号
    read_signal(input, 100);
    
    // 根据配置选择策略
    FilterType filter_type = get_filter_config();
    
    switch (filter_type) {
        case FILTER_MOVING_AVERAGE:
            signal_processor_set_strategy(&processor, &moving_average_strategy);
            break;
        case FILTER_MEDIAN:
            signal_processor_set_strategy(&processor, &median_filter_strategy);
            break;
        case FILTER_KALMAN:
            signal_processor_set_strategy(&processor, &kalman_filter_strategy);
            break;
    }
    
    // 处理信号（使用选定的策略）
    signal_processor_process(&processor, input, output, 100);
}
```

#### 8. 命令模式（Command Pattern）

**目的**：将请求封装为对象，从而可以参数化客户端、队列请求、记录日志、支持撤销操作。

**适用场景**：
- 操作队列
- 事件记录
- 撤销/重做功能
- 宏命令

**C语言实现**：

```c
// 命令接口
typedef struct Command Command;

struct Command {
    int (*execute)(Command* self);
    int (*undo)(Command* self);
    void* context;
};

// 具体命令：设置报警阈值
typedef struct {
    Command base;
    AlarmType alarm_type;
    float new_threshold;
    float old_threshold;  // 用于撤销
} SetThresholdCommand;

static int set_threshold_execute(Command* self) {
    SetThresholdCommand* cmd = (SetThresholdCommand*)self;
    
    // 保存旧值
    cmd->old_threshold = get_alarm_threshold(cmd->alarm_type);
    
    // 设置新值
    return set_alarm_threshold(cmd->alarm_type, cmd->new_threshold);
}

static int set_threshold_undo(Command* self) {
    SetThresholdCommand* cmd = (SetThresholdCommand*)self;
    
    // 恢复旧值
    return set_alarm_threshold(cmd->alarm_type, cmd->old_threshold);
}

Command* create_set_threshold_command(AlarmType type, float threshold) {
    SetThresholdCommand* cmd = malloc(sizeof(SetThresholdCommand));
    if (cmd != NULL) {
        cmd->base.execute = set_threshold_execute;
        cmd->base.undo = set_threshold_undo;
        cmd->alarm_type = type;
        cmd->new_threshold = threshold;
    }
    return (Command*)cmd;
}

// 命令队列
typedef struct {
    Command* commands[MAX_COMMANDS];
    size_t count;
    size_t current;  // 当前位置（用于撤销/重做）
} CommandQueue;

int command_queue_execute(CommandQueue* queue, Command* cmd) {
    if (queue->count >= MAX_COMMANDS) {
        return -1;
    }
    
    int result = cmd->execute(cmd);
    if (result == 0) {
        // 清除当前位置之后的命令（如果有）
        for (size_t i = queue->current; i < queue->count; i++) {
            free(queue->commands[i]);
        }
        
        // 添加新命令
        queue->commands[queue->current] = cmd;
        queue->count = queue->current + 1;
        queue->current++;
    }
    
    return result;
}

int command_queue_undo(CommandQueue* queue) {
    if (queue->current == 0) {
        return -1;  // 没有可撤销的命令
    }
    
    queue->current--;
    return queue->commands[queue->current]->undo(queue->commands[queue->current]);
}

int command_queue_redo(CommandQueue* queue) {
    if (queue->current >= queue->count) {
        return -1;  // 没有可重做的命令
    }
    
    int result = queue->commands[queue->current]->execute(queue->commands[queue->current]);
    if (result == 0) {
        queue->current++;
    }
    
    return result;
}

// 使用示例
void example_command_usage(void) {
    CommandQueue queue = {0};
    
    // 执行命令
    Command* cmd1 = create_set_threshold_command(ALARM_HR_HIGH, 120.0);
    command_queue_execute(&queue, cmd1);
    
    Command* cmd2 = create_set_threshold_command(ALARM_HR_LOW, 50.0);
    command_queue_execute(&queue, cmd2);
    
    // 撤销最后一个命令
    command_queue_undo(&queue);
    
    // 重做
    command_queue_redo(&queue);
}
```

### 医疗器械特定模式

#### 9. 管道-过滤器模式（Pipeline-Filter Pattern）

**目的**：将数据处理分解为一系列独立的处理步骤（过滤器），通过管道连接。

**适用场景**：
- 信号处理链
- 数据转换流程
- 多阶段验证

**C语言实现**：

```c
// 过滤器接口
typedef struct Filter Filter;

struct Filter {
    int (*process)(Filter* self, const void* input, void* output, size_t* output_size);
    Filter* next;
    void* context;
};

// 管道
typedef struct {
    Filter* first_filter;
    Filter* last_filter;
} Pipeline;

void pipeline_add_filter(Pipeline* pipeline, Filter* filter) {
    if (pipeline->first_filter == NULL) {
        pipeline->first_filter = filter;
        pipeline->last_filter = filter;
    } else {
        pipeline->last_filter->next = filter;
        pipeline->last_filter = filter;
    }
    filter->next = NULL;
}

int pipeline_process(Pipeline* pipeline, const void* input, void* output, size_t* output_size) {
    if (pipeline->first_filter == NULL) {
        return -1;
    }
    
    // 使用两个缓冲区交替处理
    uint8_t buffer1[MAX_BUFFER_SIZE];
    uint8_t buffer2[MAX_BUFFER_SIZE];
    
    const void* current_input = input;
    void* current_output = buffer1;
    size_t current_size = *output_size;
    
    Filter* filter = pipeline->first_filter;
    bool use_buffer1 = true;
    
    while (filter != NULL) {
        int result = filter->process(filter, current_input, current_output, &current_size);
        if (result != 0) {
            return result;
        }
        
        // 准备下一次迭代
        current_input = current_output;
        current_output = use_buffer1 ? buffer2 : buffer1;
        use_buffer1 = !use_buffer1;
        
        filter = filter->next;
    }
    
    // 复制最终结果
    memcpy(output, current_input, current_size);
    *output_size = current_size;
    
    return 0;
}

// ECG信号处理管道示例
// 过滤器1：去除基线漂移
static int baseline_removal_process(Filter* self, const void* input, 
                                   void* output, size_t* output_size) {
    const int16_t* in = (const int16_t*)input;
    int16_t* out = (int16_t*)output;
    size_t count = *output_size / sizeof(int16_t);
    
    // 高通滤波去除基线漂移
    apply_highpass_filter(in, out, count, 0.5);  // 0.5 Hz截止频率
    
    return 0;
}

// 过滤器2：50Hz陷波滤波
static int notch_filter_process(Filter* self, const void* input, 
                               void* output, size_t* output_size) {
    const int16_t* in = (const int16_t*)input;
    int16_t* out = (int16_t*)output;
    size_t count = *output_size / sizeof(int16_t);
    
    // 去除50Hz工频干扰
    apply_notch_filter(in, out, count, 50.0);
    
    return 0;
}

// 过滤器3：低通滤波
static int lowpass_filter_process(Filter* self, const void* input, 
                                 void* output, size_t* output_size) {
    const int16_t* in = (const int16_t*)input;
    int16_t* out = (int16_t*)output;
    size_t count = *output_size / sizeof(int16_t);
    
    // 低通滤波去除高频噪声
    apply_lowpass_filter(in, out, count, 40.0);  // 40 Hz截止频率
    
    return 0;
}

// 过滤器4：QRS检测
static int qrs_detection_process(Filter* self, const void* input, 
                                void* output, size_t* output_size) {
    const int16_t* in = (const int16_t*)input;
    QRSResult* result = (QRSResult*)output;
    size_t count = *output_size / sizeof(int16_t);
    
    // 检测QRS波群
    detect_qrs_complex(in, count, result);
    
    *output_size = sizeof(QRSResult);
    return 0;
}

// 构建ECG处理管道
Pipeline* create_ecg_pipeline(void) {
    Pipeline* pipeline = malloc(sizeof(Pipeline));
    pipeline->first_filter = NULL;
    pipeline->last_filter = NULL;
    
    // 添加过滤器
    Filter* baseline_filter = create_filter(baseline_removal_process);
    Filter* notch_filter = create_filter(notch_filter_process);
    Filter* lowpass_filter = create_filter(lowpass_filter_process);
    Filter* qrs_filter = create_filter(qrs_detection_process);
    
    pipeline_add_filter(pipeline, baseline_filter);
    pipeline_add_filter(pipeline, notch_filter);
    pipeline_add_filter(pipeline, lowpass_filter);
    pipeline_add_filter(pipeline, qrs_filter);
    
    return pipeline;
}

// 使用管道
void process_ecg_signal(const int16_t* raw_signal, size_t signal_len) {
    Pipeline* pipeline = create_ecg_pipeline();
    
    QRSResult result;
    size_t output_size = sizeof(result);
    
    pipeline_process(pipeline, raw_signal, &result, &output_size);
    
    // 使用检测结果
    uint16_t heart_rate = calculate_heart_rate(&result);
    display_heart_rate(heart_rate);
    
    destroy_pipeline(pipeline);
}
```


### 设计模式选择指南

| 问题场景 | 推荐模式 | 原因 |
|---------|---------|------|
| 需要创建不同类型的对象 | 工厂模式 | 集中管理对象创建逻辑 |
| 需要全局唯一实例 | 单例模式 | 确保资源唯一性 |
| 需要统一不同接口 | 适配器模式 | 兼容不同实现 |
| 需要动态添加功能 | 装饰器模式 | 不修改原有代码 |
| 需要事件通知机制 | 观察者模式 | 解耦事件源和处理者 |
| 需要状态机 | 状态模式 | 清晰的状态转换 |
| 需要可替换的算法 | 策略模式 | 算法独立变化 |
| 需要操作队列/撤销 | 命令模式 | 操作对象化 |
| 需要数据处理流程 | 管道-过滤器模式 | 模块化处理步骤 |

### 最佳实践

#### 1. 适度使用设计模式

```c
// ❌ 过度设计：简单功能使用复杂模式
typedef struct {
    int (*add)(int a, int b);
} AddStrategy;

typedef struct {
    AddStrategy* strategy;
} Calculator;

int calculator_add(Calculator* calc, int a, int b) {
    return calc->strategy->add(a, b);
}

// ✅ 简单直接
int add(int a, int b) {
    return a + b;
}
```

#### 2. 保持接口简单

```c
// ✅ 好的接口设计
typedef struct {
    int (*init)(void);
    int (*read)(void* data, size_t size);
    int (*deinit)(void);
} Sensor;

// ❌ 过于复杂的接口
typedef struct {
    int (*init)(void);
    int (*configure)(const Config* config);
    int (*calibrate)(const CalibrationData* data);
    int (*self_test)(void);
    int (*read)(void* data, size_t size);
    int (*read_async)(void* data, size_t size, Callback callback);
    int (*get_status)(Status* status);
    int (*reset)(void);
    int (*deinit)(void);
} ComplexSensor;  // 接口过于复杂
```

#### 3. 文档化设计决策

```c
/**
 * @pattern: Factory Pattern
 * @rationale: 支持多种传感器类型，集中管理创建逻辑
 * @alternatives_considered: 
 *   - 直接创建：不够灵活，难以扩展
 *   - 抽象工厂：过于复杂，当前不需要
 * @tradeoffs:
 *   - 优点：易于添加新传感器类型
 *   - 缺点：增加一层间接性
 */
Sensor* sensor_factory_create(SensorType type);
```

#### 4. 考虑性能影响

```c
// 在嵌入式系统中，注意设计模式的性能开销

// ❌ 频繁的动态内存分配
void process_samples(void) {
    for (int i = 0; i < 1000; i++) {
        Command* cmd = create_command();  // 每次循环都分配内存
        cmd->execute(cmd);
        free(cmd);
    }
}

// ✅ 使用对象池
typedef struct {
    Command commands[MAX_COMMANDS];
    bool in_use[MAX_COMMANDS];
} CommandPool;

Command* command_pool_acquire(CommandPool* pool) {
    for (size_t i = 0; i < MAX_COMMANDS; i++) {
        if (!pool->in_use[i]) {
            pool->in_use[i] = true;
            return &pool->commands[i];
        }
    }
    return NULL;
}

void command_pool_release(CommandPool* pool, Command* cmd) {
    size_t index = cmd - pool->commands;
    if (index < MAX_COMMANDS) {
        pool->in_use[index] = false;
    }
}
```

### 常见陷阱

#### 1. 过度使用设计模式

**问题**：为了使用模式而使用模式，增加不必要的复杂度。

```c
// ❌ 不必要的抽象
typedef struct {
    int (*get_value)(void);
} ValueGetter;

int simple_value_getter(void) {
    return 42;
}

ValueGetter getter = { .get_value = simple_value_getter };

// ✅ 直接实现
int get_value(void) {
    return 42;
}
```

#### 2. 忽略内存管理

**问题**：设计模式涉及动态对象创建，但忘记释放内存。

```c
// ❌ 内存泄漏
void bad_example(void) {
    Sensor* sensor = sensor_factory_create(SENSOR_TEMPERATURE);
    sensor->init();
    sensor->read(&data, sizeof(data));
    // 忘记释放！
}

// ✅ 正确的资源管理
void good_example(void) {
    Sensor* sensor = sensor_factory_create(SENSOR_TEMPERATURE);
    if (sensor == NULL) {
        return;
    }
    
    sensor->init();
    sensor->read(&data, sizeof(data));
    sensor->deinit();
    
    sensor_factory_destroy(sensor);  // 释放资源
}
```

#### 3. 违反SOLID原则

**问题**：实现设计模式时违反了基本的设计原则。

```c
// ❌ 违反单一职责原则
typedef struct {
    int (*process)(void);
    int (*save)(void);
    int (*display)(void);
    int (*send)(void);
} BadCommand;  // 一个命令做太多事情

// ✅ 遵循单一职责
typedef struct {
    int (*execute)(void);
} Command;

// 每个具体命令只做一件事
typedef struct {
    Command base;
    // 处理相关的数据
} ProcessCommand;

typedef struct {
    Command base;
    // 保存相关的数据
} SaveCommand;
```

#### 4. 忽略线程安全

**问题**：在多线程环境中使用设计模式时忽略同步。

```c
// ❌ 非线程安全的单例
static ConfigManager* g_instance = NULL;

ConfigManager* config_manager_get_instance(void) {
    if (g_instance == NULL) {
        g_instance = malloc(sizeof(ConfigManager));
        // 竞态条件！
    }
    return g_instance;
}

// ✅ 线程安全的单例
static ConfigManager* g_instance = NULL;
static SemaphoreHandle_t g_mutex = NULL;

ConfigManager* config_manager_get_instance(void) {
    if (g_instance == NULL) {
        if (g_mutex == NULL) {
            g_mutex = xSemaphoreCreateMutex();
        }
        
        xSemaphoreTake(g_mutex, portMAX_DELAY);
        
        if (g_instance == NULL) {  // 双重检查
            g_instance = malloc(sizeof(ConfigManager));
            config_manager_init(g_instance);
        }
        
        xSemaphoreGive(g_mutex);
    }
    return g_instance;
}
```

### 实践练习

#### 练习1：实现工厂模式

**任务**：为多参数监护仪实现传感器工厂。

**要求**：
- 支持至少3种传感器类型（ECG、SpO2、体温）
- 统一的传感器接口
- 集中的创建和销毁逻辑
- 错误处理

#### 练习2：实现观察者模式

**任务**：实现一个报警系统，当生命体征超出阈值时通知多个观察者。

**要求**：
- 支持动态注册/注销观察者
- 至少3个观察者（显示、日志、声音报警）
- 线程安全（如果使用RTOS）

#### 练习3：实现状态模式

**任务**：为输液泵实现状态机。

**状态**：
- 空闲
- 准备（装载药液）
- 运行
- 暂停
- 完成
- 错误

**要求**：
- 清晰的状态转换逻辑
- 每个状态的进入/退出动作
- 事件处理

#### 练习4：实现管道-过滤器模式

**任务**：实现血糖仪的数据处理管道。

**过滤器**：
1. 原始数据采集
2. 温度补偿
3. 校准
4. 单位转换（mg/dL ↔ mmol/L）
5. 质量控制检查

**要求**：
- 可配置的过滤器链
- 每个过滤器独立测试
- 错误传播机制

## 自测问题

### 问题1：设计模式分类

**问题**：列举三大类设计模式，并各举一个医疗器械应用的例子。

<details>
<summary>点击查看答案</summary>

**答案**：

1. **创建型模式（Creational Patterns）**：
   - 关注对象创建机制
   - 医疗器械例子：工厂模式创建不同类型的传感器（ECG、SpO2、血压）
   - 优势：集中管理对象创建，易于扩展新类型

2. **结构型模式（Structural Patterns）**：
   - 关注对象组合和关系
   - 医疗器械例子：适配器模式统一不同通信接口（UART、SPI、I2C）
   - 优势：提供统一接口，隐藏底层差异

3. **行为型模式（Behavioral Patterns）**：
   - 关注对象间的通信和职责分配
   - 医疗器械例子：观察者模式实现报警系统（心率异常时通知显示、日志、声音报警）
   - 优势：解耦事件源和处理者，易于添加新的观察者

</details>

### 问题2：模式选择

**问题**：在以下场景中，应该使用哪种设计模式？为什么？

场景：需要实现一个血压计，测量过程包括多个状态（空闲、充气、测量、放气、显示结果），每个状态有不同的行为。

<details>
<summary>点击查看答案</summary>

**答案**：

**推荐使用：状态模式（State Pattern）**

**理由**：
1. **清晰的状态转换**：血压计有明确的状态序列，状态模式可以清晰地表达状态转换逻辑
2. **状态特定行为**：每个状态有不同的行为（充气时启动泵，测量时读取压力传感器等）
3. **易于维护**：添加新状态或修改状态行为不影响其他状态
4. **符合IEC 62304**：状态机是医疗器械软件设计的常见要求，便于文档化和验证

**实现要点**：
```c
// 定义状态接口
typedef struct State {
    void (*enter)(Context* ctx);
    void (*exit)(Context* ctx);
    void (*handle_event)(Context* ctx, Event event);
} State;

// 定义各个状态
State idle_state;
State inflating_state;
State measuring_state;
State deflating_state;
State result_state;

// 状态转换
void context_change_state(Context* ctx, State* new_state);
```

**替代方案**：
- 简单的switch-case状态机：适用于状态较少、逻辑简单的情况
- 状态模式的优势在于：更好的封装、更易扩展、更符合开闭原则

</details>

### 问题3：模式组合

**问题**：如何组合使用工厂模式和策略模式来实现可配置的信号处理系统？

<details>
<summary>点击查看答案</summary>

**答案**：

**组合方案**：

1. **使用工厂模式创建策略对象**：
```c
// 策略接口
typedef struct {
    int (*process)(const void* input, void* output, size_t size);
} FilterStrategy;

// 工厂创建不同的策略
FilterStrategy* filter_factory_create(FilterType type) {
    switch (type) {
        case FILTER_MOVING_AVERAGE:
            return create_moving_average_strategy();
        case FILTER_MEDIAN:
            return create_median_strategy();
        case FILTER_KALMAN:
            return create_kalman_strategy();
        default:
            return NULL;
    }
}
```

2. **使用策略模式实现可替换的算法**：
```c
// 信号处理器使用策略
typedef struct {
    FilterStrategy* strategy;
} SignalProcessor;

void signal_processor_set_strategy(SignalProcessor* processor, 
                                  FilterStrategy* strategy) {
    processor->strategy = strategy;
}

int signal_processor_process(SignalProcessor* processor,
                            const void* input, void* output, size_t size) {
    return processor->strategy->process(input, output, size);
}
```

3. **运行时配置**：
```c
void configure_signal_processing(void) {
    SignalProcessor processor;
    
    // 从配置读取滤波器类型
    FilterType type = config_get_filter_type();
    
    // 使用工厂创建策略
    FilterStrategy* strategy = filter_factory_create(type);
    
    // 设置策略
    signal_processor_set_strategy(&processor, strategy);
    
    // 使用处理器
    signal_processor_process(&processor, input, output, size);
}
```

**优势**：
- 工厂模式：集中管理策略对象的创建
- 策略模式：运行时可以切换不同的算法
- 组合使用：既有创建的灵活性，又有行为的可替换性

</details>

### 问题4：性能考虑

**问题**：在嵌入式医疗器械中使用设计模式时，需要注意哪些性能问题？

<details>
<summary>点击查看答案</summary>

**答案**：

**主要性能考虑**：

1. **内存开销**：
   - 问题：设计模式通常涉及额外的结构体和指针
   - 解决：使用静态分配而非动态分配
   ```c
   // ❌ 动态分配
   Sensor* sensor = malloc(sizeof(Sensor));
   
   // ✅ 静态分配
   static Sensor sensors[MAX_SENSORS];
   ```

2. **函数调用开销**：
   - 问题：通过函数指针调用增加间接性
   - 解决：在性能关键路径考虑内联或直接调用
   ```c
   // 性能关键：直接调用
   int result = fast_process(data);
   
   // 非关键路径：使用模式
   int result = strategy->process(strategy, data);
   ```

3. **缓存效率**：
   - 问题：过多的间接引用影响缓存命中率
   - 解决：保持数据结构紧凑，相关数据放在一起

4. **实时性要求**：
   - 问题：某些模式（如观察者）可能导致不确定的执行时间
   - 解决：限制观察者数量，使用优先级队列

5. **栈使用**：
   - 问题：递归或深层调用链消耗栈空间
   - 解决：避免递归，限制调用深度

**最佳实践**：
- 在性能关键代码中谨慎使用设计模式
- 使用性能分析工具测量实际开销
- 在可维护性和性能之间找到平衡
- 文档化性能相关的设计决策

</details>

### 问题5：IEC 62304合规性

**问题**：设计模式如何支持IEC 62304合规性？举例说明。

<details>
<summary>点击查看答案</summary>

**答案**：

**设计模式支持IEC 62304的方式**：

1. **可追溯性**：
   - 模式提供清晰的结构，便于建立需求到实现的追溯
   ```c
   /**
    * @pattern: Observer Pattern
    * @requirement: REQ-ALARM-001 "系统应在参数超限时触发报警"
    * @safety_class: Class B
    */
   void alarm_observer_callback(void* context, const void* subject, const void* data);
   ```

2. **模块化**：
   - 模式促进模块化设计，符合IEC 62304对软件架构的要求
   - 每个模式实现可以作为独立的软件单元进行验证

3. **风险管理**：
   - 使用状态模式可以清晰地识别和管理状态转换风险
   - 使用命令模式可以记录所有操作，支持审计追踪

4. **变更管理**：
   - 设计模式限制变更影响范围
   - 例如：添加新的传感器类型只需修改工厂，不影响其他代码

5. **验证和确认**：
   - 模式提供清晰的接口，便于编写测试用例
   ```c
   // 测试工厂模式
   void test_sensor_factory(void) {
       Sensor* sensor = sensor_factory_create(SENSOR_TEMPERATURE);
       assert(sensor != NULL);
       assert(sensor->init() == 0);
       // 验证接口行为
   }
   ```

6. **文档化**：
   - 使用标准模式名称提供共同语言
   - 便于设计文档和代码审查

**示例：使用状态模式支持风险分析**：
```c
/**
 * @state_machine: Infusion Pump
 * @hazard: 过量输液
 * @risk_control: 状态转换验证
 * 
 * 风险控制措施：
 * 1. 只允许从"准备"状态转换到"运行"状态
 * 2. 运行前必须验证剂量设置
 * 3. 异常情况自动转换到"错误"状态
 */
void running_state_enter(Context* ctx) {
    // 验证剂量设置（风险控制）
    if (!validate_dose_settings(ctx)) {
        context_change_state(ctx, &error_state);
        return;
    }
    
    start_infusion();
}
```

</details>

## 相关资源

- [软件架构设计](../index.md)
- [模块化设计](../modular-design.md)
- [分层架构设计](../layered-architecture.md)
- [接口设计](../interface-design.md)

## 参考文献

1. Gamma, E., Helm, R., Johnson, R., & Vlissides, J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley.
2. Martin, R. C. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. Prentice Hall.
3. Buschmann, F., Meunier, R., Rohnert, H., Sommerlad, P., & Stal, M. (1996). *Pattern-Oriented Software Architecture, Volume 1: A System of Patterns*. Wiley.
4. IEC 62304:2006+AMD1:2015. *Medical device software – Software life cycle processes*.
5. Douglass, B. P. (2002). *Real-Time Design Patterns: Robust Scalable Architecture for Real-Time Systems*. Addison-Wesley.
6. Hanmer, R. (2007). *Patterns for Fault Tolerant Software*. Wiley.

---

**最后更新**: 2026-02-09  
**版本**: 1.0  
**作者**: 医疗器械软件工程团队
