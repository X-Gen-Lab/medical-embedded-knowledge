---
title: 健康数据集成
description: "实现移动健康应用与医疗设备和系统的数据集成"
difficulty: 中级
estimated_time: 2-3小时
last_updated: "2026-02-11"
version: "1.0"
language: "zh-CN"
tags:
  - data-integration
  - health-data
  - apis
  - mhealth
---

# 健康数据集成

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

健康数据集成是移动医疗应用的核心功能，涉及从多个来源收集、标准化和同步健康数据。本指南介绍主要的健康数据平台、集成方法和最佳实践。

## 主要健康数据平台

### 1. Apple HealthKit（iOS）

#### 数据类型
- **生命体征**: 心率、血压、体温、血氧
- **身体测量**: 体重、身高、BMI、体脂率
- **活动数据**: 步数、距离、爬楼层数、活动能量
- **营养数据**: 卡路里、蛋白质、碳水化合物
- **睡眠分析**: 睡眠时长、睡眠阶段
- **生殖健康**: 月经周期、排卵期

#### 集成示例

```swift
import HealthKit

class HealthKitIntegration {
    let healthStore = HKHealthStore()
    
    // 请求权限
    func requestAuthorization() async throws {
        let readTypes: Set<HKObjectType> = [
            HKObjectType.quantityType(forIdentifier: .heartRate)!,
            HKObjectType.quantityType(forIdentifier: .stepCount)!,
            HKObjectType.quantityType(forIdentifier: .bloodPressureSystolic)!,
            HKObjectType.quantityType(forIdentifier: .bloodGlucose)!,
            HKObjectType.categoryType(forIdentifier: .sleepAnalysis)!
        ]
        
        let writeTypes: Set<HKSampleType> = [
            HKObjectType.quantityType(forIdentifier: .bodyMass)!,
            HKObjectType.quantityType(forIdentifier: .dietaryEnergyConsumed)!
        ]
        
        try await healthStore.requestAuthorization(toShare: writeTypes, read: readTypes)
    }
    
    // 读取最近7天的步数
    func fetchWeeklySteps() async throws -> [(Date, Double)] {
        guard let stepsType = HKQuantityType.quantityType(forIdentifier: .stepCount) else {
            throw HealthKitError.invalidType
        }
        
        let calendar = Calendar.current
        let endDate = Date()
        let startDate = calendar.date(byAdding: .day, value: -7, to: endDate)!
        
        let predicate = HKQuery.predicateForSamples(withStart: startDate, end: endDate, options: .strictStartDate)
        
        var interval = DateComponents()
        interval.day = 1
        
        return try await withCheckedThrowingContinuation { continuation in
            let query = HKStatisticsCollectionQuery(
                quantityType: stepsType,
                quantitySamplePredicate: predicate,
                options: .cumulativeSum,
                anchorDate: startDate,
                intervalComponents: interval
            )
            
            query.initialResultsHandler = { query, results, error in
                if let error = error {
                    continuation.resume(throwing: error)
                    return
                }
                
                var data: [(Date, Double)] = []
                results?.enumerateStatistics(from: startDate, to: endDate) { statistics, stop in
                    if let sum = statistics.sumQuantity() {
                        let steps = sum.doubleValue(for: HKUnit.count())
                        data.append((statistics.startDate, steps))
                    }
                }
                
                continuation.resume(returning: data)
            }
            
            healthStore.execute(query)
        }
    }
    
    // 写入体重数据
    func saveWeight(_ weight: Double, date: Date = Date()) async throws {
        guard let weightType = HKQuantityType.quantityType(forIdentifier: .bodyMass) else {
            throw HealthKitError.invalidType
        }
        
        let weightQuantity = HKQuantity(unit: .gramUnit(with: .kilo), doubleValue: weight)
        let weightSample = HKQuantitySample(
            type: weightType,
            quantity: weightQuantity,
            start: date,
            end: date
        )
        
        try await healthStore.save(weightSample)
    }
    
    // 实时监听心率变化
    func observeHeartRate(handler: @escaping (Double) -> Void) {
        guard let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate) else {
            return
        }
        
        let query = HKObserverQuery(sampleType: heartRateType, predicate: nil) { query, completionHandler, error in
            if error != nil {
                completionHandler()
                return
            }
            
            // 获取最新心率数据
            let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)
            let sampleQuery = HKSampleQuery(
                sampleType: heartRateType,
                predicate: nil,
                limit: 1,
                sortDescriptors: [sortDescriptor]
            ) { _, samples, _ in
                if let sample = samples?.first as? HKQuantitySample {
                    let heartRate = sample.quantity.doubleValue(for: HKUnit.count().unitDivided(by: .minute()))
                    handler(heartRate)
                }
                completionHandler()
            }
            
            self.healthStore.execute(sampleQuery)
        }
        
        healthStore.execute(query)
    }
}
```

