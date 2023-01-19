import csv
import requests
from bs4 import BeautifulSoup
import re

url ="https://fifaonline4.nexon.com/datacenter/PlayerList"

# 엑셀 파일로 저장하기
filename = "네이버 웹툰 인기 순위.csv"
f = open(filename, "w", encoding="utf-8-sig", newline="")
writer = csv.writer(f)

columns_name = ["순위", "웹툰명"]

writer.writerow(columns_name)
bpArray = []
for i in range(1, 9):
    data = {'n1Confederation': '0',
    'n4LeagueId': '0',
    "strSeason": ',216,217,218,262,236,254,233,231,237,246,249,253,251,252,256,261,264,265,101,214,207,206,202,201,258,259,240,241,210,225,234,294,247,297,510,508,300,257,507,260,250,',
    'n1LeftFootAblity': '0',
    'n1RightFootAblity': '0',
    'n1SkillMove': '0',
    'n1InterationalRep': '0',
    'n4BirthMonth': '0',
    'n4BirthDay': '0',
    'n4TeamId': '0',
    'n4NationId': '0',
    'n1Strong': str(i),
    'n1Grow': '0',
    'n1TeamColor': '0',
    'strSkill1': 'sprintspeed',
    'strSkill2': 'acceleration',
    'strSkill3': 'strength',
    'strSkill4': 'stamina',
    'strSearchStatus': 'off',
    'strOrderby': 'n8playergrade1',
    'teamcolorid': '0',
    'n1History': '0',
    'n4OvrMin': '94',
    'n4OvrMax': '94',
    'n4SalaryMin': '4',
    'n4SalaryMax': '34',
    'n8PlayerGrade1Min': '0',
    'n8PlayerGrade1Max': '10000',
    'n1Ability1Min': '40',
    'n1Ability1Max': '150',
    'n1Ability2Min': '40',
    'n1Ability2Max': '150',
    'n1Ability3Min': '40',
    'n1Ability3Max': '150',
    'n4BirthYearMin': '1900',
    'n4BirthYearMax': '2010',
    'n4HeightMin': '156',
    'n4HeightMax': '208',
    'n4WeightMin': '50',
    'n4WeightMax': '110',
    'n4AvgPointMin': '0',
    'n4AvgPointMax': '10',
    'n4PageNo': '1rd=0.8624194951185464'}

    res = requests.post(url, data=data)
    # soup 객체 만들기
    soup = BeautifulSoup(res.text, "lxml")
    #print(soup)
    target = "span_bp"+str(i)
    #regex = re.compile('.*span_bp.*')
    bpList = soup.find_all('span', {"class": target})
    for j in range(len(bpList)):
        if j >= 30:
            break
        bpArray.append(int(bpList[j].text.replace(",", "")))
print(bpArray)
bpArray.sort()
if len(bpArray) > 20:
    print((sum(bpArray[:20]))/20)