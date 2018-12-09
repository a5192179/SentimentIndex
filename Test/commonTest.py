import pandas as pd
allWord = ['aa', 'aa', 'bb', 'bb', 'bb', 'cc']
dict = pd.DataFrame(pd.Series(allWord).value_counts())


dict1 = pd.read_csv('E:\Project\SentimentIndex\Data\BigData2\MarkedMessageDict.csv', index_col=0, names = ['count', 'id', 'bullNum', 'bearNum'])

a=1