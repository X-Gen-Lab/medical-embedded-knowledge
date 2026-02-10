---
title: iOS医疗应用开发
difficulty: intermediate
estimated_time: 2-3小时
---

# iOS医疗应用开发

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

iOS平台因其严格的安全标准、统一的硬件生态和高质量的用户体验，成为医疗应用开发的首选平台之一。本指南涵盖iOS医疗应用开发的关键技术、最佳实践和监管要求。

## 开发环境设置

### 必需工具
- **Xcode**: Apple官方IDE（最新稳定版本）
- **macOS**: 运行Xcode的必需操作系统
- **Apple Developer Account**: 用于真机测试和应用发布
- **CocoaPods/Swift Package Manager**: 依赖管理工具

### 推荐工具
- **Instruments**: 性能分析工具
- **TestFlight**: Beta测试平台
- **Fastlane**: 自动化部署工具
- **SwiftLint**: 代码规范检查

## 编程语言选择

### Swift（推荐）
```swift
// 现代、安全、高性能
import UIKit
import HealthKit

class HealthDataManager {
    let healthStore = HKHealthStore()
    
    func requestAuthorization() async throws {
        let types: Set<HKSampleType> = [
            HKObjectType.quantityType(forIdentifier: .heartRate)!,
            HKObjectType.quantityType(forIdentifier: .bloodPressureSystolic)!
        ]
        
        try await healthStore.requestAuthorization(toShare: [], read: types)
    }
}
```

**优势**:
- 类型安全，减少运行时错误
- 现代语法，提高开发效率
- Apple官方支持，持续更新
- 优秀的性能表现

### Objective-C（遗留项目）
```objective-c
// 用于维护旧代码或与旧库集成
@interface HealthDataManager : NSObject
@property (nonatomic, strong) HKHealthStore *healthStore;
- (void)requestAuthorizationWithCompletion:(void(^)(BOOL success, NSError *error))completion;
@end
```

## 核心框架

### 1. HealthKit

HealthKit是Apple提供的健康数据框架，允许应用读取和写入健康数据。

#### 配置HealthKit
```swift
// 1. 在Xcode中启用HealthKit capability
// 2. 在Info.plist中添加隐私说明
```


```xml
<!-- Info.plist -->
<key>NSHealthShareUsageDescription</key>
<string>我们需要访问您的健康数据以提供个性化健康建议</string>
<key>NSHealthUpdateUsageDescription</key>
<string>我们需要更新您的健康数据以记录您的健康活动</string>
```

#### 读取健康数据
```swift
import HealthKit

class HealthKitManager {
    let healthStore = HKHealthStore()
    
    // 检查HealthKit可用性
    func isHealthKitAvailable() -> Bool {
        return HKHealthStore.isHealthDataAvailable()
    }
    
    // 请求授权
    func requestAuthorization() async throws {
        guard isHealthKitAvailable() else {
            throw HealthKitError.notAvailable
        }
        
        let readTypes: Set<HKObjectType> = [
            HKObjectType.quantityType(forIdentifier: .heartRate)!,
            HKObjectType.quantityType(forIdentifier: .stepCount)!,
            HKObjectType.quantityType(forIdentifier: .bloodGlucose)!,
            HKObjectType.categoryType(forIdentifier: .sleepAnalysis)!
        ]
        
        let writeTypes: Set<HKSampleType> = [
            HKObjectType.quantityType(forIdentifier: .bodyMass)!,
            HKObjectType.quantityType(forIdentifier: .bloodPressureSystolic)!
        ]
        
        try await healthStore.requestAuthorization(toShare: writeTypes, read: readTypes)
    }
    
    // 查询心率数据
    func fetchHeartRateData(completion: @escaping ([HKQuantitySample]?, Error?) -> Void) {
        guard let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate) else {
            completion(nil, HealthKitError.invalidType)
            return
        }
        
        let sortDescriptor = NSSortDescriptor(key: HKSampleSortIdentifierStartDate, ascending: false)
        let query = HKSampleQuery(sampleType: heartRateType,
                                   predicate: nil,
                                   limit: 100,
                                   sortDescriptors: [sortDescriptor]) { query, samples, error in
            guard let samples = samples as? [HKQuantitySample] else {
                completion(nil, error)
                return
            }
            completion(samples, nil)
        }
        
        healthStore.execute(query)
    }
    
    // 写入体重数据
    func saveWeight(_ weight: Double, date: Date = Date()) async throws {
        guard let weightType = HKQuantityType.quantityType(forIdentifier: .bodyMass) else {
            throw HealthKitError.invalidType
        }
        
        let weightQuantity = HKQuantity(unit: .gramUnit(with: .kilo), doubleValue: weight)
        let weightSample = HKQuantitySample(type: weightType,
                                            quantity: weightQuantity,
                                            start: date,
                                            end: date)
        
        try await healthStore.save(weightSample)
    }
    
    // 观察实时数据变化
    func observeHeartRate(handler: @escaping (HKQuantitySample) -> Void) {
        guard let heartRateType = HKQuantityType.quantityType(forIdentifier: .heartRate) else {
            return
        }
        
        let query = HKObserverQuery(sampleType: heartRateType, predicate: nil) { query, completionHandler, error in
            if error != nil {
                completionHandler()
                return
            }
            
            // 获取最新数据
            self.fetchHeartRateData { samples, error in
                if let latestSample = samples?.first {
                    handler(latestSample)
                }
                completionHandler()
            }
        }
        
        healthStore.execute(query)
    }
}

enum HealthKitError: Error {
    case notAvailable
    case invalidType
    case authorizationDenied
}
```

