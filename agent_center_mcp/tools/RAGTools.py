import random
from mcp.server.fastmcp import FastMCP

from config import logger, config_manager, nacos_config
from util import HttpClientUtil, JsonUtil
from common import *

async def query_recommend_data(query_text: str, params: dict = None):
    """
    根据用户提供的需求查询相关的课程数据，基于此课程数据进行推荐
    Args:
        query_text : 查询字符串，如："本科，3年，对java感兴趣，没有编程经验"
        params : 自定义的一些参数
    """
    # 获取必要的配置数据
    if params is None:
        params = {}
    token = params.get("user_token", "")

    # 获取网关实例
    instances = nacos_config.get_discovery_client().list_naming_instance(EDU_RAG_SERVICE_NAME).get("hosts", [])
    if not instances:
        logger.error("No gateway-service instances found")
        return None

    # 随机选择一个实例发起请求，分散负载
    instance = random.choice(instances)
    url = f"http://{instance['ip']}:{instance['port']}/query"
    request_param = {
        "query_text": query_text,
        "m": config_manager.get("rag.m", 2),
        "k": config_manager.get("rag.k", 5),
    }
    # 发起 HTTP POST 请求获取RAG数据
    response_data = HttpClientUtil.post(url, token, json=request_param) or {}
    data = response_data.get("data")
    if not data:
        logger.error(f"Failed to fetch course data from {url}")
        return None

    logger.debug("【Tool】 query_recommend_data url=%s, query_text=%s, data=%s, ", url, query_text, data)

    # 将结果序列化json，返回给大模型
    return JsonUtil.to_str(data)


def register(mcp: FastMCP):
    mcp.tool()(query_recommend_data)