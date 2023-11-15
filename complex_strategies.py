import talib as tl
import numpy as np

#added RSI thresholds 
def strategy1(stockdata,stock_list, risk_factor, money, stock_count):
    n = 1
    
    # The Relative Strength Index is a momentum oscillator that measures the speed and change of price movements.
    # It ranges from 0 to 100 and is typically used to identify overbought or oversold conditions
    stockdata["RSI"] = tl.RSI(stockdata['Close'], timeperiod=14)
    
    # Dynamic RSI thresholds based on historical RSI values
    rsi_mean = stockdata["RSI"].mean()
    rsi_std = stockdata["RSI"].std()
    buy_threshold = rsi_mean - 0.5 * rsi_std
    sell_threshold = rsi_mean + 0.5 * rsi_std
    
    price_low = stockdata.at[stockdata.index[-1], 'Low']
    price_high = stockdata.at[stockdata.index[-1], 'High']
    price_mean = (price_low + price_high) / 2
    
    # moving average of the last 26 days
    stockdata["MA"] = tl.MA(stockdata['Close'], timeperiod=26, matype=0)
    
    confidence = -risk_factor if risk_factor < 0.03 else risk_factor

    # Buying when RSI value is lower than dynamic buy threshold
    # and the mean price is 5 euro lower than the MA52. Buy the stock for the mean price
    if (stockdata.at[stockdata.index[-1], "RSI"] < buy_threshold 
        and price_mean <= (stockdata.at[stockdata.index[-1], "MA"] - 5 / (risk_factor)) 
        and money >= price_mean - 5
    ):
        buy_price = price_mean + confidence*5  # if the risk is higher, investor risks buying for more price
        position_size = max(1,int((risk_factor * money) / price_mean)) 
        if money > 5 * buy_price:
            n = min(position_size,5)

    # Selling when RSI value is higher than dynamic sell threshold
    # or if the low price is 5 lower than MA52. Sell the stock for the mean price
    elif (stockdata.at[stockdata.index[-1], "RSI"] > sell_threshold 
        or price_low <= (stockdata.at[stockdata.index[-1], "MA"] - 5 / risk_factor) and stock_count > 0):
        sell_price = price_mean - confidence*5 # if the risk is higher, investor risks selling for less price
        position_size=int(stock_count,)
        if stock_count >= 5:
            n = min(position_size, stock_count)

    return buy_price, sell_price, n


# Added Stochastic Oscillator in buy and sell conditions
def strategy2(stockdata,risk_factor,money,stock_count):
    n=1
    price_low = stockdata.at[stockdata.index[-1], 'Low']
    price_high = stockdata.at[stockdata.index[-1], 'High']
    price_mean = (price_low + price_high) / 2

    k_period = 14
    d_period = 3
    stockdata['%K'] = 100 * ((stockdata['Close'] - stockdata['Low'].rolling(window=k_period).min()) / (stockdata['High'].rolling(window=k_period).max() - stockdata['Low'].rolling(window=k_period).min()))
    stockdata['%D'] = stockdata['%K'].rolling(window=d_period).mean()

    # moving average of last 25 days
    sma_period = 25
    stockdata["SMA"] = tl.MA(stockdata['Close'], timeperiod=sma_period, matype=0)
    buy_price = 0
    sell_price= 999999

    # Calculate position size based on risk factor and available capital
    position_size = max(1,int((risk_factor * money) / price_mean))

    confidence = -risk_factor if risk_factor < 0.03 else risk_factor

    # Calculate a simple moving average (SMA) over the last N periods.
    #Buying if the mean is higher than the sma
    if (
        price_mean < stockdata.at[stockdata.index[-1], "SMA"] and money >= price_mean
        and stockdata['%K'].iloc[-1] < 20 ):
        buy_price = price_mean+ confidence*5 
        if money > 5 * buy_price:
            n = min(position_size,5)

    #Selling if the mean is lower than the sma
    elif (price_mean > stockdata.at[stockdata.index[-1], "SMA"] and stock_count > 0
        and stockdata['%K'].iloc[-1] > 80):
        sell_price = price_mean - confidence*5
        if stock_count >= 5:
            n = min(position_size, stock_count)
    return buy_price, sell_price, n



