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
# 有些数据丢了的，16-17第12轮，热刺vs西汉姆联，完全没有数据，我这边也不要这场了

labBrokes = su.BET_COMPANY['LAD_BROKES']['code']
williamHill = su.BET_COMPANY['WILLIAM_HILL']['code']

league = su.LEAGUE['ENGLAND_PREMIER_LEAGUE']
leagueCode = league['code']
leagueName = league['name']

seasonName = '17-18'
# seasonName = '16-17'
seasonCode = league['season_codes'][seasonName]

# 想取多少轮数据
# roundWantget = league['round']
roundWantget = 26
# roundWantget = 1

# 从第几轮开始取
roundWantStart = 1

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
cookie = su.COOKIE
# cookie = 'LastUrl=; FirstOKURL=http%3A//www.okooo.com/jingcai/; First_Source=www.okooo.com; Last_Source=http%3A//www.okooo.com/soccer/match/876722/odds/; data_start_isShow=1; OkAutoUuid=b8b92c071a5ba1185c065aa6d9a2175b; OkMsIndex=5; __utmc=56961525; isInvitePurview=0; PHPSESSID=f3438442d0a40ccd389ab57fc3e7620c9536b916; Hm_lvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1517120624,1517893507; IMUserID=24006237; IMUserName=ok_025742692071; __utmz=56961525.1518109164.32.9.utmcsr=okooo.com|utmccn=(referral)|utmcmd=referral|utmcct=/soccer/league/17/schedule/2746/; DRUPAL_LOGGED_IN=Y; __utma=56961525.95899878.1517120624.1518121003.1518123415.35; UWord=d411d8cd987f00b204e9800998ecf84527e; __utmb=56961525.31.8.1518125819798; Hm_lpvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1518125837'
userAgent = su.USER_AGENT

resultData = []

def decodeOddLine(oddLine, isHodd):
    print('decodeOddLine')

    result = {}

    shift = 0
    if isHodd:
        shift = 1

    odd3 = oddLine.xpath('td[%s]/a/span/text()' % (6 + shift)).extract_first()
    odd1 = oddLine.xpath('td[%s]/a/span/text()' % (7 + shift)).extract_first()
    odd0 = oddLine.xpath('td[%s]/div/a/span/text()' % (8 + shift)).extract_first()

    oddStart3 = oddLine.xpath('td[%s]/span/text()' % (3 + shift)).extract_first()
    oddStart1 = oddLine.xpath('td[%s]/span/text()' % (4 + shift)).extract_first()
    oddStart0 = oddLine.xpath('td[%s]/span/text()' % (5 + shift)).extract_first()

    result.update({
        'odd3': odd3,
        'odd1': odd1,
        'odd0': odd0,
        'oddStart3': oddStart3,
        'oddStart1': oddStart1,
        'oddStart0': oddStart0,
    })

    if not isHodd:
        prob3 = oddLine.xpath('td[10]/span/text()').extract_first()
        prob1 = oddLine.xpath('td[11]/span/text()').extract_first()
        prob0 = oddLine.xpath('td[12]/span/text()').extract_first()

        kelly3 = oddLine.xpath('td[13]/span/text()').extract_first()
        kelly1 = oddLine.xpath('td[14]/span/text()').extract_first()
        kelly0 = oddLine.xpath('td[15]/span/text()').extract_first()

        returnProb = oddLine.xpath('td[16]/span/text()').extract_first()

        hoddNum = -1
        if float(oddStart3) > float(oddStart0):
            hoddNum = 1

        goal_h = meta['match']['goalHome'] + hoddNum
        goal_a = meta['match']['goalAway']

        hResultCode = -1
        if goal_h > goal_a:
            hResultCode = 3
        elif goal_h < goal_a:
            hResultCode = 0
        else:
            hResultCode = 1

        result.update({
            'hoddNum': hoddNum,
            'hResultCode': hResultCode,
            'prob3': prob3,
            'prob1': prob1,
            'prob0': prob0,
            'kelly3': kelly3,
            'kelly1': kelly1,
            'kelly0': kelly0,
            'returnProb': returnProb
        })

    return result


