---
title: 监控与日志
description: "实现医疗系统的监控和日志管理，确保系统可观测性"
difficulty: 中级
estimated_time: 2-3小时
last_updated: "2026-02-11"
version: "1.0"
language: "zh-CN"
tags:
  - monitoring
  - logging
  - observability
  - devops
---

# 监控与日志

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

监控和日志管理是医疗器械软件运维的关键组成部分。有效的监控可以及时发现问题，完整的日志记录满足合规性要求，两者共同保障系统的可靠性和可追溯性。

## 监控基础

### 监控类型

#### 1. 基础设施监控

监控硬件和系统资源：

- **CPU使用率**: 处理器负载
- **内存使用率**: 内存占用情况
- **磁盘使用率**: 存储空间和I/O
- **网络流量**: 带宽使用和延迟

#### 2. 应用性能监控（APM）

监控应用程序性能：

- **响应时间**: 请求处理时间
- **吞吐量**: 每秒处理请求数
- **错误率**: 失败请求比例
- **事务追踪**: 端到端请求追踪

#### 3. 业务监控

监控业务指标：

- **用户活跃度**: 活跃用户数
- **功能使用率**: 各功能使用情况
- **业务流程**: 关键业务流程完成率
- **合规性指标**: 法规要求的指标

### 监控指标

#### 黄金信号（Golden Signals）

Google SRE提出的四个关键指标：

1. **延迟（Latency）**: 请求响应时间
2. **流量（Traffic）**: 系统负载
3. **错误（Errors）**: 失败请求率
4. **饱和度（Saturation）**: 资源使用率

#### RED方法

面向微服务的监控方法：

1. **Rate**: 请求速率
2. **Errors**: 错误率
3. **Duration**: 请求持续时间

#### USE方法

面向资源的监控方法：

1. **Utilization**: 资源使用率
2. **Saturation**: 资源饱和度
3. **Errors**: 错误数量

## Prometheus监控

### Prometheus架构

Prometheus是开源的监控和告警系统，采用拉取模式收集指标。

**核心组件**:
- **Prometheus Server**: 指标收集和存储
- **Pushgateway**: 短期任务指标推送
- **Alertmanager**: 告警管理
- **Exporters**: 指标导出器
- **Client Libraries**: 客户端库

### 部署Prometheus

#### Docker Compose部署

```yaml
# docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.45.0
    container_name: prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=30d'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - ./rules:/etc/prometheus/rules:ro
      - prometheus-data:/prometheus
    networks:
      - monitoring
    restart: unless-stopped

  alertmanager:
    image: prom/alertmanager:v0.26.0
    container_name: alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
      - alertmanager-data:/alertmanager
    networks:
      - monitoring
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:v1.6.0
    container_name: node-exporter
    command:
      - '--path.procfs=/host/proc'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    networks:
      - monitoring
    restart: unless-stopped

  grafana:
    image: grafana/grafana:10.0.0
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning:ro
    networks:
      - monitoring
    restart: unless-stopped

volumes:
  prometheus-data:
  alertmanager-data:
  grafana-data:

networks:
  monitoring:
    driver: bridge
```

#### prometheus.yml配置

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'medical-device-prod'
    environment: 'production'

# 告警规则文件
rule_files:
  - '/etc/prometheus/rules/*.yml'

# 告警管理器配置
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093

