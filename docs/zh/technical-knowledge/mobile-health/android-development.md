---
title: Android医疗应用开发
description: "学习Android医疗应用开发，构建安全可靠的移动健康解决方案"
difficulty: 中级
estimated_time: 2-3小时
last_updated: "2026-02-11"
version: "1.0"
language: "zh-CN"
tags:
  - android
  - mobile-development
  - mhealth
  - healthcare-apps
---

# Android医疗应用开发

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

Android平台凭借其开放性、广泛的设备覆盖和灵活的开发选项，成为医疗应用开发的重要平台。本指南涵盖Android医疗应用开发的核心技术、最佳实践和监管要求。

## 开发环境设置

### 必需工具
- **Android Studio**: Google官方IDE（最新稳定版本）
- **Android SDK**: 支持API Level 26+（Android 8.0+）
- **Java Development Kit (JDK)**: JDK 11或更高版本
- **Google Play Developer Account**: 用于应用发布

### 推荐工具
- **Android Profiler**: 性能分析工具
- **Firebase**: 后端服务和分析
- **Gradle**: 构建工具
- **LeakCanary**: 内存泄漏检测

## 编程语言选择

### Kotlin（推荐）
```kotlin
// 现代、简洁、安全
import android.health.connect.HealthConnectClient
import android.health.connect.datatypes.HeartRateRecord
import kotlinx.coroutines.flow.Flow

class HealthDataManager(private val context: Context) {
    private val healthConnectClient by lazy {
        HealthConnectClient.getOrCreate(context)
    }
    
    suspend fun requestPermissions() {
        val permissions = setOf(
            HealthPermission.READ_HEART_RATE,
            HealthPermission.READ_STEPS,
            HealthPermission.WRITE_WEIGHT
        )
        
        healthConnectClient.permissionController.requestPermissions(
            context as Activity,
            permissions
        )
    }
    
    suspend fun readHeartRate(): List<HeartRateRecord> {
        val response = healthConnectClient.readRecords(
            ReadRecordsRequest(
                recordType = HeartRateRecord::class,
                timeRangeFilter = TimeRangeFilter.before(Instant.now())
            )
        )
        return response.records
    }
}
```

**优势**:
- 空安全，减少NullPointerException
- 协程支持，简化异步编程
- 扩展函数，提高代码可读性
- Google官方推荐

### Java（传统方法）
```java
// 用于维护旧代码
public class HealthDataManager {
    private Context context;
    
    public HealthDataManager(Context context) {
        this.context = context;
    }
    
    public void requestPermissions(Activity activity) {
        // 请求权限
    }
}
```

## 核心框架

### 1. Health Connect

Health Connect是Android的统一健康数据平台，替代了Google Fit API。

#### 配置Health Connect
```kotlin
// build.gradle (app level)
dependencies {
    implementation("androidx.health.connect:connect-client:1.1.0-alpha07")
}
```

```xml
<!-- AndroidManifest.xml -->
<manifest>
    <uses-permission android:name="android.permission.health.READ_HEART_RATE"/>
    <uses-permission android:name="android.permission.health.READ_STEPS"/>
    <uses-permission android:name="android.permission.health.WRITE_WEIGHT"/>
    
    <application>
        <activity android:name=".MainActivity">
            <!-- Health Connect权限处理 -->
            <intent-filter>
                <action android:name="androidx.health.ACTION_SHOW_PERMISSIONS_RATIONALE"/>
            </intent-filter>
        </activity>
    </application>
</manifest>
```


#### 读写健康数据

