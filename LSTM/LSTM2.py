import csv
import pandas as pd #导入Pandas
import random
import numpy as np
import datetime
import logging
import sys
import os

np.random.seed(1234)
from keras.preprocessing import sequence
from keras.optimizers import SGD, RMSprop, Adagrad
# from keras.utils import np_utils
import np_utils
from keras.models import Sequential
from keras.models import load_model
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM, GRU
from keras.layers.normalization import BatchNormalization
from keras import regularizers
from keras.callbacks import EarlyStopping

# def score(words, bullDict, bearDict, wordNum):
#     mesScore = []
#     for word in words:
#         try:
#             bullNum = bullDict[0][word]
#         except:
#             bullNum = 0
#         if bullNum < 10:
#             bullNum = 0
#         try:
#             bearNum = bearDict[0][word]
#         except:
#             bearNum = 0
#         if bearNum < 10:
#             bearNum = 0
#         wordScore = (bullNum / 2 - bearNum) / wordNum * 1000
#         mesScore.append(wordScore)
#     return mesScore


def score(words, allWordDict, noUse):
    # markers = ['$btc.x']
    # markers = ['$btc.x', '.', 'the', 'to', 'is', 'a', 'thi', 'it', 'are']
    # markers = []
    mes = []
    index = 0
    for eachWord in words:
        index += 1
        bStopWord = False
        if index == 1 and eachWord == '$btc.x':
            bStopWord = True
        # for marker in markers:
        #     if eachWord == marker:
        #         bStopWord = True
        #         break
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
    wordFile = '../../Data/TidyOriginalData/MarkedMessage.csv'
    outputPath = '../../Data/Output/LSTM2_adam_TidyOriginalData_mask_zero=True_Porter_NoSW_VALOn_Epoch4'
    dictPath = '../../Data/TidyOriginalData'
    dictFilePath = dictPath + '/MarkedMessageDict.csv'
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

    with open(wordFile, 'r', newline='', encoding='utf-8') as f:
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
    dict = pd.DataFrame(pd.Series(allWord).value_counts())
    dict['id'] = list(range(1, len(dict) + 1))
    logger.info('dictNum=' + str(len(dict)))
    # b========================
    # save dict
    if not os.path.exists(dictFilePath):
        for word in dict.index:
            line = []
            line.append(word)
            line.append(dict[0][word])
            line.append(dict['id'][word])
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



    trainMesDF = pd.DataFrame(trainMes, columns=['message'])
    # cw = lambda x: x.split(' ')
    trainMesDF['split'] = trainMesDF['message'].apply(mySplit)
    trainData = pd.DataFrame(trainMarks, columns=['mark'])
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' score begin')
    # trainData['message'] = trainMesDF['split'].apply(score, args=(bullDict, bearDict, wordNum))
    # score2 = lambda xx: list(dict['id'][xx])
    trainData['message'] = trainMesDF['split'].apply(score, args=(dict, 1))
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' score end')
    logger.info('score end')
    maxlen = 30
    trainData['message'] = list(sequence.pad_sequences(trainData['message'], maxlen=maxlen))
    x = np.array(list(trainData['message']))  # 训练集
    y = np.array(list(trainData['mark']))

    # train==========================================================================
    print('Build model...')
    model = Sequential()
    model.add(Embedding(len(dict) + 1, 256, input_length=maxlen, mask_zero=True))
    model.add(LSTM(activation='sigmoid', units=128, recurrent_activation='hard_sigmoid', bias_regularizer=regularizers.l2(0.1)))
    # model.add(LSTM(activation='sigmoid', units=128, recurrent_activation='hard_sigmoid'))
    model.add(Dropout(0.5))
    # model.add(BatchNormalization())
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    # model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")#rmsprop
    early_stopping = EarlyStopping(monitor='val_loss', patience=0)
    # model.fit(x, y, batch_size=16, epochs=10, shuffle=True, validation_split=0.1, verbose=2, callbacks=[early_stopping])  # 训练时间为若干个小时
    model.fit(x, y, batch_size=16, epochs=5, shuffle=True, validation_split=0.1, verbose=2)  # 训练时间为若干个小时
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' train end')
    logger.info('train end')
    model.save(outputPath + '/LSTM2.h5')
    # model = load_model(outputPath + '/LSTM2.h5')
    # test ==========================================================================
    testMesDF = pd.DataFrame(testMes, columns=['message'])
    testMesDF['split'] = testMesDF['message'].apply(mySplit)
    testData = pd.DataFrame(testMarks, columns=['mark'])
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' test score begin')
    testData['message'] = testMesDF['split'].apply(score, args=(dict, 1))
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' test score end')
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
    logger.info('My test accuracy=' + str(rightNum/allNum))

    a = 1
