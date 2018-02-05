import scrapy
from scrapy.crawler import CrawlerProcess
import re

ENGLAND_PREMIER_LEAGUE = 17
league = ENGLAND_PREMIER_LEAGUE
date = '2018-01-30'

class SoccerSpider(scrapy.Spider):

    #按照联赛-轮次-球队查询

    name = 'soccer'
    start_urls = ['http://www.okooo.com/jingcai/'+date]

    def parse(self, response):
        # matches = response.xpath('//div[@class="touzhu_1"]').extract()

        matches = response.xpath('//div[@class="touzhu_1"]')
        matches_ext = response.xpath('//div[@class="touzhu_1"]').extract()

        i = 0
        for match in matches:
            print(i)
            i+=1

            # print(match)
            # print (match.extract())

            # print (match.xpath('::attr(data-hname)')).extract()
            # print (match.xpath('::attr(data-name)'))
            # print(match.css('div::attr(data-name)').extract())

            # print(match.xpath('@data-name'))
            # print(match.xpath('@data-name').extract())
            # print(match.xpath('@data-name').extract().strip())

            # print(match.css('div::attr(data-hname)').extract())


            team_h_s = match.css('div::attr(data-hname)').extract_first()
            team_a_s = match.css('div::attr(data-aname)').extract_first()

            tm_node_liansai = match.xpath("div[@class='liansai']")

            team_detail = match.xpath("div[@class='shenpf ']//div[contains(@class,'zhum')]/text()").extract()
            # team_detail = tm_node_liansai.xpath("div[@class='shenpf ']//div[contains(@class,'zhum')]/text()").extract()
            team_h_d = team_detail[0]
            team_a_d = team_detail[1]

            # match_id = match.css('div::attr(data-mid)').extract()

            # match_id = matches_ext.xpath('//div[@data-end=2]/@data-mid').extract()
            # match_id = matches_ext.xpath('//div/@data-mid').extract()
            # match_id = matches_ext.xpath('//div[@class="touzhu_1"]').extract()
            # match_id = match.xpath('//div[@class="touzhu_1"]').extract()
            # match_id = match.xpath("//div[@data-end='2']/@data-mid").extract()

            # match_id = match.xpath("//div[contains(@data-end,'2')]/@data-mid").extract()
            # match_id = match.xpath("//[contains(@data-end,'2')]/@data-mid").extract()


            # match_id = match.css('div::attr(data-aname)').extract()


            match_id = match.xpath("@data-mid").extract_first()
            # day_index = match.xpath("span[@class='xulie']/text()").extract()

            # day_index = match.xpath("div[@class='liansai']/span/text()").extract_first()
            day_index = tm_node_liansai.xpath("span/text()").extract_first()

            # type = match.xpath("div[@class='liansai']/a/text()").extract_first()
            type = tm_node_liansai.xpath("a/text()").extract_first()

            # time = match.xpath("div[@class='liansai']/div/@title").extract_first()
            # time_re = re.search(r'\d.*',time)
            # time = re.sub(r'^\D+(\d+.*)$',r'\1',match.xpath("div[@class='liansai']/div/@title").extract_first())
            time = re.sub(r'^\D+(\d+.*)$',r'\1',tm_node_liansai.xpath("div/@title").extract_first())

            if(i == 4):
                print(team_h_s)
                print(team_a_s)

                print(team_h_d)
                print(team_a_d)

                # print(match.extract())
                print(match_id)
                print(day_index)
                print(type)
                print(time)



process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})


process.crawl(SoccerSpider)
process.start() # the script will block here until the crawling is finished
