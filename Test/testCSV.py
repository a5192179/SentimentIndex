import csv

# 使用数字和字符串的数字都可以
# datas = [['name', 'age'],
#          ['Bob', 14],
#          ['Tom', 23],
#         ['Jerry', '18']]

# with open('../../Data/csv2.csv', 'a', newline='') as f:
#     writer = csv.writer(f)
#     for row in datas:
#         writer.writerow(row)

with open('../../Data/csv2.csv', 'r', newline='') as f:
    lines = csv.reader(f)
    with open('../../Data/csv3.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        for row in lines:
            print(row)
            row[1] = row[1].replace('ag', 'age2')
            print(row)
            # writer.writerow(row)