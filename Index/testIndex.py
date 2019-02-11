import csv
import pandas as pd #导入Pandas
import random
import numpy as np
import datetime
import logging
import sys
import os
import time

from keras.preprocessing import sequence
from keras.models import load_model

import matplotlib.pyplot as plt

o_path = os.getcwd() # 返回当前工作目录
o_path += '/../LSTM'
sys.path.append(o_path) # 添加自己指定的搜索路径
from LSTM2 import score
from LSTM2 import mySplit


def myMean(listA):
    if listA == []:
        return 0
    temp = 0
    for i in listA:
        temp += i
    return temp/len(listA)


if __name__ == '__main__':
    dictPath = '../../Data/BigData2'
    dictDataPath = dictPath + '/MarkedMessage.csv'
    dictFilePath = dictPath + '/MarkedMessageDict.csv'
    testDataPath = '../../Data/AfterTrainDataDate/CleanedMessage.csv'
    inputPath = '../../Data/Output/LSTM2_adam_BigData2_mask_zero=True_Porter_MoreMark_NoSW_VALOn_Epoch5'
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
    bullLineNum = 0
    bearLineNum = 0
    bearWordNum = 0
    lineNum = 0
    markAll = []
    messageAll = []

    with open(dictDataPath, 'r', newline='', encoding='utf-8') as f:
        lines = csv.reader(f)
        for line in lines:
            lineNum += 1
            messageAll.append(line[3])
            if line[2] == '1':
                bullLineNum += 1
                markAll.append(1)
            elif line[2] == '-1':
                bearLineNum += 1
                markAll.append(0)
            else:
                raise Exception('wrong mark ' + line[2])
            if lineNum % 10000 == 0:
                print('lineNum =', lineNum, ', bullLineNum=', bullLineNum, ', bearLineNum=', bearLineNum)

    index = list(range(lineNum))
    # random.shuffle(index)
    trainMesNum = int(lineNum * 0.9)
    trainIndex = index[0: trainMesNum]
    testMesNum = lineNum - trainMesNum
    testIndex = index[trainMesNum: lineNum]
    logger.info('trainMesNum=' + str(trainMesNum) + ', testMesNum=' + str(testMesNum))

    trainMes = np.array(messageAll)[trainIndex]
    trainMarks = np.array(markAll)[trainIndex]
    testMes = np.array(messageAll)[testIndex]
    testMarks = np.array(markAll)[testIndex]

    trainMes = trainMes.tolist()
    trainMarks = trainMarks.tolist()
    testMes = testMes.tolist()
    testMarks = testMarks.tolist()

    # prepare train data
    bullWord = []
    bullWordNum = 0
    bearWord = []
    bearWordNum = 0
    lineNum_train = 0
    allWord = []
    allWordNum = 0
    for line in trainMes:
        lineNum_train += 1
        message = mySplit(line)
        for word in message:
            if word == '':
                continue
            allWord.append(word)
            allWordNum += 1
            if trainMarks[lineNum_train - 1] == 1:
                bullWord.append(word)
                bullWordNum += 1
            elif trainMarks[lineNum_train - 1] == 0:
                bearWord.append(word)
                bearWordNum += 1
            else:
                raise Exception('wrong mark ' + trainMarks[lineNum_train - 1])
        if lineNum_train % 10000 == 0:
            print('lineNum_train =', lineNum_train, ', bullWordNum=', bullWordNum, ', bearWordNum=', bearWordNum)
    logger.info('bullWordNum=' + str(bullWordNum) + ', bearWordNum=' + str(bearWordNum))
    lineNum_test = 0
    for line in testMes:
        lineNum_test += 1
        message = mySplit(line)
        for word in message:
            if word == '':
                continue
            allWord.append(word)
            allWordNum += 1
        if lineNum_test % 10000 == 0:
            print('lineNum_test =', lineNum_test, ', allWordNum=', allWordNum)
    logger.info('allWordNum=' + str(allWordNum))
    # =====================================================================
    # adjust test message
    # testBull = 0
    # testBear = 0
    # deleteIndex = []
    # for i in range(len(testMes)):
    #     if testMarks[i] == 1:
    #         if testBear < testBull:
    #             deleteIndex.append(i)
    #         else:
    #             testBull += 1
    #     elif testMarks[i] == 0:
    #         testBear += 1
    #     else:
    #         raise Exception('wrong mark ' + testMarks[i])
    # np.delete(testMes, deleteIndex)
    # np.delete(testMarks, deleteIndex)
    #
    # logger.info('testBull=' + str(testBull) + ', testBear=' + str(testBear))
    # =====================================================================
    wordNum = bullWordNum + bearWordNum
    bullDict = pd.DataFrame(pd.Series(bullWord).value_counts()) #统计词的出现次数
    bearDict = pd.DataFrame(pd.Series(bearWord).value_counts()) #统计词的出现次数
    allWordDict = pd.DataFrame(pd.Series(allWord).value_counts())
    allWordDict['id'] = list(range(1, len(allWordDict) + 1))
    logger.info('dictNum=' + str(len(allWordDict)))
    # train==========================================================================
    model = load_model(inputPath + './LSTM2.h5')
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

    testMesDF = pd.DataFrame(testMes, columns=['message'])
    # cw = lambda x: x.split(' ')
    testMesDF['split'] = testMesDF['message'].apply(mySplit)
    testData = pd.DataFrame(testMarks, columns=['mark'])
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' test score begin')
    testData['message'] = testMesDF['split'].apply(score, args=(allWordDict, 1))#allWordDict
    # b====================================================
    # delete empty line
    # nullNum = 0
    # deleteIndex = []
    # for i in range(lineNum):
    #     if testData['message'][i] == [] or testData['message'][i] == [1]:
    #         nullNum += 1
    #         deleteIndex.append(i)
    #         if testData['mark'][i] == 1:
    #             bullLineNum -= 1
    #         else:
    #             bearLineNum -= 1
    # testData.drop(deleteIndex, inplace=True)
    # # nullNum = testData['message'].isnull().value_counts
    # # testData.dropna(axis=0, how='any')
    # lineNum = lineNum - nullNum
    # if lineNum != len(testData) or lineNum != (bullLineNum + bearLineNum):
    #     raise Exception('lineNum error after delete')
    # logger.info('after delete, lineNum =' + str(lineNum) + ', bullLineNum=' + str(bullLineNum) + ', bearLineNum=' + str(bearLineNum))
    # e====================================================
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' test score end')
    maxlen = 30
    testData['message'] = list(sequence.pad_sequences(testData['message'], maxlen=maxlen))
    xt = np.array(list(testData['message']))  # 训练集
    yt = np.array(list(testData['mark']))

    score = model.evaluate(xt, yt, batch_size=16)
    print('Test score:', score)
    logger.info('Test score=' + str(score))

    # loss, accuracy = model.evaluate(xt, yt)
    # print('\ntest loss', loss)
    # print('accuracy', accuracy)
    # logger.info('test end')
    # logger.info('accuracy=' + str(accuracy) + ', loss=' + str(loss))

    # my test ========================================================================
    results = model.predict(xt, batch_size=16)
    beginTime = "2018-01-11T00:00:00Z"
    beginTime = time.strptime(beginTime, "%Y-%m-%dT%H:%M:%SZ")
    beginTime = time.mktime(beginTime)
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
    if len(testTime) != len(results):
        raise Exception('len(testTime) != len(results)')
    for i in range(len(results)):
        messageTime = testTime[i]
        messageTime = time.strptime(messageTime, "%Y-%m-%dT%H:%M:%SZ")
        messageTime = time.mktime(messageTime)
        if messageTime < beginTime:
            continue
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

