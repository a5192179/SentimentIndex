def myMean(listA):
    if listA == []:
        return 0
    temp = 0
    for i in listA:
        temp += i
    return temp/len(listA)

def normalized(listA):
    listB = []
    if listA == []:
        return 0
    maxNum = 0
    for i in listA:
        if listA != 0:
            maxNum = listA[0]
            break
    if maxNum == 0:
        raise Exception(['all num is 0, no denominator'])
    for i in listA:
        if maxNum < i:
            maxNum = i
    for i in listA:
        listB.append(i/maxNum)
    return listB