import scrapy

class DmozSpider(scrapy.Spider):
    # name = "dmoz"
    # allowed_domains = ["dmoz.org"]
    # start_urls = [
    #     "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
    #     "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    # ]
    #
    # def parse(self, response):
    #     for sel in response.xpath('//ul/li'):
    #         title = sel.xpath('a/text()').extract()
    #         link = sel.xpath('a/@href').extract()
    #         desc = sel.xpath('text()').extract()
    #         print(title, link, desc)
    #
    #         # def parse(self, response):
    #         #     for sel in response.xpath('//ul/li'):
    #         #         item = DmozItem()
    #         #         item['title'] = sel.xpath('a/text()').extract()
    #         #         item['link'] = sel.xpath('a/@href').extract()
    #         #         item['desc'] = sel.xpath('text()').extract()
    #         #         yield item

    name = 'woodenrobot'
    start_urls = ['http://woodenrobot.me']

    def parse(self, response):
        titles = response.xpath('//a[@class="post-title-link"]/text()').extract()
        for title in titles:
            print (title.strip())