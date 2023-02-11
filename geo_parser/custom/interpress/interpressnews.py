import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
from async_retrying import retry

# api_call = 'https://www.interpressnews.ge/ka/api/category/19/' # konfliqtebi
# api_call = 'https://www.interpressnews.ge/ka/api/category/36/' # eqskluzivi
# api_call = 'https://www.interpressnews.ge/ka/api/category/44/' # interviu
# api_call = 'https://www.interpressnews.ge/ka/api/category/48/' # tvalsazrisi

statuses = {x for x in range(100, 600)}
statuses.remove(200)
statuses.remove(429)



BASE_URL = 'https://www.interpressnews.ge'
TOTAL = 120


import aiohttp
import asyncio
from bs4 import BeautifulSoup


@retry(attempts=20)
async def fetch(session, url):
    async with session.get(url) as response:
        page = await response.text()
        soup = BeautifulSoup(page, 'html.parser')
        return [e.text for e in soup.find_all('p')]

async def main(urls, chunk_data):
    conn = aiohttp.TCPConnector(limit=2)
    async with aiohttp.ClientSession(connector=conn) as session:
        tasks = [fetch(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)
        for response in responses:
            for text in response:
                chunk_data.append(text)


chunk_data = []

for page_num in tqdm(range(1, TOTAL)):
    payload = {'page': page_num, 'csrfmiddlewaretoken': 'yPdsn'}

    response = requests.post(api_call, data=payload)

    data = response.text

    results = json.loads(data)['results']

    urls = [f'{BASE_URL}/ka{e["url"]}' for e in results]

    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(urls, chunk_data))

    if len(chunk_data) > 1_000:
        with open('anonsi.txt', 'a', encoding='utf-8') as f:
            f.write('\n'.join(chunk_data))
        print("SPITTED")
        chunk_data = []



# with open('urls.txt', 'w') as f:
#     f.write('\n'.join(urls_all))


    