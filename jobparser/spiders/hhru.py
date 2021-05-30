import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import HhruItem
# from jobparser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?clusters=true&enable_snippets=true&salary=&st=searchVacancy&text=Python&from=suggest_post']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        vacancies_link = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").extract()
        for link in vacancies_link:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        item_name = response.xpath("//h1/text()").extract_first()
        item_salary = response.xpath("//p/span[@data-qa='bloko-header-2']/text()").extract()
        item_link = response.url
        item_site = 'hh.ru'
        # + дополнительные поля
        item = HhruItem(name=item_name, salary=item_salary, link=item_link, site=item_site)
        yield item







