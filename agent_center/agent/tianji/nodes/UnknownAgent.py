from agent.tianji.nodes.BaseNodeAgent import BaseNodeAgent
from agent.prompts import system_prompt_config

class UnknownAgent(BaseNodeAgent):
    """
    未知意图智能体（兜底智能体）
    """

    def system_prompt(self) -> str:
        return system_prompt_config.chat_unknown_message