### 2. CareKit

CareKit是用于构建护理管理应用的开源框架。

```swift
import CareKit
import CareKitStore

class CareKitManager {
    let storeManager = OCKSynchronizedStoreManager(
        wrapping: OCKStore(name: "carekit-store", type: .onDisk)
    )
    
    // 创建护理计划
    func createCarePlan() async throws {
        let schedule = OCKSchedule.dailyAtTime(
            hour: 8, minutes: 0,
            start: Date(), end: nil,
            text: "每天早上8点"
        )
        
        let task = OCKTask(
            id: "medication",
            title: "服用降压药",
            carePlanUUID: nil,
            schedule: schedule
        )
        
        try await storeManager.store.addTask(task)
    }
    
    // 记录任务完成
    func completeTask(taskID: String) async throws {
        let query = OCKTaskQuery(for: Date())
        let tasks = try await storeManager.store.fetchTasks(query: query)
        
        guard let task = tasks.first(where: { $0.id == taskID }) else {
            throw CareKitError.taskNotFound
        }
        
        let outcome = OCKOutcome(
            taskUUID: task.uuid,
            taskOccurrenceIndex: 0,
            values: [OCKOutcomeValue(true)]
        )
        
        try await storeManager.store.addOutcome(outcome)
    }
}
```

### 3. ResearchKit

ResearchKit用于创建医学研究和临床试验应用。

```swift
import ResearchKit

class SurveyManager {
    // 创建调查问卷
    func createSurvey() -> ORKOrderedTask {
        var steps = [ORKStep]()
        
        // 知情同意
        let consentDocument = ORKConsentDocument()
        consentDocument.title = "研究知情同意书"
        
        let consentStep = ORKConsentReviewStep(
            identifier: "consent",
            signature: nil,
            in: consentDocument
        )
        steps.append(consentStep)
        
        // 问卷题目
        let questionStep = ORKQuestionStep(
            identifier: "pain_level",
            title: "疼痛评分",
            question: "请评估您当前的疼痛程度（0-10分）",
            answer: ORKAnswerFormat.scale(
                withMaximumValue: 10,
                minimumValue: 0,
                defaultValue: 5,
                step: 1,
                vertical: false,
                maximumValueDescription: "极度疼痛",
                minimumValueDescription: "无疼痛"
            )
        )
        steps.append(questionStep)
        
        // 主动任务（如步态测试）
        let walkingStep = ORKOrderedTask.shortWalk(
            withIdentifier: "walking",
            intendedUseDescription: "测试您的步态和平衡能力",
            numberOfStepsPerLeg: 20,
            restDuration: 30,
            options: []
        )
        
        return ORKOrderedTask(identifier: "survey", steps: steps)
    }
}
```

## UI框架

### SwiftUI（现代方法）

