"""
Python code to implement concepts in Technical Analysis of Stocks & Commodiities magazine 
April 2026 article "A Synthetic Oscillator" by John F Ehlers. This python code is provided 
for TraderTips section of the magazine.

Written By:
Rajeev Jain, Feb 2026
jainraje@yahoo,com

All code available in GitHub:
https://github.com/jainraje/TraderTipArticles/

HELPER FUNCTIONS 
Not included in Trader Tip article but included in the associated
Jupyter notebook found in the GitHub repo.

Functions called:
- HannFilter
- SuperSmoother
- HighPassFilter
- UltimateSmoother
- RMS

"""

# import required python libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import math
print(yf.__version__)

# MAIN CODE FOR ARTICLE

def synthetic_oscillator(close, params=(15, 25, 4)):
    """
    Synthetic Oscillator function (Python version compatible with list-based helper functions)
    close       : list of closing prices
    lower_bound : Lower bound of cycle period
    upper_bound : Upper bound of cycle period
    length      : smoothing length (not directly used here)
    returns: list of oscillator values

    """

    lower_bound = params[0]
    upper_bound = params[1]
    length = params[2]

    n = len(close)
    synth = [0] * n
    phase = [0] * n

    # Step 1: Price preprocessing with Hann window
    price = hann_lowpass(close, length=12)

    # Step 2: Real component (bandpass filtered & normalized)
    hp = high_pass(price, upper_bound)
    lp = super_smoother(hp, lower_bound)
    rms_lp = rms(lp, 100)
    real = [lp[i] / rms_lp[i] if rms_lp[i] != 0 else 0 for i in range(n)]

    # Step 3: Imaginary component (rate of change normalized)
    roc = [0] * n
    for i in range(1, n):
        roc[i] = real[i] - real[i-1]
    qrms = rms(roc, 100)
    imag = [roc[i] / qrms[i] if qrms[i] != 0 else 0 for i in range(n)]

    # Step 4: Dominant cycle period (DC) calculation
    dc = [0] * n
    for i in range(1, n):
        denom = (real[i] - real[i-1]) * imag[i] - (imag[i] - imag[i-1]) * real[i]
        if denom != 0:
            dc_val = 2 * math.pi * (real[i]**2 + imag[i]**2) / denom
            # limit DC to lower and upper bounds
            dc[i] = max(lower_bound, min(dc_val, upper_bound))
        else:
            dc[i] = lower_bound

    # Step 5: Midpoint cycle
    mid = math.sqrt(lower_bound * upper_bound)

    # Step 6: Bandpass filter at average dominant cycle
    hp2 = high_pass(close, mid)
    bp = ultimate_smoother(hp2, mid)

    # Step 7: Phase accumulation
    for i in range(1, n):
        phase[i] = phase[i-1] + 360 / dc[i]

        # Reset phase at BP zero crossings
        if bp[i-1] < 0 <= bp[i]:
            phase[i] = 180 / dc[i]
        elif bp[i-1] > 0 >= bp[i]:
            phase[i] = 180 + 180 / dc[i]

    # Step 8: Synthetic oscillator = sine of cumulative phase
    synth = [math.sin(math.radians(p)) for p in phase]

    # Step 9: Remove reset glitch if continuity falls in same quadrant
    for i in range(1, n):
        if 0 < phase[i] < 90 and synth[i] < synth[i-1]:
            synth[i] = synth[i-1]
        elif 180 < phase[i] < 270 and synth[i] > synth[i-1]:
            synth[i] = synth[i-1]

    return synth