class S3Spider(scrapy.Spider):
    name = 'S3Spider'

    # 因为第一步就是批量取，先随便发个请求，确认是一个有返回的请求即可
    start_urls = ['https://www.baidu.com']

    def parse(self, response):
        d('parse')

        for i in range(roundWantStart, roundWantStart + roundWantget):
            round_url = 'http://www.okooo.com/soccer/league/%s/schedule/%s/1-1-%s/' % (leagueCode, seasonCode, i)

            headers = {
                'User-Agent': userAgent,
                'Connection': 'keep-alive',
                'Referer': round_url,
                'Cookie': cookie
            }

            meta = {
                'match': {}
            }

            meta['match'].update({
                'round': i
            })

            d('Round %s' % (i))
            yield Request(url=round_url, headers=headers, callback=self.parseRound, meta=meta)

    def parseRound(self, response):
        d('parseRound')
        roundIndex = response.meta['match']['round']
        matches = response.xpath('//*[@id="team_fight_table"]/tr')

        matchIndex = 0
        for i in range(1, len(matches)):
            matchPath = matches[i]

            scoreText = matchPath.xpath('td[4]/a/strong/text()').extract_first()

            # 延期比赛会当做一场全新的比赛来看待
            if scoreText == None and matchPath.xpath('td[4]/text()').extract_first().find('延期') > -1:
                d('延期')
                continue

            matchId = matchPath.xpath('@matchid').extract_first()
            startTime = matchPath.xpath('td[1]/text()').extract_first()
            teamHome = matchPath.xpath('td[3]/text()').extract_first()
            teamAway = matchPath.xpath('td[5]/text()').extract_first().strip()
            goalHome = int(scoreText.split('-')[0])
            goalAway = int(scoreText.split('-')[1])

            resultCode = -1
            if goalHome > goalAway:
                resultCode = 3
            elif goalHome < goalAway:
                resultCode = 0
            else:
                resultCode = 1

            meta = {}

            matchIndex += 1
            meta['match'] = {
                'matchId': matchId,
                'leagueCode': leagueCode,
                'leagueName': leagueName,
                'seasonCode': seasonCode,
                'seasonName': seasonName,
                'round': roundIndex,
                'vsText': '%s %s %s' % (teamHome, scoreText, teamAway),
                'matchIndex': matchIndex,
                'startTime': startTime,
                'teamHome': teamHome,
                'teamAway': teamAway,
                'goalHome': goalHome,
                'goalAway': goalAway,
                'scoreText': scoreText,
                'resultCode': resultCode
            }

            # 获取立博详细赔率
            # oddLadBrokesDetailUrl = 'http://www.okooo.com/soccer/match/%s/odds/change/%s/' %(matchId,LAD_BROKES)
            # yield scrapy.Request(url=oddLadBrokesDetailUrl,headers=headers,callback=self.parseOddsDetail,meta=meta)

            # 去比赛详细页面获得赔率
            # url = 'http://www.okooo.com/soccer/match/%s/odds/' % (matchId)
            url = 'http://www.okooo.com/soccer/match/%s/odds/ajax/?page=0&trnum=0&companytype=BaijiaBooks&type=1' % (
            matchId)
            # url = 'http://www.okooo.com/soccer/match/135290/odds/ajax/?page=0&trnum=0&companytype=BaijiaBooks&type=1'
            # 'http://www.okooo.com/soccer/match/877199/odds/ajax/?page=0&trnum=0&companytype=BaijiaBooks&type=1'

            # cookie = {
            #     '__utma':'56961525.95899878.1517120624.1518169593.1518186546.38',
            #     '__utmb':'56961525.5.9.1518186550970',
            #     '__utmc':'56961525',
            #     '__utmz':{'56961525.1518109164.32.9.utmcsr':'okooo.com|utmccn=(referral)|utmcmd=referral|utmcct=/soccer/league/17/schedule/2746/'},
            #     'data_start_isShow':'1',
            #     'DRUPAL_LOGGED_IN':'Y',
            #     'First_Source':'www.okooo.com',
            #     'FirstOKURL':'http%3A//www.okooo.com/jingcai/',
            #     'Hm_lpvt_5ffc07c2ca2eda4cc1c4d8e50804c94b':'1518186551',
            #     'Hm_lvt_5ffc07c2ca2eda4cc1c4d8e50804c94b':'1517120624,1517893507',
            #     'IMUserID':'24006237',
            #     'IMUserName':'ok_025742692071',
            #     'isInvitePurview':'0',
            #     'Last_Source':'http%3A//www.okooo.com/soccer/match/876722/odds/',
            #     'LastUrl':'',
            #     'OkAutoUuid':'b8b92c071a5ba1185c065aa6d9a2175b',
            #     'OkMsIndex':'5',
            #     'PHPSESSID':'f3438442d0a40ccd389ab57fc3e7620c9536b916',
            #     'UWord':'d441d8cd987f00b204e9800998ecf84927e'
            # }
            headers = {
                'User-Agent': userAgent,
                'Connection': 'keep-alive',
                'Referer': 'http://www.okooo.com/soccer/match/%s/odds/' % (matchId),
                # 'Cookie': cookie,
                # 'Cookie':'LastUrl=; FirstOKURL=http%3A//www.okooo.com/jingcai/; First_Source=www.okooo.com; Last_Source=http%3A//www.okooo.com/soccer/match/876722/odds/; data_start_isShow=1; OkAutoUuid=b8b92c071a5ba1185c065aa6d9a2175b; OkMsIndex=5; __utmc=56961525; isInvitePurview=0; PHPSESSID=f3438442d0a40ccd389ab57fc3e7620c9536b916; Hm_lvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1517120624,1517893507; IMUserID=24006237; IMUserName=ok_025742692071; __utmz=56961525.1518109164.32.9.utmcsr=okooo.com|utmccn=(referral)|utmcmd=referral|utmcct=/soccer/league/17/schedule/2746/; DRUPAL_LOGGED_IN=Y; __utma=56961525.95899878.1517120624.1518121003.1518123415.35; UWord=d411d8cd987f00b204e9800998ecf84527e; __utmb=56961525.37.8.1518126519745; Hm_lpvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1518126698',
                'X-Requested-With': 'XMLHttpRequest',
                'Accept-Language': 'zh-CN,zh;q=0.9,ja;q=0.8,en;q=0.7,zh-TW;q=0.6',
                'Accept': 'text/html, */*',
                'Pragma': 'no-cache',
                'Proxy-Connection': 'keep-alive'
            }
            # 'Origin:http://www.okooo.com'
            yield scrapy.Request(url=url, headers=headers, cookies=cookie, callback=self.parseOddsDetail, meta=meta)

    def parseOddsDetail(self, response):
        d('parseOddsDetail')
        # d(type(response))
        # d(response.text)
        # d(response.meta)

        # d('response.body')
        # d(response.body)

        meta = response.meta
        # i('Round: %s Match: %s %s' % (meta['match']['round'], meta['match']['matchId'], meta['match']['vsText']))

        # # startTime = response.xpath('body/div[4]/div[4]/div[1]/div/div[2]/p[1]/text()')
        # startTime = response.xpath('//div[@class="qbx_2"]')
        # # startTime = response.xpath('//div[@class="qbx_2"]/p[1]/text()')
        # d(startTime)

        # oddLine = response.xpath('//*[@id="tr82"]')
        # oddLine = response.xpath('/html/body/span[38]')
        # oddLine = response.xpath('*[@id="tr82"]')

        # sel = Selector(response)
        sel = Selector(response)
        oddLine = sel.xpath('//tr[@id="tr82"]')
        # oddLine = sel.xpath('/html/body/span[38]')

        # d('oddLine'+oddLine.extract_first())
        # d(oddLine.extract())

        if len(oddLine.extract()) > 0:
            # d('oddLine nnnnoooooooooooooooot None')
            # d('oddLine : ')
            # print('=================================',oddLine.extract_first(),'=================================',)
            # '/html/body/span[38]'
            odd3 = oddLine.xpath('td[6]/a/span/text()').extract_first()
            odd1 = oddLine.xpath('td[7]/a/span/text()').extract_first()
            odd0 = oddLine.xpath('td[8]/div/a/span/text()').extract_first()

            # d('odd3odd3odd3odd3odd3odd3odd3odd3odd3 : ')
            # d(odd3)

            oddStart3 = oddLine.xpath('td[3]/span/text()').extract_first()
            oddStart1 = oddLine.xpath('td[4]/span/text()').extract_first()
            oddStart0 = oddLine.xpath('td[5]/span/text()').extract_first()

            prob3 = oddLine.xpath('td[10]/span/text()').extract_first()
            prob1 = oddLine.xpath('td[11]/span/text()').extract_first()
            prob0 = oddLine.xpath('td[12]/span/text()').extract_first()

            kelly3 = oddLine.xpath('td[13]/span/text()').extract_first()
            kelly1 = oddLine.xpath('td[14]/span/text()').extract_first()
            kelly0 = oddLine.xpath('td[15]/span/text()').extract_first()

            returnProb = oddLine.xpath('td[16]/span/text()').extract_first()

            hoddNum = -1
            if float(oddStart3) > float(oddStart0):
                hoddNum = 1

            goal_h = meta['match']['goalHome'] + hoddNum
            goal_a = meta['match']['goalAway']

            hResultCode = -1
            if goal_h > goal_a:
                hResultCode = 3
            elif goal_h < goal_a:
                hResultCode = 0
            else:
                hResultCode = 1

            meta['match'].update({
                # 'startTime': startTime,
                'hoddNum': hoddNum,
                'hResultCode': hResultCode,
                'odd3': odd3,
                'odd1': odd1,
                'odd0': odd0,
                'prob3': prob3,
                'prob1': prob1,
                'prob0': prob0,
                'kelly3': kelly3,
                'kelly1': kelly1,
                'kelly0': kelly0,
                'returnProb': returnProb,
                'oddStart3': oddStart3,
                'oddStart1': oddStart1,
                'oddStart0': oddStart0,
            })

            # d(meta)

            headers = {
                'User-Agent': userAgent,
                'Connection': 'keep-alive',
                'Referer': 'http://www.okooo.com/soccer/match/%s/' % (meta['match']['matchId']),
                'X-Requested-With': 'XMLHttpRequest',
                # 'Cookie': su.COOKIE
            }

            # 去比赛让球详细页面获得赔率
            # url = 'http://www.okooo.com/soccer/match/%s/hodds/' % (meta['match']['matchId'])
            # yield scrapy.Request(url=url, headers=headers, callback=self.parseHoddsDetail, meta=meta)
            url = 'http://www.okooo.com/soccer/match/%s/hodds/ajax/?page=0&trnum=0&companytype=BaijiaBooks' % (
            meta['match']['matchId'])
            # yield scrapy.Request(url=url, headers=headers, callback=self.parseHoddsDetail, meta=meta)
            yield scrapy.Request(url=url, headers=headers, cookies=cookie, callback=self.parseHoddsDetail, meta=meta)
        else:
            w('no LabBroke odd')

    def parseHoddsDetail(self, response):
        d('parseHoddsDetail')

        meta = response.meta

        hodd = str(meta['match']['hoddNum'])

        oddLine = response.xpath('//tr[contains(@id,"%s") and td[3]/span/text()="%s"]' % (labBrokes, hodd))
        # oddLine = response.xpath('//tr[contains(@id,"%s")]' % (labBrokes))#这个可以用


        print(oddLine)
        print(oddLine.extract())

        if oddLine == []:
            print('no LabBrokes hodd')
            oddLine = response.xpath('//tr[contains(@id,"%s") and td[3]/span/text()="%s"]' % (williamHill, hodd))
            print(oddLine)
            print(oddLine.extract())
            hoddFrom = williamHill
        else:
            hoddFrom = labBrokes

        if oddLine != []:
            hodd3 = oddLine.xpath('td[7]/a/span/text()').extract_first()
            hodd1 = oddLine.xpath('td[8]/a/span/text()').extract_first()
            hodd0 = oddLine.xpath('td[9]/a/span/text()').extract_first()

            hoddStart3 = oddLine.xpath('td[4]/a/span/text()').extract_first()
            hoddStart1 = oddLine.xpath('td[5]/a/span/text()').extract_first()
            hoddStart0 = oddLine.xpath('td[6]/a/span/text()').extract_first()

            meta['match'].update({
                'hodd3':hodd3,
                'hodd1':hodd1,
                'hodd0':hodd0,
                'hoddStart3':hoddStart3,
                'hoddStart1':hoddStart1,
                'hoddStart0':hoddStart0,
                'hoddFrom':hoddFrom
            })
        else:
            w('no hodd found')

        #最后再去取一下精确时间
        match_url = 'http://www.okooo.com/soccer/match/%s/odds/' % (meta['match']['matchId'])
        round_url = 'http://www.okooo.com/soccer/league/%s/schedule/%s/1-1-%s/' % (leagueCode, seasonCode, i)

        headers = {
            'User-Agent': userAgent,
            'Connection': 'keep-alive',
            'Referer': round_url,
            'Cookie': cookie
        }

        yield scrapy.Request(url=match_url, headers=headers, cookies=cookie, callback=self.parserTime, meta=meta)

    def parserTime(self, response):
        d('parserTime')

        meta = response.meta

        # startTime = response.xpath('body/div[4]/div[4]/div[1]/div/div[2]/p[1]/text()').extract_first()
        # startTime = response.xpath('/html/body/div[4]/div[4]/div[1]/div/div[2]/p[1]')
        # startTime = response.xpath('//div[@class="qbx_2"]')
        startTime = response.xpath('//div[@class="qbx_2"]/p[1]/text()').extract_first()
        startTime = " ".join(startTime.split())#截去中间夹的\xa0 空格符&npsp
        print(startTime)
        # startTime.replace('\\xa0','')

        # sel = Selector(response)
        # startTime = sel.xpath('body')
        # startTime = sel.xpath('body/div[4]/div[4]/div[1]/div/div[2]/p[1]/text()')
        # startTime = sel.xpath('body/div[@class="qbx_2"]')

        d(startTime)

        meta['match'].update({
            'startTime': startTime
        })

        print(meta['match'])
        resultData.append(meta['match'])

process = CrawlerProcess({
    'USER_AGENT': su.USER_AGENT
})

process.crawl(S3Spider)
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

for matchData in resultData:
    writeCsv(resultCsvFile, matchData)