```swift
import SwiftUI
import HealthKit

struct HealthDashboardView: View {
    @StateObject private var viewModel = HealthViewModel()
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // 心率卡片
                    HealthMetricCard(
                        title: "心率",
                        value: viewModel.heartRate,
                        unit: "bpm",
                        icon: "heart.fill",
                        color: .red
                    )
                    
                    // 步数卡片
                    HealthMetricCard(
                        title: "步数",
                        value: viewModel.stepCount,
                        unit: "步",
                        icon: "figure.walk",
                        color: .green
                    )
                    
                    // 血糖卡片
                    HealthMetricCard(
                        title: "血糖",
                        value: viewModel.bloodGlucose,
                        unit: "mg/dL",
                        icon: "drop.fill",
                        color: .blue
                    )
                }
                .padding()
            }
            .navigationTitle("健康数据")
            .task {
                await viewModel.loadHealthData()
            }
        }
    }
}

struct HealthMetricCard: View {
    let title: String
    let value: Double?
    let unit: String
    let icon: String
    let color: Color
    
    var body: some View {
        HStack {
            Image(systemName: icon)
                .font(.system(size: 40))
                .foregroundColor(color)
            
            VStack(alignment: .leading) {
                Text(title)
                    .font(.headline)
                if let value = value {
                    Text("\(Int(value)) \(unit)")
                        .font(.title2)
                        .bold()
                } else {
                    Text("无数据")
                        .foregroundColor(.gray)
                }
            }
            
            Spacer()
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}

@MainActor
class HealthViewModel: ObservableObject {
    @Published var heartRate: Double?
    @Published var stepCount: Double?
    @Published var bloodGlucose: Double?
    
    private let healthManager = HealthKitManager()
    
    func loadHealthData() async {
        do {
            try await healthManager.requestAuthorization()
            // 加载各项健康数据
            await loadHeartRate()
            await loadStepCount()
            await loadBloodGlucose()
        } catch {
            print("加载健康数据失败: \(error)")
        }
    }
    
    private func loadHeartRate() async {
        // 实现心率数据加载
    }
    
    private func loadStepCount() async {
        // 实现步数数据加载
    }
    
    private func loadBloodGlucose() async {
        // 实现血糖数据加载
    }
}
```

### UIKit（传统方法）

```swift
import UIKit

class HealthViewController: UIViewController {
    private let tableView = UITableView()
    private var healthData: [HealthMetric] = []
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadHealthData()
    }
    
    private func setupUI() {
        title = "健康数据"
        view.backgroundColor = .systemBackground
        
        tableView.delegate = self
        tableView.dataSource = self
        tableView.register(HealthMetricCell.self, forCellReuseIdentifier: "cell")
        
        view.addSubview(tableView)
        tableView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            tableView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor)
        ])
    }
    
    private func loadHealthData() {
        // 加载健康数据
    }
}

extension HealthViewController: UITableViewDelegate, UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return healthData.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "cell", for: indexPath) as! HealthMetricCell
        cell.configure(with: healthData[indexPath.row])
        return cell
    }
}
```

## 数据持久化

### Core Data

```swift
import CoreData

class PersistenceController {
    static let shared = PersistenceController()
    
    let container: NSPersistentContainer
    
    init() {
        container = NSPersistentContainer(name: "HealthApp")
        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("Core Data加载失败: \(error)")
            }
        }
    }
    
    func saveContext() {
        let context = container.viewContext
        if context.hasChanges {
            do {
                try context.save()
            } catch {
                print("保存失败: \(error)")
            }
        }
    }
}
```

### UserDefaults（简单数据）

```swift
class SettingsManager {
    static let shared = SettingsManager()
    private let defaults = UserDefaults.standard
    
    var notificationsEnabled: Bool {
        get { defaults.bool(forKey: "notificationsEnabled") }
        set { defaults.set(newValue, forKey: "notificationsEnabled") }
    }
    
    var reminderTime: Date? {
        get { defaults.object(forKey: "reminderTime") as? Date }
        set { defaults.set(newValue, forKey: "reminderTime") }
    }
}
```

### Keychain（敏感数据）

```swift
import Security

class KeychainManager {
    static let shared = KeychainManager()
    
    func save(key: String, data: Data) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        
        SecItemDelete(query as CFDictionary)
        return SecItemAdd(query as CFDictionary, nil) == errSecSuccess
    }
    
    func load(key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]
        
        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)
        return result as? Data
    }
    
    func delete(key: String) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        
        return SecItemDelete(query as CFDictionary) == errSecSuccess
    }
}
```

## 网络通信

### URLSession

