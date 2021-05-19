from lxml import html
import requests
from datetime import datetime
from pprint import pprint
from pymongo import MongoClient

mongodb = MongoClient('localhost', 27017)
db = mongodb['db_news']
collection = db.news

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'}

def get_news_mail():
    url = 'https://news.mail.ru/'
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)

    list_news = list(set(dom.xpath(
        "//div[@class='js-module']//a[contains(@class, 'photo photo') or contains(@class, 'list__text')]/@href")))
    for items in list_news:
        news = {}
        response = requests.get(items, headers=headers)
        dom = html.fromstring(response.text)
        news['name'] = dom.xpath("//h1/text()")
        news['date'] = dom.xpath("//span[contains(@class, 'note__text ') and contains(@datetime, '-')]/@datetime")
        news['link'] = dom.xpath("//a[@class = 'link color_gray breadcrumbs__link']/@href")
        news['site'] = url

        collection.insert_one(news)


def get_news_lenta():
    url = 'https://lenta.ru/'
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)

    list_news = dom.xpath("//time[@class = 'g-time']/../..")
    for items in list_news:
        news = {}
        news['name'] = items.xpath(".//a[@href]/text()")[0].replace('\xa0', ' ')
        news['date'] = items.xpath(".//time[@class = 'g-time']/@datetime")
        news['link'] = url + items.xpath(".//a[@href]/@href")[0]
        news['site'] = url

        collection.insert_one(news)

def get_news_yandex():
    url = 'https://yandex.ru/news'
    response = requests.get(url, headers=headers)
    dom = html.fromstring(response.text)

    list_news = dom.xpath("//a[contains(@href, 'rubric=index') and @class = 'mg-card__link']/ancestor :: article")
    for items in list_news:
        news = {}
        news['name'] = items.xpath(".//h2[@class = 'mg-card__title']/text()")[0].replace('\xa0', ' ')
        news['date'] = items.xpath(".//span[@class = 'mg-card-source__time']/text()")
        news['link'] = items.xpath(".//a[@class = 'mg-card__source-link']/@href")
        news['site'] = url

        collection.insert_one(news)

get_news_mail()
get_news_lenta()
get_news_yandex()


