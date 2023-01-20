import csv
import requests
import os
from bs4 import BeautifulSoup
import math
import time

url ="https://fifaonline4.nexon.com/datacenter/PlayerList"


startTime = time.time()

# 엑셀 파일로 저장하기
# filename = "네이버 웹툰 인기 순위.csv"
# f = open(filename, "w", encoding="utf-8-sig", newline="")
# writer = csv.writer(f)

# columns_name = ["순위", "웹툰명"]

# writer.writerow(columns_name)
bpDict = {}
for i in range(95, 120):
    bpArray = []
    for j in range(1, 9):
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
                'n1Strong': str(j),
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
                'n4OvrMin': str(i),
                'n4OvrMax': str(i),
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
        target = "span_bp"+str(j)
        #regex = re.compile('.*span_bp.*')
        bpList = soup.find_all('span', {"class": target})

        for k in range(len(bpList)):
            if k >= 30:
                break
            bpArray.append(int(bpList[k].text.replace(",", "")))
    bpArray.sort()

    if len(bpArray) > 20:
        bpDict[i] = int((sum(bpArray[:20]))*0.9/20)


desktop = os.path.expanduser('~')
materialPath = f'material_crawler.txt'

f = open(materialPath, 'w')
for key, val in bpDict.items():
    f.write('{0}: {1}\n'.format(str(key), str(val)[:-4]))
f.close()
#f = open(materialPath, 'r')

# prices = {}
# #----------------
# while True:
#     line = f.readline()
#     if not line:
#         break
#     split_line = line.split(': ')
#     prices[int(split_line[0])] = int(split_line[1])
#
# f.close()

endTime = time.time()

print(f"{endTime - startTime:.5f} sec")