def strategy3(stockdata,risk_factor,money,stock_count):
    n=1
    # Define the period for Bollinger Bands calculation and the number of standard deviations
    bb_period = 20
    num_std_dev = 2
    price_low = stockdata.at[stockdata.index[-1], 'Low']
    price_high = stockdata.at[stockdata.index[-1], 'High']
    price_mean = (price_low + price_high) / 2
    # Calculate the rolling mean and standard deviation of the closing prices, 
    stockdata['RollingMean'] = stockdata['Close'].rolling(bb_period).mean()
    stockdata['RollingStd'] = stockdata['Close'].rolling(bb_period).std()

    # Calculate the upper and lower Bollinger Bands
    stockdata['UpperBand'] = stockdata['RollingMean'] + (num_std_dev * stockdata['RollingStd'])
    stockdata['LowerBand'] = stockdata['RollingMean'] - (num_std_dev * stockdata['RollingStd'])

    # Determine the buy and sell signals based on Bollinger Bands
    buy_price = 0
    sell_price = 9999999999

    # Calculate position size based on risk factor and available capital
    position_size = max(1,int((risk_factor * money) / price_mean))
    confidence = -risk_factor if risk_factor < 0.03 else risk_factor

    if (stockdata.at[stockdata.index[-1], 'Close'] < stockdata.at[stockdata.index[-1], 'LowerBand'] and money >= stockdata.at[stockdata.index[-1], 'Close']):
        buy_price = price_mean + confidence*5 
        if money > 5 * buy_price:
            n = min(position_size,5)
    elif (stockdata.at[stockdata.index[-1], 'Close'] > stockdata.at[stockdata.index[-1], 'UpperBand'] and stock_count>0):
        sell_price = price_mean - confidence*5 
        if stock_count >= 5:
            n = min(position_size, stock_count)

    return buy_price, sell_price, n



def strategy4(stockdata, risk_factor, money, stock_count):
    n = 1
    # Define the short-term and long-term periods for the EMA calculation
    short_term_period = 12
    long_term_period = 26
    price_low = stockdata.at[stockdata.index[-1], 'Low']
    price_high = stockdata.at[stockdata.index[-1], 'High']
    price_mean = (price_low + price_high) / 2
    # Calculate the short-term and long-term exponential moving averages (EMA)
    short_term_ema = stockdata['Close'].ewm(span=short_term_period, adjust=False).mean()
    long_term_ema = stockdata['Close'].ewm(span=long_term_period, adjust=False).mean()

    # Calculate the MACD line by subtracting the long-term EMA from the short-term EMA
    macd_line = short_term_ema - long_term_ema

    # Define the signal line period
    signal_line_period = 9

    # Calculate the signal line as a 9-period EMA of the MACD line
    signal_line = macd_line.ewm(span=signal_line_period, adjust=False).mean()

    buy_price = np.nan
    sell_price = np.nan

    # Calculate position size based on risk factor and available capital
    position_size = max(1,int((risk_factor * money) / price_mean))  
    confidence = -risk_factor if risk_factor < 0.03 else risk_factor

    if (macd_line.iloc[-1]  > signal_line.iloc[-1] and money >= stockdata.at[stockdata.index[-1], 'Close']):
        buy_price = price_mean + confidence*5
        if money > 5 * buy_price:
            n = min(position_size,5)

    elif (macd_line.iloc[-1] < signal_line.iloc[-1] and stock_count > 0):
        sell_price = price_mean + confidence*5
        if stock_count >= 5:  
            n = min(position_size, stock_count)

    return buy_price, sell_price, n

