# coding=UTF-8
import requests
from bs4 import BeautifulSoup
import html
import random
from models import session , Stocks

#去得user-agent 表單，偽裝瀏覽器用
def get_user_agent_list():
    user_agent_list=[]
    with open("user-agent.txt","r") as f:
        for line in f.readlines():
            line = line.strip()        
            user_agent_list.append(line)
    return user_agent_list

user_agent_list = get_user_agent_list()

req_session = requests.Session()
headers={"User-Agent":user_agent_list[random.randint(0,len(user_agent_list)-1)]
        ,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8" }

url = "http://isin.twse.com.tw/isin/single_main.jsp"
res = req_session.get(url ,headers = headers)
parsepage = BeautifulSoup(html.unescape(res.text), "lxml")
trs = parsepage.findAll("tr")

for tr in trs[1:] :
    tds = tr.findAll("td")
    params = dict(isin = tds[1].text \
                ,code = tds[2].text , name = tds[3].text \
                ,market_category = tds[4].text , securities_category = tds[5].text \
                ,industry = tds[6].text , issue_date = tds[7].text \
                ,cfi_code = tds[8].text , remark = tds[9].text )
    stocks=Stocks(**params)
    session.add(stocks)
session.commit()
    


