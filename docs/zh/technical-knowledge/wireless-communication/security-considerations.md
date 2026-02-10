---
title: 无线通信安全考虑
difficulty: intermediate
estimated_time: 2-3小时
---

# 无线通信安全考虑

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

医疗器械的无线通信涉及敏感的健康数据传输，必须实施严格的安全措施以保护患者隐私、确保数据完整性并防止未授权访问。本章节详细介绍无线医疗器械的安全威胁、防护措施和最佳实践。

## 安全威胁模型

### 常见攻击类型

#### 1. 窃听攻击（Eavesdropping）

```
威胁: 攻击者截获无线传输的医疗数据
影响: 患者隐私泄露
防护: 端到端加密

示例场景:
- 攻击者在医院附近使用WiFi嗅探器
- 截获未加密的患者生命体征数据
```

#### 2. 中间人攻击（MITM）

```
威胁: 攻击者拦截并篡改通信
影响: 数据完整性破坏，可能危及患者安全
防护: 相互认证、证书验证

示例场景:
- 伪造WiFi接入点
- 拦截并修改输液泵的剂量指令
```

#### 3. 重放攻击（Replay Attack）

```
威胁: 攻击者重放之前捕获的合法消息
影响: 执行未授权操作
防护: 时间戳、序列号、nonce

示例场景:
- 重放"停止报警"命令
- 导致关键报警被忽略
```

#### 4. 拒绝服务攻击（DoS）

```
威胁: 攻击者干扰无线通信
影响: 设备无法通信，功能失效
防护: 频率跳变、冗余通道

示例场景:
- 发送大量干扰信号
- 阻塞2.4 GHz频段
```

#### 5. 设备冒充（Impersonation）

```
威胁: 攻击者伪装成合法设备
影响: 未授权访问系统
防护: 设备认证、证书

示例场景:
- 伪造医疗传感器
- 发送虚假生命体征数据
```

### 威胁评估矩阵

| 攻击类型 | 可能性 | 影响 | 风险等级 | 优先级 |
|---------|-------|------|---------|--------|
| 窃听 | 高 | 中 | 高 | 1 |
| MITM | 中 | 高 | 高 | 1 |
| 重放 | 中 | 高 | 高 | 2 |
| DoS | 中 | 中 | 中 | 3 |
| 设备冒充 | 低 | 高 | 中 | 2 |

## 加密技术

### 对称加密

#### AES（高级加密标准）

```c
#include "mbedtls/aes.h"

// AES-128-CBC加密
typedef struct {
    uint8_t key[16];      // 128位密钥
    uint8_t iv[16];       // 初始化向量
} aes_context_t;

// 加密医疗数据
int encrypt_medical_data(const uint8_t *plaintext, size_t len,
                        uint8_t *ciphertext,
                        aes_context_t *ctx) {
    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    
    // 设置加密密钥
    mbedtls_aes_setkey_enc(&aes, ctx->key, 128);
    
    // CBC模式加密
    int ret = mbedtls_aes_crypt_cbc(&aes,
                                    MBEDTLS_AES_ENCRYPT,
                                    len,
                                    ctx->iv,
                                    plaintext,
                                    ciphertext);
    
    mbedtls_aes_free(&aes);
    return ret;
}

// 解密医疗数据
int decrypt_medical_data(const uint8_t *ciphertext, size_t len,
                        uint8_t *plaintext,
                        aes_context_t *ctx) {
    mbedtls_aes_context aes;
    mbedtls_aes_init(&aes);
    
    // 设置解密密钥
    mbedtls_aes_setkey_dec(&aes, ctx->key, 128);
    
    // CBC模式解密
    int ret = mbedtls_aes_crypt_cbc(&aes,
                                    MBEDTLS_AES_DECRYPT,
                                    len,
                                    ctx->iv,
                                    ciphertext,
                                    plaintext);
    
    mbedtls_aes_free(&aes);
    return ret;
}
```

#### AES-GCM（推荐）

