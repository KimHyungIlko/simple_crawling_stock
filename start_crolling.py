# -*- coding: utf-8 -*-
# -*- coding: euc-kr -*- 
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from win10toast import ToastNotifier
import time
import pymysql

toaster = ToastNotifier()

# 종목 url 들어가기
def get_code(company_code):
    url = "https://finance.naver.com/item/main.nhn?code=" + company_code
    result = requests.get(url)
    bs_obj = BeautifulSoup(result.content, "html.parser")
    return bs_obj

# 주가 정보 가져오기
def get_price(company_code):
    bs_obj = get_code(company_code)
    no_today = bs_obj.find("p", {"class": "no_today"})
    blind = no_today.find("span", {"class": "blind"})
    now_price = blind.text
    return now_price

# 인터넷 연결 확인
def internet_on():
    try:
        urllib2.urlopen('https://finance.naver.com', timeout=1)
        return True
    except urllib2.URLError as err: 
        return False

#SQL연동---------------------------------------
mymoney_db = pymysql.connect(
    user='root', 
    passwd='asdfqwer', 
    host='127.0.0.1', 
    db='bbs', 
    charset='utf8'
)
cursor = mymoney_db.cursor(pymysql.cursors.DictCursor)
def update_date(date,price,code):
    data=(date,price,code)
    sql = "UPDATE mymoney SET date = %s , before_price=%s where codes=%s;"
    cursor.execute(sql,data)
    mymoney_db.commit()

def insert(name, price, codes, date):
    sql = "INSERT INTO `mymoney` VALUES (%s, %s,%s,%s);"
    cursor.executemany(sql, name,price,codes,date)
    mymoney_db.commit()

def delete(name):
    sql = 'DELETE FROM `mymoney` WHERE name=%s;'
    cursor.execute(sql,name)
    mymoney_db.commit()
#행수를 구해서 수에 맞게 반복
def counting():
    sql = "SELECT COUNT(*) FROM `mymoney`;"
    cursor.execute(sql)
    line_num = cursor.fetchall()
    return line_num

def mymoney_data():
    sql = "SELECT * FROM `mymoney`;"
    cursor.execute(sql)
    result = cursor.fetchall()
    for num in range(len(result)):
        company_name.insert(num,result[num][u'name'])
        yesterday_price.insert(num,result[num][u'before_price'])
        company_codes.insert(num,result[num][u'codes'])
    before_date.insert(0,result[0][u'date'])
    return result

def compare_date(date):
    sql = "SELECT * FROM `mymoney`;"
    # print("now : "+ date)
    cursor.execute(sql)
    result = cursor.fetchall()
    yesterday=result[0][u'date']
    if str(yesterday) != date:
        return 1
    else :
        return 0
#--------------------------------------------------------------------------------------------
#초기설정
story=""
yesterday_price=[]
company_name = []
int_yesterday_price=[]
int_present_price=[]
company_codes = []
revenue_rate=[]
before_pirce = []
present_price=[]
now = datetime.now()
now_date=now.strftime("%Y-%m-%d")
line_num=counting()[0]['COUNT(*)']
# now_time=now.strftime("%H%M")
before_date=[]
# c_date=now.strftime("%Y-%m-%d")
# formattedDate = now.strftime("%Y%m%d_%H%M%S")
# print(compare_date(c_date))
# print (now)
mymoney_data()

for a in range(len(company_codes)):
    int_yesterday_price.insert(a,int(yesterday_price[a].replace(",", "")))
    before_pirce.insert(a,yesterday_price[a].replace(",", ""))

while True:
    if internet_on():
        print(now)
        for number in range(line_num):
            now_price = get_price(company_codes[number])
            present_price.insert(number,now_price)
            int_present_price.insert(number,int(present_price[number].replace(",", "")))
            revenue_rate.insert(number,round(float(int_present_price[number]-int_yesterday_price[number])/int_yesterday_price[number]*100,2))
            print(company_name[number]+" : "+present_price[number]+u"  수익률 : "+str(revenue_rate[number])+"%")
            if before_pirce[number] != present_price[number] :            
                if  before_pirce[number] > present_price[number] :
                    # print(company_name[number]+u" 이전주가 : "+yesterday_price[number]+"\n"+u" 주가 : "+present_price[number]+ u" ▼"+str(revenue_rate[number])+"%\n" )
                    story+=(company_name[number]+u" 어제주가 : "+yesterday_price[number]+"\n"+u" 현주가 : "+present_price[number]+ u" ▼"+str(revenue_rate[number])+"%\n" )
                else :
                    story+=(company_name[number]+u" 어제주가 : "+yesterday_price[number]+"\n"+u" 현주가 : "+present_price[number]+ u" ▲"+str(revenue_rate[number])+"%\n" )
                    # print(company_name[number]+u" 이전주가 : "+yesterday_price[number]+"\n"+u" 주가 : "+present_price[number]+ u" ▲"+str(revenue_rate[number])+"%\n" )
                before_pirce[number] = present_price[number]
        print("-------------------------------")

        if  story :
            toaster.show_toast(u"주가 분석",story,duration=10)
    #날짜 변환시 자동으로 금일 종가/날짜 저장  and before_date[0]!=now.strftime("%Y-%m-%d")
        if int(now.strftime("%H%M")) > 1530 or int(now.strftime("%H%M")) < 900 :
            # print("test")
            for number in range(line_num):
                update_date(now.strftime("%Y-%m-%d"),present_price[number],company_codes[number])
            before_date[0]=now_date
            

    story=""
    time.sleep(30)