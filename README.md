# 기업의 조건에 따른 개발자 수요 분석

## 프로젝트 진행 계획

![image](https://user-images.githubusercontent.com/78605779/206906077-f8cef6ee-c0b4-4b8c-b60d-bdf44cb6b009.png)

## 유명 기업들의 채용 공고 페이지 크롤링 가능 여부

![image](https://user-images.githubusercontent.com/78605779/206906882-d2ab1722-aa78-48cc-8956-d0870bbf8a11.png)

## 유명 채용 공고 사이트 크롤링 가능 여부

![image](https://user-images.githubusercontent.com/78605779/206906928-2733feaf-9a3e-40de-b133-85bb2fc55740.png)

## 유명 채용 공고 사이트 API 제공 여부

![image](https://user-images.githubusercontent.com/78605779/206906962-4ab9c18c-f59c-45c4-8ad8-59de19d4e6c8.png)

## 워크넷 API를 이용하여 데이터 수집

[워크넷 open api 활용](https://openapi.work.go.kr/opi/opi/opia/wantedApiListVw.do)

1. 1 페이지부터 1,000 페이지까지의 데이터를 csv로 저장

```python
# parsing 하기
for pageNum in range (1, 1000):
  StartPage = "&startPage=" + str(pageNum)
  result = requests.get(url + serviceKey + Calltp + Return + StartPage + occupation + empTpGb + Display)
  soup = BeautifulSoup(result.text, 'lxml-xml')
  wanteds = soup.find_all("wanted")

  row = []
  for wanted in wanteds:
      row.append(parse())

  # pandas 데이터프레임에 넣기
  df = pd.DataFrame(row)

  df.to_csv(str(pageNum)+".csv", mode='w', encoding='utf-8')
```

2. 총 94,232 건의 데이터 수집


![image](https://user-images.githubusercontent.com/78605779/206906685-6d8e83cc-7e21-4682-a40f-0d3af35a5403.png)

## 채용 공고 데이터 전처리

1. 임금 형태의 시급 또는 주급 형태의 데이터 삭제

```python
df_year_cost = df_all[df_all.임금형태 == '연봉']
df_month_cost = df_all[df_all.임금형태 == '월급']
```

2. 월급 데이터를 연봉 데이터로 변환

```python
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
  
  return int((minYearCost + maxYearCost) / 2)

def convertFixMonthCost(x):
    x = x.replace('만원', '')
    return int(x) * 12

df_month_cost.급여 = df_month_cost.급여.apply(convertMonthCost)
```

3. 연봉 데이터의 문자 삭제 및 범위 데이터를 평균 데이터로 변환

```python
def removePostfix(x):
  if x.__contains__('~'):
    return getAvg(x)
  return int(x.replace('만원',''))

def getAvg(x):
  x = x.replace('만원', '')
  x = x.replace(' ', '')
  split = x.split('~')

df_year_cost.급여 = df_year_cost.급여.apply(removePostfix)
```

4. 불필요한 columns 삭제

```python
df_all.drop(['Unnamed: 0', 
             'Unnamed: 0.1', 
             'Unnamed: 0.1.1',
             '임금형태'], 
            axis=1, 
            inplace=True)
```

## 직업 코드 데이터 전처리

![image](https://user-images.githubusercontent.com/78605779/206906608-88a57029-1070-42db-a468-523877971179.png)

## 비 IT 직군과 IT 직군의 채용 공고 비율

![image](https://user-images.githubusercontent.com/78605779/206906588-175a7aa0-bb6b-48e9-9ce7-330a8c5cb8a3.png)

## IT 직군의 채용 공고 지역의 분포도 확인을 위한 전처리

**채용 공고 근무 지역 데이터를 geo-json 의 지역 데이터로 변환**

```python
IT_df = merged[merged['대분류'] == '연구/IT']

IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'서귀포시' if '서귀포시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'제주시' if '제주시' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'합천군' if '합천군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'거창군' if '거창군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'함양군' if '함양군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'산청군' if '산청군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'하동군' if '하동군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'남해군' if '남해군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'고성군' if '고성군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'창녕군' if '창녕군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'함안군' if '함안군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'의령군' if '의령군' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'창원시진해구' if '창원시 진해구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'창원시마산회원구' if '창원시 마산회원구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'창원시마산합포구' if '창원시 마산합포구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'창원시성산구' if '경남 창원시 성산구' in x else x)
IT_df.근무지역 = IT_df.근무지역.apply(lambda x:'창원시의창구' if '창원시 의창구' in x else x)
...
```

## IT 직군의 채용 지역 분포도

![image](https://user-images.githubusercontent.com/78605779/206906484-4a784b6d-2237-4cc5-8d1d-b6e63d94dc6e.png)

## IT 직군의 경력 요구사항 비율

![image](https://user-images.githubusercontent.com/78605779/206906464-2360aa75-33f4-47de-a740-2aa022a14b73.png)

## IT 직군의 경력별 급여 분포도

![image](https://user-images.githubusercontent.com/78605779/206906434-62de415d-7741-4d85-b152-c51e0a9a3346.png)

## IT 직군의 각 분야별 수요

![image](https://user-images.githubusercontent.com/78605779/206906406-504d66d3-9b4f-4809-bb1a-5e120d5da851.png)

## IT 직군의 최소 학력 요구사항 비율

![image](https://user-images.githubusercontent.com/78605779/206906334-ef9d1e53-cad8-4f63-b74e-774cfeb204aa.png)

## IT 직군의 최소 학력별 급여 분포도

![image](https://user-images.githubusercontent.com/78605779/206906283-4e929020-74c6-4aab-99f1-01f3211d1073.png)