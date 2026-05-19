# Data Agent

基于 **LangGraph** + **大语言模型** 的智能数据分析 Agent，支持自然语言查询自动转 SQL，从数据仓库中获取结果并返回分析数据。

## 架构总览

项目分为两个子模块：

| 模块 | 目录 | 技术栈 |
|------|------|--------|
| **Backend** | `data-agent/` | FastAPI + LangGraph + Qdrant + Elasticsearch + MySQL |
| **Frontend** | `date-agent-frontend/` | Vue 3 + Vite |

```
用户输入（自然语言）
       │
       ▼
┌──────────────────────┐
│   FastAPI /api/query │  ← SSE 流式响应
└──────────┬───────────┘
           │
           ▼
┌────────────────────────────────────────────────┐
│          LangGraph Agent（12 节点）              │
│                                                  │
│  关键词提取 → 多路召回 → 信息合并 → 上下文构建    │
│  → SQL 生成 → SQL 校验 → 自动修正 → 执行        │
└──────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│  数据层                                    │
│  ┌─────────┐ ┌────────┐ ┌─────────────┐   │
│  │  MySQL  │ │ Qdrant │ │    ES       │   │
│  │ 数据仓库 │ │ 向量库  │ │ 全文检索     │   │
│  │ 元数据   │ │ 语义搜索 │ │ 字段值检索   │   │
│  └─────────┘ └────────┘ └─────────────┘   │
└──────────────────────────────────────────┘
```

## 核心特性

- **自然语言转 SQL** — 中文查询自动解析为精确 SQL
- **多路召回** — 关键词 + 向量语义 + 全文检索 三路召回字段/指标/表信息
- **智能 SQL 生命周期** — 生成 → 校验 → 自动修正 → 执行，闭环处理
- **SSE 流式输出** — 每个处理阶段实时推送，前端实时展示进度
- **可配置元数据** — 通过 YAML 配置文件定义表结构、字段别名、业务指标
- **元数据知识库构建** — 自动化脚本将元数据同步至 MySQL / Qdrant / ES

## 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| Agent 框架 | LangGraph |
| 大语言模型 | 通义千问 (DashScope / OpenAI 兼容接口) |
| Embedding | BGE (BAAI/bge-large-zh-v1.5) |
| 向量数据库 | Qdrant |
| 全文检索 | Elasticsearch |
| 数据库 | MySQL + aiomysql + SQLAlchemy |
| 前端 | Vue 3 + Vite |
| 配置管理 | OmegaConf |

## Agent 工作流程

| 步骤 | 节点 | 说明 |
|------|------|------|
| 1 | `extract_keywords` | jieba 分词 + LLM 关键词扩展 |
| 2 | `column_recall` | 从 Qdrant 向量库召回相关字段 |
| 3 | `value_recall` | 从 ES 全文检索召回字段值 |
| 4 | `metric_recall` | 从 Qdrant 向量库召回业务指标 |
| 5 | `merge_retrieved_info` | 合并三路召回结果 |
| 6 | `filter_table_info` | LLM 过滤无关表信息 |
| 7 | `filter_metric_info` | LLM 过滤无关指标信息 |
| 8 | `add_context` | 注入日期/数据库方言等上下文 |
| 9 | `generate_sql` | LLM 生成 SQL |
| 10 | `validate_sql` | EXPLAIN 校验 SQL 语法 |
| 11 | `correct_sql` | 校验失败时 LLM 自动修正 |
| 12 | `execute_sql` | 执行 SQL 并返回结果 |

## 快速开始

### 前置依赖

- Python 3.11+
- MySQL 8.0+
- Qdrant 1.7+
- Elasticsearch 8.0+
- Docker（可选，用于启动依赖服务）

### 安装 & 配置

```bash
# 1. 进入后端目录
cd data-agent

# 2. 创建虚拟环境
python -m venv .venv
# Linux/Mac
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
# 或使用 uv
uv sync

# 4. 配置
cp conf/app_config.yaml.example conf/app_config.yaml
# 编辑 conf/app_config.yaml，填入实际的数据库地址、密码和 LLM API Key
```

