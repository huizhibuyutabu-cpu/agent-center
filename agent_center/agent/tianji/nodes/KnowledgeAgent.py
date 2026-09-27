from agent.tianji.nodes.BaseNodeAgent import BaseNodeAgent
from agent.prompts import system_prompt_config

class KnowledgeAgent(BaseNodeAgent):
    """
    知识讲解智能体
    """
    def system_prompt(self):
        return system_prompt_config.chat_knowledge_message