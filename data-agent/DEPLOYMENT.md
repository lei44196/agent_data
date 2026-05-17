# 部署指南

本文档详细说明 Data Agent 项目的部署流程，包括环境准备、服务启动和配置管理。

## 目录

- [环境要求](#环境要求)
- [服务架构](#服务架构)
- [数据准备](#数据准备)
- [详细部署步骤](#详细部署步骤)
- [配置说明](#配置说明)
- [验证部署](#验证部署)
- [常见问题](#常见问题)

## 环境要求

### 基础环境

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.10+ | 建议使用3.11 |
| MySQL | 8.0+ | 数据仓库和元数据库 |
| Qdrant | 1.7+ | 向量数据库 |
| Elasticsearch | 8.0+ | 全文搜索引擎 |
| Docker | 24.0+ | 可选，用于运行中间件 |

### 硬件配置

| 环境 | CPU | 内存 | 磁盘 |
|------|-----|------|------|
| 开发环境 | 2核 | 4GB | 20GB |
| 生产环境 | 4核+ | 8GB+ | 50GB+ |

## 服务架构

```
                    ┌─────────────────┐
                    │   FastAPI      │
                    │   Web服务      │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │  ChatService   │
                    │  聊天服务      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────┴───┐  ┌──────┴─────┐  ┌────┴────┐
     │ LangGraph  │  │ Repository │  │ Client  │
     │ Agent      │  │ Layer      │  │ Layer   │
     └────────┬───┘  └──────┬─────┘  └────┬────┘
              │              │              │
              │      ┌───────┴───────┐      │
              │      │               │      │
    ┌─────────┴──┐ ┌─┴────┐ ┌───────┴──┐ ┌─┴──────┐
    │ MySQL DW  │ │Qdrant│ │Elasticsearch│ │Embedding│
    │ 数据仓库  │ │向量库 │ │全文检索  │ │ 服务   │
    └───────────┘ └──────┘ └──────────┘ └────────┘
```

## 数据准备

### 1. 创建MySQL数据库

```sql
-- 创建元数据库
CREATE DATABASE meta DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建数据仓库数据库
CREATE DATABASE dw DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户并授权
CREATE USER 'dataagent'@'%' IDENTIFIED BY 'YourStrongPassword123';
GRANT ALL PRIVILEGES ON meta.* TO 'dataagent'@'%';
GRANT ALL PRIVILEGES ON dw.* TO 'dataagent'@'%';
FLUSH PRIVILEGES;
```

### 2. 创建表结构

元数据库表结构（系统自动创建）：

```sql
-- 事实表表信息
CREATE TABLE table_info (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50),
    description TEXT,
    INDEX idx_name (name)
);

-- 字段信息
CREATE TABLE column_info (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    role VARCHAR(50),
    description TEXT,
    examples JSON,
    alias JSON,
    table_id VARCHAR(255),
    INDEX idx_name (name),
    INDEX idx_table_id (table_id)
);

-- 指标信息
CREATE TABLE metric_info (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    relevant_columns JSON,
    alias JSON,
    INDEX idx_name (name)
);

-- 字段-指标关联
CREATE TABLE column_metric (
    column_id VARCHAR(255),
    metric_id VARCHAR(255),
    PRIMARY KEY (column_id, metric_id),
    INDEX idx_metric_id (metric_id)
);
```

### 3. 配置元数据

编辑 `conf/meta_config.yaml`：

```yaml
tables:
  - name: fact_order           # 表名
    role: fact                  # 表角色: fact(事实表) / dim(维度表)
    description: 订单事实表    # 表描述
    columns:
      - name: order_id         # 字段名
        role: primary_key      # 字段角色
        description: 订单ID
        alias: [订单号, 订单ID]
        sync: false            # 是否同步值到ES

metrics:
  - name: GMV                  # 指标名
    description: 成交总额
    relevant_columns:           # 相关字段
      - fact_order.order_amount
    alias: [成交总额, 订单总额]
```

## 详细部署步骤

### 方式一：Docker部署（推荐）

#### 1. 启动中间件服务

创建 `docker-compose.yml`：

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: meta
      MYSQL_USER: dataagent
      MYSQL_PASSWORD: YourStrongPassword123
    ports:
      - "3307:3306"
    volumes:
      - mysql_data:/var/lib/mysql

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data

volumes:
  mysql_data:
  qdrant_data:
  es_data:
```

启动服务：

```bash
docker-compose up -d
```

#### 2. 启动Embedding服务

```bash
docker run -p 8081:8081 \
  -v /path/to/bge/model:/model \
  imay/bge-large-zh-v1.5
```

#### 3. 运行应用

```bash
# 克隆并进入项目
cd data-agent

# 构建元数据知识库
python -m app.scripts.build_meta_knowledge -c conf/meta_config.yaml

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 方式二：本地开发部署

#### 1. 安装Python依赖

```bash
# 使用pip
pip install -r requirements.txt

# 或使用poetry
poetry install
```

#### 2. 启动中间件

确保MySQL、Qdrant、Elasticsearch服务已启动：

```bash
# 检查MySQL
mysql -h localhost -P 3307 -u dataagent -p

# 检查Qdrant
curl http://localhost:6333/health

# 检查Elasticsearch
curl http://localhost:9200
```

#### 3. 配置应用

```bash
# 复制配置模板
cp conf/app_config.yaml.example conf/app_config.yaml

# 编辑配置
vim conf/app_config.yaml
```

#### 4. 构建元数据知识库

```bash
python -m app.scripts.build_meta_knowledge -c conf/meta_config.yaml
```

预期输出：

```
加载元数据配置文件
保存表信息和字段信息到meta数据库
同步字段信息到qdrant
同步字段值到es
保存metric信息到meta数据库
同步metric信息到qdrant
元数据知识库构建完成
```

#### 5. 启动服务

```bash
# 开发模式（热重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

## 配置说明

### 应用配置 (app_config.yaml)

```yaml
# 日志配置
logging:
  file:
    enable: true              # 启用文件日志
    level: INFO               # 日志级别
    path: logs                # 日志目录
    rotation: "10 MB"         # 单文件大小限制
    retention: "7 days"        # 日志保留天数
  console:
    enable: true              # 启用控制台日志
    level: INFO

# 元数据库配置
db_meta:
  host: localhost
  port: 3307
  user: dataagent
  password: YourStrongPassword123
  database: meta

# 数据仓库配置
db_dw:
  host: localhost
  port: 3307
  user: dataagent
  password: YourStrongPassword123
  database: dw

# Qdrant向量数据库配置
qdrant:
  host: localhost
  port: 6333
  embedding_size: 1024        # Embedding向量维度

# Embedding服务配置
embedding:
  host: localhost
  port: 8081
  model: BAAI/bge-large-zh-v1.5

# Elasticsearch配置
es:
  host: localhost
  port: 9200
  index_name: data_agent

# LLM大模型配置
llm:
  model_name: qwen-max        # 模型名称
  api_key: your_api_key       # DashScope API Key
```

### 元数据配置 (meta_config.yaml)

```yaml
tables:
  - name: dim_product          # 表名
    role: dim                  # 表角色: fact(事实表) / dim(维度表)
    description: 商品维度表
    columns:
      - name: product_id
        role: primary_key      # 主键
        description: 商品ID
        alias: [商品ID, 产品ID]
        sync: false            # sync: true会同步值到ES用于全文检索

metrics:
  - name: GMV
    description: 成交总额
    relevant_columns:
      - fact_order.order_amount
    alias: [成交总额]
```

### 环境变量配置

也可通过环境变量覆盖配置文件：

```bash
export DB_META_HOST=localhost
export DB_META_PORT=3307
export DB_META_USER=dataagent
export DB_META_PASSWORD=YourStrongPassword123
export DB_META_DATABASE=meta
```

## 验证部署

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

### 2. 测试查询

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "查询2025年1月的销售额"}'
```

预期返回（SSE流式）：

```
data: {"stage": "抽取关键词"}

data: {"stage": "召回字段信息"}

data: {"stage": "合并召回信息"}

data: {"stage": "生成SQL"}

data: {"sql": "SELECT SUM(order_amount) FROM fact_order WHERE ..."}

data: {"stage": "校验SQL"}

data: {"stage": "执行SQL"}

data: {"result": [{"SUM(order_amount)": 1234567.89}]}
```

### 3. 检查日志

```bash
# 查看应用日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

## 常见问题

### 1. 数据库连接失败

**错误信息**：`Connection refused`

**解决方案**：
- 检查MySQL服务是否启动：`systemctl status mysql`
- 验证端口配置是否正确
- 检查防火墙设置

### 2. Qdrant向量库连接失败

**错误信息**：`Cannot connect to Qdrant`

**解决方案**：
- 确认Qdrant服务已启动：`docker ps | grep qdrant`
- 检查端口6333是否可访问

### 3. LLM调用失败

**错误信息**：`Authentication Error`

**解决方案**：
- 检查API Key是否正确
- 确认DashScope服务可用
- 检查网络代理设置

### 4. 元数据构建失败

**错误信息**：`Table 'meta.table_info' doesn't exist`

**解决方案**：
- 确保元数据库表结构已创建
- 检查meta_config.yaml中的表名是否与实际数据库一致

### 5. 内存不足

**错误信息**：`Out of Memory`

**解决方案**：
- 增加Python进程内存限制
- 减少batch_size配置
- 使用分批处理

## 性能优化

### 1. 数据库连接池

```yaml
# app_config.yaml
db_meta:
  pool_size: 10
  max_overflow: 20
```

### 2. Embedding批处理

在 `column_recall.py` 中调整批处理大小：

```python
embedding_batch_size = 20  # 调整此值
```

### 3. 向量检索参数

```python
# 调整召回数量和相似度阈值
columns = await column_qdrant_repository.search(embedding, threshold=0.6, top_k=5)
```

## 监控与日志

### 日志配置

```yaml
logging:
  file:
    enable: true
    level: INFO
    path: logs/app.log
```

### 健康检查端点

```bash
GET /health
```

返回示例：
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "mysql": "connected",
    "qdrant": "connected",
    "elasticsearch": "connected"
  }
}
```