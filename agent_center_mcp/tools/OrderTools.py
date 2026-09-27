import random

from mcp.server import FastMCP

from common import *
from config import nacos_config, logger
from tools.result import PrePlaceOrder
from util import HttpClientUtil, JsonUtil

"""
流程：
    1. 从 params 获取用户 token 和 request_id
    2. 通过 Nacos 获取业务系统网关实例列表
    3. 随机选择一个实例发起 HTTP 请求完成预下单
    4. 将返回结果转换为 PrePlaceOrder 对象
    5. 序列化json返回
"""


def pre_place_order(course_ids: list, params: dict = None):
    """
    课程购买预下单工具函数。

    Args:
        course_ids (list): 课程 ID 列表
        params : 自定义的一些参数
    """
    # 获取必要的配置数据
    if params is None:
        params = {}
    token = params.get("user_token", "")
    request_id = params.get("request_id", "")

    # 强制将所有元素转为字符串
    course_ids = [str(cid) for cid in course_ids]

    # 获取网关实例
    instances = nacos_config.get_discovery_client().list_naming_instance(GATEWAY_SERVICE_NAME).get("hosts", [])
    if not instances:
        logger.error("No gateway-service instances found")
        return None

    # 随机选择一个实例发起请求，分散负载
    instance = random.choice(instances)
    url = f"http://{instance['ip']}:{instance['port']}/ts/orders/prePlaceOrder"

    # 发起 GET 请求，并传递 courseIds 参数
    response_data = HttpClientUtil.get(url, token, params={"courseIds": ",".join(course_ids)}) or {}
    data = response_data.get("data")
    if not data:
        logger.error(f"预下单失败，url={url}, courseIds={course_ids}")
        return None

    logger.debug("【Tool】 pre_place_order url=%s, data=%s, request_id=%s", url, data, request_id)

    # 转换为 PrePlaceOrder 对象
    order = PrePlaceOrder.of(data)

    # 将结果序列化json，返回给大模型
    return JsonUtil.to_str(order)

def register(mcp: FastMCP):
    mcp.tool()(pre_place_order)