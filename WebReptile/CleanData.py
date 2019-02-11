import csv
import os
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer

lineNum = 0
markers = [':', '(', ')', '.', '*', ';', ',', '"', '-', '!', '?', '💵', '%', '💪', '👽', '😍', '😭', '🙃', '😝', '🌝', '😝', '🌚', '😠', '😤', '😎', '🤠', '😳','🤡', '😱', '🤔', '😊', '😐', '😑' '😁', '🤑', '😉', '🤐', '😂', '😷', '🎆', '🐻', '🤣', '💩', '💰', '🚀', '🤞', '🙋🏻‍', '♂', '🙌🏾', '📉', '📈', '📊',
           '💱', '📚', '🔥', '😀', '👀', '🤣', '🌊', '🎉', '👹', '💣', '🤷🏻', '🙈', '🐳', '💥', '📁', '👍', '👎', '💀', '🤦🏽', '🤦🏻‍', '‍♂️', '👋', '📞', '✈️', '☝️', '🌎', '❤️', '💯', '🔨', '☕️',
           '🐂', '🐃', '🖕', '🎅🏼', '👇', '🐫', '💸', '🙏', '🛫', '🕶', '🌽', '👑', '🥂', '💤', '💪🏻', '🚽', '👋', '🌋', '🏃', '♀️', '🏝', '🛳', '✌🏽', '👌🏾', '🏦', '💸', '👌', '🔻', '🤙', '🍻', '✅', '🤖']
# inputFile = '../../Data/OriginTestMessage.csv'
# outputFile = '../../Data/CleanedTestMessage_MoreMark.csv'
# inputFile = '../../Data/BigData/OriginMessage.csv'
# outputFile = '../../Data/BigData/CleanedMessage_MoreMark.csv'
inputFile = '../../Data/TidyOriginalData/TidyOriginalMessage.csv'
outputFolder = '../../Data/LSTM/Input/2018120801'
outputFile = outputFolder + '/CleanedMessage.csv'
if os.path.exists(outputFile):
    os.remove(outputFile)
if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)
with open(inputFile, 'r', newline='', encoding='utf-8') as f:
    lines = csv.reader(f)
    for line in lines:
        lineNum += 1
    print('no error line')

lineNum = 0
with open(inputFile, 'r', newline='', encoding='utf-8') as f:
    lines = csv.reader(f)
    for line in lines:
        lineNum += 1
        # print("id = ", line[0], " begin")
        # 检查
        if line == "":
            print("id = ", line[0], " is empty")
        # 删除引号
        if line[3][0] == '"' and line[3][-1] == '"':
            line[3][0] = ''
            line[3][-1] = ''
        # 转义
        line[3] = line[3].replace('&quot;', '"')
        line[3] = line[3].replace('&amp;', '&')
        line[3] = line[3].replace('&lt;', '<')
        line[3] = line[3].replace('&gt;', '>')
        line[3] = line[3].replace('&#39;', '\'')
        line[3] = line[3].replace('“', '"')
        line[3] = line[3].replace('”', '"')
        line[3] = line[3].replace('’', '\'')

        # 删除网址
        index = line[3].find('https://')
        if index == -1:
            index = line[3].find('http://')
        if index != -1:
            line[3] = line[3][0:index]

        #改为小写
        line[3] = line[3].lower()

        # 标点分割
        temp = line[3]
        index_temp = 0
        index_line = 0

        for word in temp:
            index_temp = index_temp + 1  # word在temp里面的第几个字符的索引，从1开始
            index_line = index_line + 1  # word在line里面的第几个字符的索引，从1开始
            if not(word.isalpha() or word.isnumeric()):
                if word.isspace():
                    continue
                if word == '.':
                    if index_temp != len(temp):
                        if temp[index_temp] == 'x':
                            continue
                        if temp[index_temp].isnumeric():
                            continue
                if word == '$':
                    if index_line > 1 and not (line[3][index_line - 2].isspace()):  # 字符的前一位不是空格
                        line[3] = line[3][0: index_line - 1] + ' ' + line[3][index_line - 1: len(line[3])]  # 前加空格
                        index_line = index_line + 1
                    continue
                if word == '\'' and index_temp < len(temp) and temp[index_temp] == 's':
                    continue
                # if index_temp > 1 and not (temp[index_temp - 2].isspace()):  # 字符的前一位不是空格
                #     line[3] = line[3][0: index_line - 1] + ' ' + line[3][index_line - 1: len(line[3])]  # 前加空格
                #     index_line = index_line + 1
                # if index_temp < len(temp) and not (temp[index_temp].isspace()):  # 字符的后一位不是空格
                #     line[3] = line[3][0: index_line] + ' ' + line[3][index_line: len(line[3])]   # 后加空格
                #     index_line = index_line + 1
                if index_line > 1 and not (line[3][index_line - 2].isspace()):  # 字符的前一位不是空格
                    line[3] = line[3][0: index_line - 1] + ' ' + line[3][index_line - 1: len(line[3])]  # 前加空格
                    index_line = index_line + 1
                if index_line < len(line[3]) and not (line[3][index_line].isspace()):  # 字符的后一位不是空格
                    line[3] = line[3][0: index_line] + ' ' + line[3][index_line: len(line[3])]   # 后加空格
                    index_line = index_line + 1

        # 改为词根
        # ================================
        stemmer = PorterStemmer()
        message = line[3].split(' ')
        for i in range(len(message)):
            message[i] = stemmer.stem(message[i])
        line[3] = ' '.join(message)
        # ================================
        # lemmatizer = WordNetLemmatizer()
        # message = line[3].split(' ')
        # for i in range(len(message)):
        #     message[i] = lemmatizer.lemmatize(message[i])
        # line[3] = ' '.join(message)
        # ================================

        if line[3] != '' and line[3][-1] == '':
            a=1

        # 保存
        with open(outputFile, 'a', newline='', encoding='utf-8') as fwrite:
            writer = csv.writer(fwrite)
            writer.writerow(line)
        # print("id = ", line[0], " end")
        if lineNum % 1000 == 0:
            print('lineNum =', str(lineNum))


