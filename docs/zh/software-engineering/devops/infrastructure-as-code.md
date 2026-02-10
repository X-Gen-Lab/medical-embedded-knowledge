---
title: 基础设施即代码（IaC）
difficulty: intermediate
estimated_time: 2-3小时
---

# 基础设施即代码（IaC）

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

基础设施即代码（Infrastructure as Code, IaC）是一种通过代码来管理和配置基础设施的方法。对于医疗器械软件，IaC提供了可重复、可审计、可版本控制的基础设施管理方式，满足合规性要求。

## IaC核心概念

### 什么是IaC

IaC将基础设施配置转化为代码，使用版本控制系统管理，通过自动化工具部署和维护。

**核心原则**:
- **声明式配置**: 描述期望状态，而非执行步骤
- **版本控制**: 所有配置纳入Git管理
- **可重复性**: 相同代码产生相同结果
- **自动化**: 自动化创建、更新、销毁基础设施

**收益**:
- 环境一致性
- 快速环境创建
- 降低人为错误
- 完整的变更历史
- 灾难恢复能力

### IaC工具对比

| 工具 | 类型 | 语言 | 云支持 | 适用场景 |
|------|------|------|---------|----------|
| Terraform | 声明式 | HCL | 多云 | 基础设施配置 |
| Ansible | 命令式 | YAML | 多云 | 配置管理 |
| CloudFormation | 声明式 | JSON/YAML | AWS | AWS专用 |
| Pulumi | 声明式 | 多语言 | 多云 | 复杂逻辑 |
| Chef | 命令式 | Ruby | 多云 | 配置管理 |
| Puppet | 声明式 | DSL | 多云 | 配置管理 |

## Terraform

### Terraform基础

Terraform是HashiCorp开发的开源IaC工具，支持多云平台。

**核心概念**:
- **Provider**: 云平台或服务的接口
- **Resource**: 基础设施组件
- **Module**: 可重用的配置单元
- **State**: 基础设施当前状态
- **Plan**: 变更预览
- **Apply**: 执行变更

### 医疗器械基础设施示例

#### 项目结构

```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── terraform.tfvars
├── versions.tf
├── modules/
│   ├── network/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── compute/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── database/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── monitoring/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/
    ├── dev/
    │   └── terraform.tfvars
    ├── test/
    │   └── terraform.tfvars
    └── prod/
        └── terraform.tfvars
```

#### versions.tf

```hcl
terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.10"
    }
  }
  
  # 远程状态存储
  backend "s3" {
    bucket         = "medical-device-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project         = "Medical Device"
      Environment     = var.environment
      ManagedBy       = "Terraform"
      RegulatoryClass = "II"
      Compliance      = "FDA,IEC62304,ISO13485"
    }
  }
}
```

#### variables.tf

```hcl
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["dev", "test", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, test, staging, or prod."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "medical-device"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage (GB)"
  type        = number
  default     = 100
}

variable "enable_backup" {
  description = "Enable automated backups"
  type        = bool
  default     = true
}

variable "backup_retention_days" {
  description = "Backup retention period (days)"
  type        = number
  default     = 30
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

#### main.tf

```hcl
# 网络模块
module "network" {
  source = "./modules/network"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  
  tags = var.tags
}

# 计算模块
module "compute" {
  source = "./modules/compute"
  
  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  instance_type      = var.instance_type
  
  tags = var.tags
  
  depends_on = [module.network]
}

# 数据库模块
module "database" {
  source = "./modules/database"
  
  project_name          = var.project_name
  environment           = var.environment
  vpc_id                = module.network.vpc_id
  private_subnet_ids    = module.network.private_subnet_ids
  db_instance_class     = var.db_instance_class
  db_allocated_storage  = var.db_allocated_storage
  enable_backup         = var.enable_backup
  backup_retention_days = var.backup_retention_days
  
  tags = var.tags
  
  depends_on = [module.network]
}

