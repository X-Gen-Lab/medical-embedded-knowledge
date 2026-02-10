---
title: 容器化与编排
difficulty: intermediate
estimated_time: 2-3小时
---

# 容器化与编排

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

容器化技术为医疗器械软件提供了一致的运行环境，简化了部署和扩展。Docker和Kubernetes是容器化和编排的事实标准，但在医疗器械领域需要特别考虑合规性、安全性和可追溯性。

## Docker容器化

### Docker基础

Docker是一个开源的容器化平台，允许将应用及其依赖打包到轻量级、可移植的容器中。

**核心概念**:
- **镜像（Image）**: 只读模板，包含应用和依赖
- **容器（Container）**: 镜像的运行实例
- **Dockerfile**: 定义镜像构建步骤的文本文件
- **Registry**: 存储和分发镜像的仓库

### 医疗器械软件Dockerfile示例

```dockerfile
# 多阶段构建 - 构建阶段
FROM gcc:11 AS builder

# 设置工作目录
WORKDIR /app

# 复制源代码
COPY src/ ./src/
COPY CMakeLists.txt ./

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    cmake \
    libssl-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 构建应用
RUN mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    cmake --build . --parallel 4

# 运行阶段 - 最小化镜像
FROM debian:bullseye-slim

# 添加元数据标签
LABEL maintainer="dev@medical-device.com" \
      version="1.0.0" \
      description="Medical Device Software" \
      regulatory.fda.class="II" \
      regulatory.iec62304.class="B"

# 创建非root用户
RUN groupadd -r medapp && useradd -r -g medapp medapp

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    libssl1.1 \
    libpq5 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 复制构建产物
COPY --from=builder /app/build/bin/medical-app /usr/local/bin/
COPY --from=builder /app/build/lib/*.so /usr/local/lib/

# 复制配置文件
COPY config/ /etc/medical-app/

# 设置权限
RUN chown -R medapp:medapp /etc/medical-app && \
    chmod 755 /usr/local/bin/medical-app

# 切换到非root用户
USER medapp

# 暴露端口
EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 启动应用
ENTRYPOINT ["/usr/local/bin/medical-app"]
CMD ["--config", "/etc/medical-app/config.yaml"]
```

### Docker最佳实践

#### 1. 多阶段构建

减小镜像大小，提高安全性：

```dockerfile
# 构建阶段
FROM node:16 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# 运行阶段
FROM node:16-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
USER node
CMD ["node", "dist/main.js"]
```

#### 2. 最小化镜像层

合并RUN命令，减少层数：

```dockerfile
# 不推荐
RUN apt-get update
RUN apt-get install -y package1
RUN apt-get install -y package2

# 推荐
RUN apt-get update && apt-get install -y \
    package1 \
    package2 \
    && rm -rf /var/lib/apt/lists/*
```

#### 3. 使用.dockerignore

排除不必要的文件：

```
# .dockerignore
.git
.gitignore
*.md
tests/
docs/
*.log
.vscode/
.idea/
node_modules/
__pycache__/
*.pyc
```

#### 4. 安全扫描

使用工具扫描镜像漏洞：

```bash
# Trivy扫描
trivy image medical-device:latest

# Clair扫描
clair-scanner medical-device:latest

# Docker Scout扫描
docker scout cves medical-device:latest
```

### Docker Compose

用于定义和运行多容器应用：

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    image: medical-device:latest
    container_name: medical-app
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=medicaldb
      - REDIS_HOST=redis
    depends_on:
      - postgres
      - redis
    volumes:
      - ./config:/etc/medical-app:ro
      - app-logs:/var/log/medical-app
    networks:
      - medical-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  postgres:
    image: postgres:13-alpine
    container_name: medical-db
    environment:
      - POSTGRES_DB=medicaldb
      - POSTGRES_USER=meduser
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - medical-network
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    container_name: medical-cache
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    networks:
      - medical-network
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: medical-proxy
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    networks:
      - medical-network
    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:
  app-logs:

networks:
  medical-network:
    driver: bridge

secrets:
  db_password:
    file: ./secrets/db_password.txt