# 抓取配置
scrape_configs:
  # Prometheus自身
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # 节点监控
  - job_name: 'node'
    static_configs:
      - targets:
          - 'node-exporter:9100'
        labels:
          instance: 'prod-server-01'

  # 医疗器械应用
  - job_name: 'medical-app'
    static_configs:
      - targets:
          - 'app01:8080'
          - 'app02:8080'
          - 'app03:8080'
    metrics_path: '/metrics'
    scrape_interval: 10s

  # PostgreSQL
  - job_name: 'postgres'
    static_configs:
      - targets:
          - 'postgres-exporter:9187'

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets:
          - 'redis-exporter:9121'

  # Kubernetes集群
  - job_name: 'kubernetes-apiservers'
    kubernetes_sd_configs:
      - role: endpoints
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https

  # Kubernetes节点
  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)

  # Kubernetes Pods
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name
```


### 告警规则

#### rules/medical-app.yml

```yaml
groups:
  - name: medical_app_alerts
    interval: 30s
    rules:
      # 应用可用性告警
      - alert: MedicalAppDown
        expr: up{job="medical-app"} == 0
        for: 1m
        labels:
          severity: critical
          regulatory: "FDA Class II"
        annotations:
          summary: "Medical application is down"
          description: "Instance {{ $labels.instance }} has been down for more than 1 minute."
          runbook_url: "https://wiki.medical-device.com/runbooks/app-down"

      # 高错误率告警
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }} on {{ $labels.instance }}."

      # 响应时间告警
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High response time"
          description: "95th percentile response time is {{ $value }}s on {{ $labels.instance }}."

      # CPU使用率告警
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is {{ $value | humanize }}% on {{ $labels.instance }}."

      # 内存使用率告警
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is {{ $value | humanize }}% on {{ $labels.instance }}."

      # 磁盘空间告警
      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes{fstype!~"tmpfs|fuse.lxcfs"} / node_filesystem_size_bytes)) * 100 > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Disk space low"
          description: "Disk usage is {{ $value | humanize }}% on {{ $labels.instance }} {{ $labels.mountpoint }}."

      # 数据库连接池告警
      - alert: DatabaseConnectionPoolExhausted
        expr: db_connection_pool_active / db_connection_pool_max > 0.9
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Database connection pool nearly exhausted"
          description: "Connection pool usage is {{ $value | humanizePercentage }} on {{ $labels.instance }}."

      # 证书过期告警
      - alert: SSLCertificateExpiringSoon
        expr: (ssl_certificate_expiry_seconds - time()) / 86400 < 30
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "SSL certificate expiring soon"
          description: "SSL certificate for {{ $labels.instance }} expires in {{ $value }} days."
```

### Alertmanager配置

#### alertmanager.yml

```yaml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.medical-device.com:587'
  smtp_from: 'alerts@medical-device.com'
  smtp_auth_username: 'alerts@medical-device.com'
  smtp_auth_password: '${SMTP_PASSWORD}'

# 路由配置
route:
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'default'
  
  routes:
    # 严重告警立即发送
    - match:
        severity: critical
      receiver: 'critical-alerts'
      group_wait: 0s
      repeat_interval: 5m
    
    # 监管相关告警
    - match:
        regulatory: 'FDA Class II'
      receiver: 'regulatory-alerts'
      group_wait: 0s
    
    # 警告级别告警
    - match:
        severity: warning
      receiver: 'warning-alerts'
      repeat_interval: 1h

# 接收器配置
receivers:
  - name: 'default'
    email_configs:
      - to: 'devops@medical-device.com'
        headers:
          Subject: '[Monitoring] {{ .GroupLabels.alertname }}'

  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@medical-device.com'
        headers:
          Subject: '[CRITICAL] {{ .GroupLabels.alertname }}'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#critical-alerts'
        title: 'Critical Alert'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'regulatory-alerts'
    email_configs:
      - to: 'regulatory@medical-device.com,qa@medical-device.com'
        headers:
          Subject: '[REGULATORY] {{ .GroupLabels.alertname }}'

  - name: 'warning-alerts'
    email_configs:
      - to: 'devops@medical-device.com'
        headers:
          Subject: '[WARNING] {{ .GroupLabels.alertname }}'
    slack_configs:
      - api_url: '${SLACK_WEBHOOK_URL}'
        channel: '#monitoring'

# 抑制规则
inhibit_rules:
  # 如果实例宕机，抑制其他告警
  - source_match:
      severity: 'critical'
      alertname: 'MedicalAppDown'
    target_match:
      severity: 'warning'
    equal: ['instance']
```

### 应用程序指标暴露

#### Python示例（使用prometheus_client）

```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from flask import Flask, Response
import time

app = Flask(__name__)

# 定义指标
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_USERS = Gauge(
    'active_users',
    'Number of active users'
)

DB_CONNECTION_POOL = Gauge(
    'db_connection_pool_active',
    'Active database connections'
)

DB_CONNECTION_POOL_MAX = Gauge(
    'db_connection_pool_max',
    'Maximum database connections'
)

# 业务指标
PATIENT_RECORDS_PROCESSED = Counter(
    'patient_records_processed_total',
    'Total patient records processed',
    ['operation']
)

