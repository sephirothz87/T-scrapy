import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request, HtmlResponse
from scrapy.selector import Selector
import re
import time
import SoccerUtil as su
import logging
from logging import debug as d, info as i, warning as w, error as e, critical as c

# 因为在取16-17数值的时候就遇到了数据丢失的情况，不得已再写一个纯粹一点的版本来做基础数据
# 不能再从赔率变化页面取初始赔率和最终赔率了，而是要从比赛详情页取，这样也能更简单些
# 想取详细信息要趁早，基本各大联赛结束之后就去抓一波整个赛季的
# 能做数据整个的话尽量做个整个
# 英超
# 从07-08赛季开始才有赔率信息
# 从09-10赛季开始有让球赔率信息
# 10-11赛季才有赔率变化信息     但赔率变化信息也不全

labBrokes = su.BET_COMPANY['LAD_BROKES']
williamHill = su.BET_COMPANY['WILLIAM_HILL']

league = su.LEAGUE['ENGLAND_PREMIER_LEAGUE']
leagueCode = league['code']
leagueName = league['name']

seasonName = '16-17'
seasonCode = league['season_codes'][seasonName]

# 想取多少轮数据
# roundWantget = league['round']
# roundWantget = 26
roundWantget = 1

# 从第几轮开始取
roundWantStart = 1

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

resultData = []


class T6Spider(scrapy.Spider):
    name = 'T6Spider'

    # 因为第一步就是批量取，先随便发个请求，确认是一个有返回的请求即可
    start_urls = ['https://www.baidu.com']

    def parse(self, response):

        headers = {
            'User-Agent': su.USER_AGENT,
            'Connection': 'keep-alive',
            'Referer': 'http://www.okooo.com/soccer/match/877199/odd/',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': su.COOKIE
        }

        url = 'http://www.okooo.com/soccer/match/877199/odds/ajax/?page=0&trnum=0&companytype=BaijiaBooks&type=1'
        yield Request(url=url, headers=headers, callback=self.parseTrue)

    def parseTrue(self,response):
        # d(response)
        # d(response.body)
        # d(response.text)

        sel = Selector(response)
        # print(sel.extract())

        oddLine = sel.xpath('//tr[@id="tr82"]')
        print(oddLine.extract())





process = CrawlerProcess({
    'USER_AGENT': su.USER_AGENT
})

process.crawl(T6Spider)
process.start()  # the script will block here until the crawling is finished

resultCsvFile = '../../report/' + time.strftime("%Y-%m-%d-%H%M%S", time.localtime()) + '.csv'

def single(value):
    value = str(value)
    if value.startswith('{'):
        return '"' + value + '"'
    else:
        return value

def writeCsv(fileName, matchObj):
    f = open(fileName, 'a')
    line = ','.join(map(single, matchObj.values()))

    f.write(line)
    f.write('\n')
    f.close()

# for matchData in resultData:
#     writeCsv(resultCsvFile, matchData)
