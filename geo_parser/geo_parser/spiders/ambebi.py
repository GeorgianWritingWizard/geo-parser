import scrapy


class AmbebiGESpider(scrapy.Spider):
    name = "ambebige"
    start_urls = [
        'https://www.ambebi.ge/article/288570-abc'
    ]

    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
    }

    def parse(self, response, **kwargs):
        orig_url = response.url
        split_url = response.url.split('-')
        url = split_url[0]
        pk = url.split('/')[-1]
        new_pk = int(pk)
        for i in range(new_pk, 21168, -1):
            next_link = orig_url.replace(pk, str(i))
            yield response.follow(next_link, self.parse_news)

    def parse_news(self, response):
        yield {
            'title': response.css('div.article_block > h1 ::text').get(),
            'content': [content.strip() for content in response.css('div.article_content *::text').getall()
                        if content.strip()],
        }
