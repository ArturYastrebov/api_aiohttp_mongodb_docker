from aiohttp import web
from aiohttp_session import SimpleCookieStorage, session_middleware
from aiohttp_security import setup as setup_security, SessionIdentityPolicy
from aiohttp_security.abc import AbstractAuthorizationPolicy
from API_aiohttp.db import users_collection
from API_aiohttp.routes import setup_routes


class SimpleJack_AuthorizationPolicy(AbstractAuthorizationPolicy):

    async def authorized_userid(self, identity: str) -> str:
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        user = await users_collection.find_one({'name': identity})
        return user['_id'] if user else None

    async def permits(self, identity: str, permission: str, context: str = None) -> bool:
        """Check user permissions.
        Return True if the identity is allowed the permission
        in the current context, else return False.
        """
        users = users_collection.find()
        user_list = [user.get('name') async for user in users if user.get('name')]
        permission_list = ['do_short_url', ]
        return identity in user_list and permission in permission_list


async def make_app() -> web.Application:
    # make app
    middleware = session_middleware(SimpleCookieStorage())
    app = web.Application(middlewares=[middleware])

    # add the routes
    setup_routes(app)

    # set up policies
    policy = SessionIdentityPolicy()
    setup_security(app, policy, SimpleJack_AuthorizationPolicy())

    return app


if __name__ == '__main__':
    web.run_app(make_app(), port=9000)