```kotlin
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.*
import androidx.health.connect.client.request.ReadRecordsRequest
import androidx.health.connect.client.time.TimeRangeFilter
import java.time.Instant
import java.time.ZonedDateTime

class HealthConnectManager(private val context: Context) {
    private val healthConnectClient by lazy {
        HealthConnectClient.getOrCreate(context)
    }
    
    // 检查Health Connect是否可用
    suspend fun isAvailable(): Boolean {
        return HealthConnectClient.isAvailable(context)
    }
    
    // 检查权限
    suspend fun hasPermissions(permissions: Set<String>): Boolean {
        val granted = healthConnectClient.permissionController.getGrantedPermissions()
        return permissions.all { it in granted }
    }
    
    // 读取步数
    suspend fun readStepCount(startTime: Instant, endTime: Instant): Long {
        val request = ReadRecordsRequest(
            recordType = StepsRecord::class,
            timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
        )
        
        val response = healthConnectClient.readRecords(request)
        return response.records.sumOf { it.count }
    }
    
    // 写入体重数据
    suspend fun writeWeight(weight: Double, time: ZonedDateTime) {
        val weightRecord = WeightRecord(
            weight = Mass.kilograms(weight),
            time = time.toInstant(),
            zoneOffset = time.offset
        )
        
        healthConnectClient.insertRecords(listOf(weightRecord))
    }
    
    // 读取心率数据
    suspend fun readHeartRate(startTime: Instant, endTime: Instant): List<HeartRateRecord> {
        val request = ReadRecordsRequest(
            recordType = HeartRateRecord::class,
            timeRangeFilter = TimeRangeFilter.between(startTime, endTime)
        )
        
        val response = healthConnectClient.readRecords(request)
        return response.records
    }
    
    // 写入血压数据
    suspend fun writeBloodPressure(systolic: Int, diastolic: Int, time: ZonedDateTime) {
        val bloodPressureRecord = BloodPressureRecord(
            systolic = Pressure.millimetersOfMercury(systolic.toDouble()),
            diastolic = Pressure.millimetersOfMercury(diastolic.toDouble()),
            time = time.toInstant(),
            zoneOffset = time.offset
        )
        
        healthConnectClient.insertRecords(listOf(bloodPressureRecord))
    }
    
    // 删除记录
    suspend fun deleteRecords(recordIdsList: List<String>, recordType: KClass<out Record>) {
        healthConnectClient.deleteRecords(
            recordType = recordType,
            recordIdsList = recordIdsList,
            clientRecordIdsList = emptyList()
        )
    }
}
```


### 2. Google Fit API（遗留）

虽然Health Connect是新标准，但许多现有应用仍使用Google Fit。

```kotlin
import com.google.android.gms.fitness.Fitness
import com.google.android.gms.fitness.FitnessOptions
import com.google.android.gms.fitness.data.DataType

class GoogleFitManager(private val context: Context) {
    private val fitnessOptions = FitnessOptions.builder()
        .addDataType(DataType.TYPE_STEP_COUNT_DELTA, FitnessOptions.ACCESS_READ)
        .addDataType(DataType.TYPE_HEART_RATE_BPM, FitnessOptions.ACCESS_READ)
        .addDataType(DataType.TYPE_WEIGHT, FitnessOptions.ACCESS_WRITE)
        .build()
    
    fun requestPermissions(activity: Activity) {
        if (!GoogleSignIn.hasPermissions(GoogleSignIn.getLastSignedInAccount(context), fitnessOptions)) {
            GoogleSignIn.requestPermissions(
                activity,
                REQUEST_OAUTH_REQUEST_CODE,
                GoogleSignIn.getLastSignedInAccount(context),
                fitnessOptions
            )
        }
    }
    
    suspend fun readDailySteps(): Int = suspendCoroutine { continuation ->
        val account = GoogleSignIn.getAccountForExtension(context, fitnessOptions)
        
        Fitness.getHistoryClient(context, account)
            .readDailyTotal(DataType.TYPE_STEP_COUNT_DELTA)
            .addOnSuccessListener { dataSet ->
                val total = dataSet.dataPoints.firstOrNull()
                    ?.getValue(Field.FIELD_STEPS)?.asInt() ?: 0
                continuation.resume(total)
            }
            .addOnFailureListener { e ->
                continuation.resumeWithException(e)
            }
    }
    
    companion object {
        const val REQUEST_OAUTH_REQUEST_CODE = 1001
    }
}
```

## UI框架

### Jetpack Compose（现代方法）

