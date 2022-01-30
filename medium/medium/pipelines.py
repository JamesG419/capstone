# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from scrapy.exporters import CsvItemExporter
from scrapy import signals
import os


class DefaultValuesPipeline:
    def process_item(self, item, spider):
        item.setdefault('author', None)
        item.setdefault('title', None)
        item.setdefault('subtitle', None)
        item.setdefault('publication', None) 
        item.setdefault('read_time', 0)
        item.setdefault('claps', 0 )
        item.setdefault('responses', 0)
        item.setdefault('published_date', '')
        item.setdefault('article_url', '')

        return item


class CsvWriterPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline
    
    def spider_opened(self, spider):
        try:
            self.file = open(f'./scraped_data/{spider.name}.csv', 'w+b')
        except OSError:
            os.makedirs('./scraped_data/')
            self.file = open(f'./scraped_data/{spider.name}.csv', 'w+b')
        self.exporter = CsvItemExporter(self.file)
        self.exporter.fields_to_export = [
            'author',
            'title',
            'subtitle',
            'publication',
            'read_time',
            'claps',
            'responses',
            'published_date',
            'article_url',
            ]
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
