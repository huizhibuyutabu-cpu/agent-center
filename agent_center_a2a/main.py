import uvicorn
import multiprocessing

from app.BaseApp import BaseApp
from config import logger
from app import *

# 定义需要启动的所有 A2A 应用实例，每个应用实现了 BaseApp 接口
APPS = [
    recommend_app,
    buy_app,
    consult_app,
    knowledge_app,
    unknown_app
]


def main():
    """
    主入口函数。
    作用：
        1. 遍历 APPS 列表，为每个子应用创建独立的进程。
        2. 启动每个进程对应的服务。
        3. 等待所有子进程结束（一般不会结束，除非异常或手动停止）。
    """
    processes = []

    # 为每一个 App 启动独立进程，保证服务之间互不影响
    for app in APPS:
        proc = multiprocessing.Process(target=start, args=[app])
        proc.start()  # 异步启动子进程
        processes.append(proc)

    # 等待所有子进程结束
    for proc in processes:
        proc.join()


def start(app: BaseApp):
    """
    启动单个应用服务。

    参数:
        app (BaseApp): 继承自 BaseApp 的服务实例，必须实现：
            - app_type(): 返回服务名称
            - port(): 返回绑定端口
            - host(): 返回绑定 IP
            - server(): 返回最终用于 uvicorn.run 的 server 对象

    功能：
        1. 输出启动日志。
        2. 使用 uvicorn 启动对应 FastAPI/A2A 服务。
    """
    logger.info(f"启动服务【{app.app_type()}】，监听端口：{app.port()}")

    # uvicorn 运行时构建应用，并设置 host、port 等基础参数
    uvicorn.run(
        app.server().build(),
        host=app.host(),
        port=app.port(),
        access_log=False  # 关闭 uvicorn 的 access log，使用自己项目的日志体系
    )


if __name__ == "__main__":
    # 项目的主入口，当以脚本方式运行时，启动所有 App 服务
    main()