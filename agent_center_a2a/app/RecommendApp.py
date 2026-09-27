from a2a.server.agent_execution import AgentExecutor

from app.BaseApp import BaseApp
from executor.MyExecutor import MyExecutor
from agent import recommend_agent

class RecommendApp(BaseApp):
    """
    课程推荐应用
    """

    def app_type(self):
        return "recommend"

    def agent_executor(self) -> AgentExecutor:
        return MyExecutor(recommend_agent)


recommend_app = RecommendApp()