```c
// AES-GCM提供加密+认证
#include "mbedtls/gcm.h"

typedef struct {
    uint8_t key[16];
    uint8_t nonce[12];    // 96位nonce
    uint8_t tag[16];      // 认证标签
} aes_gcm_context_t;

int encrypt_with_gcm(const uint8_t *plaintext, size_t len,
                     const uint8_t *aad, size_t aad_len,
                     uint8_t *ciphertext,
                     aes_gcm_context_t *ctx) {
    mbedtls_gcm_context gcm;
    mbedtls_gcm_init(&gcm);
    
    // 设置密钥
    mbedtls_gcm_setkey(&gcm, MBEDTLS_CIPHER_ID_AES, ctx->key, 128);
    
    // 加密并生成认证标签
    int ret = mbedtls_gcm_crypt_and_tag(&gcm,
                                        MBEDTLS_GCM_ENCRYPT,
                                        len,
                                        ctx->nonce, 12,
                                        aad, aad_len,
                                        plaintext,
                                        ciphertext,
                                        16, ctx->tag);
    
    mbedtls_gcm_free(&gcm);
    return ret;
}
```

### 非对称加密

#### RSA

```c
#include "mbedtls/rsa.h"

// RSA密钥对生成
void generate_rsa_keypair() {
    mbedtls_rsa_context rsa;
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    
    mbedtls_rsa_init(&rsa, MBEDTLS_RSA_PKCS_V21, MBEDTLS_MD_SHA256);
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    
    // 种子随机数生成器
    mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                          (const unsigned char *)"medical_device", 14);
    
    // 生成2048位RSA密钥对
    mbedtls_rsa_gen_key(&rsa, mbedtls_ctr_drbg_random, &ctr_drbg,
                        2048, 65537);
    
    // 导出公钥和私钥
    export_keys(&rsa);
    
    mbedtls_rsa_free(&rsa);
}

// RSA签名（用于固件验证）
int sign_firmware(const uint8_t *firmware, size_t len,
                 uint8_t *signature,
                 mbedtls_rsa_context *rsa) {
    uint8_t hash[32];
    
    // 计算SHA-256哈希
    mbedtls_sha256(firmware, len, hash, 0);
    
    // RSA签名
    return mbedtls_rsa_pkcs1_sign(rsa, NULL, NULL,
                                  MBEDTLS_RSA_PRIVATE,
                                  MBEDTLS_MD_SHA256,
                                  32, hash, signature);
}
```

#### ECC（椭圆曲线加密）

```c
#include "mbedtls/ecdsa.h"

// ECDSA签名（更高效）
int sign_with_ecdsa(const uint8_t *data, size_t len,
                   uint8_t *signature, size_t *sig_len) {
    mbedtls_ecdsa_context ctx;
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    uint8_t hash[32];
    
    mbedtls_ecdsa_init(&ctx);
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    
    // 使用P-256曲线
    mbedtls_ecp_group_load(&ctx.grp, MBEDTLS_ECP_DP_SECP256R1);
    
    // 生成密钥对
    mbedtls_ecdsa_genkey(&ctx, MBEDTLS_ECP_DP_SECP256R1,
                        mbedtls_ctr_drbg_random, &ctr_drbg);
    
    // 计算哈希
    mbedtls_sha256(data, len, hash, 0);
    
    // 签名
    mbedtls_mpi r, s;
    mbedtls_mpi_init(&r);
    mbedtls_mpi_init(&s);
    
    int ret = mbedtls_ecdsa_sign(&ctx.grp, &r, &s, &ctx.d,
                                hash, 32,
                                mbedtls_ctr_drbg_random, &ctr_drbg);
    
    // 编码签名
    encode_ecdsa_signature(&r, &s, signature, sig_len);
    
    mbedtls_mpi_free(&r);
    mbedtls_mpi_free(&s);
    mbedtls_ecdsa_free(&ctx);
    
    return ret;
}
```

## 密钥管理

### 密钥生成

```c
// 使用硬件随机数生成器
int generate_secure_key(uint8_t *key, size_t key_len) {
    mbedtls_entropy_context entropy;
    mbedtls_ctr_drbg_context ctr_drbg;
    
    mbedtls_entropy_init(&entropy);
    mbedtls_ctr_drbg_init(&ctr_drbg);
    
    // 添加设备特定的熵源
    uint8_t device_id[16];
    get_unique_device_id(device_id);
    mbedtls_entropy_update_manual(&entropy, device_id, 16);
    
    // 种子DRBG
    const char *pers = "medical_device_key_gen";
    mbedtls_ctr_drbg_seed(&ctr_drbg, mbedtls_entropy_func, &entropy,
                          (const unsigned char *)pers, strlen(pers));
    
    // 生成密钥
    int ret = mbedtls_ctr_drbg_random(&ctr_drbg, key, key_len);
    
    mbedtls_ctr_drbg_free(&ctr_drbg);
    mbedtls_entropy_free(&entropy);
    
    return ret;
}
```

