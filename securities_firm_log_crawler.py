# coding=UTF-8
import os
import re
import csv
import time
import datetime
import requests
from bs4 import BeautifulSoup
import html
import configparser
import time
import random
from models import session , securities_firm_log_creator

mConfigParser = configparser.RawConfigParser()
mConfigParser.read(os.path.abspath('.') + '/config.ini')
since = mConfigParser.get('DATE','securities_since')
until = mConfigParser.get('DATE','securities_until')

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

#轉換時間格式
def formatDateTime(timestamp, formatStr):
    timeArray = time.localtime(timestamp)
    otherStyleTime = time.strftime(formatStr, timeArray)
    return otherStyleTime

#解析買超或賣超表並存入db
def parse_table_to_db(table_names,net_status,bank_id,bank_name,branch_id,branch_name,date,SecuritiesFirmLog):

    for index,name in enumerate(table_names):
        a_link=re.search("GenLink2stk\('[ASP]{0,2}(.*?)','(.*?)'\)", name.text)
        parent_tr=name.find_parent('tr')
        t3n1=parent_tr.findAll("td", {"class": ["t3n1_rev", "t3n1"]})
        stock_code = a_link.group(1)
        stock_name = a_link.group(2)
        buy = to_number(t3n1[0].text)
        sell = to_number(t3n1[1].text)
        deviation = to_number(t3n1[2].text)
        # print(stock_code)
        sfl = SecuritiesFirmLog(bank_id = bank_id,bank_name=bank_name \
                    , branch_id = branch_id,branch_name=branch_name \
                    , stock_name = stock_name , stock_code = stock_code \
                    , net_status = net_status , buy = buy \
                    , sell = sell, deviation = deviation \
                    , date = date)
        session.add(sfl)

    session.commit()


#抓取卷商買入買出頁面
def get_securities_firm_log(bank_id,bank_name,branch_id,branch_name,category,start_date,finall_date,SecuritiesFirmLog):
    if "(停)" in branch_name:
        # print(branch_name)
        return

    print(branch_id + " : " + finall_date)
    # time.sleep(random.randint(1,2))
    session=requests.Session()
    headers={"User-Agent":user_agent_list[random.randint(0,len(user_agent_list)-1)]
              ,"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
              ,"Referer":"https://www.moneydj.com/"}

    url = "https://www.moneydj.com/z/zg/zgb/zgb0.djhtm?a={}&b={}&c={}&e={}&f={}"\
          .format(bank_id,\
                branch_id,\
                category,\
                start_date,\
                finall_date)
    try :
        res = session.get(url , headers = headers)
        parsepage = BeautifulSoup(html.unescape(res.text), "lxml")
        oMainTable=parsepage.find("table", {"id": "oMainTable"})
        tables=oMainTable.findAll("table")
        buy_table=tables[0]
        sell_table=tables[1]
        buy_table_names=buy_table.findAll("td", {"class": "t4t1"})
        sell_table_names=sell_table.findAll("td", {"class": "t4t1"})

        parse_table_to_db(table_names = buy_table_names , net_status = "B" \
                    ,bank_id = bank_id , bank_name = bank_name , branch_id = branch_id \
                    ,branch_name = branch_name , date = finall_date , SecuritiesFirmLog = SecuritiesFirmLog)

        parse_table_to_db(table_names = sell_table_names , net_status = "S" \
                    ,bank_id = bank_id , bank_name = bank_name , branch_id = branch_id \
                    ,branch_name = branch_name , date = finall_date , SecuritiesFirmLog = SecuritiesFirmLog)
    except :
	    print(branch_id + " : " + finall_date + " => error")
	    time.sleep(random.randint(1,5))
	    get_securities_firm_log(bank_id,bank_name,branch_id,branch_name,category,start_date,finall_date,SecuritiesFirmLog)



#取得卷商列表
def get_securities_firm_list():
    securities_firm_list=[]
    with open("securitiesFirm.csv", newline="",encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            securities_firm_list.append(row)
    return securities_firm_list

#以月份建立table
def create_securities_firm_table(since) :
    suffix = since.split("-")[0] + "_" + since.split("-")[1]
    SecuritiesFirmLog = securities_firm_log_creator('securities_firm_log_' + suffix)
    pre_month = since.split("-")[1]
    return pre_month , SecuritiesFirmLog
	
	
# 跳下一天
def add_one_days(since) :
    date_split = since.split("-")
    datetime_params = dict(year=int(date_split[0]),month=int(date_split[1]),day=int(date_split[2]))
    since = datetime.datetime(**datetime_params)+datetime.timedelta(days = 1)
    since = since.strftime("%Y-%m-%d")
    return since
 
if __name__ == "__main__":    

    since_timeArray = time.strptime(since, "%Y-%m-%d")
    since_sec = int(time.mktime(since_timeArray))
    
    until_timeArray = time.strptime(until, "%Y-%m-%d")
    until_sec = int(time.mktime(until_timeArray))

    pre_month , SecuritiesFirmLog = create_securities_firm_table(since = since)

    #now_sec = int(time.mktime(datetime.datetime.now().timetuple()))

    while until > since : 

        # 台股2019六日不開市
        if datetime.datetime.strptime(since, "%Y-%m-%d").isoweekday() > 5 :
            since = add_one_days(since = since)
            continue

        if pre_month != since.split("-")[1] :
            pre_month , SecuritiesFirmLog = create_securities_firm_table(since = since)

        current_date = re.sub("-0", "-" , since)
        for row in get_securities_firm_list():
            get_securities_firm_log(bank_id = row["bank_id"] , bank_name = row["bank_name"]\
                            ,branch_id = row["branch_id"] , branch_name = row["branch_name"]\
                            ,category = "E" , start_date = current_date \
                            ,finall_date = current_date , SecuritiesFirmLog = SecuritiesFirmLog)
        # 跳下一天
        since = add_one_days(since = since)

