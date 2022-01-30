import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst

from medium.items import MediumItem

class BetterHumansSpider(scrapy.Spider):
    name = 'better_humans'
    start_urls = ['https://medium.com/better-humans/archive']
    custom_settings = {
        'ITEM_PIPELINES': {
            'medium.pipelines.DefaultValuesPipeline': 100,
            'medium.pipelines.CsvWriterPipeline': 200,
        },
    }

    def parse(self, response):
        year_div = response.xpath("/html/body/div[1]/div[2]/div/div[3]/div[1]/div[1]/div/div[2]")
        years = year_div.xpath(".//a/@href").getall()
        year_pages = []
        for year in ['2018', '2019', '2020']:
            for url in years:
                if year in url:
                    year_pages.append(url)

        if len(year_pages) != 0:
            yield from response.follow_all(year_pages, callback=self.parse_months)

    def parse_months(self, response):
        month_div = response.xpath("/html/body/div[1]/div[2]/div/div[3]/div[1]/div[1]/div/div[3]")
        month_pages = month_div.xpath(".//a/@href").getall()
        if len(month_pages) != 0:
            yield from response.follow_all(month_pages, callback=self.parse_days)
        else:
            yield from self.parse_articles(response)

    def parse_days(self, response):
        day_div = response.xpath("/html/body/div[1]/div[2]/div/div[3]/div[1]/div[1]/div/div[4]")        
        day_pages = day_div.xpath(".//a/@href").getall()
        if len(day_pages) != 0:
            yield from response.follow_all(day_pages, callback=self.parse_articles)

    def parse_articles(self, response):
        articles = response.xpath('/html/body/div[1]/div[2]/div/div[3]/div[1]/div[2]/*')
        for article_selector in articles:
            yield self.populate_item(article_selector, response.url)

    def populate_item(self, selector, url):
        item_loader = ItemLoader(item=MediumItem(), selector=selector)
        item_loader.default_output_processor = TakeFirst()
        item_loader.add_xpath('author', './/a[@data-action="show-user-card"]/text()')
        item_loader.add_xpath('title', './/*[contains(@class, "title")]/text()')
        item_loader.add_xpath('title', './/h3[contains(@class, "title")]/*/text()')
        item_loader.add_xpath('subtitle', './/*[@name="previewSubtitle"]/text()')
        item_loader.add_xpath('publication', './/a[@data-action="show-collection-card"]/text()')
        item_loader.add_xpath('read_time', './/*[@class="readingTime"]/@title')
        item_loader.add_xpath('claps', './/button[@data-action="show-recommends"]/text()')
        item_loader.add_xpath('responses', './/a[@class="button button--chromeless u-baseColor--buttonNormal"]/text()')
        item_loader.add_xpath('published_date', './/time/text()')
        item_loader.add_xpath('article_url', './/a[contains(@class, "button--smaller")]/@href')

        return item_loader.load_item()
        