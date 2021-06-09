# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

class InstaPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.instagramm

    def process_item(self, item, spider):

        collection = self.db.ist_08062021
        collection.insert_one(item)

        return item
