# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst

def change_url(value):
    try:
        result = value.replace('w_82', 'w_600').replace('h_82', 'h_600')
        return result
    except Exception:
        return value


def change_type(value):
    try:
        result = int(value.replace(' ', ''))
        return result
    except Exception:
        return value


class LeroyparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(change_url))
    price = scrapy.Field(output_processor=MapCompose(change_type))
    link = scrapy.Field()
    _id = scrapy.Field()
    specifications = scrapy.Field()

