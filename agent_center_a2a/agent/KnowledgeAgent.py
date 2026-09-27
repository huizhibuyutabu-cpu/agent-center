from agent.BaseAgent import BaseAgent
from agent.prompts import system_prompt_config


class KnowledgeAgent(BaseAgent):
    """
    知识讲解智能体
    """

    def system_prompt(self):
        return system_prompt_config.chat_knowledge_message


knowledge_agent = KnowledgeAgent()