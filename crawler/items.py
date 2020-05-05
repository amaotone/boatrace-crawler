# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class OddsItem(scrapy.Item):
    date = scrapy.Field()
    stadium = scrapy.Field()
    round_ = scrapy.Field()

    win = scrapy.Field()  # 単勝
    place_show = scrapy.Field()  # 複勝
    exacta = scrapy.Field()  # 2連単
    quinella = scrapy.Field()  # 2連複
    trifecta = scrapy.Field()  # 3連単
    trio = scrapy.Field()  # 3連複
    quinella_place = scrapy.Field()  # 拡連複
