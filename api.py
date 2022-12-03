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

IT_df = merged[merged['대분류'] == '연구/IT']

IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '서귀포시' if '서귀포시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '제주시' if '제주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '합천군' if '합천군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '거창군' if '거창군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '함양군' if '함양군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '산청군' if '산청군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '하동군' if '하동군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '남해군' if '남해군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '고성군' if '고성군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '창녕군' if '창녕군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '함안군' if '함안군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '의령군' if '의령군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '창원시진해구' if '창원시 진해구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '창원시마산회원구' if '창원시 마산회원구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '창원시마산합포구' if '창원시 마산합포구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '창원시성산구' if '경남 창원시 성산구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '창원시의창구' if '창원시 의창구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '양산시' if '양산시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '거제시' if '거제시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '밀양시' if '밀양시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '김해시' if '김해시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '사천시' if '사천시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '통영시' if '통영시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '진주시' if '진주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '울릉군' if '울릉군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '울진군' if '울진군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '봉화군' if '봉화군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '예천군' if '예천군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '칠곡군' if '칠곡군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '성주군' if '성주군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '고령군' if '고령군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '청도군' if '청도군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '영덕군' if '영덕군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '영양군' if '영양군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '청송군' if '청송군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '의성군' if '의성군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '군위군' if '군위군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '경산시' if '경산시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '문경시' if '문경시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '상주시' if '상주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '영천시' if '영천시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '영주시' if '영주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '구미시' if '구미시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '안동시' if '안동시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '김천시' if '김천시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '경주시' if '경주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '포항시북구' if '포항시 북구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '포항시남구' if '포항시 남구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '신안군' if '신안군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '진도군' if '진도군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '완도군' if '완도군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '장성군' if '장성군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '영광군' if '영광군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '함평군' if '함평군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '무안군' if '무안군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '영암군' if '영암군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '해남군' if '해남군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '강진군' if '강진군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '장흥군' if '장흥군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '화순군' if '화순군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '보성군' if '보성군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '고흥군' if '고흥군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '구례군' if '구례군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '곡성군' if '곡성군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '담양군' if '담양군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '광양시' if '광양시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '나주시' if '나주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '순천시' if '순천시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '여수시' if '여수시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '목포시' if '목포시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '부안군' if '부안군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '고창군' if '고창군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '순창군' if '순창군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '임실군' if '임실군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '장수군' if '장수군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '무주군' if '무주군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '진안군' if '진안군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '완주군' if '완주군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '김제시' if '김제시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '남원시' if '남원시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '정읍시' if '정읍시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '익산시' if '익산시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '군산시' if '군산시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '전주시덕진구' if '전주시 덕진구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '전주시완산구' if '전주시 완산구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '태안군' if '태안군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '예산군' if '예산군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '홍성군' if '홍성군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '청양군' if '청양군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '서천군' if '서천군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '부여군' if '부여군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '금산군' if '금산군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '당진시' if '당진시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '계룡시' if '계룡시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '논산시' if '논산시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '서산시' if '서산시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '아산시' if '아산시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '보령시' if '보령시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '공주시' if '공주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '천안시서북구' if '천안시 서북구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '천안시동남구' if '천안시 동남구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '증평군' if '증평군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '단양군' if '단양군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '음성군' if '음성군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '괴산군' if '괴산군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '진천군' if '진천군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '영동군' if '영동군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '옥천군' if '옥천군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '보은군' if '보은군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '청원군' if '청원군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '제천시' if '제천시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '충주시' if '충주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '청주시흥덕구' if '청주시 흥덕구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '청주시상당구' if '청주시 상당구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '양양군' if '양양군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '고성군' if '고성군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '인제군' if '인제군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '양구군' if '양구군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '화천군' if '화천군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '철원군' if '철원군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '정선군' if '정선군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '평창군' if '평창군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '영월군' if '영월군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '횡성군' if '횡성군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '홍천군' if '홍천군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '삼척시' if '삼척시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '속초시' if '속초시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '태백시' if '태백시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '동해시' if '동해시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '강릉시' if '강릉시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '원주시' if '원주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '춘천시' if '춘천시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '양평군' if '양평군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '가평군' if '가평군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '연천군' if '연천군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '여주시' if '여주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '포천시' if '포천시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '양주시' if '양주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '광주시' if '광주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '화성시' if '화성시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '김포시' if '김포시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '안성시' if '안성시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '이천시' if '이천시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '파주시' if '파주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '용인시수지구' if '용인시 수지구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '용인시기흥구' if '용인시 기흥구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '용인시처인구' if '용인시 처인구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '하남시' if '하남시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '의왕시' if '의왕시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '군포시' if '군포시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '시흥시' if '시흥시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '오산시' if '오산시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '남양주시' if '남양주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '구리시' if '구리시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '과천시' if '과천시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '고양시일산서구' if '고양시 일산서구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '고양시일산동구' if '고양시 일산동구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '고양시덕양구' if '고양시 덕양구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '안산시단원구' if '안산시 단원구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '안산시상록구' if '안산시 상록구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '동두천시' if '동두천시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '평택시' if '평택시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '광명시' if '광명시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '부천시' if '부천시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '부천시오정구' if '부천시 오정구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '부천시소사구' if '부천시 소사구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '부천시원미구' if '부천시 원미구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '안양시동안구' if '안양시 동안구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '안양시만안구' if '안양시 만안구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '의정부시' if '의정부시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '성남시분당구' if '성남시 분당구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '성남시중원구' if '성남시 중원구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '성남시수정구' if '성남시 수정구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '수원시영통구' if '수원시 영통구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '수원시팔달구' if '수원시 팔달구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '수원시권선구' if '수원시 권선구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '수원시장안구' if '수원시 장안구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '세종시' if '세종시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '울주군' if '울주군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '북구' if '북구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '동구' if '동구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '남구' if '남구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '중구' if '중구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '대덕구' if '대덕구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '유성구' if '유성구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '서구' if '서구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '중구' if '중구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '동구' if '동구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '광산구' if '광산구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '북구' if '북구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '남구' if '남구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '서구' if '서구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '동구' if '동구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '옹진군' if '옹진군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '강화군' if '강화군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '서구' if '서구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '계양구' if '계양구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '부평구' if '부평구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '남동구' if '남동구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '연수구' if '연수구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '남구' if '남구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '동구' if '동구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '중구' if '중구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '달성군' if '달성군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '달서구' if '달서구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '수성구' if '수성구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '북구' if '북구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '남구' if '남구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '서구' if '서구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '동구' if '동구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '중구' if '중구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '기장군' if '기장군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '사상구' if '사상구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '수영구' if '수영구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '연제구' if '연제구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '강서구' if '강서구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '금정구' if '금정구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '사하구' if '사하구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '해운대구' if '해운대구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '북구' if '북구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '남구' if '남구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '동래구' if '동래구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '부산진구' if '부산진구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '영도구' if '영도구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '동구' if '동구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '서구' if '서구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '중구' if '중구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '강동구' if '강동구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '송파구' if '송파구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '강남구' if '강남구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '서초구' if '서초구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '관악구' if '관악구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '동작구' if '동작구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '영등포구' if '영등포구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '금천구' if '금천구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '구로구' if '구로구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '강서구' if '강서구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '양천구' if '양천구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '마포구' if '마포구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '서대문구' if '서대문구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '은평구' if '은평구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '노원구' if '노원구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '도봉구' if '도봉구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '강북구' if '강북구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '성북구' if '성북구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '중랑구' if '중랑구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '동대문구' if '동대문구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '광진구' if '광진구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '성동구' if '성동구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '용산구' if '용산구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '중구' if '중구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x: '종로구' if '종로구' in x else x)
