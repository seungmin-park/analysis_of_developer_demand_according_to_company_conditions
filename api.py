import os

import numpy as np
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

# url 잘게 자르기
url = "http://openapi.work.go.kr/opi/opi/opia/wantedApi.do"
serviceKey = "?authKey={authKey}"
Calltp = "&callTp=L"
Return = "&returnType=XML"
empTpGb = "&empTpGb=1"
Display = "&display=100"
occupation = "&occupation=022|023|024|025|026"


# 항목 parsing 함수작성하기
def parse():
    try:
        COMPANY = wanted.find("company").get_text()
        TITLE = wanted.find("title").get_text()
        SAL_TMNM = wanted.find("salTpNm").get_text()
        SAL = wanted.find("sal").get_text()
        REGION = wanted.find("region").get_text()
        HOLIDAY_TPNM = wanted.find("holidayTpNm").get_text()
        MIN_DEUBG = wanted.find("minEdubg").get_text()
        CAREER = wanted.find("career").get_text()
        regDt = wanted.find("regDt").get_text()
        jobsCd = wanted.find("jobsCd").get_text()
        return {
            "회사명": COMPANY,
            "체용제목": TITLE,
            "임금형태": SAL_TMNM,
            "급여": SAL,
            "근무지역": REGION,
            "근무형태": HOLIDAY_TPNM,
            "최소학력": MIN_DEUBG,
            "경력": CAREER,
            "등록일자": regDt,
            "직종코드": jobsCd
        }
    except AttributeError as e:
        return {
            "회사명": None,
            "체용제목": None,
            "임금형태": None,
            "급여": None,
            "근무지역": None,
            "근무형태": None,
            "최소학력": None,
            "경력": None,
            "직종코드": None,
            "우대조건": None
        }


# parsing 하기
for pageNum in range(1, 1000):
    StartPage = "&startPage=" + str(pageNum)
    result = requests.get(url + serviceKey + Calltp + Return + StartPage + occupation + empTpGb + Display)
    soup = BeautifulSoup(result.text, 'lxml-xml')
    wanteds = soup.find_all("wanted")

    row = []
    for wanted in wanteds:
        row.append(parse())

    # pandas 데이터프레임에 넣기
    df = pd.DataFrame(row)

    df.to_csv(str(pageNum) + ".csv", mode='w', encoding='utf-8')

path = "./"
file_list = os.listdir(path)
file_list_csv = [file for file in file_list if file.endswith(".csv")]

print("file_list_csv: {}".format(file_list_csv))

df_all = pd.DataFrame()
for i in range(0, len(file_list_csv)):
    if file_list_csv[i].split('.')[1] == 'csv':
        file = file_list_csv[i]
        df = pd.read_csv(file, encoding='utf-8')
        df_all = pd.concat([df_all, df])

df_all.to_csv("20221130.csv", mode='w', encoding='utf-8')

import pandas as pd

df_all = pd.read_csv("/content/20221130.csv")
df_all.sort_values('등록일자')


def convertMonthCost(x):
    if x.__contains__("~"):
        return rangeCost(x)
    else:
        return convertFixMonthCost(x)


def rangeCost(x):
    x = x.replace('만원', '')
    x = x.replace(' ', '')

    costs = x.split('~')

    minMonthCost = costs[0]
    maxMonthCost = costs[1]
    minYearCost = int(minMonthCost) * 12
    maxYearCost = int(maxMonthCost) * 12

    yearCost = str(int((minYearCost + maxYearCost) / 2)) + "만원"
    return yearCost


def convertFixMonthCost(x):
    x = x.replace('만원', '')
    yearCost = str(int(x) * 12) + "만원"
    return yearCost


def temp(x):
    x = x.replace('만원', '')
    x = x.replace(' ', '')
    split = x.split('~')

    return str(int(int(split[0]) + int(split[1]) / 2)) + '만원'


df_year_cost = df_all[df_all.임금형태 == '연봉']
df_year_cost.급여 = df_year_cost.급여.apply(lambda x: temp(x) if x.__contains__('~') else x)
df_month_cost = df_all[df_all.임금형태 == '월급']
df_month_cost.급여 = df_month_cost.급여.apply(convertMonthCost)
df_all = pd.concat((df_year_cost, df_month_cost), sort=False)

df_all.drop(['Unnamed: 0', 'Unnamed: 0.1', '임금형태'], axis=1, inplace=True)

workCode = pd.read_csv('/content/직종코드.csv')
workCode = workCode.replace(r'^\s*$', np.nan, regex=True)
workCode.dropna(thresh=2, inplace=True)
workCode.fillna(method='ffill', inplace=True)

# 불필요한 열 삭제
workCode.drop(['0'], axis=1, inplace=True)

# 채용 공고와 병합을 위한 columns 이름 변경
workCode.columns = ['직종코드', '대분류', '중분류', '소분류']

workCode.to_csv("new_직종코드.csv", mode='w', encoding='utf-8')

# 채용 공고와 직종코드 정보 합치기
merged = pd.merge(left=df_all, right=workCode, how='inner', on='직종코드')

ITCount = merged[merged['대분류'] == '연구/IT'].대분류.count()
NoneITCount = merged[merged['대분류'] != '연구/IT'].대분류.count()

ratio = [ITCount, NoneITCount]
labels = ['IT 직군', '비 IT직군']
plt.pie(ratio, labels=labels, autopct='%.1f%%', colors=['red', 'green'])
plt.show()
