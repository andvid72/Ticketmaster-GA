import json, urllib3, time, random
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from GA_module import *
from GA_telegram import *
from bs4 import BeautifulSoup
from GA_automatic_onlsale import *
from GA_automatic_prelsale import *
EachUrl = 'https://www.ticketmaster.com/copa-america-2024-group-a-argentina-atlanta-georgia-06-20-2024/event/0E006039EBC5889C'
response = Scrapeops(EachUrl)
soup = BeautifulSoup(BeautifulSoup(response.text,'html.parser').prettify(),'html.parser')
TotalPriceRangeScript_str = str(soup.find(id='__NEXT_DATA__').contents[0])
TotalPriceRangeScript_json = json.loads(TotalPriceRangeScript_str)
facets = json.loads(TotalPriceRangeScript_json['props']['pageProps']['edpData']['context']['eventLevelAvailability'])['facets']
secnames = TotalPriceRangeScript_json['props']['pageProps']['edpData']['context']['event']['secnames']
print(facets)
print(secnames)