```


## Kubernetes编排

### Kubernetes基础

Kubernetes（K8s）是一个开源的容器编排平台，用于自动化容器化应用的部署、扩展和管理。

**核心概念**:
- **Pod**: 最小部署单元，包含一个或多个容器
- **Deployment**: 管理Pod的副本和更新
- **Service**: 为Pod提供稳定的网络访问
- **ConfigMap**: 存储配置数据
- **Secret**: 存储敏感信息
- **Namespace**: 资源隔离和组织

### 医疗器械应用部署配置

#### Deployment配置

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: medical-device
  namespace: production
  labels:
    app: medical-device
    version: v1.0.0
    regulatory.class: "II"
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: medical-device
  template:
    metadata:
      labels:
        app: medical-device
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      # 安全上下文
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      
      # 初始化容器
      initContainers:
      - name: init-db
        image: busybox:1.35
        command: ['sh', '-c', 'until nc -z postgres 5432; do echo waiting for db; sleep 2; done;']
      
      # 应用容器
      containers:
      - name: medical-app
        image: registry.medical-device.com/medical-device:v1.0.0
        imagePullPolicy: IfNotPresent
        
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        
        # 环境变量
        env:
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: medical-config
              key: db.host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: medical-secrets
              key: db.password
        
        # 资源限制
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        
        # 健康检查
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 3
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # 挂载卷
        volumeMounts:
        - name: config
          mountPath: /etc/medical-app
          readOnly: true
        - name: logs
          mountPath: /var/log/medical-app
        - name: data
          mountPath: /var/lib/medical-app
      
      # 卷定义
      volumes:
      - name: config
        configMap:
          name: medical-config
      - name: logs
        emptyDir: {}
      - name: data
        persistentVolumeClaim:
          claimName: medical-data-pvc
      
      # 镜像拉取密钥
      imagePullSecrets:
      - name: registry-credentials
      
      # 节点选择
      nodeSelector:
        workload: medical-device
      
      # 容忍度
      tolerations:
      - key: "medical-device"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
      
      # 亲和性
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - medical-device
              topologyKey: kubernetes.io/hostname
```

#### Service配置

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: medical-device
  namespace: production
  labels:
    app: medical-device
spec:
  type: ClusterIP
  selector:
    app: medical-device
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

#### Ingress配置

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: medical-device
  namespace: production
  annotations:
    kubernetes.io/ingress.class: "nginx"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  tls:
  - hosts:
    - medical-device.com
    secretName: medical-device-tls
  rules:
  - host: medical-device.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: medical-device
            port:
              number: 80
```

#### ConfigMap配置

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: medical-config
  namespace: production
data:
  db.host: "postgres.production.svc.cluster.local"
  db.port: "5432"
  db.name: "medicaldb"
  redis.host: "redis.production.svc.cluster.local"
  redis.port: "6379"
  log.level: "INFO"
  app.config: |
    server:
      port: 8080
      timeout: 30s
    database:
      max_connections: 100
      connection_timeout: 5s
    cache:
      ttl: 3600
```

#### Secret配置

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: medical-secrets
  namespace: production
type: Opaque
stringData:
  db.password: "secure_password_here"
  redis.password: "redis_password_here"
  api.key: "api_key_here"
```

#### PersistentVolumeClaim配置

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: medical-data-pvc
  namespace: production
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: fast-ssd
```

### Helm图表

Helm是Kubernetes的包管理器，简化应用部署和管理。

#### Chart结构

```
medical-device/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── pvc.yaml
│   ├── hpa.yaml
│   └── _helpers.tpl
└── charts/
```

#### Chart.yaml

```yaml
apiVersion: v2
name: medical-device
description: Medical Device Software Helm Chart
type: application
version: 1.0.0
appVersion: "1.0.0"
keywords:
  - medical-device
  - healthcare
  - fda
maintainers:
  - name: DevOps Team
    email: devops@medical-device.com
dependencies:
  - name: postgresql
    version: "11.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
  - name: redis
    version: "16.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: redis.enabled
```

#### values.yaml

```yaml
# 默认配置值
replicaCount: 3

image:
  repository: registry.medical-device.com/medical-device
  pullPolicy: IfNotPresent
  tag: "1.0.0"

imagePullSecrets:
  - name: registry-credentials

nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: medical-device.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: medical-device-tls
      hosts:
        - medical-device.com

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

nodeSelector:
  workload: medical-device

tolerations: []

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
    - weight: 100
      podAffinityTerm:
        labelSelector:
          matchExpressions:
          - key: app.kubernetes.io/name
            operator: In
            values:
            - medical-device
        topologyKey: kubernetes.io/hostname

# 应用配置
config:
  db:
    host: "postgres"
    port: 5432
    name: "medicaldb"
  redis:
    host: "redis"
    port: 6379
  log:
    level: "INFO"

# 数据库配置
postgresql:
  enabled: true
  auth:
    username: meduser
    password: ""
    database: medicaldb
  primary:
    persistence:
      enabled: true
      size: 10Gi

# Redis配置
redis:
  enabled: true
  auth:
    enabled: true
    password: ""
  master:
    persistence:
      enabled: true
      size: 5Gi
```

#### 部署命令

```bash
# 安装
helm install medical-device ./medical-device \
  --namespace production \
  --create-namespace \
  --values values-prod.yaml

# 升级
helm upgrade medical-device ./medical-device \
  --namespace production \
  --values values-prod.yaml

# 回滚
helm rollback medical-device 1 --namespace production

# 卸载
helm uninstall medical-device --namespace production
```

### 自动扩缩容

#### Horizontal Pod Autoscaler (HPA)

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: medical-device-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: medical-device
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 30
      selectPolicy: Max
```

#### Vertical Pod Autoscaler (VPA)

```yaml
# vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: medical-device-vpa
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: medical-device
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: medical-app
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 1000m
        memory: 1Gi
      controlledResources:
      - cpu
      - memory
