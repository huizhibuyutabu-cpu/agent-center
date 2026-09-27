from a2a.server.agent_execution import AgentExecutor

from app.BaseApp import BaseApp
from executor.MyExecutor import MyExecutor
from agent import unknown_agent


class UnknownApp(BaseApp):
    """
    未知意图应用
    """

    def app_type(self):
        return "unknown"

    def agent_executor(self) -> AgentExecutor:
        return MyExecutor(unknown_agent)


unknown_app = UnknownApp()