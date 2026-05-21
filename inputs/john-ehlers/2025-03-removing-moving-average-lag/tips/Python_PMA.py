#
# import required python libraries
#
import pandas as pd
import numpy as np
import datetime as dt

import matplotlib.pyplot as plt
import yfinance as yf


#
# Retrieve S&P 500 daily price data from Yahoo Finance
# 

symbol = '^GSPC'
ohlcv = yf.download(symbol, start="2015-01-15", end="2025-01-22")
ohlcv


#
# Introducing the Projected Moving Average PMA
# 

def linear_regression_slope(samples):
    # Use numpy's polyfit to calculate the slope (1st degree polynomial)
    m, b = np.polyfit(np.arange(len(samples)), np.array(samples), 1)

    return m
    
def calc_linear_regression_slope(in_series, length):
    slope = in_series.rolling(length).apply(linear_regression_slope)
    return slope

def calc_sma(in_series, length):
    return in_series.rolling(length).mean()

def calc_pma(in_series, length):
    sma = calc_sma(in_series, length)
    slope = calc_linear_regression_slope(in_series, length)
    pma = (sma + slope * length / 2)
    return pma


#
# S&P500 applying SMA and PMA indicators using 30 trading days
# 

length = 30
df = ohlcv.copy()

df['SMA'] = calc_sma(df['Close'], length)
df['PMA'] = calc_pma(df['Close'], length)
simple_plot1(df['2023-09':'2024-09-04'], length)




#
# S&P500 applying SMA and PMA indicators using 200 trading days
# 

length = 200
df = ohlcv.copy()

df['SMA'] = calc_sma(df['Close'], length)
df['PMA'] = calc_pma(df['Close'], length)
simple_plot1(df['2023-09':'2024-09-04'], length)



#
# Prediction to Further Reduce Lag
# 

def calc_pma_prediction(pma, slope, length):
    # Predict = PMA + 0.5*(Slope - Slope[2])*Length
    predict = pma + (slope - slope.shift(2)) * length / 2

    return predict


#
# S&P500 applying PMA and PMA Prediction indicators
# 


length = 30
df = ohlcv.copy()

df['SMA'] = calc_sma(df['Close'], length)
df['PMA'] = calc_pma(df['Close'], length)
#df['LRC'] = df['Close'].rolling(length).apply(linear_regression_curve)
df['Slope'] = df['Close'].rolling(length).apply(linear_regression_slope)
df['Predict'] = calc_pma_prediction(df['PMA'], df['Slope'], length)
df['Signal'] = np.where(df['Predict'] > df['PMA'], 1, 0)
simple_plot2(df['2023-09':'2024-09-04'], length, signal_ena=True)




#
# Introducing Generalized Prediction of an Indicator
# 

def calc_general_prediction(smooth): 
 
    predict = 1.5*smooth - 0.5*smooth.shift(4) 
    return predict


#
# S&P 500 appling Slope and Slope Prediction indicators
# 

length = 30
df = ohlcv.copy()

df['SMA'] = calc_sma(df['Close'], length)
df['PMA'] = calc_pma(df['Close'], length)

#df['LRC'] = df['Close'].rolling(length).apply(linear_regression_curve)
df['Slope'] = df['Close'].rolling(length).apply(linear_regression_slope)
df['Predict'] = calc_pma_prediction(df['PMA'], df['Slope'], length)
df['Slope Predict'] = calc_general_prediction(df['Slope'])
