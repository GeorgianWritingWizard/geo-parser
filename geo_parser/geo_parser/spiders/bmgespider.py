import scrapy


class BMGESpider(scrapy.Spider):
    name = "bmge"
    start_urls = [
        'https://bm.ge/ka/all-news/20.10.2013-27.01.2023/1/'
    ]

    def parse(self, response, **kwargs):
        news_links = response.css('div.single-news a::attr(href)').getall() + \
                     response.css('div.single-news-inner a::attr(href)').getall()

        yield from response.follow_all(news_links, self.parse_news)

        next_link = response.css('div.next a::attr(href)').getall()

        self.logger.info('Parse function called on %s', next_link)
        if next_link:
            yield response.follow(next_link[-1], self.parse)

    def parse_news(self, response):
        yield {
            'title': response.css('div.article-title h2::text').get(),
            'content': [content.strip() for content in response.css('div.single-text *::text').getall()
                        if content.strip()],
        }
