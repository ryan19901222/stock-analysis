import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import configparser
import os
import html
import re
import time
import random
import csv
from models import session , SecuritiesFirm


mConfigParser = configparser.RawConfigParser()
mConfigParser.read(os.path.abspath('.') + '/config.ini')
executable_path = mConfigParser.get('PATH','chrome_path')


def get_all_securities_firm_dataset():
    securities_firm_list=[]
    chromeOptions = webdriver.ChromeOptions()
    # chromeOptions.add_argument('--headless')
    # chromeOptions.add_argument('--log-level=3')
    # browser = webdriver.Chrome(executable_path=executable_path,chrome_options=chromeOptions)
    browser = webdriver.Chrome(executable_path=executable_path)
    browser.get("https://www.moneydj.com/z/zg/zgb/zgb0.djhtm")
    src_page = browser.page_source
    parsepage = BeautifulSoup(src_page, 'lxml')
    # sel_Broker = parsepage.findAll("select")
    sel_Broker = parsepage.find("select", {"name": "sel_Broker"})
    options=sel_Broker.findAll("option")

    for option in options:
        bank_id=option["value"]
        bank_name=option.text
        select = Select(browser.find_element_by_name("sel_Broker"))
        select.select_by_value(bank_id)
        new_src_page = browser.page_source
        new_parsepage = BeautifulSoup(new_src_page, 'lxml')
        sel_BrokerBranch = new_parsepage.find("select", {"name": "sel_BrokerBranch"})
        brokerBranch_options=sel_BrokerBranch.findAll("option")
        for brokerBranch_option in brokerBranch_options:
            branch_id=brokerBranch_option["value"]
            branch_name=brokerBranch_option.text
            row={"bank_id":bank_id,"bank_name":bank_name,"branch_id":branch_id,"branch_name":branch_name}
            # row=[bank_id,bank_name,branch_id,branch_name]
            securities_firm_list.append(row)
            print(row)
            print("---------------")
    browser.quit()
    return securities_firm_list



if __name__ == "__main__":
    securities_firm_list = get_all_securities_firm_dataset()
    for securities_firm in securities_firm_list:
        securities_firm=SecuritiesFirm(**securities_firm)
        session.add(securities_firm)
    session.commit()
    # with open("securitiesFirm.csv", "w", newline="",encoding="utf-8") as csv_file:
        # writer = csv.writer(csv_file, dialect='excel')
        # fieldnames = ["bank_id","bank_name","branch_id","branch_name"]
        # writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # writer.writeheader()
        # for securities_firm in securities_firm_list:
            # writer.writerow(securities_firm)

            
