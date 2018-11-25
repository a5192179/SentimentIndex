import json
import urllib.request
import time
import datetime
import csv
import os
import logging
import numpy as np
import sys
from MyMail import send_mail


def checkLimit(secondHistoNum=15, hourHistoNum=8000):
    limHourUrl = 'https://min-api.cryptocompare.com/stats/rate/hour/limit'
    limSecondUrl = 'https://min-api.cryptocompare.com/stats/rate/second/limit'

    url = limSecondUrl
    response = urllib.request.urlopen(url)
    if response.code < 100:
        raise Exception(url + ", url read error, code = " + str(response.code))
    temp = json.loads(response.read())
    secondHistoNumLeft = temp['CallsLeft']['Histo']

    url = limHourUrl
    response = urllib.request.urlopen(url)
    if response.code < 100:
        raise Exception(url + ", url read error, code = " + str(response.code))
    temp = json.loads(response.read())
    hourHistoNumLeft = temp['CallsLeft']['Histo']
    return secondHistoNumLeft, hourHistoNumLeft


def readUrl(cycle, logger):
    # check limit
    # maxSecondHistoNum=15, maxHourHistoNum=8000
    # secondHistoNumLeft, hourHistoNumLeft = checkLimit()
    secondHistoNumLeft = 15
    hourHistoNumLeft = 6000
    if secondHistoNumLeft <= 1:
        raise Exception("url read limit, secondHistoNum = " +
                        str(secondHistoNumLeft))
    if hourHistoNumLeft <= 1:
        raise Exception("url read limit, hourHistoNumLeft = " +
                        str(hourHistoNumLeft))
    log = 'secondHistoNumLeft:' + \
        str(secondHistoNumLeft) + ', hourHistoNumLeft:' + str(hourHistoNumLeft)
    logger.info(log)
    # read data
    if cycle == 'minute':
        url = 'https://min-api.cryptocompare.com/data/histominute?fsym=BTC&tsym=USD&limit=2000&aggregate=1&e=CCCAGG'
    elif cycle == 'hour':
        url = 'https://min-api.cryptocompare.com/data/histohour?fsym=BTC&tsym=USD&limit=2000&aggregate=1&e=CCCAGG'
    else:
        raise Exception("Wrong cycle:" + cycle)

    response = urllib.request.urlopen(url)
    if response.code < 100:
        raise Exception("url read error, code = " + str(response.code))
    temp = json.loads(response.read())
    if temp['Response'] != 'Success':
        raise Exception("url read error, Response = " + temp['Response'])
    log = 'messages num =' + str(len(temp['Data']))
    logger.info(log)

    Data = []
    for data in temp['Data']:
        Data.append([data['time'],
                     data['close'],
                     data['high'],
                     data['low'],
                     data['open'],
                     data['volumefrom'],
                     data['volumeto']])

    return Data


def saveData(data, priceFile):
    if not os.path.exists(priceFile):
        lastTime = []
    else:
        with open(priceFile, 'r', newline='', encoding='utf-8') as f:
            lines = csv.reader(f)
            for line in lines:
                lastTime = line[0]

    lastDataIndex = 0
    if lastTime != []:
        lastTime = int(lastTime)
        for line in data:
            if line[0] != lastTime:
                lastDataIndex += 1
            else:
                break
        if lastDataIndex == len(data):
            lastDataIndex = -1
            print("data broken")

    with open(priceFile, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in range(lastDataIndex + 1, len(data)):
            writer.writerow(data[i])


if __name__ == '__main__':
    logger = logging.getLogger("AppName")
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.formatter = formatter
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    logger.info('Begin')

    cycle = 'minute'
    # cycle = 'hour'

    priceFolder = '../../Data/Coin/'
    if not os.path.exists(priceFolder):
        os.makedirs(priceFolder)
    if cycle == 'minute':
        priceFileName = '/minutePrice.csv'
        timeDelta = 10  # hour
    else:
        priceFileName = '/hourPrice.csv'
        timeDelta = 600  # hour

    maxReadNum = 30000
    readNum = 0

    priceFile = priceFolder + priceFileName
    try:
        while (readNum < maxReadNum):
            # print('readNum=', readNum, ', minID=', minID, 'time=', str(datetime.datetime.now()))
            logger.info('next time:'+str(datetime.datetime.now() +
                                         datetime.timedelta(hours=timeDelta))[0:19])
            timeArray = time.strptime(str(datetime.datetime.now() + datetime.timedelta(hours=timeDelta))[0:19],
                                      "%Y-%m-%d %H:%M:%S")
            startTime = int(time.mktime(timeArray))

            data = readUrl(cycle, logger)
            data.pop()  # the last one has empty volumefrom

            saveData(data, priceFile)
            logger.info('save data end.')
            if readNum < maxReadNum:
                now = time.time()
                delay = startTime - now
                print('delay=', delay)
                time.sleep(delay + 1)

            readNum += 1
    except:
        mailto_list = ['13568827344@139.com']
        subject = 'Notice!!!'
        content = 'Coin data error!'
        print(content)
        if send_mail(mailto_list, subject, content):
            print("Notice mail successfully send.")
        else:
            print("Notice mail failed.")
        