MEDICAL_DEVICE_READINGS = Counter(
    'medical_device_readings_total',
    'Total medical device readings',
    ['device_type', 'status']
)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    request_duration = time.time() - request.start_time
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.endpoint
    ).observe(request_duration)
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint,
        status=response.status_code
    ).inc()
    
    return response

@app.route('/metrics')
def metrics():
    """Prometheus指标端点"""
    return Response(generate_latest(), mimetype='text/plain')

@app.route('/api/patient/<patient_id>')
def get_patient(patient_id):
    # 业务逻辑
    PATIENT_RECORDS_PROCESSED.labels(operation='read').inc()
    return {'patient_id': patient_id}

@app.route('/api/device/reading', methods=['POST'])
def record_device_reading():
    # 记录设备读数
    device_type = request.json.get('device_type')
    status = 'success'  # 或 'error'
    
    MEDICAL_DEVICE_READINGS.labels(
        device_type=device_type,
        status=status
    ).inc()
    
    return {'status': 'ok'}
```

#### Go示例（使用prometheus/client_golang）

```go
package main

import (
    "net/http"
    "time"
    
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    httpRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )
    
    httpRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request duration",
            Buckets: prometheus.DefBuckets,
        },
        []string{"method", "endpoint"},
    )
    
    activeUsers = promauto.NewGauge(
        prometheus.GaugeOpts{
            Name: "active_users",
            Help: "Number of active users",
        },
    )
    
    patientRecordsProcessed = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "patient_records_processed_total",
            Help: "Total patient records processed",
        },
        []string{"operation"},
    )
)

func metricsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        
        // 调用下一个处理器
        next.ServeHTTP(w, r)
        
        // 记录指标
        duration := time.Since(start).Seconds()
        httpRequestDuration.WithLabelValues(r.Method, r.URL.Path).Observe(duration)
        httpRequestsTotal.WithLabelValues(r.Method, r.URL.Path, "200").Inc()
    })
}

func main() {
    // 注册指标端点
    http.Handle("/metrics", promhttp.Handler())
    
    // 应用路由
    mux := http.NewServeMux()
    mux.HandleFunc("/api/patient", handlePatient)
    
    // 应用中间件
    http.Handle("/", metricsMiddleware(mux))
    
    http.ListenAndServe(":8080", nil)
}

func handlePatient(w http.ResponseWriter, r *http.Request) {
    patientRecordsProcessed.WithLabelValues("read").Inc()
    w.Write([]byte("OK"))
}
```

## Grafana可视化

### Grafana仪表板

#### 医疗器械应用仪表板

```json
{
  "dashboard": {
    "title": "Medical Device Application Dashboard",
    "tags": ["medical-device", "production"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "id": 2,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "id": 3,
        "title": "Response Time (95th percentile)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "id": 4,
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "active_users"
          }
        ]
      },
      {
        "id": 5,
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "{{instance}}"
          }
        ]
      },
      {
        "id": 6,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "{{instance}}"
          }
        ]
      }
    ]
  }
}
```

### Grafana配置

#### provisioning/datasources/prometheus.yml

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: "15s"
```

#### provisioning/dashboards/dashboards.yml

```yaml
apiVersion: 1

providers:
  - name: 'Medical Device Dashboards'
    orgId: 1
    folder: 'Medical Device'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

## 日志管理

### ELK Stack

ELK Stack（Elasticsearch、Logstash、Kibana）是流行的日志管理解决方案。

#### Docker Compose部署

```yaml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.9.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
      - xpack.security.enabled=true
      - ELASTIC_PASSWORD=${ELASTIC_PASSWORD}
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - logging
    restart: unless-stopped

  logstash:
    image: docker.elastic.co/logstash/logstash:8.9.0
    container_name: logstash
    ports:
      - "5000:5000"
      - "5044:5044"
    volumes:
      - ./logstash/pipeline:/usr/share/logstash/pipeline:ro
      - ./logstash/config/logstash.yml:/usr/share/logstash/config/logstash.yml:ro
    environment:
      - "LS_JAVA_OPTS=-Xms1g -Xmx1g"
    networks:
      - logging
    depends_on:
      - elasticsearch
    restart: unless-stopped

  kibana:
    image: docker.elastic.co/kibana/kibana:8.9.0
    container_name: kibana
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
      - ELASTICSEARCH_USERNAME=elastic
      - ELASTICSEARCH_PASSWORD=${ELASTIC_PASSWORD}
    networks:
      - logging
    depends_on:
      - elasticsearch
    restart: unless-stopped

  filebeat:
    image: docker.elastic.co/beats/filebeat:8.9.0
    container_name: filebeat
    user: root
    volumes:
      - ./filebeat/filebeat.yml:/usr/share/filebeat/filebeat.yml:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - filebeat-data:/usr/share/filebeat/data
    networks:
      - logging
    depends_on:
      - logstash
    restart: unless-stopped