### 构建元数据知识库

在启动服务前，需先构建元数据知识库，将 `conf/meta_config.yaml` 中定义的表结构、字段别名、业务指标同步至 MySQL/Qdrant/ES：

```bash
python -m app.scripts.build_meta_knowledge -c conf/meta_config.yaml
```

### 启动服务

```bash
# 启动 API 服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端（另一个终端）
cd ../date-agent-frontend
npm install
npm run dev
```

前端访问 `http://localhost:5173`，API 服务访问 `http://localhost:8000/docs`。

### 调用示例

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "统计2025年1月份各品类的销售额占比"}'
```

响应为 SSE 流式数据：

```
data: {"stage": "抽取关键词"}
data: {"stage": "召回字段信息"}
data: {"stage": "生成SQL", "sql": "SELECT ..."}
data: {"result": [{"category": "电子产品", "sales": 5000000.00}]}
```

## 项目结构

```
agent_data/
├── data-agent/                  # 后端服务
│   ├── app/
│   │   ├── agent/
│   │   │   ├── nodes/           # LangGraph 节点（12 个）
│   │   │   ├── graph.py         # LangGraph 图定义
│   │   │   ├── llm.py           # LLM 客户端配置
│   │   │   ├── state.py         # Agent 状态定义
│   │   │   └── context.py       # Agent 运行时上下文
│   │   ├── api/
│   │   │   └── routers/         # API 路由
│   │   ├── clients/             # 数据源客户端（MySQL/Qdrant/ES/Embedding）
│   │   ├── config/              # 配置加载与数据类定义
│   │   ├── models/              # ORM 与数据模型
│   │   ├── repositories/        # 数据访问层
│   │   ├── service/             # 业务服务层
│   │   ├── core/                # 中间件、日志、生命周期
│   │   └── scripts/             # 元数据知识库构建脚本
│   ├── conf/
│   │   ├── app_config.yaml      # 应用配置（已 gitignore）
│   │   ├── app_config.yaml.example  # 配置模板
│   │   └── meta_config.yaml     # 元数据表结构定义
│   ├── prompts/                 # LLM Prompt 模板
│   ├── docker/                  # Docker 相关文件
│   ├── main.py                  # 应用入口
│   └── pyproject.toml           # 项目依赖
│
├── date-agent-frontend/         # 前端页面
│   ├── src/
│   │   ├── App.vue              # 聊天界面主组件
│   │   ├── main.js              # Vue 入口
│   │   └── style.css            # 全局样式
│   ├── index.html
│   └── vite.config.js           # 代理配置到后端 8000 端口
│
├── .gitignore
└── README.md
```

## 配置说明

### `conf/meta_config.yaml`

定义数据仓库的**表结构**和**业务指标**，是 Agent 生成 SQL 的上下文来源：

```yaml
tables:
  - name: fact_order
    role: fact           # fact=事实表，dim=维度表
    description: 订单事实表
    columns:
      - name: order_amount
        role: measure     # primary_key/foreign_key/dimension/measure
        description: 订单金额
        alias: [销售额, 收入]  # 中文别名
        sync: false       # 是否同步到 ES 做全文检索
```

### `conf/app_config.yaml`

应用运行时配置，包含数据库连接、向量库、ES、LLM 等参数。**包含敏感信息，已加入 `.gitignore`，请参考 `app_config.yaml.example` 创建。**

## API 文档

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/query` | POST | 自然语言查询（SSE 流式响应） |
| `/health` | GET | 健康检查 |
| `/docs` | GET | Swagger 文档 |

详细 API 文档见 [API.md](data-agent/API.md)。

## 开发

### 添加新的 Agent 节点

1. 在 `app/agent/nodes/` 下创建节点函数
2. 在 `app/agent/graph.py` 中注册节点和边
3. 如需 Prompt，在 `prompts/` 下添加模板文件

### 添加新的数据表

1. 在 `conf/meta_config.yaml` 中添加表定义
2. 重新运行元数据构建脚本

## 许可证

MIT License - 详见 [LICENSE](data-agent/LICENSE)。