import csv
import pandas as pd #导入Pandas
import random
import numpy as np
import datetime


from keras.preprocessing import sequence
from keras.optimizers import SGD, RMSprop, Adagrad
# from keras.utils import np_utils
import np_utils
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.embeddings import Embedding
from keras.layers.recurrent import LSTM, GRU

def score(words, bullDict, bearDict, wordNum):
    mesScore = []
    for word in words:
        try:
            bullNum = bullDict[0][word]
        except:
            bullNum = 0
        if bullNum < 10:
            bullNum = 0
        try:
            bearNum = bearDict[0][word]
        except:
            bearNum = 0
        if bearNum < 10:
            bearNum = 0
        wordScore = (bullNum / 2 - bearNum) / wordNum * 1000
        mesScore.append(wordScore)
    return mesScore


if __name__ == '__main__':
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' all begin')
    bullLineNum = 0
    bearLineNum = 0
    bearWordNum = 0
    lineNum = 0
    markAll = []
    messageAll = []

    with open('../../Data/testMarkedMessage.csv', 'r', newline='', encoding='utf-8') as f:
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
    random.shuffle(index)
    trainMesNum = int(lineNum * 0.75)
    trainIndex = index[0: trainMesNum]
    testMesNum = lineNum - trainMesNum
    testIndex = index[trainMesNum: lineNum]

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
    for line in trainMes:
        lineNum_train += 1
        message = line.split(' ')
        for word in message:
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

    wordNum = bullWordNum + bearWordNum
    bullDict = pd.DataFrame(pd.Series(bullWord).value_counts()) #统计词的出现次数
    bearDict = pd.DataFrame(pd.Series(bearWord).value_counts()) #统计词的出现次数

    trainMesDF = pd.DataFrame(trainMes, columns=['message'])
    cw = lambda x: x.split(' ')
    trainMesDF['split'] = trainMesDF['message'].apply(cw)
    trainData = pd.DataFrame(trainMarks, columns=['mark'])
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' score begin')
    trainData['message'] = trainMesDF['split'].apply(score, args=(bullDict, bearDict, wordNum))
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' score end')

    maxlen = 30
    trainData['message'] = list(sequence.pad_sequences(trainData['message'], maxlen=maxlen, dtype='float32'))
    x = np.array(list(trainData['message']))  # 训练集
    y = np.array(list(trainData['mark']))

    # train==========================================================================
    print('Build model...')
    model = Sequential()
    # model.add(Embedding(len(bullDict) + len(bearDict) + 1, 256, input_length=maxlen))
    model.add(LSTM(activation='sigmoid', units=128, recurrent_activation='hard_sigmoid', input_shape=(x.shape[1], 1)))
    model.add(Dropout(0.5))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    model.compile(loss='binary_crossentropy',
                  optimizer='rmsprop',
                  metrics=['accuracy'])
    # model.compile(loss='binary_crossentropy', optimizer='adam', class_mode="binary")

    model.fit(x, y, batch_size=16, epochs=10)  # 训练时间为若干个小时
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' train end')
    model.save('LSTM1.h5')

    # test ==========================================================================
    testMesDF = pd.DataFrame(testMes, columns=['message'])
    testMesDF['split'] = testMesDF['message'].apply(cw)
    testData = pd.DataFrame(testMarks, columns=['mark'])
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' test score begin')
    testData['message'] = testMesDF['split'].apply(score, args=(bullDict, bearDict, wordNum))
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now, ' test score end')
    testData['message'] = list(sequence.pad_sequences(testData['message'], maxlen=maxlen))
    xt = np.array(list(testData['message']))  # 训练集
    yt = np.array(list(testData['mark']))

    score = model.evaluate(xt, yt, batch_size=16)
    print('Test score:', score)

    loss, accuracy = model.evaluate(xt, yt)
    print('\ntest loss', loss)
    print('accuracy', accuracy)
    a = 1