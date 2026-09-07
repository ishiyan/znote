"""
Python code to implement concepts in Technical Analysis of Stocks & Commodiities magazine 
article "Adaptive SuperSmoother" by John F Ehlers. This python code is provided for the 
TraderTips section of the magazine.

Written By:
Rajeev Jain, July 2026
jainraje@yahoo,com

All code available in GitHub:
https://github.com/jainraje/TraderTipArticles/

"""


# import required python modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import math

print(yf.__version__)


# retrive OHLCV using YFinance
symbol = 'QQQ'
ohlcv = yf.download(
    symbol, 
    start="2000-01-01", 
    end="2026-07-11", 
    group_by="Ticker",
    auto_adjust=False,
)
ohlcv = ohlcv[symbol]
ohlcv

# functions to implement indicators calculations 

def rms(series, length):
    series = np.asarray(series, dtype=float)
    out = np.full(len(series), np.nan)

    for i in range(length - 1, len(series)):
        window = series[i - length + 1:i + 1]
        out[i] = np.sqrt(np.mean(window ** 2))

    return out

def supersmoother(price, period):
    price = np.asarray(price, dtype=float)
    out = np.full(len(price), np.nan)

    if len(price) < 3:
        return price.copy()

    Q = np.exp(-1.414 * np.pi / period)
    c1 = 2 * Q * np.cos(1.414 * np.pi / period)
    c2 = Q * Q
    a0 = (1 - c1 + c2) / 2

    # initialization
    out[0] = price[0]
    out[1] = price[1]

    for i in range(2, len(price)):
        out[i] = (
            a0 * (price[i] + price[i - 1])
            + c1 * out[i - 1]
            - c2 * out[i - 2]
        )

    return out

def adaptive_supersmoother(close, period0=20, rms_length=81):
    close = np.asarray(close, dtype=float)
    n = len(close)

    # outputs
    ss_adaptive = np.full(n, np.nan)
    ss_fixed = np.full(n, np.nan)
    period_series = np.full(n, np.nan)

    # initial pass (we update recursively)
    ss_temp = supersmoother(close, period0)

    roc1 = np.full(n, np.nan)
    roc = np.full(n, np.nan)

    for i in range(1, n):
        roc1[i] = ss_temp[i] - ss_temp[i - 1]

        # RMS normalization
        start = max(0, i - rms_length + 1)
        window = roc1[start:i + 1]
        rocrms = np.sqrt(np.mean(window ** 2)) if len(window) > 0 else 0

        if rocrms != 0:
            roc[i] = abs(roc1[i] / rocrms)
        else:
            roc[i] = 0

        roc[i] = min(roc[i], 2)

        period = period0 * (1 - 0.5 * roc[i]) ** 2
        period = max(period, 2)
        period_series[i] = period

    # Recompute adaptive SS properly (true recursive adaptive filter)
    ss_adaptive[0] = close[0]
    ss_adaptive[1] = close[1]

    for i in range(2, n):
        p = period_series[i - 1] if not np.isnan(period_series[i - 1]) else period0

        Q = np.exp(-1.414 * np.pi / p)
        c1 = 2 * Q * np.cos(1.414 * np.pi / p)
        c2 = Q * Q
        a0 = (1 - c1 + c2) / 2

        ss_adaptive[i] = (
            a0 * (close[i] + close[i - 1])
            + c1 * ss_adaptive[i - 1]
            - c2 * ss_adaptive[i - 2]
        )

    return {
        "adaptive_ss": ss_adaptive,
        "fixed_ss": supersmoother(close, period0),
        "roc": roc,
        "period": period_series
    }

def adaptive_supersmoother_series(close, period0=20, rms_length=81):
    return pd.Series(
        adaptive_supersmoother(close, period0, rms_length)["adaptive_ss"],
        index=close.index
    )


# function which encapsultes indicator call and signal generationr 
def run_calcs(ohlcv):
    
    df = ohlcv[['Close']].copy()

    df['SS'] = supersmoother(df['Close'], period=20)
    df['ASS'] = adaptive_supersmoother_series(df['Close'])

    
    df['ASS OSC'] = df['ASS'] - df['SS']
    df['ASS OSC NORM'] = (df['ASS'] - df['SS']) / df['Close'].rolling(20).std()
    
    #df['Signal'] = np.where(df['ASS OSC'] > 0, 1,0)
    df['Signal'] = np.where(df['ASS OSC'] > 0.1, 1,
                    np.where(df['ASS OSC'] < -0.1, 0, np.nan))
    df['Signal'] = df['Signal'].ffill()

    return df

df = run_calcs(ohlcv)
df
def simple_plot(df):
    import matplotlib.pyplot as plt

    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(9, 6),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]}
    )

    # -------------------
    # TOP: Price + filters + signal
    # -------------------
    ax1.plot(df.index, df['Close'], label='Close', color='black', linewidth=1.5)
    ax1.plot(df.index, df['SS'], label='SuperSmoother (SS)', linewidth=1.2)
    ax1.plot(df.index, df['ASS'], label='Adaptive SS (ASS)', linewidth=1.2)

    ax1.set_ylabel('Price')
    ax1.grid(True)

    # Signal on secondary axis (TOP)
    ax1b = ax1.twinx()
    ax1b.step(df.index, df['Signal'], where='post',
              label='Signal (ASS OSC > 0)', color='green', alpha=0.5)

    ax1b.set_ylabel('Signal (0/1)')
    ax1b.set_ylim(-0.1, 1.1)

    # combine legends (top)
    l1, lab1 = ax1.get_legend_handles_labels()
    l2, lab2 = ax1b.get_legend_handles_labels()
    ax1.legend(l1 + l2, lab1 + lab2, loc='upper left')

    ax1.set_title('Price + SuperSmoother + Adaptive SS with Signal')

    # -------------------
    # BOTTOM: Oscillator
    # -------------------
    ax2.plot(df.index, df['ASS OSC'], label='ASS - SS Oscillator', color='purple', alpha=0.8)
    ax2.plot(df.index, df['ASS OSC NORM'], label='ASS NORM- SS Oscillator', color='orange', alpha=0.8)
    
    ax2.axhline(0, color='black', linewidth=1)

    ax2.set_ylabel('Osc')
    ax2.set_xlabel('Date')
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.show()
simple_plot(df['2026':])
