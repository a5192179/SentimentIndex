def myMean(listA):
    if listA == []:
        return 0
    temp = 0
    for i in listA:
        temp += i
    return temp/len(listA)