### 2. Health Connect（Android）

#### 数据类型
- **活动记录**: 步数、距离、卡路里、运动会话
- **身体测量**: 体重、身高、体脂率
- **生命体征**: 心率、血压、血氧、体温
- **营养**: 水分摄入、营养素
- **睡眠**: 睡眠会话、睡眠阶段
- **周期追踪**: 月经周期

#### 集成示例

```kotlin
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.*
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import java.time.Instant
import java.time.ZonedDateTime
import java.time.temporal.ChronoUnit

class HealthConnectIntegration(private val context: Context) {
    private val healthConnectClient by lazy {
        HealthConnectClient.getOrCreate(context)
    }
    
    // 检查可用性
    suspend fun isAvailable(): Boolean {
        return HealthConnectClient.isAvailable(context)
    }
    
    // 请求权限
    suspend fun requestPermissions(activity: Activity) {
        val permissions = setOf(
            HealthPermission.READ_HEART_RATE,
            HealthPermission.READ_STEPS,
            HealthPermission.READ_BLOOD_PRESSURE,
            HealthPermission.READ_BLOOD_GLUCOSE,
            HealthPermission.READ_SLEEP,
            HealthPermission.WRITE_WEIGHT,
            HealthPermission.WRITE_NUTRITION
        )
        
        healthConnectClient.permissionController.requestPermissions(activity, permissions)
    }
    
    // 读取每日步数
    suspend fun readDailySteps(date: ZonedDateTime): Long {
        val startOfDay = date.truncatedTo(ChronoUnit.DAYS)
        val endOfDay = startOfDay.plusDays(1)
        
        val request = ReadRecordsRequest(
            recordType = StepsRecord::class,
            timeRangeFilter = TimeRangeFilter.between(
                startOfDay.toInstant(),
                endOfDay.toInstant()
            )
        )
        
        val response = healthConnectClient.readRecords(request)
        return response.records.sumOf { it.count }
    }
    
    // 读取心率数据
    suspend fun readHeartRateData(
        startTime: Instant,
        endTime: Instant
    ): List<HeartRateData> {
        val request = ReadRecordsRequest(
            recordType = HeartRateRecord::class,
            timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
        )
        
        val response = healthConnectClient.readRecords(request)
        return response.records.map { record ->
            HeartRateData(
                timestamp = record.time,
                bpm = record.samples.firstOrNull()?.beatsPerMinute ?: 0
            )
        }
    }
    
    // 写入体重
    suspend fun writeWeight(weight: Double, time: ZonedDateTime) {
        val weightRecord = WeightRecord(
            weight = Mass.kilograms(weight),
            time = time.toInstant(),
            zoneOffset = time.offset
        )
        
        healthConnectClient.insertRecords(listOf(weightRecord))
    }
    
    // 写入营养数据
    suspend fun writeNutrition(
        calories: Double,
        protein: Double,
        carbs: Double,
        fat: Double,
        time: ZonedDateTime
    ) {
        val nutritionRecord = NutritionRecord(
            energy = Energy.kilocalories(calories),
            protein = Mass.grams(protein),
            totalCarbohydrate = Mass.grams(carbs),
            totalFat = Mass.grams(fat),
            startTime = time.toInstant(),
            endTime = time.toInstant(),
            startZoneOffset = time.offset,
            endZoneOffset = time.offset
        )
        
        healthConnectClient.insertRecords(listOf(nutritionRecord))
    }
    
    // 读取睡眠数据
    suspend fun readSleepData(date: ZonedDateTime): List<SleepSessionRecord> {
        val startOfDay = date.truncatedTo(ChronoUnit.DAYS).minusHours(12)
        val endOfDay = startOfDay.plusDays(1)
        
        val request = ReadRecordsRequest(
            recordType = SleepSessionRecord::class,
            timeRangeFilter = TimeRangeFilter.between(
                startOfDay.toInstant(),
                endOfDay.toInstant()
            )
        )
        
        val response = healthConnectClient.readRecords(request)
        return response.records
    }
}

data class HeartRateData(
    val timestamp: Instant,
    val bpm: Long
)
```

