# **************************************************************************
# *【Creat time】：2018-11-02 21:58          【Version】：0.0
# *【Writer】：LiShuai 461837929@qq.com
# *【Writer department】：
# *【Function】：
# * 根据指定时间的价格数据、情绪指数输出拟合的系数矩阵
# * 输入：
# * 起始时间
# * 结束时间
# * 时间间隔
# * 情绪文本路径
# * 网络参数
# * 价格文件路径
# * 参数保存路径
# * 输出：
# * 系数矩阵参数
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


import os
import sys

currentPath = os.getcwd() # 返回当前工作目录
toolsPath = currentPath + '/../Tools'
sys.path.append(toolsPath) # 添加自己指定的搜索路径
import convertTime
coinPricePath = currentPath
sys.path.append(coinPricePath) # 添加自己指定的搜索路径
from coinPrice import coinPrice
# from sentimentIndex import sentimentIndex
LSTMPath = currentPath + '/../LSTM'
sys.path.append(LSTMPath)
import LSTMClass
import sentimentScore as sentimentScor
import matplotlib.pyplot as plt


def generateParaMatrix(beginTime, endTime, coinDataPeriod, senDataPeriod, wordsPath, dictPath, modelPath, pricePath, paraOutPath):
    coinPriceIns = coinPrice(pricePath)
    coinPriceIns.setCoinPrice(beginTime, endTime, coinDataPeriod)  # time close high low open volumefrom 
    LSTMIns = LSTMClass.cLSTM(modelPath, dictPath)
    sentimentScoreIns = sentimentScor.sentimentScore()
    sentimentScoreIns.setSentimentScore(beginTime, endTime, senDataPeriod, LSTMIns, wordsPath)
    sentimentScore = sentimentScoreIns.getSentimentScore()
    sentimentTimes = sentimentScoreIns.getSentimentTime()
    messageNum = sentimentScoreIns.getMessageNum()
    senDataNum = len(sentimentScore)
    coinDataNum = len(coinPriceIns.Price)
    # ====================
    # check
    if senDataNum != coinDataNum:
        raise Exception('senDataNum is not equal to coinDataNum')
    for i in range(senDataNum):
        if sentimentTimes[i] != coinPriceIns.Price[i][0]:
            wrongSenTime = convertTime.timestamp_datetime(sentimentTimes[i])
            wrongCoinTime = convertTime.timestamp_datetime(coinPriceIns.Price[i][0])
            raise Exception(['SenTime time:' + wrongSenTime + ' is not equal to coin time:' + wrongCoinTime])
    # ====================
    price = []
    for temp in coinPriceIns.Price:
        price.append(temp[1])
    deltaSen = []
    deltaPrice = []
    for i in range(0, senDataNum - 1):
        deltaSen.append(sentimentScore[i + 1] - sentimentScore[i])
    for i in range(0, senDataNum - 1):
        deltaPrice.append(coinPriceIns.Price[i + 1][1] - coinPriceIns.Price[i][1])
    directSen = []
    directPrice = []
    directPredict = []
    rightFlag = []
    rightFlag.append(0)
    allPredictNum = 0
    rightNum = 0
    senGate = 0.1
    for i in range(senDataNum - 1):
        if deltaSen[i] > senGate:
            directSen.append(1)
            directPredict.append(1)
        elif deltaSen[i] < -senGate:
            directSen.append(-1)
            directPredict.append(-1)
        else:
            directSen.append(0)
            directPredict.append(0)
        if deltaPrice[i] > 0:
            directPrice.append(1)
        else:
            directPrice.append(-1)
        if i > 0:
            # if directPredict[i - 1] * directPrice[i] > 0:
            if directPredict[i] * directPrice[i] > 0:
                allPredictNum += 1
                rightFlag.append(0.5)
                rightNum += 1
            # elif directPredict[i - 1] * directPrice[i] < 0:
            elif directPredict[i] * directPrice[i] < 0:
                allPredictNum += 1
                rightFlag.append(-0.5)
            else:
                rightFlag.append(0)
        
    # if 1:
    #     print('begin figure')
    #     # plt.subplot(211)
    #     fig = plt.figure()
    #     ax1 = fig.add_subplot(111)
    #     ax1.plot(range(len(directSen)), directSen, 'rv', range(len(directSen)), rightFlag, 'g*')
    #     ax1.set_ylabel('sen')
    #     ax1.set_title('Predict num = ' + str(allPredictNum) + ', right rate:' + str(rightNum/allPredictNum))

    #     ax2 = ax1.twinx()  # this is the important function
    #     ax2.plot(range(len(directPrice)), directPrice, 'b^')
    #     # ax2.set_xlim([0, np.e])
    #     ax2.set_ylabel('coin')
    #     ax2.set_xlabel('sen is before, coin is after')
    #     print('mid figure')
    #     for i in range(0, len(deltaSen), 5):
    #         plt.axvline(i)

    #     print('before figure show')
    #     # plt.plot(range(len(deltaSen) - 1), deltaSen[0:len(deltaSen) - 1], 'r', range(len(deltaPrice) - 1), deltaPrice[1:len(deltaPrice)], 'b')
    #     # plt.title('sentiment of half an hour')
    #     # plt.subplot(212)
    #     # plt.plot(range(len(deltaPrice) - 1), deltaPrice[1:len(deltaPrice)])
    #     # plt.title('price of half an hour')
    #     plt.grid(True)
    #     plt.show()
    #     a=1
    if 1:
        print('begin figure')
        # plt.subplot(211)
        fig = plt.figure()
        ax1 = fig.add_subplot(211)
        ax1.plot(range(len(deltaSen) - 1), deltaSen[1:len(deltaSen)], 'r')
        ax1.set_ylabel('sen')
        ax1.set_title("Double Y axis")

        ax2 = ax1.twinx()  # this is the important function
        ax2.plot(range(len(deltaPrice) - 1), deltaPrice[0:len(deltaPrice) - 1], 'b', range(len(deltaPrice) - 1), messageNum[1:len(deltaPrice)], 'g')
        # ax2.set_xlim([0, np.e])
        ax2.set_ylabel('coin')
        ax2.set_xlabel('sen is before, coin is after')
        print('mid figure')
        for i in range(0, len(deltaSen) - 1, 5):
            plt.axvline(i)

        print('before figure show')
        # plt.plot(range(len(deltaSen) - 1), deltaSen[0:len(deltaSen) - 1], 'r', range(len(deltaPrice) - 1), deltaPrice[1:len(deltaPrice)], 'b')
        # plt.title('sentiment of half an hour')
        # plt.subplot(212)
        # plt.plot(range(len(deltaPrice) - 1), deltaPrice[1:len(deltaPrice)])
        # plt.title('price of half an hour')
        plt.grid(True)
        ax3 = fig.add_subplot(212)
        ax3.plot(range( len(price) ), sentimentScore[0:len(sentimentScore)], 'rv-')
        ax3.set_ylabel('sen')
        ax3.set_title("Double Y axis")

        ax4 = ax3.twinx()  # this is the important function
        ax4.plot(range( len(price) ), price, 'b^-')
        # ax2.set_xlim([0, np.e])
        ax4.set_ylabel('coin')
        ax4.set_xlabel('sen is before, coin is after')
        print('mid figure')
        for i in range(0, len(price), 5):
            plt.axvline(i)
        plt.grid(True)
        plt.show()
        a=1

    a=1

if __name__ == '__main__':
    strBeginTime = '2018-10-07T00:00:00'
    strEndTime = '2018-10-19T00:00:00'
    coinDataPeriod = 43200  # second, 1 day = 86400
    senDataPeriod = 43200  # second
    wordsPath = '../../Data/TidyOriginalData/CleanedMessage.csv'
    dictPath = '../../Data/TidyOriginalData/MarkedMessageDict.csv'
    modelPath = '../../Data/Output/LSTM2_adam_TidyOriginalData_mask_zero=True_Porter_NoSW_VALOn_Epoch4/LSTM2.h5'
    pricePath = '../../Data/Coin/Cleaned/cleanedMinutePrice.csv'
    paraOutPath = '../../Data/Output/Para/para.csv'

    beginTime = convertTime.datetime_timestamp(strBeginTime)
    endTime = convertTime.datetime_timestamp(strEndTime)

    generateParaMatrix(beginTime, endTime, coinDataPeriod, senDataPeriod, wordsPath, dictPath, modelPath, pricePath, paraOutPath)





