import csv
import pandas as pd #导入Pandas
import random
import numpy as np
import datetime
import logging
import sys
import os
import time


import matplotlib.pyplot as plt
currentPath = os.getcwd() # 返回当前工作目录
toolsPath = currentPath + '/../Tools'
sys.path.append(toolsPath) # 添加自己指定的搜索路径
from mathCommon import myMean


if __name__ == '__main__':
    dictPath = '../../Data/LSTM/2018120801/Input'
    dictDataPath = dictPath + '/MarkedMessage.csv'

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' all begin')
    bullLineNum = 0
    bearLineNum = 0
    bearWordNum = 0
    lineNum = 0
    markAll = []
    messageAll = []

    results = []
    allMesTime = []
    yt = []
    with open(dictDataPath, 'r', newline='', encoding='utf-8') as f:
        lines = csv.reader(f)
        for line in lines:
            if line[2] == '-1':
                results.append(0)
                yt.append(0)
            else:
                results.append(1)
                yt.append(1)
            allMesTime.append(line[1])

    beginTime = "2018-10-06T00:00:00Z"
    beginTime = time.strptime(beginTime, "%Y-%m-%dT%H:%M:%SZ")
    beginTime = time.mktime(beginTime)
    endTime = "2018-11-20T00:00:00Z"
    endTime = time.strptime(endTime, "%Y-%m-%dT%H:%M:%SZ")
    endTime = time.mktime(endTime)
    # date_str = "2016-11-30T13:00:00Z"
    # a = time.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    # a = time.mktime(a)
    sentimentIndex = []
    messageNum = []
    rightNum = []
    rightRate = []
    tempResult = []
    tempNum = 0
    tempRightNum = 0
    tempTagNum = 0
    if len(allMesTime) != len(results):
        raise Exception('len(allMesTime) != len(results)')
    for i in range(len(results)):
        messageTime = allMesTime[i]
        messageTime = time.strptime(messageTime, "%Y-%m-%dT%H:%M:%SZ")
        messageTime = time.mktime(messageTime)
        if messageTime < beginTime:
            continue
        if messageTime >= endTime:
            break
        elif beginTime <= messageTime < beginTime + 1800: # and messageTime < :
            tempResult.append(results[i])
            tempNum += 1
            if yt[i] == 1 or yt[i] == 0:
                tempTagNum += 1
            if (results[i] > 0.5 and yt[i] == 1) or (results[i] < 0.5 and yt[i] == 0):
                tempRightNum += 1
        else:
            #calculate
            sentimentIndex.append(myMean(tempResult))
            messageNum.append(tempNum)
            rightNum.append(tempRightNum)
            if tempTagNum > 0:
                rightRate.append(tempRightNum/tempTagNum)
            else:
                rightRate.append(0)
            #update
            beginTime += 1800
            tempResult = []
            tempNum = 0
            tempRightNum = 0
            tempTagNum = 0

    #==========================================
    #show
    plt.subplot(211)
    plt.plot(range(len(sentimentIndex)), sentimentIndex)
    plt.title('sentimentIndex of half an hour')
    plt.subplot(212)
    plt.plot(range(len(messageNum)), messageNum)
    plt.title('message num in half an hour')
    plt.show()

    a = 1