### 3. 可穿戴设备集成

#### Apple Watch

```swift
import WatchConnectivity

class WatchConnectivityManager: NSObject, WCSessionDelegate {
    static let shared = WatchConnectivityManager()
    private var session: WCSession?
    
    func setupSession() {
        if WCSession.isSupported() {
            session = WCSession.default
            session?.delegate = self
            session?.activate()
        }
    }
    
    // 发送数据到Apple Watch
    func sendHealthData(_ data: [String: Any]) {
        guard let session = session, session.isReachable else {
            return
        }
        
        session.sendMessage(data, replyHandler: nil) { error in
            print("发送失败: \(error)")
        }
    }
    
    // 接收来自Apple Watch的数据
    func session(_ session: WCSession, didReceiveMessage message: [String : Any]) {
        if let heartRate = message["heartRate"] as? Double {
            // 处理心率数据
            handleHeartRate(heartRate)
        }
    }
    
    func session(_ session: WCSession, activationDidCompleteWith activationState: WCSessionActivationState, error: Error?) {
        // 处理激活完成
    }
    
    func sessionDidBecomeInactive(_ session: WCSession) {}
    func sessionDidDeactivate(_ session: WCSession) {}
    
    private func handleHeartRate(_ heartRate: Double) {
        // 保存到HealthKit或本地数据库
    }
}
```

#### Wear OS

```kotlin
import com.google.android.gms.wearable.*

class WearableDataManager(private val context: Context) : DataClient.OnDataChangedListener {
    private val dataClient: DataClient by lazy {
        Wearable.getDataClient(context)
    }
    
    fun startListening() {
        dataClient.addListener(this)
    }
    
    fun stopListening() {
        dataClient.removeListener(this)
    }
    
    // 发送数据到手表
    fun sendHealthData(heartRate: Int, steps: Int) {
        val putDataReq = PutDataMapRequest.create("/health_data").apply {
            dataMap.putInt("heart_rate", heartRate)
            dataMap.putInt("steps", steps)
            dataMap.putLong("timestamp", System.currentTimeMillis())
        }.asPutDataRequest()
        
        dataClient.putDataItem(putDataReq)
    }
    
    // 接收来自手表的数据
    override fun onDataChanged(dataEvents: DataEventBuffer) {
        dataEvents.forEach { event ->
            if (event.type == DataEvent.TYPE_CHANGED) {
                val dataItem = event.dataItem
                if (dataItem.uri.path == "/health_data") {
                    val dataMap = DataMapItem.fromDataItem(dataItem).dataMap
                    val heartRate = dataMap.getInt("heart_rate")
                    val steps = dataMap.getInt("steps")
                    
                    // 处理数据
                    handleHealthData(heartRate, steps)
                }
            }
        }
    }
    
    private fun handleHealthData(heartRate: Int, steps: Int) {
        // 保存到Health Connect或本地数据库
    }
}
```

## 数据标准化

### FHIR（Fast Healthcare Interoperability Resources）

```kotlin
// FHIR Observation资源示例
data class FHIRObservation(
    val resourceType: String = "Observation",
    val id: String,
    val status: String,
    val category: List<CodeableConcept>,
    val code: CodeableConcept,
    val subject: Reference,
    val effectiveDateTime: String,
    val valueQuantity: Quantity?
)

data class CodeableConcept(
    val coding: List<Coding>,
    val text: String?
)

data class Coding(
    val system: String,
    val code: String,
    val display: String
)

data class Reference(
    val reference: String,
    val display: String?
)

data class Quantity(
    val value: Double,
    val unit: String,
    val system: String,
    val code: String
)

// 转换HealthKit数据到FHIR
class FHIRConverter {
    fun convertHeartRateToFHIR(heartRate: Double, patientId: String, date: Date): FHIRObservation {
        return FHIRObservation(
            id = UUID.randomUUID().toString(),
            status = "final",
            category = listOf(
                CodeableConcept(
                    coding = listOf(
                        Coding(
                            system = "http://terminology.hl7.org/CodeSystem/observation-category",
                            code = "vital-signs",
                            display = "Vital Signs"
                        )
                    ),
                    text = "Vital Signs"
                )
            ),
            code = CodeableConcept(
                coding = listOf(
                    Coding(
                        system = "http://loinc.org",
                        code = "8867-4",
                        display = "Heart rate"
                    )
                ),
                text = "Heart rate"
            ),
            subject = Reference(
                reference = "Patient/$patientId",
                display = null
            ),
            effectiveDateTime = ISO8601DateFormatter().string(from: date),
            valueQuantity = Quantity(
                value = heartRate,
                unit = "beats/minute",
                system = "http://unitsofmeasure.org",
                code = "/min"
            )
        )
    }
}
```

