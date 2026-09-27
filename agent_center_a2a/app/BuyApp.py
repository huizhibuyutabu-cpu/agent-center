from a2a.server.agent_execution import AgentExecutor

from app.BaseApp import BaseApp
from executor.MyExecutor import MyExecutor
from agent import buy_agent


class BuyApp(BaseApp):
    """
    课程购买应用
    """

    def app_type(self):
        return "buy"

    def agent_executor(self) -> AgentExecutor:
        return MyExecutor(buy_agent)


buy_app = BuyApp()