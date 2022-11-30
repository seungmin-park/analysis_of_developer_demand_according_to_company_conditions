import requests
from bs4 import BeautifulSoup
import pandas as pd

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