def plot_trading_signals(df, params, plot_so_ena=False, plot_roc2_ena=True, plot_buy_sell_ena=True):
    
    fig, (ax1, ax2) = plt.subplots(
        2, 1,
        figsize=(9, 6),
        sharex=True,
        constrained_layout=True,
        gridspec_kw={'height_ratios': [2, 1]}
    )
    
    # --- Price subplot ---
    ax1.plot(df.index, df['Close'], label='Close', color='black')
    ax1.set_ylabel('Close Price')

    if plot_buy_sell_ena:
        ax1.set_title(f"Ticker='{symbol}', Close & Buy and Sell Signals")
    else:
        ax1.set_title(f"Ticker='{symbol}', Close")
    ax1.grid(True)

    if plot_buy_sell_ena:
        # --- Plot Buy/Sell markers only on transitions ---
        if 'Signal' in df.columns:
            buy_idx = df[(df['Signal'] == 1) & (df['Signal'].shift(1) != 1)]
            sell_idx = df[(df['Signal'] == -1) & (df['Signal'].shift(1) != -1)]
    
            ax1.scatter(
                buy_idx.index,
                buy_idx['Close'],
                marker='^',
                color='green',
                s=100,
                label='Buy',
                zorder=3
            )
    
            ax1.scatter(
                sell_idx.index,
                sell_idx['Close'],
                marker='v',
                color='red',
                s=100,
                label='Sell',
                zorder=3
            )

    ax1.legend(loc='upper left')

    # --- Oscillator subplot ---
    ax2_left = ax2
    ax2_right = ax2.twinx()


    title_text = f"params={params}"

    if plot_so_ena and 'SO' in df.columns:
        ax2_right.plot(df.index, df['SO'], label='Synthetic Oscillator', color='darkblue')
        title_text += f", SO_last={df['SO'].iloc[-1]:.2f}"

    if plot_roc2_ena and 'ROC2' in df.columns:
        ax2_right.plot(df.index, df['ROC2'], label='ROC2', color='darkblue')
        title_text += f", ROC2_last={df['ROC2'].iloc[-1]:.2f}"
        if 'Signal' in df.columns:
            ax2_left.plot(df.index, df['Signal'], label='Signal', color='lightblue')
            ax2_left.set_ylabel('Signal')

    ax2_right.set_ylabel('Oscillators')
    ax2_right.axhline(0, color='black', linewidth=2)
    ax2_right.set_title(title_text)
    ax2_right.grid(True)

    lines_left, labels_left = ax2_left.get_legend_handles_labels()
    lines_right, labels_right = ax2_right.get_legend_handles_labels()
    ax2_right.legend(lines_left + lines_right, labels_left + labels_right, loc='upper left')
    
    plt.xticks(rotation=45)
    plt.show()


# The following function contains all indicator calculations and trading logic.
def calc_trading_strategy(ohlcv, params=None):

    if params is None:
        params=(17, 23, 8)

    length = params[2]

    df = ohlcv.copy()
    # synthetic oscillator indicator (aka SO)
    df['SO'] = synthetic_oscillator(df['Close'], params)

    # run SO output through Hann lowpass filter and perform ROC 
    df['SO2'] = hann_lowpass(df['SO'], params[2])
    df['ROC2'] = df['SO2'] - df['SO2'].shift()

    # buy logic (ROC2 cross above 0)
    cond_buy = (df['ROC2'] > 0) & (df['ROC2'].shift() < 0)
    df['Signal'] = np.where(cond_buy, 1, np.nan)

    # sell logic (ROC2 cross below 0)
    cond_sell = (df['ROC2'] < 0) & (df['ROC2'].shift() > 0)
    df['Signal'] = np.where(cond_sell, -1, df['Signal'])
    df['Signal'] = df['Signal'].fillna(method='ffill')

    # add BUY and SELL alerts to dataframe
    df['Alert'] = np.where((df['Signal']==1) & (df['Signal'].shift()== -1), 'BUY', '')
    df['Alert'] = np.where((df['Signal']==-1) & (df['Signal'].shift()== 1), 'SELL', df['Alert'])

    return df


# EXAMPLE USAGE

# download price data from Yahoo Finance
symbol = '^GSPC'
symbol = 'ES=F'
ohlcv = yf.download(
    symbol, 
    start="2000-01-01", 
    end="2026-02-12", 
    group_by="Ticker",
    auto_adjust=True,
    progress=False,
)
ohlcv = ohlcv[symbol]


# Call trading strategy and plotting functions. 
# Use slicing technique to set plot start and end timeframes.
# Set arguments on plotting function to enable or disable 
# desired indicator plots

# example usage below shows closing price for instrument in top subplot
# and Synthetic Oscillator in the bottom subplot

# --- Set Indicator Parameters as desired ---
lower_bound = 17
upper_bound = 23
length = 8
params=(lower_bound, upper_bound, length)    
df = calc_trading_strategy(ohlcv, params)
plot_trading_signals(df['2010':'2010'], params, plot_so_ena=True, plot_roc2_ena=False, plot_buy_sell_ena=False)


# Call trading strategy and plotting functions. 
# Use slicing technique to set plot start and end timeframes.
# Note the Signal line (light blue) generates the buy and sell
# signals as the ROC2 indicator goes above and below zero.
# Inspect plot for buy or sell signal.

# --- Set Indicator Parameters as desired ---
lower_bound = 17
upper_bound = 23
length = 8

params=(lower_bound, upper_bound, length)    
df = calc_trading_strategy(ohlcv, params)
plot_trading_signals(df['2010':'2010'], params, plot_so_ena=False, plot_roc2_ena=True, plot_buy_sell_ena=True)


# Inspect resulting dataframe for a BUY or SELL Alert
# example below shows most recent last 12 days
df.tail(12)


# Filter to inspect all BUY and SELL Alerts
# Use slicing techniques to zero in on specific time frames
cond = df['Alert'] != ''
df[cond]['2025':'2025'].head(10)