```kotlin
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.launch

@Composable
fun HealthDashboardScreen(viewModel: HealthViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("健康数据") })
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            HealthMetricCard(
                title = "心率",
                value = uiState.heartRate?.toString() ?: "--",
                unit = "bpm",
                icon = Icons.Default.Favorite,
                color = MaterialTheme.colorScheme.error
            )
            
            HealthMetricCard(
                title = "步数",
                value = uiState.stepCount?.toString() ?: "--",
                unit = "步",
                icon = Icons.Default.DirectionsWalk,
                color = MaterialTheme.colorScheme.primary
            )
            
            HealthMetricCard(
                title = "体重",
                value = uiState.weight?.toString() ?: "--",
                unit = "kg",
                icon = Icons.Default.MonitorWeight,
                color = MaterialTheme.colorScheme.secondary
            )
        }
    }
    
    LaunchedEffect(Unit) {
        viewModel.loadHealthData()
    }
}

@Composable
fun HealthMetricCard(
    title: String,
    value: String,
    unit: String,
    icon: ImageVector,
    color: Color
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Icon(
                imageVector = icon,
                contentDescription = title,
                tint = color,
                modifier = Modifier.size(48.dp)
            )
            
            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = "$value $unit",
                    style = MaterialTheme.typography.headlineMedium,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

class HealthViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(HealthUiState())
    val uiState: StateFlow<HealthUiState> = _uiState.asStateFlow()
    
    fun loadHealthData() {
        viewModelScope.launch {
            // 加载健康数据
            _uiState.update { it.copy(
                heartRate = 72,
                stepCount = 8543,
                weight = 70.5
            )}
        }
    }
}

data class HealthUiState(
    val heartRate: Int? = null,
    val stepCount: Int? = null,
    val weight: Double? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)
```


### XML布局（传统方法）

```kotlin
class HealthActivity : AppCompatActivity() {
    private lateinit var binding: ActivityHealthBinding
    private val viewModel: HealthViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityHealthBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupObservers()
        viewModel.loadHealthData()
    }
    
    private fun setupObservers() {
        viewModel.uiState.observe(this) { state ->
            binding.heartRateText.text = state.heartRate?.toString() ?: "--"
            binding.stepCountText.text = state.stepCount?.toString() ?: "--"
            binding.weightText.text = state.weight?.toString() ?: "--"
        }
    }
}
```

```xml
<!-- activity_health.xml -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:padding="16dp">
    
    <com.google.android.material.card.MaterialCardView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:layout_marginBottom="16dp">
        
        <LinearLayout
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:orientation="horizontal"
            android:padding="16dp">
            
            <ImageView
                android:layout_width="48dp"
                android:layout_height="48dp"
                android:src="@drawable/ic_heart"
                android:tint="@color/red"/>
            
            <LinearLayout
                android:layout_width="0dp"
                android:layout_height="wrap_content"
                android:layout_weight="1"
                android:orientation="vertical"
                android:layout_marginStart="16dp">
                
                <TextView
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="心率"
                    android:textSize="16sp"/>
                
                <TextView
                    android:id="@+id/heartRateText"
                    android:layout_width="wrap_content"
                    android:layout_height="wrap_content"
                    android:text="--"
                    android:textSize="24sp"
                    android:textStyle="bold"/>
            </LinearLayout>
        </LinearLayout>
    </com.google.android.material.card.MaterialCardView>
</LinearLayout>
```

## 数据持久化

### Room Database

```kotlin
import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Entity(tableName = "health_records")
data class HealthRecord(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val type: String,
    val value: Double,
    val unit: String,
    val timestamp: Long,
    val notes: String? = null
)

@Dao
interface HealthRecordDao {
    @Query("SELECT * FROM health_records ORDER BY timestamp DESC")
    fun getAllRecords(): Flow<List<HealthRecord>>
    
    @Query("SELECT * FROM health_records WHERE type = :type ORDER BY timestamp DESC LIMIT :limit")
    fun getRecordsByType(type: String, limit: Int = 100): Flow<List<HealthRecord>>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertRecord(record: HealthRecord)
    
    @Insert
    suspend fun insertRecords(records: List<HealthRecord>)
    
    @Delete
    suspend fun deleteRecord(record: HealthRecord)
    
    @Query("DELETE FROM health_records WHERE timestamp < :timestamp")
    suspend fun deleteOldRecords(timestamp: Long)
}

@Database(entities = [HealthRecord::class], version = 1)
abstract class HealthDatabase : RoomDatabase() {
    abstract fun healthRecordDao(): HealthRecordDao
    
    companion object {
        @Volatile
        private var INSTANCE: HealthDatabase? = null
        
        fun getDatabase(context: Context): HealthDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    HealthDatabase::class.java,
                    "health_database"
                )
                .fallbackToDestructiveMigration()
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
```

### DataStore（轻量级数据）