# 监控模块
module "monitoring" {
  source = "./modules/monitoring"
  
  project_name = var.project_name
  environment  = var.environment
  
  tags = var.tags
}
```


#### modules/network/main.tf

```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-vpc"
    }
  )
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-igw"
    }
  )
}

# Public Subnets
resource "aws_subnet" "public" {
  count = length(var.availability_zones)
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-public-${count.index + 1}"
      Type = "public"
    }
  )
}

# Private Subnets
resource "aws_subnet" "private" {
  count = length(var.availability_zones)
  
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + 10)
  availability_zone = var.availability_zones[count.index]
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-private-${count.index + 1}"
      Type = "private"
    }
  )
}

# NAT Gateway
resource "aws_eip" "nat" {
  count  = length(var.availability_zones)
  domain = "vpc"
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-nat-eip-${count.index + 1}"
    }
  )
}

resource "aws_nat_gateway" "main" {
  count = length(var.availability_zones)
  
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-nat-${count.index + 1}"
    }
  )
  
  depends_on = [aws_internet_gateway.main]
}

# Route Tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-public-rt"
    }
  )
}

resource "aws_route_table" "private" {
  count  = length(var.availability_zones)
  vpc_id = aws_vpc.main.id
  
  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-private-rt-${count.index + 1}"
    }
  )
}

# Route Table Associations
resource "aws_route_table_association" "public" {
  count = length(var.availability_zones)
  
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table_association" "private" {
  count = length(var.availability_zones)
  
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Security Groups
resource "aws_security_group" "app" {
  name        = "${var.project_name}-${var.environment}-app-sg"
  description = "Security group for application servers"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description = "HTTP from ALB"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }
  
  egress {
    description = "All outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-app-sg"
    }
  )
}

resource "aws_security_group" "db" {
  name        = "${var.project_name}-${var.environment}-db-sg"
  description = "Security group for database"
  vpc_id      = aws_vpc.main.id
  
  ingress {
    description     = "PostgreSQL from app"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-db-sg"
    }
  )
}
```

#### modules/database/main.tf

```hcl
# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-${var.environment}-db-subnet-group"
  subnet_ids = var.private_subnet_ids
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-db-subnet-group"
    }
  )
}

# RDS Parameter Group
resource "aws_db_parameter_group" "main" {
  name   = "${var.project_name}-${var.environment}-pg13"
  family = "postgres13"
  
  parameter {
    name  = "log_connections"
    value = "1"
  }
  
  parameter {
    name  = "log_disconnections"
    value = "1"
  }
  
  parameter {
    name  = "log_statement"
    value = "all"
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-pg13"
    }
  )
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier     = "${var.project_name}-${var.environment}-db"
  engine         = "postgres"
  engine_version = "13.12"
  
  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true
  
  db_name  = "medicaldb"
  username = "meduser"
  password = random_password.db_password.result
  
  db_subnet_group_name   = aws_db_subnet_group.main.name
  parameter_group_name   = aws_db_parameter_group.main.name
  vpc_security_group_ids = [var.db_security_group_id]
  
  # 备份配置
  backup_retention_period = var.backup_retention_days
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:00-sun:05:00"
  
  # 高可用配置
  multi_az               = var.environment == "prod" ? true : false
  deletion_protection    = var.environment == "prod" ? true : false
  skip_final_snapshot    = var.environment != "prod"
  final_snapshot_identifier = var.environment == "prod" ? "${var.project_name}-${var.environment}-final-snapshot" : null
  
  # 监控配置
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  monitoring_interval             = 60
  monitoring_role_arn             = aws_iam_role.rds_monitoring.arn
  
  # 性能洞察
  performance_insights_enabled    = true
  performance_insights_retention_period = 7
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-db"
    }
  )
}

