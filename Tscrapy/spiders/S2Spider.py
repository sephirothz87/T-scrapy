import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request,HtmlResponse
import re
import time

# 按照联赛-轮次-球队查询比赛基本信息

ENGLAND_PREMIER_LEAGUE_CODE = 17
ENGLAND_PREMIER_LEAGUE_NAME = '英超'
ENGLAND_PREMIER_LEAGUE_MATCH_PER_TURN = 10
SEASON_ENGLAND_PREMIER_LEAGUE_17_18 = 13222
TOTAL_ROUND = 26
# TOTAL_ROUND = 1

# 博彩公司代号
WILLIAM_HILL = 14
LAD_BROKES = 82

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
#如果获取失败，重新去网站刷新一下cookie
COOKIE = '__utmc=56961525; LastUrl=; FirstOKURL=http%3A//www.okooo.com/jingcai/; First_Source=www.okooo.com; Hm_lvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1517120624; Last_Source=http%3A//www.okooo.com/soccer/match/876722/odds/; IMUserName=ok_025742692071; __utmz=56961525.1517821150.16.3.utmcsr=okooo.com|utmccn=(referral)|utmcmd=referral|utmcct=/jingcai/2018-02-03/; __utma=56961525.95899878.1517120624.1517833475.1517848115.18; data_start_isShow=1; PHPSESSID=d932002d848166585fd346e771a90c5131becbce; Hm_lpvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1517849579; __utmb=56961525.53.8.1517849580034; DRUPAL_LOGGED_IN=Y; IMUserID=24006237; OkAutoUuid=b8b92c071a5ba1185c065aa6d9a2175b; OkMsIndex=5; isInvitePurview=0; UWord=5a9291a00f6e4c9e03f939fab73258b3a2d'

leagueCode = ENGLAND_PREMIER_LEAGUE_CODE
leagueName = ENGLAND_PREMIER_LEAGUE_NAME
seasonCode = SEASON_ENGLAND_PREMIER_LEAGUE_17_18
seasonName = '17-18'
# match_per_turn = 10

