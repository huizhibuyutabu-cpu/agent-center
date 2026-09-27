from agent.tianji.nodes.BaseNodeAgent import BaseNodeAgent
from agent.tianji.tools import pre_place_order
from agent.prompts import system_prompt_config

class BuyAgent(BaseNodeAgent):
    """
    课程购买智能体
    """

    def system_prompt(self) -> str:
        return system_prompt_config.chat_buy_message

    def tools(self):
        return [pre_place_order]