# 随机密码
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# 存储密码到Secrets Manager
resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.project_name}-${var.environment}-db-password"
  
  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-${var.environment}-db-password"
    }
  )
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id = aws_secretsmanager_secret.db_password.id
  secret_string = jsonencode({
    username = aws_db_instance.main.username
    password = random_password.db_password.result
    engine   = "postgres"
    host     = aws_db_instance.main.address
    port     = aws_db_instance.main.port
    dbname   = aws_db_instance.main.db_name
  })
}

# RDS监控IAM角色
resource "aws_iam_role" "rds_monitoring" {
  name = "${var.project_name}-${var.environment}-rds-monitoring"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
      }
    ]
  })
  
  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}
```

### Terraform工作流程

#### 1. 初始化

```bash
# 初始化Terraform
terraform init

# 切换工作空间
terraform workspace new prod
terraform workspace select prod
```

#### 2. 规划

```bash
# 生成执行计划
terraform plan -out=tfplan

# 查看计划详情
terraform show tfplan

# 保存计划为JSON
terraform show -json tfplan > tfplan.json
```

#### 3. 应用

```bash
# 应用变更
terraform apply tfplan

# 自动批准（生产环境不推荐）
terraform apply -auto-approve

# 针对特定资源
terraform apply -target=module.database
```

#### 4. 销毁

```bash
# 销毁所有资源
terraform destroy

# 针对特定资源
terraform destroy -target=module.compute
```

### Terraform最佳实践

#### 1. 状态管理

使用远程状态存储：

```hcl
terraform {
  backend "s3" {
    bucket         = "medical-device-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"
    
    # 启用版本控制
    versioning = true
  }
}
```

#### 2. 模块化

创建可重用的模块：

```hcl
# 使用本地模块
module "network" {
  source = "./modules/network"
  # ...
}

# 使用远程模块
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
  # ...
}
```

#### 3. 变量验证

添加输入验证：

```hcl
variable "environment" {
  type = string
  
  validation {
    condition     = contains(["dev", "test", "prod"], var.environment)
    error_message = "Environment must be dev, test, or prod."
  }
}

variable "db_allocated_storage" {
  type = number
  
  validation {
    condition     = var.db_allocated_storage >= 20 && var.db_allocated_storage <= 65536
    error_message = "DB storage must be between 20 and 65536 GB."
  }
}
```

#### 4. 输出值

定义有用的输出：

```hcl
# outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = module.network.vpc_id
}

output "db_endpoint" {
  description = "Database endpoint"
  value       = module.database.db_endpoint
  sensitive   = true
}

output "app_url" {
  description = "Application URL"
  value       = "https://${module.compute.alb_dns_name}"
}
```

#### 5. 数据源

使用数据源获取现有资源：

```hcl
# 获取当前AWS账户信息
data "aws_caller_identity" "current" {}

# 获取可用区
data "aws_availability_zones" "available" {
  state = "available"
}

# 获取最新AMI
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}
```

## Ansible

### Ansible基础

Ansible是一个开源的配置管理和应用部署工具，使用YAML语法。

**核心概念**:
- **Inventory**: 主机清单
- **Playbook**: 任务剧本
- **Role**: 可重用的任务集合
- **Module**: 执行具体任务的单元
- **Handler**: 事件触发的任务

### 医疗器械配置管理示例

#### 项目结构

```
ansible/
├── ansible.cfg
├── inventory/
│   ├── dev.yml
│   ├── test.yml
│   └── prod.yml
├── group_vars/
│   ├── all.yml
│   ├── dev.yml
│   ├── test.yml
│   └── prod.yml
├── host_vars/
├── playbooks/
│   ├── site.yml
│   ├── deploy.yml
│   └── backup.yml
└── roles/
    ├── common/
    ├── medical-app/
    ├── database/
    └── monitoring/
```

#### ansible.cfg

```ini
[defaults]
inventory = inventory/prod.yml
remote_user = ansible
private_key_file = ~/.ssh/ansible_key
host_key_checking = False
retry_files_enabled = False
gathering = smart
fact_caching = jsonfile
fact_caching_connection = /tmp/ansible_facts
fact_caching_timeout = 3600

