import asyncio
import random

import aiohttp_session
import bcrypt
import pytest_asyncio
from aiohttp_security import setup as setup_security, SessionIdentityPolicy, remember, forget, is_anonymous

import pytest
from aiohttp import web
from aiohttp_session import session_middleware, SimpleCookieStorage
from pytest_aiohttp.plugin import aiohttp_client

from API_aiohttp.routes import setup_routes
from API_aiohttp.db import users_collection
from API_aiohttp.main import SimpleJack_AuthorizationPolicy


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.get_event_loop()


@pytest_asyncio.fixture()
async def client(aiohttp_client):
    middleware = session_middleware(SimpleCookieStorage())
    app = web.Application(middlewares=[middleware])
    setup_routes(app)
    policy = SessionIdentityPolicy()
    setup_security(app, policy, SimpleJack_AuthorizationPolicy())
    return aiohttp_client(app)


@pytest.fixture(scope="function")
def user_create(request: web.Request):
    salt = bcrypt.gensalt()
    rehashed_password = bcrypt.hashpw("test_hashed_password".encode("utf-8"), salt)
    user = {"name": "test_user_name", "salt": salt, "password": rehashed_password}
    users_collection.insert_one(user)
    remember(request, web.HTTPFound("/"), identity=user["name"])
    yield user
    forget(request, web.HTTPFound("/"))
    users_collection.delete_one({"name": user["name"]})


@pytest_asyncio.fixture
async def session_create(client):
    client = await client
    username, password = "test_user_name", "test_hashed_password"
    data = {"username": username, "password": password}
    await client.post("/login", data=data)


data_registrations = [
    ("new_user_name", "wrong_pass", "test_hashed_password", 'id="error_registration">Your passwords are not the same'),
    (
        "test_user_name",
        "test_hashed_password",
        "test_hashed_password",
        'id="error_registration">The database already has such a nickname',
    ),
    ("new_user_name", "test_hashed_password", "test_hashed_password", "<title>Short url</title>"),
]


def func_ids(some_datas):
    # return f'{some_data[0]} + {some_data[1]} == {some_data[2]}'
    return [some_data[3] for some_data in some_datas]


@pytest.fixture(params=data_registrations, ids=func_ids(data_registrations))
def create_registration_data(request, user_create):
    yield request.param
    users_collection.delete_one({"name": request.param[0]})
