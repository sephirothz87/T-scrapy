import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request,HtmlResponse
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
cookie = 'LastUrl=; FirstOKURL=http%3A//www.okooo.com/jingcai/; First_Source=www.okooo.com; Last_Source=http%3A//www.okooo.com/soccer/match/876722/odds/; IMUserName=ok_025742692071; __utmz=56961525.1517821150.16.3.utmcsr=okooo.com|utmccn=(referral)|utmcmd=referral|utmcct=/jingcai/2018-02-03/; data_start_isShow=1; IMUserID=24006237; OkAutoUuid=b8b92c071a5ba1185c065aa6d9a2175b; OkMsIndex=5; __utmc=56961525; DRUPAL_LOGGED_IN=Y; isInvitePurview=0; PHPSESSID=f3438442d0a40ccd389ab57fc3e7620c9536b916; Hm_lvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1517120624,1517893507; __utma=56961525.95899878.1517120624.1517893506.1517895607.21; UWord=d451d8cd984f00b204e9800998ecf84127e; Hm_lpvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1517896077; __utmb=56961525.66.8.1517896134153'


def calChange(str):
    if (len(str) > 4):
        if str[4:5] == '↑':
            return 1
        elif str[4:5] == '↓':
            return -1
        else:
            print('calChangeError')
            return 0
    else:
        return 0

def exChangeTime(str):
    reg = r'\D*(\d+)\D+(\d+)\D+'
    return re.sub(reg,r'\1:\2',str)

