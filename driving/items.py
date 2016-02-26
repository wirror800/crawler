# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ProvinceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    parent = scrapy.Field()
    code = scrapy.Field()
    pinyin = scrapy.Field()
    link = scrapy.Field()

class UrlItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = scrapy.Field()
    district = scrapy.Field()

class SchoolItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    cost = scrapy.Field()
    tel = scrapy.Field()
    students = scrapy.Field()
    coaches = scrapy.Field()
    ranges = scrapy.Field()
    summary = scrapy.Field()
    intro = scrapy.Field()
    pic = scrapy.Field()
    address = scrapy.Field()
    service = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    location = scrapy.Field()
    url = scrapy.Field()