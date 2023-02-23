import aiohttp
import logging

async def get_short_url(long_url: str) -> str:
    """
    Get long url and return short url.
    """
    url = f"http://tinyurl.com/api-create.php?url={long_url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            short_url = await response.text()
            return short_url

# Create a logger
logger = logging.getLogger(__name__)

# Configure the logger
logging.basicConfig(level=logging.INFO)
