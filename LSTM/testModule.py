import csv
import pandas as pd #导入Pandas
import random
import numpy as np
import datetime
import logging
import sys
import os

from keras.preprocessing import sequence
from keras.optimizers import SGD, RMSprop, Adagrad
# from keras.utils import np_utils
import np_utils
from keras.models import Sequential
from keras.models import load_model
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM, GRU


# def score(words, allWordDict, noUse):
#     mes = []
#     for eachWord in words:
#         try:
#             wordIndex = allWordDict['id'][eachWord]
#         except:
#             wordIndex = 0
#         if wordIndex > 0:
#             mes.append(wordIndex)
#     return mes

def score(words, allWordDict, noUse):
    markers = ['$btc.x', '.', 'the', 'to', 'is', 'a', 'thi', 'it', 'are']
    mes = []
    for eachWord in words:
        bStopWord = False
        for marker in markers:
            if eachWord == marker:
                bStopWord = True
                break
        if bStopWord:
            continue
        try:
            wordFrequence = allWordDict[0][eachWord]
        except:
            wordFrequence = 0
        if wordFrequence < 5:
            continue
        try:
            wordIndex = allWordDict['id'][eachWord]
        except:
            wordIndex = 0
        if wordIndex > 0:
            mes.append(wordIndex)
    return mes


def mySplit(mes):
    temp = mes.split(' ')
    rmes = []
    for word in temp:
        if word != '':
            rmes.append(word)
    return rmes


if __name__ == '__main__':
    dictPath = '../../Data/BigData'
    dictDataPath = dictPath + '/MarkedMessage_MoreMark.csv'
    dictFilePath = dictPath + '/MarkedMessageDict_MoreMark.csv'
    testDataPath = '../../Data/MarkedTestMessage_MoreMark.csv'
    inputPath = '../../Data/Output/LSTM2_adam_BigData_mask_zero=True_Porter_MoreMark_SW'
    outputPath = inputPath + '/Test'
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
    trainMesNum = int(lineNum * 0.75)
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
    # b========================
    # save dict
    if not os.path.exists(dictFilePath):
        for word in allWordDict.index:
            line = []
            line.append(word)
            line.append(allWordDict[0][word])
            line.append(allWordDict['id'][word])
            try:
                bullNum = bullDict[0][word]
            except:
                bullNum = 0
            try:
                bearNum = bearDict[0][word]
            except:
                bearNum = 0
            line.append(bullNum)
            line.append(bearNum)
            with open(dictFilePath, 'a', newline='', encoding='utf-8') as fwrite:
                writer = csv.writer(fwrite)
                writer.writerow(line)
    # e========================
    # train==========================================================================
    model = load_model(inputPath + './LSTM2.h5')
    # test ==========================================================================
    testMarks = []
    testMes = []
    lineNum = 0
    bullLineNum = 0
    bearLineNum = 0
    with open(testDataPath, 'r', newline='', encoding='utf-8') as f:
        lines = csv.reader(f)
        for line in lines:
            lineNum += 1
            testMes.append(line[3])
            if line[2] == '1':
                bullLineNum += 1
                testMarks.append(1)
            elif line[2] == '-1':
                bearLineNum += 1
                testMarks.append(0)
            else:
                raise Exception('wrong mark ' + line[2])
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
    nullNum = 0
    deleteIndex = []
    for i in range(lineNum):
        if testData['message'][i] == [] or testData['message'][i] == [1]:
            nullNum += 1
            deleteIndex.append(i)
            if testData['mark'][i] == 1:
                bullLineNum -= 1
            else:
                bearLineNum -= 1
    testData.drop(deleteIndex, inplace=True)
    # nullNum = testData['message'].isnull().value_counts
    # testData.dropna(axis=0, how='any')
    lineNum = lineNum - nullNum
    if lineNum != len(testData) or lineNum != (bullLineNum + bearLineNum):
        raise Exception('lineNum error after delete')
    logger.info('after delete, lineNum =' + str(lineNum) + ', bullLineNum=' + str(bullLineNum) + ', bearLineNum=' + str(bearLineNum))
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
    results = model.predict_classes(xt, batch_size=16)
    rightNum = 0
    allNum = 0
    for i in range(len(results)):
        if results[i] == yt[i]:
            rightNum += 1
            allNum += 1
        else:
            allNum += 1
    if lineNum != allNum:
        raise Exception('lineNum if defferent with allNum')
    logger.info('My test accuracy=' + str(rightNum/allNum))
    logger.info('My test can not predict=' + str(nullNum / (nullNum + allNum)))
    # 保存
    testMesDF.drop(deleteIndex, inplace=True)
    if os.path.exists(outputPath + '/result.csv'):
        os.remove(outputPath + '/result.csv')
    for i in range(len(results)):
        try:
            line = []
            line.append(str(yt[i]))
            line.append(str(results[i]))
            if results[i] == yt[i]:
                line.append('R')
            else:
                line.append('F')
            line.append(testData['message'][i])
            line.append(testMesDF['message'][i])
            with open(outputPath + '/result.csv', 'a', newline='', encoding='utf-8') as fwrite:
                writer = csv.writer(fwrite)
                writer.writerow(line)
        except:
            print('i=' + str(i) + 'is wrong line')

    a = 1
