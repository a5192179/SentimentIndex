import csv

import datetime
import logging
import sys
import os
import time

import matplotlib.pyplot as plt


def myMean(listA):
    if listA == []:
        return 0
    temp = 0
    for i in listA:
        temp += i
    return temp/len(listA)


if __name__ == '__main__':
    # testDataPath = '../../Data/AfterTrainDataDate/CleanedMessage.csv'
    testDataPath = '../../Data/BigData3/CleanedMessage.csv'
    inputPath = '../../Data/Output/timeAnalyse'
    outputPath = inputPath + '/testIndex'
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    logger = logging.getLogger("AppName")
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
    file_handler = logging.FileHandler(outputPath + "/log.log")
    file_handler.setFormatter(formatter)
    # 控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.formatter = formatter  # 也可以直接给formatter赋值
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    logger.info('Begin')

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' all begin')

    # test ==========================================================================
    testMarks = []
    testMes = []
    testTime = []
    testID = []
    lineNum = 0
    bullLineNum = 0
    bearLineNum = 0
    with open(testDataPath, 'r', newline='', encoding='utf-8') as f:
        lines = csv.reader(f)
        for line in lines:
            lineNum += 1
            testMes.append(line[3])
            testTime.append(line[1])
            testID.append(line[0])
            if line[2] == '1':
                bullLineNum += 1
                testMarks.append(1)
            elif line[2] == '-1':
                bearLineNum += 1
                testMarks.append(0)
            else:
                testMarks.append(0.5)
    logger.info('lineNum =' + str(lineNum) + ', bullLineNum=' + str(bullLineNum) + ', bearLineNum=' + str(bearLineNum))

    # my test ========================================================================
    beginTime = "2010-01-11T00:00:00Z"
    beginTime = time.strptime(beginTime, "%Y-%m-%dT%H:%M:%SZ")
    beginTime = time.mktime(beginTime)
    # date_str = "2016-11-30T13:00:00Z"
    # a = time.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    # a = time.mktime(a)
    messageNum = [0] * 24

    for i in range(len(testTime)):

        messageTime = testTime[i]
        messageTime = time.strptime(messageTime, "%Y-%m-%dT%H:%M:%SZ")
        messageTime = time.mktime(messageTime)
        if messageTime < beginTime:
            continue
        temp = testTime[i].split('T')
        temp2 = temp[1].split(':')
        messageTimeStr = temp2[0]
        hour = int(messageTimeStr)
        messageNum[hour] += 1

    #==========================================
    #show
    plt.plot(range(24), messageNum)
    plt.title('sentimentIndex of half an hour')
    # plt.subplot(211)
    # plt.plot(range(len(sentimentIndex)), sentimentIndex)
    # plt.title('sentimentIndex of half an hour')
    # plt.subplot(212)
    # plt.plot(range(len(messageNum)), messageNum)
    # plt.title('message num in half an hour')
    plt.show()

    a = 1

