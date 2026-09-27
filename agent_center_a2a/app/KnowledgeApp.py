from a2a.server.agent_execution import AgentExecutor

from app.BaseApp import BaseApp
from executor.MyExecutor import MyExecutor
from agent import knowledge_agent

class KnowledgeApp(BaseApp):
    """
    知识讲解应用
    """

    def app_type(self):
        return "knowledge"

    def agent_executor(self) -> AgentExecutor:
        return MyExecutor(knowledge_agent)


knowledge_app = KnowledgeApp()