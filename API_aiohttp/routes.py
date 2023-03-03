import os
import aiohttp_session
import bcrypt
from aiohttp import web
from aiohttp_security import is_anonymous, forget, remember, check_permission
from API_aiohttp.db import users_collection
from API_aiohttp.utility import get_short_url, logger

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


async def get_homepage(request: web.Request) -> web.Response:
    session = await aiohttp_session.get_session(request)
    user = session.get("AIOHTTP_SECURITY", "Anonim")
    is_logged = not await is_anonymous(request)
    with open(BASE_DIR + "/templates/MAIN_FORM.html") as f:
        content = f.read()
    return web.Response(
        text=content.format(logged="" if is_logged else "NOT", nickname=f"{user}" if is_logged else "Anonim"),
        content_type="text/html",
    )


async def get_login_page(request: web.Request) -> web.Response:
    with open(BASE_DIR + "/templates/LOGIN_FORM.html") as f:
        content = f.read()
    return web.Response(
        content_type="text/html",
        text=content.format(
            error_message="",
        ),
    )


async def get_forgotten_user(request: web.Request):
    session = await aiohttp_session.get_session(request)
    user = session.get("AIOHTTP_SECURITY", "Anonim")
    redirect_response = web.HTTPFound("/")
    await forget(request, redirect_response)
    logger.info(f"User forget on session. Nickname: {user}")
    raise redirect_response


async def post_login_handler(request: web.Request) -> web.Response:
    data = await request.post()
    user = await users_collection.find_one({"name": data["username"]})
    if user:
        entered_password = data["password"].encode("utf-8")
        rehashed_password = bcrypt.hashpw(entered_password, user["salt"])
        if user["password"] != rehashed_password:
            error_message = "Wrong password"
        else:
            redirect_response = web.HTTPFound("/short_url")
            await remember(request, redirect_response, identity=user["name"])
            raise redirect_response
    else:
        error_message = "User not found in DB"
    with open(BASE_DIR + "/templates/LOGIN_FORM.html") as f:
        content = f.read()
    return web.Response(
        text=content.format(
            error_message=error_message,
        ),
        content_type="text/html",
    )


async def get_short_url_page(request: web.Request) -> web.Response:
    await check_permission(request, "do_short_url")
    with open(BASE_DIR + "/templates/SHORT_URL_FORM.html") as f:
        content = f.read()
    return web.Response(
        content_type="text/html",
        text=content.format(
            short_url="",
            error_message="",
        ),
    )


async def post_short_url_handler(request: web.Request) -> web.Response:
    await check_permission(request, "do_short_url")
    data = await request.post()
    data_url = data["data_url"]
    short_url = await get_short_url(data_url)
    logger.info("User try to get short_url link")
    with open(BASE_DIR + "/templates/SHORT_URL_FORM.html") as f:
        content = f.read()
    return web.Response(
        text=content.format(
            short_url=f"{short_url}" if short_url != "Error" else "",
            error_message="" if short_url != "Error" else "Wrong link",
        ),
        content_type="text/html",
    )


async def get_registration_page(request: web.Request) -> web.Response:
    with open(BASE_DIR + "/templates/REGISTRATION_FORM.html") as f:
        content = f.read()
    return web.Response(
        content_type="text/html",
        text=content.format(
            error_message="",
        ),
    )


async def post_registration_handler(request: web.Request) -> web.Response:
    data = await request.post()
    username, password, confirm_password = data["username"], data["password"], data["confirm_password"]
    if await users_collection.find_one({"name": username}):
        error_message = "The database already has such a nickname. Change your nickname."
    elif password != confirm_password:
        error_message = "Your passwords are not the same"
    else:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        user = {"name": username, "salt": salt, "password": hashed_password}
        await users_collection.insert_one(user)
        logger.info(f"Save to DB :{username}")
        redirect_response = web.HTTPFound("/short_url")
        await remember(request, redirect_response, identity=username)
        logger.info(f"User remember on session. Nickname: {username}")
        raise redirect_response
    with open(BASE_DIR + "/templates/REGISTRATION_FORM.html") as f:
        content = f.read()
    return web.Response(
        text=content.format(
            error_message=error_message,
        ),
        content_type="text/html",
    )


def setup_routes(app):
    app.add_routes(
        [
            web.get("/", get_homepage),
            web.get("/login", get_login_page),
            web.post("/login", post_login_handler),
            web.get("/forget", get_forgotten_user),
            web.get("/short_url", get_short_url_page),
            web.post("/short_url", post_short_url_handler),
            web.get("/registration", get_registration_page),
            web.post("/registration", post_registration_handler),
        ]
    )
