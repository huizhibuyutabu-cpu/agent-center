from agent.tianji.nodes.BaseNodeAgent import BaseNodeAgent
from agent.prompts import system_prompt_config

class RecommendAgent(BaseNodeAgent):
    """
    课程推荐智能体
    """

    def system_prompt(self):
        return system_prompt_config.chat_recommend_message