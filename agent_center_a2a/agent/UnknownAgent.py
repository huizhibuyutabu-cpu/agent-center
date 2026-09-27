from agent.BaseAgent import BaseAgent
from agent.prompts import system_prompt_config


class UnknownAgent(BaseAgent):
    """
    未知意图智能体
    """

    def system_prompt(self):
        return system_prompt_config.chat_unknown_message


unknown_agent = UnknownAgent()