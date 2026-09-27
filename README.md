# AgentCenter · 智能体中台（天机学堂 AI 助手）

在天机学堂在线学习平台（Java Spring Cloud 微服务，课程 / 题库 / 交易 / 用户等十余个业务微服务）之上构建的「学生端 AI 助手」智能体中台：为课程推荐、购买辅助、课程咨询等传统业务新增 IT 知识答疑、AI 文本创作等智能体能力，形成

```text
业务系统 → Spring Cloud 网关 → AgentCenter 智能体中台（Python，多租户）→ 子智能体 + MCP 工具 + EduRAG 检索增强
```

的完整 AI 应用链路。

## 系统架构

```text
业务系统（Spring Cloud 微服务）
        │  /acs/**
        ▼
agent-center-gateway（Spring Cloud Gateway）
        · /acs 路由 → lb://agent-center（Nacos 负载均衡，StripPrefix=1）
        · JWT 公钥鉴权（AuthFilter + JwtUtils）
        · Redis 令牌桶限流（replenishRate=10/s，burstCapacity=20，按路径解析 key）
        · Resilience4j 熔断降级（COUNT_BASED 滑窗，失败率 50% 熔断，10s 后半开放行 3 个）
        ▼
AgentCenter 智能体中台（agent_center，FastAPI + LangGraph）
        · 3 种智能体模式：路由(1001) / 文本(1002) / A2A(1003)，按 agentId 切换
        · 会话记忆：AsyncPostgresSaver Checkpointer（thread_id = 会话 ID），支持多轮状态恢复
        · SSE 流式输出 + 按会话中断生成
        · 请求来源过滤（仅网关可调用）+ JWT token 校验
        · Nacos 注册 / 注销（10s 心跳）+ 系统提示词热更新（60s 轮询 + MD5 变更检测）
        ├─ 路由模式：意图识别节点 → 推荐 / 购买 / 咨询 / 知识 / 兜底 5 个子智能体（LangGraph StateGraph）
        ├─ A2A 模式（agent_center_a2a × 5 个独立服务）：AgentCard 能力发现 + Task 任务模型 + SSE 流式，
        │   主 Agent 作为 A2A 客户端经 JSON-RPC 调用子 Agent 并汇总结果，多进程部署、独立扩缩容
        ├─ MCP 工具（agent_center_mcp，FastMCP streamable-http）：课程查询 / 预下单 / RAG 检索 3 个工具，
        │   工具内经 Nacos 服务发现调用 EduRAG 网关实例并随机分散负载；
        │   客户端基于 langchain-mcp-adapters，用 ToolCallInterceptor 自动注入 user_token / request_id 完成鉴权透传
        └─ EduRAG 检索增强（独立仓库）：平台课程数据导入 Milvus（BGE-M3 向量化），
            混合检索 + bge-reranker-large 精排（k=5 → m=2），推荐智能体先检索真实课程数据再调课程详情工具
```

## 目录结构

```
├── agent_center/          # AgentCenter 主服务（智能体中台，FastAPI + LangGraph + Nacos）
│   ├── agent/tianji/      # 路由智能体：意图识别 + 5 个子智能体（LangGraph StateGraph）
│   ├── agent/tja2a/       # A2A 客户端：主 Agent 调用 5 个 A2A 子服务并汇总结果
│   ├── web/               # FastAPI 路由（鉴权 / 对话 / 会话）+ 请求来源过滤中间件
│   ├── config/            # Nacos 注册发现 + 配置中心（提示词热更新）
│   ├── dao/ vo/           # 会话 / 应用数据访问（PostgreSQL 会话记忆）
│   ├── sql/               # 数据库脚本
│   └── main.py            # 服务入口（uvicorn 异步）
├── agent_center_a2a/      # A2A 子智能体服务 × 5（推荐 / 购买 / 咨询 / 知识 / 兜底，多进程独立部署）
│   ├── app/               # 各子 Agent 的 A2A 应用（AgentCard + 执行器）
│   ├── executor/          # MyExecutor：Task 事件流推送 + 工具结果回传
│   └── main.py            # 服务入口
├── agent_center_mcp/      # MCP 工具服务（FastMCP，streamable-http 传输）
│   ├── tools/             # 课程查询 / 预下单 / RAG 检索 3 个工具
│   └── main.py            # 服务入口（AgentCenterServer）
├── agent-center-gateway/  # Spring Cloud Gateway 网关（Java，JDK 17+ / Spring Boot 3.3.5）
│   └── src/main/java/com/agent/center/
│       ├── filter/        # JWT 鉴权过滤器
│       ├── limiter/       # 限流 key 解析器
│       ├── fallback/      # 熔断降级
│       └── util/          # JWT 工具
└── integrated_qa_system/  # EduRAG 检索增强系统（已单独开源，见下方「相关项目」）
```

