from __future__ import division, print_function, absolute_import
from keras.models import Sequential, model_from_json
from keras.layers import Dense, Dropout, Flatten, Conv3D, MaxPooling3D, BatchNormalization, Input
from keras.optimizers import RMSprop
from keras.preprocessing.image import ImageDataGenerator
from keras.utils.np_utils import to_categorical
from keras.callbacks import ReduceLROnPlateau, TensorBoard
import h5py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('white')
from sklearn.metrics import confusion_matrix, accuracy_score
import os
import sys
import matplotlib.pyplot as plt
import re
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split
from keras import backend as K
from keras.callbacks import ModelCheckpoint


def r2_keras(y_true, y_pred):
    SS_res =  K.sum(K.square(y_true - y_pred)) 
    SS_tot = K.sum(K.square(y_true - K.mean(y_true)))
    return ( 1 - SS_res/(SS_tot + K.epsilon()) )


#Change to 001_Python_Codes directory
os.chdir('E:\\Fajar\\CNN_Permeability\\001_PythonCodes')
sys.path.append(os.getcwd())
#Import datagenerator
from my_classes_001 import DataGenerator

#Change to script directory


#Load the data
dim1,dim2,dim3,chn = 100,100,100,1
#dim1,dim2,dim3,chn = 150,150,150,1
image3D_stack = []
phi = []
ssa = []
os.chdir('..\\002_Data\\Berea Sandstone')
for image3D_dir in os.listdir(os.getcwd())[:100]:
    phi.append([float(s) for s in re.findall('[-+]?\d*\.\d+|\d+',
                image3D_dir)][1])
    ssa.append([float(s) for s in re.findall('[-+]?\d*\.\d+|\d+',
                image3D_dir)][2])
k = np.power(1-np.array(phi), 3)/np.power(ssa, 2)
k_norm = k/np.max(k)
#Split the data
#X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.1,
#                                                  random_state=42)
#plt.scatter(np.arange(1,9262),k[:9261], s = 3)
#
#plt.scatter((1-np.array(phi)),k)
#plt.yscale('log')

# Parameters
params = {'dim': (dim1,dim2,dim3),
          'batch_size': 20,
          'n_classes': 1,
          'n_channels': chn,
          'shuffle': False}

#Datasets
partition = {
		'train': os.listdir(os.getcwd())[:90],
		'validation': os.listdir(os.getcwd())[90:100]
		}
labels = dict(zip(os.listdir(os.getcwd())[:100], k_norm))

# Generators
training_generator = DataGenerator(partition['train'], labels, **params)
validation_generator = DataGenerator(partition['validation'], labels, **params)



#Define a model
model = Sequential()
model.add(Conv3D(32, kernel_size=5, strides=(2, 2, 2), padding='valid',
                 data_format='channels_last', dilation_rate=(1, 1, 1),
                 activation='relu', use_bias=True,
                 kernel_initializer='glorot_uniform', bias_initializer='zeros',
                 kernel_regularizer=None, bias_regularizer=None, 
                 activity_regularizer=None, kernel_constraint=None,
                 bias_constraint=None, input_shape=(dim1, dim2, dim3, chn)))
model.add(Conv3D(32, kernel_size=5, strides=(2, 2, 2), padding='valid',
                 data_format='channels_last', dilation_rate=(1, 1, 1),
                 activation='relu', use_bias=True,
                 kernel_initializer='glorot_uniform', bias_initializer='zeros',
                 kernel_regularizer=None, bias_regularizer=None, 
                 activity_regularizer=None, kernel_constraint=None,
                 bias_constraint=None))
model.add(MaxPooling3D(pool_size=(2, 2, 2), strides=(1, 1, 1), padding='valid',
                       data_format='channels_last'))
model.add(Conv3D(32, kernel_size=3, strides=(1, 1, 1), padding='valid',
                 data_format='channels_last', dilation_rate=(1, 1, 1),
                 activation='relu', use_bias=True,
                 kernel_initializer='glorot_uniform', bias_initializer='zeros',
                 kernel_regularizer=None, bias_regularizer=None, 
                 activity_regularizer=None, kernel_constraint=None,
                 bias_constraint=None))
model.add(Conv3D(32, kernel_size=3, strides=(1, 1, 1), padding='valid',
                 data_format='channels_last', dilation_rate=(1, 1, 1),
                 activation='relu', use_bias=True,
                 kernel_initializer='glorot_uniform', bias_initializer='zeros',
                 kernel_regularizer=None, bias_regularizer=None, 
                 activity_regularizer=None, kernel_constraint=None,
                 bias_constraint=None))
model.add(MaxPooling3D(pool_size=(2, 2, 2), strides=(1, 1, 1), padding='valid',
                       data_format='channels_last'))
model.add(Flatten(data_format='channels_last'))
model.add(Dense(128, activation='relu', use_bias=True,
                kernel_initializer='glorot_uniform', bias_initializer='zeros',
                kernel_regularizer=None, bias_regularizer=None,
                activity_regularizer=None, kernel_constraint=None,
                bias_constraint=None))
model.add(Dense(64, activation='relu', use_bias=True,
                kernel_initializer='glorot_uniform', bias_initializer='zeros',
                kernel_regularizer=None, bias_regularizer=None,
                activity_regularizer=None, kernel_constraint=None,
                bias_constraint=None))
model.add(Dense(1, activation=None, use_bias=True,
                kernel_initializer='glorot_uniform', bias_initializer='zeros',
                kernel_regularizer=None, bias_regularizer=None,
                activity_regularizer=None, kernel_constraint=None,
                bias_constraint=None))

#Compile the model
model.compile(optimizer='Adam', loss='mean_squared_error', metrics=[r2_keras],
              loss_weights=None, sample_weight_mode=None,weighted_metrics=None,
              target_tensors=None)
#Train the model
#model.fit(X_train, y_train, batch_size=10, epochs=1, verbose=1,
#          callbacks=None, validation_split=0.0, validation_data=None,
#          shuffle=True, class_weight=None, sample_weight=None, initial_epoch=0,
#          steps_per_epoch=None, validation_steps=None)

# This checkpoint object will store the model parameters in the file "weights.hdf5"
checkpoint = ModelCheckpoint(filepath='weights3.hdf5', monitor='val_loss')


os.chdir('E:\\Fajar\\CNN_Permeability\\002_Data\\Berea Sandstone npy')
# Train model on dataset
model.fit_generator(generator=training_generator,
                    epochs=100,
                    validation_data=validation_generator,
                    callbacks=[checkpoint],
                    use_multiprocessing=False)


model.load_weights('weights3.hdf5')

testing_training = model.predict_generator(generator=training_generator, steps=None,
                                  max_queue_size=10, workers=1,
                                  use_multiprocessing=False, verbose=0)

testing_validation = model.predict_generator(generator=validation_generator, steps=None,
                                  max_queue_size=10, workers=1,
                                  use_multiprocessing=False, verbose=0)

plt.figure()
plt.scatter(np.arange(0,len(testing_training)),k_norm[:len(testing_training)])
plt.scatter(np.arange(0,len(testing_training)),testing_training)

plt.figure()
plt.scatter(np.arange(0,len(testing_validation)),k_norm[:len(testing_validation)])
plt.scatter(np.arange(0,len(testing_validation)),testing_validation)

