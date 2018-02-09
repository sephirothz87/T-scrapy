import json
import SoccerUtil as su
import logging
from logging import debug as d,info as i,warning as w,error as e,critical as c


#
logging.basicConfig(level=logging.DEBUG)
print(su.LEAGUE)
# debug('a')
# info('b')
# error('c')
# warning('d')
# critical('e')
# critical(su.LEAGUE)

d('a')
i('b')
e('c')
w('d')
c('e')
c(su.LEAGUE)
#


#
# f = open("const.json",encoding="utf-8")
#
# setting = json.load(f)
#
# print(setting)
#