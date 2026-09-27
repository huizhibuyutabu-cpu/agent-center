import random

from langchain.tools import tool, ToolRuntime

from agent.tianji.tools.result import PrePlaceOrder
from common import *
from config import logger
from util import HttpClientUtil, JsonUtil

"""
流程：
    1. 从 RunnableConfig 获取用户 token 和 request_id
    2. 通过 Nacos 获取业务系统网关实例列表
    3. 随机选择一个实例发起 HTTP 请求完成预下单
    4. 将返回结果转换为 PrePlaceOrder 对象
    5. 序列化json返回
"""


@tool
def pre_place_order(course_ids: list, runtime: ToolRuntime):
    """
    课程购买预下单工具函数。

    Args:
        course_ids (list): 课程 ID 列表
        runtime: 获取运行参数
    """
    # 强制将所有元素转为字符串
    course_ids = [str(cid) for cid in course_ids]

    # 获取必要的配置数据
    user_token = runtime.context.user_token
    request_id = runtime.context.request_id

    # TODO 从 Nacos 获取业务系统网关实例
    url = f"http://127.0.0.1:10010/ts/orders/prePlaceOrder"

    # 发起 GET 请求，并传递 courseIds 参数
    response_data = HttpClientUtil.get(url, user_token, params={"courseIds": ",".join(course_ids)}) or {}
    data = response_data.get("data")
    if not data:
        logger.error(f"预下单失败，url={url}, courseIds={course_ids}")
        return None

    logger.debug("【Tool】 pre_place_order url=%s, data=%s, request_id=%s", url, data, request_id)

    # 转换为 PrePlaceOrder 对象
    order = PrePlaceOrder.of(data)

    # 将结果序列化json，返回给大模型
    return JsonUtil.to_str(order)