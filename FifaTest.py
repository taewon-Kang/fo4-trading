import itertools
import csv
import requests
import os
from bs4 import BeautifulSoup
import math
import time
import re

# 1장 만들 때 필요한 기대 횟수(풀칸 기준, 인덱스 1부터 사용)
UPGRADE_PTG = [0, 1, 1.234, 1.5625, 2, 3.846]

# 강화 단계에 따른 오버롤 증가량(인덱스 1부터 사용)
OVERALL = [0, 0, 1, 2, 4, 6, 8]

# 강화 확률(풀칸 기준, 인덱스 1부터 사용)
PTG = [1, 1, 0.81, 0.64, 0.5, 0.26]

ICON_OVR = {

}
# 재료에 따른 강화 칸 수
ENH_GAGE = [{0},
            {-5: 0.584,
             -4: 0.7805,
             -3: 1.044,
             -2: 1.396,
             -1: 1.868,
             0: 2.5,
             1: 3.3475,
             2: 4.484,
             3: 5},

            {-4: 0.5215,
             -3: 0.697,
             -2: 0.932,
             -1: 1.242,
             0: 1.666,
             1: 2.237,
             2: 3,
             3: 4.03,
             4: 5},

            {-3: 0.524,
             -2: 0.6995,
             -1: 0.935,
             0: 1.25,
             1: 1.672,
             2: 2.237,
             3: 2.994,
             4: 4.009,
             5: 5},

            {-2: 0.559,
             -1: 0.7475,
             0: 1,
             1: 1.3385,
             2: 1.7925,
             3: 2.401,
             4: 3.2175,
             5: 4.313,
             6: 5},

            {-2: 0.558,
             -1: 0.747,
             0: 1,
             1: 1.339,
             2: 1.795,
             3: 2.406,
             4: 3.227,
             5: 4.3295,
             6: 5},

            {-2: 0.557,
             -1: 0.746,
             0: 1,
             1: 1.3405,
             2: 1.798,
             3: 2.412,
             4: 3.237,
             5: 4.346,
             6: 5},

            {-2: 0.56,
             -1: 0.75,
             0: 1,
             1: 1.33,
             2: 1.77,
             3: 2.37,
             4: 3.16,
             5: 4.21,
             6: 5}]

# 기본 재료 값
DEFAULT_MATERIAL_PRICES = '76: 20\n77: 25\n78: 35\n79: 35\n80: 60\n81: 70\n82: 90\n83: 110\n84: 400\n85: 500\n86: ' \
                          '600\n87: 700\n88: 800\n89: 950\n90: 1000\n91: 1000\n92: 1000\n93: 1050\n94: 1050\n95: ' \
                          '1000\n96: 1000\n97: 1200\n98: 1400\n99: 2400\n100: 3300\n101: 4300\n102: 6000\n103: ' \
                          '9300\n104: 14000\n105: 23000\n106: 39000\n107: 75000\n108: 150000\n109: 370000\n110: ' \
                          '630000\n111: 900000\n112: 1400000\n113: 2000000\n114: 3600000\n115: 4200000\n116: ' \
                          '6600000\n117: 9500000\n118: 14000000\n119: 19000000\n120: 27000000 '

desktop = os.path.expanduser('~')
pathMenu = input('재료값 1.수작업 2.크롤링\n')
filePath = 'material_crawler.txt' if pathMenu == '2' else 'material.txt'
materialPath = f'{filePath}'
if not os.path.isfile(materialPath):
    f = open(materialPath, 'w')
    f.write(DEFAULT_MATERIAL_PRICES)
f = open(materialPath, 'r')

prices = {}
nameDict = {}

while True:
    line = f.readline()
    if not line:
        break
    split_line = line.split(': ')
    prices[int(split_line[0])] = int(split_line[1])

f.close()

# 버닝 유무에 따른 배율 (1, 1.25)
burningDay = 1
# 계산기 최대 강화 단계
maxGrade = 4

couponTh = 500000

mode = 1


