import csv
import os

# inputFile = '../../Data/CleanedTestMessage_MoreMark.csv'
# outputFile = '../../Data/MarkedTestMessage_MoreMark.csv'
inputFile = '../../Data/BigData/CleanedMessage_MoreMark.csv'
outputFile = '../../Data/BigData/MarkedMessage_MoreMark.csv'

if os.path.exists(outputFile):
    os.remove(outputFile)

bSetLenth = False
minLenth = 10

allLineNum = 0
lineNum = 0
bullNum = 0
bearNum = 0
with open(inputFile, 'r', newline='', encoding='utf-8') as f:
    lines = csv.reader(f)
    for line in lines:
        allLineNum += 1

        if not len(line[2]):
            continue

        if bSetLenth:
            splitLine = line[3].split(' ')
            if len(splitLine) < minLenth:
                continue

        lineNum += 1
        if line[2] == 'Bearish':
            line[2] = '-1'
            bearNum += 1
        elif line[2] == 'Bullish':
            line[2] = '1'
            bullNum += 1
        else:
            raise Exception('wrong mark ' + line[2])

        # 保存
        with open(outputFile, 'a', newline='', encoding='utf-8') as fwrite:
            writer = csv.writer(fwrite)
            writer.writerow(line)

        if lineNum % 1000 == 0:
            print('lineNum =', lineNum)
    print('allLineNum=', allLineNum, ', lineNum =', lineNum, ', bullLineNum=', bullNum, ', bearLineNum=', bearNum)