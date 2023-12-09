# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CaseItem(scrapy.Item):
    case_number = scrapy.Field()
    case_name = scrapy.Field()
    judge = scrapy.Field()
    mediator = scrapy.Field()
    carrier = scrapy.Field()
    accident_date = scrapy.Field()
    date_assigned = scrapy.Field()
    district = scrapy.Field()
    county = scrapy.Field()
    docket_data = scrapy.Field()
    schedule = scrapy.Field()
    pfbs = scrapy.Field()