resultData = []

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
        # print('parse')

        meta = {
            'match':{}
        }

        for i in range(1,TOTAL_ROUND+1):
            round_url = 'http://www.okooo.com/soccer/league/%s/schedule/%s/1-1-%s/' %(leagueCode, seasonCode, i)

            headers = {
                'User-Agent': USER_AGENT,
                'Connection': 'keep-alive',
                'Referer': round_url,
                'Cookie': COOKIE
            }

            meta['match'].update({
                'round':i
            })

            # print('Round %s' %(i))
            yield Request(url=round_url,headers=headers,callback=self.parseRound,meta=meta)


    def parseRound(self, response):
        # print('parseRound')
        matches = response.xpath('//*[@id="team_fight_table"]/tr')

        for i in range(1, len(matches)):
            # print('Round:',response.meta['match']['round'],'Match:',i)
            # match = matches.xpath('tr[%s]' %(i))
            matchPath = matches[i]
            # print(match.extract())

            matchId = matchPath.xpath('@matchid').extract_first()
            startTime = matchPath.xpath('td[1]/text()').extract_first()
            teamHome = matchPath.xpath('td[3]/text()').extract_first()
            teamAway = matchPath.xpath('td[5]/text()').extract_first().strip()
            scoreText = matchPath.xpath('td[4]/a/strong/text()').extract_first()
            goalHome = int(scoreText.split('-')[0])
            goalAway = int(scoreText.split('-')[1])

            resultCode = -1
            if goalHome>goalAway:
                resultCode = 3
            elif goalHome<goalAway:
                resultCode = 0
            else:
                resultCode = 1

            headers = {
                'User-Agent': USER_AGENT,
                'Connection': 'keep-alive',
                'Referer': 'http://www.okooo.com/soccer/match/%s/' %(matchId),
                'Cookie': COOKIE
            }

            meta = {}

            meta={
                'odd_l_group': False,
                'odd_w_group': False,
                'hodd_w_group': False
            }
            meta['match']={
                'matchId':matchId,
                'leagueCode':leagueCode,
                'leagueName':leagueName,
                'seasonCode':seasonCode,
                'seasonName':seasonName,
                'round':response.meta['match']['round'],
                'vsText':'%s %s %s' %(teamHome,scoreText,teamAway),
                'matchIndex':i,
                'startTime':startTime,
                'teamHome':teamHome,
                'teamAway':teamAway,
                'goalHome':goalHome,
                'goalAway':goalAway,
                'scoreText':scoreText,
                'resultCode':resultCode
            }

            #获取立博详细赔率
            oddLadBrokesDetailUrl = 'http://www.okooo.com/soccer/match/%s/odds/change/%s/' %(matchId,LAD_BROKES)
            yield scrapy.Request(url=oddLadBrokesDetailUrl,headers=headers,callback=self.parseOddsDetail,meta=meta)

    def parseOddsDetail(self, response):
        # print('parseOddsDetail')
        # print('Round:', response.meta['match']['round'],'Match:', response.meta['match']['matchId'], response.meta['match']['vsText'])

        meta = response.meta
        curOddGroup = {}
        oddStartObj = {}
        oddEndObj = {}

        shift = 0
        # curOddGroup['hodd'] =
        tmpHoddNum = '0'

        url = response.url
        if url.find('hodds') > 0:
            shift = 1
            if url.rfind('-')>0:
                tmpHoddNum = url[len(url) - 2:]
            else:
                tmpHoddNum = url[len(url) - 1:]
        else:
            tmpHoddNum = '0'

        oddsTable = response.xpath('/html/body/div[1]/table')

        # print(williamHillOdds.extract())

        finalOdd = oddsTable.xpath('tr[%s]' %(3+shift))

        finalOddTime = finalOdd.xpath('td[1]/text()').extract_first()

        finalOddTimeSp = exChangeTime(finalOdd.xpath('td[2]/text()').extract_first())

        finalOdd3 = finalOdd.xpath('td[%s]/text()' %(3+shift)).extract_first()
        finalOdd1 = finalOdd.xpath('td[%s]/text()' %(4+shift)).extract_first()
        finalOdd0 = finalOdd.xpath('td[%s]/text()' %(5+shift)).extract_first()

        finalProb3 = finalOdd.xpath('td[%s]/text()' %(6+shift)).extract_first()
        finalProb1 = finalOdd.xpath('td[%s]/text()' %(7+shift)).extract_first()
        finalProb0 = finalOdd.xpath('td[%s]/text()' %(8+shift)).extract_first()

        finalKellyW3 = finalOdd.xpath('td[%s]/span/text()' %(9+shift)).extract_first()
        finalKellyW1 = finalOdd.xpath('td[%s]/span/text()' %(10+shift)).extract_first()
        finalKellyW0 = finalOdd.xpath('td[%s]/span/text()' %(11+shift)).extract_first()

        finalKellyReg3 = 0
        finalKellyReg1 = 0
        finalKellyReg0 = 0

        if not finalKellyW3:
            finalKellyW3 = finalOdd.xpath('td[%s]/text()' %(9+shift)).extract_first()
        if not finalKellyW1:
            finalKellyW1 = finalOdd.xpath('td[%s]/text()' %(10+shift)).extract_first()
        if not finalKellyW0:
            finalKellyW0 = finalOdd.xpath('td[%s]/text()' %(11+shift)).extract_first()

        finalKellyReg3 = calChange(finalKellyW3)
        finalKellyReg1 = calChange(finalKellyW1)
        finalKellyReg0 = calChange(finalKellyW0)

        finalKellyW3 = finalKellyW3[0:4]
        finalKellyW1 = finalKellyW1[0:4]
        finalKellyW0 = finalKellyW0[0:4]

        finalReturnProb = finalOdd.xpath('td[%s]/text()' %(12+shift)).extract_first()

        oddEndObj = {
            'hoddNum':tmpHoddNum,
            'time':finalOddTime,
            'timeSp':finalOddTimeSp,
            'odd3':finalOdd3,
            'odd1':finalOdd1,
            'odd0':finalOdd0,
            'reg3':0,
            'reg1':0,
            'reg0':0,
            'prob3':finalProb3,
            'prob1':finalProb1,
            'prob0':finalProb0,
            'kelly3':finalKellyW3,
            'kelly1':finalKellyW1,
            'kelly0':finalKellyW0,
            'kellyReg3':finalKellyReg3,
            'kellyReg1':finalKellyReg1,
            'kellyReg0':finalKellyReg0,
            'returnProb':finalReturnProb
        }
        curOddGroup['oddEnd'] = oddEndObj

        startOdd = oddsTable.xpath('tr[last()]')

        startOddTime = startOdd.xpath('td[1]/text()').extract_first()

        startOddTimeSp = exChangeTime(startOdd.xpath('td[2]/text()').extract_first())

        startOdd3 = startOdd.xpath('td[%s]/text()' %(3+shift)).extract_first()
        startOdd1 = startOdd.xpath('td[%s]/text()' %(4+shift)).extract_first()
        startOdd0 = startOdd.xpath('td[%s]/text()' %(5+shift)).extract_first()

        startProb3 = startOdd.xpath('td[%s]/text()' %(6+shift)).extract_first()
        startProb1 = startOdd.xpath('td[%s]/text()' %(7+shift)).extract_first()
        startProb0 = startOdd.xpath('td[%s]/text()' %(8+shift)).extract_first()

        startKelly3 = startOdd.xpath('td[%s]/text()' %(9+shift)).extract_first()
        startKelly1 = startOdd.xpath('td[%s]/text()' %(10+shift)).extract_first()
        startKelly0 = startOdd.xpath('td[%s]/text()' %(11+shift)).extract_first()

        startReturnProb = startOdd.xpath('td[%s]/text()' %(12+shift)).extract_first()

        oddStartObj = {
            'hoddNum':tmpHoddNum,
            'time':startOddTime,
            'timeSp':startOddTimeSp,
            'odd3':startOdd3,
            'odd1':startOdd1,
            'odd0':startOdd0,
            'reg3':0,
            'reg1':0,
            'reg0':0,
            'prob3':startProb3,
            'prob1':startProb1,
            'prob0':startProb0,
            'kelly3':startKelly3,
            'kelly1':startKelly1,
            'kelly0':startKelly0,
            'kellyReg3':0,
            'kellyReg1':0,
            'kellyReg0':0,
            'returnProb':startReturnProb
        }
        curOddGroup['oddStartObj'] = oddStartObj

        changeOdds = oddsTable.xpath('tr')
        oddChangeGroup = []

        loopEnd = len(changeOdds)-1+shift
        for i in range(4+shift,loopEnd):
            # print('==========one odds group==========')
            tmpOdd = changeOdds[i]

            oddTime = tmpOdd.xpath('td[1]/text()').extract_first()
            oddTimeSp = exChangeTime(tmpOdd.xpath('td[2]/text()').extract_first())

            odd3 = tmpOdd.xpath('td[%s]/span/text()' %(3+shift)).extract_first()
            odd1 = tmpOdd.xpath('td[%s]/span/text()' %(4+shift)).extract_first()
            odd0 = tmpOdd.xpath('td[%s]/span/text()' %(5+shift)).extract_first()

            reg3 = 0
            reg3 = 0
            reg0 = 0

            if not odd3:
                odd3 = tmpOdd.xpath('td[%s]/text()' %(3+shift)).extract_first()
            if not odd1:
                odd1 = tmpOdd.xpath('td[%s]/text()' %(4+shift)).extract_first()
            if not odd0:
                odd0 = tmpOdd.xpath('td[%s]/text()' %(5+shift)).extract_first()

            reg3 = calChange(odd3)
            reg1 = calChange(odd1)
            reg0 = calChange(odd0)
            odd3 = odd3[0:4]
            odd1 = odd1[0:4]
            odd0 = odd0[0:4]

            prob3 = tmpOdd.xpath('td[%s]/text()' %(6+shift)).extract_first()
            prob1 = tmpOdd.xpath('td[%s]/text()' %(7+shift)).extract_first()
            prob0 = tmpOdd.xpath('td[%s]/text()' %(8+shift)).extract_first()

            kelly3 = tmpOdd.xpath('td[%s]/text()' %(9+shift)).extract_first()
            kelly1 = tmpOdd.xpath('td[%s]/text()' %(10+shift)).extract_first()
            kelly0 = tmpOdd.xpath('td[%s]/text()' %(11+shift)).extract_first()

            kellyChangeW3 = 0
            kellyChangeW1 = 0
            kellyChangeW0 = 0

            returnProb = tmpOdd.xpath('td[%s]/text()' %(12+shift)).extract_first()

            oddChangeGroup.append({
                'hoddNum':tmpHoddNum,
                'time':oddTime,
                'timeSp':oddTimeSp,
                'odd3':odd3,
                'odd1':odd1,
                'odd0':odd0,
                'reg3':reg3,
                'reg1':reg1,
                'reg0':reg0,
                'prob3':prob3,
                'prob1':prob1,
                'prob0':prob0,
                'kelly3':kelly3,
                'kelly1':kelly1,
                'kelly0':kelly0,
                'kellyReg3':0,
                'kellyReg1':0,
                'kellyReg0':0,
                'returnProb':returnProb
            })

        curOddGroup['oddChangeGroup'] = oddChangeGroup
        #mock
        # odd_group = ''
        # odd_group = {
        #
        # }

        headers = {
            'User-Agent': USER_AGENT,
            'Connection': 'keep-alive',
            'Referer': 'http://www.okooo.com/soccer/match/%s/' % (meta['match']['matchId']),
            'Cookie': COOKIE
        }

        if not meta['odd_l_group']:
            #更新立博赔率数据到结果中
            # odd_group = 'mock odd_l_group'
            # meta.update({'odd_l_group': True})
            # meta['match'].update({
            #     'oddChangeGroupLadBrode':curOddGroup
            # })

            meta['odd_l_group'] = True
            meta['match']['oddChangeGroupLadBrokes'] = curOddGroup

            hoddNum='-1'
            if float(startOdd3)>float(startOdd0):
                hoddNum='1'

            hodd = int(hoddNum)
            goal_h = meta['match']['goalHome'] + hodd
            goal_a = meta['match']['goalAway']

            hResultCode = -1
            if goal_h > goal_a:
                hResultCode = 3
            elif goal_h < goal_a:
                hResultCode = 0
            else:
                hResultCode = 1

            meta['match'].update({
                'hResultCode':hResultCode,
                'hoddNum':hoddNum,
                'oddFinalLadBrokes3':finalOdd3,
                'oddFinalLadBrokes1':finalOdd1,
                'oddFinalLadBrokes0':finalOdd0,
                'probLadBrokes3':finalProb3,
                'probLadBrokes1':finalProb1,
                'probLadBrokes0':finalProb0,
                'kellyLadBrokes3':finalKellyW3,
                'kellyLadBrokes1':finalKellyW1,
                'kellyLadBrokes0':finalKellyW0,
                'kellyReg3':finalKellyReg3,
                'kellyReg1':finalKellyReg1,
                'kellyReg0':finalKellyReg0,
                'returnProbLadBrokes':finalReturnProb,
                'oddStartLadBrokes3': startOdd3,
                'oddStartLadBrokes1': startOdd1,
                'oddStartLadBrokes0': startOdd0,
            })

            # hoddLadBrokesDetailUrl = 'http://www.okooo.com/soccer/match/%s/hodds/change/%s/?boundary=%s' % (meta['id'], LAD_BROKES, hoddNum)
            oddWilliamHillDetailUrl = 'http://www.okooo.com/soccer/match/%s/odds/change/%s/' % (meta['match']['matchId'], WILLIAM_HILL)

            #取威廉希尔的赔率
            yield scrapy.Request(url=oddWilliamHillDetailUrl, headers=headers, callback=self.parseOddsDetail, meta=meta)
        elif not meta['odd_w_group']:
            # 更新威廉希尔赔率数据到结果中
            # odd_group = 'mock odd_w_group'
            # meta.update({'odd_w_group': odd_group})

            meta['odd_w_group'] = True
            meta['match']['oddChangeGroupWillamHill'] = curOddGroup

            hoddWilliamHillDetailUrl = 'http://www.okooo.com/soccer/match/%s/hodds/change/%s/?boundary=%s' % (meta['match']['matchId'], WILLIAM_HILL, meta['match']['hoddNum'])

            #取威廉希尔的让球赔率
            yield scrapy.Request(url=hoddWilliamHillDetailUrl, headers=headers, callback=self.parseOddsDetail, meta=meta)
        elif not meta['hodd_w_group']:
            # 更新威廉希尔的让球赔率数据到结果中
            # odd_group = 'mock hodd_w_group'
            # meta.update({'hodd_w_group': odd_group})

            meta['hodd_w_group'] = True
            meta['match']['hoddChangeGroupWillamHill'] = curOddGroup
            meta['match'].update({
                'hoddWillamHill3':finalOdd3,
                'hoddWillamHill1':finalOdd1,
                'hoddWillamHill0':finalOdd0
            })
            # print(meta)
            print(meta['match'])
            resultData.append(meta['match'])

process = CrawlerProcess({
    'USER_AGENT': USER_AGENT
})

process.crawl(S2Spider)
process.start()  # the script will block here until the crawling is finished

# print(resultData)
# print(type(resultData))
# print(resultData[0])
# print(resultData[0].values())
# ssss = ','.join(map(str,resultData[0].values()))
# print(ssss)

# resultCsvFile = '../report/'+time.strftime("%Y-%m-%d-%H%M%S", time.localtime())+'.csv'
resultCsvFile = time.strftime("%Y-%m-%d-%H%M%S", time.localtime())+'.csv'
print(resultCsvFile)

def single(value):
    value = str(value)
    if value.startswith('{'):
        return '"'+value+'"'
    else:
        return value

def writeCsv(fileName,matchObj):
    f = open(fileName,'a')
    line = ','.join(map(single,matchObj.values()))

    f.write(line)
    f.write('\n')
    f.close()

for matchData in resultData:
    writeCsv(resultCsvFile,matchData)