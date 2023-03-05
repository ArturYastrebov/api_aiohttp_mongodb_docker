import os

from aiohttp import web
from aiohttp_session import SimpleCookieStorage, session_middleware
from aiohttp_security import setup as setup_security, SessionIdentityPolicy
from aiohttp_security.abc import AbstractAuthorizationPolicy
from API_aiohttp.db import users_collection
from API_aiohttp.routes import setup_routes


class SimpleJack_AuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity: str) -> str:
        user = await users_collection.find_one({"name": identity})
        return user["_id"] if user else None

    async def permits(self, identity: str, permission: str, context: str = None) -> bool:
        users = users_collection.find()
        user_names = [user.get("name") async for user in users if user.get("name")]
        allowed_permissions = [
            "do_short_url",
        ]
        return identity in user_names and permission in allowed_permissions


async def make_app() -> web.Application:
    middleware = session_middleware(SimpleCookieStorage())
    app = web.Application(middlewares=[middleware])
    setup_routes(app)
    policy = SessionIdentityPolicy()
    setup_security(app, policy, SimpleJack_AuthorizationPolicy())
    return app


if __name__ == "__main__":
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 8000))
    web.run_app(make_app(), host=host, port=port)
