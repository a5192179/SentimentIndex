# **************************************************************************
# *【Creat time】：2018-12-04 22:41          【Version】：0.0
# *【Writer】：LiShuai 461837929@qq.com
# *【Writer department】：
# *【Function】：
# *
# * 输入：
# *
# *【Description】：
# *
# *
# *-------------------------------------------------------------------------
# *【Modification】：****-**-** **：**       【Version】：*.*
# *
# *【Writer】：LiShuai 461837929@qq.com
# *【Writer department】：
# *【Function】：
# *
# *
# *
# *【Description】：
# *
# *
# *
# **************************************************************************
import pandas as pd
import numpy as np
from keras.models import load_model
from keras.preprocessing import sequence
import datetime

import os
import sys
currentPath = os.getcwd() # 返回当前工作目录
LSTMPath = currentPath + '/../LSTM'
sys.path.append(LSTMPath) # 添加自己指定的搜索路径
from LSTM2 import score
from LSTM2 import mySplit


class cLSTM:

    def __init__(self, modelPath, dictPath):
        self.setDict(dictPath)
        self.setModel(modelPath)


    def setDict(self, dictPath):
        self.dict = pd.read_csv(dictPath, index_col=0, names=['count', 'id', 'bullNum', 'bearNum'])

    def setModel(self, modelPath):
        self.model = load_model(modelPath)

    def computeScore(self, mes):
        mesDF = pd.DataFrame(mes, columns=['message'])  # 用mes构造message列
        mesDF['split'] = mesDF['message'].apply(mySplit)  # 用message列和mySplit规则构造新的列
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(now, ' test score begin')
        mesScore = mesDF['split'].apply(score, args=(self.dict, 1))  # 这里变成pandas的series类型
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(now, ' test score end')
        maxlen = 30
        mesScoreCuted = list(sequence.pad_sequences(mesScore, maxlen=maxlen))
        xt = np.array(mesScoreCuted)
        results = self.model.predict(xt, batch_size=16)  # 0~1的list
        return results

