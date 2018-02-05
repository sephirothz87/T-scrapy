import scrapy
from scrapy.crawler import CrawlerProcess
import re

# 按照联赛-轮次-球队查询比赛基本信息

ENGLAND_PREMIER_LEAGUE = 17
ENGLAND_PREMIER_LEAGUE_MATCH_PER_TURN = 10
SEASON_ENGLAND_PREMIER_LEAGUE_17_18 = 13222

# 博彩公司代号
WILLIAM_HILL = 14
WILLIAM_HILL = 14

league = ENGLAND_PREMIER_LEAGUE
season = SEASON_ENGLAND_PREMIER_LEAGUE_17_18
turn = 1
match_per_turn = 10

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
cookie = '__utmc=56961525; LastUrl=; FirstOKURL=http%3A//www.okooo.com/jingcai/; First_Source=www.okooo.com; Hm_lvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1517120624; Last_Source=http%3A//www.okooo.com/soccer/match/876722/odds/; IMUserName=ok_025742692071; __utmz=56961525.1517821150.16.3.utmcsr=okooo.com|utmccn=(referral)|utmcmd=referral|utmcct=/jingcai/2018-02-03/; __utma=56961525.95899878.1517120624.1517833475.1517848115.18; data_start_isShow=1; PHPSESSID=d932002d848166585fd346e771a90c5131becbce; DRUPAL_LOGGED_IN=Y; IMUserID=24006237; OkAutoUuid=b8b92c071a5ba1185c065aa6d9a2175b; OkMsIndex=5; isInvitePurview=0; UWord=5a9291a00f6e4c9e03f939fab73258b3a2d; Hm_lpvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1517850445; __utmb=56961525.62.8.1517850444706'

class T1Spider(scrapy.Spider):
    name = 'T1Spider'
    # start_urls = ['http://www.okooo.com/soccer/match/954300/odds/']
    # start_urls = ['http://www.okooo.com/I/?method=ok.soccer.odds.GetProcess']

    # headers = {
    #     'User-Agent':user_agent,
    #     'Connection':'keep-alive',
    #     'Referer':'http://www.okooo.com/soccer/match/954300/',
    #     'Cookie':cookie
    # }

    def start_requests(self):
        url = 'http://www.okooo.com/I/?method=ok.soccer.odds.GetProcess'

        headers = {
            'User-Agent': user_agent,
            'Connection': 'keep-alive',
            'Referer': 'http://www.okooo.com/soccer/match/954300/',
            'Cookie': cookie,
            'X-Requested-With': 'XMLHttpRequest'
        }

        yield scrapy.FormRequest(
            url = url,
            headers=headers,
            formdata = {
                'match_id': '954300',
                'betting_type_id': '1',
                'provider_id': '14'
            },
            callback=self.parse
        )

    def parse(self, response):
        print('parse')
        print(response)
        print()
        # print(response.extract())

        # williamHillOdds = response.xpath('//*[@id="tr14"]')
        #
        # print(williamHillOdds)
        #
        # startTimeW = williamHillOdds.xpath('td[3]/@title').extract_first()
        #
        # startOddW3 = williamHillOdds.xpath('td[3]/span/text()').extract_first()
        # startOddW1 = williamHillOdds.xpath('td[4]/span/text()').extract_first()
        # startOddW0 = williamHillOdds.xpath('td[5]/span/text()').extract_first()
        #
        # print(startTimeW)
        # print(startOddW3)
        # print(startOddW1)
        # print(startOddW0)
        # print()
        # print()


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
})

process.crawl(T1Spider)
process.start()  # the script will block here until the crawling is finished
