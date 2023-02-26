

import pytest


@pytest.mark.asyncio
async def test_main_form(client):
    client = await client
    resp = await client.get('/')
    assert resp.status == 200


@pytest.mark.asyncio
async def test_login_form(client):
    client = await client
    resp = await client.get('/login')
    assert resp.status == 200


@pytest.mark.asyncio
async def test_forget_action(client, user_create):
    client = await client
    resp = await client.get('/forget')
    assert resp.status == 200

@pytest.mark.asyncio
@pytest.mark.parametrize('username, password, expected', (
        ('test_user_name', 'wrong_pass', 'id="error_login">Wrong password'),
        ('wrong_user_name', 'test_hashed_password', 'id="error_login">User not found in DB'),
        ('test_user_name', 'test_hashed_password', '<title>Short url</title>'),
))
async def test_handler_login_ok(client, user_create, username, password, expected):
    data = {
        'username': username,
        'password': password
    }
    client = await client
    resp = await client.post('/login', data=data)
    assert resp.status == 200
    text = await resp.text()
    assert expected in text



@pytest.mark.asyncio
async def test_post_do_short_url_form(client, user_create):
    data = {
        'username': 'test_user_name',
        'password': 'test_hashed_password'
    }
    client = await client
    await client.post('/login', data=data)
    resp = await client.get('/short_url')
    assert resp.status == 200
    # text = await resp.text()
    # assert text == "Hello, world"


#
@pytest.mark.asyncio
async def test_post_handler_short_url(client, user_create):
    data = {
        'username': 'test_user_name',
        'password': 'test_hashed_password'
    }
    client = await client
    await client.post('/login', data=data)
    data = {
        'data_url': 'https://www.ea.com/ru-ru/fifa/ultimate-team/web-app/'
    }
    resp = await client.post('/short_url', data=data)
    assert resp.status == 200
    text = await resp.text()
    assert "https://tinyurl.com/2qobeku5" in text


#
@pytest.mark.asyncio
async def test_post_handle_registration(client, create_registration_data):
    username, password, password2, expected = create_registration_data
    client = await client
    data = {
        'username': username,
        'password': password,
        'password2': password2
    }
    resp = await client.post('/registration', data=data)
    assert resp.status == 200
    text = await resp.text()
    assert expected in text


#
@pytest.mark.asyncio
async def test_get_registration_form(client):
    client = await client
    resp = await client.get('/registration')
    assert resp.status == 200
    # text = await resp.text()
    # assert text == "Hello, world"