### 密钥存储

```c
// 使用安全存储区域
typedef enum {
    KEY_STORAGE_FLASH,      // 加密Flash
    KEY_STORAGE_SECURE_ELEMENT,  // 安全元件
    KEY_STORAGE_TRUSTZONE   // ARM TrustZone
} key_storage_type_t;

// 安全存储密钥
int store_key_securely(const uint8_t *key, size_t key_len,
                      const char *key_id) {
    #ifdef USE_SECURE_ELEMENT
        // 使用硬件安全元件（如ATECC608）
        return secure_element_store_key(key, key_len, key_id);
    #elif defined(USE_TRUSTZONE)
        // 使用ARM TrustZone
        return trustzone_store_key(key, key_len, key_id);
    #else
        // 加密后存储在Flash
        uint8_t encrypted_key[32];
        uint8_t device_key[16];
        
        // 使用设备唯一密钥加密
        get_device_unique_key(device_key);
        aes_encrypt(key, key_len, encrypted_key, device_key);
        
        return flash_write(key_id, encrypted_key, key_len);
    #endif
}

// 读取密钥
int load_key_securely(uint8_t *key, size_t key_len,
                     const char *key_id) {
    #ifdef USE_SECURE_ELEMENT
        return secure_element_load_key(key, key_len, key_id);
    #elif defined(USE_TRUSTZONE)
        return trustzone_load_key(key, key_len, key_id);
    #else
        uint8_t encrypted_key[32];
        uint8_t device_key[16];
        
        flash_read(key_id, encrypted_key, key_len);
        get_device_unique_key(device_key);
        
        return aes_decrypt(encrypted_key, key_len, key, device_key);
    #endif
}
```

### 密钥轮换

```c
// 定期更新密钥
typedef struct {
    uint8_t current_key[16];
    uint8_t next_key[16];
    uint32_t key_version;
    time_t key_expiry;
} key_rotation_context_t;

void rotate_encryption_key(key_rotation_context_t *ctx) {
    // 检查密钥是否过期
    if (time(NULL) >= ctx->key_expiry) {
        // 生成新密钥
        generate_secure_key(ctx->next_key, 16);
        
        // 通知对端新密钥
        send_key_update_message(ctx->next_key, ctx->key_version + 1);
        
        // 等待确认
        if (wait_for_key_update_ack()) {
            // 切换到新密钥
            memcpy(ctx->current_key, ctx->next_key, 16);
            ctx->key_version++;
            ctx->key_expiry = time(NULL) + KEY_LIFETIME;
            
            // 安全删除旧密钥
            secure_zero_memory(ctx->next_key, 16);
        }
    }
}

#define KEY_LIFETIME (30 * 24 * 3600)  // 30天
```

## 认证机制

### 设备认证

```c
// 基于证书的设备认证
typedef struct {
    uint8_t *device_cert;     // 设备证书
    size_t cert_len;
    uint8_t *private_key;     // 私钥
    size_t key_len;
    uint8_t *ca_cert;         // CA证书
    size_t ca_cert_len;
} device_identity_t;

// 相互认证
bool mutual_authentication(device_identity_t *local,
                          device_identity_t *peer) {
    // 1. 验证对端证书
    if (!verify_certificate(peer->device_cert, peer->cert_len,
                           local->ca_cert, local->ca_cert_len)) {
        log_error("Peer certificate verification failed");
        return false;
    }
    
    // 2. 生成挑战
    uint8_t challenge[32];
    generate_random(challenge, 32);
    
    // 3. 发送挑战给对端
    send_challenge(challenge, 32);
    
    // 4. 接收并验证签名响应
    uint8_t signature[256];
    size_t sig_len;
    receive_signature(signature, &sig_len);
    
    if (!verify_signature(challenge, 32, signature, sig_len,
                         peer->device_cert)) {
        log_error("Signature verification failed");
        return false;
    }
    
    // 5. 响应对端的挑战
    uint8_t peer_challenge[32];
    receive_challenge(peer_challenge, 32);
    
    sign_challenge(peer_challenge, 32, signature, &sig_len,
                  local->private_key);
    send_signature(signature, sig_len);
    
    return true;
}
```

### 用户认证

