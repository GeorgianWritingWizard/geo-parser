from tqdm import tqdm
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from initial import initial_link

BASE = 'https://ka.wikipedia.org'

TIMEOUT = 5024


async def get_links(session, url):
    async with session.get(url, timeout=TIMEOUT) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        div = soup.find('div', {'class': 'mw-allpages-body'})
        all_a = div.find_all('a')

        current_page_links = [BASE + page.attrs['href'] for page in all_a]

        possible_next = soup.find(
            'div', {'class': 'mw-allpages-nav'}).find_all('a')

        if len(possible_next) == 2:
            next = BASE + possible_next[-1].attrs['href']
        else:
            next = None

        return current_page_links, next


async def parse_page(session, url):
    async with session.get(url, timeout=TIMEOUT) as response:
        soup = BeautifulSoup(await response.text(), 'html.parser')
        a = soup.find('div', {'class': 'mw-parser-output'})

        if not a:
            return ''

        for e in a.find_all('span', {'class': 'mw-editsection'}):
            e.decompose()

        for e in a.find_all('ul'):
            e.decompose()

        for e in a.find_all('h2'):
            e.decompose()

        for e in a.find_all('td'):
            e.decompose()

        for e in a.find_all('table'):
            e.decompose()

        for e in a.find_all('div', {'class': 'reflist'}):
            e.decompose()

        return a.text


async def main():
    conn = aiohttp.TCPConnector(limit=10)
    async with aiohttp.ClientSession(connector=conn) as session:
        current_page_links, next_link = await get_links(session, initial_link)
        with tqdm(total=466790) as pbar:
            while next_link:
                tasks = [parse_page(session, url) for url in current_page_links]
                data = []
                for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc='Parsing Pages', leave=False):
                    data.append(await f)

                    if len(data) > 300:
                        with open('wikipedia.txt', 'a', encoding='utf-8') as f:
                            for line in data:
                                f.write(line.strip() + '\n')

                        data = []

                current_page_links, next_link = await get_links(session, next_link)
                pbar.update(len(tasks))

        with open('wikipedia.txt', 'a', encoding='utf-8') as f:
            for line in data:
                f.write(line.strip() + '\n')


if __name__ == "__main__":
    asyncio.run(main())