## 核心设计

- **路由智能体（LangGraph StateGraph）**：意图识别节点将请求条件路由到 5 个子智能体；
  AsyncPostgresSaver Checkpointer 实现会话级记忆（thread_id = 会话 ID），支持多轮状态恢复与历史会话还原；SSE 流式输出并支持按会话中断生成。
- **A2A 多智能体架构**：5 个子智能体拆分为独立 A2A 服务（a2a-sdk：AgentCard 能力发现 + Task 任务模型 + SSE 流式事件），多进程部署、独立扩缩容；主 Agent 作为 A2A 客户端经 JSON-RPC 调用子 Agent 并汇总结果。
- **MCP 工具服务**：FastMCP（streamable-http 传输）封装课程查询、预下单、RAG 检索 3 个工具；工具内经 Nacos 服务发现定位 EduRAG 实例并随机分散负载；客户端拦截器自动注入鉴权参数，实现 token 透传。
- **Agentic RAG**：推荐智能体先经 RAG 工具检索 Milvus 中的真实课程数据（混合检索 + 精排，k=5 → m=2）再调用课程详情工具，替代大模型「编造推荐」。
- **服务治理**：AgentCenter 与 RAG 服务经 Nacos 注册 / 注销（10s 心跳）；7 份系统提示词存 Nacos，60s 轮询 + MD5 变更检测实现热更新；FastAPI 中间件校验请求来源（仅网关可调用）与 JWT token。
- **网关层**：/acs 路由负载均衡、JWT 公钥鉴权、Redis 令牌桶限流（replenishRate=10/s、burstCapacity=20）、Resilience4j 熔断降级。

## 量化指标

| 指标 | 数值 |
| --- | --- |
| 智能体模式 | 3 种（路由 / 文本 / A2A），agentId 切换，会话管理与网关体系复用 |
| A2A 子智能体 | 5 个独立服务，多进程部署 |
| 系统提示词 | 7 份存 Nacos，热更新轮询周期 60s（MD5 变更检测） |
| Nacos 心跳 | 注册 / 注销 10s 心跳 |
| 限流验证（JMeter） | 25 并发：20 个通过、5 个返回 429（令牌桶 10/s + 容量 20 生效） |
| RAG 检索 | 混合检索 k=5 → bge-reranker-large 精排 m=2 |

## 职责划分

- Python 侧（`agent_center` / `agent_center_a2a` / `agent_center_mcp`）：独立完成。
- Java 网关（`agent-center-gateway`）：熟悉级 / 参与（路由、限流、熔断配置与联调）。

## 快速开始

### 1. 依赖

```bash
# Python 服务（agent_center / agent_center_a2a / agent_center_mcp）
conda env create -f agent_center/environment.yml

# Java 网关（JDK 17+，Maven）
cd agent-center-gateway && mvn spring-boot:run
```

### 2. 配置

各服务根目录的 `application.yml` 中敏感值均为占位符（`your-mysql-user` / `your-nacos-username` / `your-dashscope-api-key` 等），
按注释填入自己的 MySQL / PostgreSQL / Redis / Nacos / DashScope 配置。

### 3. 启动顺序

1. 启动 Nacos 注册中心（默认 `127.0.0.1:8848`）
2. `python agent_center/main.py`（智能体中台，注册名 agent-center）
3. `python agent_center_mcp/main.py`（MCP 工具服务）
4. `python agent_center_a2a/main.py`（5 个子智能体自动以多进程启动，占用 3601-3605 端口）
5. EduRAG 检索服务：见 [integrated-qa-system](https://github.com/your-github-username/integrated-qa-system)
6. 网关：`cd agent-center-gateway && mvn spring-boot:run`（/acs 入口，端口 10086）

## 相关项目

- **EduRAG 企业知识库智能问答系统**（RAG 检索增强能力提供方，三级级联管道 + 混合检索 + BERT 意图分类）：
  [integrated-qa-system](https://github.com/your-github-username/integrated-qa-system)
- 业务侧新增的 `tj-aigc` 对话微服务（SSE 流式聊天、会话管理，经 Nacos + Feign 与中台集成）属于公司业务代码，不在本仓库内。

## 许可证

[MIT](LICENSE)