```c
// 多因素认证
typedef struct {
    char username[32];
    uint8_t password_hash[32];
    uint8_t totp_secret[20];     // TOTP密钥
    bool biometric_enabled;
} user_credentials_t;

bool authenticate_user(user_credentials_t *creds,
                      const char *password,
                      const char *totp_code) {
    // 1. 验证密码
    uint8_t hash[32];
    hash_password(password, hash);
    
    if (memcmp(hash, creds->password_hash, 32) != 0) {
        log_warning("Password verification failed");
        return false;
    }
    
    // 2. 验证TOTP（时间基础一次性密码）
    uint32_t expected_totp = generate_totp(creds->totp_secret, time(NULL));
    uint32_t provided_totp = atoi(totp_code);
    
    if (expected_totp != provided_totp) {
        log_warning("TOTP verification failed");
        return false;
    }
    
    // 3. 生物识别（可选）
    if (creds->biometric_enabled) {
        if (!verify_biometric()) {
            log_warning("Biometric verification failed");
            return false;
        }
    }
    
    return true;
}

// TOTP实现
uint32_t generate_totp(const uint8_t *secret, time_t timestamp) {
    uint64_t time_step = timestamp / 30;  // 30秒时间窗口
    uint8_t hmac[20];
    
    // HMAC-SHA1
    mbedtls_md_hmac(mbedtls_md_info_from_type(MBEDTLS_MD_SHA1),
                    secret, 20,
                    (uint8_t *)&time_step, 8,
                    hmac);
    
    // 动态截断
    int offset = hmac[19] & 0x0F;
    uint32_t code = ((hmac[offset] & 0x7F) << 24) |
                    ((hmac[offset + 1] & 0xFF) << 16) |
                    ((hmac[offset + 2] & 0xFF) << 8) |
                    (hmac[offset + 3] & 0xFF);
    
    return code % 1000000;  // 6位数字
}
```

## 安全通信协议

### TLS/DTLS

```c
#include "mbedtls/ssl.h"

// TLS配置
typedef struct {
    mbedtls_ssl_context ssl;
    mbedtls_ssl_config conf;
    mbedtls_x509_crt cacert;
    mbedtls_x509_crt owncert;
    mbedtls_pk_context pkey;
} tls_context_t;

// 初始化TLS客户端
int init_tls_client(tls_context_t *ctx) {
    mbedtls_ssl_init(&ctx->ssl);
    mbedtls_ssl_config_init(&ctx->conf);
    mbedtls_x509_crt_init(&ctx->cacert);
    mbedtls_x509_crt_init(&ctx->owncert);
    mbedtls_pk_init(&ctx->pkey);
    
    // 加载CA证书
    mbedtls_x509_crt_parse(&ctx->cacert, ca_cert_pem, ca_cert_len);
    
    // 加载客户端证书和私钥
    mbedtls_x509_crt_parse(&ctx->owncert, client_cert_pem, client_cert_len);
    mbedtls_pk_parse_key(&ctx->pkey, client_key_pem, client_key_len, NULL, 0);
    
    // 配置TLS
    mbedtls_ssl_config_defaults(&ctx->conf,
                                MBEDTLS_SSL_IS_CLIENT,
                                MBEDTLS_SSL_TRANSPORT_STREAM,
                                MBEDTLS_SSL_PRESET_DEFAULT);
    
    // 设置最低TLS版本
    mbedtls_ssl_conf_min_version(&ctx->conf,
                                 MBEDTLS_SSL_MAJOR_VERSION_3,
                                 MBEDTLS_SSL_MINOR_VERSION_3);  // TLS 1.2
    
    // 配置密码套件（仅允许强加密）
    const int ciphersuites[] = {
        MBEDTLS_TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
        MBEDTLS_TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
        0
    };
    mbedtls_ssl_conf_ciphersuites(&ctx->conf, ciphersuites);
    
    // 设置证书
    mbedtls_ssl_conf_ca_chain(&ctx->conf, &ctx->cacert, NULL);
    mbedtls_ssl_conf_own_cert(&ctx->conf, &ctx->owncert, &ctx->pkey);
    
    // 要求服务器证书验证
    mbedtls_ssl_conf_authmode(&ctx->conf, MBEDTLS_SSL_VERIFY_REQUIRED);
    
    mbedtls_ssl_setup(&ctx->ssl, &ctx->conf);
    
    return 0;
}
```

## 防护措施实现