class T3Spider(scrapy.Spider):
    name = 'T2Spider'
    # start_urls = ['http://www.okooo.com/soccer/match/954300/odds/']
    # start_urls = ['http://www.okooo.com/soccer/match/954348/odds/change/14/']
    # start_urls = ['http://www.okooo.com/soccer/match/954344/odds/change/14/']
    # start_urls = ['http://www.okooo.com/soccer/match/954344/odds/change/82/']
    # start_urls = ['http://www.okooo.com/soccer/match/954344/hodds/change/14/?boundary=1']


    # headers = {
    #     'User-Agent': user_agent,
    #     'Connection': 'keep-alive',
    #     'Referer': 'http://www.okooo.com/soccer/match/954378/',
    #     'Cookie': cookie
    # }


    start_urls = ['https://www.baidu.com']
    #17-18  第6轮 布莱顿vs纽卡
    # start_urls = ['http://www.okooo.com/soccer/match/954378/odds/change/14/']
    #17-18  第7轮 哈德斯菲尔德vs热刺
    # start_urls = ['http://www.okooo.com/soccer/match/954376/odds/change/14/']


    def parse(self,response):
        print('parse')

        #17-18  第7轮 哈德斯菲尔德vs热刺
        # tmp_url = 'http://www.okooo.com/soccer/match/954376/odds/change/14/'
        #17-18  第7轮 斯托克城vs南安普顿
        tmp_url = 'http://www.okooo.com/soccer/match/954326/odds/change/14/'

        headers = {
            'User-Agent': user_agent,
            'Connection': 'keep-alive',
            'Referer': 'http://www.okooo.com/soccer/match/954378/',
            'Cookie': cookie
        }

        yield Request(url=tmp_url,headers=headers,callback=self.parseOddsDetail)

    def parseOddsDetail(self, response):
        print('parseOddsDetail')
        print(response)
        print(response.body)
        print(response.url)
        print()
        # print(response.extract())

        shift = 0

        if response.url.find('hodds') > 0:
            shift = 1

        williamHillOdds = response.xpath('/html/body/div[1]/table')
        #
        # print(williamHillOdds.extract())

        finalOdd = williamHillOdds.xpath('tr[%s]' %(3+shift))

        finalOddW3 = finalOdd.xpath('td[%s]/text()' %(3+shift)).extract_first()
        finalOddW1 = finalOdd.xpath('td[%s]/text()' %(4+shift)).extract_first()
        finalOddW0 = finalOdd.xpath('td[%s]/text()' %(5+shift)).extract_first()

        finalPerW3 = finalOdd.xpath('td[%s]/text()' %(6+shift)).extract_first()
        finalPerW1 = finalOdd.xpath('td[%s]/text()' %(7+shift)).extract_first()
        finalPerW0 = finalOdd.xpath('td[%s]/text()' %(8+shift)).extract_first()

        finalKellyW3 = finalOdd.xpath('td[%s]/span/text()' %(9+shift)).extract_first()
        finalKellyW1 = finalOdd.xpath('td[%s]/span/text()' %(10+shift)).extract_first()
        finalKellyW0 = finalOdd.xpath('td[%s]/span/text()' %(11+shift)).extract_first()

        finalKellyChangeW3 = 0
        finalKellyChangeW1 = 0
        finalKellyChangeW0 = 0

        if not finalKellyW3:
            finalKellyW3 = finalOdd.xpath('td[%s]/text()' %(9+shift)).extract_first()
        if not finalKellyW1:
            finalKellyW1 = finalOdd.xpath('td[%s]/text()' %(10+shift)).extract_first()
        if not finalKellyW0:
            finalKellyW0 = finalOdd.xpath('td[%s]/text()' %(11+shift)).extract_first()

        finalKellyChangeW3 = calChange(finalKellyW3)
        finalKellyChangeW1 = calChange(finalKellyW1)
        finalKellyChangeW0 = calChange(finalKellyW0)

        finalKellyW3 = finalKellyW3[0:4]
        finalKellyW1 = finalKellyW1[0:4]
        finalKellyW0 = finalKellyW0[0:4]

        finalReturnPer = finalOdd.xpath('td[%s]/text()' %(12+shift)).extract_first()

        print('==========final odds group==========')
        print(finalOddW3)
        print(finalOddW1)
        print(finalOddW0)

        print(finalPerW3)
        print(finalPerW1)
        print(finalPerW0)

        print(finalKellyW3)
        print(finalKellyW1)
        print(finalKellyW0)

        print(finalKellyChangeW3)
        print(finalKellyChangeW1)
        print(finalKellyChangeW0)

        print(finalReturnPer)

        startOdd = williamHillOdds.xpath('tr[last()]')

        startOddTime = startOdd.xpath('td[1]/text()').extract_first()

        startOddTimeSp = exChangeTime(startOdd.xpath('td[2]/text()').extract_first())

        startOddW3 = startOdd.xpath('td[%s]/text()' %(3+shift)).extract_first()
        startOddW1 = startOdd.xpath('td[%s]/text()' %(4+shift)).extract_first()
        startOddW0 = startOdd.xpath('td[%s]/text()' %(5+shift)).extract_first()

        startPerW3 = startOdd.xpath('td[%s]/text()' %(6+shift)).extract_first()
        startPerW1 = startOdd.xpath('td[%s]/text()' %(7+shift)).extract_first()
        startPerW0 = startOdd.xpath('td[%s]/text()' %(8+shift)).extract_first()

        startKellyW3 = startOdd.xpath('td[%s]/text()' %(9+shift)).extract_first()
        startKellyW1 = startOdd.xpath('td[%s]/text()' %(10+shift)).extract_first()
        startKellyW0 = startOdd.xpath('td[%s]/text()' %(11+shift)).extract_first()

        startReturnPer = startOdd.xpath('td[%s]/text()' %(12+shift)).extract_first()


        print('==========start odds group==========')
        print(startOddTime)
        print(startOddTimeSp)

        print(startOddW3)
        print(startOddW1)
        print(startOddW0)

        print(startPerW3)
        print(startPerW1)
        print(startPerW0)

        print(startKellyW3)
        print(startKellyW1)
        print(startKellyW0)

        print(startReturnPer)

        changeOdds = williamHillOdds.xpath('tr')

        loopEnd = len(changeOdds)-1+shift
        for i in range(4+shift,loopEnd):
            print('==========one odds group==========')
            tmpOdd = changeOdds[i]

            OddTime = tmpOdd.xpath('td[1]/text()').extract_first()
            OddTimeSp = exChangeTime(tmpOdd.xpath('td[2]/text()').extract_first())

            OddW3 = tmpOdd.xpath('td[%s]/span/text()' %(3+shift)).extract_first()
            OddW1 = tmpOdd.xpath('td[%s]/span/text()' %(4+shift)).extract_first()
            OddW0 = tmpOdd.xpath('td[%s]/span/text()' %(5+shift)).extract_first()

            OddChangeW3 = 0
            OddChangeW1 = 0
            OddChangeW0 = 0

            if not OddW3:
                OddW3 = tmpOdd.xpath('td[%s]/text()' %(3+shift)).extract_first()
            if not OddW1:
                OddW1 = tmpOdd.xpath('td[%s]/text()' %(4+shift)).extract_first()
            if not OddW0:
                OddW0 = tmpOdd.xpath('td[%s]/text()' %(5+shift)).extract_first()

            OddChangeW3 = calChange(OddW3)
            OddChangeW1 = calChange(OddW1)
            OddChangeW0 = calChange(OddW0)
            OddW3 = OddW3[0:4]
            OddW1 = OddW1[0:4]
            OddW0 = OddW0[0:4]

            perW3 = tmpOdd.xpath('td[%s]/text()' %(6+shift)).extract_first()
            perW1 = tmpOdd.xpath('td[%s]/text()' %(7+shift)).extract_first()
            perW0 = tmpOdd.xpath('td[%s]/text()' %(8+shift)).extract_first()

            kellyW3 = tmpOdd.xpath('td[%s]/text()' %(9+shift)).extract_first()
            kellyW1 = tmpOdd.xpath('td[%s]/text()' %(10+shift)).extract_first()
            kellyW0 = tmpOdd.xpath('td[%s]/text()' %(11+shift)).extract_first()

            kellyChangeW3 = 0
            kellyChangeW1 = 0
            kellyChangeW0 = 0

            returnPer = tmpOdd.xpath('td[%s]/text()' %(12+shift)).extract_first()

            print(OddTime)
            print(OddTimeSp)

            print(OddW3)
            print(OddChangeW3)

            print(OddW1)
            print(OddChangeW1)

            print(OddW0)
            print(OddChangeW0)

            print(perW3)
            print(perW1)
            print(perW0)

            print(kellyW3)
            print(kellyChangeW3)

            print(kellyW1)
            print(kellyChangeW1)

            print(kellyW0)
            print(kellyChangeW0)

            print(returnPer)


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
})

process.crawl(T3Spider)
process.start()  # the script will block here until the crawling is finished
