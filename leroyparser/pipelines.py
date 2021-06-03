# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient

class LeroyparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.leroy_merlin


    def process_item(self, item, spider):
        spec = {}
        for i, el in enumerate(item['specifications']):
            if i % 2 != 0:
                try:
                    el = float(el.strip())
                except ValueError:
                    el = el.strip()
                spec[item['specifications'][i - 1]] = el
        item['specifications'] = spec

        collection = self.db.l_m_0306
        collection.insert_one(item)

        return item



class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img) #(img.replace('w_82', 'w_600').replace('h_82', 'h_600'))
                except TypeError as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        dir = item['name']
        urls = request.url.split('/')
        file_name = urls[len(urls) - 1]
        return f'full/{dir}/{file_name}'