```kotlin
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

class SettingsManager(private val context: Context) {
    private val dataStore = context.dataStore
    
    companion object {
        val NOTIFICATIONS_ENABLED = booleanPreferencesKey("notifications_enabled")
        val REMINDER_TIME = longPreferencesKey("reminder_time")
        val SYNC_FREQUENCY = intPreferencesKey("sync_frequency")
    }
    
    val notificationsEnabled: Flow<Boolean> = dataStore.data
        .map { preferences ->
            preferences[NOTIFICATIONS_ENABLED] ?: true
        }
    
    suspend fun setNotificationsEnabled(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[NOTIFICATIONS_ENABLED] = enabled
        }
    }
    
    suspend fun setReminderTime(time: Long) {
        dataStore.edit { preferences ->
            preferences[REMINDER_TIME] = time
        }
    }
}
```

### EncryptedSharedPreferences（敏感数据）

```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecureStorageManager(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()
    
    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )
    
    fun saveAuthToken(token: String) {
        sharedPreferences.edit()
            .putString("auth_token", token)
            .apply()
    }
    
    fun getAuthToken(): String? {
        return sharedPreferences.getString("auth_token", null)
    }
    
    fun clearAuthToken() {
        sharedPreferences.edit()
            .remove("auth_token")
            .apply()
    }
}
```

## 网络通信

### Retrofit + OkHttp

```kotlin
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.*
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import java.util.concurrent.TimeUnit

// API接口定义
interface HealthApiService {
    @GET("patients/{id}")
    suspend fun getPatient(@Path("id") patientId: String): PatientData
    
    @POST("health-data")
    suspend fun uploadHealthData(@Body data: HealthData): ApiResponse
    
    @GET("medications")
    suspend fun getMedications(@Query("patientId") patientId: String): List<Medication>
}

// Retrofit配置
object ApiClient {
    private const val BASE_URL = "https://api.example.com/"
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = if (BuildConfig.DEBUG) {
            HttpLoggingInterceptor.Level.BODY
        } else {
            HttpLoggingInterceptor.Level.NONE
        }
    }
    
    private val authInterceptor = Interceptor { chain ->
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer ${getAuthToken()}")
            .addHeader("Content-Type", "application/json")
            .build()
        chain.proceed(request)
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .addInterceptor(authInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()
    
    val apiService: HealthApiService = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(HealthApiService::class.java)
    
    private fun getAuthToken(): String {
        // 从安全存储获取token
        return ""
    }
}

// Repository层
class HealthRepository(private val apiService: HealthApiService) {
    suspend fun getPatientData(patientId: String): Result<PatientData> {
        return try {
            val data = apiService.getPatient(patientId)
            Result.success(data)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun uploadHealthData(data: HealthData): Result<ApiResponse> {
        return try {
            val response = apiService.uploadHealthData(data)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```


## 推送通知

### Firebase Cloud Messaging

```kotlin
import com.google.firebase.messaging.FirebaseMessaging
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage

class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        // 发送token到服务器
        sendTokenToServer(token)
    }
    
    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        
        message.notification?.let {
            showNotification(it.title, it.body)
        }
        
        message.data.isNotEmpty().let {
            handleDataPayload(message.data)
        }
    }
    
    private fun showNotification(title: String?, body: String?) {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        
        // 创建通知渠道（Android 8.0+）
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "健康提醒",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "用药提醒和健康通知"
            }
            notificationManager.createNotificationChannel(channel)
        }
        
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build()
        
        notificationManager.notify(NOTIFICATION_ID, notification)
    }
    
    private fun handleDataPayload(data: Map<String, String>) {
        // 处理数据消息
        when (data["type"]) {
            "medication_reminder" -> scheduleMedicationReminder(data)
            "appointment" -> showAppointmentNotification(data)
        }
    }
    
    companion object {
        private const val CHANNEL_ID = "health_notifications"
        private const val NOTIFICATION_ID = 1001
    }
}
```

### 本地通知（AlarmManager + WorkManager）

