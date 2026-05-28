# Generate 100 random variables in 5 batches of 20, between -1.0 and 1.0
import pandas as pd
import numpy as np
import random

def rand():
    return random.random()
 
random_values = []
for x in list(range(5)):
    for i in list(range(20)):
        random_values.append(2*(rand()-0.5))
        
x_values = np.arange(1, len(random_values) + 1)
df = pd.DataFrame(index=x_values, columns=['A'], data=random_values)
df

df['C'] = 0
df['D'] = 0

# Apply the formulas for first-order discrete random walk
# C[n] = 0.1 + C[n-1] + A[n]
for i in range(3, len(df)+1):
    df.loc[i, 'C'] = 0.1 + df.loc[i-1, 'C'] + df.loc[i, 'A']

# Apply the formulas for second-order discrete random walk
# D[n] = 0.1 + (D[n-1] + A[n-1] + A[n])/2
for i in range(3, len(df)+1):
    df.loc[i, 'D'] = 0.1 + (df.loc[i-1, 'D'] + df.loc[i-1, 'A'] + df.loc[i, 'A'])/2

df
# Plot results
df = df.rename(columns={'C':'1st Order','D':'2nd Order'})
cols = ['1st Order', '2nd Order']
ax = df[cols].plot(figsize=(9, 6), grid=True, title='First and Second Order Discrete Randowm Walk Simulations')

# Implement Ultimate Smoother Function
def ultimate_smoother(price_data, period):
    """
    Ultimate Smoother Function (as described by John Ehlers)
    
    Parameters:
    price_data (list or numpy array): The price series to smooth.
    period (int): The period used for the smoothing.

    Returns:
    numpy array: The smoothed price series.
    """
    
    # Initialize arrays to store the smoothed values and intermediate variables
    US = np.zeros_like(price_data)
    
    # Calculate the smoothing coefficients
    a1 = np.exp(-1.414 * 3.14159 / period)
    b1 = 2 * a1 * np.cos(1.414 * 180 / period)
    c2 = b1
    c3 = -a1 * a1
    c1 = (1 + c2 - c3) / 4
    
    # Apply the smoothing function (recursive filter)
    for i in range(len(price_data)):
        if i >= 2:  # Start applying the recursive formula after the 2nd index (CurrentBar >= 4)
            US[i] = (1 - c1) * price_data[i] + (2 * c1 - c2) * price_data[i - 1] \
                    - (c1 + c3) * price_data[i - 2] + c2 * US[i - 1] + c3 * US[i - 2]
        else:
            # For the first few points, just use the price value (no smoothing yet)
            US[i] = price_data[i]

    return US

# Plot UltimateSmoother using a 20-day period on S&P 500 closing data
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

symbol = '^GSPC'
ohlcv = yf.download(symbol, start="2023-12-25", end="2024-12-25")

df = ohlcv.copy()
df['US/20'] = ultimate_smoother(prices=df['Close'], period=20)
cols = [
    'Close',
    'US/20', 
]
ax = df[cols].plot(figsize=(12,8), grid=True, title=f"{symbol}, Ultimate Smoother / 20day period", marker='.')

# Autocorrelation indicator calculation
def autocorrelation_indicator(data, length=20):
    # Apply UltimateSmoother
    filt = ultimate_smoother(data, length)  
    num_lags = 100  # Number of lags (0 to 99)
    num_bars = len(filt)  # Number of time points (bars)
    
    # Initialize the correlation matrix (2D array)
    corr_matrix = np.zeros((num_lags, num_bars))  # Shape: [lags, time]

    # Calculate correlation for each lag
    for lag in range(num_lags):
        for time_idx in range(length, num_bars):  # Start after smoothing length
            sx = sy = sxx = sxy = syy = 0
            for j in range(length):
                x = filt[time_idx - j] if (time_idx - j) >= 0 else 0
                y = filt[time_idx - lag - j] if (time_idx - lag - j) >= 0 else 0
                
                sx += x
                sy += y
                sxx += x * x
                sxy += x * y
                syy += y * y


            
            # Ensure the denominator is positive before calculating the correlation
            denominator_x = (length * sxx - sx ** 2)
            denominator_y = (length * syy - sy ** 2)
            
            if denominator_x > 0 and denominator_y > 0:
                corr_matrix[lag, time_idx] = (length * sxy - sx * sy) / sqrt(denominator_x * denominator_y)

    return corr_matrix

def plot_heatmap(corr_matrix):
    fig, ax = plt.subplots(figsize=(12, 6))  # Adjust figure size to make the plot clearer
    im = ax.imshow(corr_matrix, aspect='auto', interpolation='nearest', cmap='RdYlGn_r')  # Use a diverging colormap

    # Set axis labels
    ax.set_xlabel('Time (Index)', fontsize=12)
    ax.set_ylabel('Lag', fontsize=12)
    ax.set_title('AutoCorrelation Heatmap', fontsize=14)
    
    # Set ticks for lags (vertical axis)
    ax.set_yticks(np.arange(0, 100, 10))
    ax.set_yticklabels(np.arange(0, 100, 10))
    
    # Set ticks for time (horizontal axis)
    ax.set_xticks(np.arange(0, corr_matrix.shape[1], corr_matrix.shape[1] // 10))  # Ticks every ~10 bars
    ax.set_xticklabels(np.arange(0, corr_matrix.shape[1], corr_matrix.shape[1] // 10))

    # Add color bar
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Correlation Value', fontsize=12)

    plt.show()
price_data = ohlcv['Close'].tolist()

# Calculate the autocorrelation matrix
corr_matrix = autocorrelation_indicator(price_data, length=20)

# Plot the heatmap
plot_heatmap(corr_matrix)
