#!/usr/bin/python
import json
import urllib.request
import time
import datetime
import csv
import os


def determineDatelimit(messageTime, direction, endDate):
    # endTime = "2018-10-21T00:00:00Z"
    endTime = time.strptime(endDate, "%Y-%m-%dT%H:%M:%SZ")
    endTime = time.mktime(endTime)

    messageTime = time.strptime(messageTime, "%Y-%m-%dT%H:%M:%SZ")
    messageTime = time.mktime(messageTime)
    if direction > 0:
        if messageTime > endTime:
            return True
    else:
        if messageTime < endTime:
            return True
    return False


def readUrl(url):
    #b=========================================
    # print('read begin')
    # proxy_support = urllib.request.ProxyHandler({'https':'113.200.56.13:8010'})
    # opener = urllib.request.build_opener(proxy_support)
    # opener.addheaders = [('User-Agent',
    #                       'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36')]
    # urllib.request.install_opener(opener)
    # response = urllib.request.urlopen(urlTest)
    # b===============
    # # test
    # urlTest = 'https://www.baidu.com'
    # urlTest = 'https://whatismyipaddress.com/'
    # response = opener.open(urlTest)
    # print(response.read())
    # response.close()
    # e===============
    # response = opener.open(url)
    # response = opener.open(url)
    # print('read end')
    #e=========================================

    # b=========================================
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36')]
    # urlTest = 'https://whatismyipaddress.com/'
    print(url)
    response = opener.open(url)
    # print(response.read())
    # e=========================================

    # b=========================================
    # response = urllib.request.urlopen(url)
    # e=========================================
    
    # check head
    if response.code != 200:
        raise Exception("url read error, code = " + str(response.code))
    header = response.getheaders()
    remainNum = header[16][1]
    if int(remainNum) < 2:
        raise Exception("url read limit, remainNum = " + str(remainNum))
    # html = response.read()
    temp = json.loads(response.read())
    response.close()
    print('messages num =', len(temp['messages']))
    info = []
    message = []
    for mes in temp['messages']:
        tempInfo = {'id': mes['id'],
                    'created_at': mes['created_at'],
                    'userID': mes['user']['id'],
                    'username': mes['user']['username'],
                    'join_date': mes['user']['join_date'],
                    'official': mes['user']['official'],
                    'identity': mes['user']['identity'],
                    'followers': mes['user']['followers'],
                    'following': mes['user']['following'],
                    'ideas': mes['user']['ideas'],
                    'watchlist_stocks_count': mes['user']['watchlist_stocks_count'],
                    'like_count': mes['user']['like_count'],
                    'symbolID': temp['symbol']['id'],
                    'symbol': temp['symbol']['symbol']}
        if mes['entities']['sentiment']:
            tempMes = {'id': mes['id'],
                       'created_at': mes['created_at'],
                       'sentiment': mes['entities']['sentiment']['basic'],
                       'body': mes['body']}
        else:
            tempMes = {'id': mes['id'],
                       'created_at': mes['created_at'],
                       'sentiment': '',
                       'body': mes['body']}
        info.append(tempInfo)
        message.append(tempMes)
    print("len(info) = " + str(len(info)) +
          ", len(message) = " + str(len(message)))
    if len(info) != len(message):
        raise Exception("data dismatch  error, len(info) = " +
                        str(len(info)) + ", len(message) = " + str(len(message)))
    bOK = 1
    return bOK, message, info, int(remainNum)


