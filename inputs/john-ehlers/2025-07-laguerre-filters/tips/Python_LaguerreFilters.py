# import required python libraries
# %matplotlib inline

import pandas as pd
import numpy as np
import yfinance as yf
import math
import datetime as dt
import matplotlib.pyplot as plt
import mplfinance as mpf

print(yf.__version__)


# Use Yahoo Finance python package to obtain OHLCV data 
symbol = '^GSPC'
symbol = 'SPY'
ohlcv = yf.download(symbol, start="1995-01-01", end="2025-04-18", group_by="Ticker", auto_adjust=True)
ohlcv = ohlcv[symbol]


# Python code building block/routines used to implement the Laguerre filter, 
# the Laguerre oscillator, and the UltimateSmoother as defined by John Ehlers
# in his article. 

def calc_ultimate_smoother(price, period):
    
    a1 = np.exp(-1.414 * np.pi / period)
    b1 = 2*a1*np.cos(math.radians(1.414 * 180 / period))
    c2 = b1
    c3 = -a1 * a1
    c1 = (1 + c2 - c3)/4

    us_values = []

    for i in range(len(price)):
        if i >= 4:
            us_values.append(
                (1-c1)*price[i] + (2*c1 - c2)*price[i-1] - (c1 + c3)*price[i-2] + c2*us_values[i-1] + c3*us_values[i-2]
            )
        else:
            us_values.append(price[i]) 

    return us_values


def calc_rms(price):
    
    length = len(price)
    sum_sq = 0
    for count in range(length):
        sum_sq += price[count] * price[count]
    return np.sqrt(sum_sq / length)


def laguerre_filter(prices, length=40, gama=0.8):
    prices = pd.Series(prices)
    
    # Apply the Ultimate Smoother to get L0
    L0 = calc_ultimate_smoother(prices, length)
    
    # Initialize lagged values
    L1 = pd.Series(np.zeros_like(prices), index=prices.index)
    L2 = pd.Series(np.zeros_like(prices), index=prices.index)
    L3 = pd.Series(np.zeros_like(prices), index=prices.index)
    L4 = pd.Series(np.zeros_like(prices), index=prices.index)
    L5 = pd.Series(np.zeros_like(prices), index=prices.index)
    Laguerre = pd.Series(np.zeros_like(prices), index=prices.index)
        
    for i in range(1, len(prices)):
        L1[i] = -gama * L0[i-1] + L0[i-1] + gama * L1[i-1]
        L2[i] = -gama * L1[i-1] + L1[i-1] + gama * L2[i-1]
        L3[i] = -gama * L2[i-1] + L2[i-1] + gama * L3[i-1]
        L4[i] = -gama * L3[i-1] + L3[i-1] + gama * L4[i-1]
        L5[i] = -gama * L4[i-1] + L4[i-1] + gama * L5[i-1]
        Laguerre[i] = (L0[i] + 4 * L1[i] + 6 * L2[i] + 4 * L3[i] + L5[i]) / 16

    return Laguerre

def laguerre_oscillator(prices, length=40, gama=0.8):
    prices = pd.Series(prices)
    
    # Apply the Ultimate Smoother to get L0
    L0 = calc_ultimate_smoother(prices, length)
    
    # Initialize lagged values
    if 1:
        L1 = pd.Series(np.zeros_like(prices), index=prices.index)
        LaguerreOsc = pd.Series(np.zeros_like(prices), index=prices.index)
    else:
        L1 =[0] * len(prices)
        LaguerreOsc = [0] * len(prices)
        
    for i in range(1, len(prices)):
        L1[i] = -gama * L0[i] + L0[i-1] + gama * L1[i-1]
    
    rms = L1.rolling(100).apply(calc_rms)
    LaguerreOsc = (L0 - L1)/rms
    
    return LaguerreOsc


def simple_plot1(df):
    
    cols = ['Close', 'US', 'Laguerre']
    ax = df[cols].plot(marker='.', grid=True, figsize=(9,6), title=f'Laguerre Filter vs UltimateSmoother, Ticker={symbol}')
    ax.set_xlabel('')

# Below is example usage to run the Laguerre filter and the UltimateSmoother 
# indicator calculations using the length and gamma suggested in John Ehlers' article
# with a simple plot presenting price overlaid with indicators.

length = 30
gama = 0.8

df = ohlcv.copy()
df['US'] = calc_ultimate_smoother(df['Close'], period=length)
df['Laguerre'] = laguerre_filter(df['Close'], length=length, gama=gama)
simple_plot1(df['2024-03':'2025-02-10'])

# Example usage to run the Laguerre Filter, Laguerre Oscillator, and 
# UltimateSmoother indicator calculations using the length and gamma 
# suggested in the article.
# 
# The plot is created using MatplotLib and MplFinance python packages. 
# This plot presents all indicators on a single plot. Crossovers of the 
# Laguerre Filter and UltimateSmoother are overlaid on the price candles.
# The Laguerre Oscillator is plotted as a 2nd subplot.

df = ohlcv.copy()
df['US'] = calc_ultimate_smoother(df['Close'], period=40)
df['Laguerre'] = laguerre_filter(df['Close'], length=40, gama=0.2)
df['LaguerreOsc'] = 100/3*laguerre_oscillator(df['Close'], 20, 0.8)
df
mpf_plot1(df['2024-03':'2025-02-10'])
