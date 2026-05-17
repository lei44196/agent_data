# 贡献指南

感谢您对 Data Agent 项目的兴趣！我们欢迎各种形式的贡献，包括但不限于代码提交、问题反馈、文档改进等。

## 目录

- [行为准则](#行为准则)
- [快速开始](#快速开始)
- [开发环境设置](#开发环境设置)
- [开发流程](#开发流程)
- [代码规范](#代码规范)
- [提交规范](#提交规范)
- [测试指南](#测试指南)
- [文档贡献](#文档贡献)
- [问题反馈](#问题反馈)

## 行为准则

参与本项目的所有成员应遵守以下行为准则：

- **友善**：对所有社区成员保持友好和尊重
- **包容**：欢迎和尊重不同的观点和经验
- **协作**：积极与其他社区成员合作
- **专业**：保持专业态度，避免人身攻击
- **坦诚**：对问题和错误保持坦诚态度

## 快速开始

### Fork 仓库

1. 点击 GitHub 页面右上角的 **Fork** 按钮
2. 克隆你的 Fork 到本地：

```bash
git clone https://github.com/YOUR_USERNAME/data-agent.git
cd data-agent
```

### 关联上游仓库

```bash
git remote add upstream https://github.com/original/data-agent.git
```

## 开发环境设置

### 1. 创建虚拟环境

```bash
# 使用venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 使用conda
conda create -n data-agent python=3.11
conda activate data-agent
```

### 2. 安装依赖

```bash
# 安装项目依赖
pip install -e ".[dev]"

# 或安装所有依赖
pip install -r requirements.txt
```

### 3. 配置pre-commit钩子

```bash
pip install pre-commit
pre-commit install
```

### 4. 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_chat_service.py

# 带覆盖率运行
pytest --cov=app tests/
```

## 开发流程

### 1. 创建功能分支

```bash
# 确保在最新代码基础上创建分支
git checkout main
git pull upstream main

# 创建新分支
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

### 2. 分支命名规范

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 新功能 | feature/* | feature/add-metric-filter |
| Bug修复 | fix/* | fix/sql-validation-error |
| 文档更新 | docs/* | docs/update-api-doc |
| 重构 | refactor/* | refactor/agent-nodes |
| 测试 | test/* | test/add-integration-test |

### 3. 编写代码

在编写代码时，请遵循：

- [代码规范](#代码规范)
- [提交规范](#提交规范)
- 添加适当的测试

### 4. 提交代码

```bash
# 查看修改状态
git status

# 添加修改的文件
git add .

# 提交（遵循提交规范）
git commit -m "feat: add new metric recall node"

# 推送到你的Fork
git push origin feature/your-feature-name
```

### 5. 创建Pull Request

1. 在 GitHub 上打开你的 Fork 仓库
2. 点击 **Compare & pull request** 按钮
3. 填写 PR 描述：
   - 标题：简洁描述改动内容
   - 正文：详细说明改动原因、影响范围、相关issue等
4. 确保所有检查通过
5. 提交 PR

## 代码规范

### Python代码规范

本项目遵循 **PEP 8** 规范，并使用以下工具进行代码质量控制：

#### 格式化

使用 `ruff` 进行代码格式化：

```bash
# 格式化所有Python文件
ruff format .

# 检查格式化
ruff format --check .
```

#### 代码检查

```bash
# 运行所有检查
ruff check .

# 自动修复可修复的问题
ruff check --fix .
```

#### 类型检查

使用 `pyright` 进行静态类型检查：

```bash
pyright app/
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块 | 小写下划线 | `chat_service.py` |
| 类 | 大驼峰 | `MetaKnowledgeService` |
| 函数 | 小写下划线 | `build_meta_knowledge` |
| 常量 | 大写下划线 | `MAX_EMBEDDING_BATCH_SIZE` |
| 变量 | 小写下划线 | `table_infos` |

### 导入规范

```python
# 标准库
import os
import sys
from pathlib import Path

# 第三方库
from fastapi import APIRouter
from langgraph.graph import StateGraph

# 本地导入
from app.service.meta_knowledge_service import MetaKnowledgeService
```

### 异步编程规范

```python
# 推荐：使用async/await
async def fetch_data():
    result = await client.fetch()
    return result

# 避免：不要在异步函数中使用阻塞调用
async def bad_example():
    # 错误：使用阻塞的requests库
    response = requests.get(url)  # 不要这样做
```

## 提交规范

### 提交信息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug修复 |
| docs | 文档更新 |
| style | 代码格式（不影响功能） |
| refactor | 重构（不是新功能或bug修复） |
| test | 添加测试 |
| chore | 构建过程或辅助工具变更 |

### Scope 影响范围

| 范围 | 说明 |
|------|------|
| agent | Agent相关 |
| api | API接口 |
| service | 服务层 |
| repository | 数据访问层 |
| config | 配置相关 |
| db | 数据库相关 |

### 示例

```
feat(agent): add metric recall node

Add a new node to recall metric information from Qdrant vector database
based on user query keywords.

Closes #123
```

```
fix(validate_sql): correct SQL syntax validation

When SQL contains subqueries, the validation regex incorrectly flagged
valid SQL as invalid. This fix updates the validation pattern.

Fixes #456
```

## 测试指南

### 测试结构

```
tests/
├── unit/                    # 单元测试
│   ├── test_service/
│   └── test_repository/
├── integration/             # 集成测试
│   └── test_agent/
└── fixtures/               # 测试数据
```

### 编写测试

```python
import pytest
from app.service.meta_knowledge_service import MetaKnowledgeService

class TestMetaKnowledgeService:
    """MetaKnowledgeService单元测试"""

    @pytest.fixture
    def service(self, mock_repository):
        """测试fixture"""
        return MetaKnowledgeService(
            dw_repository=mock_repository,
            meta_repository=mock_repository
        )

    @pytest.mark.asyncio
    async def test_build_meta_knowledge(self, service, sample_config):
        """测试元数据知识库构建"""
        result = await service.build_meta_knowledge(sample_config)

        assert result is not None
        assert len(result['tables']) > 0
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 运行特定测试文件
pytest tests/unit/test_service.py::TestMetaKnowledgeService::test_build_meta_knowledge

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 文档贡献

### 文档类型

1. **API文档** (`API.md`) - API接口说明
2. **部署指南** (`DEPLOYMENT.md`) - 安装部署说明
3. **代码注释** - 复杂逻辑的注释说明
4. **README更新** - 项目主页文档

### 文档编写规范

- 使用 Markdown 格式
- 代码块标注语言
- 中文标点符号
- 适当的标题层级
- 添加示例代码

## 问题反馈

### 创建Issue

在创建Issue时，请选择适当的模板：

- **Bug Report** - 报告bug
- **Feature Request** - 功能请求
- **Question** - 问题咨询

### Issue格式

```markdown
## 问题描述
清晰描述遇到的问题

## 复现步骤
1. 执行...
2. 点击...
3. 出现...

## 预期行为
描述期望的结果

## 实际行为
描述实际的结果

## 环境信息
- OS: [e.g. macOS 14.0]
- Python版本: [e.g. 3.11.0]
- 相关版本: [e.g. 1.0.0]

## 日志
如有错误日志，请粘贴

## 截图
如有相关截图，请附上
```

## 常用命令

```bash
# 克隆仓库
git clone https://github.com/yourusername/data-agent.git

# 创建分支
git checkout -b feature/your-feature

# 查看状态
git status

# 提交代码
git commit -m "your commit message"

# 推送代码
git push origin feature/your-feature

# 更新fork
git fetch upstream
git merge upstream/main

# 运行测试
pytest

# 代码检查
ruff check .
ruff format .
```

## 联系方式

- GitHub Issues: https://github.com/yourusername/data-agent/issues
- 讨论组: https://github.com/yourusername/data-agent/discussions

## 许可

参与本项目即表示您同意以 MIT 许可证开源您的贡献。