def saveDataByMax(maxID, messageFolder, messageFileName, endDate):

    maxReadNum = 3000
    readNum = 0
    while (readNum < maxReadNum and maxID > 0):
        remainNum = 200
        # print('readNum=', readNum, ', maxID=', maxID, 'time=', str(datetime.datetime.now()))
        print('next time:', str(datetime.datetime.now() +
                                datetime.timedelta(hours=1))[0:19])
        timeArray = time.strptime(str(datetime.datetime.now() + datetime.timedelta(hours=1))[0:19],
                                  "%Y-%m-%d %H:%M:%S")
        startTime = int(time.mktime(timeArray))
        bReadToEnd = False
        while (remainNum > 10 and readNum < maxReadNum and maxID > 0):
            print('readNum=', readNum, ', maxID=', maxID, ', remainNum=',
                  remainNum, 'time=', str(datetime.datetime.now()))
            url = 'https://api.stocktwits.com/api/2/streams/symbol/BTC.X.json?max=' + \
                str(maxID)

            bOK, message, info, remainNum = readUrl(url)
            if not bOK:
                raise Exception("readUrl error, url = " + url)

            readNum = readNum + 1

            time.sleep(10)

            maxID = info[-1]['id'] - 1
            messageList = []
            infoList = []
            mesNum = 0
            infoNum = 0
            for mes in message:
                direction = -1
                dataStopFlag = determineDatelimit(mes['created_at'], direction, endDate)
                if dataStopFlag:
                    print('date end:' + mes['created_at'])
                    bReadToEnd = True
                    break
                messageList.append(
                    [mes['id'], mes['created_at'], mes['sentiment'], mes['body']])
                mesNum += 1
            for inf in info:
                infoNum += 1
                if infoNum > mesNum:
                    break
                infoList.append([inf['id'],
                                 inf['userID'],
                                 inf['username'],
                                 inf['join_date'],
                                 inf['official'],
                                 inf['identity'],
                                 inf['followers'],
                                 inf['following'],
                                 inf['ideas'],
                                 inf['watchlist_stocks_count'],
                                 inf['like_count'],
                                 inf['symbolID'],
                                 inf['symbol']])
            # with open('../../Data/OriginMessage.csv', 'a', newline='', encoding='utf-8') as f:
            with open(messageFolder + messageFileName + '.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in messageList:
                    writer.writerow(row)
            with open(messageFolder + messageFileName + 'Info.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in infoList:
                    writer.writerow(row)
            if bReadToEnd:
                return
        if readNum < maxReadNum and maxID > 0:
            now = time.time()
            delay = startTime - now
            print('delay=', delay)
            time.sleep(delay + 1)


def saveDataBySince(minID, messageFolder, messageFileName, endDate):

    maxReadNum = 3000
    readNum = 0
    while (readNum < maxReadNum):
        remainNum = 200
        # print('readNum=', readNum, ', minID=', minID, 'time=', str(datetime.datetime.now()))
        print('next time:', str(datetime.datetime.now() +
                                datetime.timedelta(hours=1))[0:19])
        timeArray = time.strptime(str(datetime.datetime.now() + datetime.timedelta(hours=1))[0:19],
                                  "%Y-%m-%d %H:%M:%S")
        startTime = int(time.mktime(timeArray))
        bReadToEnd = False
        while (remainNum > 10 and readNum < maxReadNum):
            print('readNum=', readNum, ', minID=', minID, ', remainNum=',
                  remainNum, 'time=', str(datetime.datetime.now()))
            url = 'https://api.stocktwits.com/api/2/streams/symbol/BTC.X.json?since=' + \
                str(minID - 30 + 2)

            bOK, message, info, remainNum = readUrl(url)
            if not bOK:
                raise Exception("readUrl error, url = " + url)
            readNum = readNum + 1

            time.sleep(10)

            minID = info[0]['id'] - 1
            messageList = []
            infoList = []
            mesNum = 0
            mesIgnoreNum = 0
            infoNum = 0
            infoIgnoreNum = 0
            for mes in message:
                direction = 1
                dataStopFlag = determineDatelimit(mes['created_at'], direction, endDate)
                if dataStopFlag:
                    print('date end:' + mes['created_at'])
                    bReadToEnd = True
                    mesIgnoreNum += 1
                    continue
                messageList.append(
                    [mes['id'], mes['created_at'], mes['sentiment'], mes['body']])
                mesNum += 1
            for inf in info:
                if infoIgnoreNum < mesIgnoreNum:
                    infoIgnoreNum += 1
                    continue
                infoNum += 1
                infoList.append([inf['id'],
                                 inf['userID'],
                                 inf['username'],
                                 inf['join_date'],
                                 inf['official'],
                                 inf['identity'],
                                 inf['followers'],
                                 inf['following'],
                                 inf['ideas'],
                                 inf['watchlist_stocks_count'],
                                 inf['like_count'],
                                 inf['symbolID'],
                                 inf['symbol']])
            if infoNum != mesNum:
                raise Exception("infoNum dismatch mesNum")
            # with open('../../Data/OriginMessage.csv', 'a', newline='', encoding='utf-8') as f:
            with open(messageFolder + messageFileName + '.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # for i in range(len(messageList)):
                #     writer.writerow(messageList[len(messageList) - i])
                for row in reversed(messageList):
                    writer.writerow(row)
            with open(messageFolder + messageFileName + 'Info.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                # for i in range(len(infoList)):
                #     writer.writerow(infoList[len(infoList) - i])
                for row in reversed(infoList):
                    writer.writerow(row)
            if bReadToEnd:
                return
        if readNum < maxReadNum:
            now = time.time()
            delay = startTime - now
            print('delay=', delay)
            time.sleep(delay + 1)


if __name__ == '__main__':
    # maxID = 134398415
    # url = 'https://api.stocktwits.com/api/2/streams/symbol/BTC.X.json?since=' + str(maxID)
    # bOK, tempMessage, info, remainNum = readUrl(url)
    # if bOK:
    #     print(bOK)
    # else:
    #     print('false')
    endDate = "2018-11-30T00:00:00Z"
    bUseMax = False
    if bUseMax:
        maxID = 104358138  # not include
        messageFolder = '../../Data'
        messageFileName = '/OriginMessage'
        if not os.path.exists(messageFolder):
            os.makedirs(messageFolder)
        saveDataByMax(maxID, messageFolder, messageFileName, endDate)
    else:
        minID = 145997171
        messageFolder = '../../Data/TidyOriginalData'
        messageFileName = '/TidyOriginalMessage'
        if not os.path.exists(messageFolder):
            os.makedirs(messageFolder)
        saveDataBySince(minID, messageFolder, messageFileName, endDate)
