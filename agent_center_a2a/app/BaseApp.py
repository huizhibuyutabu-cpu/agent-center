from abc import ABC, abstractmethod

from a2a.server.agent_execution import AgentExecutor
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities

from config import config_manager


class BaseApp(ABC):
    """
    抽象类，所有 App 服务的基类。
    """

    @abstractmethod
    def app_type(self):
        """
        返回应用类型（字符串）。
        """

    @abstractmethod
    def agent_executor(self) -> AgentExecutor:
        """
        返回智能体执行器（实现 execute/cancel）。
        每个具体 App 将返回适配自身业务逻辑的 AgentExecutor。
        """

    def agent_card(self) -> AgentCard:
        """构建并返回当前 App 的 AgentCard（智能体卡片）。"""
        app_type = self.app_type()

        # 从配置中读取技能列表并构造成 AgentSkill 对象
        skills_config = config_manager.get(f'app.{app_type}.skills', [])
        skills = [AgentSkill(**skill) for skill in skills_config]

        return AgentCard(
            name=config_manager.get(f'app.{app_type}.card.name'),
            description=config_manager.get(f'app.{app_type}.card.description'),
            url=f"http://{config_manager.get(f'app.{app_type}.card.host')}:{self.port()}/",
            version=config_manager.get(f'app.{app_type}.card.version'),
            default_input_modes=['text'],  # 默认只支持文本输入
            default_output_modes=['text'],  # 默认只输出文本
            capabilities=AgentCapabilities(
                streaming=True  # 默认支持流式输出
            ),
            skills=skills,  # 配置的技能
        )

    def http_handler(self) -> DefaultRequestHandler:
        """构建请求处理器。"""

        return DefaultRequestHandler(
            agent_executor=self.agent_executor(),
            task_store=InMemoryTaskStore(),  # 默认使用内存存储任务状态
        )

    def host(self) -> str:
        """返回服务监听 IP。"""
        app_type = self.app_type()
        return config_manager.get(f'app.{app_type}.host', '0.0.0.0')

    def port(self) -> int:
        """返回服务监听端口。 默认端口：3600"""
        app_type = self.app_type()
        return int(config_manager.get(f'app.{app_type}.port', 3600))

    def server(self):
        """构建 A2AStarletteApplication 服务实例。"""

        return A2AStarletteApplication(
            agent_card=self.agent_card(),
            http_handler=self.http_handler()
        )