### 防重放攻击

```c
// 使用滑动窗口防重放
#define REPLAY_WINDOW_SIZE 64

typedef struct {
    uint64_t last_seq;
    uint64_t window[REPLAY_WINDOW_SIZE / 64];
} replay_protection_t;

bool check_replay(replay_protection_t *ctx, uint64_t seq) {
    // 序列号太旧
    if (seq + REPLAY_WINDOW_SIZE < ctx->last_seq) {
        return false;
    }
    
    // 序列号是新的
    if (seq > ctx->last_seq) {
        // 更新窗口
        uint64_t diff = seq - ctx->last_seq;
        if (diff < REPLAY_WINDOW_SIZE) {
            // 移位窗口
            for (int i = 0; i < REPLAY_WINDOW_SIZE / 64; i++) {
                ctx->window[i] <<= diff;
            }
        } else {
            // 清空窗口
            memset(ctx->window, 0, sizeof(ctx->window));
        }
        
        ctx->last_seq = seq;
        ctx->window[0] |= 1;
        return true;
    }
    
    // 检查窗口内的序列号
    uint64_t diff = ctx->last_seq - seq;
    uint64_t index = diff / 64;
    uint64_t bit = diff % 64;
    
    if (ctx->window[index] & (1ULL << bit)) {
        // 已接收过
        return false;
    }
    
    // 标记为已接收
    ctx->window[index] |= (1ULL << bit);
    return true;
}
```

### 安全固件更新

```c
// 验证固件签名
bool verify_firmware_signature(const uint8_t *firmware, size_t len,
                              const uint8_t *signature, size_t sig_len) {
    mbedtls_rsa_context rsa;
    uint8_t hash[32];
    
    // 加载公钥
    load_public_key(&rsa);
    
    // 计算固件哈希
    mbedtls_sha256(firmware, len, hash, 0);
    
    // 验证签名
    int ret = mbedtls_rsa_pkcs1_verify(&rsa,
                                       NULL, NULL,
                                       MBEDTLS_RSA_PUBLIC,
                                       MBEDTLS_MD_SHA256,
                                       32, hash, signature);
    
    mbedtls_rsa_free(&rsa);
    return (ret == 0);
}

// 安全启动
void secure_boot() {
    // 1. 验证bootloader
    if (!verify_bootloader_signature()) {
        halt_system("Bootloader verification failed");
    }
    
    // 2. 验证应用固件
    if (!verify_application_signature()) {
        halt_system("Application verification failed");
    }
    
    // 3. 启动应用
    jump_to_application();
}
```

## 监管合规

### FDA网络安全指南

```
关键要求:
1. 设计阶段的威胁建模
2. 安全风险管理
3. 软件物料清单（SBOM）
4. 漏洞管理计划
5. 安全更新机制

文档要求:
- 网络安全设计文档
- 威胁分析报告
- 渗透测试结果
- 事件响应计划
```

### IEC 62443（工业网络安全）

```
安全级别:
- SL 1: 防止偶然违规
- SL 2: 防止有意违规（基本技能）
- SL 3: 防止有意违规（专业技能）
- SL 4: 防止有意违规（高级技能）

医疗器械通常要求: SL 2-3
```

## 最佳实践总结

### 设计原则

1. ✅ 默认安全（Secure by Default）
2. ✅ 纵深防御（Defense in Depth）
3. ✅ 最小权限原则
4. ✅ 失败安全（Fail Secure）
5. ✅ 安全更新机制

### 实施检查清单

- [ ] 所有无线通信使用加密
- [ ] 实施相互认证
- [ ] 使用强密码套件（AES-128+）
- [ ] 安全存储密钥和证书
- [ ] 实施防重放保护
- [ ] 定期密钥轮换
- [ ] 安全固件更新
- [ ] 日志和审计
- [ ] 渗透测试
- [ ] 漏洞管理流程

## 参考资源

- [FDA - Cybersecurity in Medical Devices](https://www.fda.gov/medical-devices/digital-health-center-excellence/cybersecurity)
- [IEC 62443 Series](https://www.iec.ch/cyber-security)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [OWASP IoT Security](https://owasp.org/www-project-internet-of-things/)

---

**相关章节**: 
- [蓝牙安全](bluetooth-ble.md#配对与安全)
- [WiFi安全](wifi.md#安全配置)
- [互联互通安全](../interoperability/index.md#安全考虑)
