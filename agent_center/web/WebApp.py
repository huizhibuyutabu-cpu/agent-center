from fastapi import FastAPI, Request
from starlette.responses import PlainTextResponse
from web.routers import *
from .RequestFilter import RequestFilter  # 👈 关键：引入刚才写的文件
from agent import AGENTS
from config import get_async_pg_pool, close_async_pg_pool, logger, nacos_config, config_manager
from common import *

# ========================= 创建 FastAPI 实例 =========================
app = FastAPI(
    title="Agent Center Web Server",
    description="黑马程序员智能体中心"
)

# ========================= 中间件 =========================
app.add_middleware(RequestFilter) # 👈 关键：注册中间件

# ========================= 异常处理 =========================
def system_exception_handler(req: Request, exc: Exception):
    return PlainTextResponse(
        content=str(exc),
        status_code=500
    )

app.add_exception_handler(Exception, system_exception_handler)

# ========================= Nacos 注册与注销 =========================
def register_service():
    client = nacos_config.get_discovery_client()
    ip = nacos_config.get_discovery_ip()
    service_name = nacos_config.get_discovery_name()
    port = int(config_manager.get(SERVER_PORT))
    group_name = nacos_config.get_discovery_group()

    result = client.add_naming_instance(
        service_name=service_name,
        ip=ip,
        port=port,
        group_name=group_name,
        heartbeat_interval=10
    )
    logger.info(f"✅ Registered {service_name} to Nacos: {result}")
    return result

def deregister_service():
    ip = nacos_config.get_discovery_ip()
    service_name = nacos_config.get_discovery_name()
    port = int(config_manager.get(SERVER_PORT))

    result = nacos_config.get_discovery_client().remove_naming_instance(
        service_name, ip, port
    )
    logger.info(f"🧹 Deregistered {service_name} from Nacos")
    return result

# ========================= 启动与关闭事件 =========================
async def startup():
    await get_async_pg_pool()
    for agent in AGENTS.values():
        await agent.init()
    register_service()

async def shutdown():
    await close_async_pg_pool()
    for agent in AGENTS.values():
        await agent.destroy()
    deregister_service()

app.add_event_handler("startup", startup)
app.add_event_handler("shutdown", shutdown)

# ========================= 路由注册 =========================
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(session_router, prefix="/session", tags=["session"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])