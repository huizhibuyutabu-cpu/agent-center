import asyncio
from agent.BaseAgent import BaseAgent
from agent.mcp import mcp_service
from agent.prompts import system_prompt_config
from agent.tools import pre_place_order


class BuyAgent(BaseAgent):
    """
    课程购买智能体
    """

    def system_prompt(self) -> str:
        return system_prompt_config.chat_buy_message

    def tools(self) -> list:
        # return [pre_place_order]
        tool = asyncio.run(mcp_service.get_tool("pre_place_order"))
        return [tool]

buy_agent = BuyAgent()