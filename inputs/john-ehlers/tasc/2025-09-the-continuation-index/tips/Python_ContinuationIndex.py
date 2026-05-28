"""
Written By: Rajeev Jain, 2025-07-23
Trader Tips python code for TAS&C Magazine article "The Continuation Index"

"""

# import required python libraries
# %matplotlib inline

import pandas as pd
import numpy as np
import math
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt

print(yf.__version__)


# Use Yahoo Finance python package to obtain OHLCV data for the SP500 index
symbol = '^GSPC'
ohlcv = yf.download(
    symbol, 
    start="2019-01-01", 
    end="2025-07-24", 
    auto_adjust=True,
    multi_level_index=False,
    progress=False,
)

# Python functions to implement UltimateSmoother, Laguerre Filter and 
# Continuation Index as defined in John Ehlers' article. 
def ultimate_smoother(price_series, period):
    """
    Ultimate Smoother function converted from EasyLanguage to Python.
    
    Parameters:
        price_series (list or np.array): Time series of prices (e.g., closing prices)
        period (float): Smoothing period

    Returns:
        np.array: Smoothed price series
    """
    price_series = np.asarray(price_series)
    n = len(price_series)
    US = np.zeros(n)

    # Filter coefficients
    Q = math.exp(-1.414 * math.pi / period)
    c1 = 2 * Q * math.cos(1.414 * math.pi / period)
    c2 = Q * Q
    a0 = (1 + c1 + c2) / 4

    for i in range(n):
        if i < 3:
            US[i] = price_series[i]
        else:
            US[i] = ((1 - a0) * price_series[i] +
                     (2 * a0 - c1) * price_series[i - 1] +
                     (c2 - a0) * price_series[i - 2] +
                     c1 * US[i - 1] -
                     c2 * US[i - 2])
    return US

def laguerre_filter(price_series, gama, order, length):
    """
    Laguerre Filter Function converted from EasyLanguage to Python.
    Parameters:
        price_series (list or np.array): Input price data
        gama (float): Laguerre parameter, 0 <= gama < 1
        order (int): Filter order (integer <= 10)
        length (float): Length for Ultimate Smoother
    Returns:
        np.array: Laguerre filtered series
    """
    assert 0 <= gama < 1, "gama must be in [0, 1)"
    assert order <= 10 and order >= 1, "order must be integer between 1 and 10"
    price_series = np.asarray(price_series)
    n = len(price_series)
    output = np.zeros(n)

    # Initialize Laguerre matrix: shape (order+1, 2)
    LG = np.zeros((order + 1, 2))

    # Precompute ultimate smoother once
    smoothed_price = ultimate_smoother(price_series, length)
    for t in range(n):
        # Shift previous values: LG[:, 2] = LG[:, 1]
        LG[:, 1] = LG[:, 0]
        # Update LG[1] using the smoothed price at current time
        LG[1, 0] = smoothed_price[t]
        # Compute rest of the Laguerre components recursively
        for count in range(2, order + 1):
            LG[count, 0] = (
                -gama * LG[count - 1, 1] +
                LG[count - 1, 1] +
                gama * LG[count, 1]
            )
        # Sum current values of LG[1] to LG[order]
        FIR = np.sum(LG[1:order + 1, 0])
        output[t] = FIR / order
    return output

def continuation_index(close_prices, gama=0.8, order=8, length=40):
    """
    Continuation Index by John F. Ehlers (converted from EasyLanguage).
    
    Parameters:
        close_prices (list or np.array): Series of closing prices
        gama (float): Laguerre gamma (0 <= gama < 1)
        order (int): Order of Laguerre filter (<= 10)
        length (int): Base smoothing period
    Returns:
        np.array: Continuation Index values
    """
    close_prices = np.asarray(close_prices)
    n = len(close_prices)

    # Step 1: Ultimate Smoother with Length / 2
    US = ultimate_smoother(close_prices, length / 2)
    # Step 2: Laguerre Filter
    LG = laguerre_filter(close_prices, gama, order, length)
    # Step 3: Variance = avg(abs(US - LG)) over Length
    diff = np.abs(US - LG)
    variance = np.convolve(diff, np.ones(length)/length, mode='same')
    # Step 4: Normalized difference, scaled by 2
    with np.errstate(divide='ignore', invalid='ignore'):
        ref = np.where(variance != 0, 2 * (US - LG) / variance, 0)
    # Step 5: Inverse Fisher Transform compression
    CI = (np.exp(2 * ref) - 1) / (np.exp(2 * ref) + 1)
    return CI

# Compare Laguerre filter response for gamma setting of 0.4 vs gamma setting of 0.8
gama1 = 0.4
gama2 = 0.8
order = 8
length = 40
df = ohlcv.copy()
df['Laguerre_0.4'] = laguerre_filter(df['Close'], gama1, order, length)
df['Laguerre_0.8'] = laguerre_filter(df['Close'], gama2, order, length)
cols = ['Close', 'Laguerre_0.4', 'Laguerre_0.8']
ax = df[-255:][cols].plot(marker='.', grid=True, figsize=(9,6), title=f'Ticker={symbol}, Laguerre Filter Response, Gamma Parameter Comparison')
ax.set_xlabel('')
plt.show()

# Compare Laguerre filter response for order of 4 vs order of 8
order1 = 4
order2 = 8
length = 40
gama = 0.8
df = ohlcv.copy()
df['Laguerre_4th'] = laguerre_filter(df['Close'], gama, order1, length)
df['Laguerre_8th'] = laguerre_filter(df['Close'], gama, order2, length)
df
cols = ['Close', 'Laguerre_4th', 'Laguerre_8th']
ax = df[-255:][cols].plot(marker='.', grid=True, figsize=(9,6), title=f'Ticker={symbol}, Laguerre Filter Response, Order Parameter Comparison')
ax.set_xlabel('')
plt.show()

# Example of continuation index using default setting for 
# daily close of S&P 500 index
def plot_ci(df):
    ax = df[['Close', 'Laguerre']].plot(
        marker='.', 
        grid=True, 
        figsize=(9,4), 
        title=f'Ticker={symbol}'
    )
    ax.set_xlabel('')
    ax = df[['CI']].plot(
        marker='.', 
        grid=True, 
        figsize=(9,2), 
        title=f'Continuation Index'
    )
    ax.set_xlabel('')

gama=0.8
order=8
length=40
df = ohlcv.copy()
df['Laguerre'] = laguerre_filter(df['Close'], gama, order, length)
df['CI'] = continuation_index(df['Close'], gama, order, length)
plot_ci(df[-252:])
