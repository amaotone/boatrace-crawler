import scrapy


class OddsSpider(scrapy.Spider):
    name = "odds"
    allowed_domains = ["www.boatrace.jp"]
    start_urls = ["https://www.boatrace.jp/owpc/pc/race/index"]

    def parse(self, response):
        print(response.css("tbody ul.textLinks3 li:nth-child(2) > a").getall())
