#
# import required python libraries
#
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import math

#
# Retrieve S&P 500 daily price data from Yahoo Finance
# 

symbol = '^GSPC'
ohlcv = yf.download(symbol, start="2000-01-01", end="2025-02-21", group_by="Ticker")
# ohlcv = ohlcv[symbol]  # un-comment for older versions of yf module
ohlcv



#
# Python code for highpass, rms and ultimate oscillator functions highlighted in the article
# 

def calc_highpass(price, period):
    
    a1 = np.exp(-1.414 * np.pi / period)
    b1 = 2 * a1 * np.cos(math.radians(1.414 * 180 / period))
    c2 = b1
    c3 = -a1 * a1
    c1 = (1 + c2 - c3)/4

    out_values = []
    for i in range(len(price)):
        if i >= 4:
            out_values.append(
                c1*(price[i] - 2*price[i-1] + price[i-2]) + c2*out_values[i-1] + c3*out_values[i-2]
            )
        else:
            out_values.append(price[i])
    
    return out_values


def calc_rms(price):

    length = len(price)
    sum_sq = 0
    for count in range(length):
        sum_sq += price[count] * price[count]
    return np.sqrt(sum_sq / length)
    

def calc_ultimate_oscillator(close, band_edge, band_width):

    df = close.to_frame('Close')
    df['HP1'] = calc_highpass(df['Close'], band_width * band_edge)
    df['HP2'] = calc_highpass(df['Close'], band_edge)
    df['Signal'] = df['HP1'] - df['HP2']
    df['RMS'] = df['Signal'].rolling(100).apply(calc_rms)
    df['UO'] = df['Signal']/df['RMS']
    
    return df['UO'] 

#
# S&P500 applying EMA and Ultimate Oscillator
# 

band_edge=30
band_width=2
length = band_edge

df = ohlcv.copy()
df['EMA'] = calc_ema(df['Close'], period=length)
df['UO'] = calc_ultimate_oscillator(df['Close'], band_edge, band_width)

# Plot using MatPlotLib python package
plot_uo(df['2024':'2024'])
