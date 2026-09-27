import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain_mcp_adapters.tools import ToolCallInterceptor

from config import config_manager, logger


class ParamsInterceptor(ToolCallInterceptor):

    async def __call__(self, request: MCPToolCallRequest, handler):
        """ MCP 请求拦截器，用于在原请求参数中设置业务参数 """

        # 复制原请求参数，增加params业务参数
        new_args = dict(request.args)  # 复制
        new_args["params"] = {
            "user_token": request.runtime.context.user_token,
            "request_id": request.runtime.context.request_id
        }

        # 覆盖请求对象中的参数
        new_request = request.override(args=new_args)

        # 执行MCP远程工具
        return await handler(new_request)


class MCPService:
    """
    封装MCP服务的客户端
    """

    def __init__(self):
        servers_config = {}
        for item in config_manager.get("mcp-servers", []):
            servers_config[item["name"]] = {
                "transport": item["transport"],
                "url": item["url"]
            }

        self.client = MultiServerMCPClient(servers_config, tool_interceptors=[ParamsInterceptor()])

    async def get_tools(self):
        """
        获取所有工具列表
        """
        return await self.client.get_tools()

    async def get_tool(self, name: str):
        """
        根据名字获取工具
        """
        try:
            tools = await self.get_tools()
        except Exception as e:
            # 记录日志或处理异常
            logger.error(f"获取工具列表失败: {str(e)}")
            return None

        for tool in tools:
            if tool.name == name:
                return tool
        return None


mcp_service = MCPService()

if __name__ == "__main__":
    # 测试代码
    tools = asyncio.run(mcp_service.get_tools())
    print(f"tools:{tools}")

    print("-"*100)

    tool = asyncio.run(mcp_service.get_tool("query_course_by_id"))
    print(f"query_course_by_id:{tool}")