[privilege_escalation]
become = True
become_method = sudo
become_user = root
become_ask_pass = False

[ssh_connection]
pipelining = True
control_path = /tmp/ansible-ssh-%%h-%%p-%%r
```

#### inventory/prod.yml

```yaml
all:
  children:
    medical_app:
      hosts:
        app01.medical-device.com:
          ansible_host: 10.0.1.10
        app02.medical-device.com:
          ansible_host: 10.0.1.11
        app03.medical-device.com:
          ansible_host: 10.0.1.12
      vars:
        app_port: 8080
        app_version: "1.0.0"
    
    database:
      hosts:
        db01.medical-device.com:
          ansible_host: 10.0.2.10
          db_role: primary
        db02.medical-device.com:
          ansible_host: 10.0.2.11
          db_role: replica
      vars:
        db_port: 5432
        db_name: medicaldb
    
    monitoring:
      hosts:
        monitor01.medical-device.com:
          ansible_host: 10.0.3.10
      vars:
        prometheus_port: 9090
        grafana_port: 3000
```

#### playbooks/site.yml

```yaml
---
- name: Configure all servers
  hosts: all
  roles:
    - common

- name: Deploy medical application
  hosts: medical_app
  roles:
    - medical-app

- name: Configure database
  hosts: database
  roles:
    - database

- name: Configure monitoring
  hosts: monitoring
  roles:
    - monitoring
```

#### roles/medical-app/tasks/main.yml

```yaml
---
- name: Install dependencies
  apt:
    name:
      - python3
      - python3-pip
      - nginx
      - supervisor
    state: present
    update_cache: yes

- name: Create application user
  user:
    name: medapp
    system: yes
    shell: /bin/bash
    home: /opt/medical-app

- name: Create application directories
  file:
    path: "{{ item }}"
    state: directory
    owner: medapp
    group: medapp
    mode: '0755'
  loop:
    - /opt/medical-app
    - /opt/medical-app/bin
    - /opt/medical-app/config
    - /var/log/medical-app

- name: Download application binary
  get_url:
    url: "https://releases.medical-device.com/{{ app_version }}/medical-app"
    dest: /opt/medical-app/bin/medical-app
    mode: '0755'
    owner: medapp
    group: medapp
    checksum: "sha256:{{ app_checksum }}"

- name: Copy configuration file
  template:
    src: config.yaml.j2
    dest: /opt/medical-app/config/config.yaml
    owner: medapp
    group: medapp
    mode: '0600'
  notify: restart medical-app

- name: Copy systemd service file
  template:
    src: medical-app.service.j2
    dest: /etc/systemd/system/medical-app.service
    mode: '0644'
  notify:
    - reload systemd
    - restart medical-app

- name: Enable and start medical-app service
  systemd:
    name: medical-app
    enabled: yes
    state: started

- name: Configure nginx
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/sites-available/medical-app
    mode: '0644'
  notify: restart nginx

- name: Enable nginx site
  file:
    src: /etc/nginx/sites-available/medical-app
    dest: /etc/nginx/sites-enabled/medical-app
    state: link
  notify: restart nginx

- name: Configure log rotation
  template:
    src: logrotate.j2
    dest: /etc/logrotate.d/medical-app
    mode: '0644'
```

#### roles/medical-app/handlers/main.yml

```yaml
---
- name: reload systemd
  systemd:
    daemon_reload: yes

- name: restart medical-app
  systemd:
    name: medical-app
    state: restarted

- name: restart nginx
  systemd:
    name: nginx
    state: restarted
```

#### roles/medical-app/templates/config.yaml.j2

```yaml
server:
  host: 0.0.0.0
  port: {{ app_port }}
  timeout: 30s

