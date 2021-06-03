import scrapy
from scrapy.http import HtmlResponse
from leroyparser.items import LeroyparserItem
from scrapy.loader import ItemLoader


class LeroyruSpider(scrapy.Spider):
    name = 'leroyru'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search):
        super(LeroyruSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa-pagination-item = 'right']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        goods_links = response.xpath("//div[@class = 'phytpj4_plp largeCard']/a")
        for link in goods_links:
            yield response.follow(link, callback=self.parse_good)


    def parse_good(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroyparserItem(), response=response)

        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('photos', "//img[@alt = 'image thumb']/@src")
        loader.add_xpath('price', "//uc-pdp-price-view[@slot = 'primary-price']/span[@slot = 'price']/text()")
        loader.add_value('link', response.url)
        loader.add_xpath('specifications', "//dt/text() | //dd/text()")

        yield loader.load_item()