volumes:
  elasticsearch-data:
  filebeat-data:

networks:
  logging:
    driver: bridge
```

#### Logstash配置

```ruby
# logstash/pipeline/medical-app.conf
input {
  beats {
    port => 5044
  }
  
  tcp {
    port => 5000
    codec => json
  }
}

filter {
  # 解析JSON日志
  if [message] =~ /^\{/ {
    json {
      source => "message"
    }
  }
  
  # 添加地理位置信息
  if [client_ip] {
    geoip {
      source => "client_ip"
      target => "geoip"
    }
  }
  
  # 解析时间戳
  date {
    match => ["timestamp", "ISO8601"]
    target => "@timestamp"
  }
  
  # 添加合规性标签
  mutate {
    add_field => {
      "regulatory_class" => "FDA Class II"
      "iec62304_class" => "B"
      "data_classification" => "PHI"
    }
  }
  
  # 过滤敏感信息
  mutate {
    gsub => [
      "message", "\d{3}-\d{2}-\d{4}", "XXX-XX-XXXX",  # SSN
      "message", "\d{16}", "XXXXXXXXXXXX****"          # 信用卡号
    ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "medical-app-%{+YYYY.MM.dd}"
    user => "elastic"
    password => "${ELASTIC_PASSWORD}"
  }
  
  # 严重错误发送到告警系统
  if [level] == "ERROR" or [level] == "FATAL" {
    http {
      url => "http://alertmanager:9093/api/v1/alerts"
      http_method => "post"
      format => "json"
    }
  }
}
```

#### Filebeat配置

```yaml
# filebeat/filebeat.yml
filebeat.inputs:
  - type: container
    paths:
      - '/var/lib/docker/containers/*/*.log'
    processors:
      - add_docker_metadata:
          host: "unix:///var/run/docker.sock"
      - decode_json_fields:
          fields: ["message"]
          target: ""
          overwrite_keys: true

  - type: log
    enabled: true
    paths:
      - /var/log/medical-app/*.log
    fields:
      app: medical-device
      environment: production
    multiline.pattern: '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
    multiline.negate: true
    multiline.match: after

output.logstash:
  hosts: ["logstash:5044"]

logging.level: info
logging.to_files: true
logging.files:
  path: /var/log/filebeat
  name: filebeat
  keepfiles: 7
  permissions: 0644
```

### 结构化日志

#### Python日志配置

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """JSON格式化器"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'regulatory_class': 'FDA Class II',
            'iec62304_class': 'B'
        }
        
        # 添加异常信息
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # 添加自定义字段
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'patient_id'):
            log_data['patient_id'] = record.patient_id
        if hasattr(record, 'device_id'):
            log_data['device_id'] = record.device_id
        
        return json.dumps(log_data)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/var/log/medical-app/app.log'),
        logging.StreamHandler()
    ]
)

# 应用JSON格式化器
for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())

# 使用日志
logger = logging.getLogger(__name__)

def process_patient_data(patient_id, user_id):
    logger.info(
        'Processing patient data',
        extra={'patient_id': patient_id, 'user_id': user_id}
    )
    
    try:
        # 处理逻辑
        pass
    except Exception as e:
        logger.error(
            'Failed to process patient data',
            exc_info=True,
            extra={'patient_id': patient_id, 'user_id': user_id}
        )
```


### 日志级别和内容

#### 日志级别定义

| 级别 | 用途 | 示例 |
|------|------|------|
| TRACE | 详细调试信息 | 函数进入/退出 |
| DEBUG | 调试信息 | 变量值、中间状态 |
| INFO | 一般信息 | 操作成功、状态变更 |
| WARN | 警告信息 | 可恢复错误、性能问题 |
| ERROR | 错误信息 | 操作失败、异常 |
| FATAL | 致命错误 | 系统崩溃、数据损坏 |

#### 医疗器械日志要求

必须记录的事件：

1. **用户操作**
   - 登录/登出
   - 数据访问
   - 配置变更
   - 权限变更

2. **系统事件**
   - 应用启动/停止
   - 配置加载
   - 服务状态变更
   - 资源告警

3. **业务事件**
   - 患者数据访问
   - 医疗设备读数
   - 诊断结果
   - 处方记录

4. **安全事件**
   - 认证失败
   - 授权失败
   - 数据导出
   - 异常访问模式

5. **错误和异常**
   - 应用错误
   - 系统错误
   - 数据验证失败
   - 集成失败

### 日志保留策略

#### 保留期限

根据法规要求设置保留期限：

- **FDA要求**: 至少保留设备预期寿命期间
- **HIPAA要求**: 至少6年
- **GDPR要求**: 根据数据处理目的确定

#### 日志归档

```python
#!/usr/bin/env python3
"""日志归档脚本"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class LogArchiver:
    def __init__(self, log_dir, archive_dir, retention_days):
        self.log_dir = Path(log_dir)
        self.archive_dir = Path(archive_dir)
        self.retention_days = retention_days
        
        # 创建归档目录
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def archive_old_logs(self):
        """归档旧日志"""
        cutoff_date = datetime.now() - timedelta(days=1)
        
        for log_file in self.log_dir.glob('*.log'):
            # 检查文件修改时间
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if mtime < cutoff_date:
                # 压缩并归档
                archive_name = f"{log_file.stem}_{mtime.strftime('%Y%m%d')}.log.gz"
                archive_path = self.archive_dir / archive_name
                
                with open(log_file, 'rb') as f_in:
                    with gzip.open(archive_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # 删除原文件
                log_file.unlink()
                print(f"Archived: {log_file} -> {archive_path}")
    
    def cleanup_old_archives(self):
        """清理过期归档"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for archive_file in self.archive_dir.glob('*.log.gz'):
            mtime = datetime.fromtimestamp(archive_file.stat().st_mtime)
            
            if mtime < cutoff_date:
                archive_file.unlink()
                print(f"Deleted old archive: {archive_file}")
    
    def run(self):
        """执行归档和清理"""
        print(f"Starting log archival at {datetime.now()}")
        self.archive_old_logs()
        self.cleanup_old_archives()
        print(f"Completed log archival at {datetime.now()}")

if __name__ == '__main__':
    archiver = LogArchiver(
        log_dir='/var/log/medical-app',
        archive_dir='/var/log/medical-app/archive',
        retention_days=2190  # 6年
    )
    archiver.run()
```

## 分布式追踪

### Jaeger

Jaeger是开源的分布式追踪系统，用于监控和排查微服务架构中的问题。

#### Docker Compose部署

```yaml
version: '3.8'

services:
  jaeger:
    image: jaegertracing/all-in-one:1.48
    container_name: jaeger
    environment:
      - COLLECTOR_ZIPKIN_HOST_PORT=:9411
      - COLLECTOR_OTLP_ENABLED=true
    ports:
      - "5775:5775/udp"
      - "6831:6831/udp"
      - "6832:6832/udp"
      - "5778:5778"
      - "16686:16686"  # UI
      - "14268:14268"
      - "14250:14250"
      - "9411:9411"
    networks:
      - tracing
    restart: unless-stopped

networks:
  tracing:
    driver: bridge
```

#### Python应用集成

```python
from jaeger_client import Config
from flask import Flask, request
from opentracing.ext import tags
from opentracing.propagation import Format

app = Flask(__name__)

# 配置Jaeger
config = Config(
    config={
        'sampler': {
            'type': 'const',
            'param': 1,
        },
        'local_agent': {
            'reporting_host': 'jaeger',
            'reporting_port': 6831,
        },
        'logging': True,
    },
    service_name='medical-app',
    validate=True,
)

tracer = config.initialize_tracer()

@app.before_request
def before_request():
    """开始追踪"""
    span_ctx = tracer.extract(Format.HTTP_HEADERS, request.headers)
    span = tracer.start_span(
        operation_name=request.endpoint,
        child_of=span_ctx
    )
    
    # 添加标签
    span.set_tag(tags.HTTP_METHOD, request.method)
    span.set_tag(tags.HTTP_URL, request.url)
    span.set_tag(tags.SPAN_KIND, tags.SPAN_KIND_RPC_SERVER)
    span.set_tag('regulatory.class', 'FDA Class II')
    
    request.span = span

@app.after_request
def after_request(response):
    """结束追踪"""
    if hasattr(request, 'span'):
        request.span.set_tag(tags.HTTP_STATUS_CODE, response.status_code)
        
        if response.status_code >= 400:
            request.span.set_tag(tags.ERROR, True)
        
        request.span.finish()
    
    return response

@app.route('/api/patient/<patient_id>')
def get_patient(patient_id):
    """获取患者信息"""
    with tracer.start_span('get_patient', child_of=request.span) as span:
        span.set_tag('patient.id', patient_id)
        
        # 数据库查询
        with tracer.start_span('db_query', child_of=span) as db_span:
            db_span.set_tag(tags.DATABASE_TYPE, 'postgresql')
            db_span.set_tag(tags.DATABASE_STATEMENT, 'SELECT * FROM patients WHERE id = ?')
            # 执行查询
            pass
        
        return {'patient_id': patient_id}
```

## 医疗器械监控特殊考虑

### 1. 合规性监控

监控合规性相关指标：

```yaml
# Prometheus规则
groups:
  - name: compliance_monitoring
    rules:
      # 审计日志完整性
      - alert: AuditLogGap
        expr: increase(audit_log_entries[1h]) == 0
        for: 1h
        labels:
          severity: critical
          compliance: "FDA,HIPAA"
        annotations:
          summary: "Audit log gap detected"
          description: "No audit log entries in the last hour."
      
      # 数据备份监控
      - alert: BackupFailed
        expr: time() - backup_last_success_timestamp > 86400
        for: 1h
        labels:
          severity: critical
          compliance: "FDA,ISO13485"
        annotations:
          summary: "Backup failed or overdue"
          description: "Last successful backup was more than 24 hours ago."
      
      # 访问控制监控
      - alert: UnauthorizedAccessAttempt
        expr: rate(auth_failures_total[5m]) > 5
        for: 5m
        labels:
          severity: warning
          compliance: "HIPAA"
        annotations:
          summary: "High rate of unauthorized access attempts"
          description: "{{ $value }} failed authentication attempts per second."
```

### 2. 性能监控

监控关键性能指标：

```python
# 性能监控指标
from prometheus_client import Histogram, Summary

# 响应时间分布
RESPONSE_TIME = Histogram(
    'response_time_seconds',
    'Response time distribution',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# 数据处理时间
PROCESSING_TIME = Summary(
    'data_processing_seconds',
    'Data processing time',
    ['operation']
)

# 医疗设备读数延迟
DEVICE_READING_LATENCY = Histogram(
    'device_reading_latency_seconds',
    'Medical device reading latency',
    ['device_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)
```

### 3. 安全监控

监控安全事件：

```yaml
# Logstash安全事件过滤
filter {
  # 检测SQL注入尝试
  if [request_uri] =~ /(\%27)|(\')|(\-\-)|(\%23)|(#)/ {
    mutate {
      add_tag => ["security_threat", "sql_injection"]
      add_field => {
        "threat_level" => "high"
      }
    }
  }
  
  # 检测XSS尝试
  if [request_uri] =~ /<script|javascript:|onerror=/ {
    mutate {
      add_tag => ["security_threat", "xss"]
      add_field => {
        "threat_level" => "high"
      }
    }
  }
  
  # 检测异常访问模式
  if [status_code] == 403 or [status_code] == 401 {
    mutate {
      add_tag => ["security_event", "unauthorized_access"]
    }
  }
}

output {
  # 安全事件发送到SIEM
  if "security_threat" in [tags] {
    http {
      url => "https://siem.medical-device.com/api/events"
      http_method => "post"
      format => "json"
    }
  }
}
```

### 4. 数据质量监控

监控数据质量指标：

```python
from prometheus_client import Counter, Gauge

# 数据验证失败
DATA_VALIDATION_FAILURES = Counter(
    'data_validation_failures_total',
    'Total data validation failures',
    ['data_type', 'validation_rule']
)

# 数据完整性检查
DATA_INTEGRITY_CHECKS = Counter(
    'data_integrity_checks_total',
    'Total data integrity checks',
    ['check_type', 'result']
)

# 数据质量分数
DATA_QUALITY_SCORE = Gauge(
    'data_quality_score',
    'Data quality score (0-100)',
    ['data_source']
)

def validate_patient_data(data):
    """验证患者数据"""
    try:
        # 验证必填字段
        if not data.get('patient_id'):
            DATA_VALIDATION_FAILURES.labels(
                data_type='patient',
                validation_rule='required_field'
            ).inc()
            return False
        
        # 验证数据格式
        if not is_valid_patient_id(data['patient_id']):
            DATA_VALIDATION_FAILURES.labels(
                data_type='patient',
                validation_rule='format'
            ).inc()
            return False
        
        # 数据完整性检查
        DATA_INTEGRITY_CHECKS.labels(
            check_type='patient_data',
            result='pass'
        ).inc()
        
        return True
    except Exception as e:
        DATA_INTEGRITY_CHECKS.labels(
            check_type='patient_data',
            result='error'
        ).inc()
        raise
```

## 监控最佳实践

### 1. 监控即代码

将监控配置纳入版本控制：

```
monitoring/
├── prometheus/
│   ├── prometheus.yml
│   └── rules/
│       ├── app.yml
│       ├── infrastructure.yml
│       └── compliance.yml
├── grafana/
│   ├── dashboards/
│   └── provisioning/
├── alertmanager/
│   └── alertmanager.yml
└── README.md
```

### 2. 分层监控

实施多层次监控：

- **基础设施层**: CPU、内存、磁盘、网络
- **平台层**: Kubernetes、Docker、数据库
- **应用层**: 请求、响应、错误
- **业务层**: 用户、交易、功能使用

### 3. 告警疲劳预防

避免告警疲劳：

- 设置合理的阈值
- 使用告警分组
- 实施告警抑制
- 定期审查告警规则

### 4. 可观测性三支柱

结合使用三种可观测性工具：

- **指标（Metrics）**: Prometheus
- **日志（Logs）**: ELK Stack
- **追踪（Traces）**: Jaeger

### 5. SLO/SLI监控

定义和监控服务级别目标：

```yaml
# SLO定义
slos:
  - name: availability
    target: 99.9%
    window: 30d
    sli:
      expr: |
        sum(rate(http_requests_total{status!~"5.."}[5m])) /
        sum(rate(http_requests_total[5m]))
  
  - name: latency
    target: 95%
    threshold: 1s
    window: 30d
    sli:
      expr: |
        histogram_quantile(0.95,
          rate(http_request_duration_seconds_bucket[5m])
        ) < 1
  
  - name: error_rate
    target: 99.9%
    window: 30d
    sli:
      expr: |
        1 - (sum(rate(http_requests_total{status=~"5.."}[5m])) /
        sum(rate(http_requests_total[5m])))
```

## 故障排查

### 常见问题

1. **指标缺失**
   - 检查Prometheus配置
   - 验证应用指标端点
   - 检查网络连接

2. **告警不触发**
   - 验证告警规则语法
   - 检查Alertmanager配置
   - 查看Prometheus日志

3. **日志丢失**
   - 检查Filebeat状态
   - 验证Logstash配置
   - 检查Elasticsearch存储

4. **仪表板显示异常**
   - 验证数据源配置
   - 检查查询语句
   - 查看Grafana日志

### 调试工具

```bash
# Prometheus查询
curl 'http://prometheus:9090/api/v1/query?query=up'

# 检查告警规则
promtool check rules rules/*.yml

# 测试Alertmanager配置
amtool check-config alertmanager.yml

# 查看Elasticsearch索引
curl -X GET "elasticsearch:9200/_cat/indices?v"

# 测试Logstash配置
logstash -f pipeline.conf --config.test_and_exit
```

## 相关资源

- [CI/CD流水线](ci-cd-pipeline.md) - 自动化构建和部署
- [容器化](containerization.md) - Docker和Kubernetes实践
- [基础设施即代码](infrastructure-as-code.md) - IaC工具和实践

## 参考文献

1. Prometheus官方文档: https://prometheus.io/docs/
2. Grafana官方文档: https://grafana.com/docs/
3. Elastic Stack文档: https://www.elastic.co/guide/
4. Jaeger文档: https://www.jaegertracing.io/docs/
5. "Site Reliability Engineering" - Google
6. "Observability Engineering" - Charity Majors等

---

**标签**: 监控, 日志, Prometheus, Grafana, ELK, Jaeger, 可观测性, 医疗器械

**最后更新**: 2024-01
