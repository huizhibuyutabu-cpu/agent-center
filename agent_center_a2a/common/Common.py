
# 业务系统网关的微服务名称
GATEWAY_SERVICE_NAME = "gateway-service"

# ============================
# server 配置
# ============================
SERVER_LOGGER_FILE = "server.logger.file"  # 日志输出文件
SERVER_LOGGER_LEVEL = "server.logger.level"  # 日志级别

# ============================
# nacos 配置
# ============================
NACOS_SERVER_ADDR = "nacos.server-addr"  # NACOS 注册中心地址
NACOS_USERNAME = "nacos.username"  # NACOS 用户名
NACOS_PASSWORD = "nacos.password"  # NACOS 密码

NACOS_CONFIG_NAMESPACE = "nacos.config.namespace"  # NACOS 配置 namespace
NACOS_CONFIG_GROUP = "nacos.config.group"  # NACOS 配置 group

NACOS_DISCOVERY_NAME = "nacos.discovery.name"  # 服务注册名称
NACOS_DISCOVERY_NAMESPACE = "nacos.discovery.namespace"  # 服务发现 namespace
NACOS_DISCOVERY_IP = "nacos.discovery.ip"  # 服务注册 IP

# ============================
# AI OpenAI 配置
# ============================
AI_OPENAI_MODEL = "ai.openai.model"  # 模型名称
AI_OPENAI_API_KEY = "ai.openai.api-key"  # API Key
AI_OPENAI_BASE_URL = "ai.openai.base-url"  # Base URL
AI_OPENAI_TEMPERATURE = "ai.openai.temperature"  # Temperature 参数
AI_OPENAI_TIMEOUT = "ai.openai.timeout"  # 请求超时时间

# ============================
# prompt 配置
# ============================
PROMPT_RECOMMEND_CHAT_DATA_ID = "prompt.recommend.chat.data-id"
PROMPT_BUY_CHAT_DATA_ID = "prompt.buy.chat.data-id"
PROMPT_CONSULT_CHAT_DATA_ID = "prompt.consult.chat.data-id"
PROMPT_KNOWLEDGE_CHAT_DATA_ID = "prompt.knowledge.chat.data-id"
PROMPT_UNKNOWN_CHAT_DATA_ID = "prompt.unknown.chat.data-id"
PROMPT_TEXT_CHAT_DATA_ID = "prompt.text.chat.data-id"
PROMPT_A2A_CHAT_DATA_ID = "prompt.a2a.chat.data-id"