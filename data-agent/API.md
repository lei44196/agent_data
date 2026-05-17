# API接口文档

本文档详细描述 Data Agent 项目提供的所有API接口。

## 目录

- [基础信息](#基础信息)
- [认证方式](#认证方式)
- [查询接口](#查询接口)
- [数据模型](#数据模型)
- [错误码说明](#错误码说明)
- [调用示例](#调用示例)

## 基础信息

| 项目 | 说明 |
|------|------|
| 基础URL | `http://localhost:8000` |
| 数据格式 | JSON |
| 字符编码 | UTF-8 |

## 认证方式

当前版本暂未实现认证，生产环境部署时请添加适当的认证机制：

- API Key认证
- JWT Token认证
- OAuth2.0认证

## 查询接口

### POST /api/query

自然语言查询接口，将用户查询转换为SQL并返回结果。

**请求头**

| 头部 | 必填 | 说明 |
|------|------|------|
| Content-Type | 是 | application/json |

**请求体 (Request Body)**

```json
{
  "query": "统计2025年1月份各品类的销售额占比"
}
```

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| query | string | 是 | 自然语言查询语句 |

**响应格式**

采用 Server-Sent Events (SSE) 流式响应

```
Content-Type: text/event-stream
```

**响应事件格式**

```json
data: {"stage": "抽取关键词"}

data: {"stage": "召回字段信息"}

data: {"stage": "合并召回信息"}

data: {"stage": "生成SQL", "sql": "SELECT ..."}

data: {"stage": "校验SQL"}

data: {"stage": "执行SQL"}

data: {"result": [{"category": "电子产品", "sales": 123456}]}
```

**SSE事件类型**

| stage | 说明 | 附加字段 |
|-------|------|----------|
| 抽取关键词 | 正在从查询中提取关键词 | - |
| 召回字段信息 | 正在从向量库召回相关字段 | - |
| 召回字段值 | 正在从ES召回字段值 | - |
| 召回指标信息 | 正在从向量库召回相关指标 | - |
| 合并召回信息 | 正在合并召回的信息 | - |
| 表信息过滤 | 正在过滤相关表信息 | - |
| 指标信息过滤 | 正在过滤相关指标信息 | - |
| 添加上下文 | 正在添加上下文信息 | - |
| 生成SQL | SQL生成完成 | sql |
| 校验SQL | SQL校验中 | - |
| 修正SQL | SQL修正中 | sql (修正后) |
| 执行SQL | SQL执行中 | - |
| error | 执行出错 | error |
| result | 最终结果 | result |

**完整响应示例**

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "统计2025年1月份各品类的销售额占比"}'
```

```
data: {"stage": "抽取关键词"}

data: {"stage": "召回字段信息"}

data: {"stage": "召回字段值"}

data: {"stage": "召回指标信息"}

data: {"stage": "合并召回信息"}

data: {"stage": "表信息过滤"}

data: {"stage": "指标信息过滤"}

data: {"stage": "添加上下文"}

data: {"stage": "生成SQL", "sql": "SELECT p.category, SUM(o.order_amount) as sales FROM fact_order o JOIN dim_product p ON o.product_id = p.product_id JOIN dim_date d ON o.date_id = d.date_id WHERE d.year = 2025 AND d.month = 1 GROUP BY p.category ORDER BY sales DESC"}

data: {"stage": "校验SQL"}

data: {"stage": "执行SQL"}

data: {"result": [{"category": "电子产品", "sales": 5000000.00}, {"category": "服装", "sales": 3000000.00}, {"category": "食品", "sales": 2000000.00}]}
```

### GET /health

健康检查接口，用于检查服务状态。

**请求示例**

```bash
curl http://localhost:8000/health
```

**响应示例**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "mysql_meta": "connected",
    "mysql_dw": "connected",
    "qdrant": "connected",
    "elasticsearch": "connected"
  }
}
```

**响应字段说明**

| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 服务状态：healthy/unhealthy |
| version | string | 服务版本号 |
| services | object | 各依赖服务状态 |

### GET /docs

Swagger API文档界面。

**访问地址**

```
http://localhost:8000/docs
```

### GET /openapi.json

OpenAPI规范JSON文件。

**访问地址**

```
http://localhost:8000/openapi.json
```

## 数据模型

### QuerySchema

查询请求模型

```python
class QuerySchema:
    query: str  # 自然语言查询
```

### QueryResponse

查询响应事件模型

```python
class StageResponse:
    stage: str           # 当前处理阶段
    sql: Optional[str]   # 生成的SQL (仅在生成SQL阶段)
    error: Optional[str] # 错误信息 (仅在出错时)
    result: Optional[List[Dict]]  # 查询结果 (仅在最终结果)
```

## 错误码说明

| HTTP状态码 | 错误类型 | 说明 |
|-----------|---------|------|
| 200 | - | 请求成功 |
| 400 | BadRequest | 请求参数错误 |
| 404 | NotFound | 资源不存在 |
| 500 | InternalServerError | 服务器内部错误 |
| 503 | ServiceUnavailable | 服务不可用 |

### 错误响应格式

```json
{
  "error": "SQL syntax error",
  "detail": "Near 'SELEC' at line 1"
}
```

### 常见错误及处理

| 错误信息 | 原因 | 处理方法 |
|---------|------|---------|
| Connection refused | 数据库连接失败 | 检查数据库服务状态 |
| Table not found | 表不存在 | 检查meta_config配置 |
| Authentication failed | 认证失败 | 检查API Key配置 |
| Rate limit exceeded | 请求频率超限 | 降低请求频率 |

## 调用示例

### Python requests

```python
import requests
import json

url = "http://localhost:8000/api/query"
payload = {"query": "统计2025年1月份各品类的销售额占比"}

response = requests.post(url, json=payload, stream=True)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = json.loads(line[6:])
            print(data)

            if 'result' in data:
                print("最终结果:", data['result'])
```

### Python aiohttp

```python
import aiohttp
import json

async def query():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://localhost:8000/api/query",
            json={"query": "统计2025年1月份各品类的销售额占比"}
        ) as response:
            async for line in response.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data: '):
                    data = json.loads(line[6:])
                    print(data)

# 运行
import asyncio
asyncio.run(query())
```

### JavaScript Fetch

```javascript
async function query() {
  const response = await fetch('http://localhost:8000/api/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query: '统计2025年1月份各品类的销售额占比' })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const line = decoder.decode(value).trim();
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      console.log(data);
    }
  }
}

query();
```

### cURL

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "统计2025年1月份各品类的销售额占比"}'
```

### Golang

```go
package main

import (
    "bufio"
    "encoding/json"
    "fmt"
    "net/http"
    "strings"
)

func query() {
    req, _ := http.NewRequest("POST", "http://localhost:8000/api/query",
        strings.NewReader(`{"query": "统计2025年1月份各品类的销售额占比"}`))
    req.Header.Set("Content-Type", "application/json")

    client := &http.Client{}
    resp, _ := client.Do(req)
    defer resp.Body.Close()

    scanner := bufio.NewScanner(resp.Body)
    for scanner.Scan() {
        line := scanner.Text()
        if strings.HasPrefix(line, "data: ") {
            var data map[string]interface{}
            json.Unmarshal([]byte(line[6:]), &data)
            fmt.Printf("%+v\n", data)
        }
    }
}

func main() {
    query()
}
```

## 限流说明

当前版本未实现限流，生产环境建议：

- 配置API Gateway实现限流
- 使用Redis实现令牌桶限流
- 建议QPS：10-50（根据LLM响应时间调整）

## 注意事项

1. **流式响应**：`/api/query` 接口返回SSE流式数据，客户端需要正确处理
2. **超时设置**：建议客户端设置合理的超时时间（建议60秒以上）
3. **重试机制**：建议实现指数退避重试机制
4. **错误处理**：关注响应中的 `error` 字段，及时处理异常情况