database:
  host: {{ db_host }}
  port: {{ db_port }}
  name: {{ db_name }}
  user: {{ db_user }}
  password: {{ db_password }}
  max_connections: 100

logging:
  level: {{ log_level }}
  file: /var/log/medical-app/app.log
  max_size: 100MB
  max_backups: 10

regulatory:
  fda_class: "II"
  iec62304_class: "B"
  version: "{{ app_version }}"
  build_number: "{{ build_number }}"
```

### Ansible最佳实践

#### 1. 使用Ansible Vault加密敏感数据

```bash
# 创建加密文件
ansible-vault create group_vars/prod/vault.yml

# 编辑加密文件
ansible-vault edit group_vars/prod/vault.yml

# 运行playbook时提供密码
ansible-playbook site.yml --ask-vault-pass

# 使用密码文件
ansible-playbook site.yml --vault-password-file ~/.vault_pass
```

#### 2. 使用角色组织代码

```yaml
# requirements.yml
---
roles:
  - name: geerlingguy.postgresql
    version: 3.4.0
  
  - name: geerlingguy.nginx
    version: 3.1.0

# 安装角色
ansible-galaxy install -r requirements.yml
```

#### 3. 使用标签控制执行

```yaml
- name: Deploy application
  hosts: medical_app
  tasks:
    - name: Update application
      include_role:
        name: medical-app
      tags: [deploy, update]
    
    - name: Update configuration
      template:
        src: config.yaml.j2
        dest: /opt/medical-app/config/config.yaml
      tags: [config]

# 只执行特定标签
ansible-playbook site.yml --tags deploy
ansible-playbook site.yml --skip-tags config
```

#### 4. 使用检查模式

```bash
# 检查模式（不实际执行）
ansible-playbook site.yml --check

# 差异模式（显示变更）
ansible-playbook site.yml --check --diff
```

## 医疗器械IaC特殊考虑

### 1. 合规性标签

在所有资源上添加合规性标签：

```hcl
locals {
  common_tags = {
    Project         = "Medical Device"
    Environment     = var.environment
    ManagedBy       = "Terraform"
    RegulatoryClass = "II"
    IEC62304Class   = "B"
    ISO13485        = "true"
    DataClassification = "PHI"
  }
}
```

### 2. 审计日志

启用所有服务的审计日志：

```hcl
# CloudTrail
resource "aws_cloudtrail" "main" {
  name                          = "${var.project_name}-${var.environment}-trail"
  s3_bucket_name                = aws_s3_bucket.cloudtrail.id
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  
  event_selector {
    read_write_type           = "All"
    include_management_events = true
  }
}
```

### 3. 加密

确保所有数据加密：

```hcl
# S3加密
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.main.arn
    }
  }
}

# EBS加密
resource "aws_ebs_encryption_by_default" "main" {
  enabled = true
}
```

### 4. 备份策略

实施自动化备份：

```hcl
# AWS Backup
resource "aws_backup_plan" "main" {
  name = "${var.project_name}-${var.environment}-backup-plan"
  
  rule {
    rule_name         = "daily_backup"
    target_vault_name = aws_backup_vault.main.name
    schedule          = "cron(0 2 * * ? *)"
    
    lifecycle {
      delete_after = 30
    }
  }
}
```

## 相关资源

- [CI/CD流水线](ci-cd-pipeline.md) - 自动化构建和部署
- [容器化](containerization.md) - Docker和Kubernetes实践
- [监控与日志](monitoring-logging.md) - 监控和日志管理

## 参考文献

1. Terraform官方文档: https://www.terraform.io/docs/
2. Ansible官方文档: https://docs.ansible.com/
3. "Terraform: Up & Running" - Yevgeniy Brikman
4. "Ansible for DevOps" - Jeff Geerling
5. AWS Well-Architected Framework

---

**标签**: IaC, Terraform, Ansible, 基础设施, 自动化, 医疗器械

**最后更新**: 2024-01
