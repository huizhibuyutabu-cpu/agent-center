from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from config import config_manager, logger
from util import JWTUtil

# ========================= 不需要校验 JWT 的 URL 列表 =========================
no_check_list = [
    "/auth/token",
    "/docs",
    "/openapi.json"
]

class RequestFilter(BaseHTTPMiddleware):
    """JWT 验证中间件，负责请求来源和 token 的校验"""

    def __init__(self, app):
        self.public_key = config_manager.get("jwt.public_key")
        super().__init__(app)

    def verify_token(self, token: str) -> bool:
        try:
            decoded = JWTUtil.verify_token(token, self.public_key)
            return decoded is not None
        except Exception as e:
            logger.error(e)
            return False

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        logger.debug(f"【RequestFilter】接收到请求路径，path = {path}")

        if path in no_check_list:
            return await call_next(request)

        request_from = request.headers.get("request-from")
        if request_from != "agent-center-gateway":
            return Response(
                status_code=401,
                content="请求只能通过网关转发，不能直接访问！"
            )

        token = request.headers.get("token")
        if not token:
            return Response(
                status_code=401,
                content="请求中缺少 token ！"
            )

        if not self.verify_token(token):
            return Response(
                status_code=401,
                content="token 已失效！"
            )

        return await call_next(request)