```kotlin
import androidx.work.*
import java.util.concurrent.TimeUnit

class NotificationManager(private val context: Context) {
    private val workManager = WorkManager.getInstance(context)
    
    // 使用WorkManager调度定期提醒
    fun scheduleDailyMedicationReminder(hour: Int, minute: Int) {
        val currentDate = Calendar.getInstance()
        val dueDate = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, hour)
            set(Calendar.MINUTE, minute)
            set(Calendar.SECOND, 0)
            
            if (before(currentDate)) {
                add(Calendar.DAY_OF_MONTH, 1)
            }
        }
        
        val timeDiff = dueDate.timeInMillis - currentDate.timeInMillis
        
        val reminderWork = PeriodicWorkRequestBuilder<MedicationReminderWorker>(
            24, TimeUnit.HOURS
        )
            .setInitialDelay(timeDiff, TimeUnit.MILLISECONDS)
            .setConstraints(
                Constraints.Builder()
                    .setRequiresBatteryNotLow(true)
                    .build()
            )
            .build()
        
        workManager.enqueueUniquePeriodicWork(
            "medication_reminder",
            ExistingPeriodicWorkPolicy.REPLACE,
            reminderWork
        )
    }
    
    fun cancelMedicationReminder() {
        workManager.cancelUniqueWork("medication_reminder")
    }
}

class MedicationReminderWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        showNotification()
        return Result.success()
    }
    
    private fun showNotification() {
        val notificationManager = applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) 
            as android.app.NotificationManager
        
        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_medication)
            .setContentTitle("服药提醒")
            .setContentText("该服用您的药物了")
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .build()
        
        notificationManager.notify(1, notification)
    }
    
    companion object {
        private const val CHANNEL_ID = "medication_reminders"
    }
}
```

## 安全最佳实践

### 1. 网络安全配置

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <domain-config cleartextTrafficPermitted="false">
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2025-12-31">
            <pin digest="SHA-256">base64encodedpin==</pin>
            <pin digest="SHA-256">backuppin==</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config">
</application>
```

### 2. 生物识别认证

```kotlin
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity

class BiometricAuthManager(private val activity: FragmentActivity) {
    
    fun canAuthenticate(): Boolean {
        val biometricManager = BiometricManager.from(activity)
        return when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
            BiometricManager.BIOMETRIC_SUCCESS -> true
            else -> false
        }
    }
    
    fun authenticate(
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        val executor = ContextCompat.getMainExecutor(activity)
        
        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    onSuccess()
                }
                
                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    onError(errString.toString())
                }
                
                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    onError("认证失败")
                }
            }
        )
        
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("生物识别认证")
            .setSubtitle("验证身份以访问健康数据")
            .setNegativeButtonText("取消")
            .build()
        
        biometricPrompt.authenticate(promptInfo)
    }
}
```

### 3. 数据加密

```kotlin
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties

class EncryptionManager {
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply {
        load(null)
    }
    
    private fun getOrCreateKey(): SecretKey {
        if (!keyStore.containsAlias(KEY_ALIAS)) {
            val keyGenerator = KeyGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_AES,
                "AndroidKeyStore"
            )
            
            val keyGenParameterSpec = KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
            )
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256)
                .build()
            
            keyGenerator.init(keyGenParameterSpec)
            return keyGenerator.generateKey()
        }
        
        return keyStore.getKey(KEY_ALIAS, null) as SecretKey
    }
    
    fun encrypt(data: ByteArray): Pair<ByteArray, ByteArray> {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())
        
        val iv = cipher.iv
        val encryptedData = cipher.doFinal(data)
        
        return Pair(encryptedData, iv)
    }
    
    fun decrypt(encryptedData: ByteArray, iv: ByteArray): ByteArray {
        val cipher = Cipher.getInstance(TRANSFORMATION)
        val spec = GCMParameterSpec(128, iv)
        cipher.init(Cipher.DECRYPT_MODE, getOrCreateKey(), spec)
        
        return cipher.doFinal(encryptedData)
    }
    
    companion object {
        private const val KEY_ALIAS = "health_data_key"
        private const val TRANSFORMATION = "AES/GCM/NoPadding"
    }
}
```

## 测试

### 单元测试

```kotlin
import org.junit.Test
import org.junit.Assert.*
import org.junit.Before
import org.mockito.Mock
import org.mockito.Mockito.*
import org.mockito.MockitoAnnotations
import kotlinx.coroutines.test.runTest

class HealthRepositoryTest {
    @Mock
    private lateinit var apiService: HealthApiService
    
