import requests

import importlib,sys

importlib.reload(sys)

import scrapy
from scrapy.crawler import CrawlerProcess
import re



url = 'http://www.okooo.com/soccer/match/954300/odds/'


res = requests.get(url=url)

# print(res.url)
content = res.text
print(res)

print(content)
#
#
# williamHillOdds = content.xpath('//*[@id="tr14"]')
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

