import itertools
import os
import constant

desktop = os.path.expanduser('~')
materialPath = f'material.txt'
if not os.path.isfile(materialPath):
    f = open(materialPath, 'w')
    f.write(constant.DEFAULT_MATERIAL_PRICES)
f = open(materialPath, 'r')

prices = {}

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

                temp_gage += constant.ENH_GAGE[target_grade][el]

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

    fee = 0.8 + 0.004 * int(input())

    for i in range(1, maxGrade):

        effs = []

        for e in get_best_materials(grade1 + constant.OVERALL[i], i):
            ptg = constant.PTG[i] * float(e[0]) * 0.2

            res = (target_prices[i + 1] * ptg * fee + target_prices[1] * (1 - ptg) * 0.8)

            card1 = 0.8 if i != 1 else 1

            useRes = (target_prices[i + 1] * ptg + target_prices[1] * (1 - ptg) * card1)

            spend = target_prices[i] + e[1]

            effs.append([res / spend, e[1], e[2], e[0], int(res - spend), int((res * (1 / fee)) - spend),
                         int(res - spend) / ptg, int(useRes - spend) / ptg, ptg, useRes / spend])

        effs = sorted(effs, key=lambda x: -x[6])
        if effs[0][6] < 0:
            effs = sorted(effs, key=lambda x: -x[0])
            result_efficiency.append(effs[0])
        else:
            result_efficiency.append(effs[0])
        effs = sorted(effs, key=lambda x: -x[7])
        if effs[0][7] < 0:
            effs = sorted(effs, key=lambda x: -x[9])
            use_efficiency.append(effs[0])
        else:
            use_efficiency.append(effs[0])

    best_enhance = []
    print("/////////////////////////////////////////")
    print("결과")
    print("수쿠 적용 시       사용 시")
    for i in range(len(result_efficiency)):
        e = result_efficiency[i]
        e2 = use_efficiency[i]
        print(str(e[0])[:5] + "(" + str(int(e[6])) + ") / " + str(e2[9])[:5] + "(" + str(int(e2[7])) + ") 재료 값:" + str(
            e[1]) + str(e[2]) + " " + str(e[3]) + "칸(" + str(e[8] * 100)[:4] + "%) 재료 값:" + str(e2[1]) + str(
            e2[2]) + " " + str(e2[3]) + "칸(" + str(e2[8] * 100)[:4] + "%)")
        best_enhance.append([i, i + 1, int(e[6])])
        for j in range(i + 1, len(result_efficiency)):
            tempPrice = 0
            for k in range(i, j):
                tempPrice += result_efficiency[k][7]
            tempPrice += result_efficiency[j][6]
            best_enhance.append([i, j + 1, tempPrice])
    best_enhance = sorted(best_enhance, key=lambda x: -x[2])
    print(str(best_enhance[0][0] + 1) + " ==> " + str(best_enhance[0][1] + 1) + " : " + str(best_enhance[0][2]))


while True:
    print("------------------------------------------------------------")
    print("메뉴 [1]=강화데이 {0}, [2]=1카부터 {1}카까지 강화 계산기, [3]=재료 값 출력, [4]=재료 값 수정, [5]=최대 강화:{1}".format(
        "ON/[OFF]" if burningDay == 1 else "[ON]/OFF", maxGrade))
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