def get_best_materials(target, target_grade):
    material_combinations = []

    duplicate_dict = {}

    max_material_ovr = target + 6 if target_grade >= 4 else target + target_grade + 2

    start = target_grade - 6 if target_grade < 4 else -2

    end = target_grade + 2 if target_grade < 4 else 6

    for i in range(1, 6):

        ovr_list = []

        for j in range(i):

            plus1 = 0

            if i == 1:
                plus1 = 1

            for k in range(start, end + plus1):
                ovr_list.append(k)

        ovr_list = itertools.combinations(ovr_list, i)

        for e in ovr_list:

            temp_price = 0

            temp_gage = 0

            for el in e:
                temp_price += prices[target + el]

                temp_gage += ENH_GAGE[target_grade][el]

            e = list(map(lambda x: x + target, sorted(e)))

            if tuple(e) in duplicate_dict:

                continue

            else:

                duplicate_dict[tuple(e)] = 1
            temp_gage *= burningDay
            material_combinations.append([temp_gage if temp_gage <= 5 else 5, temp_price, e])

    combinations = sorted(material_combinations, key=lambda x: x[0])

    return combinations


def calc_efficiency():
    target_prices = [0]

    print("1카 오버롤 입력")

    grade1 = int(input())

    print("1카부터 {0}카까지 가격 입력".format(maxGrade))

    for i in range(1, maxGrade + 1):
        target_prices.append(int(input()))

    # i=시작 강화, j=목표 강화

    result_efficiency = []
    use_efficiency = []
    print("수수료 쿠폰 ex)30%면 30 입력")
    straight = [[0], [0, 0], [0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
    notStraight = [0]
    fee = 0.8 + 0.004 * int(input())

    for i in range(1, maxGrade):
        effs = []
        bestMat = []
        oneTimeBest = []
        for e in get_best_materials(grade1 + OVERALL[i], i):
            # e[1] 재료 값 e[2] 재료 목록

            ptg = PTG[i] * float(e[0]) * 0.2  # 확률
            card1fee = fee if target_prices[1] > 600000 else 0.8

            oneTime = target_prices[i + 1] * fee * ptg + target_prices[1] * (1 - ptg) * card1fee
            oneTimeBest.append([oneTime - (target_prices[i] + e[1]), e[1], e[2], ptg])
            if i == 1:
                bestMat.append([e[1] / ptg, e[2], str(ptg * 100)[:5], e[1],
                                target_prices[2] * fee - target_prices[1] - e[1] / ptg])  # 1->2
            elif i == 2:
                bestMat.append([e[1] / ptg + straight[1][2][0] / ptg, e[2], str(ptg * 100)[:5], e[1],
                                target_prices[3] * fee - target_prices[1] - e[1] / ptg - straight[1][2][
                                    0] / ptg])  # 1->3
            elif i == 3:
                bestMat.append([e[1] / ptg + straight[1][3][0] / ptg, e[2], str(ptg * 100)[:5], e[1],
                                target_prices[4] * fee - target_prices[1] - e[1] / ptg - straight[1][3][
                                    0] / ptg])  # 1->4
            elif i == 4:
                bestMat.append([e[1] / ptg + straight[1][4][0] / ptg, e[2], str(ptg * 100)[:5], e[1],
                                target_prices[5] * fee - target_prices[1] - e[1] / ptg - straight[1][4][
                                    0] / ptg])  # 1->5
            elif i == 5:
                bestMat.append([e[1] / ptg + straight[1][5][0] / ptg, e[2], str(ptg * 100)[:5], e[1],
                                target_prices[6] * fee - target_prices[1] - e[1] / ptg - straight[1][5][
                                    0] / ptg])  # 1->6
        straight[1].append(sorted(bestMat, key=lambda x: -x[4])[0])
        oneTimeBest = sorted(oneTimeBest, key=lambda x: -x[0])
        notStraight.append(oneTimeBest[0])
    for i in range(2, maxGrade + 1):
        print("1 => " + str(i) + " ==> 재료 값 : " + str(int(straight[1][i][0])) + str(straight[1][i][1]) + str(
            straight[1][i][2])[:5] + "% 수익 : " + str(int(straight[1][i][4])))
    for i in range(1, maxGrade):
        print(str(i) + " => " + str(i + 1) + " ==> 순이익 : " + str(int(notStraight[i][0])) + " 재료 : " + str(
            notStraight[i][1]) + str(
            notStraight[i][2]) + " 확률 : " + str(notStraight[i][3] * 100)[:5] + "%")
    if maxGrade == 3:
        if target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2] > notStraight[2][0]:
            straight[2].append([target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2],
                                'continuous'])  # 2->3
        else:
            straight[2].append([notStraight[2][0], 'one'])

    elif maxGrade == 4:
        if target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2] > notStraight[2][0]:
            straight[2].append([target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2],
                                'continuous'])  # 2->3
        else:
            straight[2].append([notStraight[2][0], 'one'])

        if target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2] > notStraight[2][0] + \
                notStraight[3][0]:
            straight[2].append([target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2],
                                'continuous'])  # 2->4
        else:
            straight[2].append([notStraight[2][0] + notStraight[3][0], 'one'])

        if target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3] > notStraight[3][0]:
            straight[3].append([target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3],
                                'continuous'])  # 3->4
        else:
            straight[3].append([notStraight[3][0], 'one'])

    elif maxGrade == 5:
        if target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2] > notStraight[2][0]:
            straight[2].append([target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2],
                                'continuous'])  # 2->3
        else:
            straight[2].append([notStraight[2][0], 'one'])

        if target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2] > notStraight[2][0] + \
                notStraight[3][0]:
            straight[2].append([target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2],
                                'continuous'])  # 2->4
        else:
            straight[2].append([notStraight[2][0] + notStraight[3][0], 'one'])

        if target_prices[5] * fee - straight[1][5][0] + straight[1][2][0] - target_prices[2] > notStraight[2][0] + \
                notStraight[3][0] + notStraight[4][0]:
            straight[2].append([target_prices[5] * fee - straight[1][5][0] + straight[1][2][0] - target_prices[2],
                                'continuous'])  # 2->5
        else:
            straight[2].append([notStraight[2][0] + notStraight[3][0] + notStraight[4][0], 'one'])

        if target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3] > notStraight[3][0]:
            straight[3].append([target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3],
                                'continuous'])  # 3->4
        else:
            straight[3].append([notStraight[3][0], 'one'])

        if target_prices[5] * fee - straight[1][5][0] + straight[1][3][0] - target_prices[3] > notStraight[3][0] + \
                notStraight[4][0]:
            straight[3].append([target_prices[5] * fee - straight[1][5][0] + straight[1][3][0] - target_prices[3],
                                'continuous'])  # 3->5
        else:
            straight[3].append([notStraight[3][0] + notStraight[4][0], 'one'])

        if target_prices[5] * fee - straight[1][5][0] + straight[1][4][0] - target_prices[4] > notStraight[4][0]:
            straight[4].append([target_prices[5] * fee - straight[1][5][0] + straight[1][4][0] - target_prices[4],
                                'continuous'])  # 4->5
        else:
            straight[4].append([notStraight[4][0], 'one'])

    elif maxGrade == 6:
        if target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2] > notStraight[2][0]:
            straight[2].append([target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2],
                                'continuous'])  # 2->3
        else:
            straight[2].append([notStraight[2][0], 'one'])

        if target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2] > notStraight[2][0] + \
                notStraight[3][0]:
            straight[2].append([target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2],
                                'continuous'])  # 2->4
        else:
            straight[2].append([notStraight[2][0] + notStraight[3][0], 'one'])

        if target_prices[5] * fee - straight[1][5][0] + straight[1][2][0] - target_prices[2] > notStraight[2][0] + \
                notStraight[3][0] + notStraight[4][0]:
            straight[2].append([target_prices[5] * fee - straight[1][5][0] + straight[1][2][0] - target_prices[2],
                                'continuous'])  # 2->5
        else:
            straight[2].append([notStraight[2][0] + notStraight[3][0] + notStraight[4][0], 'one'])

        if target_prices[6] * fee - straight[1][6][0] + straight[1][2][0] - target_prices[2] > notStraight[2][0] + \
                notStraight[3][0] + notStraight[4][0] + notStraight[5][0]:
            straight[2].append([target_prices[6] * fee - straight[1][6][0] + straight[1][2][0] - target_prices[2],
                                'continuous'])  # 2->6
        else:
            straight[2].append([notStraight[2][0] + notStraight[3][0] + notStraight[4][0] + notStraight[5][0], 'one'])

        if target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3] > notStraight[3][0]:
            straight[3].append([target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3],
                                'continuous'])  # 3->4
        else:
            straight[3].append([notStraight[3][0], 'one'])

        if target_prices[5] * fee - straight[1][5][0] + straight[1][3][0] - target_prices[3] > notStraight[3][0] + \
                notStraight[4][0]:
            straight[3].append([target_prices[5] * fee - straight[1][5][0] + straight[1][3][0] - target_prices[3],
                                'continuous'])  # 3->5
        else:
            straight[3].append([notStraight[3][0] + notStraight[4][0], 'one'])

        if target_prices[6] * fee - straight[1][6][0] + straight[1][3][0] - target_prices[3] > notStraight[3][0] + \
                notStraight[4][0] + notStraight[5][0]:
            straight[3].append([target_prices[6] * fee - straight[1][6][0] + straight[1][3][0] - target_prices[3],
                                'continuous'])  # 3->6
        else:
            straight[3].append([notStraight[3][0] + notStraight[4][0] + notStraight[5][0], 'one'])

        if target_prices[5] * fee - straight[1][5][0] + straight[1][4][0] - target_prices[4] > notStraight[4][0]:
            straight[4].append([target_prices[5] * fee - straight[1][5][0] + straight[1][4][0] - target_prices[4],
                                'continuous'])  # 4->5
        else:
            straight[4].append([notStraight[4][0], 'one'])

        if target_prices[6] * fee - straight[1][6][0] + straight[1][4][0] - target_prices[4] > notStraight[4][0] + \
                notStraight[5][0]:
            straight[4].append([target_prices[6] * fee - straight[1][6][0] + straight[1][4][0] - target_prices[4],
                                'continuous'])  # 4->6
        else:
            straight[4].append([notStraight[5][0], 'one'])

        if target_prices[6] * fee - straight[1][6][0] + straight[1][5][0] - target_prices[5] > notStraight[5][0]:
            straight[5].append([target_prices[6] * fee - straight[1][6][0] + straight[1][5][0] - target_prices[5],
                                'continuous'])  # 5->6
        else:
            straight[5].append([notStraight[5][0], 'one'])

    maxEff = 0
    startG = 0
    endG = 0
    howMuch = 0
    for i in range(1, maxGrade):
        for j in range(i + 1, maxGrade + 1):
            eff = straight[i][j][0 if i != 1 else 4]
            if i == 1 and j == 2:
                if straight[1][2][4] > notStraight[1][0]:
                    eff = straight[1][2][4]
                else:
                    eff = notStraight[1][0]
            if maxEff < eff:
                maxEff = eff
                startG = i
                endG = j
                if i == 1:
                    if j == 2:
                        if straight[1][2][4] > notStraight[1][0]:
                            howMuch = 'continuous'
                        else:
                            howMuch = 'one'
                    else:
                        howMuch = 'continuous'
                else:
                    howMuch = straight[i][j][1]

    print(str(startG) + " => " + str(endG) + " ===> 순이익 : " + str(int(maxEff)) + " 횟수 : " + str(howMuch))


