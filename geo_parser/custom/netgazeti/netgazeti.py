from bs4 import BeautifulSoup
from tqdm import tqdm
import asyncio


BASE = 'https://netgazeti.ge/category/news/page/'


base_urls = [BASE + str(num) for num in range(1, 4067)]


import asyncio
import aiohttp
from bs4 import BeautifulSoup

TIMEOUT = 1024

async def get_links(session, url):
    async with session.get(url, timeout=TIMEOUT) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        divs = soup.find_all('div', {'class': 'col-lg-4 col-md-4 col-sm-6 mb-3'})
        urls = [div.find_all('a')[0].attrs['href'] for div in divs]
        return  urls

async def parse_page(session, url):
    async with session.get(url, timeout=TIMEOUT) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        article = soup.find('article')
        return [e.text for e in article.find_all('p')]

async def main():
    BATCH = 500
    conn = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(connector=conn) as session:
        for i in tqdm(range(3500, len(base_urls), BATCH)):
            tasks = [get_links(session, url) for url in base_urls[i: i + BATCH]]
            links = []
            for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc='Getting links', leave=False):
                links.extend(await f)

            tasks = [parse_page(session, link) for link in links]
            data = []

            for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc='Parsing links', leave=False):
                data.extend(await f)

                if len(data) > 10_000:
                    with open('netgazeti.txt', 'a', encoding='utf-8') as f:
                        f.write('\n'.join(data))
                    data = []

        with open('netgazeti.txt', 'a', encoding='utf-8') as f:
            f.write('\n'.join(data))

    

if __name__ == "__main__":
    asyncio.run(main())




