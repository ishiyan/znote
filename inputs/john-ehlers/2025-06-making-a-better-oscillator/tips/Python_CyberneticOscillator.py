#
# import required python libraries
#
%matplotlib inline
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
import math
import datetime as dt
print(yf.__version__)

#
# Use Yahoo Finance python package to obtain OHLCV data 
#
symbol = '^GSPC'
symbol = 'SPY'
ohlcv = yf.download(symbol, start="1995-01-01", end="2025-04-18", group_by="Ticker", auto_adjust=True)
ohlcv = ohlcv[symbol]

#
# Use pandas built in plot function to see simple price chart 
#
ax = ohlcv['Close'].plot(
    figsize=(9,6), 
    grid=True, 
    title=f'{symbol}', 
    #marker='.'
)


#
# Building block / routines used to implement cybernetic oscillaor indicator 
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

def calc_super_smoother(price, period):
        
        a1 = np.exp(-1.414 * np.pi / period)
        b1 = 2 * a1 * np.cos(math.radians(1.414 * 180 / period))
        c2 = b1
        c3 = -a1 * a1
        c1 = (1 - c2 - c3)
    
        out_values = []
        for i in range(len(price)):
            if i >= 4:
                out_values.append(c1*(price[i]+price[i-1])/2 + c2*out_values[i-1] + c3*out_values[i-2])
            else:
                out_values.append(price[i])
        
        return out_values

def calc_rms(price):
    
    length = len(price)
    sum_sq = 0
    for count in range(length):
        sum_sq += price[count] * price[count]
    return np.sqrt(sum_sq / length)

def calc_cybernetic_oscillator(close, params=(30, 20)):

    hp_length = params[0]
    lp_length = params[1]
    
    df = pd.DataFrame(index=close.index, data=close)
    df['HP'] = calc_highpass(close, hp_length)
    df['LP'] = calc_super_smoother(df['HP'], lp_length)
    df['RMS'] = df['LP'].rolling(100).apply(calc_rms)
    df['CO'] = df['LP']/df['RMS']

    return df['CO']

#
# Exampe python code to create two versions of the cybernetic oscillator 
# as presented in June 2005 Trader Tip article
#

lp_length = 20
hp1_length = 30
hp2_length = 250

co1_params=(hp1_length, lp_length)
co2_params=(hp2_length, lp_length)

df = ohlcv.copy()
df['CO1'] = calc_cybernetic_oscillator(ohlcv['Close'], params=co1_params)
df['CO2'] = calc_cybernetic_oscillator(ohlcv['Close'], params=co2_params)
df


#
# MatPlotLib routine to plot Close, CO1 and CO2 values
#
def plot_indicators1(df):
    # Create a figure with three subplots stacked vertically
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 6), sharex=True)

    # Plotting the first subplot (e.g., Price Data)
    ax1.set_title(f"S&P 500")
    ax1.plot(df.index, df['Close'], label='Close', color='blue', marker='.')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.set_ylabel('Price Plot')
    ax1.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # Plotting the second subplot
    ax2.set_title(f'Cybernetic Oscillator {co1_params}')
    ax2.plot(df.index, df['CO1'], label='CO1', color='red')
    ax2.axhline(y=0, color='black', linestyle='-', label='zero')
    #ax2.set_ylabel('Linear Slope')
    ax2.grid(True, linestyle='-', alpha=0.5)
    ax2.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # Plotting the third subplot
    ax3.set_title(f'Cybernetic Oscillator {co2_params}')
    ax3.plot(df.index, df['CO2'], label='CO2', color='blue')
    ax3.axhline(y=0, color='black', linestyle='-', label='zero')
    ax3.grid(True, linestyle='-', alpha=0.5)
    ax3.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Improve overall layout
    plt.tight_layout()

    # Show the plot
    plt.show()



plot_indicators1(df['2024-03':'2025'])


#
# Example python code to implement the simple dual ROC strategy showcased 
# in trader tip article the python code is bundled in a *strategy* routine 
# so it can easily be called, paramater as passed into the routine as a variable
#
def strategy(ohlcv, params):
    
    df = ohlcv.copy()
    df['LP'] = calc_super_smoother(df['Close'], params[0])
    df['BP1'] = calc_highpass(df['LP'],params[1] )
    df['ROC1'] = df['BP1'] - df['BP1'].shift(2)
    
    df['BP2'] = calc_highpass(df['LP'],params[2])
    df['ROC2'] = df['BP2'] - df['BP2'].shift(2)
    
    df['Signal'] = np.where((df['ROC1'] > 0 ) & (df['ROC2'] >0 ), 1, np.nan)
    df['Signal'] = np.where((df['ROC1'] < 0 ) & (df['ROC2'] <0 ), 0, df['Signal'])
    df['Signal'] = df['Signal'].fillna(method='ffill')
    return df


