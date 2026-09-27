import asyncio
from mcp.server.fastmcp import FastMCP
from tools import register_all_tools
from config import config_manager

# 创建 MCP 服务实例
mcp = FastMCP(
    name="AgentCenterServer",
    port=config_manager.get("server.port", 8000),
)

# 注册所有工具
register_all_tools(mcp)

# 列出所有工具
tools = asyncio.run(mcp.list_tools())
for tool in tools:
    print(f"Registered tool: {tool.name}")

if __name__ == "__main__":
    mcp.run(transport="streamable-http")