```

### 医疗器械容器化特殊考虑

#### 1. 合规性标签

在镜像和Pod中添加合规性元数据：

```yaml
metadata:
  labels:
    regulatory.fda.class: "II"
    regulatory.iec62304.class: "B"
    regulatory.iso13485: "true"
    version: "1.0.0"
    build.number: "12345"
    build.date: "2024-01-15"
```

#### 2. 审计日志

确保所有操作都有审计日志：

```yaml
# 启用Kubernetes审计日志
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse
  namespaces: ["production"]
  verbs: ["create", "update", "patch", "delete"]
  resources:
  - group: ""
    resources: ["pods", "services", "configmaps", "secrets"]
  - group: "apps"
    resources: ["deployments", "statefulsets"]
```

#### 3. 数据持久化

医疗数据必须持久化存储：

```yaml
# StatefulSet用于有状态应用
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: medical-database
spec:
  serviceName: medical-database
  replicas: 3
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 100Gi
```

#### 4. 网络策略

限制Pod间通信：

```yaml
# networkpolicy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: medical-device-netpol
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: medical-device
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: production
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

#### 5. 备份和恢复

定期备份关键数据：

```yaml
# cronjob-backup.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: production
spec:
  schedule: "0 2 * * *"  # 每天凌晨2点
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:13
            command:
            - /bin/sh
            - -c
            - |
              pg_dump -h postgres -U meduser medicaldb | \
              gzip > /backup/backup-$(date +%Y%m%d-%H%M%S).sql.gz
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: medical-secrets
                  key: db.password
            volumeMounts:
            - name: backup
              mountPath: /backup
          volumes:
          - name: backup
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

## 容器安全最佳实践

### 1. 镜像安全

- 使用官方基础镜像
- 定期更新镜像
- 扫描漏洞
- 签名镜像

```bash
# 使用Docker Content Trust
export DOCKER_CONTENT_TRUST=1
docker push registry.medical-device.com/medical-device:v1.0.0

# 使用Cosign签名
cosign sign --key cosign.key registry.medical-device.com/medical-device:v1.0.0
```

### 2. 运行时安全

- 非root用户运行
- 只读根文件系统
- 禁用特权模式
- 限制能力（Capabilities）

### 3. 网络安全

- 使用网络策略
- 启用TLS加密
- 限制出站流量
- 使用服务网格（如Istio）

### 4. 密钥管理

- 使用Kubernetes Secrets
- 集成外部密钥管理（如Vault）
- 定期轮换密钥
- 加密静态数据

```yaml
# 使用External Secrets Operator
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: medical-secrets
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: medical-secrets
    creationPolicy: Owner
  data:
  - secretKey: db.password
    remoteRef:
      key: secret/data/medical-device/db
      property: password
```

## 监控和日志

### Prometheus监控

```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: medical-device
  namespace: production
spec:
  selector:
    matchLabels:
      app: medical-device
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### 日志收集

```yaml
# fluentd-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
  namespace: kube-system
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/medical-device-*.log
      pos_file /var/log/fluentd-medical-device.pos
      tag kubernetes.medical-device
      <parse>
        @type json
        time_key time
        time_format %Y-%m-%dT%H:%M:%S.%NZ
      </parse>
    </source>
    
    <filter kubernetes.medical-device>
      @type record_transformer
      <record>
        regulatory_class "II"
        environment "production"
      </record>
    </filter>
    
    <match kubernetes.medical-device>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      logstash_format true
      logstash_prefix medical-device
    </match>
```

## 故障排查

### 常用命令

```bash
# 查看Pod状态
kubectl get pods -n production

# 查看Pod日志
kubectl logs -f medical-device-xxx -n production

# 进入容器
kubectl exec -it medical-device-xxx -n production -- /bin/sh

# 查看事件
kubectl get events -n production --sort-by='.lastTimestamp'

# 查看资源使用
kubectl top pods -n production
kubectl top nodes

# 描述资源
kubectl describe pod medical-device-xxx -n production
```

### 常见问题

1. **ImagePullBackOff**: 检查镜像名称和拉取密钥
2. **CrashLoopBackOff**: 查看日志，检查健康检查配置
3. **Pending**: 检查资源请求和节点容量
4. **OOMKilled**: 增加内存限制

## 相关资源

- [CI/CD流水线](ci-cd-pipeline.md) - 自动化构建和部署
- [基础设施即代码](infrastructure-as-code.md) - IaC工具和实践
- [监控与日志](monitoring-logging.md) - 监控和日志管理

## 参考文献

1. Docker官方文档: https://docs.docker.com/
2. Kubernetes官方文档: https://kubernetes.io/docs/
3. Helm官方文档: https://helm.sh/docs/
4. "Kubernetes in Action" - Marko Lukša
5. "Docker Deep Dive" - Nigel Poulton

---

**标签**: Docker, Kubernetes, 容器化, 编排, Helm, 医疗器械

**最后更新**: 2024-01
