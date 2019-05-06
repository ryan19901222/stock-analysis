# coding=UTF-8
import os
import configparser
from sqlalchemy import create_engine, Table, Column, Float, Integer, BigInteger, DATE, String, MetaData, ForeignKey , Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker , relationship, backref

mConfigParser = configparser.RawConfigParser()
mConfigParser.read(os.path.abspath('.') + '/config.ini')
db_host = mConfigParser.get('DB','host')
db_name = mConfigParser.get('DB','name')
db_username = mConfigParser.get('DB','username')
db_password = mConfigParser.get('DB','password')
db_port = mConfigParser.get('DB','port')


# DB_CONNECT_STRING = "sqlite:///:memory:"
# engine = create_engine(DB_CONNECT_STRING, echo=True)
# DB_CONNECT_STRING = "mysql+pymysql://root:gj4rm4_dylan@127.0.0.1:3306/stocker"
DB_CONNECT_STRING = "mysql+pymysql://"+db_username+":"+db_password+"@"+db_host+":"+db_port+"/"+db_name+""
engine = create_engine(DB_CONNECT_STRING, max_overflow=5)
# engine = create_engine(DB_CONNECT_STRING, max_overflow=5, echo=True)

Base = declarative_base()

class SecuritiesFirm(Base):

    __tablename__ = "securities_firm"

    branch_id = Column("branch_id", String(50), primary_key=True)
    branch_name = Column("branch_name", String(50))
    bank_id = Column("bank_id", String(50))
    bank_name = Column("bank_name", String(50))


def securities_firm_log_creator(tablename):
    class SecuritiesFirmLog(Base):

        __tablename__ = tablename
        # __table_args__ = (Index('securities_firm_log_index', "branch_id", "stock_code"), )

        id = Column("id", Integer, primary_key=True, autoincrement=True)
        bank_id = Column("bank_id", String(50))
        bank_name = Column("bank_name", String(50))
        branch_id = Column("branch_id", String(50), index=True)
        # branch_id = Column(String(50) , ForeignKey("securities_firm.branch_id") )
        branch_name = Column("branch_name", String(50))
        stock_name = Column("stock", String(50))
        stock_code = Column("stock_code", String(50), index=True)
        net_status = Column("net_status", String(1))
        buy = Column("buy", Integer)
        sell = Column("sell", Integer)
        deviation = Column("deviation", Integer)
        date = Column("date", DATE)

        # securities_firm = relationship('SecuritiesFirm')

    Base.metadata.create_all(engine)

    return SecuritiesFirmLog 

class Stocks(Base):
    
    __tablename__ = "stocks"

    code = Column("code", String(50), primary_key=True)
    isin = Column("isin", String(50)) 
    name = Column("name", String(50))
    market_category = Column("market_category", String(50))
    securities_category = Column("securities_category", String(50))
    industry = Column("industry", String(50))
    issue_date = Column("issue_date", DATE)
    cfi_code = Column("cfi_code", String(50))
    remark = Column("remark", String(255))


def stocks_log_creator(tablename):

    class StocksLog(Base):

        __tablename__ = tablename

        id = Column("id", Integer, primary_key=True, autoincrement=True)
        name = Column("name", String(50))
        code = Column("code", String(50), index=True)
        opening_price = Column("opening_price", String(50))#開盤價
        highest_price = Column("highest_price", String(50))#最高價
        lowest_price = Column("lowest_price", String(50))#最低價
        closing_price = Column("closing_price", String(50))#收盤價
        change = Column("change", String(50))#漲跌價差
        trade_volume = Column("trade_volume", BigInteger)#成交股數
        trade_value = Column("trade_value", BigInteger)#成交金額
        transaction = Column("transaction", Integer)#成交筆數
        taiwan_date = Column("taiwan_date", String(50))
        date = Column("date", DATE)

    Base.metadata.create_all(engine)

    return StocksLog 

#創建表（如果表已存在不創建）
# SecuritiesFirmLogCreator("securities_firm_log")
Base.metadata.create_all(engine)
DB_Session = sessionmaker(bind=engine)
session = DB_Session()