    private lateinit var repository: HealthRepository
    
    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        repository = HealthRepository(apiService)
    }
    
    @Test
    fun `getPatientData returns success when API call succeeds`() = runTest {
        // Given
        val patientId = "123"
        val expectedData = PatientData(id = patientId, name = "张三")
        `when`(apiService.getPatient(patientId)).thenReturn(expectedData)
        
        // When
        val result = repository.getPatientData(patientId)
        
        // Then
        assertTrue(result.isSuccess)
        assertEquals(expectedData, result.getOrNull())
    }
    
    @Test
    fun `uploadHealthData returns failure when API call fails`() = runTest {
        // Given
        val healthData = HealthData(heartRate = 72)
        `when`(apiService.uploadHealthData(healthData)).thenThrow(RuntimeException("Network error"))
        
        // When
        val result = repository.uploadHealthData(healthData)
        
        // Then
        assertTrue(result.isFailure)
    }
}
```

### UI测试（Espresso）

```kotlin
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class HealthActivityTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(HealthActivity::class.java)
    
    @Test
    fun testHealthDataDisplay() {
        // 验证心率显示
        onView(withId(R.id.heartRateText))
            .check(matches(isDisplayed()))
        
        // 验证步数显示
        onView(withId(R.id.stepCountText))
            .check(matches(isDisplayed()))
    }
    
    @Test
    fun testAddMedicationReminder() {
        // 点击添加按钮
        onView(withId(R.id.addReminderButton))
            .perform(click())
        
        // 输入药物名称
        onView(withId(R.id.medicationNameInput))
            .perform(typeText("阿司匹林"), closeSoftKeyboard())
        
        // 保存
        onView(withId(R.id.saveButton))
            .perform(click())
        
        // 验证提醒已添加
        onView(withText("阿司匹林"))
            .check(matches(isDisplayed()))
    }
}
```

## Google Play发布

### 1. 应用签名

```bash
# 生成密钥库
keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias my-key-alias

# 在build.gradle中配置签名
android {
    signingConfigs {
        release {
            storeFile file("my-release-key.jks")
            storePassword "your-store-password"
            keyAlias "my-key-alias"
            keyPassword "your-key-password"
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

### 2. 医疗应用要求

- 提供隐私政策URL
- 完整的数据安全表单
- 医疗器械批准文件（如适用）
- 目标受众和内容分级
- 应用权限说明

### 3. ProGuard配置

```proguard
# proguard-rules.pro

# 保留Health Connect类
-keep class androidx.health.connect.** { *; }

# 保留数据模型
-keep class com.example.healthapp.data.** { *; }

# Retrofit
-keepattributes Signature
-keepattributes Exceptions
-keep class retrofit2.** { *; }

# Gson
-keep class com.google.gson.** { *; }
-keep class * implements com.google.gson.TypeAdapter
```

## 性能优化

### 1. 启动优化

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        
        // 延迟初始化非关键组件
        lifecycleScope.launch {
            delay(1000)
            initializeNonCriticalComponents()
        }
    }
    
    private fun initializeNonCriticalComponents() {
        // 初始化分析工具
        // 初始化崩溃报告
    }
}
```

### 2. 内存优化

```kotlin
class ImageLoader(private val context: Context) {
    private val cache = LruCache<String, Bitmap>(
        (Runtime.getRuntime().maxMemory() / 1024 / 8).toInt()
    )
    
    fun loadImage(url: String, imageView: ImageView) {
        cache.get(url)?.let {
            imageView.setImageBitmap(it)
            return
        }
        
        // 从网络加载
        loadFromNetwork(url) { bitmap ->
            cache.put(url, bitmap)
            imageView.setImageBitmap(bitmap)
        }
    }
}
```

### 3. 后台任务

```kotlin
class DataSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {
    
    override suspend fun doWork(): Result {
        return try {
            syncHealthData()
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }
    
    private suspend fun syncHealthData() {
        // 同步健康数据到服务器
    }
}
```

## 常见问题

### Q: Health Connect在所有设备上都可用吗？
A: Health Connect需要Android 9.0+，部分设备可能需要从Google Play下载Health Connect应用。

### Q: 如何处理不同设备的传感器差异？
A: 使用SensorManager检查传感器可用性，提供降级方案。

### Q: 应用需要医疗器械认证吗？
A: 取决于应用功能。诊断、治疗类应用可能需要FDA或其他监管机构批准。

## 相关资源

- [Health Connect文档](https://developer.android.com/health-and-fitness/guides/health-connect)
- [Android Jetpack](https://developer.android.com/jetpack)
- [Material Design 3](https://m3.material.io/)
- [Google Play医疗应用政策](https://support.google.com/googleplay/android-developer/answer/9876937)

## 下一步

- [iOS医疗应用开发](ios-development.md)
- [移动应用安全](mobile-security.md)
- [健康数据集成](health-data-integration.md)
- [跨平台开发](cross-platform-development.md)

---

*最后更新: 2024年*