## 数据同步策略

### 1. 增量同步

```swift
class DataSyncManager {
    private let lastSyncKey = "lastSyncTimestamp"
    
    func syncHealthData() async throws {
        let lastSync = UserDefaults.standard.object(forKey: lastSyncKey) as? Date ?? Date.distantPast
        let now = Date()
        
        // 获取自上次同步以来的新数据
        let newData = try await fetchHealthDataSince(lastSync)
        
        // 上传到服务器
        try await uploadToServer(newData)
        
        // 更新最后同步时间
        UserDefaults.standard.set(now, forKey: lastSyncKey)
    }
    
    private func fetchHealthDataSince(_ date: Date) async throws -> [HealthData] {
        // 从HealthKit获取数据
        return []
    }
    
    private func uploadToServer(_ data: [HealthData]) async throws {
        // 上传数据
    }
}
```

### 2. 冲突解决

```kotlin
class ConflictResolver {
    enum class ResolutionStrategy {
        SERVER_WINS,      // 服务器数据优先
        CLIENT_WINS,      // 客户端数据优先
        LATEST_WINS,      // 最新数据优先
        MERGE             // 合并数据
    }
    
    fun resolveConflict(
        serverData: HealthRecord,
        clientData: HealthRecord,
        strategy: ResolutionStrategy
    ): HealthRecord {
        return when (strategy) {
            ResolutionStrategy.SERVER_WINS -> serverData
            ResolutionStrategy.CLIENT_WINS -> clientData
            ResolutionStrategy.LATEST_WINS -> {
                if (serverData.timestamp > clientData.timestamp) serverData else clientData
            }
            ResolutionStrategy.MERGE -> {
                mergeRecords(serverData, clientData)
            }
        }
    }
    
    private fun mergeRecords(server: HealthRecord, client: HealthRecord): HealthRecord {
        // 合并逻辑
        return server.copy(
            value = (server.value + client.value) / 2,
            timestamp = maxOf(server.timestamp, client.timestamp)
        )
    }
}
```

## 数据验证

### 数据质量检查

```swift
class DataValidator {
    // 验证心率数据
    func validateHeartRate(_ heartRate: Double) -> ValidationResult {
        switch heartRate {
        case 0:
            return .invalid("心率不能为0")
        case 1..<30:
            return .warning("心率异常低")
        case 30..<220:
            return .valid
        case 220...:
            return .warning("心率异常高")
        default:
            return .invalid("无效的心率值")
        }
    }
    
    // 验证血压数据
    func validateBloodPressure(systolic: Int, diastolic: Int) -> ValidationResult {
        guard systolic > diastolic else {
            return .invalid("收缩压必须大于舒张压")
        }
        
        if systolic < 70 || systolic > 250 {
            return .warning("收缩压超出正常范围")
        }
        
        if diastolic < 40 || diastolic > 150 {
            return .warning("舒张压超出正常范围")
        }
        
        return .valid
    }
}

enum ValidationResult {
    case valid
    case warning(String)
    case invalid(String)
}
```

## 最佳实践

### 1. 权限管理
- 仅请求必需的权限
- 提供清晰的权限说明
- 支持部分权限授予
- 定期检查权限状态

### 2. 数据隐私
- 最小化数据收集
- 本地处理优先
- 匿名化敏感数据
- 提供数据导出和删除功能

### 3. 性能优化
- 批量读写数据
- 使用后台任务同步
- 实施数据缓存策略
- 限制查询频率

### 4. 错误处理
- 优雅处理权限拒绝
- 网络错误重试机制
- 数据验证失败提示
- 同步冲突解决

## 相关资源

- [HealthKit文档](https://developer.apple.com/documentation/healthkit)
- [Health Connect文档](https://developer.android.com/health-and-fitness/guides/health-connect)
- [FHIR规范](https://www.hl7.org/fhir/)
- [IEEE 11073标准](https://standards.ieee.org/standard/11073-10101-2019.html)

## 下一步

- [iOS医疗应用开发](ios-development.md)
- [Android医疗应用开发](android-development.md)
- [移动应用安全](mobile-security.md)

---

*最后更新: 2024年*
