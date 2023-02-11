import requests
import json
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from async_retrying import retry
from tqdm import tqdm



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
    'accept-language': 'en-US,en;q=0.9,ka;q=0.8',
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



chunk_data = []

for i in tqdm(range(149000, 294200, 15)):
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

    response = requests.post('https://1tv.ge/wp-json/witv/posts', cookies=cookies, headers=headers, data=data)

    jsonify = json.loads(response.text)

    urls = [entry['post_permalink'] for entry in jsonify['data']]

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(urls, chunk_data))

    if len(chunk_data) > 1_000:
        with open('1tv_second.txt', 'a', encoding='utf-8') as f:
            f.write('\n'.join(chunk_data))
        print("SPITTED")
        chunk_data = []


with open('1tv_second.txt', 'a', encoding='utf-8') as f:
    f.write('\n'.join(chunk_data))
    print("SPITTED")
    chunk_data = []