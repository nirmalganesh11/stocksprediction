import re
from django.shortcuts import render,HttpResponse
import yfinance as yf
import math
from sklearn.preprocessing import MinMaxScaler
# Create your views here.
import numpy as np
import tensorflow as tf
import keras
from keras.preprocessing import image
from keras.models import Sequential
from keras.layers import Conv2D, MaxPool2D, Flatten,Dense,Dropout,BatchNormalization,LSTM,Bidirectional
from keras import regularizers
from tensorflow.keras.optimizers import Adam,RMSprop,SGD,Adamax
import csv
from keras.callbacks import EarlyStopping,ModelCheckpoint
from keras import optimizers
import pandas as pd
from datetime import timedelta, date
from django.core.paginator import Paginator


df=None
df1=None
df2=None





def download(request,id):
    global df,df1,df2
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data.csv"' # your filename
    
    if id=='0':
        writer = csv.writer(response)
        writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        for ind in df.index:
            writer.writerow([ind,df['Open'][ind],df['High'][ind],df['Low'][ind],df['Close'][ind],df['Volume'][ind]])
    elif id=='1':
        writer = csv.writer(response)
        writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        for ind in df1.index:
            writer.writerow([ind,df1['Open'][ind],df1['High'][ind],df1['Low'][ind],df1['Close'][ind],df1['Volume'][ind]])
    elif id=='2':
        writer = csv.writer(response)
        writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        for ind in df2.index:
            writer.writerow([ind,df2['Open'][ind],df2['High'][ind],df2['Low'][ind],df2['Close'][ind],df2['Volume'][ind]])
    elif id=='3':
        writer = csv.writer(response)
        writer.writerow(['', 'Date','Prediction'])
        for ind in df.index:
            writer.writerow([ind,df['Date'][ind],df['Prediction'][ind]])
    elif id=='4':
        writer = csv.writer(response)
        writer.writerow(['', 'Symbol','Name','High','Low','Open','Close','Net Change','% Change','Industory','Country'])
        for ind in df.index:
            writer.writerow([ind,df['symbol'][ind],df['name'][ind],df['high'][ind],df['low'][ind],df['open'][ind],df['close'][ind],df['net change'][ind],df['% Change'][ind],df['industory'][ind],df['country'][ind]])
    return response


def predict(request):
    global df
    stocks="BTC-INR"
    start_date='2000-04-01'
    close_date='2022-08-13'
    context={"flag":False}
    if request.method == 'POST':
        stocks = request.POST.get('company1')
        days=int(request.POST.get('days'))
        bitcoin = yf.Ticker(stocks)
        df=bitcoin.history(start=str(start_date), end=str(close_date), actions=False)
       
        x=list(map(str,df.index.strftime('%d-%m-%y')))
        y_high=list(df['Close'])
        df=df.drop(['Open','High','Volume','Low'],axis=1)
        min_max_scalar=MinMaxScaler(feature_range=(0,1))
        data=df.values
        scaled_data=min_max_scalar.fit_transform(data)
        train_data=scaled_data[:,:]
        x_train=[]
        y_train=[]
        interval=90
        for i in range(interval,len(train_data)):
            x_train.append(train_data[i-interval:i,0])
            y_train.append(train_data[i,0])
        x_train,y_train=np.array(x_train),np.array(y_train)
        x_train=np.reshape(x_train,(x_train.shape[0],x_train.shape[1],1))
        

        stop = EarlyStopping(
        monitor='val_loss', 
        mode='min',
        patience=5
        )

        checkpoint= ModelCheckpoint(
            filepath='./',
            save_weights_only=True,
            monitor='val_loss',
            mode='min',
            save_best_only=True)

        model=Sequential()
        model.add(LSTM(200,return_sequences=True,input_shape=(x_train.shape[1],1)))
        model.add(LSTM(units=100))
        model.add(Dense(100))
        model.add(Dense(1))

        adam = optimizers.Adam(lr=0.0005)

        model.compile(optimizer=adam, loss='mse')
        model.fit(x_train, y_train, batch_size=512, epochs=10,shuffle=True, validation_split=0.05, callbacks = [checkpoint,stop])
        model.load_weights("./")
        df_test=bitcoin.history(start='2000-01-01', end='2032-05-13', actions=False)
        df_test=df_test.drop(['Open','High','Volume','Low'],axis=1)
        predicted=[]
        for i in range(days):
            if predicted!=[]:
                if (-interval+i)<0:
                    test_value=df_test[-interval+i:].values
                    test_value=np.append(test_value,predicted)
                else:
                    test_value=np.array(predicted)
            else:
                test_value=df_test[-interval+i:].values
            test_value=test_value[-interval:].reshape(-1,1)
            test_value=min_max_scalar.transform(test_value)
            test=[]
            test.append(test_value)
            test=np.array(test)
            test=np.reshape(test,(test.shape[0],test.shape[1],1))
            tomorrow_prediction=model.predict(test)
            tomorrow_prediction=min_max_scalar.inverse_transform(tomorrow_prediction)
            predicted.append(tomorrow_prediction[0][0])
        predicted_x=[]
        for i in range(1,days+1):
            predicted_x.append( str((date.today() + timedelta(days=i)).strftime('%d-%m-%y')))
        if predicted[0]<predicted[-1] and y_high[-1]<predicted[-1]:
            buy="Yes"
        else:
            buy="No"

        dic={}
        dic['Date']=predicted_x
        dic['Prediction']=predicted
        df=pd.DataFrame.from_dict(dic)
        context={
                'x':x,
                'y_high':y_high,
                'company':stocks,
                'predicted_x':predicted_x,
                'predicted_y':predicted,
                "flag":True,
                "days":days,
                "csv":zip(predicted_x,predicted),
                "max_price":round(max(predicted),2),
                "min_price":round(min(predicted),2),
                "buy":buy,
                "change_in_precentage":round(((max(predicted)-min(predicted))/(min(predicted)))*100,2),
                "change_in_price":round((max(predicted)-min(predicted)),2)
            }
    
    return render(request,'predict.html',context)



def details(request,id):
    global df
    stocks = str(id)

    bitcoin = yf.Ticker(stocks)
    des=bitcoin.info
    temp_des={}
    for key in des:
        if des[key]!='None' and des[key]!=[]:
            temp_des[key]=des[key]
    des=temp_des
    df=bitcoin.history(start='2000-01-01', end='2032-05-13',  actions=False)
    df['Date']=df.index.strftime('%d-%m-%Y')
    x=list(map(str,df.index.strftime('%d-%m-%y')))
    y_high=list(df['High'])
    y_open=list(df['Open'])
    y_low=list(df['Low'])
    y_close=list(df['Close'])
    y_volume=list(df['Volume'])    
    context={
            'x':x,
            'y_high':y_high,
            'y_low':y_low,
            'y_open':y_open,
            'y_close':y_close,
            'y_volume':y_volume,
            'company':stocks,
            'df':df,
            'predicted_x':[1,2,3,4,5],
            'predicted_y':[5,4,3,2,1],
            'max_price':round(max(y_high),2),
            'min_price':round(min(y_low),2),
            'last_day_price':round(y_close[-1],2),
            'change_in_price':round(y_high[-1]-y_high[0],2),
            'change_in_precentage':round(((y_high[-1]-y_high[0])/y_high[0])*100,2),
            "description":des,
            "flag":True,
            'company':stocks,
        }
    
    return render(request,'details.html',context)