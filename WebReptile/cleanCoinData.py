import csv
import os
import time

def timestamp_datetime(value):
    format = '%Y-%m-%d %H:%M:%S'
    # value为传入的值为时间戳(整形)，如：1332888820
    value = time.localtime(value)
    ## 经过localtime转换后变成
    ## time.struct_time(tm_year=2012, tm_mon=3, tm_mday=28, tm_hour=6, tm_min=53, tm_sec=40, tm_wday=2, tm_yday=88, tm_isdst=0)
    # 最后再经过strftime函数转换为正常日期格式。
    dt = time.strftime(format, value)
    return dt


inputFile = '../../Data/Coin/minutePrice.csv'
outputFile = '../../Data/Coin/Cleaned/cleanedMinutePrice.csv'
if os.path.exists(outputFile):
    os.remove(outputFile)
lineNum = 0
with open(inputFile, 'r', newline='', encoding='utf-8') as f:
    lines = csv.reader(f)
    for line in lines:
        lineNum += 1
        if lineNum == 1:
            beginTime = int(line[0])
        if lineNum == 2:
            endTime = int(line[0])
    print('no error line')
    period = endTime - beginTime
    print('period = ', str(period))

lineNum = 0
times = []
lastLine = []
with open(inputFile, 'r', newline='', encoding='utf-8') as f:
    lines = csv.reader(f)
    for line in lines:
        line.append('0') # 标志位，0 表示原始数据，没有操作
        lineNum += 1
        lineTime = int(line[0])
        if lineNum > 1:
            if times.count(lineTime) > 1:
                raise Exception('repeat time:', line[0])
        if lineNum > 1 and lineTime > times[-1] + period:
            wrongTimeBegin = timestamp_datetime(times[-1])
            wrongTimeEnd = timestamp_datetime(lineTime)
            print('time period longer than before, begin:', wrongTimeBegin, ', end:', wrongTimeEnd)
            if (lineTime - times[-1]) % period != 0:
                raise Exception('wrong time, period:', period)
            lostNum = (lineTime - times[-1]) / period - 1
            if lostNum % 1 != 0:
                raise Exception('wrong lostNum:', lostNum)
            lostNum = int(lostNum)
            print('repair num:', lostNum)
            for i in range(lostNum):
                repairTime = times[-1] + (i + 1) * period
                data1 = (float(line[1]) - float(lastLine[1])) / (lostNum + 1) * (i + 1) + float(lastLine[1])
                data2 = (float(line[2]) - float(lastLine[2])) / (lostNum + 1) * (i + 1) + float(lastLine[2])
                data3 = (float(line[3]) - float(lastLine[3])) / (lostNum + 1) * (i + 1) + float(lastLine[3])
                data4 = (float(line[4]) - float(lastLine[4])) / (lostNum + 1) * (i + 1) + float(lastLine[4])
                data5 = (float(line[5]) - float(lastLine[5])) / (lostNum + 1) * (i + 1) + float(lastLine[5])
                data6 = (float(line[6]) - float(lastLine[6])) / (lostNum + 1) * (i + 1) + float(lastLine[6])
                newLine = [repairTime, data1, data2, data3, data4, data5, data6, 1] # 最后一个标志位，1 表示线性插值
                with open(outputFile, 'a', newline='', encoding='utf-8') as fwrite:
                    writer = csv.writer(fwrite)
                    writer.writerow(newLine)
        elif lineNum > 1 and lineTime < times[-1] + period:
            wrongTimeBegin = timestamp_datetime(times[-1])
            wrongTimeEnd = timestamp_datetime(lineTime)
            raise Exception('time period shorter than before, begin:', wrongTimeBegin, ', end:', wrongTimeEnd)

        times.append(lineTime)
        lastLine = line

        # 保存
        with open(outputFile, 'a', newline='', encoding='utf-8') as fwrite:
            writer = csv.writer(fwrite)
            writer.writerow(line)
        # print("id = ", line[0], " end")
        if lineNum % 1000 == 0:
            print('lineNum =', str(lineNum))