params=(20, 55, 156)
data = strategy(ohlcv, params)
data


#
# The Simple Dual ROC strategy indicators are visualized in the MatplotLib 
# routine below. Here LP, BP1 and BP2 can be see observed along with price
#
def plot_indicators2(df):
    
    # Create a figure with three subplots stacked vertically
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(9, 6), sharex=True)

    # Plotting the first subplot (e.g., Price Data)
    ax1.set_title(f"Ticker={symbol}")
    ax1.plot(df.index, df['Close'], label='Close', color='blue',)
    ax1.plot(df.index, df['LP'], label='LP', color='orange', )
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.set_ylabel('Price Plot')
    ax1.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # Plotting the second subplot
    ax2.set_title(f'BP1')
    ax2.plot(df.index, df['BP1'], label='BP1', color='red')
    ax2.axhline(y=0, color='black', linestyle='--', label='zero')
    #ax2.set_ylabel('Linear Slope')
    ax2.grid(True, linestyle='-', alpha=0.5)
    ax2.legend(loc='upper left', bbox_to_anchor=(1, 1))

    # Plotting the third subplot
    ax3.set_title(f'BP2')
    ax3.plot(df.index, df['BP2'], label='BP2', color='blue')
    ax3.axhline(y=0, color='black', linestyle='--', label='zero')
    ax3.grid(True, linestyle='-', alpha=0.5)
    ax3.legend(loc='upper left', bbox_to_anchor=(1, 1))
    
    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Improve overall layout
    plt.tight_layout()

    # Show the plot
    plt.show()

plot_indicators2(data['2024-03':'2025'])


#
# A simple backtest framework/routines are provided which allow changing 
# parameters and visualize performance results. Performance can be compared 
# against Buy&Hold of same ticker by setting. All buy and sell occur on the 
# day of the buy/sell signal using market close values
#
def backtest(data):

    df = data.copy()
    
    df['Return Ratio'] = np.where(df['Signal'].shift()==1, 1+df['Close'].pct_change(),1 )
    df['Strategy'] = df['Return Ratio'].cumprod()
    df['BH'] = (1+df['Close'].pct_change()).cumprod()

    df['Peak'] = df['Strategy'].cummax()
    df['% DD'] = 100*(df['Strategy']/df['Peak']-1)

    df['Peak'] = df['BH'].cummax()
    df['BH % DD'] = 100*(df['BH']/df['Peak']-1)

    df.at[df.index[0], 'Strategy'] = 1
    df.at[df.index[0], 'BH'] = 1

    return df


def plot_backtest_results(df, strategy_name="Simple Dual ROC Strategy", compare_bh_ena=False):

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9, 6), sharex=True)

    ax1.set_title(f"{strategy_name}, Ticker={symbol},")
    ax1.plot(df.index, df['Strategy'], label='Strategy Equity Curve', color='blue',)

    if compare_bh_ena:
        ax1.plot(df.index, df['BH'], label='Buy & Hold Equity Curve', color='orange',)
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.set_ylabel('Cumulative Return')
    ax1.legend(loc='upper left', bbox_to_anchor=(1, 1))

    ax2.set_title(f"% Drawdown")
    ax2.plot(df.index, df['% DD'], label='Strategy Drawdown', color='blue',)

    if compare_bh_ena:
        ax2.plot(df.index, df['BH % DD'], label='Buy & Hold Drawdown', color='orange',)

    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.set_ylabel('% drawdown')
    ax2.legend(loc='upper left', bbox_to_anchor=(1, 1))

#
# Putting the building blocks toegther, parameters can be changed and results viewed visually
# Here using default values presenyed in article
#
params=(20, 55, 156)
data = strategy(ohlcv, params)
df = backtest(data['2009':'2024'])
plot_backtest_results(df, strategy_name="Simple Dual ROC Strategy", compare_bh_ena=False)


#
# Here change parameter and see results compared to buy & hold of same ticker
#
params=(50, 55, 156)
data = strategy(ohlcv, params)
df = backtest(data['2009':'2024'])
plot_backtest_results(df, compare_bh_ena=True)
