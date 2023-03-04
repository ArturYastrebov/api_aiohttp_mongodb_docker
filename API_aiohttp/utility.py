import aiohttp
import logging
from aiohttplimiter import Limiter, default_keyfunc

async def get_short_url(long_url: str) -> str:
    url = f"http://tinyurl.com/api-create.php?url={long_url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            short_url = await response.text()
            return short_url


logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

limiter = Limiter(keyfunc=default_keyfunc)
