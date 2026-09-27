from abc import ABC, abstractmethod
from collections.abc import AsyncIterable
from typing import Any

from a2a.types import Message
from a2a.utils import get_message_text
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from config import config_manager, logger
from agent.result.ToolContext import ToolContext

class BaseAgent(ABC):

    def __init__(self, provider: str = "openai"):
        """
        初始化 Agent（加载模型、构建 LangChain Agent）。

        参数:
            provider (str): 模型提供方标识，对应配置项 ai.<provider>.*

        自动加载配置项：
            ai.<provider>.model
            ai.<provider>.api-key
            ai.<provider>.base-url
            ai.<provider>.temperature
            ai.<provider>.timeout
        """
        cfg = config_manager
        prefix = f"ai.{provider}"

        # 基本模型配置
        self.model_name = cfg.get(f"{prefix}.model")
        self.api_key = cfg.get(f"{prefix}.api-key")
        self.base_url = cfg.get(f"{prefix}.base-url")
        self.temperature = float(cfg.get(f"{prefix}.temperature", 0.7))
        self.timeout = int(cfg.get(f"{prefix}.timeout", 60))

        # 初始化 LLM（统一走 OpenAI 风格 API）
        self.llm = init_chat_model(
            model=self.model_name,
            model_provider="openai",  # 所有模型按 OpenAI schema 统一封装
            api_key=self.api_key,
            base_url=self.base_url,
            temperature=self.temperature,
            timeout=self.timeout
        )

        # 创建 LangChain enhanced agent（支持工具调用 + 上下文）
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools(),  # 工具由子类决定
            context_schema=ToolContext  # 自定义上下文，用于跨工具传递信息
        )

    @abstractmethod
    def system_prompt(self) -> str:
        """
        返回系统提示词（必须由子类实现）。
        通常用于定义 Agent 的角色、行为规则、语气等。
        """
        pass

    def tools(self) -> list:
        """
        返回智能体可使用的工具列表。
        默认无工具，子类可覆盖实现。
        """
        return []

    def system_prompt_params(self):
        """
        返回用于格式化 system_prompt 的动态参数（可选）。
        子类如需参数化 system_prompt，可以覆盖本方法。
        """
        return {}

    async def execute(self, message: Message) -> AsyncIterable[dict[str, Any]]:
        """执行智能体，并以流式方式（async generator）返回模型输出。"""

        # 读取输入文本
        input_text = get_message_text(message)

        # 解析历史聊天记录，构造 LangChain Message 列表
        history = message.metadata.get("history", [])
        history_messages = []
        for msg in history:
            if msg.get("type") == "USER":
                history_messages.append(HumanMessage(msg.get("content")))
            elif msg.get("type") == "ASSISTANT":
                history_messages.append(AIMessage(msg.get("content")))

        # 构建完整 Prompt
        prompts = [
            *history_messages,
            SystemMessage(self.system_prompt().format(**self.system_prompt_params())),
            HumanMessage(input_text)
        ]

        # 从 message.metadata 中读取上下文参数
        user_token = message.metadata.get("user_token", "")
        request_id = message.metadata.get("request_id", "")

        try:
            # 启动流式生成
            res = self.agent.astream(
                input={"messages": prompts},
                stream_mode="messages",  # 按消息流式产出 AIMessage
                context=ToolContext(
                    user_token=user_token,
                    request_id=request_id
                )
            )

            # 逐条流式返回内容
            async for chunk, metadata in res:
                # chunk 可能为工具事件或 AIMessage，需要判断处理
                if isinstance(chunk, AIMessage) and hasattr(chunk, "content") and chunk.content:
                    yield {"content": chunk.content, "done": False, "tool": False}
                elif isinstance(chunk, ToolMessage):
                    yield {"content": chunk.content, "done": False, "tool": True, "name": chunk.name}

            # 正常结束
            yield {"content": "", "done": True}
        except Exception as e:
            logger.error("LLM execute error", exc_info=True)

            # 错误场景也返回 done=True
            yield {
                "content": "处理请求时出错。",
                "done": True
            }