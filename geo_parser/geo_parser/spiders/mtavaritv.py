import scrapy


class MtavariTVSpider(scrapy.Spider):
    name = "mtavaritv"
    start_urls = [
        'https://mtavari.tv/news/111058'
    ]

    def parse(self, response, **kwargs):
        split_url = response.url.split('-')
        url = split_url[0]
        pk = url.split('/')[-1]
        new_pk = int(pk)
        for i in range(new_pk, 3, -1):
            next_link = url.replace(pk, str(i))
            yield response.follow(next_link, self.parse_news)

    def parse_news(self, response):
        yield {
            'title': response.css('h1.id__Title-bhuaj0-10 ::text').get(),
            'content': [content.strip() for content in response.css('div.EditorContent__EditorContentWrapper-ygblm0-0 *::text').getall()
                        if content.strip()],
        }
