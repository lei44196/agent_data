# Data Agent

一个基于大语言模型的智能数据分析Agent，能够理解自然语言查询，自动生成并执行SQL，从数据库中获取数据并返回分析结果。

## 项目简介

Data Agent 是一款智能数据查询助手，通过自然语言处理技术，让用户无需编写SQL即可完成数据分析工作。用户只需用日常语言描述他们的数据需求，Agent会自动：

1. 理解用户查询意图
2. 从元数据库中检索相关的表、字段和指标信息
3. 生成对应的SQL语句
4. 校验和修正SQL
5. 执行查询并返回结果

## 核心特性

- **自然语言转SQL**：将中文查询转换为精确的SQL语句
- **多数据源支持**：支持MySQL数据仓库、多向量数据库检索
- **智能纠错**：自动校验和修正生成的SQL
- **实时流式输出**：支持SSE流式返回查询进度和结果
- **元数据管理**：自动构建和管理数据仓库的元信息
- **向量检索**：基于Embedding的语义搜索能力

## 技术栈

| 类别 | 技术 |
|------|------|
| Web框架 | FastAPI |
| Agent框架 | LangGraph |
| LLM | 通义千问 (DashScope) |
| Embedding | BGE (BAAI/bge-large-zh-v1.5) |
| 向量数据库 | Qdrant |
| 全文检索 | Elasticsearch |
| 数据库 | MySQL (aiomysql) |
| 异步框架 | asyncio |

## 快速开始

### 环境要求

- Python 3.10+
- MySQL 8.0+
- Qdrant 1.7+
- Elasticsearch 8.0+
- Docker (可选)

### 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/data-agent.git
cd data-agent

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 配置

编辑 `conf/app_config.yaml` 配置文件：

```yaml
db_meta:
  host: localhost
  port: 3307
  user: your_user
  password: your_password
  database: meta

db_dw:
  host: localhost
  port: 3307
  user: your_user
  password: your_password
  database: dw

qdrant:
  host: localhost
  port: 6333
  embedding_size: 1024

embedding:
  host: localhost
  port: 8081
  model: BAAI/bge-large-zh-v1.5

es:
  host: localhost
  port: 9200
  index_name: data_agent

llm:
  model_name: qwen-max
  api_key: your_api_key
```

### 启动服务

```bash
# 启动API服务
cd app
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 构建元数据知识库

在启动服务前，需要先构建元数据知识库：

```bash
python -m app.scripts.build_meta_knowledge -c conf/meta_config.yaml
```

## 使用方法

### API调用

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "统计2025年1月份各品类的销售额占比"}'
```

### Python客户端调用

```python
import requests

response = requests.post(
    "http://localhost:8000/api/query",
    json={"query": "统计2025年1月份各品类的销售额占比"},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

## 项目结构

```
data-agent/
├── app/
│   ├── agent/                 # Agent核心模块
│   │   ├── nodes/             # LangGraph节点
│   │   │   ├── extract_keywords.py    # 关键词提取
│   │   │   ├── column_recall.py        # 字段召回
│   │   │   ├── value_recall.py        # 值召回
│   │   │   ├── metric_recall.py       # 指标召回
│   │   │   ├── merge_retrieved_info.py # 信息合并
│   │   │   ├── filter_table_info.py   # 表信息过滤
│   │   │   ├── filter_metric_info.py  # 指标信息过滤
│   │   │   ├── add_context.py         # 添加上下文
│   │   │   ├── generate_sql.py        # SQL生成
│   │   │   ├── validate_sql.py        # SQL校验
│   │   │   ├── correct_sql.py         # SQL修正
│   │   │   └── execute_sql.py         # SQL执行
│   │   ├── context.py         # Agent上下文
│   │   ├── graph.py           # LangGraph图定义
│   │   ├── llm.py             # LLM配置
│   │   └── state.py           # Agent状态定义
│   ├── api/                   # API路由
│   │   └── routers/
│   │       └── chat_router.py
│   ├── clients/               # 数据源客户端
│   │   ├── mysql_client.py
│   │   ├── qdrant_client.py
│   │   ├── es_client.py
│   │   └── embedding_client.py
│   ├── config/                # 配置管理
│   │   ├── app_config.py
│   │   └── meta_config.py
│   ├── models/                # 数据模型
│   │   ├── mysql/
│   │   ├── qdrant/
│   │   └── es/
│   ├── repositories/          # 数据访问层
│   │   ├── mysql/
│   │   ├── qdrant/
│   │   └── es/
│   ├── service/               # 业务服务层
│   │   ├── chat_service.py
│   │   └── meta_knowledge_service.py
│   ├── core/                  # 核心模块
│   └── scripts/               # 脚本工具
├── conf/                      # 配置文件
│   ├── app_config.yaml
│   └── meta_config.yaml
└── requirements.txt
```

## Agent工作流程

```
用户查询
    │
    ▼
┌─────────────────┐
│ extract_keywords │  关键词提取
└────────┬────────┘
         │
         ├────────────────────┬────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ column_recall   │ │ value_recall   │ │ metric_recall   │
│ 字段信息召回    │ │ 字段值召回     │ │ 指标召回        │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             ▼
              ┌─────────────────────────┐
              │ merge_retrieved_info    │
              │ 合并召回信息            │
              └────────────┬────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌─────────────────┐             ┌─────────────────┐
│ filter_table_info│             │filter_metric_info│
│ 表信息过滤       │             │ 指标信息过滤    │
└────────┬────────┘             └────────┬────────┘
         └───────────────┬───────────────┘
                         ▼
              ┌─────────────────────────┐
              │ add_context             │
              │ 添加上下文              │
              └────────────┬────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │ generate_sql            │
              │ 生成SQL                 │
              └────────────┬────────────┘
                         │
                         ▼
              ┌─────────────────────────┐
              │ validate_sql            │
              │ 校验SQL                 │
              └────────────┬────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
         校验通过               校验失败
              │                     │
              ▼                     ▼
      ┌───────────────┐    ┌─────────────────┐
      │ execute_sql  │    │ correct_sql     │
      │ 执行SQL      │    │ 修正SQL        │
      └───────────────┘    └─────────────────┘
```

## 贡献指南

欢迎提交Issue和Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目主页：https://github.com/lei44196/data-agent
- 问题反馈：https://github.com/lei44196/data-agent/issues
