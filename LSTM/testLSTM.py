import numpy
from keras.models import Sequential
from keras.layers.recurrent import LSTM
from keras.layers import Dense, Activation

xx = numpy.random.rand(800,100)
yy = numpy.random.rand(800)

model = Sequential()
model.add(LSTM(8,input_shape=(100, 1, 0)))
model.add(Dense(2))

model.compile(optimizer='adadelta', loss='mse')
model.fit(xx, yy, batch_size=30, nb_epoch=5, verbose=1)
a=1