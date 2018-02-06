import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request,HtmlResponse
import re

# 按照联赛-轮次-球队查询比赛基本信息

ENGLAND_PREMIER_LEAGUE = 17
ENGLAND_PREMIER_LEAGUE_MATCH_PER_TURN = 10
SEASON_ENGLAND_PREMIER_LEAGUE_17_18 = 13222
# TOTAL_ROUND = 26
TOTAL_ROUND = 1

# 博彩公司代号
WILLIAM_HILL = 14
LAD_BROKES = 82

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
#如果获取失败，重新去网站刷新一下cookie
COOKIE = '__utmc=56961525; LastUrl=; FirstOKURL=http%3A//www.okooo.com/jingcai/; First_Source=www.okooo.com; Hm_lvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1517120624; Last_Source=http%3A//www.okooo.com/soccer/match/876722/odds/; IMUserName=ok_025742692071; __utmz=56961525.1517821150.16.3.utmcsr=okooo.com|utmccn=(referral)|utmcmd=referral|utmcct=/jingcai/2018-02-03/; __utma=56961525.95899878.1517120624.1517833475.1517848115.18; data_start_isShow=1; PHPSESSID=d932002d848166585fd346e771a90c5131becbce; Hm_lpvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1517849579; __utmb=56961525.53.8.1517849580034; DRUPAL_LOGGED_IN=Y; IMUserID=24006237; OkAutoUuid=b8b92c071a5ba1185c065aa6d9a2175b; OkMsIndex=5; isInvitePurview=0; UWord=5a9291a00f6e4c9e03f939fab73258b3a2d'

league = ENGLAND_PREMIER_LEAGUE
season = SEASON_ENGLAND_PREMIER_LEAGUE_17_18
# match_per_turn = 10

def calChange(str):
    if str.endswith('↑'):
        return 1
    elif str.endswith('↓'):
        return -1
    else:
        return 0

def exChangeTime(str):
    reg = r'\D*(\d+)\D+(\d+)\D+'
    return re.sub(reg,r'\1:\2',str)

class S2Spider(scrapy.Spider):
    name = 'S2Spider'
    start_urls = ['http://www.baidu.com']

    def parse(self,response):
        print('parse')

        for i in range(1,TOTAL_ROUND+1):
            round_url = 'http://www.okooo.com/soccer/league/%s/schedule/%s/1-1-%s/' %(league, season, i)

            headers = {
                'User-Agent': USER_AGENT,
                'Connection': 'keep-alive',
                'Referer': round_url,
                'Cookie': COOKIE
            }

            meta = {
                'round':i
            }

            print('Round %s' %(i))
            yield Request(url=round_url,headers=headers,callback=self.parseRound,meta=meta)


    def parseRound(self, response):
        print('parseRound')
        matches = response.xpath('//*[@id="team_fight_table"]/tr')
        # print(matches.extract())

        # for i in range(2, match_per_turn + 2):
        for i in range(1, len(matches)):
            print('Round:',response.meta['round'],'Match:',i)
            # match = matches.xpath('tr[%s]' %(i))
            match = matches[i]
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

            # oddDetailUrl = 'http://www.okooo.com/soccer/match/%s/odds/' % (id)
            # hoddDetailUrl = 'http://www.okooo.com/soccer/match/%s/hodds/' % (id)

            headers = {
                'User-Agent': USER_AGENT,
                'Connection': 'keep-alive',
                'Referer': 'http://www.okooo.com/soccer/match/%s/' %(id),
                'Cookie': COOKIE
            }

            meta = response.meta

            meta.update({
                'id':id,
                'match':i,
                'vs':'%s %s %s' %(teamHome,scoreText,teamAway),
                'odd_l_group':False,
                'odd_w_group': False,
                'hodd_w_group': False,
            })

            # meta = {
            #     'round': response.meta['round'],
            #     'match': i,
            #     'vs': '%s %s %s' % (teamHome, scoreText, teamAway)
            # }

            #获取立博详细赔率
            oddLadBrokesDetailUrl = 'http://www.okooo.com/soccer/match/%s/odds/change/%s/' %(id,LAD_BROKES)
            yield scrapy.Request(url=oddLadBrokesDetailUrl,headers=headers,callback=self.parseOddsDetail,meta=meta)

    def parseOddsDetail(self, response):
        print('parseOddsDetail')
        print('Round:', response.meta['round'],'Match:', response.meta['match'], response.meta['vs'])
        # print(response)
        # print(response.body)
        # print(response.url)
        # print()
        # print(response.extract())

        shift = 0

        if response.url.find('hodds') > 0:
            shift = 1

        oddsTable = response.xpath('/html/body/div[1]/table')

        # print(williamHillOdds.extract())

        finalOdd = oddsTable.xpath('tr[%s]' %(3+shift))

        finalOddTime = finalOdd.xpath('td[1]/text()').extract_first()

        finalOddTimeSp = exChangeTime(finalOdd.xpath('td[2]/text()').extract_first())

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

        startOdd = oddsTable.xpath('tr[last()]')

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

        changeOdds = oddsTable.xpath('tr')

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

        meta = response.meta

        #mock
        odd_group = ''
        # odd_group = {
        #
        # }

        headers = {
            'User-Agent': USER_AGENT,
            'Connection': 'keep-alive',
            'Referer': 'http://www.okooo.com/soccer/match/%s/' % (meta['id']),
            'Cookie': COOKIE
        }

        # if not meta['odd_l_request']:
        #     # 获取立博详细赔率
        #     meta.update({'odd_l_request': True})
        #     oddLadBrokesDetailUrl = 'http://www.okooo.com/soccer/match/%s/odds/change/%s/' % (meta['id'], LAD_BROKES)
        #     yield scrapy.Request(url=oddLadBrokesDetailUrl, headers=headers, callback=self.parseOddsDetail, meta=meta)
        if not meta['odd_l_group']:
            #更新立博赔率数据到结果中
            odd_group = 'mock odd_l_group'
            meta.update({'odd_l_group': odd_group})

            hodd='-1'
            if float(startOddW3)>float(startOddW0):
                hodd='1'

            meta.update({'hodd':hodd})

            # hoddLadBrokesDetailUrl = 'http://www.okooo.com/soccer/match/%s/hodds/change/%s/?boundary=%s' % (meta['id'], LAD_BROKES, hodd)
            oddWilliamHillDetailUrl = 'http://www.okooo.com/soccer/match/%s/odds/change/%s/' % (meta['id'], WILLIAM_HILL)

            #取威廉希尔的赔率
            yield scrapy.Request(url=oddWilliamHillDetailUrl, headers=headers, callback=self.parseOddsDetail, meta=meta)
        elif not meta['odd_w_group']:
            # 更新威廉希尔赔率数据到结果中
            odd_group = 'mock odd_w_group'
            meta.update({'odd_w_group': odd_group})

            hoddWilliamHillDetailUrl = 'http://www.okooo.com/soccer/match/%s/hodds/change/%s/?boundary=%s' % (meta['id'], WILLIAM_HILL, meta['hodd'])

            #取威廉希尔的让球赔率
            yield scrapy.Request(url=hoddWilliamHillDetailUrl, headers=headers, callback=self.parseOddsDetail, meta=meta)
        elif not meta['hodd_w_group']:
            # 更新威廉希尔的让球赔率数据到结果中
            odd_group = 'mock hodd_w_group'
            meta.update({'hodd_w_group': odd_group})
            print(meta)

process = CrawlerProcess({
    'USER_AGENT': USER_AGENT
})

process.crawl(S2Spider)
process.start()  # the script will block here until the crawling is finished