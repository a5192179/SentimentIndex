import time
import datetime
import csv
import os

old2NewFile = '../../Data/AfterTrainDataDate/TestMessage.csv'
new2OldFile = '../../Data/OriginMessage.csv'
saveFile = '../../Data/TidyOriginalData/TidyOriginalMessage.csv'
if os.path.exists(saveFile):
    os.remove(saveFile)
gapTime = "2018-01-11T11:46:42Z"
gapTime = time.strptime(gapTime, "%Y-%m-%dT%H:%M:%SZ")
gapTime = time.mktime(gapTime)
messageList = []
with open(new2OldFile, 'r', newline='', encoding='utf-8') as f:
    lines = csv.reader(f)
    for line in lines:
        messageTime = line[1]
        messageTime = time.strptime(messageTime, "%Y-%m-%dT%H:%M:%SZ")
        messageTime = time.mktime(messageTime)
        if messageTime > gapTime:
            continue
        messageList.append(line)
messageList.reverse()
with open(old2NewFile, 'r', newline='', encoding='utf-8') as f:
    lines = csv.reader(f)
    for line in lines:
        messageList.append(line)

with open(saveFile, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # for i in range(len(infoList)):
    #     writer.writerow(infoList[len(infoList) - i])
    for row in messageList:
        writer.writerow(row)
