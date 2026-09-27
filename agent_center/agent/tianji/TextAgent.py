from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
from agent.BaseAgent import *
from agent.prompts import system_prompt_config
from config import config_manager, logger
from typing import Optional


class TextAgent(BaseAgent):
    """
    TextAgent：通用文本生成智能体（非路由型）。

    功能：
    - 纯粹执行系统提示词 + 用户输入
    - 不依赖多节点 Graph，不需要状态管理
    - 使用 LangChain agent.stream 实现流式输出
    - 适用于通用文本解释、随问随答等简单场景
    """

    def __init__(self, provider: str = "openai"):
        self.provider = provider
        self.llm: Optional[BaseChatModel] = None  # LLM 实例
        self.agent: Optional[BaseAgent] = None  # LangChain agent 实例

    async def init(self):
        """
        初始化 TextAgent：
        1. 从配置读取模型参数
        2. 创建 LLM 实例
        3. 创建 LangChain Agent（无工具）
        """
        cfg = config_manager
        prefix = f"ai.{self.provider}"

        # 加载模型配置
        model_name = cfg.get(f"{prefix}.model")
        api_key = cfg.get(f"{prefix}.api-key")
        base_url = cfg.get(f"{prefix}.base-url")
        temperature = float(cfg.get(f"{prefix}.temperature", 0.7))
        timeout = int(cfg.get(f"{prefix}.timeout", 60))

        # 初始化 LLM（统一走 openai-compatible 接口）
        self.llm = init_chat_model(
            model=model_name,
            model_provider="openai",
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            timeout=timeout
        )

        # 创建一个无工具的通用智能体
        self.agent = create_agent(
            model=self.llm
        )

    async def execute(self, question: str, session_id: str, user_token: str) -> AsyncIterable[str]:
        """
        TextAgent 的主执行方法：

        流程：
        1. 构建 SystemMessage + HumanMessage
        2. 调用 agent.stream 产生流式生成内容
        3. 逐段转换为 SSE 事件推送至前端
        4. 不参与会话状态保存（无 checkpointer）
        """
        try:
            # System + 用户消息结构
            prompts = [
                SystemMessage(system_prompt_config.chat_text_message),
                HumanMessage(question)
            ]

            # 流式生成，返回 (token, metadata)
            res = self.agent.stream(
                input={"messages": prompts},
                stream_mode="messages"  # 以 message token 形式流式返回
            )

            # 输出内容 token
            for token, metadata in res:
                if token.content:
                    yield make_sse_event(1001, token.content)

        except Exception as e:
            # 捕获并打印异常，不终止 SSE 流
            logger.error(f"❌ TextAgent Error: {e}")
            yield make_sse_event(2001, str(e))

        # 推送 SSE 停止事件，表示内容发送完毕
        yield format_sse_data(STOP_EVENT)

    def id(self) -> int:
        """TextAgent 的唯一 ID，用于系统标识"""
        return 1002

    # --- 以下两个方法 TextAgent 不支持，会话不需要状态保存 ---
    def session_detail(self, user_id: int, session_id: str) -> list:
        """TextAgent 不进行会话持久化，因此无需实现 session_detail"""
        raise NotImplementedError("暂不提供实现.")

    def delete_session(self, session_id: str):
        """TextAgent 不具备持久化能力，因此无需删除会话"""
        raise NotImplementedError("暂不提供实现.")


# 全局 TextAgent 实例
text_agent = TextAgent()