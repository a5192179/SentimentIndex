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
import csv
import pandas

class myLSTM:

    def __init__(self, netPath, dictPath):
        self.netPath = netPath
        self.dict = self.setDict(dictPath)


    def setDict(self, dictPath):
        for
        allWordDict = pd.DataFrame(pd.Series(allWord).value_counts())
        allWordDict['id'] = list(range(1, len(allWordDict) + 1))
        logger.info('dictNum=' + str(len(allWordDict)))

    def score(self, words, allWordDict, noUse):
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

    def mySplit(self, mes):
        temp = mes.split(' ')
        rmes = []
        for word in temp:
            if word != '':
                rmes.append(word)
        return rmes

    def computeScore(self, mes):



