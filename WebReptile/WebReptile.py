#!/usr/bin/python
import json
import urllib.request
import time
import datetime
import csv
import os


def readUrl(url):
    response = urllib.request.urlopen(url)
    # check head
    if response.code != 200:
        raise Exception("url read error, code = " + str(response.code))
    header = response.getheaders()
    remainNum = header[16][1]
    if int(remainNum) < 2:
        raise Exception("url read limit, remainNum = " + str(remainNum))
    # html = response.read()
    temp = json.loads(response.read())
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
    print("len(info) = " + str(len(info)) + ", len(message) = " + str(len(message)))
    if len(info) != len(message):
        raise Exception("data dismatch  error, len(info) = " + str(len(info)) + ", len(message) = " + str(len(message)))
    bOK = 1
    return bOK, message, info, int(remainNum)

def saveDataBySince(maxID, messageFolder):

    maxReadNum = 5000
    readNum = 0
    while (readNum < maxReadNum and maxID > 0):
        remainNum = 200
        #print('readNum=', readNum, ', maxID=', maxID, 'time=', str(datetime.datetime.now()))
        print('next time:', str(datetime.datetime.now() + datetime.timedelta(hours=1))[0:19])
        timeArray = time.strptime(str(datetime.datetime.now() + datetime.timedelta(hours=1))[0:19],
                              "%Y-%m-%d %H:%M:%S")
        startTime = int(time.mktime(timeArray))
        while (remainNum >10 and readNum < maxReadNum and maxID > 0):
            print('readNum=', readNum, ', maxID=', maxID, ', remainNum=', remainNum, 'time=', str(datetime.datetime.now()))
            url = 'https://api.stocktwits.com/api/2/streams/symbol/BTC.X.json?max=' + str(maxID)

            bOK, message, info, remainNum = readUrl(url)
            if not bOK:
                raise Exception("readUrl error, url = " + url)
            readNum = readNum + 1
            maxID = info[-1]['id'] - 1
            messageList = []
            infoList = []
            for mes in message:
                messageList.append([mes['id'], mes['created_at'], mes['sentiment'], mes['body']])
            for inf in info:
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
            with open(messageFolder + '/OriginMessage.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in messageList:
                    writer.writerow(row)
            with open(messageFolder + '/OriginMessageInfo.csv', 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for row in infoList:
                    writer.writerow(row)
        if readNum < maxReadNum and maxID > 0:
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
    maxID = 97867473 # not include
    messageFolder = '../../Data'
    if not os.path.exists(messageFolder):
        os.makedirs(messageFolder)
    saveDataBySince(maxID, messageFolder)
    

