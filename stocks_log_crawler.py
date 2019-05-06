# coding=UTF-8
import os
import requests
import time
import datetime
import re
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
import html
import random
from models import session , Stocks , stocks_log_creator
from sqlalchemy import or_
import configparser
import json


mConfigParser = configparser.RawConfigParser()
# mConfigParser.read(os.path.abspath('.') + '/config.ini')
# mConfigParser.read(os.path.abspath('.') + '/campany_config.ini')
mConfigParser.read(os.path.abspath('.') + '/vm_config.ini')
since = mConfigParser.get('DATE','stock_since')
until = mConfigParser.get('DATE','stock_until')

# t = time.time()
# print (int(round(t * 1000)))

#去得user-agent 表單，偽裝瀏覽器用
def get_user_agent_list():
    user_agent_list=[]
    with open("user-agent.txt","r") as f:
        for line in f.readlines():
            line = line.strip()        
            user_agent_list.append(line)
    return user_agent_list

user_agent_list = get_user_agent_list()


#解析數量轉數字
def to_number(text):
    return int(re.sub("[^\\-\d]", "",text))

def add_one_month (since):
    date_split = since.split("-")
    datetime_params = dict(year=int(date_split[0]),month=int(date_split[1]),day=int(date_split[2]))
    since = datetime.datetime(**datetime_params) + relativedelta(months=1)
    return since.strftime("%Y-%m-%d")  

#以年份建立table
def create_stocks_log_table(since) :
    suffix = since.split("-")[0] 
    StocksLog = stocks_log_creator('stocks_log_' + suffix)
    return suffix , StocksLog

def crawler_stocks_log_by_url(url):
    try :
        req_session = requests.Session()
        headers = {"User-Agent":user_agent_list[random.randint(0,len(user_agent_list)-1)]
                ,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8" }
        res = req_session.get(url ,headers = headers)
        parsepage = BeautifulSoup(html.unescape(res.text), "lxml")
        content = parsepage.find('html').text
        #轉成json物件
        contentJsonObj = json.loads(content)
        if 'data' not in contentJsonObj:
            return

        for data in contentJsonObj["data"] :
            taiwan_date_split = data[0].split("/")
            date=since.split("-")[0]+"-"+taiwan_date_split[1]+"-"+taiwan_date_split[2]
            params=dict(name = stock.name , code = stock.code \
                ,opening_price = data[3] , highest_price = data[4] \
                ,lowest_price = data[5] , closing_price = data[6] \
                ,change = data[7] , trade_volume = to_number(data[1]) \
                ,trade_value = to_number(data[2]) , transaction = to_number(data[8]) \
                ,taiwan_date = data[0].strip() , date = date)
            stl=StocksLog(**params)
            session.add(stl)
    except :
        print(url + " => error")
        time.sleep(random.randint(1,5))
        crawler_stocks_log_by_url(url)


if __name__ == "__main__": 
    stocks = session.query(Stocks).filter(or_(Stocks.market_category == "上市" \
                                        ,Stocks.market_category == "上櫃"))\
                                        .filter(or_(Stocks.securities_category == "ETF" \
                                        ,Stocks.securities_category == "股票"))
    # since_timeArray = time.strptime(since, "%Y-%m-%d")
    pre_year , StocksLog = create_stocks_log_table(since)
    while until > since : 
        for stock in stocks :
            stock_number = stock.code
            issue_date = stock.issue_date
            issue_date_split = str(issue_date).split("-")
            since_date_split = since.split("-")

            if pre_year != since_date_split[0] :
                pre_year , StocksLog = create_stocks_log_table(since)    
            
            #比較是否為發行年月
            if (since_date_split[0] + since_date_split[1]) < (issue_date_split[0] + issue_date_split[1]) :
                continue
            print(stock.code + " : " + since)
            since_date = since.replace("-","")
            url = "http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={}&stockNo={}" \
                    .format(since_date,stock_number)
            
            print(url)
            crawler_stocks_log_by_url(url)
            session.commit()
            time.sleep(random.randint(3,10))
            
        time.sleep(random.randint(10,30))
        since = add_one_month(since = since)
