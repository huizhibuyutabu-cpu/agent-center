from agent.tianji.nodes.BaseNodeAgent import BaseNodeAgent
from agent.prompts import system_prompt_config


class IntentAgent(BaseNodeAgent):
    """
    意图识别智能体
    """

    def system_prompt(self):
        return system_prompt_config.chat_route_message

    def do_result(self, messages):
        return {"intent": messages[-1].content}