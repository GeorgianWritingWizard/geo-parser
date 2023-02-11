import requests
import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from async_retrying import retry
from tqdm import tqdm


TIMEOUT = 1024

async def parse_page(session, url):
    async with session.get(url, timeout=TIMEOUT) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        return [e.text for e in soup.find_all('p')]

cookies = {
    '__asc': 'a3356b48185f7186ca4ea9483a7',
    '__auc': 'a3356b48185f7186ca4ea9483a7',
    '_fbp': 'fb.1.1674887851396.1804148471',
    '_ga': 'GA1.2.117633730.1674887851',
    '_gid': 'GA1.2.1758963729.1674887851',
    '_gat_gtag_UA_6557483_1': '1',
}

headers = {
    'authority': '1tv.ge',
    'accept': '*/*',
    'accept-`la`nguage': 'en-US,en;q=0.9,ka;q=0.8',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    # 'cookie': '__asc=a3356b48185f7186ca4ea9483a7; __auc=a3356b48185f7186ca4ea9483a7; _fbp=fb.1.1674887851396.1804148471; _ga=GA1.2.117633730.1674887851; _gid=GA1.2.1758963729.1674887851; _gat_gtag_UA_6557483_1=1',
    'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjMzOTc5NDEiLCJhcCI6IjMyMjU1MDIyOCIsImlkIjoiMDZhZDlhZThhMDJmMjNkOSIsInRyIjoiZDdjNzMxM2NjYzMzYTczMTcyYzQ4MGZjY2RmY2I0NjAiLCJ0aSI6MTY3NDg4OTEwNDMxMH19',
    'origin': 'https://1tv.ge',
    'referer': 'https://1tv.ge/',
    'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'traceparent': '00-d7c7313ccc33a73172c480fccdfcb460-06ad9ae8a02f23d9-01',
    'tracestate': '3397941@nr=0-1-3397941-322550228-06ad9ae8a02f23d9----1674889104310',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'x-newrelic-id': 'VwUOVl9XCRACUVFXAAEOVFE=',
    'x-requested-with': 'XMLHttpRequest',
}

async def get_links(session, url, data, cookies, headers):
    async with session.post(url, timeout=TIMEOUT, cookies=cookies, headers=headers, data=data) as response:
        jsonify = json.loads(await response.text())
        a = [entry['post_permalink'] for entry in jsonify['data']]
        return a

def generate_data(i):
    data = {
                'page_id': '1426',
                'offset': f'{i}',
                'tpl_ver': '39.9.94',
                'lang': 'ge',
                'per_page': '15',
                'personal_feeds': '0',
                'is_home': '1',
                'latest_id': '1761873',
            }

    return data


chunk_data = []
BATCH = 500

async def main():
    url = 'https://1tv.ge/wp-json/witv/posts'
    conn = aiohttp.TCPConnector(limit=5)
    async with aiohttp.ClientSession(connector=conn) as session:
        for i in tqdm(range(149000, 294200, BATCH)):
            tasks = [get_links(session, url, generate_data(i), cookies, headers) for i in range(i, i + BATCH)]

            links = []
            for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc='Getting links', leave=False):
                links.extend(await f)

            tasks = [parse_page(session, link) for link in links]
            data = []

            for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc='Parsing links', leave=False):
                data.extend(await f)

                if len(data) > 10_000:
                    with open('1tv_v2.txt', 'a', encoding='utf-8') as f:
                        f.write('\n'.join(data))
                    data = []


    with open('1tv_v2.txt', 'a', encoding='utf-8') as f:
        f.write('\n'.join(data))


if __name__ == "__main__":
    asyncio.run(main())