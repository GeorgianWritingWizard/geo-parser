import re

import scrapy
from urllib.parse import unquote


class ONGESpider(scrapy.Spider):
    name = "onge"
    start_urls = [
        'https://on.ge/story/114711'
    ]

    @staticmethod
    def check_if_contains_digit(url):
        if re.search(r'\d', url):
            return True
        return False

    def parse(self, response, **kwargs):
        split_url = response.url.split('-')
        url = split_url[0]
        pk = url.split('/')[-1]
        new_pk = int(pk)
        for i in range(new_pk, 3, -1):
            next_link = url.replace(pk, str(i))
            yield response.follow(next_link, self.parse_news)

    def parse_news(self, response):
        if self.check_if_contains_digit(response.url):
            split_url = response.url.split('-')
            yield {
                'title': ' '.join(map(lambda x: unquote(x), split_url[1:])),
                'content': [content.strip() for content in response.css('.global-text-content *::text').getall()
                            if content.strip()],
            }
