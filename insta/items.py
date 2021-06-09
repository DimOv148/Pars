# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaItem(scrapy.Item):
    # define the fields for your item here like:
    parent_user_id = scrapy.Field()
    parent_user_name = scrapy.Field()
    profile_photo = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    short_code = scrapy.Field()
    user_link = scrapy.Field()
    all = scrapy.Field()
    _id = scrapy.Field()
