from itertools import combinations

import os

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

prices = {
    76: 20,
    77: 25,
    78: 35,
    79: 35,
    80: 60,
    81: 70,
    82: 90,
    83: 110,
    84: 400,
    85: 500,
    86: 600,
    87: 700,
    88: 800,
    89: 950,
    90: 1100,
    91: 1100,
    92: 1300,
    93: 1400,
    94: 1500,
    95: 900,
    96: 1000,
    97: 1200,
    98: 1600,
    99: 2500,
    100: 3150,
    101: 4800,
    102: 6800,
    103: 9200,
    104: 14000,
    105: 23500,
    106: 41000,
    107: 79000,
    108: 180000,
    109: 320000,
    110: 630000,
    111: 900000,
    112: 1400000,
    113: 2000000,
    114: 3600000,
    115: 4200000,
    116: 6600000,
    117: 9500000,
    118: 14000000,
    119: 19000000,
    120: 27000000}

UPGRADE_PTG = [0, 1, 1.234, 1.5625, 2, 3.846]

OVERALL = [0, 0, 1, 2, 4, 6, 8]

PTG = [1, 1, 0.81, 0.64, 0.5, 0.26]


def getBestCombi(target, targetGrade):
    combis = []

    dupDict = {}

    maxGageAbil = target + 6 if targetGrade >= 4 else target + targetGrade + 2

    start = targetGrade - 6 if targetGrade < 4 else -2

    end = targetGrade + 2 if targetGrade < 4 else 6

    for i in range(1, 6):

        abilList = []

        for j in range(i):

            plus1 = 0

            if i == 1:
                plus1 = 1

            for k in range(start, end + plus1):
                abilList.append(k)

        abilCombis = combinations(abilList, i)

        for e in abilCombis:

            tempPrice = 0

            tempGage = 0

            for el in e:
                tempPrice += prices[target + el]

                tempGage += ENH_GAGE[targetGrade][el]

            e = list(map(lambda x: x + target, sorted(e)))

            if tuple(e) in dupDict:

                continue

            else:

                dupDict[tuple(e)] = 1
            combis.append([tempGage if tempGage <= 5 else 5, tempPrice, e])

    combis = sorted(combis, key=lambda x: x[0])

    return combis


def getBestCombi2(target, targetGrade, purposeGage):
    combis = []

    dupDict = {}

    maxGageAbil = target + 6 if targetGrade >= 4 else target + targetGrade + 2

    start = targetGrade - 6 if targetGrade < 4 else -2

    end = targetGrade + 1 if targetGrade < 4 else 5

    combis.append([5, prices[maxGageAbil], maxGageAbil])

    for i in range(2, 6):

        abilList = []

        for j in range(i):

            for k in range(start, end):
                abilList.append(k)

        abilCombis = combinations(abilList, i)

        for e in abilCombis:

            tempPrice = 0

            tempGage = 0

            for el in e:
                tempPrice += prices[target + el]

                tempGage += ENH_GAGE[targetGrade][el]

            e = list(map(lambda x: x + target, sorted(e)))

            if tuple(e) in dupDict:

                continue

            else:

                dupDict[tuple(e)] = 1

            if tempGage >= float(purposeGage):
                combis.append([tempPrice, e])

    combis = sorted(combis, key=lambda x: x[0])

    return combis


def calcEfficiency():
    targetPrices = [0]

    print("Input Grade 1 Overall")

    grade1 = int(input())

    print("Input Prices Grade 1 ~ 6")

    for i in range(1, 7):
        targetPrices.append(int(input()))

    # i=시작 강화, j=목표 강화

    resEff = []

    for i in range(1, 7):

        for j in range(i + 1, 7):

            resPrice = 0

            for k in range(i, j):

                matCnt = 1

                for l in range(j - 1, k - 1, -1):
                    matCnt *= UPGRADE_PTG[l]

                if (i == 1 and j == 6):
                    print((getBestCombi(grade1 + OVERALL[k], k)[0][0] + targetPrices[i]) * matCnt)

                resPrice += (getBestCombi(grade1 + OVERALL[k], k)[0][0] + targetPrices[i]) * matCnt

            eff = (targetPrices[j] * 0.94) / resPrice

            resEff.append([eff, [i, j], targetPrices[j] * 0.94, resPrice])

    resEff = sorted(resEff, key=lambda x: -x[0])

    for i in range(5):
        print(resEff[i])


def calcEfficiency2():
    targetPrices = [0]

    print("Input Grade 1 Overall")

    grade1 = int(input())

    print("Input Prices Grade 1 ~ 6")

    for i in range(1, 7):
        targetPrices.append(int(input()))

    # i=시작 강화, j=목표 강화

    resEff = []

    print("fee")

    fee = 0.8 + 0.004 * int(input())

    for i in range(1, 6):

        effs = []

        for e in getBestCombi(grade1 + OVERALL[i], i):
            # 강화 확률
            ptg = PTG[i] * float(e[0]) * 0.2
            # 기대 가격
            res = (targetPrices[i + 1] * ptg * fee + targetPrices[1] * (1 - ptg) * 0.8)

            spend = targetPrices[i] + e[1]

            effs.append([res / spend, e[1], e[2], e[0], int(res - spend), int((res * (1 / fee)) - spend),
                         int(res - spend)/ptg, int((res * (1 / fee)) - spend) / ptg])

        effs = sorted(effs, key=lambda x: -x[6])
        if effs[0][6] < 0:
            effs = sorted(effs, key=lambda x: -x[0])
            resEff.append(effs[0])
        else:
            resEff.append(effs[0])

    for e in resEff:
        print(str(e[0])[:5] + " " + str(e[0] * (1 / fee))[:5] + " " + str(e[4]) + " " + str(e[5]) + " 재료 값:" + str(
            e[1]) + " " + str(e[2]) + " " + str(e[3]) + "칸" + " " + str(int(e[6])) + " " + str(int(e[7])))


# print("Input Overall")

# target = int(input())

# print("Input Current Grade")

# targetGrade = int(input())

# print("Input Upgrade Purpose")

# purposeGage = int(input())

# res = getBestCombi(99, 5, 5)

# minPrice = res[0][0]

#

# for e in res:

#     if e[0] == minPrice:

#         print(e)

# os.system("pause")


# calcEfficiency()

while True:

    choose = int(input())

    if choose == 1:

        print("Input Overall")

        target = int(input())

        print("Input Current Grade")

        targetGrade = int(input())

        print("Input Upgrade Purpose")

        purposeGage = float(input())

        res = getBestCombi2(target, targetGrade, purposeGage)

        minPrice = res[0][0]

        for e in res:

            if e[0] == minPrice:
                print(e)

    elif choose == 2:

        calcEfficiency2()

    elif choose == 3:

        for key, val in prices.items():
            print("%d:%d만원" % (key, val))

    elif choose == 4:

        while True:

            targetOVR = int(input())

            if targetOVR == -1:
                break

            newPrice = int(input())

            prices[targetOVR] = newPrice