```swift
import Foundation

class APIClient {
    static let shared = APIClient()
    private let baseURL = "https://api.example.com"
    
    func fetchPatientData(patientID: String) async throws -> PatientData {
        guard let url = URL(string: "\(baseURL)/patients/\(patientID)") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("Bearer \(getAuthToken())", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.serverError
        }
        
        return try JSONDecoder().decode(PatientData.self, from: data)
    }
    
    func uploadHealthData(_ data: HealthData) async throws {
        guard let url = URL(string: "\(baseURL)/health-data") else {
            throw APIError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(getAuthToken())", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(data)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.uploadFailed
        }
    }
    
    private func getAuthToken() -> String {
        // 从Keychain获取认证令牌
        return ""
    }
}

enum APIError: Error {
    case invalidURL
    case serverError
    case uploadFailed
    case unauthorized
}
```

## 推送通知

### 本地通知

```swift
import UserNotifications

class NotificationManager {
    static let shared = NotificationManager()
    
    func requestAuthorization() async throws -> Bool {
        let center = UNUserNotificationCenter.current()
        return try await center.requestAuthorization(options: [.alert, .sound, .badge])
    }
    
    func scheduleMedicationReminder(at date: Date, medication: String) {
        let content = UNMutableNotificationContent()
        content.title = "服药提醒"
        content.body = "该服用\(medication)了"
        content.sound = .default
        content.badge = 1
        
        let calendar = Calendar.current
        let components = calendar.dateComponents([.hour, .minute], from: date)
        let trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: true)
        
        let request = UNNotificationRequest(
            identifier: "medication-\(medication)",
            content: content,
            trigger: trigger
        )
        
        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("添加通知失败: \(error)")
            }
        }
    }
    
    func cancelNotification(identifier: String) {
        UNUserNotificationCenter.current().removePendingNotificationRequests(withIdentifiers: [identifier])
    }
}
```

### 远程推送

```swift
import UIKit

class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(_ application: UIApplication,
                     didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        // 注册远程推送
        UNUserNotificationCenter.current().delegate = self
        application.registerForRemoteNotifications()
        return true
    }
    
    func application(_ application: UIApplication,
                     didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        print("Device Token: \(token)")
        // 发送token到服务器
    }
    
    func application(_ application: UIApplication,
                     didFailToRegisterForRemoteNotificationsWithError error: Error) {
        print("注册远程推送失败: \(error)")
    }
}

extension AppDelegate: UNUserNotificationCenterDelegate {
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                willPresent notification: UNNotification,
                                withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        completionHandler([.banner, .sound])
    }
    
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                didReceive response: UNNotificationResponse,
                                withCompletionHandler completionHandler: @escaping () -> Void) {
        // 处理用户点击通知
        completionHandler()
    }
}
```

## 安全最佳实践

### 1. 数据加密

```swift
import CryptoKit

class EncryptionManager {
    // 生成密钥
    static func generateKey() -> SymmetricKey {
        return SymmetricKey(size: .bits256)
    }
    
    // 加密数据
    static func encrypt(data: Data, key: SymmetricKey) throws -> Data {
        let sealedBox = try AES.GCM.seal(data, using: key)
        return sealedBox.combined!
    }
    
    // 解密数据
    static func decrypt(data: Data, key: SymmetricKey) throws -> Data {
        let sealedBox = try AES.GCM.SealedBox(combined: data)
        return try AES.GCM.open(sealedBox, using: key)
    }
}
```

### 2. 生物识别认证

```swift
import LocalAuthentication

class BiometricAuthManager {
    func authenticate() async throws -> Bool {
        let context = LAContext()
        var error: NSError?
        
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            throw BiometricError.notAvailable
        }
        
        return try await context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: "验证身份以访问健康数据"
        )
    }
}

enum BiometricError: Error {
    case notAvailable
    case authenticationFailed
}
```

### 3. 证书固定

```swift
class CertificatePinningDelegate: NSObject, URLSessionDelegate {
    func urlSession(_ session: URLSession,
                    didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        
        guard let serverTrust = challenge.protectionSpace.serverTrust,
              let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        
        let serverCertificateData = SecCertificateCopyData(certificate) as Data
        
        // 比较证书
        if let localCertPath = Bundle.main.path(forResource: "certificate", ofType: "cer"),
           let localCertData = try? Data(contentsOf: URL(fileURLWithPath: localCertPath)),
           serverCertificateData == localCertData {
            let credential = URLCredential(trust: serverTrust)
            completionHandler(.useCredential, credential)
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

## 测试

### 单元测试

```swift
import XCTest
@testable import HealthApp

