import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import SjruItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&noGeo=1&page=1']


    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class = 'icMQ_ bs_sM _3ze9n f-test-button-dalshe f-test-link-Dalshe']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        vacancies_link = response.xpath("//div[@class = '_1h3Zg _2rfUm _2hCDz _21a7u']/a/@href").extract()
        for link in vacancies_link:
            yield response.follow(link, callback=self.vacancy_parse)


    def vacancy_parse(self, response: HtmlResponse):
        item_name = response.xpath("//h1/text()").extract_first()
        item_salary = response.xpath("//span[@class = '_1h3Zg _2Wp8I _2rfUm _2hCDz']/text()").extract()
        item_link = response.url
        item_site = 'superjob.ru'
        # + дополнительные поля
        item = SjruItem(name=item_name, salary=item_salary, link=item_link, site=item_site)
        yield item