import aiohttp_security
import aiohttp_session
import bcrypt
from aiohttp import web
from aiohttp_security import is_anonymous, forget, remember, check_permission

from API_aiohttp.db import users_collection
from API_aiohttp.utility import get_short_url, logger


async def main_form(request: web.Request) -> web.Response:
    """
    Handle get requests to '/' endpoint.
    """
    session = await aiohttp_session.get_session(request)
    user = session.get('AIOHTTP_SECURITY', 'Anonim')
    is_logged = not await is_anonymous(request)
    with open('templates/MAIN_FORM.html') as f:
        content = f.read()
    return web.Response(text=content.format(
        logged='' if is_logged else 'NOT',
        nickname=f'{user}' if is_logged else 'Anonim'
    ), content_type='text/html')


async def login_form(request: web.Request) -> web.Response:
    """
    Handle get requests to '/login' endpoint.
    """
    with open('templates/LOGIN_FORM.html') as f:
        content = f.read()
    return web.Response(content_type='text/html', text=content.format(
        error='',
    ))

async def forget_action(request: web.Request):
    """
    Handle get requests to '/forget' endpoint.
    """
    session = await aiohttp_session.get_session(request)
    user = session.get('AIOHTTP_SECURITY', 'Anonim')
    redirect_response = web.HTTPFound('/')
    await forget(request, redirect_response)
    logger.info(f'User remember on session. Nickname: {user}')
    raise redirect_response

async def handler_login(request: web.Request) -> web.Response:
    """
    Handle post requests to '/login' endpoint.
    """
    data = await request.post()
    user = await users_collection.find_one({'name': data['username']})
    if user:
        entered_password = data['password'].encode('utf-8')
        rehashed_password = bcrypt.hashpw(entered_password, user['salt'])
        if user['password'] != rehashed_password:
            error_msg = 'Wrong password'
        else:
            redirect_response = web.HTTPFound('/short_url')
            await remember(request, redirect_response, identity=user['name'])
            raise redirect_response
    else:
        error_msg = 'User not found in DB'
    with open('templates/LOGIN_FORM.html') as f:
        content = f.read()
    return web.Response(text=content.format(
        error=error_msg,
    ), content_type='text/html')

async def do_short_url_form(request: web.Request) -> web.Response:
    """
    Handle get requests to '/short_url' endpoint.
    """
    await check_permission(request, 'do_short_url')
    with open('templates/SHORT_URL_FORM.html') as f:
        content = f.read()
    return web.Response(content_type='text/html', text=content.format(
        short_url='',
        error='',
    ))

async def handler_short_url(request: web.Request) -> web.Response:
    """
    Handle post requests to '/short_url' endpoint.
    """
    await check_permission(request, 'do_short_url')
    data = await request.post()
    data_url = data['data_url']
    short_url = await get_short_url(data_url)
    logger.info('User try to get short_url link')
    with open('templates/SHORT_URL_FORM.html') as f:
        content = f.read()
    return web.Response(text=content.format(
        short_url=f'{short_url}' if short_url != 'Error' else '',
        error='' if short_url != 'Error' else 'Wrong link',
    ), content_type='text/html')


async def registration_form(request: web.Request) -> web.Response:
    """
     Handle get requests to '/registration' endpoint.
     """
    with open('templates/REGISTRATION_FORM.html') as f:
        content = f.read()
    return web.Response(content_type='text/html', text=content.format(
        error='',
    ))

async def handle_registration(request: web.Request) -> web.Response:
    """
     Handle post requests to '/registration' endpoint.
     """
    data = await request.post()
    username, password, password2 = data['username'], data['password'], data['password2']
    if await users_collection.find_one({"name": username}):
        error = 'The database already has such a nickname. Change your nickname.'
    elif password != password2:
        error = 'Your passwords are not the same'
    else:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        user = {"name": username, 'salt': salt, "password": hashed_password}
        await users_collection.insert_one(user)
        logger.info(f'Save to DB :{username}')
        redirect_response = web.HTTPFound('/short_url')
        await remember(request, redirect_response, identity=username)
        logger.info(f'User remember on session. Nickname: {username}')
        raise redirect_response
    with open('templates/REGISTRATION_FORM.html') as f:
        content = f.read()
    return web.Response(text=content.format(
        error=error,
    ), content_type='text/html')

def setup_routes(app):
    """
    Add the routes to app.
    """
    # add the routes
    app.add_routes([
        web.get('/', main_form),
        web.get('/login', login_form),
        web.get('/forget', forget_action),
        web.post('/login', handler_login),
        web.get('/short_url', do_short_url_form),
        web.post('/short_url', handler_short_url),
        web.get('/registration', registration_form),
        web.post('/registration', handle_registration)])
