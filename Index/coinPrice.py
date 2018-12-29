# **************************************************************************
# *【Creat time】：2018-12-01 15:14          【Version】：0.0
# *【Writer】：LiShuai 461837929@qq.com
# *【Writer department】：
# *【Function】：
# * coinPrice 相关的函数
# * 输入：
# * 起始时间
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
import csv
import matplotlib.pyplot as plt
import time

class coinPrice:
    cointPrice = []

    def __init__(self, pricePath):
        self.pricePath = pricePath

    def readPriceData(self, pricePath):
        allPrice = []
        with open(pricePath, 'r', newline='', encoding='utf-8') as f:
            lines = csv.reader(f)
            for line in lines:
                temp = [int(line[0]), float(line[1]), float(line[2]), float(line[3]), float(line[4]), float(line[5]), float(line[6])]
                allPrice.append(temp)  # time  close high low open volumefrom volumeto
        return allPrice

    def cutPrice(self, beginTime, endTime, allPrice):
        cutedPrice = []
        for line in allPrice:
            if line[0] < beginTime:
                continue
            if line[0] >= endTime:
                break
            cutedPrice.append(line)
        return cutedPrice

    def convertPeriod(self, dataPeriod, cutedPrice):
        if len(cutedPrice) < 2:
            raise Exception('cuted price data num is less than 2')
        dataPeriodOld = cutedPrice[1][0] - cutedPrice[0][0]
        if dataPeriod % dataPeriodOld != 0:
            raise Exception('period dismatch, old:' + str(dataPeriodOld) + ', new:' + str(dataPeriodOld))
        numEach = dataPeriod/dataPeriodOld
        if len(cutedPrice) % numEach != 0:
            raise Exception('cutedPrice lens dismatch, len:' + str(len(cutedPrice)) + ', numEach:' + str(numEach))
        price = []
        conter = 0
        for eachPrice in cutedPrice:
            conter += 1
            if conter == 1:
                open = eachPrice[4]
                high = eachPrice[2]
                low = eachPrice[3]
                volumefrom = eachPrice[5]
                volumeto = eachPrice[5]
                continue
            if high < eachPrice[2]:
                high = eachPrice[2]
            if low > eachPrice[3]:
                low = eachPrice[3]
            if conter == numEach:
                close = eachPrice[1]
                time = eachPrice[0]
                price.append([time, close, high, low, open, volumefrom, volumeto])  # time close high low open volumefrom volumeto
                conter = 0
        return price


    def setCoinPrice(self, beginTime, endTime, dataPeriod):
        self.beginTime = beginTime
        self.endTime = endTime
        if self.cointPrice != []:
            print('coinPrice has been set')
        allPrice = self.readPriceData(self.pricePath)
        cutedPrice = self.cutPrice(beginTime, endTime, allPrice)
        self.Price = self.convertPeriod(dataPeriod, cutedPrice)

    def showPrice(self):
        close = []
        for tempPrice in self.Price:
            close.append(tempPrice[1])
        plt.figure(1)
        plt.plot(range(len(self.Price)), close)
        plt.title('price of half an hour')
        plt.grid(True)
        plt.show()
        a=1

if __name__ == '__main__':
    pricePath = '../../Data/Coin/Cleaned/cleanedMinutePrice.csv'
    cCoinPrice = coinPrice(pricePath)
    beginTime = "2018-10-06T00:00:00Z"
    beginTime = time.strptime(beginTime, "%Y-%m-%dT%H:%M:%SZ")
    beginTime = time.mktime(beginTime)
    endTime = "2018-11-20T00:00:00Z"
    endTime = time.strptime(endTime, "%Y-%m-%dT%H:%M:%SZ")
    endTime = time.mktime(endTime)
    dataPeriod = 1800
    cCoinPrice.setCoinPrice(beginTime, endTime, dataPeriod)
    cCoinPrice.showPrice()
