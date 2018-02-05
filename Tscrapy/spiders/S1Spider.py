import scrapy
from scrapy.crawler import CrawlerProcess
import re

#按照联赛-轮次-球队查询比赛基本信息

ENGLAND_PREMIER_LEAGUE = 17
ENGLAND_PREMIER_LEAGUE_MATCH_PER_TURN = 10
SEASON_ENGLAND_PREMIER_LEAGUE_17_18 = 13222


league = ENGLAND_PREMIER_LEAGUE
season = SEASON_ENGLAND_PREMIER_LEAGUE_17_18
turn = 1
match_per_turn = 10

class S1Spider(scrapy.Spider):



    name = 'S1Spider'
    start_urls = ['http://www.okooo.com/soccer/league/%s/schedule/%s/1-1-%s' %(league,season,turn)]

    def parse(self, response):
        # matches = response.xpath('//div[@class="touzhu_1"]').extract()

        # matches = response.xpath('//div[@class="touzhu_1"]')
        # matches_ext = response.xpath('//div[@class="touzhu_1"]').extract()
        #
        # i = 0
        # for match in matches:
        #     print(i)
        #     i+=1
        #
        #     # print(match)
        #     # print (match.extract())
        #
        #     # print (match.xpath('::attr(data-hname)')).extract()
        #     # print (match.xpath('::attr(data-name)'))
        #     # print(match.css('div::attr(data-name)').extract())
        #
        #     # print(match.xpath('@data-name'))
        #     # print(match.xpath('@data-name').extract())
        #     # print(match.xpath('@data-name').extract().strip())
        #
        #     # print(match.css('div::attr(data-hname)').extract())
        #
        #
        #     team_h_s = match.css('div::attr(data-hname)').extract_first()
        #     team_a_s = match.css('div::attr(data-aname)').extract_first()
        #
        #     tm_node_liansai = match.xpath("div[@class='liansai']")
        #
        #     team_detail = match.xpath("div[@class='shenpf ']//div[contains(@class,'zhum')]/text()").extract()
        #     # team_detail = tm_node_liansai.xpath("div[@class='shenpf ']//div[contains(@class,'zhum')]/text()").extract()
        #     team_h_d = team_detail[0]
        #     team_a_d = team_detail[1]
        #
        #     # match_id = match.css('div::attr(data-mid)').extract()
        #
        #     # match_id = matches_ext.xpath('//div[@data-end=2]/@data-mid').extract()
        #     # match_id = matches_ext.xpath('//div/@data-mid').extract()
        #     # match_id = matches_ext.xpath('//div[@class="touzhu_1"]').extract()
        #     # match_id = match.xpath('//div[@class="touzhu_1"]').extract()
        #     # match_id = match.xpath("//div[@data-end='2']/@data-mid").extract()
        #
        #     # match_id = match.xpath("//div[contains(@data-end,'2')]/@data-mid").extract()
        #     # match_id = match.xpath("//[contains(@data-end,'2')]/@data-mid").extract()
        #
        #
        #     # match_id = match.css('div::attr(data-aname)').extract()
        #
        #
        #     match_id = match.xpath("@data-mid").extract_first()
        #     # day_index = match.xpath("span[@class='xulie']/text()").extract()
        #
        #     # day_index = match.xpath("div[@class='liansai']/span/text()").extract_first()
        #     day_index = tm_node_liansai.xpath("span/text()").extract_first()
        #
        #     # type = match.xpath("div[@class='liansai']/a/text()").extract_first()
        #     type = tm_node_liansai.xpath("a/text()").extract_first()
        #
        #     # time = match.xpath("div[@class='liansai']/div/@title").extract_first()
        #     # time_re = re.search(r'\d.*',time)
        #     # time = re.sub(r'^\D+(\d+.*)$',r'\1',match.xpath("div[@class='liansai']/div/@title").extract_first())
        #     time = re.sub(r'^\D+(\d+.*)$',r'\1',tm_node_liansai.xpath("div/@title").extract_first())
        #
        #     if(i == 4):
        #         print(team_h_s)
        #         print(team_a_s)
        #
        #         print(team_h_d)
        #         print(team_a_d)
        #
        #         # print(match.extract())
        #         print(match_id)
        #         print(day_index)
        #         print(type)
        #         print(time)


        matches = response.xpath('//*[@id="team_fight_table"]')
        # matches = response.xpath('//*[@id="team_fight_table"]/tbody')
        #
        # print(matches.extract())

        for i in range(2,match_per_turn+2):
            print(i)
            match = matches.xpath('tr[%s]' %(i))

            # print(match.extract())

            id = match.xpath('@matchid').extract_first()
            time = match.xpath('td[1]/text()').extract_first()
            teamHome = match.xpath('td[3]/text()').extract_first()
            teamAway = match.xpath('td[5]/text()').extract_first().strip()
            scoreText = match.xpath('td[4]/a/strong/text()').extract_first()
            goalHome = scoreText.split('-')[0]
            goalAway = scoreText.split('-')[1]

            print(id)
            print(time)
            print(teamHome)
            print(teamAway)
            print(scoreText)
            print(goalHome)
            print(goalAway)

            print()




process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
})


process.crawl(S1Spider)
process.start() # the script will block here until the crawling is finished
