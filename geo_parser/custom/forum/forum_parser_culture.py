import aiohttp
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests
import asyncio
BASE_URL = 'https://forum.ge/?showforum=36&prune_day=100&sort_by=Z-A&sort_key=last_post&st='


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
    'Accept-Language': 'en-US,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


all_pages = [BASE_URL + f'{i}' for i in range(0, 3320, 40)]


TIMEOUT = 5048


async def parse_post(session, url):
    async with session.get(url, timeout=TIMEOUT) as response:
        bs = BeautifulSoup(await response.text(), 'html.parser')

        tds = bs.find_all('td')
        res = []
        for td in tds:
            res.extend([e.text for e in td.find_all(
                'div', {'class': 'postcolor'})])
            break

        return res


def get_posts(page_url):
    data = requests.get(page_url, headers=headers)
    bs = BeautifulSoup(data.content, 'html.parser')
    ok = bs.findAll('table')[6].find_all(lambda tag: tag.name == 'td' and len(
        tag['class']) == 1 and 'row4' in tag['class'])
    page_posts = [post.find('a').attrs['href'] for post in ok]

    return page_posts


async def generate_inner_pages(session, url):
    async with session.get(url, timeout=TIMEOUT) as response:
        bs = BeautifulSoup(await response.text(), 'html.parser')

        try:
            last_page_num = bs.find(
                'div', {'class': 'w3-bar'}).find_all('a')[3].attrs['title'].split(':')[-1].strip()
        except:
            last_page_num = None

        if not last_page_num:
            return None
        urls = []
        for i in range(0, int(last_page_num) + 1):
            urls.append(url + f'&st={i * 15}')

        return urls


async def main():
    data = []
    BATCH = 1
    conn = aiohttp.TCPConnector(limit=2)
    async with aiohttp.ClientSession(connector=conn) as session:
        with open('forum_ge_cu.txt', 'a', encoding='utf-8') as file:

            for i in tqdm(range(0, len(all_pages), BATCH), desc="FORUM PAGE NUMBER"):
                posts = []

                for page in all_pages[i: i + BATCH]:
                    posts.extend(get_posts(page))

                tasks = [generate_inner_pages(session, post) for post in posts]
                inner_posts = []

                for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc='GENERATIN INNER PAGES', leave=False):
                    try:
                        innder_data = await f
                        if innder_data:
                            inner_posts.extend(innder_data)
                    except:
                        print("SHIT TIMEOUT")

                tasks = [parse_post(session, inner_post)
                         for inner_post in inner_posts]

                for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc='PARSNG INNER PAGES', leave=False):
                    try:
                        data.extend(await f)
                    except:
                        print("SHIT TIMEOUT")
                        continue

                    if len(data) > 1_000:
                        # yeh fuck it
                        ss = set(data)
                        for line in list(ss):
                            file.write(line.strip() + '\n')

                        data = []

        with open('forum_ge_cu.txt', 'a', encoding='utf-8') as file:
            ss = set(data)
            for line in list(ss):
                file.write(line.strip() + '\n')

if __name__ == "__main__":
    asyncio.run(main())
