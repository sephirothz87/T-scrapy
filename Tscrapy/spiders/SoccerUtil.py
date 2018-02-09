DEBUG = True
# 1 INFO级
DEBUG_LEVEL = 4
# Chrome
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'


# 如果获取失败，重新去网站刷新一下cookie
# COOKIE = 'LastUrl=; FirstOKURL=http%3A//www.okooo.com/jingcai/; First_Source=www.okooo.com; Last_Source=http%3A//www.okooo.com/soccer/match/876722/odds/; data_start_isShow=1; OkAutoUuid=b8b92c071a5ba1185c065aa6d9a2175b; OkMsIndex=5; __utmc=56961525; isInvitePurview=0; PHPSESSID=f3438442d0a40ccd389ab57fc3e7620c9536b916; Hm_lvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1517120624,1517893507; IMUserID=24006237; IMUserName=ok_025742692071; __utmz=56961525.1518109164.32.9.utmcsr=okooo.com|utmccn=(referral)|utmcmd=referral|utmcct=/soccer/league/17/schedule/2746/; DRUPAL_LOGGED_IN=Y; __utma=56961525.95899878.1517120624.1518121003.1518123415.35; UWord=d411d8cd987f00b204e9800998ecf84527e; __utmb=56961525.22.8.1518124182143; Hm_lpvt_5ffc07c2ca2eda4cc1c4d8e50804c94b=1518124185'


def calChange(str):
    if str.endswith('↑'):
        return 1
    elif str.endswith('↓'):
        return -1
    else:
        return 0


def exChangeTime(str):
    reg = r'\D*(\d+)\D+(\d+)\D+'
    return re.sub(reg, r'\1:\2', str)


# dubug用的log
def dp(val):
    if DEBUG:
        print(val)


LEAGUE = {
    "ENGLAND_PREMIER_LEAGUE": {
        "code": 17,
        "name": "英超",
        "match_per_turn": 10,
        "season_codes": {
            "17-18": 13222,
            "16-17": 12651
        },
        "round": 38
    }
}
BET_COMPANY = {
    "LAD_BROKES": {"code": 82},
    "WILLIAM_HILL": {"code": 14}
}

# 如果获取失败，重新去网站刷新一下cookie
COOKIE = {
    '__utma': '56961525.95899878.1517120624.1518169593.1518186546.38',
    '__utmb': '56961525.5.9.1518186550970',
    '__utmc': '56961525',
    '__utmz': {
        '56961525.1518109164.32.9.utmcsr': 'okooo.com|utmccn=(referral)|utmcmd=referral|utmcct=/soccer/league/17/schedule/2746/'},
    'data_start_isShow': '1',
    'DRUPAL_LOGGED_IN': 'Y',
    'First_Source': 'www.okooo.com',
    'FirstOKURL': 'http%3A//www.okooo.com/jingcai/',
    'Hm_lpvt_5ffc07c2ca2eda4cc1c4d8e50804c94b': '1518186551',
    'Hm_lvt_5ffc07c2ca2eda4cc1c4d8e50804c94b': '1517120624,1517893507',
    'IMUserID': '24006237',
    'IMUserName': 'ok_025742692071',
    'isInvitePurview': '0',
    'Last_Source': 'http%3A//www.okooo.com/soccer/match/876722/odds/',
    'LastUrl': '',
    'OkAutoUuid': 'b8b92c071a5ba1185c065aa6d9a2175b',
    'OkMsIndex': '5',
    'PHPSESSID': 'f3438442d0a40ccd389ab57fc3e7620c9536b916',
    'UWord': 'd441d8cd987f00b204e9800998ecf84927e'
}