seed = 0
strSeason = ['101']
searchFee = 30

SeasonDict = {
    '101': 'ICON',
    '278': '23 TOTY',
    '279': '23 TOTY-N',
    '272': 'BWC',
    '273': 'WC22',
    '268': 'LN',
    '274': 'RMCF',
    '258': '22 TOTY',
    '259': '22 TOTY-N',
    '267': '22 TOTS',
    '280': '22 UCL'
}
searchMinOvr = 103
searchMaxOvr = 200
while True:
    seasonString = []
    for e in strSeason:
        seasonString.append(SeasonDict[e])
    print("------------------------------------------------------------")
    print(
        "메뉴 [1]=강화데이 {0}, [2]=1카부터 {1}카까지 강화 계산기, [3]=재료 값 출력, [4]=재료 값 수정, [5]=최대 강화:{1}, [6]=재료값 크롤링, [7]=매물 검색기, [8]=강화 시드:{2}, [9]=검색기 시즌 수정:{3}, [10]=수수료 수정:{4}, [11]=검색 오버롤 범위:{5}~{6}, [12]=모드 설정[{7}]".format(
            "ON/[OFF]" if burningDay == 1 else "[ON]/OFF", maxGrade, seed, seasonString, searchFee, searchMinOvr,
            searchMaxOvr, "NORMAL" if mode == 1 else "ONE"))
    choose = int(input())

    if choose == 1:

        burningDay = 1 if burningDay == 1.25 else 1.25
    elif choose == 2:

        calc_efficiency()

    elif choose == 3:

        for key, val in prices.items():
            print("%s:%s만원" % (key, val))

    elif choose == 4:

        while True:
            print("바꿀 재료 오버롤 입력 -1 입력 시 메뉴로 이동")
            targetOVR = int(input())

            if targetOVR == -1:
                break
            print("재료 값 입력")
            newPrice = int(input())

            prices[targetOVR] = newPrice
    elif choose == 5:
        print("최대 강화 단계 입력 max = 6")
        maxGrade = int(input())

    elif choose == 6:
        url = "https://fifaonline4.nexon.com/datacenter/PlayerList"

        startTime = time.time()

        # 엑셀 파일로 저장하기
        # filename = "네이버 웹툰 인기 순위.csv"
        # f = open(filename, "w", encoding="utf-8-sig", newline="")
        # writer = csv.writer(f)

        # columns_name = ["순위", "웹툰명"]

        # writer.writerow(columns_name)
        bpDict = {}
        for i in range(97, 126):
            bpArray = []
            for j in range(1, 9):
                data = {'n1Confederation': '0',
                        'n4LeagueId': '0',
                        "strSeason": ',216,217,218,262,236,254,233,231,237,246,249,253,251,252,256,261,264,265,101,214,207,206,202,201,258,259,240,241,210,225,234,294,247,297,510,508,300,257,507,260,250,278,279,',
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
                target = "span_bp" + str(j)
                # regex = re.compile('.*span_bp.*')
                bpList = soup.find_all('span', {"class": target})
                for k in range(len(bpList)):
                    if k >= 30:
                        break
                    bpArray.append(int(bpList[k].text.replace(",", "")))
            bpArray.sort()

            if len(bpArray) > 25:
                bpDict[i] = int((sum(bpArray[:25])) * 0.94 / 25)
            else:
                bpDict[i] = int((sum(bpArray[:10])) * 0.94 / 10)

        desktop = os.path.expanduser('~')
        materialPath = f'material_crawler.txt'

        f = open(materialPath, 'w')
        for key, val in bpDict.items():
            f.write('{0}: {1}\n'.format(str(key), str(val)[:-4]))
        f.close()
        # f = open(materialPath, 'r')

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

        f = open(materialPath, 'r')

        while True:
            line = f.readline()
            if not line:
                break
            split_line = line.split(': ')
            prices[int(split_line[0])] = int(split_line[1])

        f.close()

        print(f"{endTime - startTime:.5f} sec")
    elif choose == 7:
        url = "https://fifaonline4.nexon.com/datacenter/PlayerList"

        startTime = time.time()

        bpDict = {}

        nameDict = {}

        tempFee = searchFee * 0.004 + 0.8

        for e in strSeason:
            convertedSeason = ','
            convertedSeason = convertedSeason + e + ','
            data = {'n1Confederation': '0',
                    'n4LeagueId': '0',
                    "strSeason": convertedSeason,  # 272 273 : BWC, WC22 278, 279: 23 TOTY, 274, 268: LN, RMF
                    'n1LeftFootAblity': '0',
                    'n1RightFootAblity': '0',
                    'n1SkillMove': '0',
                    'n1InterationalRep': '0',
                    'n4BirthMonth': '0',
                    'n4BirthDay': '0',
                    'n4TeamId': '0',
                    'n4NationId': '0',
                    'n1Strong': '1',
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
                    'n4OvrMin': searchMinOvr,
                    'n4OvrMax': searchMaxOvr,
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
            ovrClass = re.compile('^skillData_')
            ovrList = soup.find_all('span', {"class": ovrClass, "data-type": False})
            tempOvrList = []
            for e2 in ovrList:
                if ' ' in e2.get_text():
                    if e2.get_text().replace(" ", ""):
                        tempOvrList.append(e2.get_text().replace(" ", "").replace("\r\n", ""))

            nameList = soup.find_all('div', {"class": "name"})
            seasonList = soup.find_all('div', {"class": "season"})
            prefixSeason = []
            for e2 in seasonList:
                prefixSeason.append(e2.find_next('img').get('src').split('/season/')[1][:-4])
            tempNameList = []
            indexCnt = 0
            for e2 in nameList:
                nameDict["[" + prefixSeason[indexCnt] + "] " + e2.get_text()] = []
                tempNameList.append("[" + prefixSeason[indexCnt] + "] " + e2.get_text())
                indexCnt += 1

            for idx in range(len(tempOvrList)):
                nameDict[tempNameList[idx]].append(tempOvrList[idx])

            for k in range(1, 7):
                bpTarget = "span_bp" + str(k)
                bpAllList = soup.find_all('span', {"class": bpTarget})
                for idx in range(len(bpAllList)):
                    nameDict[tempNameList[idx]].append(bpAllList[idx].get_text())

        endTime = time.time()

        print(f"{endTime - startTime:.5f} sec")

        # ----------------------------------------------------------
        allBestCase = []
        nowCnt = 1
        startTime = time.time()
        for key, value in nameDict.items():

            target_prices = [0]

            print(key)
            print(str(nowCnt) + "/" + str(len(nameDict)))
            nowCnt += 1

            grade1 = int(value[0])

            for i in range(1, maxGrade + 1):
                convertedStr = value[i].replace(",", "")
                splicedStr = convertedStr[:len(convertedStr) - 4]
                ratio = 1
                if i == 1 or i == 4:
                    ratio = 1.04
                target_prices.append(int(splicedStr) * ratio)
            if seed > 0 and target_prices[1] > seed:
                continue
            straight = [[0], [0, 0], [0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
            notStraight = [0]
            fee = tempFee

            for i in range(1, maxGrade):
                effs = []
                bestMat = []
                oneTimeBest = []
                for e in get_best_materials(grade1 + OVERALL[i], i):
                    # e[1] 재료 값 e[2] 재료 목록

                    ptg = PTG[i] * float(e[0]) * 0.2  # 확률
                    card1fee = fee if target_prices[1] > 600000 else 0.8

                    oneTime = target_prices[i + 1] * fee * ptg + target_prices[1] * (1 - ptg) * card1fee
                    oneTimeBest.append([oneTime - (target_prices[i] + e[1]), e[1], e[2], ptg])
                    if i == 1:
                        bestMat.append([e[1] / ptg, e[2], str(ptg * 100)[:5], e[1],
                                        target_prices[2] * fee - target_prices[1] - e[1] / ptg])  # 1->2
                    elif i == 2:
                        bestMat.append([e[1] / ptg + straight[1][2][0] / ptg, e[2], str(ptg * 100)[:5], e[1],
                                        target_prices[3] * fee - target_prices[1] - e[1] / ptg - straight[1][2][
                                            0] / ptg])  # 1->3
                    elif i == 3:
                        bestMat.append([e[1] / ptg + straight[1][3][0] / ptg, e[2], str(ptg * 100)[:5], e[1],
                                        target_prices[4] * fee - target_prices[1] - e[1] / ptg - straight[1][3][
                                            0] / ptg])  # 1->4
                    elif i == 4:
                        bestMat.append([e[1] / ptg + straight[1][4][0] / ptg, e[2], str(ptg * 100)[:5], e[1],
                                        target_prices[5] * fee - target_prices[1] - e[1] / ptg - straight[1][4][
                                            0] / ptg])  # 1->5
                    elif i == 5:
                        bestMat.append([e[1] / ptg + straight[1][5][0] / ptg, e[2], str(ptg * 100)[:5], e[1],
                                        target_prices[6] * fee - target_prices[1] - e[1] / ptg - straight[1][5][
                                            0] / ptg])  # 1->6
                straight[1].append(sorted(bestMat, key=lambda x: -x[4])[0])
                oneTimeBest = sorted(oneTimeBest, key=lambda x: -x[0])
                notStraight.append(oneTimeBest[0])
            for i in range(2, maxGrade + 1):
                print("1 => " + str(i) + " ==> 재료 값 : " + str(int(straight[1][i][0])) + str(straight[1][i][1]) + str(
                    straight[1][i][2])[:5] + "% 수익 : " + str(int(straight[1][i][4])))
            for i in range(1, maxGrade):
                print(str(i) + " => " + str(i + 1) + " ==> 순이익 : " + str(int(notStraight[i][0])) + " 재료 : " + str(
                    notStraight[i][1]) + str(
                    notStraight[i][2]) + " 확률 : " + str(notStraight[i][3] * 100)[:5] + "%")
            if maxGrade == 3:
                if target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2] > notStraight[2][
                    0]:
                    straight[2].append(
                        [target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2],
                         'continuous'])  # 2->3
                else:
                    straight[2].append([notStraight[2][0], 'one'])

            elif maxGrade == 4:
                if target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2] > notStraight[2][
                    0]:
                    straight[2].append(
                        [target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2],
                         'continuous'])  # 2->3
                else:
                    straight[2].append([notStraight[2][0], 'one'])

                if target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2] > notStraight[2][
                    0] + notStraight[3][0]:
                    straight[2].append(
                        [target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2],
                         'continuous'])  # 2->4
                else:
                    straight[2].append([notStraight[2][0] + notStraight[3][0], 'one'])

                if target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3] > notStraight[3][
                    0]:
                    straight[3].append(
                        [target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3],
                         'continuous'])  # 3->4
                else:
                    straight[3].append([notStraight[3][0], 'one'])

            elif maxGrade == 5:
                if target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2] > notStraight[2][
                    0]:
                    straight[2].append(
                        [target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2],
                         'continuous'])  # 2->3
                else:
                    straight[2].append([notStraight[2][0], 'one'])

                if target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2] > notStraight[2][
                    0] + notStraight[3][0]:
                    straight[2].append(
                        [target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2],
                         'continuous'])  # 2->4
                else:
                    straight[2].append([notStraight[2][0] + notStraight[3][0], 'one'])

                if target_prices[5] * fee - straight[1][5][0] + straight[1][2][0] - target_prices[2] > notStraight[2][
                    0] + notStraight[3][0] + notStraight[4][0]:
                    straight[2].append(
                        [target_prices[5] * fee - straight[1][5][0] + straight[1][2][0] - target_prices[2],
                         'continuous'])  # 2->5
                else:
                    straight[2].append([notStraight[2][0] + notStraight[3][0] + notStraight[4][0], 'one'])

                if target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3] > notStraight[3][
                    0]:
                    straight[3].append(
                        [target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3],
                         'continuous'])  # 3->4
                else:
                    straight[3].append([notStraight[3][0], 'one'])

                if target_prices[5] * fee - straight[1][5][0] + straight[1][3][0] - target_prices[3] > notStraight[3][
                    0] + notStraight[4][0]:
                    straight[3].append(
                        [target_prices[5] * fee - straight[1][5][0] + straight[1][3][0] - target_prices[3],
                         'continuous'])  # 3->5
                else:
                    straight[3].append([notStraight[3][0] + notStraight[4][0], 'one'])

                if target_prices[5] * fee - straight[1][5][0] + straight[1][4][0] - target_prices[4] > notStraight[4][
                    0]:
                    straight[4].append(
                        [target_prices[5] * fee - straight[1][5][0] + straight[1][4][0] - target_prices[4],
                         'continuous'])  # 4->5
                else:
                    straight[4].append([notStraight[4][0], 'one'])

            elif maxGrade == 6:
                if target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2] > notStraight[2][
                    0]:
                    straight[2].append(
                        [target_prices[3] * fee - straight[1][3][0] + straight[1][2][0] - target_prices[2],
                         'continuous'])  # 2->3
                else:
                    straight[2].append([notStraight[2][0], 'one'])

                if target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2] > notStraight[2][
                    0] + notStraight[3][0]:
                    straight[2].append(
                        [target_prices[4] * fee - straight[1][4][0] + straight[1][2][0] - target_prices[2],
                         'continuous'])  # 2->4
                else:
                    straight[2].append([notStraight[2][0] + notStraight[3][0], 'one'])

                if target_prices[5] * fee - straight[1][5][0] + straight[1][2][0] - target_prices[2] > notStraight[2][
                    0] + notStraight[3][0] + notStraight[4][0]:
                    straight[2].append(
                        [target_prices[5] * fee - straight[1][5][0] + straight[1][2][0] - target_prices[2],
                         'continuous'])  # 2->5
                else:
                    straight[2].append([notStraight[2][0] + notStraight[3][0] + notStraight[4][0], 'one'])

                if target_prices[6] * fee - straight[1][6][0] + straight[1][2][0] - target_prices[2] > notStraight[2][
                    0] + notStraight[3][0] + notStraight[4][0] + notStraight[5][0]:
                    straight[2].append(
                        [target_prices[6] * fee - straight[1][6][0] + straight[1][2][0] - target_prices[2],
                         'continuous'])  # 2->6
                else:
                    straight[2].append(
                        [notStraight[2][0] + notStraight[3][0] + notStraight[4][0] + notStraight[5][0], 'one'])

                if target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3] > notStraight[3][
                    0]:
                    straight[3].append(
                        [target_prices[4] * fee - straight[1][4][0] + straight[1][3][0] - target_prices[3],
                         'continuous'])  # 3->4
                else:
                    straight[3].append([notStraight[3][0], 'one'])

                if target_prices[5] * fee - straight[1][5][0] + straight[1][3][0] - target_prices[3] > notStraight[3][
                    0] + notStraight[4][0]:
                    straight[3].append(
                        [target_prices[5] * fee - straight[1][5][0] + straight[1][3][0] - target_prices[3],
                         'continuous'])  # 3->5
                else:
                    straight[3].append([notStraight[3][0] + notStraight[4][0], 'one'])

                if target_prices[6] * fee - straight[1][6][0] + straight[1][3][0] - target_prices[3] > notStraight[3][
                    0] + notStraight[4][0] + notStraight[5][0]:
                    straight[3].append(
                        [target_prices[6] * fee - straight[1][6][0] + straight[1][3][0] - target_prices[3],
                         'continuous'])  # 3->6
                else:
                    straight[3].append([notStraight[3][0] + notStraight[4][0] + notStraight[5][0], 'one'])

                if target_prices[5] * fee - straight[1][5][0] + straight[1][4][0] - target_prices[4] > notStraight[4][
                    0]:
                    straight[4].append(
                        [target_prices[5] * fee - straight[1][5][0] + straight[1][4][0] - target_prices[4],
                         'continuous'])  # 4->5
                else:
                    straight[4].append([notStraight[4][0], 'one'])

                if target_prices[6] * fee - straight[1][6][0] + straight[1][4][0] - target_prices[4] > notStraight[4][
                    0] + notStraight[5][0]:
                    straight[4].append(
                        [target_prices[6] * fee - straight[1][6][0] + straight[1][4][0] - target_prices[4],
                         'continuous'])  # 4->6
                else:
                    straight[4].append([notStraight[5][0], 'one'])

                if target_prices[6] * fee - straight[1][6][0] + straight[1][5][0] - target_prices[5] > notStraight[5][
                    0]:
                    straight[5].append(
                        [target_prices[6] * fee - straight[1][6][0] + straight[1][5][0] - target_prices[5],
                         'continuous'])  # 5->6
                else:
                    straight[5].append([notStraight[5][0], 'one'])

            maxEff = 0
            startG = 0
            endG = 0
            howMuch = 0
            for i in range(1, maxGrade):
                if mode == 2:
                    howMuch = 'one'
                    if notStraight[i][0] > maxEff:
                        maxEff = notStraight[i][0]
                        startG = i
                        endG = i + 1
                else:
                    for j in range(i + 1, maxGrade + 1):
                        eff = straight[i][j][0 if i != 1 else 4]
                        if i == 1 and j == 2:
                            if straight[1][2][4] > notStraight[1][0]:
                                eff = straight[1][2][4]
                            else:
                                eff = notStraight[1][0]
                        if maxEff < eff:
                            maxEff = eff
                            startG = i
                            endG = j
                            if i == 1:
                                if j == 2:
                                    if straight[1][2][4] > notStraight[1][0]:
                                        howMuch = 'continuous'
                                    else:
                                        howMuch = 'one'
                                else:
                                    howMuch = 'continuous'
                            else:
                                howMuch = straight[i][j][1]

            print(str(startG) + " => " + str(endG) + " ===> 순이익 : " + str(int(maxEff)) + " 횟수 : " + str(howMuch))
            effPercent = int(maxEff) / (target_prices[endG] * tempFee - maxEff) if (target_prices[
                                                                                        endG] * tempFee - maxEff) != 0 else 0
            allBestCase.append([key, startG, endG, int(maxEff), grade1, target_prices[1], howMuch,
                                target_prices[endG] * tempFee - maxEff, effPercent])

        for e in sorted(allBestCase, key=lambda x: -x[3]):
            if seed > 0:
                if seed > e[7]:
                    print(e[0] + "(OVR" + str(e[4]) + ") " + str(e[1]) + " => " + str(e[2]) + " 수익 : " + str(
                        e[3]) + "  1카 가격 : {0} 수익% : {1}".format(str(int(e[5])), str(e[8])[:5]))
            else:
                print(e[0] + "(OVR" + str(e[4]) + ") " + str(e[1]) + " => " + str(e[2]) + " 수익 : " + str(
                    e[3]) + "  1카 가격 : {0} 수익% : {1}".format(str(int(e[5])), str(e[8])[:5]))
        endTime = time.time()
        print(f"{endTime - startTime:.5f} sec")
    elif choose == 8:
        print("시드 입력 ex) 400억 = 4000000")
        seed = int(input())

    elif choose == 9:
        print("시즌 입력 0 입력 시 모두 선택, -1 입력 시 종료")
        print(SeasonDict)
        tempSeason = []
        while True:
            season = input()
            if season == '-1':
                break
            elif season == '0':
                tempSeason = list(SeasonDict.keys())
            else:
                tempSeason.append(season)
        if len(tempSeason) > 0:
            strSeason = tempSeason
    elif choose == 10:
        print('수수료 쿠폰 입력 없으면 0')
        searchFee = int(input())
    elif choose == 11:
        print('최소 오버롤 입력')
        searchMinOvr = int(input())
        print('최대 오버롤 입력')
        searchMaxOvr = int(input())
    elif choose == 12:
        print('모드 입력 1)일반 모드 2)인강, 강화 데이 모드')
        mode = int(input())

os.system("pause")