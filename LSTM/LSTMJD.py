import csv
import pandas as pd #导入Pandas
import random
import numpy as np
import datetime
import logging
import sys
import os
import shutil

from keras.preprocessing import sequence
from keras.optimizers import SGD, RMSprop, Adagrad
# from keras.utils import np_utils
import np_utils
from keras.models import Sequential
from keras.models import load_model
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM, GRU
import jieba #导入结巴分词

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
    # markers = ['$btc.x', '.', 'the', 'to', 'is', 'a', 'thi', 'it', 'are']
    markers = []
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
    outputPath = '../../Data/Output/JD/LSTMTest'
    dictFolderPath = outputPath + '/Dict'
    dictFilePath = dictFolderPath + '/dict_train.csv'

    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    else:
        shutil.rmtree(outputPath)
        os.makedirs(outputPath)

    if not os.path.exists(dictFolderPath):
        os.makedirs(dictFolderPath)

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

    neg = pd.read_excel('../../Data/neg.xls', header=None, index=None)
    pos = pd.read_excel('../../Data/pos.xls', header=None, index=None)  # 读取训练语料完毕
    pos['mark'] = 1
    neg['mark'] = 0  # 给训练语料贴上标签
    pn = pd.concat([pos, neg], ignore_index=True)  # 合并语料
    neglen = len(neg)
    poslen = len(pos)  # 计算语料数目

    cw = lambda x: list(jieba.cut(x))  # 定义分词函数
    pn['words'] = pn[0].apply(cw)

    comment = pd.read_excel('../../Data/sum.xls')  # 读入评论内容
    # comment = pd.read_csv('a.csv', encoding='utf-8')
    comment = comment[comment['rateContent'].notnull()]  # 仅读取非空评论
    comment['words'] = comment['rateContent'].apply(cw)  # 评论分词

    d2v_train = pd.concat([pn['words'], comment['words']], ignore_index=True)

    w = []  # 将所有词语整合在一起
    for i in d2v_train:
        w.extend(i)

    dict = pd.DataFrame(pd.Series(w).value_counts())  # 统计词的出现次数
    del w, d2v_train
    dict['id'] = list(range(1, len(dict) + 1))

    # b========================
    # save dict

    if not os.path.exists(outputPath):
        os.makedirs(outputPath)
    if not os.path.exists(dictFilePath):
        for word in dict.index:
            line = []
            line.append(word)
            line.append(dict[0][word])
            line.append(dict['id'][word])
            # try:
            #     bullNum = bullDict[0][word]
            # except:
            #     bullNum = 0
            # try:
            #     bearNum = bearDict[0][word]
            # except:
            #     bearNum = 0
            # line.append(bullNum)
            # line.append(bearNum)
            with open(dictFilePath, 'a', newline='', encoding='utf-8') as fwrite:
                writer = csv.writer(fwrite)
                writer.writerow(line)
    # e========================

    get_sent = lambda x: list(dict['id'][x])
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' score begin')
    pn['sent'] = pn['words'].apply(get_sent)  # 速度太慢
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' score end')
    maxlen = 50

    print("Pad sequences (samples x time)")
    pn['sent'] = list(sequence.pad_sequences(pn['sent'], maxlen=maxlen))

    x = np.array(list(pn['sent']))[::2]  # 训练集
    y = np.array(list(pn['mark']))[::2]
    xt = np.array(list(pn['sent']))[1::2]  # 测试集
    yt = np.array(list(pn['mark']))[1::2]
    xa = np.array(list(pn['sent']))  # 全集
    ya = np.array(list(pn['mark']))

    # train==========================================================================
    print('Build model...')
    model = Sequential()
    model.add(Embedding(len(dict) + 1, 256, input_length=maxlen, mask_zero=True))
    model.add(LSTM(activation='sigmoid', units=128, recurrent_activation='hard_sigmoid'))
    model.add(Dropout(0.5))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy'])
    # model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")#rmsprop

    model.fit(x, y, batch_size=16, epochs=10, shuffle=True)  # 训练时间为若干个小时
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' train end')
    logger.info('train end')
    model.save(outputPath + '/LSTM2.h5')
    # model = load_model(outputPath + '/LSTM2.h5')
    # test ==========================================================================
    # testMesDF = pd.DataFrame(testMes, columns=['message'])
    # testMesDF['split'] = testMesDF['message'].apply(mySplit)
    # testData = pd.DataFrame(testMarks, columns=['mark'])
    # now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # print(now, ' test score begin')
    # testData['message'] = testMesDF['split'].apply(score, args=(dict, 1))
    # now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # print(now, ' test score end')
    # testData['message'] = list(sequence.pad_sequences(testData['message'], maxlen=maxlen))
    # xt = np.array(list(testData['message']))  # 训练集
    # yt = np.array(list(testData['mark']))

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
