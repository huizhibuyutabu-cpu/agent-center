from agent.BaseAgent import BaseAgent
from agent.prompts import system_prompt_config
from agent.tools import query_course_by_id
import asyncio
from agent.mcp import mcp_service

class RecommendAgent(BaseAgent):
    """
    课程推荐智能体
    """

    def system_prompt(self):
        return system_prompt_config.chat_recommend_message

    def tools(self) -> list:
        # return [query_course_by_id]
        course_tool = asyncio.run(mcp_service.get_tool("query_course_by_id"))
        recommend_tool = asyncio.run(mcp_service.get_tool("query_recommend_data"))
        return [course_tool,recommend_tool]

recommend_agent = RecommendAgent()