class HealthKitManagerTests: XCTestCase {
    var sut: HealthKitManager!
    
    override func setUp() {
        super.setUp()
        sut = HealthKitManager()
    }
    
    override func tearDown() {
        sut = nil
        super.tearDown()
    }
    
    func testHealthKitAvailability() {
        // Given & When
        let isAvailable = sut.isHealthKitAvailable()
        
        // Then
        XCTAssertTrue(isAvailable)
    }
    
    func testSaveWeight() async throws {
        // Given
        let weight = 70.0
        
        // When
        try await sut.saveWeight(weight)
        
        // Then
        // 验证数据已保存
    }
}
```

### UI测试

```swift
import XCTest

class HealthAppUITests: XCTestCase {
    var app: XCUIApplication!
    
    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launch()
    }
    
    func testHealthDashboardDisplay() {
        // Given
        let heartRateLabel = app.staticTexts["心率"]
        
        // Then
        XCTAssertTrue(heartRateLabel.exists)
    }
    
    func testMedicationReminderFlow() {
        // Given
        app.buttons["添加提醒"].tap()
        
        // When
        let medicationField = app.textFields["药物名称"]
        medicationField.tap()
        medicationField.typeText("阿司匹林")
        
        app.buttons["保存"].tap()
        
        // Then
        XCTAssertTrue(app.staticTexts["阿司匹林"].exists)
    }
}
```

## App Store提交

### 1. 准备工作

- 完整的应用功能
- 所有测试通过
- 隐私政策和使用条款
- 应用图标和截图
- 应用描述和关键词

### 2. 医疗应用特殊要求

```xml
<!-- Info.plist 必需配置 -->
<key>NSHealthShareUsageDescription</key>
<string>详细说明为什么需要读取健康数据</string>

<key>NSHealthUpdateUsageDescription</key>
<string>详细说明为什么需要写入健康数据</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>如果使用位置服务，说明原因</string>
```

### 3. App Store审核指南

- 医疗应用必须提供隐私政策
- 如果是医疗器械，需要提供监管批准文件
- 不得包含误导性的健康声明
- 必须明确说明数据使用方式
- 需要提供测试账号（如适用）

## 性能优化

### 1. 启动时间优化

```swift
// 延迟非关键初始化
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    
    // 关键初始化
    setupWindow()
    
    // 延迟初始化
    DispatchQueue.main.async {
        self.setupAnalytics()
        self.setupCrashReporting()
    }
    
    return true
}
```

### 2. 内存管理

```swift
class ImageCache {
    private var cache = NSCache<NSString, UIImage>()
    
    init() {
        cache.countLimit = 100
        cache.totalCostLimit = 50 * 1024 * 1024 // 50MB
    }
    
    func setImage(_ image: UIImage, forKey key: String) {
        cache.setObject(image, forKey: key as NSString)
    }
    
    func image(forKey key: String) -> UIImage? {
        return cache.object(forKey: key as NSString)
    }
}
```

### 3. 后台任务

```swift
class BackgroundTaskManager {
    func scheduleHealthDataSync() {
        let request = BGAppRefreshTaskRequest(identifier: "com.app.healthsync")
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60) // 15分钟后
        
        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("后台任务调度失败: \(error)")
        }
    }
}
```

## 常见问题

### Q: HealthKit数据在模拟器上不可用？
A: HealthKit仅在真实设备上可用，需要使用真机进行测试。

### Q: 如何处理用户拒绝健康数据授权？
A: 提供清晰的说明，引导用户到设置中手动授权，并提供降级功能。

### Q: 应用需要医疗器械认证吗？
A: 取决于应用功能。如果用于诊断、治疗或预防疾病，可能需要FDA或其他监管机构批准。

## 相关资源

- [Apple HealthKit文档](https://developer.apple.com/documentation/healthkit)
- [CareKit开源项目](https://github.com/carekit-apple/CareKit)
- [ResearchKit开源项目](https://github.com/ResearchKit/ResearchKit)
- [iOS医疗应用审核指南](https://developer.apple.com/app-store/review/guidelines/#health-and-health-research)

## 下一步

- [Android医疗应用开发](android-development.md)
- [移动应用安全](mobile-security.md)
- [健康数据集成](health-data-integration.md)

---

*最后更新: 2024年*
